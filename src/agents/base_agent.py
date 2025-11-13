"""
Base agent architecture with skill loading and LLM fallback handling.

Provides abstract base class for all agents in the decomposition workflow.
Implements error taxonomy, retry logic, and intelligent fallback between models.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, List, Optional, Dict
import time
from datetime import datetime
from enum import Enum

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models import BaseChatModel

from src.utils.skill_loader import load_skill, SkillLoadError
from src.utils.langsmith_integration import extract_tokens_from_response
from src.utils.cost_tracker import get_cost_tracker
from src.state import ErrorType, ErrorLog
from config.llm_config import (
    ModelConfig,
    ModelProvider,
    NodeType,
    get_primary_model,
    get_fallback_models,
    RETRY_MAX_ATTEMPTS,
    RETRY_INITIAL_DELAY,
    RETRY_BACKOFF_FACTOR,
    RETRY_MAX_DELAY
)
from config.observability_config import ObservabilityConfig


class AgentError(Exception):
    """Base exception for agent errors."""
    pass


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the workflow.

    Provides:
    - Skill loading from SKILL.md files
    - LLM instantiation with fallback logic
    - Error handling with retry/fallback based on error taxonomy
    - Execution tracking and error logging
    """

    def __init__(
        self,
        node_type: NodeType,
        skill_name: Optional[str] = None
    ):
        """
        Initialize the base agent.

        Args:
            node_type: Type of workflow node this agent serves
            skill_name: Name of the skill to load (if None, no skill is loaded)
        """
        self.node_type = node_type
        self.skill_name = skill_name
        self.skill_content: Optional[str] = None

        # Model configuration
        self.primary_model_config = get_primary_model(node_type)
        self.fallback_model_configs = get_fallback_models(node_type)

        # Execution tracking
        self.execution_count = 0
        self.fallback_count = 0
        self.error_log: List[ErrorLog] = []

        # Load skill if specified
        if skill_name:
            self._load_skill()

    def _load_skill(self) -> None:
        """
        Load the skill content from SKILL.md file.

        Raises:
            AgentError: If skill loading fails
        """
        try:
            self.skill_content = load_skill(self.skill_name)
        except SkillLoadError as e:
            raise AgentError(f"Failed to load skill '{self.skill_name}': {str(e)}")

    def get_skill_content(self) -> str:
        """
        Get the loaded skill content.

        Returns:
            Skill content as string

        Raises:
            AgentError: If no skill is loaded
        """
        if self.skill_content is None:
            raise AgentError(
                f"No skill loaded. Initialize agent with skill_name parameter."
            )
        return self.skill_content

    def _create_llm(self, model_config: ModelConfig) -> BaseChatModel:
        """
        Create an LLM instance from a model configuration.

        Args:
            model_config: Model configuration to instantiate

        Returns:
            Instantiated LLM

        Raises:
            AgentError: If model instantiation fails
        """
        try:
            if model_config.provider == ModelProvider.OPENAI:
                return ChatOpenAI(
                    model=model_config.name,
                    temperature=model_config.temperature,
                    max_tokens=model_config.max_tokens
                )

            elif model_config.provider == ModelProvider.ANTHROPIC:
                return ChatAnthropic(
                    model=model_config.name,
                    temperature=model_config.temperature,
                    max_tokens=model_config.max_tokens
                )

            elif model_config.provider == ModelProvider.GOOGLE:
                return ChatGoogleGenerativeAI(
                    model=model_config.name,
                    temperature=model_config.temperature,
                    max_output_tokens=model_config.max_tokens
                )

            else:
                raise AgentError(
                    f"Unknown provider: {model_config.provider}"
                )

        except Exception as e:
            raise AgentError(
                f"Failed to instantiate model {model_config.name}: {str(e)}"
            )

    def get_llm(self, use_primary: bool = True) -> BaseChatModel:
        """
        Get an LLM instance.

        Args:
            use_primary: If True, use primary model; if False, use first fallback

        Returns:
            Instantiated LLM
        """
        if use_primary:
            return self._create_llm(self.primary_model_config)
        else:
            if not self.fallback_model_configs:
                raise AgentError("No fallback models available")
            return self._create_llm(self.fallback_model_configs[0])

    def _classify_error(self, error: Exception) -> ErrorType:
        """
        Classify an error into the error taxonomy.

        Args:
            error: Exception to classify

        Returns:
            ErrorType classification
        """
        error_str = str(error).lower()
        error_type_name = type(error).__name__.lower()

        # Transient errors (retry same model)
        transient_keywords = [
            'rate limit', 'timeout', 'connection', 'temporary',
            '503', '429', '500', 'server error', 'overloaded'
        ]

        # Content errors (switch to fallback model)
        content_keywords = [
            'parse', 'json', 'validation', 'format', 'invalid',
            'decode', 'schema', 'malformed'
        ]

        # Fatal errors (human intervention)
        fatal_keywords = [
            'authentication', 'auth', 'api key', 'permission',
            'not found', '404', '401', '403', 'missing resource'
        ]

        # Check for fatal first
        if any(keyword in error_str or keyword in error_type_name for keyword in fatal_keywords):
            return ErrorType.FATAL

        # Check for transient
        if any(keyword in error_str or keyword in error_type_name for keyword in transient_keywords):
            return ErrorType.TRANSIENT

        # Check for content
        if any(keyword in error_str or keyword in error_type_name for keyword in content_keywords):
            return ErrorType.CONTENT

        # Default to content error (switch model)
        return ErrorType.CONTENT

    def _log_error(
        self,
        error_type: ErrorType,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an error to the error log.

        Args:
            error_type: Type of error
            message: Error message
            details: Additional error details
        """
        error_entry = ErrorLog(
            timestamp=datetime.utcnow().isoformat(),
            error_type=error_type,
            node=self.node_type.value,
            message=message,
            details=details or {}
        )
        self.error_log.append(error_entry)

    def _track_cost(
        self,
        response: Any,
        model_config: ModelConfig
    ) -> Optional[float]:
        """
        Track cost for an LLM response.

        Args:
            response: LLM response object
            model_config: Model configuration used

        Returns:
            Cost in dollars, or None if tracking disabled
        """
        if not ObservabilityConfig.COST_TRACKING_ENABLED:
            return None

        try:
            # Extract token counts from response
            input_tokens, output_tokens = extract_tokens_from_response(response)

            # Calculate cost
            cost_tracker = get_cost_tracker()
            cost = cost_tracker.calculate_node_cost(
                self.node_type,
                input_tokens,
                output_tokens,
                model_config
            )

            # Record in tracker
            cost_tracker.record_node_cost(
                node_name=self.node_type.value,
                cost=cost,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                model_name=model_config.name
            )

            return cost

        except Exception as e:
            # Don't fail execution if cost tracking fails
            print(f"Warning: Cost tracking failed: {e}")
            return None

    def _retry_with_backoff(
        self,
        func: Callable[[], Any],
        max_attempts: int = RETRY_MAX_ATTEMPTS,
        initial_delay: float = RETRY_INITIAL_DELAY
    ) -> Any:
        """
        Retry a function with exponential backoff.

        Args:
            func: Function to retry
            max_attempts: Maximum retry attempts
            initial_delay: Initial delay in seconds

        Returns:
            Function result

        Raises:
            Exception: Last exception if all retries fail
        """
        delay = initial_delay

        for attempt in range(max_attempts):
            try:
                return func()
            except Exception as e:
                error_type = self._classify_error(e)

                if error_type != ErrorType.TRANSIENT or attempt == max_attempts - 1:
                    raise

                # Log transient error
                self._log_error(
                    error_type=ErrorType.TRANSIENT,
                    message=f"Transient error on attempt {attempt + 1}: {str(e)}",
                    details={'attempt': attempt + 1, 'delay': delay}
                )

                # Wait with exponential backoff
                time.sleep(delay)
                delay = min(delay * RETRY_BACKOFF_FACTOR, RETRY_MAX_DELAY)

        raise AgentError("All retry attempts failed")

    def execute_with_fallback(
        self,
        execution_func: Callable[[BaseChatModel], Any],
        enable_fallback: bool = True
    ) -> Any:
        """
        Execute a function with LLM fallback logic.

        This is the main execution method that handles:
        1. Retry with exponential backoff for transient errors
        2. Model fallback for content errors
        3. Error logging and tracking

        Args:
            execution_func: Function that takes an LLM and returns a result
            enable_fallback: Whether to enable fallback to alternate models

        Returns:
            Result from execution_func

        Raises:
            AgentError: If all attempts fail
        """
        self.execution_count += 1

        # Try primary model with retry
        try:
            llm = self.get_llm(use_primary=True)
            result = self._retry_with_backoff(lambda: execution_func(llm))

            # Track cost for successful execution
            self._track_cost(result, self.primary_model_config)

            return result

        except Exception as primary_error:
            error_type = self._classify_error(primary_error)

            # Log primary model failure
            self._log_error(
                error_type=error_type,
                message=f"Primary model failed: {str(primary_error)}",
                details={
                    'model': self.primary_model_config.name,
                    'execution_count': self.execution_count
                }
            )

            # Fatal errors - don't retry with fallback
            if error_type == ErrorType.FATAL:
                raise AgentError(
                    f"Fatal error with primary model: {str(primary_error)}"
                )

            # Content errors - try fallback if enabled
            if error_type == ErrorType.CONTENT and enable_fallback:
                if not self.fallback_model_configs:
                    raise AgentError(
                        f"No fallback models available after primary model failed"
                    )

                self.fallback_count += 1

                # Try first fallback model
                try:
                    llm = self.get_llm(use_primary=False)
                    result = self._retry_with_backoff(lambda: execution_func(llm))

                    # Track cost for fallback execution
                    self._track_cost(result, self.fallback_model_configs[0])

                    # Log successful fallback
                    self._log_error(
                        error_type=ErrorType.CONTENT,
                        message=f"Fallback successful with {self.fallback_model_configs[0].name}",
                        details={
                            'primary_model': self.primary_model_config.name,
                            'fallback_model': self.fallback_model_configs[0].name,
                            'fallback_count': self.fallback_count
                        }
                    )

                    return result

                except Exception as fallback_error:
                    self._log_error(
                        error_type=self._classify_error(fallback_error),
                        message=f"Fallback model also failed: {str(fallback_error)}",
                        details={
                            'fallback_model': self.fallback_model_configs[0].name
                        }
                    )

                    raise AgentError(
                        f"Both primary and fallback models failed. "
                        f"Primary: {str(primary_error)}. "
                        f"Fallback: {str(fallback_error)}"
                    )

            # Re-raise if no fallback or fallback disabled
            raise AgentError(f"Execution failed: {str(primary_error)}")

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """
        Execute the agent's main task.

        Must be implemented by subclasses.
        """
        pass

    def get_error_summary(self) -> Dict[str, Any]:
        """
        Get a summary of errors encountered.

        Returns:
            Dictionary with error statistics
        """
        return {
            'total_executions': self.execution_count,
            'fallback_count': self.fallback_count,
            'total_errors': len(self.error_log),
            'error_types': {
                'transient': sum(1 for e in self.error_log if e.error_type == ErrorType.TRANSIENT),
                'content': sum(1 for e in self.error_log if e.error_type == ErrorType.CONTENT),
                'fatal': sum(1 for e in self.error_log if e.error_type == ErrorType.FATAL)
            },
            'error_log': [e.model_dump() for e in self.error_log]
        }
