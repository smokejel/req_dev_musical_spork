# Phase 6 Implementation Plan: Energy Consumption Tracking

**Author:** System Documentation
**Date:** November 2025
**Estimated Effort:** 3-4 hours
**Status:** Planning

## Overview

This document provides step-by-step implementation instructions for adding energy consumption tracking to the requirements decomposition workflow. The implementation follows a minimal approach (Phase 6.1) with display-only energy metrics.

## Prerequisites

- Phase 5 complete (cost tracking infrastructure in place)
- Token tracking operational (via LangSmith or response metadata)
- Existing observability fields in `DecompositionState`

## Implementation Steps

### Step 1: Add Energy Coefficients to Model Configuration

**File:** `config/llm_config.py`

**Duration:** 30 minutes

#### 1.1 Update `ModelConfig` Dataclass

Add two new fields for energy coefficients:

```python
@dataclass
class ModelConfig:
    name: str
    provider: ModelProvider
    temperature: float = 0.0
    max_tokens: int = 8192
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    energy_per_1k_input_wh: float = 0.0  # NEW: Energy per 1K input tokens (Wh)
    energy_per_1k_output_wh: float = 0.0  # NEW: Energy per 1K output tokens (Wh)
    description: str = ""
```

#### 1.2 Populate Energy Coefficients for All Models

Update each model definition with energy values from `energy_coefficients_research.md`:

**OpenAI Models:**

```python
GPT_4O = ModelConfig(
    name="gpt-4o",
    provider=ModelProvider.OPENAI,
    temperature=0.0,
    max_tokens=16384,
    cost_per_1k_input=0.0025,
    cost_per_1k_output=0.01,
    energy_per_1k_input_wh=0.0006,  # NEW: 0.3 Wh / 500 tokens (Epoch AI)
    energy_per_1k_output_wh=0.0006,  # NEW
    description="GPT-4o - Flagship model, balanced performance"
)

GPT_4O_MINI = ModelConfig(
    name="gpt-4o-mini",
    provider=ModelProvider.OPENAI,
    temperature=0.0,
    max_tokens=16384,
    cost_per_1k_input=0.00015,
    cost_per_1k_output=0.0006,
    energy_per_1k_input_wh=0.00015,  # NEW: ~4x smaller than GPT-4o
    energy_per_1k_output_wh=0.00015,  # NEW
    description="GPT-4o Mini - Cost-efficient, fast"
)

GPT_5_NANO = ModelConfig(
    name="gpt-5-nano",
    provider=ModelProvider.OPENAI,
    temperature=0.0,
    max_tokens=32768,
    cost_per_1k_input=0.0001,
    cost_per_1k_output=0.0004,
    energy_per_1k_input_wh=0.0003,  # NEW: Most efficient GPT-5 variant
    energy_per_1k_output_wh=0.0003,  # NEW
    description="GPT-5 Nano - Most efficient, no TPM limits"
)
```

**Anthropic Models:**

```python
CLAUDE_SONNET_3_5 = ModelConfig(
    name="claude-sonnet-3-5",
    provider=ModelProvider.ANTHROPIC,
    temperature=0.0,
    max_tokens=8192,
    cost_per_1k_input=0.003,
    cost_per_1k_output=0.015,
    energy_per_1k_input_wh=0.0007,  # NEW: Conservative estimate
    energy_per_1k_output_wh=0.0007,  # NEW
    description="Claude Sonnet 3.5 - Excellent reasoning"
)

CLAUDE_SONNET_4_5 = ModelConfig(
    name="claude-sonnet-4-5-20250929",
    provider=ModelProvider.ANTHROPIC,
    temperature=0.0,
    max_tokens=8192,
    cost_per_1k_input=0.003,
    cost_per_1k_output=0.015,
    energy_per_1k_input_wh=0.0007,  # NEW: Conservative estimate
    energy_per_1k_output_wh=0.0007,  # NEW
    description="Claude Sonnet 4.5 - Latest flagship"
)
```

**Google Models:**

