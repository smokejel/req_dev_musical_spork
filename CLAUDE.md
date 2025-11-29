# CLAUDE.md - Project Context for AI Assistants

## Project Overview

**Project:** Requirements Development Agentic Workflow
**Repository:** req_dev_musical_spork
**Status:** Phase 6 Complete - Production-Ready
**Architecture:** LangGraph-based multi-agent system
**Language:** Python 3.11

This is an AI-powered requirements decomposition system using LangGraph to orchestrate multiple LLM agents for breaking down high-level system specifications into detailed, testable requirements.

**Current Phase:** Phase 6.1 (Energy Consumption Tracking) ✅ COMPLETE
**Next Step:** Production Deployment or Optional Phase 6.2-6.4 Enhancements
**Timeline:** 4.5 weeks completed (Phase 0-6.1)

For complete phase history and achievements, see: `docs/phases/README.md`

## Architecture Essentials

### 4-Node LangGraph Workflow

1. **Extract Node** (RequirementsAnalystAgent)
   - Parses specification documents (.txt, .docx, .pdf)
   - Uses Gemini 2.5 Flash-Lite (1M context, handles 88K+ tokens)

2. **Analyze Node** (SystemArchitectAgent)
   - Understands system context and constraints
   - Plans decomposition strategy (BINDING contract)
   - Uses Claude Sonnet 3.5 (architectural reasoning)

3. **Decompose Node** (RequirementsEngineerAgent)
   - Transforms system → subsystem requirements
   - Maintains parent-child traceability
   - Uses GPT-5 Nano (no TPM limits, cost-efficient)

4. **Validate Node** (QualityAssuranceAgent)
   - Automated quality scoring (4 metrics: completeness, clarity, testability, traceability)
   - Quality gate with 0.80 threshold (configurable)
   - Iterative refinement loop (max 3 iterations)
   - Uses Gemini 2.5 Flash (best price-performance)

### State Schema

Complete schema in `src/state.py`. Key fields:
- **Input:** `spec_document_path`, `target_subsystem`, `review_before_decompose`
- **Processing:** `extracted_requirements`, `system_context`, `decomposition_strategy`, `decomposed_requirements`
- **Quality Control:** `quality_metrics`, `validation_passed`, `iteration_count`, `refinement_feedback`, `validation_issues`, `previous_attempt`
- **Human Review:** `human_feedback`, `requires_human_review`
- **Observability:** `total_cost`, `cost_breakdown`, `timing_breakdown`, `total_energy_wh`, `energy_breakdown`
- **Error Handling:** `errors`, `fallback_count`, `error_log`

### Skills-Based Architecture

**Philosophy:** Skills are modular expertise modules (SKILL.md files) that guide LLM behavior through detailed methodologies, not hardcoded prompts. Enables version control, easy updates, and separation of domain knowledge from code.

**Core Skills:**
- `skills/requirements-extraction/SKILL.md` - Parse specs, identify atomic requirements
- `skills/system-analysis/SKILL.md` - Architectural reasoning, decomposition planning
- `skills/requirements-decomposition/SKILL.md` - System→subsystem transformation
- `skills/requirements-quality-validation/SKILL.md` - Quality scoring and issue identification

**Validation:** Phase 0 validated 34% quality improvement over baseline with 100% output consistency.

## Key Design Decisions

### 1. Binding Strategy Execution ⚠️ CRITICAL
- Decomposition strategy from analyze node is **100% binding** (not advisory)
- Decompose node MUST follow strategy exactly
- Strategy violations are **bugs**, not quality issues
- Validate adherence programmatically
- No subjective overrides allowed

### 2. Iterative Refinement with Feedback ⚠️ CRITICAL
- Validation node generates **specific, actionable feedback**
- Decompose node receives feedback on subsequent iterations
- Previous attempts tracked for comparison
- Max iterations prevents infinite loops
- Human review as final arbiter
- **Without feedback, iteration cannot improve quality**

