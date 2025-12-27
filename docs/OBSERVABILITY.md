# Observability & Cost Tracking Guide

**Version:** Phase 6
**Last Updated:** December 27, 2025

## Overview

The requirements decomposition system includes comprehensive observability features for tracking costs, monitoring quality trends, and managing budgets. This guide covers setup, usage, and best practices.

## Features

### Cost Tracking
- **Real-time cost monitoring** per workflow node
- **Budget management** with configurable warnings and limits
- **Historical cost trends** stored in SQLite database
- **Multi-provider support** (OpenAI, Anthropic, Google/Gemini)
- **LangSmith integration** for precise token tracking (optional)

### Quality Monitoring
- **4-dimensional quality metrics** (completeness, clarity, testability, traceability)
- **Historical quality trends** across workflow runs
- **Subsystem comparison** for identifying weak points
- **Pass rate tracking** and iteration counts

### Energy Tracking
- **Token-based energy estimation** (Wh) for each workflow execution
- **Per-node energy breakdown**
- **Contextual comparisons** (equivalent TV usage, EV distance)
- **Energy coefficients** for 8 major LLM models (Gemini, GPT, Claude)

### Reporting
- **Automated report generation** with cost and quality trends
- **Rich console output** with formatted tables
- **File export** for further analysis
- **Configurable time periods** (days/weeks/months)

## Quick Start

### 1. Enable Cost Tracking

Edit your `.env` file:

```bash
# Cost Tracking (enabled by default)
COST_TRACKING_ENABLED=true
COST_BUDGET_WARNING_THRESHOLD=1.00  # Warn at $1.00
COST_BUDGET_MAX=5.00  # Stop at $5.00
```

### 2. Optional: Enable LangSmith

For precise token tracking (recommended for production):

```bash
# LangSmith Tracing
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_langsmith_key_here
LANGCHAIN_PROJECT=requirements-decomposition
```

**Get your API key:** https://smith.langchain.com/

### 3. Run a Workflow

Cost and quality tracking happens automatically:

```bash
python main.py examples/phase0_simple_spec.txt --subsystem "Navigation"
```

### 4. Generate Reports

View historical trends:

```bash
# All reports (cost + quality)
python scripts/generate_reports.py

# Only cost report
python scripts/generate_reports.py --report cost

# Last 7 days
python scripts/generate_reports.py --days 7

# Save to file
python scripts/generate_reports.py --output reports/
```

## Cost Tracking Details

### How It Works

1. **Token Extraction**
   - Extracts token counts from LLM responses
   - Supports OpenAI, Anthropic, and Google/Gemini formats
   - Falls back to $0.00 if extraction fails

2. **Cost Calculation**
   - Uses actual model pricing from `config/llm_config.py`
   - Calculates input and output costs separately
   - Aggregates per-node costs for total

3. **Budget Management**
   - Checks budget before each node execution
   - Warns when approaching threshold
   - Halts execution if max budget exceeded

### Cost Display

During workflow execution:
```
[1/5] Extracting Requirements...
  ✓ Extracted 5 requirements (1.4s | $0.0015)
```

In results summary:
```
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Metric        ┃ Value          ┃
┣━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━┫
┃ Total Cost    ┃ $0.0123 (...)  ┃
┗━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━┛
```

Performance & Cost Breakdown:
```
┏━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┓
┃ Node      ┃ Time   ┃ % Time ┃ Cost ($) ┃
┣━━━━━━━━━━━╋━━━━━━━━╋━━━━━━━━╋━━━━━━━━━━┫
┃ Decompose ┃ 53.2s  ┃ 56.0%  ┃ $0.0089  ┃
┃ Analyze   ┃ 26.8s  ┃ 28.2%  ┃ $0.0021  ┃
┃ ...       ┃ ...    ┃ ...    ┃ ...      ┃
┃ TOTAL     ┃ 95.0s  ┃ 100.0% ┃ $0.0123  ┃
┗━━━━━━━━━━━┻━━━━━━━━┻━━━━━━━━┻━━━━━━━━━━┛
```

### Cost Tracking Modes

| Mode | Accuracy | Setup Required | Use Case |
|------|----------|----------------|----------|
| **Heuristic** | ±30% | None (default) | Development, testing |
| **LangSmith** | Precise | API key | Production, billing |

## Quality Monitoring Details

### Quality Metrics

Four dimensions scored 0.0-1.0:

| Metric | Description |
|--------|-------------|
| **Completeness** | All aspects covered, no gaps |
| **Clarity** | Unambiguous, understandable language |
| **Testability** | Clear acceptance criteria |
| **Traceability** | Proper parent-child linkage |