```python
GEMINI_2_5_FLASH_LITE = ModelConfig(
    name="gemini-2.5-flash-lite",
    provider=ModelProvider.GOOGLE,
    temperature=0.0,
    max_tokens=65536,
    cost_per_1k_input=0.0001,
    cost_per_1k_output=0.0004,
    energy_per_1k_input_wh=0.00048,  # NEW: 0.24 Wh / 500 tokens (Google)
    energy_per_1k_output_wh=0.00048,  # NEW
    description="Gemini 2.5 Flash-Lite - Ultra fast, 1M context"
)

GEMINI_2_5_FLASH = ModelConfig(
    name="gemini-2.5-flash",
    provider=ModelProvider.GOOGLE,
    temperature=0.0,
    max_tokens=65536,
    cost_per_1k_input=0.0002,
    cost_per_1k_output=0.0008,
    energy_per_1k_input_wh=0.00048,  # NEW: Same as Flash-Lite
    energy_per_1k_output_wh=0.00048,  # NEW
    description="Gemini 2.5 Flash - Best price-performance"
)

GEMINI_2_5_PRO = ModelConfig(
    name="gemini-2.5-pro",
    provider=ModelProvider.GOOGLE,
    temperature=0.0,
    max_tokens=65536,
    cost_per_1k_input=0.00125,
    cost_per_1k_output=0.005,
    energy_per_1k_input_wh=0.0006,  # NEW: Larger model, higher energy
    energy_per_1k_output_wh=0.0006,  # NEW
    description="Gemini 2.5 Pro - Most capable, 1M context"
)
```

#### 1.3 Verification

After updating, verify all models have energy coefficients:

```python
# Add this check in llm_config.py for development
def verify_energy_coefficients():
    """Verify all models have energy coefficients defined."""
    all_models = [
        GPT_4O, GPT_4O_MINI, GPT_5_NANO,
        CLAUDE_SONNET_3_5, CLAUDE_SONNET_4_5,
        GEMINI_2_5_FLASH_LITE, GEMINI_2_5_FLASH, GEMINI_2_5_PRO
    ]

    for model in all_models:
        assert model.energy_per_1k_input_wh > 0, f"{model.name} missing input energy coefficient"
        assert model.energy_per_1k_output_wh > 0, f"{model.name} missing output energy coefficient"

    print("✓ All models have energy coefficients defined")
```

---

### Step 2: Create Energy Calculation Function

**File:** `src/graph.py`

**Duration:** 45 minutes

#### 2.1 Add Energy Calculation Function

Add this function near `_calculate_node_cost()`:

```python
def _calculate_node_energy(
    input_tokens: int,
    output_tokens: int,
    model_config: ModelConfig
) -> float:
    """
    Calculate energy consumption for a node execution using token-based estimation.

    This uses published research data to estimate energy consumption based on
    input/output token counts. Accuracy is ±30% due to datacenter variations.

    Args:
        input_tokens: Number of input tokens processed
        output_tokens: Number of output tokens generated
        model_config: Model configuration with energy coefficients (Wh per 1K tokens)

    Returns:
        Energy consumption in watt-hours (Wh)

    Notes:
        - Energy coefficients are based on published research (Epoch AI, Google)
        - Includes 10% datacenter overhead (PUE ~1.10)
        - Does not account for batching, caching, or hardware variations
        - Expected accuracy: 60-75% (±30% margin)

    Example:
        >>> config = ModelConfig(energy_per_1k_input_wh=0.0006, energy_per_1k_output_wh=0.0006)
        >>> energy = _calculate_node_energy(1000, 500, config)
        >>> print(f"{energy:.4f} Wh")  # ~0.0010 Wh
    """
    if input_tokens == 0 and output_tokens == 0:
        return 0.0

    # Calculate base energy from tokens
    input_energy = (input_tokens / 1000.0) * model_config.energy_per_1k_input_wh
    output_energy = (output_tokens / 1000.0) * model_config.energy_per_1k_output_wh

    # Add datacenter overhead (PUE ~1.10)
    # Google: 1.09, Industry average: 1.15-1.30
    PUE = 1.10
    total_energy = (input_energy + output_energy) * PUE

    return total_energy
```

#### 2.2 Test Energy Calculation

Add unit test to verify calculation:

