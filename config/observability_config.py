"""
Observability and cost tracking configuration for Phase 5.1.

Handles LangSmith integration, cost tracking, and budget management.
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class ObservabilityConfig:
    """Configuration for observability features."""

    # LangSmith Tracing
    LANGSMITH_ENABLED = os.getenv('LANGCHAIN_TRACING_V2', 'false').lower() == 'true'
    LANGSMITH_ENDPOINT = os.getenv('LANGCHAIN_ENDPOINT', 'https://api.smith.langchain.com')
    LANGSMITH_API_KEY = os.getenv('LANGCHAIN_API_KEY')
    LANGSMITH_PROJECT = os.getenv('LANGCHAIN_PROJECT', 'requirements-decomposition')

    # Cost Tracking
    COST_TRACKING_ENABLED = os.getenv('COST_TRACKING_ENABLED', 'true').lower() == 'true'
    COST_BUDGET_WARNING_THRESHOLD = float(os.getenv('COST_BUDGET_WARNING_THRESHOLD', '1.00'))
    COST_BUDGET_MAX = float(os.getenv('COST_BUDGET_MAX', '5.00'))

    @classmethod
    def is_langsmith_configured(cls) -> bool:
        """Check if LangSmith is properly configured."""
        return (
            cls.LANGSMITH_ENABLED and
            cls.LANGSMITH_API_KEY is not None and
            cls.LANGSMITH_API_KEY != 'your_langsmith_key_here'
        )

    @classmethod
    def get_langsmith_settings(cls) -> dict:
        """Get LangSmith settings for environment configuration."""
        if not cls.is_langsmith_configured():
            return {}

        return {
            'LANGCHAIN_TRACING_V2': 'true',
            'LANGCHAIN_ENDPOINT': cls.LANGSMITH_ENDPOINT,
            'LANGCHAIN_API_KEY': cls.LANGSMITH_API_KEY,
            'LANGCHAIN_PROJECT': cls.LANGSMITH_PROJECT,
        }

    @classmethod
    def setup_langsmith(cls) -> bool:
        """
        Set up LangSmith tracing in the environment.

        Returns:
            True if LangSmith is configured and enabled, False otherwise
        """
        if cls.is_langsmith_configured():
            # Set environment variables for LangChain
            for key, value in cls.get_langsmith_settings().items():
                os.environ[key] = value
            return True
        return False


# Initialize on import
LANGSMITH_ACTIVE = ObservabilityConfig.setup_langsmith()
