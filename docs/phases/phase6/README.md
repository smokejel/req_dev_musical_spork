# Phase 6: Energy Consumption Tracking

**Status:** Planning
**Planned Duration:** 3-4 hours
**Date:** November 2025
**Type:** Observability Enhancement

## Overview

Phase 6 adds energy consumption tracking to the requirements decomposition workflow, providing visibility into the environmental impact of LLM operations. This builds on Phase 5's cost tracking infrastructure to add token-based energy estimation with contextual comparisons.

### Objectives

1. **Energy Visibility:** Display energy consumption (Wh) for each workflow execution
2. **Per-Node Breakdown:** Show which nodes consume the most energy
3. **Contextual Understanding:** Provide relatable comparisons (TV usage, distance driven)
4. **Minimal Overhead:** Lightweight implementation with no new dependencies
5. **Foundation for Future:** Enable future CO2 tracking and historical analysis

### Scope

**In Scope (Phase 6.1 - Minimal):**
- Token-based energy estimation using published research data
- Energy display in Performance & Cost Breakdown table
- Contextual comparisons for user understanding
- Energy coefficients for all 8 models in use

**Out of Scope (Future Enhancements):**
- CO2 emissions conversion (can add later)
- Historical energy trend tracking in database
- Automated energy reports
- Real-time hardware measurement (not applicable to API calls)

## Technical Approach

### Energy Estimation Methodology

**Type:** Heuristic token-based estimation
**Accuracy:** ±30% margin of error (60-75% accuracy)
**Justification:** Best achievable without datacenter access; sufficient for trend analysis

#### Why Not CodeCarbon?

CodeCarbon measures **local hardware** (GPU, CPU on your machine), not remote API calls. Our system uses cloud LLM APIs (OpenAI, Anthropic, Google), so energy consumption happens in their datacenters, not locally.

#### Calculation Formula

```python
# Per-node energy calculation
input_energy = (input_tokens / 1000) * model.energy_per_1k_input_wh
output_energy = (output_tokens / 1000) * model.energy_per_1k_output_wh

# Add datacenter overhead (PUE ~1.10 for Google/OpenAI)
total_energy_wh = (input_energy + output_energy) * 1.10
```

**PUE (Power Usage Effectiveness):** Ratio of total datacenter energy to IT equipment energy. Google's fleet average is 1.09 (2024), industry average is 1.15-1.30.

### Energy Coefficients

Based on published research from Epoch AI (Feb 2025), Google Cloud (Aug 2025), and ML.ENERGY benchmarks:

| Model | Energy per 1K Tokens (Wh) | Source | Notes |
|-------|---------------------------|--------|-------|
| **Gemini 2.5 Flash-Lite** | 0.00048 | Google (Aug 2025) | 0.24 Wh / 500 tokens |
| **Gemini 2.5 Flash** | 0.00048 | Google (Aug 2025) | Same as Flash-Lite |
| **Gemini 2.5 Pro** | 0.00060 | Estimated | Larger model, higher energy |
| **GPT-4o** | 0.00060 | Epoch AI (Feb 2025) | 0.3 Wh / 500 tokens |
| **GPT-4o-mini** | 0.00015 | Estimated | ~4x smaller than GPT-4o |
| **GPT-5 Nano** | 0.00030 | Estimated | Most efficient GPT-5 variant |
| **Claude Sonnet 4.5** | 0.00070 | Estimated | Conservative (comparable to GPT-4o) |
| **Claude Sonnet 3.5** | 0.00070 | Estimated | Conservative |

**Note:** Values include 10% datacenter overhead (PUE).

### Accuracy Limitations

**What We Can Measure:**
- Token counts (from LangSmith or response metadata)
- Model identifiers (which LLM was called)
- Per-query timing

**What We Cannot Measure:**
- Actual datacenter energy (no provider API access)
- GPU utilization (varies by load, time of day)
- Batching efficiency (providers batch requests internally)
- Caching benefits (repeated queries may use cached KV pairs)
- Hardware specifics (A100 vs H100 vs TPU)

**Expected Accuracy:** 60-75% (±30% margin) - Acceptable for trend analysis and optimization

## Implementation Plan

### Files to Modify

1. **`config/llm_config.py`** - Add energy coefficient fields
2. **`src/graph.py`** - Add energy calculation and tracking
3. **`main.py`** - Display energy in CLI output
4. **`src/state.py`** (Optional) - Add energy fields to state

