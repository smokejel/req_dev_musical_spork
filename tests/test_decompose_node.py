"""
Unit tests for the decompose_node function.

Tests state handling, agent execution, strategy enforcement, traceability validation,
and error handling.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch

from src.nodes.decompose_node import decompose_node, validate_strategy_adherence, validate_naming_convention
from src.state import (
    create_initial_state,
    DetailedRequirement,
    RequirementType,
    ErrorType
)
from src.agents.requirements_engineer import AgentError


# =======================================================================
# State Validation Tests (4 tests)
# =======================================================================

@pytest.mark.unit
@pytest.mark.phase2
class TestStateValidation:
    """Test state input validation."""

    def test_missing_extracted_requirements_error(self):
        """Test that missing extracted_requirements raises error."""
        state = {
            "decomposition_strategy": {},
            "target_subsystem": "Test"
        }

        result = decompose_node(state)

        # Should have errors
        assert "errors" in result
        assert len(result["errors"]) > 0
        assert result.get("requires_human_review") == True

    def test_missing_decomposition_strategy_error(self):
        """Test that missing decomposition_strategy raises error."""
        state = {
            "extracted_requirements": [{"id": "SYS-001", "text": "Test", "type": "FUNC"}],
            "target_subsystem": "Test"
        }

        result = decompose_node(state)

        # Should have errors
        assert "errors" in result
        assert len(result["errors"]) > 0
        assert result.get("requires_human_review") == True

    def test_empty_extracted_requirements_error(self):
        """Test that empty extracted_requirements raises error."""
        state = {
            "extracted_requirements": [],
            "decomposition_strategy": {"allocation_rules": []},
            "target_subsystem": "Test"
        }

        result = decompose_node(state)

        # Should have errors
        assert "errors" in result
        assert "no extracted requirements" in result["errors"][0].lower()

    def test_valid_state_processing(self):
        """Test that valid state is processed correctly."""
        state = {
            "extracted_requirements": [{"id": "SYS-FUNC-001", "text": "Test", "type": "FUNC"}],
            "decomposition_strategy": {
                "allocation_rules": ["Rule 1"],
                "naming_convention": "TEST-{TYPE}-{NNN}",
                "acceptance_criteria_required": False
            },
            "target_subsystem": "Test Subsystem"
        }

        with patch("src.nodes.decompose_node.RequirementsEngineerAgent") as mock_agent_class:
            mock_agent = Mock()
            mock_req = DetailedRequirement(
                id="TEST-FUNC-001",
                text="Test requirement",
                type=RequirementType.FUNCTIONAL,
                parent_id="SYS-FUNC-001",
                subsystem="Test Subsystem",
                acceptance_criteria=[],
                rationale="Test"
            )
            mock_agent.decompose_requirements.return_value = [mock_req]
            mock_agent.get_error_summary.return_value = {
                "error_log": [],
                "fallback_count": 0
            }
            mock_agent_class.return_value = mock_agent

            # Should not raise
            result = decompose_node(state)

            # Should have decomposed_requirements and traceability_matrix
            assert "decomposed_requirements" in result
            assert "traceability_matrix" in result


# =======================================================================
# Agent Execution Tests (5 tests)
# =======================================================================

@pytest.mark.unit
@pytest.mark.phase2
class TestAgentExecution:
    """Test agent execution and result handling."""

    @pytest.fixture
    def valid_state(self):
        """Valid state for testing."""
        return {
            "extracted_requirements": [
                {"id": "SYS-FUNC-001", "text": "System shall authenticate", "type": "FUNC"}
            ],
            "decomposition_strategy": {
                "allocation_rules": ["Rule 1"],
                "naming_convention": "BE-{TYPE}-{NNN}",
                "acceptance_criteria_required": True
            },
            "target_subsystem": "Backend"
        }

    def test_successful_decomposition(self, valid_state):
        """Test successful requirements decomposition."""
        with patch("src.nodes.decompose_node.RequirementsEngineerAgent") as mock_agent_class:
            mock_agent = Mock()
            mock_req = DetailedRequirement(
                id="BE-FUNC-001",
                text="Backend shall authenticate users",
                type=RequirementType.FUNCTIONAL,
                parent_id="SYS-FUNC-001",
                subsystem="Backend",
                acceptance_criteria=["Authenticates via OAuth2"],
                rationale="Allocated to Backend per strategy"
            )
            mock_agent.decompose_requirements.return_value = [mock_req]
            mock_agent.get_error_summary.return_value = {
                "error_log": [],
                "fallback_count": 0
            }
            mock_agent_class.return_value = mock_agent

            result = decompose_node(valid_state)

            # Agent should have been called
            mock_agent.decompose_requirements.assert_called_once()

            # State should be updated
            assert "decomposed_requirements" in result
            assert len(result["decomposed_requirements"]) == 1
            assert result["decomposed_requirements"][0]["id"] == "BE-FUNC-001"

    def test_decomposed_requirements_serialization(self, valid_state):
        """Test that DetailedRequirement objects are properly serialized to dicts."""
        with patch("src.nodes.decompose_node.RequirementsEngineerAgent") as mock_agent_class:
            mock_agent = Mock()
            mock_req = DetailedRequirement(
                id="BE-FUNC-001",
                text="Test",
                type=RequirementType.FUNCTIONAL,
                parent_id="SYS-FUNC-001",
                subsystem="Backend",
                acceptance_criteria=["AC1", "AC2"],
                rationale="Test rationale"
            )
            mock_agent.decompose_requirements.return_value = [mock_req]
            mock_agent.get_error_summary.return_value = {
                "error_log": [],
                "fallback_count": 0
            }
            mock_agent_class.return_value = mock_agent

            result = decompose_node(valid_state)

            # Should be a dict, not a Pydantic model
            assert isinstance(result["decomposed_requirements"][0], dict)
            assert result["decomposed_requirements"][0]["id"] == "BE-FUNC-001"
            assert len(result["decomposed_requirements"][0]["acceptance_criteria"]) == 2

    def test_traceability_matrix_built(self, valid_state):
        """Test that traceability matrix is built from decomposed requirements."""
        with patch("src.nodes.decompose_node.RequirementsEngineerAgent") as mock_agent_class:
            mock_agent = Mock()
            mock_req = DetailedRequirement(
                id="BE-FUNC-001",
                text="Test",
                type=RequirementType.FUNCTIONAL,
                parent_id="SYS-FUNC-001",
                subsystem="Backend",
                acceptance_criteria=["Test AC"],  # Required by strategy!
                rationale="Test"
            )
            mock_agent.decompose_requirements.return_value = [mock_req]
            mock_agent.get_error_summary.return_value = {
                "error_log": [],
                "fallback_count": 0
            }
            mock_agent_class.return_value = mock_agent

            result = decompose_node(valid_state)

            # Should have traceability_matrix
            assert "traceability_matrix" in result
            assert isinstance(result["traceability_matrix"], dict)
            assert "links" in result["traceability_matrix"]

    def test_agent_error_handling(self, valid_state):
        """Test handling of agent errors (CONTENT)."""
        with patch("src.nodes.decompose_node.RequirementsEngineerAgent") as mock_agent_class:
            mock_agent = Mock()
            mock_agent.decompose_requirements.side_effect = AgentError("Decomposition failed")
            mock_agent.get_error_summary.return_value = {
                "error_log": [],
                "fallback_count": 0
            }
            mock_agent_class.return_value = mock_agent

            result = decompose_node(valid_state)

            # Should have error
            assert "errors" in result
            assert "Decomposition failed" in result["errors"][0]
            assert result.get("requires_human_review") == True

            # Error log should have CONTENT error type
            assert len(result["error_log"]) > 0
            assert result["error_log"][-1]["error_type"] == ErrorType.CONTENT

    def test_fallback_count_tracking(self, valid_state):
        """Test that fallback count is tracked."""
        with patch("src.nodes.decompose_node.RequirementsEngineerAgent") as mock_agent_class:
            mock_agent = Mock()
            mock_req = DetailedRequirement(
                id="BE-FUNC-001",
                text="Test",
                type=RequirementType.FUNCTIONAL,
                parent_id="SYS-FUNC-001",
                subsystem="Backend",
                acceptance_criteria=["Test AC"],  # Required by strategy!
                rationale="Test"
            )
            mock_agent.decompose_requirements.return_value = [mock_req]
            mock_agent.get_error_summary.return_value = {
                "error_log": [],
                "fallback_count": 3  # Simulate 3 fallbacks
            }
            mock_agent_class.return_value = mock_agent

            # State with existing fallback_count
            state = {**valid_state, "fallback_count": 2}

            result = decompose_node(state)

            # Fallback count should be incremented
            assert result["fallback_count"] == 5  # 2 + 3


# =======================================================================
# Strategy Enforcement Tests (6 tests)
# =======================================================================

@pytest.mark.unit
@pytest.mark.phase2
class TestStrategyEnforcement:
    """Test strategy adherence validation."""

    def test_naming_convention_validation_valid(self):
        """Test that valid naming convention passes validation."""
        assert validate_naming_convention("NAV-FUNC-001", "NAV-{TYPE}-{NNN}") == True
        assert validate_naming_convention("BE-PERF-123", "BE-{TYPE}-{NNN}") == True

    def test_naming_convention_validation_invalid(self):
        """Test that invalid naming convention fails validation."""
        assert validate_naming_convention("Navigation-Function-1", "NAV-{TYPE}-{NNN}") == False
        assert validate_naming_convention("NAV-WRONG-001", "NAV-{TYPE}-{NNN}") == False

    def test_strategy_violations_detected(self):
        """Test that strategy violations are detected."""
        requirements = [
            DetailedRequirement(
                id="WRONG-FORMAT",  # Wrong naming convention
                text="Test",
                type=RequirementType.FUNCTIONAL,
                parent_id="SYS-001",
                subsystem="Navigation",
                acceptance_criteria=[],
                rationale="Test"
            )
        ]

        strategy = {
            "naming_convention": "NAV-{TYPE}-{NNN}",
            "acceptance_criteria_required": False
        }

        violations = validate_strategy_adherence(
            requirements=requirements,
            strategy=strategy,
            target_subsystem="Navigation"
        )

        assert len(violations) > 0
        assert any("naming convention" in v.lower() for v in violations)

    def test_wrong_subsystem_detected(self):
        """Test that wrong subsystem assignment is detected."""
        requirements = [
            DetailedRequirement(
                id="NAV-FUNC-001",
                text="Test",
                type=RequirementType.FUNCTIONAL,
                parent_id="SYS-001",
                subsystem="WrongSubsystem",  # Wrong!
                acceptance_criteria=[],
                rationale="Test"
            )
        ]

        strategy = {
            "naming_convention": "NAV-{TYPE}-{NNN}",
            "acceptance_criteria_required": False
        }

        violations = validate_strategy_adherence(
            requirements=requirements,
            strategy=strategy,
            target_subsystem="Navigation"
        )

        assert len(violations) > 0
        assert any("WrongSubsystem" in v for v in violations)

    def test_missing_acceptance_criteria_detected(self):
        """Test that missing acceptance criteria is detected when required."""
        requirements = [
            DetailedRequirement(
                id="NAV-FUNC-001",
                text="Test",
                type=RequirementType.FUNCTIONAL,
                parent_id="SYS-001",
                subsystem="Navigation",
                acceptance_criteria=[],  # Empty when required!
                rationale="Test"
            )
        ]

        strategy = {
            "naming_convention": "NAV-{TYPE}-{NNN}",
            "acceptance_criteria_required": True  # Required!
        }

        violations = validate_strategy_adherence(
            requirements=requirements,
            strategy=strategy,
            target_subsystem="Navigation"
        )

        assert len(violations) > 0
        assert any("acceptance criteria" in v.lower() for v in violations)

    def test_missing_parent_id_detected(self):
        """Test that missing parent_id is detected."""
        requirements = [
            DetailedRequirement(
                id="NAV-FUNC-001",
                text="Test",
                type=RequirementType.FUNCTIONAL,
                parent_id=None,  # Missing!
                subsystem="Navigation",
                acceptance_criteria=[],
                rationale="Test"
            )
        ]

        strategy = {
            "naming_convention": "NAV-{TYPE}-{NNN}",
            "acceptance_criteria_required": False
        }

        violations = validate_strategy_adherence(
            requirements=requirements,
            strategy=strategy,
            target_subsystem="Navigation"
        )

        assert len(violations) > 0
        assert any("parent_id" in v.lower() for v in violations)


# =======================================================================
# Traceability Validation Tests (3 tests)
# =======================================================================

@pytest.mark.unit
@pytest.mark.phase2
class TestTraceabilityValidation:
    """Test traceability validation in decompose node."""

    @pytest.fixture
    def valid_state(self):
        """Valid state for testing."""
        return {
            "extracted_requirements": [
                {"id": "SYS-FUNC-001", "text": "Test", "type": "FUNC"}
            ],
            "decomposition_strategy": {
                "allocation_rules": ["Rule 1"],
                "naming_convention": "BE-{TYPE}-{NNN}",
                "acceptance_criteria_required": False
            },
            "target_subsystem": "Backend"
        }

    def test_orphaned_requirement_detected(self, valid_state):
        """Test that orphaned requirements (invalid parent_id) are detected."""
        with patch("src.nodes.decompose_node.RequirementsEngineerAgent") as mock_agent_class:
            mock_agent = Mock()
            mock_req = DetailedRequirement(
                id="BE-FUNC-001",
                text="Test",
                type=RequirementType.FUNCTIONAL,
                parent_id="INVALID-PARENT-999",  # Non-existent parent!
                subsystem="Backend",
                acceptance_criteria=[],
                rationale="Test"
            )
            mock_agent.decompose_requirements.return_value = [mock_req]
            mock_agent.get_error_summary.return_value = {
                "error_log": [],
                "fallback_count": 0
            }
            mock_agent_class.return_value = mock_agent

            result = decompose_node(valid_state)

            # Should fail traceability validation
            assert "errors" in result
            assert result.get("requires_human_review") == True

    def test_valid_traceability_passes(self, valid_state):
        """Test that valid traceability passes validation."""
        with patch("src.nodes.decompose_node.RequirementsEngineerAgent") as mock_agent_class:
            mock_agent = Mock()
            mock_req = DetailedRequirement(
                id="BE-FUNC-001",
                text="Test",
                type=RequirementType.FUNCTIONAL,
                parent_id="SYS-FUNC-001",  # Valid parent
                subsystem="Backend",
                acceptance_criteria=[],
                rationale="Test"
            )
            mock_agent.decompose_requirements.return_value = [mock_req]
            mock_agent.get_error_summary.return_value = {
                "error_log": [],
                "fallback_count": 0
            }
            mock_agent_class.return_value = mock_agent

            result = decompose_node(valid_state)

            # Should succeed
            assert "decomposed_requirements" in result
            assert "traceability_matrix" in result
            assert result.get("requires_human_review") != True

    def test_traceability_matrix_contains_links(self, valid_state):
        """Test that traceability matrix contains correct links."""
        with patch("src.nodes.decompose_node.RequirementsEngineerAgent") as mock_agent_class:
            mock_agent = Mock()
            mock_req = DetailedRequirement(
                id="BE-FUNC-001",
                text="Test",
                type=RequirementType.FUNCTIONAL,
                parent_id="SYS-FUNC-001",
                subsystem="Backend",
                acceptance_criteria=[],
                rationale="Test"
            )
            mock_agent.decompose_requirements.return_value = [mock_req]
            mock_agent.get_error_summary.return_value = {
                "error_log": [],
                "fallback_count": 0
            }
            mock_agent_class.return_value = mock_agent

            result = decompose_node(valid_state)

            # Check links
            assert len(result["traceability_matrix"]["links"]) == 1
            link = result["traceability_matrix"]["links"][0]
            assert link["parent_id"] == "SYS-FUNC-001"
            assert link["child_id"] == "BE-FUNC-001"


# =======================================================================
# Error Handling Tests (2 tests)
# =======================================================================

@pytest.mark.unit
@pytest.mark.phase2
class TestErrorHandling:
    """Test error handling edge cases."""

    def test_unexpected_exception_caught(self):
        """Test that unexpected exceptions are caught and logged."""
        state = {
            "extracted_requirements": [{"id": "SYS-001", "text": "Test", "type": "FUNC"}],
            "decomposition_strategy": {},
            "target_subsystem": "Test"
        }

        with patch("src.nodes.decompose_node.RequirementsEngineerAgent") as mock_agent_class:
            mock_agent_class.side_effect = RuntimeError("Unexpected error")

            result = decompose_node(state)

            # Should have error
            assert "errors" in result
            assert result.get("requires_human_review") == True

            # Error type should be FATAL
            assert len(result["error_log"]) > 0
            assert result["error_log"][-1]["error_type"] == ErrorType.FATAL

    def test_error_type_classification_in_state(self):
        """Test that error types are correctly classified."""
        state = {
            "extracted_requirements": [{"id": "SYS-001", "text": "Test", "type": "FUNC"}],
            "decomposition_strategy": {"allocation_rules": []},
            "target_subsystem": "Test"
        }

        with patch("src.nodes.decompose_node.RequirementsEngineerAgent") as mock_agent_class:
            mock_agent = Mock()
            mock_agent.decompose_requirements.side_effect = AgentError("Content error")
            mock_agent.get_error_summary.return_value = {
                "error_log": [],
                "fallback_count": 0
            }
            mock_agent_class.return_value = mock_agent

            result = decompose_node(state)

            # AgentError should be classified as CONTENT
            assert result["error_log"][-1]["error_type"] == ErrorType.CONTENT
            assert result["error_log"][-1]["node"] == "decompose"
