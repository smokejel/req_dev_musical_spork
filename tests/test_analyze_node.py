"""
Unit tests for the analyze_node function.

Tests state handling, agent execution, strategy validation,
and error handling.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch

from src.nodes.analyze_node import analyze_node
from src.state import (
    create_initial_state,
    SystemContext,
    DecompositionStrategy,
    ErrorType
)
from src.agents.system_architect import AgentError


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
            "target_subsystem": "Test"
        }

        result = analyze_node(state)

        # Should have errors
        assert "errors" in result
        assert len(result["errors"]) > 0
        assert result.get("requires_human_review") == True

    def test_missing_target_subsystem_error(self):
        """Test that missing target_subsystem raises error."""
        state = {
            "extracted_requirements": [
                {"id": "EXTRACT-FUNC-001", "text": "Test", "type": "FUNC"}
            ]
        }

        result = analyze_node(state)

        # Should have errors
        assert "errors" in result
        assert len(result["errors"]) > 0
        assert result.get("requires_human_review") == True

    def test_empty_extracted_requirements_error(self):
        """Test that empty extracted_requirements raises error."""
        state = {
            "extracted_requirements": [],
            "target_subsystem": "Test Subsystem"
        }

        result = analyze_node(state)

        # Should have errors
        assert "errors" in result
        assert len(result["errors"]) > 0
        assert "no extracted requirements" in result["errors"][0].lower()

    def test_valid_state_processing(self, state_with_requirements):
        """Test that valid state is processed correctly."""
        with patch("src.nodes.analyze_node.SystemArchitectAgent") as mock_agent_class:
            mock_agent = Mock()
            mock_context = SystemContext(
                subsystem="Test",
                description="Test subsystem",
                constraints=[],
                interfaces=[],
                assumptions=[]
            )
            mock_strategy = DecompositionStrategy(
                allocation_rules=["Rule 1"],
                traceability_rules=["Rule 1"],
                decomposition_depth=1,
                naming_convention="TEST-{TYPE}-{NNN}",
                acceptance_criteria_required=True
            )
            mock_agent.analyze_system.return_value = (mock_context, mock_strategy)
            mock_agent.get_error_summary.return_value = {
                "error_log": [],
                "fallback_count": 0
            }
            mock_agent_class.return_value = mock_agent

            # Should not raise
            result = analyze_node(state_with_requirements)

            # Should have system_context and decomposition_strategy
            assert "system_context" in result
            assert "decomposition_strategy" in result


# =======================================================================
# Agent Execution Tests (5 tests)
# =======================================================================

@pytest.mark.unit
@pytest.mark.phase2
class TestAgentExecution:
    """Test agent execution and result handling."""

    def test_successful_analysis(self, state_with_requirements):
        """Test successful system analysis."""
        with patch("src.nodes.analyze_node.SystemArchitectAgent") as mock_agent_class:
            mock_agent = Mock()
            mock_context = SystemContext(
                subsystem="Navigation Subsystem",
                description="Handles navigation",
                constraints=["Constraint 1"],
                interfaces=["GPS"],
                assumptions=["GPS available"]
            )
            mock_strategy = DecompositionStrategy(
                allocation_rules=["IF navigation THEN allocate"],
                traceability_rules=["Must have parent_id"],
                decomposition_depth=1,
                naming_convention="NAV-{TYPE}-{NNN}",
                acceptance_criteria_required=True
            )
            mock_agent.analyze_system.return_value = (mock_context, mock_strategy)
            mock_agent.get_error_summary.return_value = {
                "error_log": [],
                "fallback_count": 0
            }
            mock_agent_class.return_value = mock_agent

            result = analyze_node(state_with_requirements)

            # Agent should have been called
            mock_agent.analyze_system.assert_called_once()

            # State should be updated
            assert result["system_context"]["subsystem"] == "Navigation Subsystem"
            assert result["decomposition_strategy"]["naming_convention"] == "NAV-{TYPE}-{NNN}"

    def test_system_context_serialization(self, state_with_requirements):
        """Test that SystemContext is properly serialized to dict."""
        with patch("src.nodes.analyze_node.SystemArchitectAgent") as mock_agent_class:
            mock_agent = Mock()
            mock_context = SystemContext(
                subsystem="Test",
                description="Test description",
                constraints=["C1", "C2"],
                interfaces=["I1"],
                assumptions=["A1"]
            )
            mock_strategy = DecompositionStrategy(
                allocation_rules=["Rule 1"],
                traceability_rules=["Rule 1"],
                decomposition_depth=1,
                naming_convention="TEST-{TYPE}-{NNN}",
                acceptance_criteria_required=True
            )
            mock_agent.analyze_system.return_value = (mock_context, mock_strategy)
            mock_agent.get_error_summary.return_value = {
                "error_log": [],
                "fallback_count": 0
            }
            mock_agent_class.return_value = mock_agent

            result = analyze_node(state_with_requirements)

            # Should be a dict, not a Pydantic model
            assert isinstance(result["system_context"], dict)
            assert result["system_context"]["subsystem"] == "Test"
            assert len(result["system_context"]["constraints"]) == 2

    def test_decomposition_strategy_serialization(self, state_with_requirements):
        """Test that DecompositionStrategy is properly serialized to dict."""
        with patch("src.nodes.analyze_node.SystemArchitectAgent") as mock_agent_class:
            mock_agent = Mock()
            mock_context = SystemContext(
                subsystem="Test",
                description="Test",
                constraints=[],
                interfaces=[],
                assumptions=[]
            )
            mock_strategy = DecompositionStrategy(
                allocation_rules=["Rule 1", "Rule 2"],
                traceability_rules=["Trace 1"],
                decomposition_depth=2,
                naming_convention="TEST-{TYPE}-{NNN}",
                acceptance_criteria_required=False
            )
            mock_agent.analyze_system.return_value = (mock_context, mock_strategy)
            mock_agent.get_error_summary.return_value = {
                "error_log": [],
                "fallback_count": 0
            }
            mock_agent_class.return_value = mock_agent

            result = analyze_node(state_with_requirements)

            # Should be a dict, not a Pydantic model
            assert isinstance(result["decomposition_strategy"], dict)
            assert len(result["decomposition_strategy"]["allocation_rules"]) == 2
            assert result["decomposition_strategy"]["decomposition_depth"] == 2

    def test_agent_error_handling(self, state_with_requirements):
        """Test handling of agent errors (CONTENT)."""
        with patch("src.nodes.analyze_node.SystemArchitectAgent") as mock_agent_class:
            mock_agent = Mock()
            mock_agent.analyze_system.side_effect = AgentError("Analysis failed")
            mock_agent.get_error_summary.return_value = {
                "error_log": [],
                "fallback_count": 0
            }
            mock_agent_class.return_value = mock_agent

            result = analyze_node(state_with_requirements)

            # Should have error
            assert "errors" in result
            assert "Analysis failed" in result["errors"][0]
            assert result.get("requires_human_review") == True

            # Error log should have CONTENT error type
            assert len(result["error_log"]) > 0
            assert result["error_log"][-1]["error_type"] == ErrorType.CONTENT

    def test_fallback_count_tracking(self, state_with_requirements):
        """Test that fallback count is tracked."""
        with patch("src.nodes.analyze_node.SystemArchitectAgent") as mock_agent_class:
            mock_agent = Mock()
            mock_context = SystemContext(
                subsystem="Test",
                description="Test",
                constraints=[],
                interfaces=[],
                assumptions=[]
            )
            mock_strategy = DecompositionStrategy(
                allocation_rules=["Rule 1"],
                traceability_rules=["Rule 1"],
                decomposition_depth=1,
                naming_convention="TEST-{TYPE}-{NNN}",
                acceptance_criteria_required=True
            )
            mock_agent.analyze_system.return_value = (mock_context, mock_strategy)
            mock_agent.get_error_summary.return_value = {
                "error_log": [],
                "fallback_count": 2  # Simulate 2 fallbacks
            }
            mock_agent_class.return_value = mock_agent

            # State with existing fallback_count
            state = {**state_with_requirements, "fallback_count": 1}

            result = analyze_node(state)

            # Fallback count should be incremented
            assert result["fallback_count"] == 3  # 1 + 2


# =======================================================================
# State Updates Tests (4 tests)
# =======================================================================

@pytest.mark.unit
@pytest.mark.phase2
class TestStateUpdates:
    """Test state update logic."""

    def test_system_context_populated(self, state_with_requirements):
        """Test that system_context is populated in state."""
        with patch("src.nodes.analyze_node.SystemArchitectAgent") as mock_agent_class:
            mock_agent = Mock()
            mock_context = SystemContext(
                subsystem="Test Subsystem",
                description="Test description",
                constraints=["C1"],
                interfaces=["I1"],
                assumptions=["A1"]
            )
            mock_strategy = DecompositionStrategy(
                allocation_rules=["Rule 1"],
                traceability_rules=["Rule 1"],
                decomposition_depth=1,
                naming_convention="TEST-{TYPE}-{NNN}",
                acceptance_criteria_required=True
            )
            mock_agent.analyze_system.return_value = (mock_context, mock_strategy)
            mock_agent.get_error_summary.return_value = {
                "error_log": [],
                "fallback_count": 0
            }
            mock_agent_class.return_value = mock_agent

            result = analyze_node(state_with_requirements)

            assert "system_context" in result
            assert result["system_context"]["subsystem"] == "Test Subsystem"

    def test_decomposition_strategy_populated(self, state_with_requirements):
        """Test that decomposition_strategy is populated in state."""
        with patch("src.nodes.analyze_node.SystemArchitectAgent") as mock_agent_class:
            mock_agent = Mock()
            mock_context = SystemContext(
                subsystem="Test",
                description="Test",
                constraints=[],
                interfaces=[],
                assumptions=[]
            )
            mock_strategy = DecompositionStrategy(
                allocation_rules=["Rule 1"],
                traceability_rules=["Rule 1"],
                decomposition_depth=1,
                naming_convention="NAV-{TYPE}-{NNN}",
                acceptance_criteria_required=True
            )
            mock_agent.analyze_system.return_value = (mock_context, mock_strategy)
            mock_agent.get_error_summary.return_value = {
                "error_log": [],
                "fallback_count": 0
            }
            mock_agent_class.return_value = mock_agent

            result = analyze_node(state_with_requirements)

            assert "decomposition_strategy" in result
            assert result["decomposition_strategy"]["naming_convention"] == "NAV-{TYPE}-{NNN}"

    def test_error_log_merging_from_agent(self, state_with_requirements):
        """Test that error log from agent is merged with state error log."""
        with patch("src.nodes.analyze_node.SystemArchitectAgent") as mock_agent_class:
            mock_agent = Mock()
            mock_context = SystemContext(
                subsystem="Test",
                description="Test",
                constraints=[],
                interfaces=[],
                assumptions=[]
            )
            mock_strategy = DecompositionStrategy(
                allocation_rules=["Rule 1"],
                traceability_rules=["Rule 1"],
                decomposition_depth=1,
                naming_convention="TEST-{TYPE}-{NNN}",
                acceptance_criteria_required=True
            )
            mock_agent.analyze_system.return_value = (mock_context, mock_strategy)
            mock_agent.get_error_summary.return_value = {
                "error_log": [
                    {
                        "timestamp": "2025-10-31T12:00:00",
                        "error_type": "TRANSIENT",
                        "node": "analyze",
                        "message": "Retry occurred",
                        "details": {}
                    }
                ],
                "fallback_count": 0
            }
            mock_agent_class.return_value = mock_agent

            result = analyze_node(state_with_requirements)

            # Error log should contain agent's errors
            assert "error_log" in result
            assert len(result["error_log"]) > 0

    def test_state_consistency_on_failure(self, state_with_requirements):
        """Test that state remains consistent even on failure."""
        with patch("src.nodes.analyze_node.SystemArchitectAgent") as mock_agent_class:
            mock_agent = Mock()
            mock_agent.analyze_system.side_effect = AgentError("Failure")
            mock_agent.get_error_summary.return_value = {
                "error_log": [],
                "fallback_count": 0
            }
            mock_agent_class.return_value = mock_agent

            # Add some existing state
            state = {
                **state_with_requirements,
                "errors": ["Existing error"],
                "error_log": [{"existing": "log"}]
            }

            result = analyze_node(state)

            # Original state should be preserved
            assert result["extracted_requirements"] == state_with_requirements["extracted_requirements"]
            assert "Existing error" in result["errors"]


# =======================================================================
# Error Handling Tests (2 tests)
# =======================================================================

@pytest.mark.unit
@pytest.mark.phase2
class TestErrorHandling:
    """Test error handling edge cases."""

    def test_unexpected_exception_caught(self, state_with_requirements):
        """Test that unexpected exceptions are caught and logged."""
        with patch("src.nodes.analyze_node.SystemArchitectAgent") as mock_agent_class:
            mock_agent_class.side_effect = RuntimeError("Unexpected error")

            result = analyze_node(state_with_requirements)

            # Should have error
            assert "errors" in result
            assert result.get("requires_human_review") == True

            # Error type should be FATAL
            assert len(result["error_log"]) > 0
            assert result["error_log"][-1]["error_type"] == ErrorType.FATAL

    def test_error_type_classification_in_state(self, state_with_requirements):
        """Test that error types are correctly classified."""
        with patch("src.nodes.analyze_node.SystemArchitectAgent") as mock_agent_class:
            mock_agent = Mock()
            mock_agent.analyze_system.side_effect = AgentError("Content error")
            mock_agent.get_error_summary.return_value = {
                "error_log": [],
                "fallback_count": 0
            }
            mock_agent_class.return_value = mock_agent

            result = analyze_node(state_with_requirements)

            # AgentError should be classified as CONTENT
            assert result["error_log"][-1]["error_type"] == ErrorType.CONTENT
            assert result["error_log"][-1]["node"] == "analyze"
