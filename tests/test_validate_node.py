"""
Unit tests for the validate_node.

Tests state validation, quality gate logic, automated validation, LLM assessment integration,
refinement feedback generation, and error handling.
"""

import pytest
from unittest.mock import Mock, patch

from src.nodes.validate_node import (
    validate_node,
    apply_quality_gate,
    determine_human_review_required
)
from src.state import QualityMetrics, QualityIssue, QualitySeverity, DecompositionState
from tests.fixtures.mock_llm_validation_responses import (
    VALID_VALIDATION_RESPONSE,
    FAILED_VALIDATION_RESPONSE,
    VALIDATION_WITH_CRITICAL_ISSUES,
    VERY_LOW_QUALITY_VALIDATION,
    AT_THRESHOLD_VALIDATION,
    BARELY_FAILS_VALIDATION
)


# =======================================================================
# State Validation Tests (4 tests)
# =======================================================================

@pytest.mark.unit
@pytest.mark.phase2
class TestStateValidation:
    """Test state validation and input checking."""

    def test_missing_decomposed_requirements_raises_error(self):
        """Test that missing decomposed_requirements raises error."""
        state = DecompositionState(
            extracted_requirements=[{"id": "SYS-001", "text": "Test"}],
            decomposition_strategy={"naming_convention": "NAV-{TYPE}-{NNN}"}
        )

        result = validate_node(state)

        assert 'errors' in result
        assert len(result['errors']) > 0
        assert 'decomposed_requirements' in result['errors'][0]

    def test_missing_extracted_requirements_raises_error(self):
        """Test that missing extracted_requirements raises error."""
        state = DecompositionState(
            decomposed_requirements=[{"id": "NAV-FUNC-001", "text": "Test"}],
            decomposition_strategy={"naming_convention": "NAV-{TYPE}-{NNN}"}
        )

        result = validate_node(state)

        assert 'errors' in result
        assert len(result['errors']) > 0
        assert 'extracted_requirements' in result['errors'][0]

    def test_missing_decomposition_strategy_raises_error(self):
        """Test that missing decomposition_strategy raises error."""
        state = DecompositionState(
            decomposed_requirements=[{"id": "NAV-FUNC-001", "text": "Test"}],
            extracted_requirements=[{"id": "SYS-001", "text": "Test"}]
        )

        result = validate_node(state)

        assert 'errors' in result
        assert len(result['errors']) > 0
        assert 'decomposition_strategy' in result['errors'][0]

    def test_empty_decomposed_requirements_raises_error(self):
        """Test that empty decomposed requirements list raises error."""
        state = DecompositionState(
            decomposed_requirements=[],
            extracted_requirements=[{"id": "SYS-001", "text": "Test"}],
            decomposition_strategy={"naming_convention": "NAV-{TYPE}-{NNN}"}
        )

        result = validate_node(state)

        assert 'errors' in result
        assert 'empty' in result['errors'][0].lower()


# =======================================================================
# Quality Gate Logic Tests (6 tests)
# =======================================================================