### 3. Zero Requirements as Success
- Empty decomposition is valid when allocation rules filter all requirements
- Quality score 1.0 (PASSED) for valid empty results
- Professional allocation report explains why no requirements allocated
- No unnecessary human review triggered

### 4. Multi-Model Strategy with Intelligent Fallback
- **Error Taxonomy:**
  - **Transient** (rate limits, timeouts) → Retry with exponential backoff
  - **Content** (parse failures, validation errors) → Switch to fallback model
  - **Fatal** (auth failures, missing resources) → Human intervention
- **Fallback Chains:** See `config/llm_config.py`
- Track fallback frequency for optimization

### 5. State Persistence to Disk
- SQLite checkpointing to disk (NOT memory: `:memory:`)
- Resume interrupted workflows via checkpoint ID
- Pattern: `SqliteSaver.from_conn_string(str(checkpoint_dir / "decomposition_state.db"))`

### 6. Observability from Day One
- Real-time cost tracking with budget management (warning: $1.00, max: $5.00)
- Quality trend monitoring across workflow runs
- Energy consumption tracking (Phase 6.1)
- LangSmith integration infrastructure (optional)
- Rich CLI output with timing, cost, and energy breakdowns

## Development Guidelines

### For AI Assistants Working on This Project

1. **State Schema is Sacred**
   - All state modifications must go through TypedDict
   - Include refinement feedback fields for iteration loop
   - Track fallback events and errors
   - Maintain backward compatibility

2. **Skills Are Separate**
   - Keep skill content in SKILL.md files (1000-2000 tokens each)
   - Don't hardcode prompts in agent code
   - Skills should be version-controlled with CHANGELOG
   - See `skills/README.md`

3. **Strategy is Binding**
   - Decomposition strategy from analyze node is 100% binding
   - Decompose node MUST follow strategy exactly
   - Strategy violations are bugs, not quality issues
   - Validate strategy adherence programmatically

4. **Refinement Requires Feedback**
   - Validation failures must generate specific feedback
   - Decompose node must consume feedback on retries
   - Track previous attempts for comparison
   - Without feedback, iteration won't improve quality

5. **Error Handling is Structured**
   - Use error taxonomy (Transient, Content, Fatal)
   - Implement intelligent fallback logic
   - Track fallback frequency for analysis
   - Don't use generic `except Exception` blocks

6. **Cost Awareness**
   - Use appropriate models per node (see LLM Model Assignment table)
   - Implement caching where possible
   - Test with mocks, not live LLM calls (see `tests/README.md`)
   - Track costs in development and production

7. **Observability Matters**
   - Add logging at key decision points
   - Use LangSmith tracing for full execution visibility (optional)
   - Include rich output for CLI feedback
   - Track quality metrics and fallback events

8. **Human-in-the-Loop**
   - Support pre-decomposition AND post-validation review
   - Use LangGraph interrupts properly
   - Provide clear prompts for human review
   - Support state inspection and resumption via checkpoint IDs

## Critical Implementation Patterns

### Refinement Feedback Loop (MUST IMPLEMENT)

```python
# In validate node:
if not validation_passed:
    feedback = generate_refinement_guidance(
        issues=metrics["issues"],
        requirements=state["subsystem_requirements"],
        strategy=state["decomposition_strategy"]
    )
    return {
        "refinement_feedback": feedback,  # Specific, actionable instructions
        "validation_issues": metrics["issues"]
    }

# In decompose node:
if state.get("refinement_feedback"):
    # This is a revision - use feedback
    subsystem_reqs = agent.decompose_with_refinement(
        requirements=state["extracted_requirements"],
        strategy=state["decomposition_strategy"],
        previous_attempt=state.get("subsystem_requirements"),
        feedback=state["refinement_feedback"]  # Tell agent what to fix
    )
```

### LLM Fallback Logic (MUST IMPLEMENT)

```python
class ErrorType(Enum):
    TRANSIENT = "transient"  # Retry same model with backoff
    CONTENT = "content"      # Switch to fallback model
    FATAL = "fatal"          # Human intervention

# Transient: RateLimitError, TimeoutError, APIError → Retry
# Content: ValidationError, JSONDecodeError, ParseError → Fallback
# Fatal: AuthError, MissingResourceError → Stop
```

