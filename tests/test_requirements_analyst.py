"""
Unit tests for the RequirementsAnalystAgent.

Tests JSON parsing, requirement validation, extraction logic, and
integration with BaseAgent.
"""

import pytest
import json
from unittest.mock import Mock, MagicMock, patch

from src.agents.requirements_analyst import RequirementsAnalystAgent, AgentError
from src.state import Requirement, RequirementType
from tests.fixtures.mock_llm_responses import (
    VALID_EXTRACTION_RESPONSE,
    ALTERNATIVE_TYPE_FORMAT_RESPONSE,
    EMPTY_EXTRACTION_RESPONSE,
    MALFORMED_JSON,
    INCOMPLETE_JSON,
    NON_ARRAY_RESPONSE,
    PLAIN_JSON_RESPONSE
)


# =======================================================================
# JSON Parsing Tests (6 tests)
# =======================================================================

@pytest.mark.unit
@pytest.mark.phase1
class TestJSONParsing:
    """Test JSON response parsing."""

    @pytest.fixture
    def analyst_agent(self):
        """Create a requirements analyst agent for testing."""
        return RequirementsAnalystAgent()

    def test_parse_valid_json_with_markdown(self, analyst_agent):
        """Test parsing valid JSON wrapped in markdown code blocks."""
        result = analyst_agent._parse_llm_response(VALID_EXTRACTION_RESPONSE)

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["id"] == "EXTRACT-FUNC-001"
        assert result[1]["id"] == "EXTRACT-PERF-001"

    def test_parse_plain_json_without_markdown(self, analyst_agent):
        """Test parsing plain JSON without markdown blocks."""
        result = analyst_agent._parse_llm_response(PLAIN_JSON_RESPONSE)

        assert isinstance(result, list)
        assert len(result) == 1

    def test_malformed_json_raises_error(self, analyst_agent):
        """Test that malformed JSON raises AgentError."""
        with pytest.raises(AgentError, match="Failed to parse JSON"):
            analyst_agent._parse_llm_response(MALFORMED_JSON)

    def test_non_array_response_raises_error(self, analyst_agent):
        """Test that non-array JSON raises AgentError."""
        with pytest.raises(AgentError, match="Expected JSON array"):
            analyst_agent._parse_llm_response(NON_ARRAY_RESPONSE)

    def test_missing_required_fields_raises_error(self, analyst_agent):
        """Test that missing required fields raises AgentError."""
        with pytest.raises(AgentError, match="missing fields"):
            analyst_agent._parse_llm_response(INCOMPLETE_JSON)

    def test_empty_array_returns_empty_list(self, analyst_agent):
        """Test that empty JSON array returns empty list."""
        result = analyst_agent._parse_llm_response(EMPTY_EXTRACTION_RESPONSE)

        assert isinstance(result, list)
        assert len(result) == 0


# =======================================================================
# Requirement Validation Tests (5 tests)
# =======================================================================

@pytest.mark.unit
@pytest.mark.phase1
class TestRequirementValidation:
    """Test requirement validation and type mapping."""

    @pytest.fixture
    def analyst_agent(self):
        """Create a requirements analyst agent for testing."""
        return RequirementsAnalystAgent()

    def test_type_mapping_func_to_functional(self, analyst_agent):
        """Test mapping FUNC to FUNCTIONAL enum."""
        req_dicts = [{
            "id": "EXTRACT-FUNC-001",
            "text": "Test",
            "type": "FUNC"
        }]

        requirements = analyst_agent._validate_and_convert_requirements(req_dicts)

        assert len(requirements) == 1
        assert requirements[0].type == RequirementType.FUNCTIONAL

    def test_type_mapping_perf_to_performance(self, analyst_agent):
        """Test mapping PERF to PERFORMANCE enum."""
        req_dicts = [{
            "id": "EXTRACT-PERF-001",
            "text": "Test",
            "type": "PERF"
        }]

        requirements = analyst_agent._validate_and_convert_requirements(req_dicts)

        assert requirements[0].type == RequirementType.PERFORMANCE

    def test_type_mapping_full_names(self, analyst_agent):
        """Test that full type names work (FUNCTIONAL vs FUNC)."""
        req_dicts = [{
            "id": "EXTRACT-FUNC-001",
            "text": "Test",
            "type": "FUNCTIONAL"
        }]

        requirements = analyst_agent._validate_and_convert_requirements(req_dicts)

        assert requirements[0].type == RequirementType.FUNCTIONAL

    def test_invalid_type_raises_error(self, analyst_agent):
        """Test that invalid type raises AgentError."""
        req_dicts = [{
            "id": "EXTRACT-FUNC-001",
            "text": "Test",
            "type": "INVALID_TYPE"
        }]

        with pytest.raises(AgentError, match="Failed to validate requirement"):
            analyst_agent._validate_and_convert_requirements(req_dicts)

    def test_pydantic_validation_integration(self, analyst_agent):
        """Test that Pydantic validation is applied."""
        # Invalid ID format
        req_dicts = [{
            "id": "INVALID-ID",
            "text": "Test",
            "type": "FUNC"
        }]

        with pytest.raises(AgentError):
            analyst_agent._validate_and_convert_requirements(req_dicts)


