"""
LLM configuration and model definitions for the requirements decomposition workflow.

Defines primary and fallback models for each node, along with their parameters.
Based on MODEL_DEFINITIONS.md and the architecture in CLAUDE.md.
"""

from typing import Dict, List, Optional
from enum import Enum
from dataclasses import dataclass


class ModelProvider(str, Enum):
    """LLM provider enumeration."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


class NodeType(str, Enum):
    """Workflow node types."""
    EXTRACT = "extract"
    ANALYZE = "analyze"
    DECOMPOSE = "decompose"
    VALIDATE = "validate"


@dataclass
class ModelConfig:
    """Configuration for a specific LLM model."""

    name: str
    """Model identifier (e.g., 'gpt-4o', 'claude-sonnet-4-5-20250929')"""

    provider: ModelProvider
    """Provider (OpenAI, Anthropic, Google)"""

    temperature: float = 0.0
    """Temperature parameter for deterministic outputs"""

    max_tokens: int = 8192
    """Maximum tokens in response"""

    cost_per_1k_input: float = 0.0
    """Cost per 1K input tokens in USD"""

    cost_per_1k_output: float = 0.0
    """Cost per 1K output tokens in USD"""

    description: str = ""
    """Model description and use case"""


# ============================================================================
# Model Definitions
# ============================================================================

# OpenAI Models
GPT_4O = ModelConfig(
    name="gpt-4o",
    provider=ModelProvider.OPENAI,
    temperature=0.0,
    max_tokens=8192,
    cost_per_1k_input=0.0025,
    cost_per_1k_output=0.01,
    description="GPT-4 Optimized - Best for complex reasoning tasks"
)

GPT_4O_MINI = ModelConfig(
    name="gpt-4o-mini",
    provider=ModelProvider.OPENAI,
    temperature=0.0,
    max_tokens=8192,
    cost_per_1k_input=0.00015,
    cost_per_1k_output=0.0006,
    description="GPT-4 Mini - Cost-effective for structured extraction"
)

# Anthropic Models
CLAUDE_SONNET_4_5 = ModelConfig(
    name="claude-sonnet-4-5-20250929",
    provider=ModelProvider.ANTHROPIC,
    temperature=0.0,
    max_tokens=8192,
    cost_per_1k_input=0.003,
    cost_per_1k_output=0.015,
    description="Claude Sonnet 4.5 - Excellent for analysis and validation"
)

CLAUDE_SONNET_3_5 = ModelConfig(
    name="claude-3-5-sonnet-20241022",
    provider=ModelProvider.ANTHROPIC,
    temperature=0.1,
    max_tokens=8192,
    cost_per_1k_input=0.003,
    cost_per_1k_output=0.015,
    description="Claude 3.5 Sonnet - Strong architectural reasoning"
)

# Google Models (for future phases)
GEMINI_1_5_PRO = ModelConfig(
    name="gemini-1.5-pro",
    provider=ModelProvider.GOOGLE,
    temperature=0.0,
    max_tokens=8192,
    cost_per_1k_input=0.00125,
    cost_per_1k_output=0.005,
    description="Gemini 1.5 Pro - Alternative for analysis tasks"
)


# ============================================================================
# Node-Specific Model Assignments
# ============================================================================

@dataclass
class NodeModelConfig:
    """Model configuration for a specific workflow node."""

    node_type: NodeType
    primary_model: ModelConfig
    fallback_models: List[ModelConfig]
    rationale: str


# Model assignments based on CLAUDE.md Section "LLM Model Assignment"
NODE_MODELS = {
    NodeType.EXTRACT: NodeModelConfig(
        node_type=NodeType.EXTRACT,
        primary_model=GPT_4O_MINI,
        fallback_models=[GPT_4O, CLAUDE_SONNET_4_5],
        rationale="Cost optimization for structured extraction. GPT-4o-mini is sufficient for parsing and ID formatting."
    ),

    NodeType.ANALYZE: NodeModelConfig(
        node_type=NodeType.ANALYZE,
        primary_model=CLAUDE_SONNET_3_5,
        fallback_models=[GPT_4O, CLAUDE_SONNET_4_5],
        rationale="Architectural reasoning and context understanding. Claude excels at system-level analysis."
    ),

    NodeType.DECOMPOSE: NodeModelConfig(
        node_type=NodeType.DECOMPOSE,
        primary_model=GPT_4O,
        fallback_models=[CLAUDE_SONNET_4_5, CLAUDE_SONNET_3_5],
        rationale="Complex reasoning and consistency. GPT-4o provides reliable decomposition with strong instruction following."
    ),

    NodeType.VALIDATE: NodeModelConfig(
        node_type=NodeType.VALIDATE,
        primary_model=CLAUDE_SONNET_4_5,
        fallback_models=[CLAUDE_SONNET_3_5, GPT_4O],
        rationale="Critical evaluation and quality assessment. Claude Sonnet 4.5 provides rigorous validation."
    )
}


# ============================================================================
# Configuration Helper Functions
# ============================================================================

def get_primary_model(node_type: NodeType) -> ModelConfig:
    """
    Get the primary model configuration for a node.

    Args:
        node_type: Type of workflow node

    Returns:
        Primary ModelConfig for that node
    """
    return NODE_MODELS[node_type].primary_model


def get_fallback_models(node_type: NodeType) -> List[ModelConfig]:
    """
    Get the fallback model configurations for a node.

    Args:
        node_type: Type of workflow node

    Returns:
        List of fallback ModelConfigs
    """
    return NODE_MODELS[node_type].fallback_models


def get_model_by_name(model_name: str) -> Optional[ModelConfig]:
    """
    Get a model configuration by its name.

    Args:
        model_name: Model identifier

    Returns:
        ModelConfig if found, None otherwise
    """
    all_models = [
        GPT_4O,
        GPT_4O_MINI,
        CLAUDE_SONNET_4_5,
        CLAUDE_SONNET_3_5,
        GEMINI_1_5_PRO
    ]

    for model in all_models:
        if model.name == model_name:
            return model

    return None


def estimate_cost(
    model: ModelConfig,
    input_tokens: int,
    output_tokens: int
) -> float:
    """
    Estimate the cost of an LLM call.

    Args:
        model: Model configuration
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens

    Returns:
        Estimated cost in USD
    """
    input_cost = (input_tokens / 1000) * model.cost_per_1k_input
    output_cost = (output_tokens / 1000) * model.cost_per_1k_output
    return input_cost + output_cost


# ============================================================================
# Default Settings
# ============================================================================

DEFAULT_QUALITY_THRESHOLD = 0.80
"""Default quality gate threshold"""

DEFAULT_MAX_ITERATIONS = 3
"""Default maximum refinement iterations"""

DEFAULT_TEMPERATURE = 0.0
"""Default temperature for deterministic outputs"""

DEFAULT_MAX_TOKENS = 8192
"""Default maximum tokens in response"""

# Retry settings for transient errors
RETRY_MAX_ATTEMPTS = 3
"""Maximum retry attempts for transient errors"""

RETRY_INITIAL_DELAY = 1.0
"""Initial delay in seconds for exponential backoff"""

RETRY_BACKOFF_FACTOR = 2.0
"""Backoff multiplier for exponential backoff"""

RETRY_MAX_DELAY = 60.0
"""Maximum delay in seconds between retries"""
