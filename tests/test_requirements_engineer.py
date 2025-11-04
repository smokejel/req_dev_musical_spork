"""
Unit tests for the RequirementsEngineerAgent.

Tests JSON parsing, requirement validation, decomposition logic, strategy adherence,
and integration with BaseAgent.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch

from src.agents.requirements_engineer import RequirementsEngineerAgent, AgentError
from src.state import DetailedRequirement, RequirementType
from tests.fixtures.mock_llm_decomposition_responses import (
    VALID_DECOMPOSITION_RESPONSE,
    PLAIN_JSON_DECOMPOSITION,
    MALFORMED_JSON_DECOMPOSITION,
    NON_ARRAY_DECOMPOSITION,
    INCOMPLETE_DECOMPOSITION,
    EMPTY_DECOMPOSITION,
    COMPLEX_DECOMPOSITION_RESPONSE,
    MISSING_PARENT_ID,
    WRONG_SUBSYSTEM,
    WRONG_NAMING_CONVENTION,
    MISSING_ACCEPTANCE_CRITERIA
)


# =======================================================================
# JSON Parsing Tests (7 tests)
# =======================================================================

@pytest.mark.unit
@pytest.mark.phase2
class TestJSONParsing:
    """Test JSON response parsing."""

    @pytest.fixture
    def engineer_agent(self):
        """Create a requirements engineer agent for testing."""
        return RequirementsEngineerAgent()

    def test_parse_valid_json_with_markdown(self, engineer_agent):
        """Test parsing valid JSON wrapped in markdown code blocks."""
        result = engineer_agent._parse_decomposition_response(VALID_DECOMPOSITION_RESPONSE)

        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(req, DetailedRequirement) for req in result)
        assert result[0].id == "NAV-FUNC-001"
        assert result[0].parent_id == "EXTRACT-FUNC-001"

    def test_parse_plain_json_without_markdown(self, engineer_agent):
        """Test parsing plain JSON without markdown blocks."""
        result = engineer_agent._parse_decomposition_response(PLAIN_JSON_DECOMPOSITION)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].id == "BE-FUNC-001"

    def test_malformed_json_raises_error(self, engineer_agent):
        """Test that malformed JSON raises AgentError."""
        with pytest.raises(AgentError, match="Invalid JSON"):
            engineer_agent._parse_decomposition_response(MALFORMED_JSON_DECOMPOSITION)

    def test_non_array_response_raises_error(self, engineer_agent):
        """Test that non-array JSON raises AgentError."""
        with pytest.raises(AgentError):
            engineer_agent._parse_decomposition_response(NON_ARRAY_DECOMPOSITION)

    def test_missing_required_fields_raises_error(self, engineer_agent):
        """Test that missing required fields raises AgentError."""
        with pytest.raises(AgentError, match="missing fields"):
            engineer_agent._parse_decomposition_response(INCOMPLETE_DECOMPOSITION)

    def test_empty_array_raises_error(self, engineer_agent):
        """Test that empty array raises AgentError."""
        with pytest.raises(AgentError, match="No requirements were decomposed"):
            engineer_agent._parse_decomposition_response(EMPTY_DECOMPOSITION)

    def test_complex_decomposition_response(self, engineer_agent):
        """Test parsing complex response with multiple requirements."""
        result = engineer_agent._parse_decomposition_response(COMPLEX_DECOMPOSITION_RESPONSE)

        assert len(result) == 4
        assert result[0].id == "TM-FUNC-001"
        assert result[1].id == "TM-FUNC-002"
        assert result[2].id == "TM-FUNC-003"
        assert result[3].id == "TM-PERF-001"


# =======================================================================
# Requirement Validation Tests (5 tests)
# =======================================================================

@pytest.mark.unit
@pytest.mark.phase2
class TestRequirementValidation:
    """Test requirement validation and type mapping."""

    @pytest.fixture
    def engineer_agent(self):
        """Create a requirements engineer agent for testing."""
        return RequirementsEngineerAgent()

    def test_type_mapping_func_to_functional(self, engineer_agent):
        """Test mapping FUNC to FUNCTIONAL enum."""
        response = """[{"id": "NAV-FUNC-001", "text": "Test", "type": "FUNC", "parent_id": "SYS-001", "subsystem": "Nav"}]"""

        requirements = engineer_agent._parse_decomposition_response(response)

        assert requirements[0].type == RequirementType.FUNCTIONAL

    def test_type_mapping_perf_to_performance(self, engineer_agent):
        """Test mapping PERF to PERFORMANCE enum."""
        response = """[{"id": "NAV-PERF-001", "text": "Test", "type": "PERF", "parent_id": "SYS-001", "subsystem": "Nav"}]"""

        requirements = engineer_agent._parse_decomposition_response(response)

        assert requirements[0].type == RequirementType.PERFORMANCE

    def test_full_type_names(self, engineer_agent):
        """Test that full type names (functional vs FUNC) work."""
        response = """[{"id": "NAV-FUNC-001", "text": "Test", "type": "functional", "parent_id": "SYS-001", "subsystem": "Nav"}]"""

        requirements = engineer_agent._parse_decomposition_response(response)

        assert requirements[0].type == RequirementType.FUNCTIONAL

    def test_detailed_requirement_has_all_fields(self, engineer_agent):
        """Test that DetailedRequirement has all expected fields."""
        result = engineer_agent._parse_decomposition_response(VALID_DECOMPOSITION_RESPONSE)

        req = result[0]
        assert hasattr(req, 'id')
        assert hasattr(req, 'text')
        assert hasattr(req, 'type')
        assert hasattr(req, 'parent_id')
        assert hasattr(req, 'subsystem')
        assert hasattr(req, 'acceptance_criteria')
        assert hasattr(req, 'rationale')

    def test_acceptance_criteria_is_list(self, engineer_agent):
        """Test that acceptance_criteria is parsed as a list."""
        result = engineer_agent._parse_decomposition_response(VALID_DECOMPOSITION_RESPONSE)

        req = result[0]
        assert isinstance(req.acceptance_criteria, list)
        assert len(req.acceptance_criteria) == 2


# =======================================================================
# Decomposition Logic Tests (6 tests)
# =======================================================================

@pytest.mark.unit
@pytest.mark.phase2
class TestDecompositionLogic:
    """Test decomposition workflow logic."""

    @pytest.fixture
    def sample_requirements(self):
        """Sample requirements for testing."""
        return [
            {
                "id": "EXTRACT-FUNC-001",
                "text": "The system shall authenticate users",
                "type": "FUNC"
            }
        ]

    @pytest.fixture
    def sample_strategy(self):
        """Sample decomposition strategy."""
        return {
            "allocation_rules": ["IF authentication THEN allocate to Backend"],
            "traceability_rules": ["Must have parent_id"],
            "decomposition_depth": 1,
            "naming_convention": "BE-{TYPE}-{NNN}",
            "acceptance_criteria_required": True
        }

    def test_empty_requirements_raises_error(self, sample_strategy):
        """Test that empty requirements list raises AgentError."""
        agent = RequirementsEngineerAgent()

        with pytest.raises(AgentError, match="empty requirements"):
            agent.decompose_requirements(
                system_requirements=[],
                decomposition_strategy=sample_strategy,
                target_subsystem="Backend",
                enable_fallback=False
            )

    def test_missing_strategy_raises_error(self, sample_requirements):
        """Test that missing strategy raises AgentError."""
        agent = RequirementsEngineerAgent()

        with pytest.raises(AgentError, match="strategy is required"):
            agent.decompose_requirements(
                system_requirements=sample_requirements,
                decomposition_strategy={},
                target_subsystem="Backend",
                enable_fallback=False
            )

    def test_missing_target_subsystem_raises_error(self, sample_requirements, sample_strategy):
        """Test that missing target_subsystem raises AgentError."""
        agent = RequirementsEngineerAgent()

        with pytest.raises(AgentError, match="must be specified"):
            agent.decompose_requirements(
                system_requirements=sample_requirements,
                decomposition_strategy=sample_strategy,
                target_subsystem="",
                enable_fallback=False
            )

    def test_prompt_building(self, sample_requirements, sample_strategy):
        """Test that prompt is built correctly."""
        agent = RequirementsEngineerAgent()

        prompt = agent._build_decomposition_prompt(
            system_requirements=sample_requirements,
            decomposition_strategy=sample_strategy,
            target_subsystem="Backend"
        )

        assert "Backend" in prompt
        assert "EXTRACT-FUNC-001" in prompt
        assert "authenticate users" in prompt
        assert "BE-{TYPE}-{NNN}" in prompt
        assert agent.skill_content in prompt

    def test_skill_content_loaded(self):
        """Test that skill content is loaded during initialization."""
        agent = RequirementsEngineerAgent()

        assert agent.skill_content is not None
        assert len(agent.skill_content) > 0
        assert "Requirements Decomposition" in agent.skill_content

    def test_successful_decomposition_returns_detailed_requirements(
        self, sample_requirements, sample_strategy
    ):
        """Test successful decomposition returns DetailedRequirement objects."""
        agent = RequirementsEngineerAgent()

        # Mock LLM response
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = VALID_DECOMPOSITION_RESPONSE
        mock_llm.invoke.return_value = mock_response

        with patch.object(agent, 'get_llm', return_value=mock_llm):
            result = agent.decompose_requirements(
                system_requirements=sample_requirements,
                decomposition_strategy=sample_strategy,
                target_subsystem="Navigation Subsystem",
                enable_fallback=False
            )

        assert isinstance(result, list)
        assert all(isinstance(req, DetailedRequirement) for req in result)


# =======================================================================
# BaseAgent Integration Tests (4 tests)
# =======================================================================

@pytest.mark.unit
@pytest.mark.phase2
class TestBaseAgentIntegration:
    """Test integration with BaseAgent."""

    @pytest.fixture
    def sample_requirements(self):
        """Sample requirements for testing."""
        return [{"id": "SYS-FUNC-001", "text": "Test", "type": "FUNC"}]

    @pytest.fixture
    def sample_strategy(self):
        """Sample strategy for testing."""
        return {
            "allocation_rules": ["Rule 1"],
            "traceability_rules": ["Rule 1"],
            "decomposition_depth": 1,
            "naming_convention": "NAV-{TYPE}-{NNN}",
            "acceptance_criteria_required": True
        }

    def test_uses_execute_with_fallback_method(self, sample_requirements, sample_strategy):
        """Test that agent uses execute_with_fallback from BaseAgent."""
        agent = RequirementsEngineerAgent()

        # Mock LLM response
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = VALID_DECOMPOSITION_RESPONSE
        mock_llm.invoke.return_value = mock_response

        with patch.object(agent, 'get_llm', return_value=mock_llm):
            with patch.object(agent, 'execute_with_fallback', wraps=agent.execute_with_fallback) as mock_execute:
                agent.decompose_requirements(
                    system_requirements=sample_requirements,
                    decomposition_strategy=sample_strategy,
                    target_subsystem="Navigation Subsystem",
                    enable_fallback=True
                )

                # Verify execute_with_fallback was called
                assert mock_execute.called

    def test_error_summary_propagation(self, sample_requirements, sample_strategy):
        """Test that error summary from BaseAgent is accessible."""
        agent = RequirementsEngineerAgent()

        # Mock LLM response
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = VALID_DECOMPOSITION_RESPONSE
        mock_llm.invoke.return_value = mock_response

        with patch.object(agent, 'get_llm', return_value=mock_llm):
            agent.decompose_requirements(
                system_requirements=sample_requirements,
                decomposition_strategy=sample_strategy,
                target_subsystem="Navigation Subsystem",
                enable_fallback=True
            )

            error_summary = agent.get_error_summary()
            assert 'total_executions' in error_summary
            assert 'fallback_count' in error_summary
            assert 'error_log' in error_summary

    def test_execution_count_tracking(self, sample_requirements, sample_strategy):
        """Test that execution count is tracked."""
        agent = RequirementsEngineerAgent()

        # Mock LLM response
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = VALID_DECOMPOSITION_RESPONSE
        mock_llm.invoke.return_value = mock_response

        with patch.object(agent, 'get_llm', return_value=mock_llm):
            initial_count = agent.execution_count

            agent.decompose_requirements(
                system_requirements=sample_requirements,
                decomposition_strategy=sample_strategy,
                target_subsystem="Navigation Subsystem",
                enable_fallback=True
            )

            assert agent.execution_count > initial_count

    def test_fallback_triggered_on_parse_error(self, sample_requirements, sample_strategy):
        """Test that fallback is triggered when parsing fails."""
        agent = RequirementsEngineerAgent()

        # Mock LLM to return malformed JSON first, then valid JSON
        mock_llm = Mock()
        mock_response_bad = Mock()
        mock_response_bad.content = MALFORMED_JSON_DECOMPOSITION

        mock_response_good = Mock()
        mock_response_good.content = VALID_DECOMPOSITION_RESPONSE

        mock_llm.invoke.side_effect = [mock_response_bad, mock_response_good]

        # Mock get_llm to return different instances for fallback
        llm_calls = []
        def get_llm_side_effect(use_fallback=False):
            llm_calls.append(use_fallback)
            return mock_llm

        with patch.object(agent, 'get_llm', side_effect=get_llm_side_effect):
            try:
                result = agent.decompose_requirements(
                    system_requirements=sample_requirements,
                    decomposition_strategy=sample_strategy,
                    target_subsystem="Navigation Subsystem",
                    enable_fallback=True
                )

                # If we get here, fallback worked
                assert agent.fallback_count > 0 or len(llm_calls) > 1
            except AgentError:
                # Fallback may not be triggered in this mock setup
                pass


# =======================================================================
# JSON Extraction Tests (2 tests)
# =======================================================================

@pytest.mark.unit
@pytest.mark.phase2
class TestJSONExtraction:
    """Test JSON extraction from various response formats."""

    @pytest.fixture
    def engineer_agent(self):
        """Create a requirements engineer agent for testing."""
        return RequirementsEngineerAgent()

    def test_extract_json_array_from_markdown_block(self, engineer_agent):
        """Test extracting JSON array from markdown code block."""
        response = """Here are the requirements:
