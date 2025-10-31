"""
Unit tests for the extract_node function.

Tests state handling, document parsing integration, agent execution,
and error handling.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch

from src.nodes.extract_node import extract_node
from src.state import create_initial_state, Requirement, RequirementType, ErrorType
from src.utils.document_parser import DocumentParseError
from src.agents.requirements_analyst import AgentError


# =======================================================================
# State Validation Tests (3 tests)
# =======================================================================

@pytest.mark.unit
@pytest.mark.phase1
class TestStateValidation:
    """Test state input validation."""

    def test_missing_spec_document_path_error(self):
        """Test that missing spec_document_path raises error."""
        state = {
            "target_subsystem": "Test"
        }

        result = extract_node(state)

        # Should have errors
        assert "errors" in result
        assert len(result["errors"]) > 0
        assert result.get("requires_human_review") == True

    def test_valid_state_processing(self, valid_state):
        """Test that valid state is processed correctly."""
        with patch("src.nodes.extract_node.parse_document") as mock_parse:
            with patch("src.nodes.extract_node.RequirementsAnalystAgent") as mock_agent_class:
                mock_parse.return_value = ("Test document", "txt")
                mock_agent = Mock()
                mock_agent.extract_requirements.return_value = []
                mock_agent.get_error_summary.return_value = {
                    "error_log": [],
                    "fallback_count": 0
                }
                mock_agent_class.return_value = mock_agent

                # Should not raise
                result = extract_node(valid_state)

    def test_state_with_optional_fields(self):
        """Test state with all optional fields present."""
        state = create_initial_state(
            spec_document_path="test.txt",
            target_subsystem="Test",
            review_before_decompose=True,
            quality_threshold=0.85,
            max_iterations=5
        )

        with patch("src.nodes.extract_node.parse_document"):
            with patch("src.nodes.extract_node.RequirementsAnalystAgent"):
                # Should process without errors
                result = extract_node(state)


# =======================================================================
# Document Parsing Integration Tests (4 tests)
# =======================================================================

@pytest.mark.unit
@pytest.mark.phase1
class TestDocumentParsingIntegration:
    """Test integration with document parser."""

    def test_successful_document_parsing(self, valid_state):
        """Test successful document parsing."""
        with patch("src.nodes.extract_node.parse_document") as mock_parse:
            with patch("src.nodes.extract_node.RequirementsAnalystAgent") as mock_agent_class:
                mock_parse.return_value = ("Parsed text", "txt")
                mock_agent = Mock()
                mock_agent.extract_requirements.return_value = []
                mock_agent.get_error_summary.return_value = {
                    "error_log": [],
                    "fallback_count": 0
                }
                mock_agent_class.return_value = mock_agent

                result = extract_node(valid_state)

                # Parser should have been called
                mock_parse.assert_called_once()

    def test_document_parse_error_handling(self, valid_state):
        """Test handling of document parse errors (FATAL)."""
        with patch("src.nodes.extract_node.parse_document") as mock_parse:
            mock_parse.side_effect = DocumentParseError("File not found")

            result = extract_node(valid_state)

            # Should have errors
            assert "errors" in result
            assert len(result["errors"]) > 0
            assert "parsing failed" in result["errors"][0].lower()
            assert result.get("requires_human_review") == True

    def test_error_log_population_on_parse_failure(self, valid_state):
        """Test that error_log is populated on parse failure."""
        with patch("src.nodes.extract_node.parse_document") as mock_parse:
            mock_parse.side_effect = DocumentParseError("Corrupted file")

            result = extract_node(valid_state)

            # Should have error_log entries
            assert "error_log" in result
            assert len(result["error_log"]) > 0
            assert result["error_log"][0]["error_type"] == "fatal"

    def test_requires_human_review_flag_on_error(self, valid_state):
        """Test that requires_human_review flag is set on errors."""
        with patch("src.nodes.extract_node.parse_document") as mock_parse:
            mock_parse.side_effect = DocumentParseError("Error")

            result = extract_node(valid_state)

            assert result.get("requires_human_review") == True


# =======================================================================
# Agent Execution Tests (5 tests)
# =======================================================================

@pytest.mark.unit
@pytest.mark.phase1
class TestAgentExecution:
    """Test agent execution and error handling."""

    def test_successful_requirement_extraction(self, valid_state):
        """Test successful requirement extraction."""
        with patch("src.nodes.extract_node.parse_document") as mock_parse:
            with patch("src.nodes.extract_node.RequirementsAnalystAgent") as mock_agent_class:
                mock_parse.return_value = ("Test doc", "txt")

                mock_req1 = Requirement(
                    id="EXTRACT-FUNC-001",
                    text="Test req 1",
                    type=RequirementType.FUNCTIONAL
                )
                mock_req2 = Requirement(
                    id="EXTRACT-PERF-001",
                    text="Test req 2",
                    type=RequirementType.PERFORMANCE
                )

                mock_agent = Mock()
                mock_agent.extract_requirements.return_value = [mock_req1, mock_req2]
                mock_agent.get_error_summary.return_value = {
                    "error_log": [],
                    "fallback_count": 0
                }
                mock_agent_class.return_value = mock_agent

                result = extract_node(valid_state)

                # Should have extracted requirements
                assert "extracted_requirements" in result
                assert len(result["extracted_requirements"]) == 2

    def test_requirement_serialization_to_state(self, valid_state):
        """Test that requirements are serialized to dictionaries."""
        with patch("src.nodes.extract_node.parse_document") as mock_parse:
            with patch("src.nodes.extract_node.RequirementsAnalystAgent") as mock_agent_class:
                mock_parse.return_value = ("Test", "txt")

                mock_req = Requirement(
                    id="EXTRACT-FUNC-001",
                    text="Test",
                    type=RequirementType.FUNCTIONAL
                )

                mock_agent = Mock()
                mock_agent.extract_requirements.return_value = [mock_req]
                mock_agent.get_error_summary.return_value = {
                    "error_log": [],
                    "fallback_count": 0
                }
                mock_agent_class.return_value = mock_agent

                result = extract_node(valid_state)

                # Requirements should be serialized
                assert isinstance(result["extracted_requirements"], list)
                assert isinstance(result["extracted_requirements"][0], dict)
                assert result["extracted_requirements"][0]["id"] == "EXTRACT-FUNC-001"

    def test_agent_error_handling(self, valid_state):
        """Test handling of agent errors (CONTENT error)."""
        with patch("src.nodes.extract_node.parse_document") as mock_parse:
            with patch("src.nodes.extract_node.RequirementsAnalystAgent") as mock_agent_class:
                mock_parse.return_value = ("Test", "txt")

                mock_agent = Mock()
                mock_agent.extract_requirements.side_effect = AgentError("Extraction failed")
                mock_agent.get_error_summary.return_value = {
                    "error_log": [],
                    "fallback_count": 0
                }
                mock_agent_class.return_value = mock_agent

                result = extract_node(valid_state)

                # Should have errors
                assert "errors" in result
                assert "extraction failed" in result["errors"][0].lower()
                assert result.get("requires_human_review") == True

    def test_fallback_count_tracking(self, valid_state):
        """Test that fallback count is tracked."""
        with patch("src.nodes.extract_node.parse_document") as mock_parse:
            with patch("src.nodes.extract_node.RequirementsAnalystAgent") as mock_agent_class:
                mock_parse.return_value = ("Test", "txt")

                mock_agent = Mock()
                mock_agent.extract_requirements.return_value = []
                mock_agent.get_error_summary.return_value = {
                    "error_log": [],
                    "fallback_count": 2
                }
                mock_agent_class.return_value = mock_agent

                result = extract_node(valid_state)

                # Fallback count should be tracked
                assert result.get("fallback_count") == 2

    def test_multiple_requirements_extracted(self, valid_state):
        """Test extracting multiple requirements."""
        with patch("src.nodes.extract_node.parse_document") as mock_parse:
            with patch("src.nodes.extract_node.RequirementsAnalystAgent") as mock_agent_class:
                mock_parse.return_value = ("Test", "txt")

                # Create 5 requirements
                reqs = [
                    Requirement(
                        id=f"EXTRACT-FUNC-{i:03d}",
                        text=f"Requirement {i}",
                        type=RequirementType.FUNCTIONAL
                    )
                    for i in range(1, 6)
                ]

                mock_agent = Mock()
                mock_agent.extract_requirements.return_value = reqs
                mock_agent.get_error_summary.return_value = {
                    "error_log": [],
                    "fallback_count": 0
                }
                mock_agent_class.return_value = mock_agent

                result = extract_node(valid_state)

                assert len(result["extracted_requirements"]) == 5


# =======================================================================
# State Update Tests (4 tests)
# =======================================================================

@pytest.mark.unit
@pytest.mark.phase1
class TestStateUpdates:
    """Test state update logic."""

    def test_extracted_requirements_populated(self, valid_state):
        """Test that extracted_requirements is populated correctly."""
        with patch("src.nodes.extract_node.parse_document") as mock_parse:
            with patch("src.nodes.extract_node.RequirementsAnalystAgent") as mock_agent_class:
                mock_parse.return_value = ("Test", "txt")

                mock_agent = Mock()
                mock_agent.extract_requirements.return_value = [
                    Requirement(
                        id="EXTRACT-FUNC-001",
                        text="Test",
                        type=RequirementType.FUNCTIONAL
                    )
                ]
                mock_agent.get_error_summary.return_value = {
                    "error_log": [],
                    "fallback_count": 0
                }
                mock_agent_class.return_value = mock_agent

                result = extract_node(valid_state)

                assert "extracted_requirements" in result
                assert len(result["extracted_requirements"]) == 1

    def test_error_log_merging_from_agent(self, valid_state):
        """Test that error_log is merged from agent."""
        with patch("src.nodes.extract_node.parse_document") as mock_parse:
            with patch("src.nodes.extract_node.RequirementsAnalystAgent") as mock_agent_class:
                mock_parse.return_value = ("Test", "txt")

                agent_error_log = [
                    {
                        "timestamp": "2025-10-30T12:00:00",
                        "error_type": "transient",
                        "node": "extract",
                        "message": "Rate limit",
                        "details": {}
                    }
                ]

                mock_agent = Mock()
                mock_agent.extract_requirements.return_value = []
                mock_agent.get_error_summary.return_value = {
                    "error_log": agent_error_log,
                    "fallback_count": 0
                }
                mock_agent_class.return_value = mock_agent

                result = extract_node(valid_state)

                # Error log should be merged
                assert "error_log" in result
                assert len(result["error_log"]) == 1

    def test_fallback_count_incrementation(self, valid_state):
        """Test that fallback_count is incremented correctly."""
        # Start with existing fallback count
        state_with_fallback = {**valid_state, "fallback_count": 1}

        with patch("src.nodes.extract_node.parse_document") as mock_parse:
            with patch("src.nodes.extract_node.RequirementsAnalystAgent") as mock_agent_class:
                mock_parse.return_value = ("Test", "txt")

                mock_agent = Mock()
                mock_agent.extract_requirements.return_value = []
                mock_agent.get_error_summary.return_value = {
                    "error_log": [],
                    "fallback_count": 2  # Agent used fallback 2 times
                }
                mock_agent_class.return_value = mock_agent

                result = extract_node(state_with_fallback)

                # Should add agent's fallback count to state's
                assert result.get("fallback_count") == 3

    def test_state_consistency_on_failure(self, valid_state):
        """Test that state remains consistent on failure."""
        with patch("src.nodes.extract_node.parse_document") as mock_parse:
            mock_parse.side_effect = Exception("Unexpected error")

            result = extract_node(valid_state)

            # State should still have all original fields
            assert "spec_document_path" in valid_state
            # Error info should be added
            assert "errors" in result
            assert "error_log" in result


# =======================================================================
# Error Handling Tests (2 tests)
# =======================================================================

@pytest.mark.unit
@pytest.mark.phase1
class TestErrorHandling:
    """Test error handling and classification."""

    def test_unexpected_exceptions_caught(self, valid_state):
        """Test that unexpected exceptions are caught."""
        with patch("src.nodes.extract_node.parse_document") as mock_parse:
            mock_parse.side_effect = RuntimeError("Unexpected runtime error")

            result = extract_node(valid_state)

            # Should handle gracefully
            assert "errors" in result
            assert result.get("requires_human_review") == True

    def test_error_type_classification_in_state(self, valid_state):
        """Test that errors are classified correctly in state."""
        with patch("src.nodes.extract_node.parse_document") as mock_parse:
            mock_parse.side_effect = DocumentParseError("File not found")

            result = extract_node(valid_state)

            # Should classify as FATAL
            assert "error_log" in result
            assert len(result["error_log"]) > 0
            assert result["error_log"][0]["error_type"] == "fatal"