### State Persistence Pattern (MUST IMPLEMENT CORRECTLY)

```python
# WRONG:
memory = SqliteSaver.from_conn_string(":memory:")

# CORRECT:
from pathlib import Path
checkpoint_dir = Path("checkpoints")
checkpoint_dir.mkdir(exist_ok=True)
memory = SqliteSaver.from_conn_string(
    str(checkpoint_dir / "decomposition_state.db")
)
```

### Strategy Adherence Validation (MUST IMPLEMENT)

```python
# After decomposition, validate strategy was followed:
adherence_check = validate_strategy_adherence(
    requirements=subsystem_reqs,
    strategy=strategy
)

if not adherence_check["passed"]:
    # This is a BUG, not a quality issue
    return {
        "errors": [f"Agent violated strategy: {adherence_check['violations']}"],
        "requires_human_review": True
    }
```

## Quick References

### Documentation

- **Phase History:** `docs/phases/README.md` - Complete development timeline
- **User Guide:** `docs/user_guide.md` - Installation, usage, configuration
- **API Reference:** `docs/api_documentation.md` - State schemas, node functions, agents
- **Testing:** `tests/README.md` - Testing strategy, running tests, fixtures
- **Implementation Plan:** `docs/implementation/mvp_plan.md` - 4.5-week roadmap
- **LLM Configuration:** `config/llm_config.py` - Model assignments, fallback chains, energy coefficients
- **Observability:** `docs/OBSERVABILITY.md` - Cost tracking, budget management, quality monitoring
- **Gemini CLI:** `docs/reference/gemini_cli.md` - Large codebase analysis guide
- **Project README:** `README.md` - Project overview, quick start, features

### LLM Model Assignment (Production)

| Node | Primary Model | Context Window | Rationale |
|------|---------------|----------------|-----------|
| **Extract** | gemini-2.5-flash-lite | 1M tokens | Ultra-fast, handles 88K+ token PDFs |
| **Analyze** | claude-sonnet-3-5 | 200K tokens | Architectural reasoning excellence |
| **Decompose** | gpt-5-nano | 32K+ tokens | No TPM limits, cost-efficient |
| **Validate** | gemini-2.5-flash | 1M tokens | Best price-performance for QA |

**Fallback chains and full model details:** `config/llm_config.py`

### Configuration

See `.env.example` for complete environment variable documentation.

**Key Settings:**
- `QUALITY_THRESHOLD=0.80` - Quality gate threshold
- `MAX_ITERATIONS=3` - Maximum refinement iterations
- `TEMPERATURE=0.0` - Deterministic outputs
- `COST_TRACKING_ENABLED=true` - Enable cost tracking
- `COST_BUDGET_MAX=5.00` - Maximum budget per run

### Git Workflow

**Branch:** `main` (or feature branches)
**Commit Guidelines:**
- Descriptive commit messages
- Reference phase in commits (e.g., "[Phase 6] Add energy tracking")
- Keep commits atomic and focused

## Resources

### External Documentation

- **LangGraph:** https://langchain-ai.github.io/langgraph/
- **LangChain:** https://python.langchain.com/
- **LangSmith:** https://smith.langchain.com/
- **Pydantic:** https://docs.pydantic.dev/

### For Questions About

- **Architecture:** `docs/implementation/mvp_plan.md` Section 2
- **Phases 1-6:** `docs/phases/README.md` or `docs/phases/phaseN/README.md`
- **State Schema:** `src/state.py` or `docs/api_documentation.md`
- **Skills:** `skills/README.md` or `docs/implementation/mvp_plan.md` Appendix A
- **Testing:** `tests/README.md` or `docs/phases/phase4/README.md`

---

**Last Updated:** November 15, 2025
**Status:** Production-Ready with Energy Tracking
**Version:** 1.0 (Optimized)