@pytest.mark.unit
@pytest.mark.phase2
class TestQualityGateLogic:
    """Test quality gate application and threshold logic."""

    def test_high_quality_passes_gate(self):
        """Test that high-quality requirements pass quality gate."""
        quality_metrics = QualityMetrics(
            completeness=0.95,
            clarity=0.90,
            testability=0.92,
            traceability=0.88,
            overall_score=0.9125,
            issues=[]
        )

        result = apply_quality_gate(quality_metrics, threshold=0.80)
        assert result is True

    def test_low_quality_fails_gate(self):
        """Test that low-quality requirements fail quality gate."""
        quality_metrics = QualityMetrics(
            completeness=0.70,
            clarity=0.75,
            testability=0.65,
            traceability=0.80,
            overall_score=0.725,
            issues=[]
        )

        result = apply_quality_gate(quality_metrics, threshold=0.80)
        assert result is False

    def test_critical_issues_fail_gate_despite_high_score(self):
        """Test that critical issues fail gate even with high overall score."""
        quality_metrics = QualityMetrics(
            completeness=0.85,
            clarity=0.88,
            testability=0.82,
            traceability=0.60,
            overall_score=0.7875,
            issues=[
                QualityIssue(
                    severity=QualitySeverity.CRITICAL,
                    requirement_id="NAV-FUNC-001",
                    dimension="traceability",
                    description="Missing parent_id",
                    suggestion="Add parent_id"
                )
            ]
        )

        result = apply_quality_gate(quality_metrics, threshold=0.70)
        assert result is False

    def test_at_threshold_passes(self):
        """Test that score exactly at threshold passes."""
        quality_metrics = QualityMetrics(
            completeness=0.80,
            clarity=0.80,
            testability=0.80,
            traceability=0.80,
            overall_score=0.80,
            issues=[]
        )

        result = apply_quality_gate(quality_metrics, threshold=0.80)
        assert result is True

    def test_barely_below_threshold_fails(self):
        """Test that score barely below threshold fails."""
        quality_metrics = QualityMetrics(
            completeness=0.82,
            clarity=0.85,
            testability=0.75,
            traceability=0.78,
            overall_score=0.79,
            issues=[]
        )

        result = apply_quality_gate(quality_metrics, threshold=0.80)
        assert result is False

    def test_custom_threshold_applied(self):
        """Test that custom quality threshold is applied."""
        quality_metrics = QualityMetrics(
            completeness=0.83,
            clarity=0.82,
            testability=0.81,
            traceability=0.84,
            overall_score=0.825,
            issues=[]
        )

        # Passes with 0.80 threshold
        assert apply_quality_gate(quality_metrics, threshold=0.80) is True

        # Fails with 0.85 threshold
        assert apply_quality_gate(quality_metrics, threshold=0.85) is False


# =======================================================================
# Automated Validation Tests (5 tests)
# =======================================================================

@pytest.mark.unit
@pytest.mark.phase2
class TestAutomatedValidation:
    """Test automated quality checking integration."""

    @pytest.fixture
    def sample_state(self):
        """Sample state for testing."""
        return DecompositionState(
            decomposed_requirements=[
                {
                    "id": "NAV-FUNC-001",
                    "text": "Navigation shall calculate routes",
                    "type": "FUNC",
                    "parent_id": "SYS-FUNC-001",
                    "subsystem": "Navigation",
                    "acceptance_criteria": ["Returns route"]
                }
            ],
            extracted_requirements=[
                {
                    "id": "SYS-FUNC-001",
                    "text": "System shall provide routing",
                    "type": "FUNC"
                }
            ],
            decomposition_strategy={
                "naming_convention": "NAV-{TYPE}-{NNN}",
                "acceptance_criteria_required": True
            },
            traceability_matrix={"links": []},
            quality_threshold=0.80
        )

    def test_automated_validation_runs_successfully(self, sample_state):
        """Test that automated validation runs without errors."""
        # Mock QualityAssuranceAgent
        with patch('src.nodes.validate_node.QualityAssuranceAgent') as MockAgent:
            mock_agent = Mock()
            mock_metrics = QualityMetrics(
                completeness=0.9,
                clarity=0.9,
                testability=0.9,
                traceability=0.9,
                overall_score=0.9,
                issues=[]
            )
            mock_agent.assess_quality.return_value = mock_metrics
            mock_agent.get_error_summary.return_value = {
                'total_executions': 1,
                'fallback_count': 0,
                'error_log': []
            }
            MockAgent.return_value = mock_agent

            result = validate_node(sample_state)

            assert 'quality_metrics' in result
            assert 'validation_passed' in result

    def test_automated_validation_detects_structural_issues(self):
        """Test that automated validation detects structural issues."""
        # This is tested indirectly through quality_checker tests
        # Here we verify it's called
        from src.utils import quality_checker

        requirements = [{"id": "NAV-FUNC-001", "text": "Test"}]  # Missing fields
        parents = []
        traceability = {}
        strategy = {"naming_convention": "NAV-{TYPE}-{NNN}"}

        result = quality_checker.validate_all_requirements(
            requirements, parents, traceability, strategy
        )

        assert 'issues' in result
        assert len(result['issues']) > 0

    def test_automated_validation_feeds_into_llm_assessment(self, sample_state):
        """Test that automated results are passed to LLM assessment."""
        with patch('src.nodes.validate_node.QualityAssuranceAgent') as MockAgent:
            mock_agent = Mock()
            mock_metrics = QualityMetrics(
                completeness=0.9,
                clarity=0.9,
                testability=0.9,
                traceability=0.9,
                overall_score=0.9,
                issues=[]
            )
            mock_agent.assess_quality.return_value = mock_metrics
            mock_agent.get_error_summary.return_value = {
                'total_executions': 1,
                'fallback_count': 0,
                'error_log': []
            }
            MockAgent.return_value = mock_agent

            validate_node(sample_state)

            # Verify assess_quality was called with automated_results
            assert mock_agent.assess_quality.called
            call_args = mock_agent.assess_quality.call_args[1]
            assert 'automated_results' in call_args

    def test_automated_validation_failure_logs_error(self):
        """Test that automated validation failure is logged."""
        state = DecompositionState(
            decomposed_requirements=[{"id": "NAV-FUNC-001"}],
            extracted_requirements=[{"id": "SYS-001"}],
            decomposition_strategy={"naming_convention": "NAV-{TYPE}-{NNN}"},
            traceability_matrix={}
        )

        # Mock quality_checker to raise error
        with patch('src.nodes.validate_node.quality_checker.validate_all_requirements') as mock_checker:
            mock_checker.side_effect = Exception("Validation error")

            result = validate_node(state)

            assert 'errors' in result
            assert len(result['errors']) > 0
            assert 'Automated validation failed' in result['errors'][0]

    def test_node_integrates_automated_and_llm_results(self, sample_state):
        """Test that node combines automated and LLM results."""
        with patch('src.nodes.validate_node.QualityAssuranceAgent') as MockAgent:
            mock_agent = Mock()
            mock_metrics = QualityMetrics(
                completeness=0.85,
                clarity=0.90,
                testability=0.88,
                traceability=0.87,
                overall_score=0.875,
                issues=[]
            )
            mock_agent.assess_quality.return_value = mock_metrics
            mock_agent.get_error_summary.return_value = {
                'total_executions': 1,
                'fallback_count': 0,
                'error_log': []
            }
            MockAgent.return_value = mock_agent

            result = validate_node(sample_state)

            # Verify quality metrics are in result
            assert result['quality_metrics']['overall_score'] == 0.875


