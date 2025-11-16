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

    energy_per_1k_input_wh: float = 0.0
    """Energy consumption per 1K input tokens in Watt-hours (Wh)"""

    energy_per_1k_output_wh: float = 0.0
    """Energy consumption per 1K output tokens in Watt-hours (Wh)"""

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
    energy_per_1k_input_wh=0.0006,  # Epoch AI (Feb 2025) - 0.3 Wh per 500 tokens
    energy_per_1k_output_wh=0.0006,  # Epoch AI (Feb 2025) - 0.3 Wh per 500 tokens
    description="GPT-4 Optimized - Best for complex reasoning tasks"
)

GPT_4O_MINI = ModelConfig(
    name="gpt-4o-mini",
    provider=ModelProvider.OPENAI,
    temperature=0.0,
    max_tokens=8192,
    cost_per_1k_input=0.00015,
    cost_per_1k_output=0.0006,
    energy_per_1k_input_wh=0.00015,  # Estimated (4x smaller than GPT-4o)
    energy_per_1k_output_wh=0.00015,  # Estimated (4x smaller than GPT-4o)
    description="GPT-4 Mini - Cost-effective for structured extraction"
)

GPT_5_NANO = ModelConfig(
    name="gpt-5-nano",
    provider=ModelProvider.OPENAI,
    temperature=0.0,
    max_tokens=32768,  # 32K+ output tokens per MODEL_DEFINITIONS.md
    cost_per_1k_input=0.0001,  # Estimate - most cost-efficient GPT-5 variant
    cost_per_1k_output=0.0005,  # Estimate - verify from OpenAI pricing
    energy_per_1k_input_wh=0.0003,  # Estimated (efficient variant, ~50% of GPT-4o)
    energy_per_1k_output_wh=0.0003,  # Estimated (efficient variant, ~50% of GPT-4o)
    description="GPT-5 Nano - Fastest, most cost-efficient GPT-5 variant"
)

# Anthropic Models
CLAUDE_SONNET_4_5 = ModelConfig(
    name="claude-sonnet-4-5-20250929",
    provider=ModelProvider.ANTHROPIC,
    temperature=0.0,
    max_tokens=8192,
    cost_per_1k_input=0.003,
    cost_per_1k_output=0.015,
    energy_per_1k_input_wh=0.0007,  # Conservative estimate (similar to GPT-4 class)
    energy_per_1k_output_wh=0.0007,  # Conservative estimate (similar to GPT-4 class)
    description="Claude Sonnet 4.5 - Excellent for analysis and validation"
)

CLAUDE_SONNET_3_5 = ModelConfig(
    name="claude-sonnet-4-5-20250929",
    provider=ModelProvider.ANTHROPIC,
    temperature=0.1,
    max_tokens=8192,
    cost_per_1k_input=0.003,
    cost_per_1k_output=0.015,
    energy_per_1k_input_wh=0.0007,  # Conservative estimate (similar to GPT-4 class)
    energy_per_1k_output_wh=0.0007,  # Conservative estimate (similar to GPT-4 class)
    description="Claude Sonnet 4.5 - Strong architectural reasoning"
)

# Google Models (Phase 4.1 - Gemini 2.5 Series for large document support)
GEMINI_2_5_FLASH_LITE = ModelConfig(
    name="gemini-2.5-flash-lite",
    provider=ModelProvider.GOOGLE,
    temperature=0.0,
    max_tokens=65536,  # 65K output tokens, 1M total context window
    cost_per_1k_input=0.0001,  # Ultra cost-efficient (verify from pricing page)
    cost_per_1k_output=0.0004,  # Ultra cost-efficient (verify from pricing page)
    energy_per_1k_input_wh=0.00048,  # Google (Aug 2025) - 0.24 Wh per 500 tokens
    energy_per_1k_output_wh=0.00048,  # Google (Aug 2025) - 0.24 Wh per 500 tokens
    description="Gemini 2.5 Flash-Lite - Ultra fast, 1M context, most cost-efficient"
)