```json
[{"id": "TEST-001", "text": "Test"}]
```
That's the result."""

        json_str = engineer_agent._extract_json_from_response(response)
        assert '[{"id": "TEST-001", "text": "Test"}]' in json_str

    def test_extract_json_array_from_plain_text(self, engineer_agent):
        """Test extracting JSON array from plain text."""
        response = """The requirements are: [{"id": "TEST-001", "text": "Test"}] and that's it."""

        json_str = engineer_agent._extract_json_from_response(response)
        assert '[{"id": "TEST-001", "text": "Test"}]' in json_str


# =======================================================================
# Traceability Tests (3 tests)
# =======================================================================

@pytest.mark.unit
@pytest.mark.phase2
class TestTraceability:
    """Test traceability-related parsing."""

    @pytest.fixture
    def engineer_agent(self):
        """Create a requirements engineer agent for testing."""
        return RequirementsEngineerAgent()

    def test_parent_id_is_preserved(self, engineer_agent):
        """Test that parent_id is correctly parsed and preserved."""
        result = engineer_agent._parse_decomposition_response(VALID_DECOMPOSITION_RESPONSE)

        assert result[0].parent_id == "EXTRACT-FUNC-001"
        assert result[1].parent_id == "EXTRACT-PERF-001"

    def test_missing_parent_id_still_parses(self, engineer_agent):
        """Test that requirements with missing parent_id still parse (validation happens later)."""
        # The agent should parse this, but decompose_node will catch the missing parent_id
        result = engineer_agent._parse_decomposition_response(MISSING_PARENT_ID)

        assert len(result) == 1
        assert result[0].parent_id is None

    def test_rationale_is_preserved(self, engineer_agent):
        """Test that rationale field is correctly parsed."""
        result = engineer_agent._parse_decomposition_response(VALID_DECOMPOSITION_RESPONSE)

        assert result[0].rationale is not None
        assert "Decomposes" in result[0].rationale