# =======================================================================
# LLM Assessment Integration Tests (4 tests)
# =======================================================================

@pytest.mark.unit
@pytest.mark.phase2
class TestLLMAssessmentIntegration:
    """Test LLM-based quality assessment integration."""

    @pytest.fixture
    def sample_state(self):
        """Sample state."""
        return DecompositionState(
            decomposed_requirements=[
                {
                    "id": "NAV-FUNC-001",
                    "text": "Navigation shall calculate routes",
                    "type": "FUNC",
                    "parent_id": "SYS-FUNC-001",
                    "subsystem": "Navigation",
                    "acceptance_criteria": ["Returns route"],
                    "rationale": "Test"
                }
            ],
            extracted_requirements=[{"id": "SYS-FUNC-001", "text": "Test", "type": "FUNC"}],
            decomposition_strategy={"naming_convention": "NAV-{TYPE}-{NNN}"},
            traceability_matrix={"links": []}
        )

    def test_llm_assessment_called(self, sample_state):
        """Test that LLM assessment is called."""
        with patch('src.nodes.validate_node.QualityAssuranceAgent') as MockAgent:
            mock_agent = Mock()
            mock_metrics = QualityMetrics(
                completeness=0.9,
                clarity=0.9,
                testability=0.9,
                traceability=0.9,
                overall_score=0.9,
                issues=[]
            )
            mock_agent.assess_quality.return_value = mock_metrics
            mock_agent.get_error_summary.return_value = {
                'total_executions': 1,
                'fallback_count': 0,
                'error_log': []
            }
            MockAgent.return_value = mock_agent

            validate_node(sample_state)

            assert mock_agent.assess_quality.called

    def test_llm_assessment_receives_correct_inputs(self, sample_state):
        """Test that LLM assessment receives correct inputs."""
        with patch('src.nodes.validate_node.QualityAssuranceAgent') as MockAgent:
            mock_agent = Mock()
            mock_metrics = QualityMetrics(
                completeness=0.9,
                clarity=0.9,
                testability=0.9,
                traceability=0.9,
                overall_score=0.9,
                issues=[]
            )
            mock_agent.assess_quality.return_value = mock_metrics
            mock_agent.get_error_summary.return_value = {
                'total_executions': 1,
                'fallback_count': 0,
                'error_log': []
            }
            MockAgent.return_value = mock_agent

            validate_node(sample_state)

            call_kwargs = mock_agent.assess_quality.call_args[1]
            assert 'requirements' in call_kwargs
            assert 'automated_results' in call_kwargs
            assert 'strategy' in call_kwargs

    def test_llm_assessment_failure_handled(self, sample_state):
        """Test that LLM assessment failure is handled gracefully."""
        with patch('src.nodes.validate_node.QualityAssuranceAgent') as MockAgent:
            mock_agent = Mock()
            from src.agents.quality_assurance import AgentError
            mock_agent.assess_quality.side_effect = AgentError("Assessment failed")
            mock_agent.get_error_summary.return_value = {
                'total_executions': 1,
                'fallback_count': 0,
                'error_log': []
            }
            MockAgent.return_value = mock_agent

            result = validate_node(sample_state)

            assert 'errors' in result
            assert 'requires_human_review' in result
            assert result['requires_human_review'] is True

    def test_agent_error_log_merged(self, sample_state):
        """Test that agent error log is merged into state."""
        with patch('src.nodes.validate_node.QualityAssuranceAgent') as MockAgent:
            mock_agent = Mock()
            mock_metrics = QualityMetrics(
                completeness=0.9,
                clarity=0.9,
                testability=0.9,
                traceability=0.9,
                overall_score=0.9,
                issues=[]
            )
            mock_agent.assess_quality.return_value = mock_metrics
            mock_agent.get_error_summary.return_value = {
                'total_executions': 2,
                'fallback_count': 1,
                'error_log': [{'message': 'Test error'}]
            }
            MockAgent.return_value = mock_agent

            result = validate_node(sample_state)

            assert 'fallback_count' in result
            assert result['fallback_count'] == 1


