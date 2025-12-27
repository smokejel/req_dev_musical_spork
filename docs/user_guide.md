# Requirements Decomposition System - User Guide

**Version:** 1.2.0 (Phase 7 Complete - Domain-Aware Requirements)
**Last Updated:** 2025-12-03

## Table of Contents

1. [Introduction](#introduction)
2. [Quick Start](#quick-start)
3. [Installation](#installation)
4. [Basic Usage](#basic-usage)
5. [Command-Line Options](#command-line-options)
6. [Input Specification Format](#input-specification-format)
7. [Understanding Output](#understanding-output)
8. [Understanding Performance & Cost](#understanding-performance--cost) **NEW**
9. [Workflow Stages](#workflow-stages)
10. [Quality Metrics](#quality-metrics)
11. [Human Review](#human-review)
12. [Troubleshooting](#troubleshooting)
13. [Best Practices](#best-practices)
14. [Examples](#examples)
15. [FAQ](#faq)

---

## Introduction

The Requirements Decomposition System is an AI-powered tool that automatically decomposes high-level system requirements into detailed, testable subsystem requirements. It uses multiple LLM agents orchestrated through a LangGraph workflow to:

- Extract requirements from specification documents
- Analyze system context and constraints
- Decompose requirements with proper traceability
- Validate quality with automated scoring
- Generate professional documentation

### Key Features

- **Automated Decomposition**: Breaks down system requirements into detailed subsystem requirements
- **Multi-Format Support**: Reads .txt, .docx, and .pdf specification documents
- **Domain-Aware Processing**: Optional domain-specific conventions, glossary, and templates **NEW (Phase 7)**
- **Quality Validation**: Automated scoring across 4-5 dimensions (completeness, clarity, testability, traceability, domain compliance)
- **Human-in-the-Loop**: Review points at quality gates for manual oversight
- **Full Traceability**: Parent-child requirement mapping in CSV format
- **Professional Output**: Markdown documentation with organized directory structure
- **Real-Time Progress**: Live feedback during workflow execution
- **Configurable Weighting**: Customize quality dimension weights via environment variables **NEW (Phase 7)**

### Use Cases

1. **Systems Engineering**: Decompose system specs into subsystem requirements
2. **Requirements Engineering**: Break down high-level requirements for implementation
3. **Requirements Traceability**: Maintain parent-child relationships automatically
4. **Quality Assurance**: Validate requirement quality before implementation
5. **Documentation**: Generate professional requirements documents

---

## Quick Start

### Prerequisites

- Python 3.11+
- API keys for at least one LLM provider (OpenAI, Anthropic, or Google)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd req_dev_ARAD

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### First Run

```bash
# Run decomposition for Authentication subsystem
python main.py examples/phase0_simple_spec.txt --subsystem "Authentication"

# Check output
ls outputs/run_*
```

---

## Installation

### 1. System Requirements

- **Python:** 3.11 or higher
- **OS:** macOS, Linux, or Windows
- **RAM:** 4GB minimum (8GB recommended)
- **Disk Space:** 500MB for dependencies + output storage

### 2. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 3. Configure API Keys

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
# Edit .env with your API keys
```

**Required:** At least one LLM provider API key (OpenAI, Anthropic, or Google)
**Recommended:** LangSmith API key for precise cost tracking (Phase 5)

See `.env.example` for complete documentation including:
- LLM API keys (OpenAI, Anthropic, Google)
- LangSmith tracing configuration
- Cost tracking and budget management
- Application settings (quality threshold, max iterations)

### 4. Verify Installation

```bash
# Test with example specification
python main.py examples/phase0_simple_spec.txt --subsystem "Authentication"

# Should complete successfully and create output directory
```

---

## Basic Usage

### Command Structure

```bash
python main.py <spec_path> --subsystem "<subsystem_name>" [options]
```

### Essential Arguments

- **`spec_path`** (required): Path to specification document (.txt, .docx, or .pdf)
- **`--subsystem`** (required): Target subsystem name (e.g., "Navigation Subsystem", "Power Management")

### Simple Example

```bash
# Decompose requirements for Navigation subsystem
python main.py examples/train_spec.txt --subsystem "Navigation Subsystem"
```

### With Options

```bash
# Higher quality threshold
python main.py spec.docx --subsystem "Power" --quality-threshold 0.90

# Enable pre-decomposition review
python main.py spec.pdf --subsystem "Comms" --review-before-decompose

# Debug mode
python main.py spec.txt --subsystem "Safety" --debug
```

---

## Command-Line Options

### Required Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `spec_path` | Path to specification document | `examples/train_spec.txt` |
| `--subsystem` | Target subsystem name | `"Navigation Subsystem"` |

### Optional Quality Parameters

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--quality-threshold` | float | 0.80 | Quality gate threshold (0.0-1.0) |
| `--max-iterations` | int | 3 | Maximum refinement iterations before human review |

### Domain-Aware Options **NEW (Phase 7)**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--domain` | string | generic | Domain name for domain-aware decomposition (e.g., "csx_dispatch") |
| `--subsystem-id` | string | None | Subsystem identifier within domain (e.g., "train_management") |
| `--list-domains` | flag | - | List all available domains and exit |
| `--list-subsystems` | string | - | List subsystems for specified domain and exit |

**Example:**
```bash
# List available domains
python main.py --list-domains

# List subsystems for csx_dispatch domain
python main.py --list-subsystems csx_dispatch

# Run with domain context
python main.py spec.txt --subsystem "Train Management" \
  --domain csx_dispatch --subsystem-id train_management
```

### Workflow Options

| Option | Description |
|--------|-------------|
| `--review-before-decompose` | Enable human review after analysis, before decomposition |
| `--resume` | Resume from checkpoint (requires `--checkpoint-id`) |
| `--checkpoint-id` | Checkpoint ID to resume from |

### Display Options

| Option | Description |
|--------|-------------|
| `--visualize` | Display workflow graph visualization and exit |
| `--debug` | Enable debug mode with verbose logging |
| `--quiet` | Suppress progress output (errors only) |
| `--help` | Show help message and exit |

### Examples

```bash
# Visualize workflow
python main.py --visualize

# Quiet mode (only show errors)
python main.py spec.txt --subsystem "Nav" --quiet

# Custom quality threshold
python main.py spec.txt --subsystem "Power" --quality-threshold 0.85

# Maximum 5 iterations
python main.py spec.txt --subsystem "Comms" --max-iterations 5

# Pre-decomposition review
python main.py spec.txt --subsystem "Safety" --review-before-decompose

# Debug mode
python main.py spec.txt --subsystem "Control" --debug
```

---

## Input Specification Format

### Supported File Types

- **`.txt`**: Plain text files
- **`.docx`**: Microsoft Word documents
- **`.pdf`**: PDF documents

### Recommended Structure

For best results, structure your specification with:

1. **Clear section headings**
2. **Numbered or bulleted requirements**
3. **Consistent terminology**
4. **Explicit requirement statements** ("shall", "must", "should")

### Example Specification (Good)

```
System Requirements Specification
==================================

1. Functional Requirements

FR-001: The system shall support user authentication via OAuth 2.0.

FR-002: The system shall maintain an audit log of all user actions.

FR-003: The system shall support at least 1000 concurrent users.

2. Performance Requirements

PR-001: User login shall complete within 2 seconds under normal load.

3. Constraints

CN-001: The system shall run on Linux kernel 5.4 or higher.
```

### Example Specification (Needs Improvement)

```
The system needs authentication and should be fast. Also it needs to
work on Linux and handle lots of users. Make sure there's logging too.
```

**Issues:**
- No requirement IDs
- Vague language ("fast", "lots of users")
- Mixed concerns in single statement
- No testable criteria

### Tips for Better Specifications

1. **Use explicit requirement language**
   - Good: "The system shall authenticate users within 2 seconds"
   - Bad: "Authentication should be fast"

2. **One requirement per statement**
   - Good: "FR-001: Support OAuth. FR-002: Support 1000 users."
   - Bad: "Support OAuth and 1000 users and logging."

3. **Include quantitative criteria**
   - Good: "Response time < 500ms"
   - Bad: "Good response time"

4. **Use consistent terminology**
   - Good: Always use "user" (not "user"/"operator"/"person")
   - Bad: Mixed terminology

---

## Understanding Output

### Output Directory Structure

Each run creates a timestamped directory in `outputs/`:

```
outputs/
└── run_20251102_143022_navigation/
    ├── README.txt                # Run metadata and summary
    ├── requirements.md           # Detailed subsystem requirements
    ├── traceability.csv         # Parent-child requirement mapping
    └── quality_report.md        # Quality metrics and validation
```

### README.txt

Contains run metadata and quick summary:

```
Requirements Decomposition Run
==============================
Run ID: 20251102_143022_navigation
Spec: examples/train_spec.txt
Subsystem: Navigation
Status: Complete (8 requirements)
Timestamp: 2025-11-02 14:30:22

Generated Files:
- requirements.md: Detailed subsystem requirements
- traceability.csv: Parent-child requirement mapping
- quality_report.md: Quality metrics and validation results

Quality Score: 0.85 (PASSED)
Iterations: 1
Human Review: No
```

### requirements.md

Professional markdown document with decomposed requirements:

```markdown
# Navigation Subsystem Requirements

**Generated:** 2025-11-02 14:30:22
**Source Specification:** examples/train_spec.txt
**Quality Score:** 0.85 (PASSED)

## Overview
This document contains detailed requirements for the Navigation subsystem,
decomposed from system-level requirements.

## Functional Requirements

### NAV-FUNC-001: Route Calculation
**Parent:** SYS-FR-001
**Type:** Functional
**Priority:** High

**Description:**
The Navigation subsystem shall calculate optimal routes between stations
considering current track conditions and speed restrictions.

**Acceptance Criteria:**
- Route calculation completes within 500ms
- Route considers all active speed restrictions
- Route minimizes total travel time

**Source:** Section 2.1 - Navigation Services

### NAV-FUNC-002: GPS Positioning
...
```

### traceability.csv

Parent-child requirement mapping:

```csv
Child ID,Parent ID,Child Text,Parent Text,Relationship Type
NAV-FUNC-001,SYS-FR-001,"Calculate optimal routes...","System shall provide navigation...","decomposition"
NAV-FUNC-002,SYS-FR-001,"Provide GPS positioning...","System shall provide navigation...","decomposition"
NAV-PERF-001,SYS-PR-002,"Route calculation < 500ms...","Navigation performance...","decomposition"
```

### quality_report.md

Detailed quality metrics and validation results:

```markdown
# Quality Validation Report

**Overall Score:** 0.85 (PASSED)
**Threshold:** 0.80
**Validation Date:** 2025-11-02 14:30:22

## Metrics

| Dimension | Score | Status |
|-----------|-------|--------|
| Completeness | 0.90 | ✅ PASS |
| Clarity | 0.85 | ✅ PASS |
| Testability | 0.80 | ✅ PASS |
| Traceability | 0.95 | ✅ PASS |

## Issues Found

None - all requirements meet quality threshold.

## Recommendations

- Consider adding more detailed acceptance criteria for NAV-FUNC-003
- Performance metrics could be more specific in NAV-PERF-002
```

### Zero Requirements Output

When no requirements are allocated (valid outcome):

```
outputs/
└── run_20251102_220036_navigation/
    ├── README.txt              # Shows "No requirements allocated"
    └── allocation_report.md    # Detailed explanation
```

**allocation_report.md:**

```markdown
# Allocation Report: Navigation

**Status:** No Requirements Allocated

## Summary
- **Specification Document:** examples/phase0_simple_spec.txt
- **Target Subsystem:** Navigation
- **Total Requirements Extracted:** 5
- **Requirements Allocated to Navigation:** 0

## Reason
No extracted requirements matched the allocation rules for the Navigation subsystem.

This is a valid outcome - it indicates that the specification document does not
contain requirements applicable to this subsystem.

## Recommendations
1. Verify subsystem name is correct
2. Review allocation rules
3. Check specification content
4. Try a different subsystem

**Note:** This is not an error. The system correctly determined that no requirements
from the specification apply to the Navigation subsystem.
```

---

## Understanding Performance & Cost

**New in Phase 4.2:** Real-time performance monitoring and cost tracking

### Performance Monitoring

Every workflow run displays detailed performance metrics showing timing breakdown per node:

```
Performance & Cost Breakdown
┌───────────────────────────┬─────────────────┬─────────────────┬─────────────────┐
│ Node                      │        Time (s) │          % Time │        Cost ($) │
├───────────────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ Decompose                 │            25.2 │           55.8% │          $0.000 │
│ Analyze                   │            17.9 │           39.5% │          $0.045 │
│ Extract                   │             2.1 │            4.6% │          $0.002 │
│ Document                  │             0.0 │            0.0% │          $0.001 │
│ Validate                  │             0.0 │            0.0% │          $0.000 │
│ TOTAL                     │            45.2 │          100.0% │          $0.048 │
└───────────────────────────┴─────────────────┴─────────────────┴─────────────────┘
Note: Cost estimates are approximate (±30%). Enable LangSmith for precise tracking.
```

### Interpreting Timing Breakdown

**Column Descriptions:**
- **Node:** Workflow stage (Extract, Analyze, Decompose, Validate, Document)
- **Time (s):** Execution duration in seconds
- **% Time:** Percentage of total workflow time
- **Cost ($):** Estimated LLM API cost

**Typical Timing Patterns:**

**Small Documents (5-10 requirements):**
```
Extract:    2-5s    (10%)
Analyze:   10-20s   (40%)
Decompose: 10-20s   (40%)
Validate:   2-5s    (10%)
Document:   <1s     (0%)
Total:     25-50s
```

**Large Documents (30-50 requirements):**
```
Extract:   5-15s    (10%)
Analyze:  30-60s    (40%)
Decompose: 30-60s   (45%)
Validate:  5-10s    (5%)
Document:  <1s      (0%)
Total:    70-150s
```

**Bottleneck Identification:**
- **Decompose >50%:** Complex decomposition, many requirements
- **Analyze >50%:** Complex system context, intricate architecture
- **Extract >20%:** Large PDF/DOCX parsing, many requirements
- **Validate >10%:** Quality refinement loop active (multiple iterations)

### Cost Estimation

**How Cost Estimation Works:**

The system uses heuristic-based calculation to estimate LLM API costs:

1. **Token Estimation:**
   - Input tokens ≈ document size + skill size + context
   - Output tokens ≈ number of requirements × average requirement length

2. **Model Pricing:**
   - Each model has configured cost per 1K tokens (input/output)
   - Extract: Gemini 2.5 Flash-Lite ($0.0001/$0.0004 per 1K)
   - Analyze: Claude Sonnet 3.5 ($0.003/$0.015 per 1K)
   - Decompose: GPT-5 Nano ($0.0002/$0.0008 per 1K)
   - Validate: Gemini 2.5 Flash ($0.0002/$0.0008 per 1K)

3. **Calculation:**
   ```
   cost = (input_tokens / 1000) × input_price +
          (output_tokens / 1000) × output_price
   ```

**Accuracy:**
- **±30% typical** - heuristic estimation without precise token counting
- Enable LangSmith for exact token counts and costs

**Typical Costs per Run:**

| Document Size | Requirements | Typical Cost | Range |
|---------------|-------------|--------------|-------|
| Small (5-10) | 5-15 | $0.01-0.05 | $0.005-$0.10 |
| Medium (10-30) | 15-40 | $0.05-0.15 | $0.03-$0.25 |
| Large (30-100) | 40-100 | $0.15-0.50 | $0.10-$1.00 |

**Cost Factors:**
- **Document size** - larger specs = more input tokens
- **Number of requirements** - more requirements = more output tokens
- **Refinement iterations** - quality loop adds decompose + validate costs
- **Model selection** - Claude Sonnet costs more than Gemini/GPT-5 Nano

### Budget Management

**Monitoring Costs:**

1. **Check Per-Run Estimates:**
   - Displayed in Results Summary after each run
   - Shown in Performance & Cost Breakdown table

2. **Track Over Time:**
   - Save terminal output to log files
   - Parse cost estimates from logs
   - Sum across multiple runs

3. **Enable LangSmith (Optional):**
   - Precise token counting
   - Exact cost tracking
   - Historical cost analysis

**Example:**
```bash
# Save run output with cost info
python main.py spec.txt --subsystem "Nav" 2>&1 | tee run_log.txt

# Check cost estimate
grep "Estimated Cost" run_log.txt
```

**Controlling Costs:**

1. **Choose Appropriate Models:**
   - Current config optimized for cost-performance balance
   - Gemini 2.5 Flash-Lite (extract) is most cost-efficient
   - GPT-5 Nano (decompose) has no TPM limits

2. **Optimize Quality Threshold:**
   - Higher threshold → more iterations → higher cost
   - Start with 0.80 (default), adjust based on results

3. **Use Smaller Documents:**
   - Break large specs into smaller sections
   - Process one subsystem at a time

4. **Limit Iterations:**
   - Default max_iterations = 3
   - Reduce if budget-constrained: `--max-iterations 1`

### Performance Optimization Tips

**Reduce Extract Time:**
- Use .txt format instead of .pdf/.docx
- Smaller documents parse faster
- Split large specs into sections

**Reduce Analyze Time:**
- Simplify system architecture descriptions
- Focus on relevant subsystems only
- Provide clear subsystem boundaries

**Reduce Decompose Time:**
- Better input specs = less LLM reasoning time
- Clear allocation rules = faster filtering
- Fewer requirements = faster decomposition

**Reduce Validate Time:**
- Higher quality inputs = fewer iterations
- Appropriate threshold = less refinement
- Clear requirements = faster scoring

### LangSmith Integration (Optional)

For **precise** performance and cost tracking, enable LangSmith:

**Setup:**

1. Create account at https://smith.langchain.com
2. Get API key from dashboard
3. Add to `.env`:

```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your-langsmith-key
LANGCHAIN_PROJECT=requirements-decomposition
```

**Benefits:**
- **Exact token counts** - precise input/output tokens per call
- **Actual costs** - calculated from real token usage
- **Trace visualization** - see full LLM call chain
- **Performance analysis** - identify slow API calls
- **Historical tracking** - compare runs over time

**Cost:**
- Free tier: 5K traces/month
- Paid tier: $39/month for 50K traces

**When to Use:**
- Production deployments
- Cost-sensitive projects
- Performance optimization
- Team collaboration

**When Not Needed:**
- MVP testing
- Occasional use
- ±30% accuracy acceptable

---

## Workflow Stages

The decomposition workflow consists of 5 stages, executed sequentially:

### 1. Extract (RequirementsAnalystAgent)

**Purpose:** Parse specification document and extract high-level requirements

**What It Does:**
- Reads specification document (.txt, .docx, .pdf)
- Identifies requirement statements
- Assigns unique IDs
- Extracts metadata (type, section, priority)

**LLM:** Gemini 2.5 Flash-Lite (1M context window, ultra-fast)

**Example Output:**
```
[1/5] Extracting Requirements...
  ✓ Extracted 15 requirements (5.7s)
```

### 2. Analyze (SystemArchitectAgent)

**Purpose:** Understand system context and create decomposition strategy

**What It Does:**
- Analyzes system architecture
- Identifies subsystem boundaries
- Creates allocation rules
- Defines naming conventions
- Plans decomposition patterns

**LLM:** Claude 3.5 Sonnet (architectural reasoning)

**Example Output:**
```
[2/5] Analyzing System Context...
  ✓ Generated decomposition strategy (27.0s)
```

**Optional:** Human review before decomposition (`--review-before-decompose`)

### 3. Decompose (RequirementsEngineerAgent)

**Purpose:** Break down system requirements into detailed subsystem requirements

**What It Does:**
- Applies allocation rules to filter requirements
- Decomposes applicable requirements (1:1, 1:N patterns)
- Maintains parent-child traceability
- Follows naming convention
- Generates acceptance criteria

**LLM:** GPT-4o (complex reasoning)

**Example Output:**
```
[3/5] Decomposing Requirements...
  ✓ Decomposed 8 requirements (15.3s)
```

Or if zero requirements allocated:
```
[3/5] Decomposing Requirements...
  ✓ No requirements allocated to subsystem (3.6s)
```

### 4. Validate (QualityAssuranceAgent)

**Purpose:** Assess quality of decomposed requirements

**What It Does:**
- Scores 4 quality dimensions (0.0-1.0):
  - **Completeness:** All aspects covered
  - **Clarity:** Unambiguous language
  - **Testability:** Clear acceptance criteria
  - **Traceability:** Proper parent-child links
- Calculates overall score
- Identifies specific issues
- Generates refinement feedback

**LLM:** Gemini 1.5 Pro (critical evaluation)

**Example Output:**
```
[4/5] Validating Quality...
  ✓ Quality score: 0.85 (PASSED) (3.2s)
```

**Quality Gate Routing:**
- **Score ≥ threshold** → PASS (continue to documentation)
- **Score < threshold AND iterations < max** → REVISE (loop back to decompose)
- **Score < threshold AND iterations ≥ max** → HUMAN REVIEW
- **Zero requirements** → PASS with 1.0 score (valid outcome)

### 5. Document

**Purpose:** Generate final documentation and outputs

**What It Does:**
- Creates requirements.md (detailed requirements)
- Generates traceability.csv (parent-child mapping)
- Produces quality_report.md (validation results)
- Writes README.txt (run metadata)

**Example Output:**
```
[5/5] Generating Documentation...
  ✓ Documentation complete (1.1s)
```

### Refinement Loop

If validation fails (score < threshold):

```
decompose → validate → [FAIL] → decompose (with refinement feedback)
          ↓
       [iteration 2]
          ↓
validate → [FAIL] → decompose (with refinement feedback)
          ↓
       [iteration 3]
          ↓
validate → [FAIL] → HUMAN REVIEW (max iterations reached)
```

---

## Quality Metrics

### Scoring System

Each requirement is scored 0.0-1.0 across **4 dimensions** (generic) or **5 dimensions** (domain-aware):

#### 1. Completeness (0.0-1.0)

**Measures:** Are all aspects of the requirement covered?

**Good (0.9+):**
```
REQ-001: The navigation system shall calculate optimal routes considering:
- Current track conditions
- Active speed restrictions
- Station dwell times
- Maintenance schedules
```

**Poor (0.5):**
```
REQ-001: The system shall calculate routes.
```

#### 2. Clarity (0.0-1.0)

**Measures:** Is the requirement unambiguous and understandable?

**Good (0.9+):**
```
REQ-002: Route calculation shall complete within 500 milliseconds for
routes up to 100 kilometers in length.
```

**Poor (0.5):**
```
REQ-002: Route calculation should be fast.
```

#### 3. Testability (0.0-1.0)

**Measures:** Can the requirement be objectively verified?

**Good (0.9+):**
```
REQ-003: GPS position accuracy shall be within 10 meters (95th percentile)
when traveling at speeds up to 200 km/h.

Acceptance Criteria:
- Test with GNSS simulator at various speeds
- Record 1000 position samples
- Verify 95% are within 10m of ground truth
```

**Poor (0.5):**
```
REQ-003: GPS shall be accurate.
```

#### 4. Traceability (0.0-1.0)

**Measures:** Is parent-child relationship clear and correct?

**Good (0.9+):**
```
REQ-NAV-001: [Derived from SYS-FR-005]
The Navigation subsystem shall calculate optimal routes...

Parent Requirement (SYS-FR-005):
"The train control system shall provide navigation services..."
```

**Poor (0.5):**
```
REQ-NAV-001: Calculate routes.
[No parent ID specified]
```

#### 5. Domain Compliance (0.0-1.0) **NEW (Phase 7)**

**Measures:** Adherence to domain-specific conventions, glossary, templates, and naming patterns.

**Applicability:** Only scored when `--domain` is specified (not for generic decomposition).

**Good (0.9+):**
```
TM-FR-001: The Train Management subsystem shall maintain an Active Train
list containing all trains currently operating within the Dispatcher's
Territory.

✓ ID format follows domain convention (TM-FR-NNN)
✓ Glossary terms capitalized ("Active Train", "Territory")
✓ Template structure followed
✓ Modal verb "shall" used correctly
```

**Poor (0.5):**
```
train-mgmt-001: The system should track active trains in the territory.

✗ ID format incorrect (should be TM-FR-001)
✗ Glossary terms not capitalized
✗ Weak modal verb "should" instead of "shall"
✗ Missing domain-specific context
```

**Scoring Breakdown:**
- **Template Format (25%):** Correct structure and sections
- **Glossary Terms (30%):** Proper capitalization and usage
- **ID Format (25%):** Follows domain naming convention
- **Naming Patterns (20%):** Consistent terminology and modal verbs

### Overall Score

**Generic (4 dimensions):**
```
overall_score = (completeness + clarity + testability + traceability) / 4
```

**Domain-Aware (5 dimensions):**
```
overall_score = (completeness + clarity + testability + traceability + domain_compliance) / 5
```

**Configurable Weighting (Phase 7.3):**

You can customize dimension weights via environment variables (must sum to 1.0):

```bash
# Generic (4 dimensions - default: 0.25 each)
QUALITY_WEIGHT_COMPLETENESS=0.25
QUALITY_WEIGHT_CLARITY=0.25
QUALITY_WEIGHT_TESTABILITY=0.25
QUALITY_WEIGHT_TRACEABILITY=0.25

# Domain-Aware (5 dimensions - default: 0.20 each)
QUALITY_WEIGHT_COMPLETENESS=0.20
QUALITY_WEIGHT_CLARITY=0.20
QUALITY_WEIGHT_TESTABILITY=0.20
QUALITY_WEIGHT_TRACEABILITY=0.20
QUALITY_WEIGHT_DOMAIN_COMPLIANCE=0.20
```

Example (prioritize testability):
```bash
QUALITY_WEIGHT_COMPLETENESS=0.20
QUALITY_WEIGHT_CLARITY=0.20
QUALITY_WEIGHT_TESTABILITY=0.35  # Higher weight
QUALITY_WEIGHT_TRACEABILITY=0.25
```

### Quality Threshold

Default: **0.80** (configurable via `--quality-threshold`)

- **Score ≥ 0.80:** PASS (high quality)
- **Score < 0.80:** NEEDS REVIEW (requires refinement or human review)

### Special Cases

**Zero Requirements:**
- Score: **1.00** (PASSED)
- Reason: Valid outcome when no requirements allocated
- No human review triggered
- Allocation report generated instead

---

## Human Review

### When Human Review Is Triggered

1. **Quality Gate Failure** (automatic)
   - Overall score < threshold
   - Max iterations reached

2. **Pre-Decomposition Review** (optional)
   - Flag: `--review-before-decompose`
   - Triggered after analysis, before decomposition

3. **Fatal Errors** (automatic)
   - Unrecoverable errors during execution

### Review Interface

When human review is triggered, you'll see:

```
╭─────────────────────────────────────────────────────────╮
│          Human Review Required                          │
│  Quality Gate Failed - Review Needed                    │
╰─────────────────────────────────────────────────────────╯

Quality Metrics:
  Overall Score: 0.72 (Threshold: 0.80)
  Completeness: 0.85
  Clarity: 0.70
  Testability: 0.65
  Traceability: 0.90

Iteration: 3 / 3 (max reached)

Issues Found:
  • REQ-NAV-001: Acceptance criteria unclear
  • REQ-NAV-003: Missing testable conditions
  • REQ-NAV-007: Ambiguous performance metric

Decomposed Requirements:
┌────────────────┬──────────────────────────────────────┐
│ ID             │ Description                          │
├────────────────┼──────────────────────────────────────┤
│ NAV-FUNC-001   │ Calculate optimal routes...          │
│ NAV-FUNC-002   │ Provide GPS positioning...           │
│ NAV-PERF-001   │ Route calculation performance...     │
└────────────────┴──────────────────────────────────────┘

Options:
  [A] Approve and continue (generate documentation despite low score)
  [R] Request revision (provide feedback for another iteration)
  [Q] Quit workflow (abandon this run)

Your choice [A/R/Q]:
```

### Review Options

#### Option A: Approve

- **What Happens:** Workflow continues to documentation
- **When to Use:**
  - Issues are minor and acceptable
  - Manual fixes preferred over LLM refinement
  - Time constraints

**Example:**
```
Your choice [A/R/Q]: A

✓ Approved by human reviewer
Continuing to documentation...

[5/5] Generating Documentation...
```

#### Option R: Revise

- **What Happens:** Workflow loops back to decompose with your feedback
- **When to Use:**
  - Issues are fixable by LLM
  - More iteration would improve quality
  - Specific improvements identified

**Example:**
```
Your choice [A/R/Q]: R

Provide feedback for the Requirements Engineer Agent:
> Make acceptance criteria more specific. Include numerical thresholds
  for performance requirements. Clarify ambiguous terms in NAV-FUNC-001.

✓ Feedback recorded
Restarting decomposition with refinement guidance...

[3/5] Decomposing Requirements... (iteration 4)
```

#### Option Q: Quit

- **What Happens:** Workflow terminates immediately
- **When to Use:**
  - Fundamental issues with input specification
  - Wrong subsystem selected
  - Need to adjust allocation rules

**Example:**
```
Your choice [A/R/Q]: Q

⚠️ Workflow abandoned by user
No output files generated
```

### Pre-Decomposition Review

Enable with `--review-before-decompose`:

```bash
python main.py spec.txt --subsystem "Nav" --review-before-decompose
```

**Review Point:** After analysis, before decomposition

**Purpose:** Verify decomposition strategy before executing decomposition

```
╭─────────────────────────────────────────────────────────╮
│          Pre-Decomposition Review                       │
╰─────────────────────────────────────────────────────────╯

Extracted Requirements: 15
Target Subsystem: Navigation

Decomposition Strategy:
  Naming Convention: NAV-{TYPE}-{NNN}
  Allocation Rules:
    - IF involves route calculation → allocate
    - IF involves GPS positioning → allocate
    - IF involves authentication → do NOT allocate

Options:
  [A] Approve strategy and continue to decomposition
  [R] Revise strategy (provide feedback to System Architect)
  [Q] Quit workflow

Your choice [A/R/Q]:
```

---

## Troubleshooting

### Common Issues

#### 1. No Requirements Allocated

**Symptom:**
```
[3/5] Decomposing Requirements...
  ✓ No requirements allocated to subsystem (3.6s)

Results Summary:
  Decomposed Requirements: 0 (None allocated)
```

**Cause:** Specification doesn't contain requirements for target subsystem

**Solution:**
- Check `allocation_report.md` for explanation
- Verify subsystem name is correct
- Try different subsystem
- Review specification content

**This is NOT an error** - it's a valid outcome.

#### 2. Quality Gate Failure

**Symptom:**
```
[4/5] Validating Quality...
  ✓ Quality score: 0.72 (NEEDS REVIEW) (3.2s)

Human Review Required
```

**Cause:** Requirements don't meet quality threshold (default 0.80)

**Solutions:**
- **Approve:** If issues are minor
- **Revise:** Provide specific feedback for improvement
- **Lower threshold:** `--quality-threshold 0.70` (not recommended)
- **Check input spec:** May need better source requirements

#### 3. API Rate Limit

**Symptom:**
```
[1/5] Extracting Requirements...
  ✗ Failed: Rate limit exceeded (5.2s)
```

**Cause:** Too many API requests to LLM provider

**Solutions:**
- Wait and retry (automatic retry with exponential backoff)
- Use different API key
- Reduce request frequency

#### 4. Parse Error (PDF/DOCX)

**Symptom:**
```
✗ Fatal Error: Failed to parse specification document
```

**Cause:** Corrupted or unsupported document format

**Solutions:**
- Convert to .txt format
- Check file isn't password-protected
- Verify file isn't corrupted
- Use simpler document formatting

#### 5. Missing API Key

**Symptom:**
```
✗ Fatal Error: No valid LLM API keys configured
```

**Cause:** Missing or invalid API keys in `.env`

**Solutions:**
- Check `.env` file exists
- Verify API keys are valid
- Ensure at least one provider key is set
- Check for typos in environment variable names

#### 6. Checkpoint Not Found

**Symptom:**
```
✗ Fatal Error: Checkpoint ID not found: 20251102_143022_nav
```

**Cause:** Resume with invalid checkpoint ID

**Solutions:**
- Check checkpoint ID spelling
- Verify checkpoint exists in `checkpoints/` directory
- Don't use spaces or special characters in checkpoint ID

#### 7. Domain Loading Failure **NEW (Phase 7)**

**Symptom:**
```
[1/5] Extracting Requirements...
  ⚠️ Domain loading failed, using generic domain: Domain 'my_domain' not found
  ✓ Extracted 15 requirements (8.1s)
```

**Cause:** Specified domain doesn't exist or has invalid structure

**Solutions:**
- Use `--list-domains` to see available domains
- Check domain directory exists: `domains/<domain_name>/`
- Verify required files present:
  - `domain_config.json`
  - `conventions.md`
  - `glossary.md`
- Check domain registered in `config/domain_config.py`
- Verify JSON syntax in `domain_config.json`

**Note:** System automatically falls back to generic domain (4-dimension scoring)

#### 8. Low Domain Compliance Score **NEW (Phase 7)**

**Symptom:**
```
Quality Metrics:
  Domain Compliance: 0.45 ✗ (below 0.80)

Issues:
  - ID format incorrect: Expected TM-FR-NNN, got TM-001
  - Glossary terms not capitalized: "active train" should be "Active Train"
  - Template structure incomplete: Missing Rationale section
```

**Cause:** Requirements don't follow domain conventions

**Solutions:**
- **Review domain conventions:** Check `domains/<domain>/conventions.md`
- **Check glossary:** Ensure terms match `domains/<domain>/glossary.md` capitalization
- **Verify ID format:** Follow naming pattern in decomposition strategy
- **Template compliance:** Include all required sections (Description, Acceptance Criteria, Rationale)
- **Modal verbs:** Use "shall" for requirements, "should" for recommendations

**Tip:** Run without domain first (`--domain generic`) to validate core quality, then add domain for compliance checking.

### Debug Mode

Enable detailed logging:

```bash
python main.py spec.txt --subsystem "Nav" --debug
```

Provides:
- Full stack traces
- LLM prompts and responses
- State transitions
- Timing breakdowns

### Getting Help

1. **Check documentation:**
   - This user guide
   - `docs/phases/` for implementation details
   - `CLAUDE.md` for architecture overview

2. **Review logs:**
   - Terminal output
   - LangSmith traces (if enabled)
   - Error messages in output

3. **Test with examples:**
   - `examples/phase0_simple_spec.txt` (known good input)
   - Compare your spec to example format

4. **File issues:**
   - GitHub issues (if repository is public)
   - Include debug output and spec (if sharable)

---

## Best Practices

### Input Specifications

1. **Use clear requirement language**
   - "shall" for mandatory requirements
   - "should" for desired features
   - "may" for optional features

2. **Include requirement IDs** in source document
   - Easier to maintain traceability
   - Simpler cross-reference

3. **Organize by section**
   - Functional requirements
   - Performance requirements
   - Constraints
   - Interfaces

4. **Be specific and quantitative**
   - Include numerical thresholds
   - Define measurable criteria
   - Specify conditions and context

### Subsystem Selection

1. **Use consistent names**
   - Match names from system architecture
   - Use full names, not abbreviations
   - Be case-sensitive

2. **One subsystem per run**
   - Simpler to manage
   - Easier to review
   - Better for iteration

3. **Test with simple subsystem first**
   - Verify workflow works
   - Calibrate quality threshold
   - Understand output format

### Quality Threshold

1. **Start with default (0.80)**
   - Good balance of quality and automation
   - Proven in testing

2. **Adjust based on domain**
   - Higher (0.85-0.90) for safety-critical systems
   - Lower (0.70-0.75) for early-stage prototypes

3. **Monitor human review frequency**
   - Too many reviews → lower threshold
   - No reviews ever → consider raising threshold

### Iteration Management

1. **Use default max iterations (3)**
   - Enough for refinement
   - Prevents infinite loops
   - Forces human review if needed

2. **Provide specific feedback**
   - Point to specific requirements
   - Suggest concrete improvements
   - Reference quality dimensions

3. **Track iteration patterns**
   - If always hitting max → adjust threshold
   - If never iterating → verify quality metrics

### Output Management

1. **Review all generated files**
   - requirements.md (detailed requirements)
   - traceability.csv (parent-child mapping)
   - quality_report.md (metrics and issues)

2. **Archive important runs**
   - Copy output directories to permanent storage
   - Include README.txt for context

3. **Compare multiple runs**
   - Different subsystems
   - Different quality thresholds
   - Different input specs

### Performance Optimization

1. **Use appropriate file formats**
   - .txt is fastest to parse
   - .docx requires conversion
   - .pdf can be slow for large documents

2. **Monitor costs**
   - LangSmith shows token usage
   - Typical run: $0.10-$0.50
   - Adjust model choices if needed

3. **Leverage caching**
   - Checkpoints enable resumption
   - Response caching reduces costs

---

## Examples

### Example 1: Simple Authentication Subsystem

**Input:** `examples/phase0_simple_spec.txt`

```
System Requirements
===================

FR-001: The system shall support user authentication via OAuth 2.0.
FR-002: The system shall maintain an audit log of all user actions.
FR-003: The system shall support at least 1000 concurrent users.
PR-001: User login shall complete within 2 seconds under normal load.
CN-001: The system shall run on Linux kernel 5.4 or higher.
```

**Command:**
```bash
python main.py examples/phase0_simple_spec.txt --subsystem "Authentication"
```

**Output:** `outputs/run_20251102_143022_authentication/`

**requirements.md:**
```markdown
## Functional Requirements

### AUTH-FUNC-001: OAuth 2.0 Implementation
**Parent:** FR-001
**Type:** Functional

**Description:**
The Authentication subsystem shall implement OAuth 2.0 protocol for user
authentication, supporting authorization code flow.

**Acceptance Criteria:**
- OAuth 2.0 authorization code flow implemented
- Support for token refresh
- Secure token storage
- Token expiration handling

### AUTH-FUNC-002: Audit Logging Integration
**Parent:** FR-002
**Type:** Functional

**Description:**
The Authentication subsystem shall log all authentication events to the
system audit log.

**Acceptance Criteria:**
- Login attempts logged (success and failure)
- Logout events logged
- Token refresh logged
- Log entries include timestamp, user ID, IP address

## Performance Requirements

### AUTH-PERF-001: Login Performance
**Parent:** PR-001
**Type:** Performance

**Description:**
The Authentication subsystem shall complete user login within 2 seconds
under normal load (up to 1000 concurrent users).

**Acceptance Criteria:**
- 95th percentile login time ≤ 2 seconds
- Measured under load of 100 logins/second
- All OAuth flows complete within timeout
```

**Quality Score:** 0.85 (PASSED)

---

### Example 2: Zero Requirements (Valid Outcome)

**Input:** `examples/phase0_simple_spec.txt`

**Command:**
```bash
python main.py examples/phase0_simple_spec.txt --subsystem "Navigation"
```

**Output:** `outputs/run_20251102_220036_navigation/`

**README.txt:**
```
Requirements Decomposition Run
==============================
Run ID: 20251102_220036_navigation
Spec: examples/phase0_simple_spec.txt
Subsystem: Navigation
Status: No requirements allocated
Timestamp: 2025-11-02 22:00:36

Result:
No requirements from the specification were allocated to the Navigation subsystem.
This is a valid outcome indicating the specification does not contain requirements
applicable to this subsystem.

Generated Files:
- allocation_report.md: Detailed explanation and recommendations
```

**allocation_report.md:**
```markdown
# Allocation Report: Navigation

**Status:** No Requirements Allocated

## Summary
- **Total Requirements Extracted:** 5
- **Requirements Allocated to Navigation:** 0

## Reason
No extracted requirements matched the allocation rules for the Navigation subsystem.

This is a valid outcome.

## Next Steps
1. Try a different subsystem: "Authentication", "Audit", "Performance"
2. Verify specification contains navigation requirements
```

**Quality Score:** 1.00 (PASSED) - valid outcome

---

### Example 3: Pre-Decomposition Review

**Command:**
```bash
python main.py examples/train_spec.txt --subsystem "Navigation" --review-before-decompose
```

**Execution:**
```
[1/5] Extracting Requirements...
  ✓ Extracted 25 requirements (7.3s)

[2/5] Analyzing System Context...
  ✓ Generated decomposition strategy (32.1s)

╭─────────────────────────────────────────────────────────╮
│          Pre-Decomposition Review                       │
╰─────────────────────────────────────────────────────────╯

Extracted Requirements: 25
Target Subsystem: Navigation

Decomposition Strategy:
  Naming Convention: NAV-{TYPE}-{NNN}
  Patterns: 1:1, 1:N

  Allocation Rules:
    ✓ Route calculation → allocate
    ✓ GPS positioning → allocate
    ✗ Authentication → do NOT allocate
    ✗ Audit logging → do NOT allocate

Estimated Requirements: 8-12

Options:
  [A] Approve and continue
  [R] Revise strategy
  [Q] Quit

Your choice [A/R/Q]: A

✓ Strategy approved

[3/5] Decomposing Requirements...
  ✓ Decomposed 10 requirements (18.7s)
```

**Use Case:** Verify allocation rules before expensive decomposition step

---

### Example 4: Quality Refinement Loop

**Command:**
```bash
python main.py examples/complex_spec.txt --subsystem "Control" --quality-threshold 0.85
```

**Execution:**
```
[1/5] Extracting Requirements...
  ✓ Extracted 40 requirements (12.1s)

[2/5] Analyzing System Context...
  ✓ Generated decomposition strategy (45.2s)

[3/5] Decomposing Requirements... (iteration 1)
  ✓ Decomposed 18 requirements (28.4s)

[4/5] Validating Quality...
  ✓ Quality score: 0.78 (NEEDS REVIEW) (5.3s)

Refinement feedback generated:
  - Improve acceptance criteria specificity
  - Add numerical thresholds to performance requirements
  - Clarify ambiguous terms

[3/5] Decomposing Requirements... (iteration 2)
  ✓ Decomposed 18 requirements (32.1s)

[4/5] Validating Quality...
  ✓ Quality score: 0.83 (NEEDS REVIEW) (5.1s)

Refinement feedback generated:
  - Further specify test conditions
  - Add edge case handling

[3/5] Decomposing Requirements... (iteration 3)
  ✓ Decomposed 18 requirements (29.8s)

[4/5] Validating Quality...
  ✓ Quality score: 0.87 (PASSED) (4.9s)

[5/5] Generating Documentation...
  ✓ Documentation complete (2.3s)

Results Summary:
  Quality Score: 0.87 (✅ PASSED)
  Iterations: 3
```

**Note:** Automatic refinement improved quality from 0.78 → 0.87 in 3 iterations

---

### Example 5: Domain-Aware Decomposition **NEW (Phase 7)**

**Input:** `examples/csx_dispatch_spec.txt`

```
System Requirements: CSX Dispatch Train Management System
==========================================================

SYS-TM-001: The system shall maintain real-time tracking of all active
trains within the dispatcher's territory.

SYS-TM-002: The system shall provide movement authority management for
trains entering and exiting track blocks.

SYS-TM-003: The system shall display train positions on the territory
map with automatic updates every 30 seconds.
```

**Command:**
```bash
# List available domains
python main.py --list-domains

# List subsystems for csx_dispatch
python main.py --list-subsystems csx_dispatch

# Run with domain context
python main.py examples/csx_dispatch_spec.txt \
  --subsystem "Train Management" \
  --domain csx_dispatch \
  --subsystem-id train_management
```

**Output:** `outputs/run_20251203_094512_train_management/`

**requirements.md (excerpt):**
```markdown
## Functional Requirements

### TM-FR-001: Active Train List Maintenance
**Parent:** SYS-TM-001
**Type:** Functional

**Description:**
The Train Management subsystem shall maintain an Active Train list
containing all trains currently operating within the Dispatcher's Territory.

**Acceptance Criteria:**
- List updates within 5 seconds of train status change
- Includes Train ID, current Block, speed, and Movement Authority
- Supports minimum 50 concurrent Active Trains per Territory
- Persists across system restarts

**Rationale:**
Derived from SYS-TM-001 to specify the core data structure for real-time
train tracking required by CSX dispatch operations.

### TM-FR-002: Movement Authority Assignment
**Parent:** SYS-TM-002
**Type:** Functional

**Description:**
The Train Management subsystem shall assign Movement Authority to trains
based on Block availability and track conditions.

**Acceptance Criteria:**
- Movement Authority includes Block ID, entry/exit limits, speed restrictions
- Updates when Block status changes (clear → occupied)
- Prevents conflicting authorities for same Block
- Logs all authority assignments to audit trail

**Rationale:**
Implements movement authority management from SYS-TM-002 with CSX-specific
Block-based control logic.
```

**Quality Metrics:**
```
Overall Score: 0.92 (✅ PASSED)

Dimension Breakdown:
  Completeness:      0.95 ✓
  Clarity:           0.90 ✓
  Testability:       0.90 ✓
  Traceability:      0.95 ✓
  Domain Compliance: 0.90 ✓  [NEW - 5th dimension]

Domain Compliance Details:
  ✓ ID format: TM-FR-NNN (correct)
  ✓ Glossary terms: "Active Train", "Territory", "Block", "Movement Authority" (capitalized)
  ✓ Template structure: Description, Acceptance Criteria, Rationale (complete)
  ✓ Modal verbs: "shall" used consistently
```

**Key Benefits:**
- **Glossary Term Enforcement:** All domain-specific terms ("Active Train", "Block", "Territory") are automatically capitalized and used consistently
- **Template Compliance:** Requirements follow CSX Dispatch template structure (Description → Acceptance Criteria → Rationale)
- **ID Format Validation:** Naming convention (TM-FR-NNN) enforced by domain rules
- **5th Quality Dimension:** Domain Compliance score (0.90) ensures adherence to CSX standards

**Note:** Without domain context, same spec would score 0.85 (4 dimensions only) and might use inconsistent terminology like "track segment" instead of "Block".

---

## FAQ

### General Questions

**Q: How long does a typical decomposition take?**
A: 30-90 seconds for simple specs (5-10 requirements), 2-5 minutes for complex specs (30-50 requirements). Most time is spent in LLM inference.

**Q: How much does it cost per run?**
A: Typical run costs $0.10-$0.50 depending on specification size and iteration count. Costs scale with token usage.

**Q: Can I use this offline?**
A: No, requires internet connection for LLM API access.

**Q: What happens if I interrupt the workflow (Ctrl+C)?**
A: Workflow stops immediately. Use checkpoints to resume (infrastructure ready, CLI pending).

### Input/Output Questions

**Q: Can I process multiple subsystems at once?**
A: Not in MVP. Run separately for each subsystem. Batch processing planned for future release.

**Q: Can I customize output format?**
A: Not currently. Markdown format is standard. Export/conversion planned for future release.

**Q: What's the largest specification I can process?**
A: Tested up to 100 requirements. Larger specs may hit token limits or require chunking.

**Q: Can I version control the outputs?**
A: Yes, all outputs are text-based (Markdown/CSV). Recommended to commit to git for tracking.

### Quality & Validation Questions

**Q: Why did my run get 0 requirements (valid outcome)?**
A: The specification doesn't contain requirements for that subsystem. Check `allocation_report.md` for details. This is NOT an error.

**Q: How do I improve quality scores?**
A: Start with better input specifications. Use specific, testable language. Review refinement feedback if quality gate fails.

**Q: Can I disable quality validation?**
A: Not recommended. You can set `--quality-threshold 0.0` to effectively disable, but this defeats the purpose.

**Q: Why does human review keep getting triggered?**
A: Quality threshold too high, max iterations too low, or input spec quality is poor. Check quality_report.md for specific issues.

### Domain-Aware Questions **NEW (Phase 7)**

**Q: What is domain-aware decomposition?**
A: Optional feature that injects domain-specific conventions (glossary, templates, naming patterns) into the decomposition process. Enables 5th quality dimension (Domain Compliance) and ensures requirements follow organizational standards.

**Q: How do I list available domains?**
A: Use `python main.py --list-domains` to see all configured domains. Use `python main.py --list-subsystems <domain>` to see subsystems for a specific domain.

**Q: When should I use domain context vs. generic?**
A: Use domain context when:
- You have established organizational standards/glossary
- Requirements must follow specific templates or naming conventions
- You want to enforce terminology consistency
- You need the 5th quality dimension (Domain Compliance)

Use generic (default) for exploratory work or when no domain standards exist.

**Q: What's the difference between 4-dimension and 5-dimension scoring?**
A:
- **4 dimensions (generic):** Completeness, Clarity, Testability, Traceability (0.25 weight each)
- **5 dimensions (domain-aware):** Above + Domain Compliance (0.20 weight each by default)

Domain Compliance checks ID format, glossary term usage, template structure, and naming patterns.

**Q: Can I customize quality dimension weights?**
A: Yes (Phase 7.3). Set environment variables in `.env`:
```bash
QUALITY_WEIGHT_COMPLETENESS=0.30  # Prioritize completeness
QUALITY_WEIGHT_CLARITY=0.20
QUALITY_WEIGHT_TESTABILITY=0.25
QUALITY_WEIGHT_TRACEABILITY=0.25
# Weights must sum to 1.0
```

**Q: How do I create my own domain?**
A:
1. Create directory: `domains/<domain_name>/`
2. Add required files:
   - `domain_config.json` (domain metadata)
   - `conventions.md` (common conventions)
   - `glossary.md` (terminology)
   - `subsystems/<subsystem_id>/` subdirectories
3. Follow structure in `domains/csx_dispatch/` as reference
4. Register in `config/domain_config.py`

See `docs/phases/phase7/README.md` for detailed guide.

**Q: Does domain context affect backward compatibility?**
A: No. Generic (non-domain) decomposition works exactly as before. Domain features are opt-in via `--domain` flag.

**Q: What if domain loading fails?**
A: System automatically falls back to generic domain with a warning. Check error log for details. Verify domain files exist and are valid.

### Technical Questions

**Q: Which LLM providers are supported?**
A: OpenAI (GPT-4o, GPT-5 Nano), Anthropic (Claude 3.5 Sonnet), Google (Gemini 2.5 series). Need at least one API key.

**Q: Can I use local/open-source models?**
A: Not currently. LangChain-compatible models could be added with code modifications.

**Q: Where are checkpoints stored?**
A: `checkpoints/` directory in project root. SQLite database format.

**Q: How do I clear old outputs?**
A: Manually delete directories in `outputs/`. Garbage collection planned for future release.

**Q: Can I run this in CI/CD pipeline?**
A: Yes, use `--quiet` mode and check exit codes. `0` = success, `2` = warnings, `1` = error.

### Troubleshooting Questions

**Q: "No JSON array found in response" error?**
A: LLM returned invalid format. Usually transient - retry. Enable `--debug` to see raw response.

**Q: "Rate limit exceeded" error?**
A: Too many API requests. Automatic retry with exponential backoff. Wait and retry, or use different API key.

**Q: Workflow seems stuck - no progress for minutes?**
A: Large LLM inference can take time. Check terminal for progress messages. Use `--debug` to see detailed timing.

**Q: "Cannot generate documentation: no subsystem requirements found" error (old)?**
A: Fixed in Phase 3. Update to latest version. Now generates allocation report instead.

---

## Support & Contributing

### Getting Support

- **Documentation:** Review this guide and `docs/` directory
- **Examples:** Test with `examples/` directory files
- **Debug Mode:** Run with `--debug` for detailed logs
- **LangSmith:** Enable tracing for full execution visibility

### Reporting Issues

Include:
1. Command used
2. Input specification (if sharable)
3. Error message or unexpected behavior
4. Output of `--debug` mode
5. Python version and OS

### Contributing

Contributions welcome! See `CONTRIBUTING.md` for guidelines.

---

**Last Updated:** 2025-11-09
**Version:** 1.1.0 (Phase 4 Complete - MVP Production-Ready)
**Status:** Production Ready with Observability