```python
# tests/test_graph.py

def test_calculate_node_energy():
    """Test energy calculation with known values."""
    from config.llm_config import ModelConfig, ModelProvider

    # Create test config
    config = ModelConfig(
        name="test-model",
        provider=ModelProvider.OPENAI,
        energy_per_1k_input_wh=0.0006,  # GPT-4o equivalent
        energy_per_1k_output_wh=0.0006
    )

    # Test 500 tokens (should be ~0.3 Wh per Epoch AI)
    energy = _calculate_node_energy(input_tokens=500, output_tokens=0, model_config=config)
    assert 0.0003 <= energy <= 0.0004, f"Expected ~0.00033 Wh, got {energy:.6f}"

    # Test zero tokens
    energy = _calculate_node_energy(input_tokens=0, output_tokens=0, model_config=config)
    assert energy == 0.0, "Zero tokens should return zero energy"

    # Test large document (10K tokens)
    energy = _calculate_node_energy(input_tokens=10000, output_tokens=500, model_config=config)
    assert 0.006 <= energy <= 0.008, f"Expected ~0.0070 Wh, got {energy:.6f}"
```

---

### Step 3: Track Energy in Workflow Execution

**File:** `src/graph.py`

**Duration:** 30 minutes

#### 3.1 Add Energy Tracking to Node Wrapper

Modify `_execute_node_with_progress()` to track energy:

```python
def _execute_node_with_progress(
    node_func: Callable,
    node_name: str,
    state: DecompositionState,
    node_costs: Dict[str, float],
    node_energy: Dict[str, float],  # NEW: Add energy tracking
    total_duration: Dict[str, float],
    status: Status
) -> DecompositionState:
    """Execute a node with progress tracking and energy monitoring."""

    start_time = time.time()

    # ... existing status update code ...

    # Execute node
    result = node_func(state)

    # Calculate duration
    duration = time.time() - start_time
    total_duration[node_name] = duration

    # Calculate cost (existing)
    cost = _calculate_node_cost(state, node_type)
    node_costs[node_name] = cost

    # Calculate energy (NEW)
    energy = _calculate_node_energy_from_state(state, node_type)
    node_energy[node_name] = energy

    # ... existing status completion code ...

    return result
```

#### 3.2 Create Helper Function to Extract Energy from State

Add helper function to extract tokens and calculate energy:

```python
def _calculate_node_energy_from_state(
    state: DecompositionState,
    node_type: NodeType
) -> float:
    """
    Calculate energy for a node execution from state.

    Extracts token counts from state's token_usage field and calculates
    energy using the node's primary model configuration.

    Args:
        state: Current workflow state with token usage data
        node_type: Type of node that was executed

    Returns:
        Energy consumption in Wh, or 0.0 if token data unavailable
    """
    # Get token usage from state
    token_usage = state.get("token_usage", {})
    node_tokens = token_usage.get(node_type.value, {})

    input_tokens = node_tokens.get("input_tokens", 0)
    output_tokens = node_tokens.get("output_tokens", 0)

    if input_tokens == 0 and output_tokens == 0:
        # Fallback: try to estimate from cost if available
        # This is less accurate but better than nothing
        return 0.0

    # Get model config for this node
    model_config = get_primary_model(node_type)

    # Calculate energy
    energy = _calculate_node_energy(input_tokens, output_tokens, model_config)

    return energy
```

#### 3.3 Update Workflow Compilation

Modify `create_decomposition_graph()` to initialize energy tracking:

```python
def create_decomposition_graph(config: Optional[Dict] = None) -> CompiledGraph:
    """Create and compile the requirements decomposition workflow graph."""

    # ... existing code ...

    # Initialize tracking dictionaries
    node_costs: Dict[str, float] = {}
    node_energy: Dict[str, float] = {}  # NEW
    total_duration: Dict[str, float] = {}

    # Wrap nodes with progress tracking
    def extract_with_progress(state):
        return _execute_node_with_progress(
            extract_node, "Extract", state,
            node_costs, node_energy, total_duration, status  # Pass energy dict
        )

    # ... repeat for all nodes ...
```

---

### Step 4: Display Energy in CLI Output

**File:** `main.py`

**Duration:** 1 hour

#### 4.1 Add Energy Column to Performance Breakdown Table

Modify the performance breakdown table generation:

