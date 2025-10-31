"""
Unit tests for the BaseAgent class.

Tests error classification, retry logic, LLM fallback, and error logging.
"""

import pytest
import time
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime

from src.agents.base_agent import BaseAgent, AgentError
from src.state import ErrorType
from config.llm_config import NodeType, ModelProvider


# =======================================================================
# Concrete Test Implementation of BaseAgent
# =======================================================================

class TestAgent(BaseAgent):
    """Concrete implementation of BaseAgent for testing purposes."""

    def execute(self, *args, **kwargs):
        """Implement abstract execute method for testing."""
        return "test_result"


# =======================================================================
# Error Classification Tests (10 tests)
# =======================================================================

@pytest.mark.unit
@pytest.mark.phase1
class TestErrorClassification:
    """Test error classification taxonomy."""

    @pytest.fixture
    def base_agent(self):
        """Create a base agent for testing."""
        return TestAgent(node_type=NodeType.EXTRACT, skill_name=None)

    def test_classify_rate_limit_error_as_transient(self, base_agent):
        """Test that rate limit errors are classified as transient."""
        error = Exception("Rate limit exceeded - 429")

        error_type = base_agent._classify_error(error)

        assert error_type == ErrorType.TRANSIENT

    def test_classify_timeout_error_as_transient(self, base_agent):
        """Test that timeout errors are classified as transient."""
        error = Exception("Connection timeout occurred")

        error_type = base_agent._classify_error(error)

        assert error_type == ErrorType.TRANSIENT

    def test_classify_503_error_as_transient(self, base_agent):
        """Test that 503 errors are classified as transient."""
        error = Exception("Server error - 503 Service Unavailable")

        error_type = base_agent._classify_error(error)

        assert error_type == ErrorType.TRANSIENT

    def test_classify_json_decode_error_as_content(self, base_agent):
        """Test that JSON decode errors are classified as content."""
        import json
        error = json.JSONDecodeError("Invalid JSON", "doc", 0)

        error_type = base_agent._classify_error(error)

        assert error_type == ErrorType.CONTENT

    def test_classify_parse_error_as_content(self, base_agent):
        """Test that parse errors are classified as content."""
        error = Exception("Parse error: malformed response")

        error_type = base_agent._classify_error(error)

        assert error_type == ErrorType.CONTENT

    def test_classify_validation_error_as_content(self, base_agent):
        """Test that validation errors are classified as content."""
        error = Exception("Validation failed: invalid format")

        error_type = base_agent._classify_error(error)

        assert error_type == ErrorType.CONTENT

    def test_classify_401_error_as_fatal(self, base_agent):
        """Test that 401 errors are classified as fatal."""
        error = Exception("Authentication failed - 401 Unauthorized")

        error_type = base_agent._classify_error(error)

        assert error_type == ErrorType.FATAL

    def test_classify_403_error_as_fatal(self, base_agent):
        """Test that 403 errors are classified as fatal."""
        error = Exception("Permission denied - 403 Forbidden")

        error_type = base_agent._classify_error(error)

        assert error_type == ErrorType.FATAL

    def test_classify_missing_resource_as_fatal(self, base_agent):
        """Test that missing resource errors are classified as fatal."""
        error = Exception("Resource not found - 404")

        error_type = base_agent._classify_error(error)

        assert error_type == ErrorType.FATAL

    def test_unknown_error_defaults_to_content(self, base_agent):
        """Test that unknown errors default to content."""
        error = Exception("Some unknown error occurred")

        error_type = base_agent._classify_error(error)

        # Default behavior is to switch models
        assert error_type == ErrorType.CONTENT


# =======================================================================
# LLM Instantiation Tests (3 tests)
# =======================================================================

@pytest.mark.unit
@pytest.mark.phase1
class TestLLMInstantiation:
    """Test LLM model instantiation."""

    def test_create_openai_model(self):
        """Test creating an OpenAI model."""
        agent = TestAgent(node_type=NodeType.EXTRACT, skill_name=None)

        with patch('src.agents.base_agent.ChatOpenAI') as mock_openai:
            llm = agent.get_llm(use_primary=True)

            # Verify ChatOpenAI was called with correct parameters
            mock_openai.assert_called_once()
            call_kwargs = mock_openai.call_args.kwargs
            assert 'model' in call_kwargs
            assert 'temperature' in call_kwargs
            assert 'max_tokens' in call_kwargs

    def test_create_anthropic_model(self):
        """Test creating an Anthropic model."""
        # Use a node that has Anthropic as primary
        agent = TestAgent(node_type=NodeType.ANALYZE, skill_name=None)

        with patch('src.agents.base_agent.ChatAnthropic') as mock_anthropic:
            llm = agent.get_llm(use_primary=True)

            # Verify ChatAnthropic was called
            mock_anthropic.assert_called_once()

    def test_invalid_provider_raises_error(self):
        """Test that invalid provider raises AgentError."""
        agent = TestAgent(node_type=NodeType.EXTRACT, skill_name=None)

        # Mock an invalid provider
        with patch.object(agent, 'primary_model_config') as mock_config:
            mock_config.provider = "invalid_provider"
            mock_config.name = "test-model"

            with pytest.raises(AgentError, match="Unknown provider"):
                agent._create_llm(mock_config)