# =======================================================================
# Refinement Feedback Generation Tests (3 tests)
# =======================================================================

@pytest.mark.unit
@pytest.mark.phase2
class TestRefinementFeedbackGeneration:
    """Test refinement feedback generation."""

    @pytest.fixture
    def sample_state(self):
        """Sample state."""
        return DecompositionState(
            decomposed_requirements=[{"id": "NAV-FUNC-001", "text": "Test", "type": "FUNC"}],
            extracted_requirements=[{"id": "SYS-001", "text": "Test", "type": "FUNC"}],
            decomposition_strategy={"naming_convention": "NAV-{TYPE}-{NNN}"},
            traceability_matrix={"links": []}
        )

    def test_feedback_generated_when_validation_fails(self, sample_state):
        """Test that feedback is generated when validation fails."""
        with patch('src.nodes.validate_node.QualityAssuranceAgent') as MockAgent:
            mock_agent = Mock()
            mock_metrics = QualityMetrics(
                completeness=0.70,
                clarity=0.75,
                testability=0.65,
                traceability=0.80,
                overall_score=0.725,
                issues=[]
            )
            mock_agent.assess_quality.return_value = mock_metrics
            mock_agent.generate_refinement_feedback.return_value = "Test feedback"
            mock_agent.get_error_summary.return_value = {
                'total_executions': 1,
                'fallback_count': 0,
                'error_log': []
            }
            MockAgent.return_value = mock_agent

            result = validate_node(sample_state)

            assert 'refinement_feedback' in result
            assert result['refinement_feedback'] is not None

    def test_no_feedback_when_validation_passes(self, sample_state):
        """Test that no feedback is generated when validation passes."""
        with patch('src.nodes.validate_node.QualityAssuranceAgent') as MockAgent:
            mock_agent = Mock()
            mock_metrics = QualityMetrics(
                completeness=0.95,
                clarity=0.90,
                testability=0.92,
                traceability=0.88,
                overall_score=0.9125,
                issues=[]
            )
            mock_agent.assess_quality.return_value = mock_metrics
            mock_agent.get_error_summary.return_value = {
                'total_executions': 1,
                'fallback_count': 0,
                'error_log': []
            }
            MockAgent.return_value = mock_agent

            result = validate_node(sample_state)

            assert result.get('refinement_feedback') is None

    def test_validation_issues_included_in_state(self, sample_state):
        """Test that validation issues are included in state."""
        with patch('src.nodes.validate_node.QualityAssuranceAgent') as MockAgent:
            mock_agent = Mock()
            mock_metrics = QualityMetrics(
                completeness=0.70,
                clarity=0.75,
                testability=0.65,
                traceability=0.80,
                overall_score=0.725,
                issues=[
                    QualityIssue(
                        severity=QualitySeverity.MAJOR,
                        requirement_id="NAV-FUNC-001",
                        dimension="testability",
                        description="Missing acceptance criteria",
                        suggestion="Add criteria"
                    )
                ]
            )
            mock_agent.assess_quality.return_value = mock_metrics
            mock_agent.generate_refinement_feedback.return_value = "Feedback"
            mock_agent.get_error_summary.return_value = {
                'total_executions': 1,
                'fallback_count': 0,
                'error_log': []
            }
            MockAgent.return_value = mock_agent

            result = validate_node(sample_state)

            assert 'validation_issues' in result
            assert len(result['validation_issues']) == 1