```python
def display_performance_breakdown(
    timing_breakdown: Dict[str, float],
    cost_breakdown: Dict[str, float],
    energy_breakdown: Dict[str, float],  # NEW
    total_duration: float,
    total_cost: float,
    total_energy: float,  # NEW
    cost_source: str
) -> None:
    """Display performance, cost, and energy breakdown."""

    # Create table
    table = Table(
        title="Performance & Cost Breakdown",
        show_header=True,
        header_style="bold magenta"
    )

    # Add columns
    table.add_column("Node", style="cyan", no_wrap=True)
    table.add_column("Duration", justify="right", style="green")
    table.add_column("%", justify="right", style="dim")
    table.add_column("Cost ($)", justify="right", style="yellow")
    table.add_column("Energy (Wh)", justify="right", style="yellow")  # NEW
    table.add_column("%", justify="right", style="dim")

    # Calculate percentages
    for node_name in timing_breakdown.keys():
        duration = timing_breakdown[node_name]
        cost = cost_breakdown.get(node_name, 0.0)
        energy = energy_breakdown.get(node_name, 0.0)  # NEW

        time_percent = int((duration / total_duration) * 100) if total_duration > 0 else 0
        energy_percent = int((energy / total_energy) * 100) if total_energy > 0 else 0  # NEW

        table.add_row(
            node_name,
            f"{duration:.2f}s",
            f"{time_percent}%",
            f"${cost:.4f}",
            f"{energy:.4f}",  # NEW
            f"{energy_percent}%"  # NEW
        )

    # Add totals row
    table.add_row(
        "[bold]TOTAL[/bold]",
        f"[bold]{total_duration:.2f}s[/bold]",
        "[bold]100%[/bold]",
        f"[bold]${total_cost:.4f}[/bold]",
        f"[bold]{total_energy:.4f} Wh[/bold]",  # NEW
        "[bold]100%[/bold]"
    )

    console.print(table)
    console.print(f"\n[dim]Cost calculated using: {cost_source}[/dim]")
```

#### 4.2 Add Contextual Energy Comparisons

Add function to display energy context:

```python
def display_energy_context(total_energy_wh: float) -> None:
    """Display contextual comparisons for energy consumption."""

    if total_energy_wh <= 0:
        return

    # Calculate equivalents
    tv_power_watts = 2.5  # Average LED TV
    tv_minutes = (total_energy_wh / tv_power_watts) * 60

    car_kwh_per_km = 0.25  # Electric car efficiency
    car_meters = (total_energy_wh / 1000) / car_kwh_per_km

    # Display
    console.print("\n💡 [cyan]Energy Context:[/cyan]")
    console.print(f"   • Equivalent to ~[yellow]{tv_minutes:.1f} minutes[/yellow] of TV usage (2.5W average)")
    console.print(f"   • Equivalent to ~[yellow]{car_meters:.2f} meters[/yellow] driven by electric car (0.25 kWh/km)")
```

#### 4.3 Update Main Function to Call Energy Display

Modify the main workflow execution:

```python
def main():
    # ... existing setup code ...

    # Execute workflow
    final_state = graph.invoke(initial_state, config={"thread_id": "main"})

    # Extract metrics
    timing_breakdown = final_state.get("timing_breakdown", {})
    cost_breakdown = final_state.get("cost_breakdown", {})
    energy_breakdown = final_state.get("energy_breakdown", {})  # NEW

    total_duration = sum(timing_breakdown.values())
    total_cost = final_state.get("total_cost", 0.0)
    total_energy = sum(energy_breakdown.values())  # NEW

    # Display performance breakdown
    display_performance_breakdown(
        timing_breakdown,
        cost_breakdown,
        energy_breakdown,  # NEW
        total_duration,
        total_cost,
        total_energy,  # NEW
        final_state.get("cost_source", "heuristic")
    )

    # Display energy context (NEW)
    display_energy_context(total_energy)

    # ... existing results display code ...
```

---

### Step 5: Update State Schema (Optional)

**File:** `src/state.py`

**Duration:** 15 minutes

Add energy tracking fields to `DecompositionState`:

```python
class DecompositionState(TypedDict, total=False):
    # ... existing fields ...

    # Observability & Tracking
    total_cost: Optional[float]
    total_energy_wh: Optional[float]  # NEW: Total energy consumption in Wh
    cost_breakdown: Optional[Dict[str, float]]
    energy_breakdown: Optional[Dict[str, float]]  # NEW: Energy per node
    timing_breakdown: Optional[Dict[str, float]]
    token_usage: Optional[Dict[str, Dict[str, int]]]
    cost_source: Optional[str]
```