# =======================================================================
# Retry Logic Tests (5 tests)
# =======================================================================

@pytest.mark.unit
@pytest.mark.phase1
class TestRetryLogic:
    """Test retry with exponential backoff."""

    @pytest.fixture
    def base_agent(self):
        """Create a base agent for testing."""
        return TestAgent(node_type=NodeType.EXTRACT, skill_name=None)

    def test_successful_retry_after_transient_error(self, base_agent):
        """Test that transient errors trigger retry and eventually succeed."""
        call_count = 0

        def failing_then_succeeding():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Rate limit - 429")
            return "success"

        result = base_agent._retry_with_backoff(failing_then_succeeding, max_attempts=3)

        assert result == "success"
        assert call_count == 2  # Failed once, succeeded on second try

    def test_max_attempts_exhausted(self, base_agent):
        """Test that max attempts are respected."""
        def always_failing():
            raise Exception("Rate limit - 429")

        with pytest.raises(Exception, match="Rate limit"):
            base_agent._retry_with_backoff(always_failing, max_attempts=3)

    def test_exponential_backoff_delays(self, base_agent):
        """Test that backoff delays increase exponentially."""
        call_times = []

        def failing_function():
            call_times.append(time.time())
            raise Exception("Timeout")

        with pytest.raises(Exception):
            base_agent._retry_with_backoff(
                failing_function,
                max_attempts=3,
                initial_delay=0.1
            )

        # Should have 3 attempts
        assert len(call_times) == 3

        # Delays should increase (allowing some timing variation)
        # First attempt: immediate
        # Second attempt: after ~0.1s
        # Third attempt: after ~0.2s
        if len(call_times) >= 2:
            delay1 = call_times[1] - call_times[0]
            assert delay1 >= 0.09  # Allow for timing variation

    def test_non_transient_error_immediate_failure(self, base_agent):
        """Test that non-transient errors don't retry."""
        call_count = 0

        def content_error_function():
            nonlocal call_count
            call_count += 1
            raise Exception("Parse error occurred")

        with pytest.raises(Exception, match="Parse error"):
            base_agent._retry_with_backoff(content_error_function, max_attempts=3)

        # Should only be called once (no retries for content errors)
        assert call_count == 1

    def test_successful_first_attempt_no_retry(self, base_agent):
        """Test that successful first attempt doesn't retry."""
        call_count = 0

        def successful_function():
            nonlocal call_count
            call_count += 1
            return "success"

        result = base_agent._retry_with_backoff(successful_function, max_attempts=3)

        assert result == "success"
        assert call_count == 1  # No retries needed


# =======================================================================
# Fallback Execution Tests (8 tests)
# =======================================================================