### Detailed Changes

#### 1. Model Configuration (`config/llm_config.py`)

```python
@dataclass
class ModelConfig:
    name: str
    provider: ModelProvider
    temperature: float = 0.0
    max_tokens: int = 8192
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    energy_per_1k_input_wh: float = 0.0  # NEW
    energy_per_1k_output_wh: float = 0.0  # NEW
    description: str = ""
```

**Update all 8 model definitions** with energy coefficients from research data.

#### 2. Energy Calculation (`src/graph.py`)

Create new function parallel to `_calculate_node_cost()`:

```python
def _calculate_node_energy(
    input_tokens: int,
    output_tokens: int,
    model_config: ModelConfig
) -> float:
    """Calculate energy consumption for a node execution.

    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model_config: Model configuration with energy coefficients

    Returns:
        Energy consumption in watt-hours (Wh)
    """
    input_energy = (input_tokens / 1000) * model_config.energy_per_1k_input_wh
    output_energy = (output_tokens / 1000) * model_config.energy_per_1k_output_wh

    # Datacenter overhead (PUE ~1.10)
    total_energy = (input_energy + output_energy) * 1.10

    return total_energy
```

**Track in `_execute_node_with_progress()`:**
- Add `node_energy: Dict[str, float] = {}` to track per-node energy
- Call `_calculate_node_energy()` after each node execution
- Accumulate total energy

#### 3. CLI Display (`main.py`)

**Performance & Cost Breakdown table:**

Add "Energy (Wh)" column:

```python
table.add_column("Energy (Wh)", justify="right", style="yellow")

# For each node:
table.add_row(
    node_name,
    f"{duration:.2f}s",
    f"{percent}%",
    f"${cost:.4f}",
    f"{energy:.4f}",  # NEW
    f"{energy_percent}%"
)
```

**Contextual comparisons** (below table):

```python
# Calculate equivalents
tv_hours = total_energy_wh / 2.5  # 2.5W average TV
car_meters = (total_energy_wh / 1000) / 0.25  # 0.25 kWh/km

console.print("\n💡 Energy Context:")
console.print(f"   • Equivalent to ~{tv_hours*60:.1f} minutes of TV usage (2.5W average)")
console.print(f"   • Equivalent to ~{car_meters:.2f} meters driven by electric car (0.25 kWh/km)")
```

## Expected Output

### CLI Display Example

```
╭──────────────── Performance & Cost Breakdown ────────────────╮
│ Node       │ Duration │ % │ Cost ($) │ Energy (Wh) │ %      │
├────────────┼──────────┼───┼──────────┼─────────────┼────────┤
│ Extract    │ 1.23s    │ 13│ $0.0042  │ 0.0198      │ 17%    │
│ Analyze    │ 2.45s    │ 27│ $0.0087  │ 0.0412      │ 34%    │
│ Decompose  │ 3.67s    │ 40│ $0.0123  │ 0.0326      │ 27%    │
│ Validate   │ 1.89s    │ 20│ $0.0056  │ 0.0264      │ 22%    │
├────────────┼──────────┼───┼──────────┼─────────────┼────────┤
│ TOTAL      │ 9.24s    │100│ $0.0308  │ 0.1200 Wh   │ 100%   │
╰────────────┴──────────┴───┴──────────┴─────────────┴────────╯

💡 Energy Context:
   • Equivalent to ~2.9 minutes of TV usage (2.5W average)
   • Equivalent to ~0.48 meters driven by electric car (0.25 kWh/km)
```

### Typical Energy Ranges

Based on research and token usage patterns:

| Workflow Type | Typical Energy | Notes |
|--------------|----------------|-------|
| **Simple spec (5 reqs)** | 0.05 - 0.15 Wh | ~3-9 minutes TV usage |
| **Medium spec (15 reqs)** | 0.20 - 0.50 Wh | ~12-30 minutes TV |
| **Complex spec (30+ reqs)** | 0.50 - 2.00 Wh | ~30-120 minutes TV |
| **Large doc (88K tokens)** | 2.00 - 5.00 Wh | ~2-5 hours TV |

## Testing Strategy

### Test Plan

1. **Unit Tests**
   - Test `_calculate_node_energy()` with known token counts
   - Verify energy coefficients are loaded correctly
   - Check energy calculation accuracy

2. **Integration Tests**
   - Run workflow with sample spec
   - Verify energy displayed in breakdown table
   - Check contextual comparisons are reasonable
   - Ensure no errors with missing token data