**Overall Score:** Average of all four dimensions

**Quality Gate:** Pass threshold = 0.80 (configurable via `--quality-threshold`)

### Quality Tracking

Automatically recorded after each workflow run:
- Overall score and dimension scores
- Validation passed/failed
- Iteration count
- Requirements count
- Timestamp and subsystem

### Quality Reports

View trends:
```bash
python scripts/generate_reports.py --report quality
```

Sample output:
```
Quality Trend Report (Last 30 days)

┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Metric                ┃ Value      ┃
┣━━━━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━┫
┃ Total Runs            ┃ 15         ┃
┃ Average Overall Score ┃ 0.874      ┃
┃ Pass Rate             ┃ 93.3%      ┃
┃ Average Iterations    ┃ 1.4        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━┛
```

## Energy Monitoring Details

### Methodology

Uses heuristic token-based estimation (±30% accuracy) based on published research from Epoch AI (Feb 2025) and Google (Aug 2025).

**Formula:**
`Total Energy (Wh) = (Input Tokens × E_in + Output Tokens × E_out) × PUE`

Where **PUE** (Power Usage Effectiveness) is ~1.10 for cloud datacenters.

### Energy Coefficients

| Model | Energy / 1K Tokens (Wh) | Notes |
|-------|-------------------------|-------|
| **Gemini 2.5 Flash** | 0.48 | Efficient (0.24 Wh / 500 tokens) |
| **GPT-4o** | 0.6 | Standard (0.3 Wh / 500 tokens) |
| **GPT-5 Nano** | 0.3 | High efficiency |
| **Claude 3.5 Sonnet** | 0.7 | Higher capacity |

### Contextual Comparisons

To make energy usage relatable, the system displays:
- **TV Usage:** Equivalent minutes of watching a 50W LED TV.
- **EV Distance:** Equivalent meters driven by an electric car (0.25 kWh/km).

## Budget Management

### Configuration

Set budget limits in `.env`:
```bash
COST_BUDGET_WARNING_THRESHOLD=1.00  # Yellow warning
COST_BUDGET_MAX=5.00                # Red error, execution stops
```

### Behavior

| Scenario | Display | Action |
|----------|---------|--------|
| `cost < warning` | Silent | Continue |
| `warning ≤ cost < max` | ⚠️ Yellow warning | Continue with warning |
| `cost ≥ max` | ⚠️ Red error | **Stop execution** |

### Example

```bash
# Set conservative budget for testing
export COST_BUDGET_MAX=0.50

python main.py large_document.pdf --subsystem "Safety"
```

If cost reaches $0.50:
```
⚠️  BUDGET EXCEEDED: $0.5123 >= $0.50 (stopping execution)
```

## Database Storage

### Location

```
checkpoints/
├── costs.db     # Cost history
└── quality.db   # Quality history
```

### Schema

**Cost Records:**
- `run_id`: Unique workflow identifier
- `timestamp`: When the run completed
- `total_cost`: Total cost for the run
- `subsystem`: Target subsystem
- `source_method`: 'langsmith' or 'heuristic'
- `node_costs`: Per-node cost breakdown
- `token_counts`: Input/output tokens per node

**Quality Records:**
- `run_id`: Unique workflow identifier
- `timestamp`: When the run completed
- `subsystem`: Target subsystem
- `overall_score`: Average quality score
- `completeness`, `clarity`, `testability`, `traceability`: Individual scores
- `validation_passed`: Boolean
- `iteration_count`: Number of refinement iterations
- `requirements_count`: Number of decomposed requirements

### Maintenance

Database files grow slowly (~1KB per run). Manual cleanup:

```bash
# Remove old records (older than 90 days)
sqlite3 checkpoints/costs.db \
  "DELETE FROM cost_runs WHERE datetime(timestamp) < datetime('now', '-90 days')"

sqlite3 checkpoints/quality.db \
  "DELETE FROM quality_runs WHERE datetime(timestamp) < datetime('now', '-90 days')"

# Optimize database
sqlite3 checkpoints/costs.db "VACUUM"
sqlite3 checkpoints/quality.db "VACUUM"
```

## Troubleshooting

### Cost showing as $0.0000

**Causes:**
1. Token extraction failed (LLM response format changed)
2. LangSmith not configured (using heuristic mode)
3. Very small documents (costs < $0.0001)

**Solutions:**
1. Enable LangSmith for precise tracking
2. Check that API responses include token metadata
3. Verify model pricing in `config/llm_config.py`

### Budget warnings not showing