GEMINI_2_5_FLASH = ModelConfig(
    name="gemini-2.5-flash",
    provider=ModelProvider.GOOGLE,
    temperature=0.0,
    max_tokens=65536,  # 65K output tokens, 1M total context window
    cost_per_1k_input=0.0002,  # Best price-performance (verify from pricing page)
    cost_per_1k_output=0.0008,  # Best price-performance (verify from pricing page)
    energy_per_1k_input_wh=0.00048,  # Google (Aug 2025) - 0.24 Wh per 500 tokens
    energy_per_1k_output_wh=0.00048,  # Google (Aug 2025) - 0.24 Wh per 500 tokens
    description="Gemini 2.5 Flash - Best price-performance, 1M context window"
)

GEMINI_2_5_PRO = ModelConfig(
    name="gemini-2.5-pro",
    provider=ModelProvider.GOOGLE,
    temperature=0.0,
    max_tokens=65536,  # 65K output tokens, 1M total context window
    cost_per_1k_input=0.0005,  # State-of-the-art thinking (verify from pricing page)
    cost_per_1k_output=0.002,   # State-of-the-art thinking (verify from pricing page)
    energy_per_1k_input_wh=0.0006,  # Estimated (+25% vs Flash for advanced reasoning)
    energy_per_1k_output_wh=0.0006,  # Estimated (+25% vs Flash for advanced reasoning)
    description="Gemini 2.5 Pro - State-of-the-art thinking model, 1M context"
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
        primary_model=GEMINI_2_5_FLASH_LITE,
        fallback_models=[GEMINI_2_5_FLASH, GPT_4O, CLAUDE_SONNET_4_5],
        rationale="Ultra-fast with 1M context window. Handles 88K+ token PDFs efficiently (tested: 396 reqs extracted in 70s). Most cost-efficient option. Note: Free tier has 250K token/min quota."
    ),

    NodeType.ANALYZE: NodeModelConfig(
        node_type=NodeType.ANALYZE,
        primary_model=CLAUDE_SONNET_3_5,
        fallback_models=[GPT_4O, CLAUDE_SONNET_4_5],
        rationale="Architectural reasoning and context understanding. Claude excels at system-level analysis."
    ),

    NodeType.DECOMPOSE: NodeModelConfig(
        node_type=NodeType.DECOMPOSE,
        primary_model=GPT_5_NANO,
        fallback_models=[GPT_4O, CLAUDE_SONNET_4_5],
        rationale="GPT-5 Nano - Fastest, most cost-efficient with higher rate limits. Handles large requirement sets (tested: 396 requirements = 31K tokens) without TPM constraints. No rate limit issues observed."
    ),

    NodeType.VALIDATE: NodeModelConfig(
        node_type=NodeType.VALIDATE,
        primary_model=GEMINI_2_5_FLASH,
        fallback_models=[CLAUDE_SONNET_4_5, GPT_4O],
        rationale="Best price-performance for quality validation. 1M context window handles large requirement sets. Balanced speed and accuracy. Quality scores: 0.85-0.99 in testing."
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
        GPT_5_NANO,
        CLAUDE_SONNET_4_5,
        CLAUDE_SONNET_3_5,
        GEMINI_2_5_FLASH_LITE,
        GEMINI_2_5_FLASH,
        GEMINI_2_5_PRO
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


def estimate_energy(
    model: ModelConfig,
    input_tokens: int,
    output_tokens: int,
    include_pue: bool = True
) -> float:
    """
    Estimate the energy consumption of an LLM call.

    Energy values are based on published research:
    - GPT-4o: Epoch AI (Feb 2025) - 0.3 Wh per 500 tokens
    - Gemini: Google (Aug 2025) - 0.24 Wh per 500 tokens
    - Others: Conservative estimates based on model class

    Args:
        model: Model configuration
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        include_pue: If True, apply PUE factor of 1.10 for datacenter overhead

    Returns:
        Estimated energy consumption in Watt-hours (Wh)
    """
    input_energy = (input_tokens / 1000) * model.energy_per_1k_input_wh
    output_energy = (output_tokens / 1000) * model.energy_per_1k_output_wh
    total_energy = input_energy + output_energy

    # Apply PUE (Power Usage Effectiveness) for datacenter overhead
    if include_pue:
        total_energy *= 1.10  # Industry standard PUE of 1.10

    return total_energy


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