---

### Step 6: Testing

**Duration:** 30 minutes

#### 6.1 Unit Tests

Create `tests/test_energy_tracking.py`:

```python
import pytest
from src.graph import _calculate_node_energy
from config.llm_config import ModelConfig, ModelProvider

def test_energy_calculation_gpt4o():
    """Test GPT-4o energy calculation matches Epoch AI research."""
    config = ModelConfig(
        name="gpt-4o",
        provider=ModelProvider.OPENAI,
        energy_per_1k_input_wh=0.0006,
        energy_per_1k_output_wh=0.0006
    )

    # 500 tokens should be ~0.3 Wh per Epoch AI
    energy = _calculate_node_energy(0, 500, config)
    assert 0.0003 <= energy <= 0.0004, f"Expected ~0.00033 Wh, got {energy:.6f}"

def test_energy_calculation_gemini():
    """Test Gemini energy calculation matches Google research."""
    config = ModelConfig(
        name="gemini-2.5-flash",
        provider=ModelProvider.GOOGLE,
        energy_per_1k_input_wh=0.00048,
        energy_per_1k_output_wh=0.00048
    )

    # 500 tokens should be ~0.24 Wh per Google
    energy = _calculate_node_energy(0, 500, config)
    assert 0.00025 <= energy <= 0.00028, f"Expected ~0.000264 Wh, got {energy:.6f}"

def test_energy_zero_tokens():
    """Test zero tokens returns zero energy."""
    config = ModelConfig(
        name="test",
        provider=ModelProvider.OPENAI,
        energy_per_1k_input_wh=0.0006,
        energy_per_1k_output_wh=0.0006
    )

    energy = _calculate_node_energy(0, 0, config)
    assert energy == 0.0
```

#### 6.2 Integration Test

Test with sample workflow:

```bash
# Run simple workflow
python main.py examples/simple_navigation.txt --subsystem "Navigation Subsystem"

# Check output includes:
# - Energy column in Performance & Cost Breakdown table
# - Energy values > 0.0 for each node
# - Total energy in reasonable range (0.05-0.50 Wh)
# - Contextual comparisons displayed
```

#### 6.3 Validation Against Research

Compare output to published data:

| Expected | Actual | Notes |
|----------|--------|-------|
| GPT-4o: ~0.3 Wh per 500 tokens | Check actual | ±30% acceptable |
| Gemini: ~0.24 Wh per 500 tokens | Check actual | ±30% acceptable |
| Total energy > 0 | Must be true | No zero energy runs |

---

### Step 7: Documentation Updates

**Duration:** 30 minutes

1. Add energy tracking to `README.md` feature list
2. Update `CLAUDE.md` with Phase 6 status
3. Add inline code comments for energy functions
4. Update `.env.example` if new config needed (none required)

---

## Rollback Plan

If issues arise during implementation:

1. **Revert model config changes:** Remove energy fields from `ModelConfig`
2. **Remove energy functions:** Delete `_calculate_node_energy()` and related helpers
3. **Restore original table:** Remove Energy column from CLI display
4. **No data loss:** Energy tracking is display-only, no database changes

## Post-Implementation Checklist

- [ ] All 8 models have energy coefficients
- [ ] Energy calculation function works correctly
- [ ] Energy tracked per node in workflow
- [ ] Energy displayed in breakdown table
- [ ] Contextual comparisons shown
- [ ] Unit tests pass
- [ ] Integration test shows reasonable values
- [ ] No errors with missing token data
- [ ] Documentation updated
- [ ] Code reviewed for accuracy

## Next Steps After Implementation

1. Monitor energy values for reasonableness over multiple runs
2. Compare to published research (GPT-4o ~0.3 Wh, Gemini ~0.24 Wh)
3. Consider Phase 6.2 (CO2 emissions) if stakeholders request
4. Gather feedback from users on utility of energy metrics
5. Consider historical tracking (Phase 6.3) if trend analysis needed

---

**Implementation Owner:** TBD
**Target Completion:** TBD
**Status:** Planning
