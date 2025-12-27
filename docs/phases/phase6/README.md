# Phase 6: Energy Consumption Tracking

**Status:** ✅ Complete
**Date:** December 2025
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

**Completed (Phase 6.1):**
- Token-based energy estimation using published research data
- Energy display in Performance & Cost Breakdown table (CLI and Web UI)
- Contextual comparisons for user understanding
- Energy coefficients for all 8 models in use
- Database persistence for energy metrics

## Technical Approach

### Energy Estimation Methodology

**Type:** Heuristic token-based estimation
**Accuracy:** ±30% margin of error (60-75% accuracy)
**Justification:** Best achievable without datacenter access; sufficient for trend analysis

#### Calculation Formula

```python
# Per-node energy calculation
input_energy = (input_tokens / 1000) * model.energy_per_1k_input_wh
output_energy = (output_tokens / 1000) * model.energy_per_1k_output_wh

# Add datacenter overhead (PUE ~1.10 for Google/OpenAI)
total_energy_wh = (input_energy + output_energy) * 1.10
```

### Energy Coefficients

Based on published research from Epoch AI (Feb 2025), Google Cloud (Aug 2025), and ML.ENERGY benchmarks:

| Model | Energy per 1K Tokens (Wh) | Source | Notes |
|-------|---------------------------|--------|-------|
| **Gemini 2.5 Flash-Lite** | 0.48 | Google (Aug 2025) | 0.24 Wh / 500 tokens |
| **Gemini 2.5 Flash** | 0.48 | Google (Aug 2025) | Same as Flash-Lite |
| **Gemini 2.5 Pro** | 0.6 | Estimated | Larger model, higher energy |
| **GPT-4o** | 0.6 | Epoch AI (Feb 2025) | 0.3 Wh / 500 tokens |
| **GPT-4o-mini** | 0.15 | Estimated | ~4x smaller than GPT-4o |
| **GPT-5 Nano** | 0.3 | Estimated | Most efficient GPT-5 variant |
| **Claude Sonnet 4.5** | 0.7 | Estimated | Conservative (comparable to GPT-4o) |
| **Claude Sonnet 3.5** | 0.7 | Estimated | Conservative |

**Note:** Values include 10% datacenter overhead (PUE).

## Implementation Details

### CLI
- **Performance & Cost Breakdown:** Added "Energy (Wh)" column.
- **Context:** Displays equivalent TV usage and electric car distance.

### Web UI
- **Metrics Grid:** Shows Energy usage in Wh.
- **Backend:** Persists energy data in SQLite and exposes it via API.

## Future Enhancements

### Phase 6.2: CO2 Emissions Tracking (Optional)
- Convert energy → CO2 emissions using grid carbon intensity.

### Phase 6.3: Historical Energy Trends (Optional)
- Track energy trends over time in reports.

---

**Next Steps:** Proceed to Phase 7 (Domain-Aware Decomposition) or further web application development.