@pytest.mark.unit
@pytest.mark.phase1
class TestFallbackExecution:
    """Test LLM fallback execution logic."""

    @pytest.fixture
    def base_agent(self):
        """Create a base agent for testing."""
        return TestAgent(node_type=NodeType.EXTRACT, skill_name=None)

    def test_primary_model_success_no_fallback(self, base_agent):
        """Test that primary model success doesn't use fallback."""
        def execution_func(llm):
            return "success"

        with patch.object(base_agent, 'get_llm') as mock_get_llm:
            mock_llm = Mock()
            mock_get_llm.return_value = mock_llm

            result = base_agent.execute_with_fallback(execution_func)

            assert result == "success"
            assert base_agent.fallback_count == 0
            # Should only call get_llm once for primary
            assert mock_get_llm.call_count == 1

    def test_transient_error_retry_then_success(self, base_agent):
        """Test that transient errors trigger retry and succeed."""
        call_count = 0

        def execution_func(llm):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Rate limit - 429")
            return "success"

        result = base_agent.execute_with_fallback(execution_func)

        assert result == "success"
        assert base_agent.fallback_count == 0  # No fallback needed

    def test_content_error_triggers_fallback(self, base_agent):
        """Test that content errors trigger fallback to secondary model."""
        primary_called = False
        fallback_called = False

        def execution_func(llm):
            nonlocal primary_called, fallback_called
            if not primary_called:
                primary_called = True
                raise Exception("JSON parse error")
            else:
                fallback_called = True
                return "success_from_fallback"

        with patch.object(base_agent, '_retry_with_backoff') as mock_retry:
            # First call (primary) raises error, second call (fallback) succeeds
            mock_retry.side_effect = [
                Exception("JSON parse error"),
                "success_from_fallback"
            ]

            result = base_agent.execute_with_fallback(execution_func)

            assert result == "success_from_fallback"
            assert base_agent.fallback_count == 1

    def test_fatal_error_no_fallback(self, base_agent):
        """Test that fatal errors don't trigger fallback."""
        def execution_func(llm):
            raise Exception("Authentication failed - 401")

        with pytest.raises(AgentError, match="Fatal error"):
            base_agent.execute_with_fallback(execution_func)

        assert base_agent.fallback_count == 0  # No fallback attempted

    def test_both_models_fail(self, base_agent):
        """Test behavior when both primary and fallback models fail."""
        def execution_func(llm):
            raise Exception("Validation error")

        with patch.object(base_agent, '_retry_with_backoff') as mock_retry:
            # Both primary and fallback raise errors
            mock_retry.side_effect = [
                Exception("Validation error"),  # Primary
                Exception("Validation error")   # Fallback
            ]

            with pytest.raises(AgentError, match="Both primary and fallback"):
                base_agent.execute_with_fallback(execution_func)

    def test_fallback_disabled(self, base_agent):
        """Test that fallback can be disabled."""
        def execution_func(llm):
            raise Exception("Parse error")

        with pytest.raises(AgentError):
            base_agent.execute_with_fallback(execution_func, enable_fallback=False)

        assert base_agent.fallback_count == 0

    def test_fallback_count_tracking(self, base_agent):
        """Test that fallback count is tracked correctly."""
        def execution_func(llm):
            raise Exception("Parse error")

        with patch.object(base_agent, '_retry_with_backoff') as mock_retry:
            mock_retry.side_effect = [
                Exception("Parse error"),
                "success"
            ]

            base_agent.execute_with_fallback(execution_func)
            assert base_agent.fallback_count == 1

            # Call again
            mock_retry.side_effect = [
                Exception("Parse error"),
                "success"
            ]

            base_agent.execute_with_fallback(execution_func)
            assert base_agent.fallback_count == 2

    def test_execution_count_tracking(self, base_agent):
        """Test that execution count is tracked."""
        def execution_func(llm):
            return "success"

        assert base_agent.execution_count == 0

        base_agent.execute_with_fallback(execution_func)
        assert base_agent.execution_count == 1

        base_agent.execute_with_fallback(execution_func)
        assert base_agent.execution_count == 2


# =======================================================================
# Error Logging Tests (4 tests)
# =======================================================================

@pytest.mark.unit
@pytest.mark.phase1
class TestErrorLogging:
    """Test error logging functionality."""

    @pytest.fixture
    def base_agent(self):
        """Create a base agent for testing."""
        return TestAgent(node_type=NodeType.EXTRACT, skill_name=None)

    def test_error_log_entry_creation(self, base_agent):
        """Test that error log entries are created correctly."""
        base_agent._log_error(
            error_type=ErrorType.TRANSIENT,
            message="Test error message",
            details={"attempt": 1, "delay": 2.0}
        )

        assert len(base_agent.error_log) == 1
        error_entry = base_agent.error_log[0]

        assert error_entry.error_type == ErrorType.TRANSIENT
        assert error_entry.message == "Test error message"
        assert error_entry.node == "extract"
        assert error_entry.details["attempt"] == 1
        assert error_entry.details["delay"] == 2.0

    def test_timestamp_recorded(self, base_agent):
        """Test that timestamps are recorded in ISO format."""
        base_agent._log_error(
            error_type=ErrorType.CONTENT,
            message="Test message"
        )

        error_entry = base_agent.error_log[0]
        # Should be able to parse as ISO datetime
        datetime.fromisoformat(error_entry.timestamp)

    def test_details_captured(self, base_agent):
        """Test that error details are captured."""
        details = {
            "model": "gpt-4o-mini",
            "attempt": 3,
            "error_code": "500"
        }

        base_agent._log_error(
            error_type=ErrorType.TRANSIENT,
            message="Server error",
            details=details
        )

        error_entry = base_agent.error_log[0]
        assert error_entry.details == details

    def test_error_summary_generation(self, base_agent):
        """Test that error summary is generated correctly."""
        # Log various errors
        base_agent._log_error(ErrorType.TRANSIENT, "Error 1")
        base_agent._log_error(ErrorType.TRANSIENT, "Error 2")
        base_agent._log_error(ErrorType.CONTENT, "Error 3")
        base_agent._log_error(ErrorType.FATAL, "Error 4")

        base_agent.execution_count = 5
        base_agent.fallback_count = 2

        summary = base_agent.get_error_summary()

        assert summary["total_executions"] == 5
        assert summary["fallback_count"] == 2
        assert summary["total_errors"] == 4
        assert summary["error_types"]["transient"] == 2
        assert summary["error_types"]["content"] == 1
        assert summary["error_types"]["fatal"] == 1
        assert len(summary["error_log"]) == 4