# =======================================================================
# Human Review Determination Tests (3 tests)
# =======================================================================

@pytest.mark.unit
@pytest.mark.phase2
class TestHumanReviewDetermination:
    """Test human review requirement logic."""

    def test_very_low_quality_requires_human_review(self):
        """Test that very low quality triggers human review."""
        quality_metrics = QualityMetrics(
            completeness=0.45,
            clarity=0.50,
            testability=0.40,
            traceability=0.35,
            overall_score=0.425,
            issues=[]
        )

        requires_review = determine_human_review_required(
            quality_metrics=quality_metrics,
            validation_passed=False,
            iteration_count=1,
            max_iterations=3
        )

        assert requires_review is True

    def test_max_iterations_requires_human_review(self):
        """Test that hitting max iterations triggers human review."""
        quality_metrics = QualityMetrics(
            completeness=0.75,
            clarity=0.75,
            testability=0.75,
            traceability=0.75,
            overall_score=0.75,
            issues=[]
        )

        requires_review = determine_human_review_required(
            quality_metrics=quality_metrics,
            validation_passed=False,
            iteration_count=3,
            max_iterations=3
        )

        assert requires_review is True

    def test_normal_failure_does_not_require_human_review(self):
        """Test that normal quality failure doesn't require human review."""
        quality_metrics = QualityMetrics(
            completeness=0.75,
            clarity=0.75,
            testability=0.70,
            traceability=0.75,
            overall_score=0.7375,
            issues=[]
        )

        requires_review = determine_human_review_required(
            quality_metrics=quality_metrics,
            validation_passed=False,
            iteration_count=1,
            max_iterations=3
        )

        assert requires_review is False


# =======================================================================
# Error Handling Tests (3 tests)
# =======================================================================

@pytest.mark.unit
@pytest.mark.phase2
class TestErrorHandling:
    """Test error handling and recovery."""

    def test_node_handles_unexpected_errors(self):
        """Test that node handles unexpected errors gracefully."""
        state = DecompositionState()

        result = validate_node(state)

        assert 'errors' in result
        assert 'requires_human_review' in result
        assert result['requires_human_review'] is True

    def test_error_log_populated_on_failure(self):
        """Test that error log is populated on failure."""
        state = DecompositionState(
            decomposed_requirements=[],
            extracted_requirements=[],
            decomposition_strategy={}
        )

        result = validate_node(state)

        assert 'error_log' in result
        assert len(result['error_log']) > 0

    def test_node_continues_after_feedback_generation_failure(self):
        """Test that node continues if feedback generation fails."""
        sample_state = DecompositionState(
            decomposed_requirements=[{"id": "NAV-FUNC-001", "text": "Test", "type": "FUNC"}],
            extracted_requirements=[{"id": "SYS-001", "text": "Test", "type": "FUNC"}],
            decomposition_strategy={"naming_convention": "NAV-{TYPE}-{NNN}"},
            traceability_matrix={"links": []}
        )

        with patch('src.nodes.validate_node.QualityAssuranceAgent') as MockAgent:
            mock_agent = Mock()
            mock_metrics = QualityMetrics(
                completeness=0.70,
                clarity=0.75,
                testability=0.65,
                traceability=0.80,
                overall_score=0.725,
                issues=[]
            )
            mock_agent.assess_quality.return_value = mock_metrics
            mock_agent.generate_refinement_feedback.side_effect = Exception("Feedback error")
            mock_agent.get_error_summary.return_value = {
                'total_executions': 1,
                'fallback_count': 0,
                'error_log': []
            }
            MockAgent.return_value = mock_agent

            result = validate_node(sample_state)

            # Node should still return results despite feedback failure
            assert 'quality_metrics' in result
            assert 'validation_passed' in result
