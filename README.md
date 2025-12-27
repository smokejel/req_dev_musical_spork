# Requirements Development Agentic Workflow

> An experimental AI-powered requirements decomposition system using LangGraph to orchestrate multiple LLM agents for breaking down high-level system specifications into detailed, testable requirements.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.0.40+-green.svg)](https://github.com/langchain-ai/langgraph)
[![Phase 5 Complete](https://img.shields.io/badge/Phase%205-Complete-brightgreen.svg)](docs/phases/phase5/README.md)
[![Phase 6 Complete](https://img.shields.io/badge/Phase%206-Complete-brightgreen.svg)](docs/phases/phase6/README.md)
[![Tests](https://img.shields.io/badge/tests-7%2F7%20passing-brightgreen.svg)](tests/)
[![Large Documents](https://img.shields.io/badge/large%20docs-88K%2B%20tokens-blue.svg)](docs/phases/phase4/README.md)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](Dockerfile)

---

## 🎯 What Does This Do?

This system automates requirements engineering by:

1. **Extracting** high-level requirements from specification documents (.txt, .docx, .pdf)
2. **Analyzing** system context and constraints
3. **Decomposing** requirements into detailed, testable specifications
4. **Validating** quality with automated scoring and human-in-the-loop review
5. **Generating** traceability matrices and professional documentation

### Example

**Input:** System specification document
**Output:** Detailed requirements with parent-child traceability, quality metrics, and professional documentation

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- API keys for LLM providers (Anthropic, OpenAI, or Google)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/req_dev_musical_spork.git
cd req_dev_ARAD

# Install dependencies
pip install -r requirements.txt

# Configure API keys (create .env file)
cp .env.example .env
# Edit .env and add your API keys
```

### First Run

```bash
# Run decomposition for Authentication subsystem
python main.py examples/phase0_simple_spec.txt --subsystem "Authentication"

# Check output
ls outputs/run_*

# Expected: Timestamped directory with requirements, traceability, and quality report
```

### Visualize Workflow Structure

```bash
# Generate workflow graph diagram (Mermaid format)
python scripts/visualize_graph.py

# View the generated diagram
# - GitHub/GitLab: View docs/workflow_graph.md directly
# - Online: Copy Mermaid code to https://mermaid.live
# - Local: Use VS Code with Mermaid extension
```

See [`docs/workflow_graph.md`](docs/workflow_graph.md) for the complete workflow diagram with node descriptions and routing logic.

### Run in LangSmith Studio

**Interactive debugging and testing in LangSmith's visual IDE:**

```bash
# Install LangGraph CLI
pip install -U "langgraph-cli[inmem]"

# Start local Agent Server
langgraph dev

# Access Studio at the provided URL:
# https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
```

**Features in Studio:**
- 🔍 **Visual Graph Execution** - Watch nodes execute in real-time
- 🧪 **State Inspection** - View `DecompositionState` at each step
- ⏪ **Time Travel Debugging** - Rewind execution to any point
- 🎯 **Interactive Testing** - Run workflows without CLI
- 📊 **LangSmith Tracing** - See token usage and costs per LLM call (if enabled)
- 🔄 **Thread Management** - Create multiple parallel test runs

See [`docs/langsmith_studio_guide.md`](docs/langsmith_studio_guide.md) for detailed Studio usage instructions.

---

## 🐳 Docker Deployment

### Quick Start with Docker Compose (Recommended)

**Prerequisites:**
- Docker and Docker Compose installed
- API keys in `.env` file

**Build and Run:**
```bash
# Build the image
docker-compose build

# Run decomposition
docker-compose run req-decomp python main.py examples/phase0_simple_spec.txt --subsystem "Authentication"

# Check output
ls outputs/run_*
```

**Interactive Shell:**
```bash
docker-compose run req-decomp /bin/bash
```

### Docker Compose Usage Examples

**Basic Decomposition:**
```bash
docker-compose run req-decomp \
  python main.py examples/train_spec.txt --subsystem "Navigation"
```

**With Custom Quality Threshold:**
```bash
docker-compose run req-decomp \
  python main.py examples/spec.txt --subsystem "Power" --quality-threshold 0.90
```

**With Human Review:**
```bash
docker-compose run req-decomp \
  python main.py examples/spec.txt --subsystem "Control" --review-before-decompose
```

**Generate Cost & Quality Reports:**
```bash
docker-compose run req-decomp \
  python scripts/generate_reports.py --days 30
```

### Alternative: Direct Docker Commands

**Build Image:**
```bash
docker build -t req-decomp:latest .
```

**Run Decomposition:**
```bash
docker run --rm \
  --env-file .env \
  -v $(pwd)/examples:/app/examples:ro \
  -v $(pwd)/outputs:/app/outputs \
  -v $(pwd)/checkpoints:/app/checkpoints \
  -v $(pwd)/data:/app/data \
  req-decomp:latest \
  python main.py examples/phase0_simple_spec.txt --subsystem "Authentication"
```

**Interactive Mode:**
```bash
docker run --rm -it \
  --env-file .env \
  -v $(pwd)/examples:/app/examples:ro \
  -v $(pwd)/outputs:/app/outputs \
  -v $(pwd)/checkpoints:/app/checkpoints \
  -v $(pwd)/data:/app/data \
  req-decomp:latest \
  /bin/bash
```

### Docker Volume Mounts

| Volume | Purpose | Mount Type | docker-compose.yml |
|--------|---------|------------|-------------------|
| `examples/` | Input specifications | Read-only (`:ro`) | ✅ Auto-mounted |
| `outputs/` | Generated requirements, reports | Read-write | ✅ Auto-mounted |
| `checkpoints/` | Workflow state (SQLite) | Read-write | ✅ Auto-mounted |
| `data/` | Cost & quality tracking databases | Read-write | ✅ Auto-mounted |
| `scripts/` | Reporting scripts | Read-only (`:ro`) | ✅ Auto-mounted |

### Development Mode

**For live code editing without rebuilding:**

The included `docker-compose.override.yml` automatically mounts source code for development:

```bash
# Edit code locally, changes reflected immediately in container
docker-compose run req-decomp python main.py examples/spec.txt --subsystem "Auth"
```

**To run without development overrides:**
```bash
docker-compose -f docker-compose.yml run req-decomp
```

### Docker Image Details

**Size:** ~400MB (optimized with multi-stage build)
- Base: Python 3.11-slim
- Build stage: Dependencies compilation
- Runtime stage: Minimal production image

**System Dependencies:**
- poppler-utils (PDF parsing)

**Environment Variables:**
- Passed via `--env-file .env` (docker-compose handles this automatically)
- Must include at least one LLM API key (see `.env.docker.example`)

**Security:**
- Examples and scripts mounted read-only for safety
- Runtime data (outputs, checkpoints, data) isolated in volumes
- `.env` file excluded from image (loaded at runtime)
- NEVER commit `.env` to version control

**Performance:**
- Same as local Python deployment
- Multi-stage build reduces layer size
- Volume I/O minimal overhead
- Network access required for LLM APIs

**LangSmith Integration:**
- Cost tracking databases persist in `data/` volume
- Enable with `LANGCHAIN_TRACING_V2=true` in `.env`
- Precise token counts and costs tracked automatically

---

## 🧪 Testing

### Run All Unit Tests (Fast, No API Costs)

```bash
# All Phase 1 unit tests
pytest tests/ -m "phase1 and unit" -v

# Specific test files
pytest tests/test_base_agent.py -v
pytest tests/test_requirements_analyst.py -v
pytest tests/test_extract_node.py -v
```

### Run Integration Tests (Requires API Keys)

```bash
# Real API calls (~$0.08 cost)
pytest tests/ -m "phase1 and integration" -v
```

### Test Coverage

- **290 total tests** (Phase 0-5 complete)
- **Unit tests:** Fast, mocked LLM responses
- **Integration tests:** Real LLM API calls (requires API keys)
- **End-to-end tests:** Full workflow testing
- **Test markers:** `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.phase{0-5}`

---

## 📁 Project Structure

```
req_dev_musical_spork/
├── README.md                          # This file
├── CLAUDE.md                          # Detailed project context for AI assistants
├── setup.py                           # Package installation configuration
├── requirements.txt                   # Python dependencies
├── .env.example                       # Example environment configuration
├── pytest.ini                         # Test configuration
│
├── src/                               # Source code
│   ├── state.py                       # State schema definitions (Pydantic models)
│   ├── agents/                        # Agent implementations
│   │   ├── base_agent.py              # Abstract base agent with error handling
│   │   └── requirements_analyst.py    # Extract node agent
│   ├── nodes/                         # LangGraph node functions
│   │   └── extract_node.py            # Document parsing & extraction
│   └── utils/                         # Utility modules
│       ├── document_parser.py         # Parse .txt, .docx, .pdf files
│       └── skill_loader.py            # Load and cache SKILL.md files
│
├── config/                            # Configuration
│   └── llm_config.py                  # LLM model definitions and assignments
│
├── skills/                            # Claude Skills (methodology guides)
│   └── requirements-extraction/       # Phase 0 validated extraction skill
│       ├── SKILL.md                   # Main methodology document
│       └── examples/                  # Good vs. bad examples
│
├── tests/                             # Test suite (110 tests)
│   ├── conftest.py                    # Shared pytest fixtures
│   ├── fixtures/                      # Mock data and responses
│   ├── test_base_agent.py             # 30 tests - Error handling & fallback
│   ├── test_requirements_analyst.py   # 20 tests - JSON parsing & validation
│   ├── test_extract_node.py           # 18 tests - Node workflow
│   ├── test_extract_integration.py    # 6 tests - Real API calls
│   ├── test_state.py                  # 17 tests - State schema validation
│   └── test_utils.py                  # 15 tests - Document parsing & skills
│
├── examples/                          # Test corpus
│   ├── phase0_simple_spec.txt         # 5 clear requirements
│   ├── phase0_medium_spec.txt         # 15 requirements with ambiguity
│   └── phase0_complex_spec.txt        # 30+ requirements, poor formatting
│
└── docs/                              # Documentation
    ├── README.md                      # Documentation index
    ├── implementation/                # Implementation plans
    │   └── mvp_plan.md                # 4.5-week MVP plan
    ├── phases/                        # Phase-specific documentation
    │   ├── phase0/                    # Skills validation results
    │   └── phase1/                    # Foundation implementation (COMPLETE ✅)
    └── reference/                     # Reference documentation
```

---

## 🏗️ Architecture

### LangGraph Workflow (4 Nodes)

```
┌─────────────┐       ┌─────────────┐       ┌──────────────┐       ┌──────────────┐
│   Extract   │──────▶│   Analyze   │──────▶│  Decompose   │──────▶│   Validate   │
│    Node     │       │    Node     │       │     Node     │       │     Node     │
└─────────────┘       └─────────────┘       └──────────────┘       └──────────────┘
      │                      │                       │                      │
      ▼                      ▼                       ▼                      ▼
Requirements          System Context        Detailed Reqs         Quality Gate
 Analyst Agent        Architect Agent       Engineer Agent           QA Agent
```

### Key Features

- **Large Document Support**: Processes 88K+ token PDFs (tested: 396 requirements extracted)
- **Multi-Model Integration**: Gemini 2.5 (1M context), GPT-5 Nano, Claude Sonnet working together
- **Performance Monitoring**: Real-time timing tracking per workflow node with bottleneck identification
- **Cost Tracking**: Heuristic-based cost estimation (±30% accuracy) displayed per-node and total
- **Energy Tracking** (Phase 6.1 ✅): Token-based energy consumption estimates (Wh) with contextual comparisons (TV minutes, electric car meters)
- **Intelligent Error Handling**: 3-tier error taxonomy (TRANSIENT, CONTENT, FATAL)
- **LLM Fallback System**: Automatic retry with exponential backoff and model switching
- **Skills-Based Architecture**: Modular expertise in SKILL.md files (Phase 0 validated)
- **Quality Gates**: Automated scoring with configurable thresholds and iterative refinement
- **Full Traceability**: Parent-child requirement relationships tracked throughout
- **Human-in-the-Loop**: Review integration at quality gates
- **Beautiful CLI Output**: Rich console tables showing progress, timing, costs, quality metrics, and energy consumption

---

## 🔧 Technology Stack

### Core Dependencies

- **LangGraph** (≥0.0.40) - Graph workflow orchestration
- **LangChain** (≥0.1.0) - LLM abstractions and chains
- **Pydantic** (≥2.5.0) - State schema validation
- **Pytest** (≥7.4.0) - Testing framework

### LLM Providers

- **Google Gemini** - 2.5 Flash-Lite, 2.5 Flash, 2.5 Pro (1M context window)
- **OpenAI** - GPT-5 Nano, GPT-4o, GPT-4o-mini
- **Anthropic** - Claude Sonnet 3.5, Claude Sonnet 4.5

### Multi-Model Strategy (Production)

| Node | Primary Model | Context | Fallback | Rationale |
|------|--------------|---------|----------|-----------|
| Extract | **Gemini 2.5 Flash-Lite** | 1M | Gemini Flash → GPT-4o | Handles 88K+ token PDFs |
| Analyze | **Claude Sonnet 3.5** | 200K | GPT-4o → Claude 4.5 | Architectural reasoning |
| Decompose | **GPT-5 Nano** | 32K+ | GPT-4o → Claude 4.5 | No TPM limits, fast |
| Validate | **Gemini 2.5 Flash** | 1M | Claude 4.5 → GPT-4o | Best price-performance |

**Note:** Free tier Gemini quota: 250K tokens/min. Upgrade to paid tier for large documents.

---

## 📊 Current Status

### Phase 6: Energy Consumption Tracking 📋 **PLANNING**

**Date:** November 2025
**Status:** Documentation complete, implementation pending
**Estimated Effort:** 3-4 hours

**Objectives:**
- Add token-based energy consumption estimates (Wh)
- Display energy in Performance & Cost Breakdown table
- Provide contextual comparisons (TV usage, car distance)
- Research-based energy coefficients for all 8 models

**Deliverables:**
- 📋 Complete planning documentation in `docs/phases/phase6/`
  - README.md: Overview and scope
  - implementation_plan.md: Detailed technical steps
  - energy_coefficients_research.md: Research sources and methodology
- ⏳ Code implementation: Pending
- 🎯 Testing strategy: Defined

**Research Findings:**
- GPT-4o: 0.3 Wh per 500-token query (Epoch AI, Feb 2025)
- Gemini 2.5 Flash: 0.24 Wh median text prompt (Google, Aug 2025)
- Token-based estimation accuracy: ±30% (acceptable for trend analysis)

**Future Enhancements (Optional):**
- Phase 6.2: CO2 emissions conversion
- Phase 6.3: Historical energy trend tracking
- Phase 6.4: Advanced adjustments (context length scaling)

[See Phase 6 Documentation](docs/phases/phase6/README.md)

### Phase 5: Production Hardening & Enhanced Observability ✅ **COMPLETE**

**Date:** November 12, 2025
**Duration:** 1 day

**Deliverables:**
- ✅ Real-time cost tracking with SQLite-based history
- ✅ Budget management ($1.00 warning, $5.00 max)
- ✅ Quality metrics tracking across runs
- ✅ Cost and quality trend reporting tools
- ✅ Automated report generation scripts
- ✅ LangSmith integration infrastructure (ready for activation)

**Key Features:**
- Historical data analysis with trend reports
- Per-node cost breakdown with model identification
- Budget warnings and execution limits
- Quality trend monitoring (4-dimensional scores)

[See Phase 5 Documentation](docs/phases/phase5/README.md)

### Phase 4: Testing & Observability ✅ **COMPLETE**

**Date:** November 6-9, 2025

**Key Achievements:**
- ✅ 88K+ token PDF processing (396 requirements)
- ✅ 7/7 E2E tests passing (100% pass rate)
- ✅ Gemini 2.5 & GPT-5 Nano integration
- ✅ Performance & cost breakdown display
- ✅ Docker deployment ready

[See Phase 4 Documentation](docs/phases/phase4/README.md)

### Phase 3: Graph Assembly & UX ✅ **COMPLETE**

**Date:** November 2, 2025
**Duration:** Week 3 of MVP

**Deliverables:**
- ✅ Complete LangGraph workflow assembly
- ✅ Real-time progress tracking with timing
- ✅ Timestamped output directory organization
- ✅ Zero requirements handling (valid empty results)
- ✅ Human-in-the-loop review integration
- ✅ State persistence with SQLite checkpointing
- ✅ Professional UX with Rich terminal output

**Key Features:**
- Interactive CLI with progress feedback
- Quality refinement loop (validate → decompose)
- Pre-decomposition review option
- Allocation reports for zero requirements
- Resume capability infrastructure

[See Phase 3 Documentation](docs/phases/phase3/README.md)

### Phase 2: Core Decomposition ✅ **COMPLETE**

**Deliverables:**
- ✅ Analyze node (SystemArchitectAgent)
- ✅ Decompose node (RequirementsEngineerAgent)
- ✅ Validate node (QualityAssuranceAgent)
- ✅ Traceability implementation
- ✅ Quality validation with 4 metrics
- ✅ Refinement feedback loop

### Phase 1: Foundation ✅ **COMPLETE**

**Deliverables:**
- ✅ Complete project structure
- ✅ State schemas with Pydantic validation
- ✅ Base agent with intelligent error handling
- ✅ Extract node with RequirementsAnalystAgent
- ✅ Document parser (txt, docx, pdf)
- ✅ Skill loader with caching
- ✅ 110 comprehensive tests (100% passing)

[See Phase 1 Documentation](docs/phases/phase1/README.md)

### Phase 0: Skills Validation ✅ **COMPLETE**

**Results:**
- 34% improvement over baseline
- 100% output consistency
- Reliable instruction adherence
- GO decision for full implementation

[See Phase 0 Results](docs/phases/phase0/results.md)

### Phase 4: Testing & Observability ✅ **COMPLETE**

**Date:** November 6-9, 2025
**Duration:** Week 4 of MVP

**Sub-Phases:**

**Phase 4.1: Large Document Support**
- ✅ Gemini 2.5 series integration (Flash-Lite, Flash, Pro)
- ✅ GPT-5 Nano for decomposition (no TPM constraints)
- ✅ 88K+ token PDF processing validated (396 requirements)
- ✅ Rate limit handling for OpenAI

**Phase 4.2: Observability & Performance Monitoring**
- ✅ Timing tracking per workflow node
- ✅ Heuristic-based cost estimation (±30% accuracy)
- ✅ Performance & cost breakdown display
- ✅ LangSmith integration infrastructure
- ✅ Rich console output with detailed metrics

**Phase 4.3: Bug Fixes & Test Updates**
- ✅ Fixed iteration_count tracking (validate node)
- ✅ Increased Test 2 timeout (350s → 600s for large docs)
- ✅ Test 5 accepts human review as valid outcome
- ✅ All test reliability issues resolved

**Phase 4.4: End-to-End Testing**
- ✅ 7/7 E2E tests passing (100% pass rate)
- ✅ Refinement loop validated (5 iterations observed)
- ✅ Quality scores: 0.85-0.99 across tests
- ✅ Zero allocation handling verified

**Phase 4.5: Documentation & Deployment**
- ✅ Docker containerization complete
- ✅ User guide updated with observability section
- ✅ MVP handoff documentation created
- ✅ All documentation complete

**Key Achievements:**
- Real-time performance monitoring with per-node timing
- Cost tracking displays estimated spend ($0.001-$0.050 per run)
- Beautiful Rich console tables showing bottlenecks
- Docker deployment ready
- 100% test pass rate
- Production-ready for real-world usage

[See Phase 4 Documentation](docs/phases/phase4/README.md)

---

## 🧩 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure your API keys:

```bash
cp .env.example .env
# Edit .env with your API keys
```

**Required:** At least one LLM provider API key (Anthropic, OpenAI, or Google)
**Recommended:** LangSmith API key for precise cost tracking (Phase 5)

See `.env.example` for complete documentation of all environment variables.

### Application Settings

Configure in `config/llm_config.py`:

```python
DEFAULT_QUALITY_THRESHOLD = 0.80  # Quality gate threshold
DEFAULT_MAX_ITERATIONS = 3        # Max refinement attempts
RETRY_MAX_ATTEMPTS = 3            # Transient error retries
RETRY_BACKOFF_FACTOR = 2.0        # Exponential backoff multiplier
```

---

## 📖 Documentation

### Quick Links

- **[User Guide](docs/user_guide.md)** - Complete guide to using the system
- [Complete Documentation Index](docs/README.md)
- [Phase 3 Implementation](docs/phases/phase3/README.md) - Latest (graph assembly & UX)
- [Phase 1 Implementation](docs/phases/phase1/README.md) - Foundation
- [Phase 0 Validation Results](docs/phases/phase0/results.md)
- [4.5-Week MVP Plan](docs/implementation/mvp_plan.md)
- [Project Context (CLAUDE.md)](CLAUDE.md) - Detailed context for AI assistants

### Key Documentation Files

- **docs/user_guide.md** - Comprehensive user guide with examples and troubleshooting
- **CLAUDE.md** - Project context, architecture, and development guidelines
- **docs/phases/phase3/README.md** - Phase 3 summary (graph, UX, zero requirements handling)
- **docs/phases/phase1/README.md** - Phase 1 summary (foundation, 110 tests)
- **docs/implementation/mvp_plan.md** - Full 4.5-week implementation plan

---

## 🤝 Contributing

This is currently an experimental research project. Contributions, suggestions, and feedback are welcome!

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Install in development mode: `pip install -e .`
4. Make your changes
5. Run tests: `pytest tests/ -m unit -v`
6. Submit a pull request

### Code Standards

- Python 3.11+ with type hints
- Pydantic models for all state schemas
- Docstrings for all functions
- Unit tests for new functionality
- Follow existing code style

---

## 🔬 Testing Philosophy

### Unit Tests (105 tests)

- **Fast**: 5-6 seconds for full suite
- **Free**: No API costs (fully mocked)
- **Comprehensive**: All components tested
- **Run Often**: Before every commit

### Integration Tests (5 tests)

- **Real**: Actual LLM API calls
- **Validation**: Phase 0 compatibility verified
- **Cost**: ~$0.08 per full run
- **Run Selectively**: Before deployments

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'src'"

**Solution:** Install the package in development mode:
```bash
pip install -e .
```

### Integration Tests Failing

**Solution:** Ensure API key is configured:
```bash
# Check if key is set
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('API Key:', 'SET' if os.getenv('ANTHROPIC_API_KEY') else 'MISSING')"

# Add to .env file
echo "ANTHROPIC_API_KEY=sk-ant-xxxxx" >> .env
```

### Tests Taking Too Long

**Solution:** Run only unit tests (skip integration tests):
```bash
pytest tests/ -m unit -v
```

---


**Phase 4 Complete ✅ | MVP Production-Ready ✅ | Observability & Performance Monitoring ✅ | Docker Deployment ✅ | 7/7 E2E Tests Passing (100%) 🚀**
