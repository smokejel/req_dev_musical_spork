# Requirements Development Agentic Workflow

> An experimental AI-powered requirements decomposition system using LangGraph to orchestrate multiple LLM agents for breaking down high-level system specifications into detailed, testable requirements.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.0.40+-green.svg)](https://github.com/langchain-ai/langgraph)
[![Phase 1 Complete](https://img.shields.io/badge/Phase%201-Complete-brightgreen.svg)](docs/phases/phase1/README.md)
[![Tests](https://img.shields.io/badge/tests-110%20passing-brightgreen.svg)](tests/)

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
- API keys for LLM providers (Anthropic, OpenAI - optional)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/req_dev_musical_spork.git
cd req_dev_musical_spork

# Install the package in development mode
pip install -e .

# Configure API keys (create .env file)
cp .env.example .env
# Edit .env and add your API keys
```

### Verify Installation

```bash
# Run unit tests to verify everything works
pytest tests/ -m "phase1 and unit" -v

# Expected output: 105 passed in ~6 seconds
```

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

- **110 total tests**
- **105 unit tests** - Fast, no external dependencies (5-6 seconds)
- **5 integration tests** - Real LLM API calls (~30-45 seconds)
- **100% passing** in Phase 1

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

- **Intelligent Error Handling**: 3-tier error taxonomy (TRANSIENT, CONTENT, FATAL)
- **LLM Fallback System**: Automatic retry with exponential backoff and model switching
- **Skills-Based Architecture**: Modular expertise in SKILL.md files (Phase 0 validated)
- **Quality Gates**: Automated scoring with 0.80 threshold and human review
- **Full Traceability**: Parent-child requirement relationships tracked throughout

---

## 🔧 Technology Stack

### Core Dependencies

- **LangGraph** (≥0.0.40) - Graph workflow orchestration
- **LangChain** (≥0.1.0) - LLM abstractions and chains
- **Pydantic** (≥2.5.0) - State schema validation
- **Pytest** (≥7.4.0) - Testing framework

### LLM Providers

- **Anthropic** - Claude 3.5 Sonnet, Claude Sonnet 4.5
- **OpenAI** - GPT-4o, GPT-4o-mini
- **Google** - Gemini 1.5 Pro (future phases)

### Multi-Model Strategy

| Node | Primary Model | Fallback | Temperature | Rationale |
|------|--------------|----------|-------------|-----------|
| Extract | GPT-4o-mini | GPT-4o | 0.0 | Cost optimization, structured extraction |
| Analyze | Claude 3.5 Sonnet | GPT-4o | 0.1 | Architectural reasoning |
| Decompose | GPT-4o | Claude 4.5 | 0.0 | Complex reasoning, consistency |
| Validate | Claude 4.5 | Claude 3.5 | 0.0 | Critical evaluation |

---

## 📊 Current Status

### Phase 1: Foundation ✅ **COMPLETE**

**Date:** October 30, 2025
**Duration:** 1 day (rapid implementation)

**Deliverables:**
- ✅ Complete project structure
- ✅ State schemas with Pydantic validation
- ✅ Base agent with intelligent error handling
- ✅ Extract node with RequirementsAnalystAgent
- ✅ Document parser (txt, docx, pdf)
- ✅ Skill loader with caching
- ✅ **110 comprehensive tests (100% passing)**
- ✅ Complete documentation

**Metrics:**
- 4,200+ lines of code
- 23 files created
- 110 tests (105 unit + 5 integration)
- 100% test success rate

### Phase 0: Skills Validation ✅ **COMPLETE**

**Results:**
- 34% improvement over baseline
- 100% output consistency
- Reliable instruction adherence
- GO decision for full implementation

### Next Up: Phase 2 (Core Decomposition)

- Analyze node (SystemArchitectAgent)
- Decompose node (RequirementsEngineerAgent)
- Traceability implementation
- Quality validation

---

## 🧩 Configuration

### Environment Variables

Create a `.env` file with your API keys:

```bash
# Required for integration tests and Phase 2+
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx

# Optional (for future phases)
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
GOOGLE_API_KEY=xxxxxxxxxxxxx

# LangSmith tracing (optional)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=xxxxxxxxxxxxx
LANGCHAIN_PROJECT=requirements-decomposition
```

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

- [Complete Documentation Index](docs/README.md)
- [Phase 1 Implementation Details](docs/phases/phase1/README.md)
- [Phase 0 Validation Results](docs/phases/phase0/results.md)
- [4.5-Week MVP Plan](docs/implementation/mvp_plan.md)
- [Project Context (CLAUDE.md)](CLAUDE.md) - Detailed context for AI assistants

### Key Documentation Files

- **CLAUDE.md** - Comprehensive project context, architecture, and development guidelines
- **docs/README.md** - Documentation navigation and organization
- **docs/phases/phase1/README.md** - Phase 1 implementation summary (110 tests, metrics, lessons learned)
- **docs/implementation/mvp_plan.md** - Full 4.5-week implementation plan with Phase 0 validation

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


**Phase 1 Complete ✅ | 110 Tests Passing ✅ | Ready for Phase 2 🚀**