3. **Validation Tests**
   - Compare energy estimates to published research
   - Verify GPT-4o: ~0.3 Wh per 500-token response
   - Verify Gemini: ~0.24 Wh per 500-token response
   - Check that total energy is non-zero for all runs

### Acceptance Criteria

- [ ] All 8 models have energy coefficients defined
- [ ] Energy calculated for each node execution
- [ ] Energy displayed in Performance & Cost Breakdown table
- [ ] Contextual comparisons shown below table
- [ ] Energy values are reasonable (0.05-5.0 Wh typical range)
- [ ] No errors when token data is unavailable (fallback to 0.0)
- [ ] Documentation complete

## Benefits

### User Benefits

1. **Environmental Awareness:** Understand energy impact of AI operations
2. **Optimization Insights:** Identify energy-hungry nodes for optimization
3. **Stakeholder Reporting:** Corporate sustainability metrics
4. **Cost Correlation:** Energy often correlates with cost inefficiencies

### Technical Benefits

1. **Minimal Overhead:** Uses existing token tracking infrastructure
2. **No Dependencies:** Pure Python calculation, no new libraries
3. **Extensible:** Foundation for future CO2 tracking
4. **Aligned with Industry:** Follows emerging best practices

## Future Enhancements

### Phase 6.2: CO2 Emissions Tracking (Optional)

**Effort:** 1-2 hours

- Convert energy → CO2 emissions using grid carbon intensity
- US grid average: 0.475 kgCO2e per kWh
- Display emissions in grams CO2e
- Add to breakdown table and comparisons

### Phase 6.3: Historical Energy Trends (Optional)

**Effort:** 2-3 hours

- Store energy data in SQLite database
- Track energy trends over time
- Generate energy efficiency reports
- Identify optimization opportunities

### Phase 6.4: Advanced Adjustments (Optional)

**Effort:** 2-3 hours

- Context length scaling (penalty for ultra-long contexts)
- Reasoning model detection (o1, o3 use 2-3x more energy)
- Provider-specific efficiency factors
- Seasonal datacenter efficiency variations

## Research Sources

1. **Epoch AI (Feb 2025):** "How much energy does ChatGPT use?"
   - https://epoch.ai/gradient-updates/how-much-energy-does-chatgpt-use
   - GPT-4o: 0.3 Wh per query (500 tokens)

2. **Google Cloud (Aug 2025):** "Measuring the environmental impact of AI inference"
   - https://cloud.google.com/blog/products/infrastructure/measuring-the-environmental-impact-of-ai-inference
   - Gemini 2.5 Flash: 0.24 Wh median text prompt

3. **ML.ENERGY Leaderboard:** Real-world energy benchmarks
   - https://ml.energy/leaderboard/
   - Open-source model energy on A100 GPUs

4. **CodeCarbon Documentation:** Methodology and carbon intensity data
   - https://mlco2.github.io/codecarbon/methodology.html
   - PUE factors, grid carbon intensities

5. **ResearchGate (2025):** "How Hungry is AI? Benchmarking Energy, Water, and Carbon Footprint of LLM Inference"
   - Per-token energy estimates across models

## Implementation Checklist

- [ ] Create `docs/phases/phase6/` directory structure
- [ ] Document Phase 6 in README.md
- [ ] Create implementation_plan.md with detailed steps
- [ ] Create energy_coefficients_research.md with sources
- [ ] Update CLAUDE.md with Phase 6 section
- [ ] Update main README.md with energy tracking feature
- [ ] Add energy fields to `ModelConfig` dataclass
- [ ] Populate energy coefficients for all 8 models
- [ ] Create `_calculate_node_energy()` function
- [ ] Track energy in `_execute_node_with_progress()`
- [ ] Add Energy column to breakdown table
- [ ] Add contextual comparisons below table
- [ ] Write unit tests for energy calculation
- [ ] Test with sample workflow run
- [ ] Verify energy values are reasonable
- [ ] Update documentation with final results

## Success Metrics

**Functional:**
- Energy displayed for all workflow executions
- Values within expected ranges (0.05-5.0 Wh)
- No errors or crashes

**Quality:**
- Accuracy within ±30% of published research
- Contextual comparisons are intuitive
- Documentation is clear

**Performance:**
- Zero measurable overhead (<1ms per calculation)
- No impact on workflow execution time

---

**Next Steps:** Review implementation_plan.md for detailed technical steps.