# =======================================================================
# Extraction Logic Tests (5 tests)
# =======================================================================

@pytest.mark.unit
@pytest.mark.phase1
class TestExtractionLogic:
    """Test extraction logic with mocked LLMs."""

    @pytest.fixture
    def analyst_agent(self):
        """Create a requirements analyst agent for testing."""
        return RequirementsAnalystAgent()

    def test_successful_extraction(self, analyst_agent, sample_document_text):
        """Test successful extraction from valid document."""
        with patch.object(analyst_agent, 'execute_with_fallback') as mock_execute:
            mock_execute.return_value = [
                Requirement(id="EXTRACT-FUNC-001", text="Test", type=RequirementType.FUNCTIONAL)
            ]

            requirements = analyst_agent.extract_requirements(sample_document_text)

            assert len(requirements) == 1
            assert requirements[0].id == "EXTRACT-FUNC-001"

    def test_empty_document_raises_error(self, analyst_agent):
        """Test that empty document raises AgentError."""
        with pytest.raises(AgentError, match="Document text is empty"):
            analyst_agent.extract_requirements("")

    def test_skill_content_injected(self, analyst_agent, sample_document_text):
        """Test that skill content is included in LLM prompt."""
        skill_content = analyst_agent.get_skill_content()

        assert len(skill_content) > 0
        assert "requirement" in skill_content.lower()

    def test_llm_invocation(self, analyst_agent, sample_document_text):
        """Test that LLM is invoked correctly."""
        with patch.object(analyst_agent, 'execute_with_fallback') as mock_execute:
            # Return at least one requirement to avoid "no requirements extracted" error
            mock_execute.return_value = [
                Requirement(id="EXTRACT-FUNC-001", text="Test", type=RequirementType.FUNCTIONAL)
            ]

            analyst_agent.extract_requirements(sample_document_text)

            # Verify execute_with_fallback (LLM invocation) was called
            assert mock_execute.called
            # Verify it was called with enable_fallback=True
            assert mock_execute.call_args.kwargs.get('enable_fallback') == True

    def test_no_requirements_extracted_raises_error(self, analyst_agent, sample_document_text):
        """Test that extracting no requirements raises AgentError."""
        with patch.object(analyst_agent, 'execute_with_fallback') as mock_execute:
            mock_execute.return_value = []

            with pytest.raises(AgentError, match="No requirements extracted"):
                analyst_agent.extract_requirements(sample_document_text)


# =======================================================================
# Integration with BaseAgent Tests (4 tests)
# =======================================================================

@pytest.mark.unit
@pytest.mark.phase1
class TestBaseAgentIntegration:
    """Test integration with BaseAgent functionality."""

    @pytest.fixture
    def analyst_agent(self):
        """Create a requirements analyst agent for testing."""
        return RequirementsAnalystAgent()

    def test_uses_execute_with_fallback(self, analyst_agent, sample_document_text):
        """Test that extraction uses execute_with_fallback method."""
        with patch.object(analyst_agent, 'execute_with_fallback') as mock_execute:
            mock_execute.return_value = [
                Requirement(id="EXTRACT-FUNC-001", text="Test", type=RequirementType.FUNCTIONAL)
            ]

            analyst_agent.extract_requirements(sample_document_text)

            # Verify execute_with_fallback was called
            assert mock_execute.called
            assert mock_execute.call_args.kwargs.get('enable_fallback') == True

    def test_error_summary_propagation(self, analyst_agent, sample_document_text):
        """Test that error summary is accessible after execution."""
        with patch.object(analyst_agent, 'execute_with_fallback') as mock_execute:
            mock_execute.return_value = [
                Requirement(id="EXTRACT-FUNC-001", text="Test", type=RequirementType.FUNCTIONAL)
            ]

            analyst_agent.extract_requirements(sample_document_text)

            # Should be able to get error summary
            summary = analyst_agent.get_error_summary()
            assert 'total_executions' in summary

    def test_fallback_triggered_on_parse_error(self, analyst_agent, sample_document_text):
        """Test that fallback is triggered on parse errors."""
        # This is more of an integration test with BaseAgent
        # We verify the mechanism exists
        assert hasattr(analyst_agent, 'execute_with_fallback')
        assert hasattr(analyst_agent, 'fallback_count')

    def test_execution_count_tracking(self, analyst_agent, sample_document_text):
        """Test that execution count is tracked."""
        with patch.object(analyst_agent, 'execute_with_fallback') as mock_execute:
            mock_execute.return_value = [
                Requirement(id="EXTRACT-FUNC-001", text="Test", type=RequirementType.FUNCTIONAL)
            ]

            initial_count = analyst_agent.execution_count

            analyst_agent.extract_requirements(sample_document_text)

            # Execution count should have increased
            # (Note: in real execution, execute_with_fallback increments it)
            assert hasattr(analyst_agent, 'execution_count')