**Causes:**
1. `COST_TRACKING_ENABLED=false` in `.env`
2. Cost below warning threshold
3. Token extraction failing

**Solutions:**
1. Set `COST_TRACKING_ENABLED=true`
2. Lower warning threshold for testing
3. Enable LangSmith integration

### Reports showing "No data available"

**Causes:**
1. No workflow runs in specified time period
2. Database files don't exist
3. Wrong database path

**Solutions:**
1. Run a workflow first: `python main.py ...`
2. Check `checkpoints/*.db` files exist
3. Verify working directory is project root

### Quality not tracked

**Causes:**
1. Workflow failed before validation
2. Quality metrics dict missing keys
3. Database write failure

**Solutions:**
1. Check workflow completes successfully
2. Review error logs in workflow output
3. Verify `checkpoints/` directory is writable

## Best Practices

### Development
- Use default heuristic mode (no setup required)
- Set conservative budget limits
- Review cost reports regularly
- Monitor quality trends for skill calibration

### Production
- **Enable LangSmith** for precise tracking
- Set appropriate budget limits for use case
- Archive old database records periodically
- Generate monthly cost/quality reports
- Alert on quality degradation trends

### Cost Optimization
1. **Identify expensive nodes** via cost breakdown
2. **Optimize prompts** in skills to reduce tokens
3. **Use cheaper models** where quality permits
4. **Enable caching** (future enhancement)
5. **Monitor trends** to catch cost spikes early

### Quality Optimization
1. **Track iteration counts** - high iterations indicate skill issues
2. **Compare subsystems** - identify problematic areas
3. **Monitor pass rates** - declining rates signal problems
4. **Review failed runs** - understand failure patterns
5. **Calibrate skills** based on quality feedback (future enhancement)

## API Reference

### Cost Tracker

```python
from src.utils.cost_tracker import get_cost_tracker

tracker = get_cost_tracker()

# Start tracking a run
tracker.start_run(run_id="20251112_143022_navigation")

# Record node cost
tracker.record_node_cost(
    node_name="extract",
    cost=0.0015,
    input_tokens=1200,
    output_tokens=300,
    model_name="gemini-2.5-flash-lite"
)

# Check budget
is_ok, warning = tracker.check_budget()
if not is_ok:
    raise RuntimeError(f"Budget exceeded: {warning}")

# Finalize run
record = tracker.finalize_run(
    subsystem="Navigation Subsystem",
    source_method="heuristic"
)

# Get trends
trends = tracker.get_cost_trends(days=30)
print(f"Average cost: ${trends['avg_cost']:.4f}")
```

### Quality Tracker

```python
from src.utils.quality_tracker import get_quality_tracker
from src.state import QualityMetrics

tracker = get_quality_tracker()

# Record quality
quality_metrics = QualityMetrics(...)  # From workflow
record = tracker.record_quality(
    run_id="20251112_143022_navigation",
    subsystem="Navigation Subsystem",
    quality_metrics=quality_metrics,
    validation_passed=True,
    iteration_count=1,
    requirements_count=15
)

# Get trends
trends = tracker.get_quality_trends(days=30)
print(f"Pass rate: {trends['pass_rate']:.1f}%")

# Compare subsystems
comparison = tracker.get_subsystem_comparison()
for subsystem, metrics in comparison.items():
    print(f"{subsystem}: {metrics['avg_score']:.3f}")
```

## Integration Examples

### Custom Budget Alert

```python
from src.utils.cost_tracker import get_cost_tracker
import smtplib

tracker = get_cost_tracker()
is_ok, warning = tracker.check_budget()

if warning and not is_ok:
    # Send email alert
    msg = f"Subject: Budget Alert\n\n{warning}"
    smtp.sendmail("from@example.com", "to@example.com", msg)
```

### Quality Degradation Alert

```python
from src.utils.quality_tracker import get_quality_tracker

tracker = get_quality_tracker()
trends = tracker.get_quality_trends(days=7)

if trends['avg_overall_score'] < 0.80:
    print(f"⚠️ Quality degradation detected: {trends['avg_overall_score']:.3f}")
    # Take action: recalibrate skills, review recent changes, etc.
```

## Related Documentation

- **Phase 5 Summary:** `docs/phases/phase5/README.md`
- **User Guide:** `docs/user_guide.md`
- **LLM Configuration:** `config/llm_config.py`
- **Skills Calibration:** Coming in Phase 6

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review Phase 5 documentation
3. Check error logs in workflow output
4. Open an issue on GitHub

---

**Last Updated:** November 12, 2025
**Phase:** 5 (Production Hardening & Enhanced Observability)
**Status:** ✅ Complete
