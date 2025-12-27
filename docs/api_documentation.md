# API Documentation

**Version:** 1.3.0 (Phase 7 Complete - Domain-Aware Requirements)
**Last Updated:** 2025-12-03

## Table of Contents

1. [Overview](#overview)
2. [Graph API](#graph-api)
3. [Node Functions](#node-functions)
4. [State Schema](#state-schema)
5. [Agent API](#agent-api)
6. [Utility Functions](#utility-functions)
7. [Phase 5: Observability & Tracking](#phase-5-observability--tracking)
8. [Configuration](#configuration)
9. [Error Handling](#error-handling)

---

## Overview

The Requirements Decomposition System is built as a modular, extensible architecture using LangGraph for workflow orchestration. This document provides complete API reference for developers extending or modifying the system.

### Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    LangGraph Workflow                    │
│  (src/graph.py - creates graph with 6 nodes)            │
└──────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────┐
│                   Node Functions                         │
│  (src/nodes/*.py - workflow execution units)            │
└──────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────┐
│                  Agent Classes                           │
│  (src/agents/*.py - LLM-powered logic)                  │
└──────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────┐
│              State Schema (TypedDict)                    │
│  (src/state.py - data flow between nodes)               │
└──────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────┐
│                Utility Functions                         │
│  (src/utils/*.py - document parsing, skill loading)     │
└──────────────────────────────────────────────────────────┘
```

### Key Design Principles

1. **Immutable State Flow**: Nodes receive state, return updated state (functional)
2. **Agent Separation**: Agents contain LLM logic, nodes orchestrate execution
3. **Skill-Based Knowledge**: Domain expertise in SKILL.md files, not code
4. **Error Taxonomy**: Intelligent handling (TRANSIENT, CONTENT, FATAL)
5. **Type Safety**: Pydantic models and TypedDict for validation

---

## Graph API

Module: `src/graph.py`

### create_decomposition_graph()

Creates and compiles the complete LangGraph workflow.

```python
def create_decomposition_graph() -> StateGraph:
    """
    Create the complete LangGraph workflow for requirements decomposition.

    Returns:
        Compiled StateGraph with checkpointing enabled

    Graph Structure:
        START → extract → analyze → [opt: human_review] → decompose
             ↓
             validate → [pass → document → END]
                      ↓
                      [revise → decompose (loop)]
                      ↓
                      [human_review → approved/revise]
    """
```

**Example Usage:**

```python
from src.graph import create_decomposition_graph
from src.state import create_initial_state

# Create graph
graph = create_decomposition_graph()

# Create initial state
initial_state = create_initial_state(
    spec_document_path="examples/spec.txt",
    target_subsystem="Navigation"
)

# Execute workflow
final_state = graph.invoke(initial_state)
```

**Graph Features:**

- **Nodes**: 6 total (extract, analyze, decompose, validate, human_review, document)
- **Conditional Routing**: Quality gate, human review, iteration limits
- **Checkpointing**: SQLite-based state persistence
- **Progress Tracking**: Real-time feedback via Rich console

---

### generate_checkpoint_id()

Generates unique checkpoint ID for state persistence.

```python
def generate_checkpoint_id(state: DecompositionState) -> str:
    """
    Generate a unique checkpoint ID for state persistence.

    Format: {timestamp}_{subsystem_slug}
    Example: 20251102_143022_navigation

    Args:
        state: Current decomposition state

    Returns:
        Unique checkpoint ID string (alphanumeric + underscores only)
    """
```

**Example:**

```python
checkpoint_id = generate_checkpoint_id(initial_state)
# Result: "20251102_143022_navigation_subsystem"

# Use with graph execution
config = {"configurable": {"thread_id": checkpoint_id}}
final_state = graph.invoke(initial_state, config=config)
```

---

### Routing Functions

#### route_after_validation()

Routes based on validation results.

```python
def route_after_validation(
    state: DecompositionState
) -> Literal["pass", "revise", "human_review"]:
    """
    Route based on validation results.

    Routing Logic:
        1. If errors exist → human_review
        2. If iteration limit reached → human_review
        3. If validation passed → pass (to documentation)
        4. If human review requested → human_review
        5. Otherwise → revise (back to decompose)

    Args:
        state: Current decomposition state

    Returns:
        Routing decision: "pass", "revise", or "human_review"
    """
```

#### route_after_human_review()

Routes based on human decision.

```python
def route_after_human_review(
    state: DecompositionState
) -> Literal["approved", "revise"]:
    """
    Route based on human decision after review.

    Args:
        state: Current decomposition state

    Returns:
        "approved" if human approved, "revise" if changes requested
    """
```

#### route_after_analyze()

Routes after analysis for optional pre-decomposition review.

```python
def route_after_analyze(
    state: DecompositionState
) -> Literal["decompose", "human_review"]:
    """
    Route after analysis - optionally allow human review before decomposition.

    Args:
        state: Current decomposition state

    Returns:
        "human_review" if review_before_decompose is True, else "decompose"
    """
```

---

### get_graph_visualization()

Returns ASCII art visualization of workflow graph.

```python
def get_graph_visualization() -> str:
    """
    Generate a text-based visualization of the graph structure.

    Returns:
        ASCII art representation of the workflow graph
    """
```

**Example:**

```python
print(get_graph_visualization())
```

---

## Node Functions

Module: `src/nodes/`

All node functions follow the same signature pattern:

```python
def node_function(state: DecompositionState) -> DecompositionState:
    """
    Execute node logic and return updated state.

    Args:
        state: Current state (read-only)

    Returns:
        Updated state with new fields populated
    """
```

### extract_node()

Module: `src/nodes/extract_node.py`

Extracts requirements from specification document.

```python
def extract_node(state: DecompositionState) -> DecompositionState:
    """
    Extract requirements from specification document.

    Uses:
        - RequirementsAnalystAgent (Gemini 2.5 Flash-Lite)
        - requirements-extraction skill
        - Document parser (txt, docx, pdf)
        - 1M context window for large documents

    Updates State:
        - extracted_requirements: List[Dict] (serialized Requirement objects)
        - errors: List[str] (if parsing fails)
        - error_log: List[Dict] (detailed error tracking)

    Returns:
        State with extracted_requirements populated
    """
```

**Example:**

```python
from src.nodes.extract_node import extract_node
from src.state import create_initial_state

state = create_initial_state(
    spec_document_path="examples/spec.txt",
    target_subsystem="Navigation"
)

result = extract_node(state)
print(f"Extracted {len(result['extracted_requirements'])} requirements")
```

---

### analyze_node()

Module: `src/nodes/analyze_node.py`

Analyzes system context and creates decomposition strategy.

```python
def analyze_node(state: DecompositionState) -> DecompositionState:
    """
    Analyze system context and create binding decomposition strategy.

    Uses:
        - SystemArchitectAgent (Claude 3.5 Sonnet)
        - system-analysis skill
        - Extracted requirements from state

    Updates State:
        - system_context: Dict (serialized SystemContext)
        - decomposition_strategy: Dict (serialized DecompositionStrategy)
        - errors: List[str] (if analysis fails)

    Returns:
        State with system_context and decomposition_strategy populated
    """
```

**Strategy Fields:**

- `allocation_rules`: Rules for subsystem allocation
- `traceability_rules`: Parent-child relationship rules
- `decomposition_depth`: Max levels (1-3)
- `naming_convention`: ID format (e.g., "NAV-{TYPE}-{NNN}")
- `acceptance_criteria_required`: Boolean flag

---

### decompose_node()

Module: `src/nodes/decompose_node.py`

Decomposes requirements following binding strategy.

```python
def decompose_node(state: DecompositionState) -> DecompositionState:
    """
    Decompose system requirements into detailed subsystem requirements.

    Uses:
        - RequirementsEngineerAgent (GPT-4o)
        - requirements-decomposition skill
        - Decomposition strategy (100% binding)

    Updates State:
        - decomposed_requirements: List[Dict] (serialized DetailedRequirement)
        - iteration_count: Incremented on each pass
        - previous_attempt: Stores previous decomposition for comparison
        - errors: List[str] (if decomposition fails)

    Returns:
        State with decomposed_requirements populated

    Note:
        Empty list is valid outcome (no requirements allocated to subsystem)
    """
```

**Refinement Loop:**

On subsequent iterations (iteration_count > 0), uses refinement feedback:

```python
if state.get("refinement_feedback"):
    # Use feedback to improve decomposition
    decomposed_requirements = agent.decompose_with_refinement(
        requirements=state["extracted_requirements"],
        strategy=state["decomposition_strategy"],
        previous_attempt=state.get("decomposed_requirements"),
        feedback=state["refinement_feedback"]
    )
```

---

### validate_node()

Module: `src/nodes/validate_node.py`

Validates quality of decomposed requirements.

```python
def validate_node(state: DecompositionState) -> DecompositionState:
    """
    Validate quality of decomposed requirements.

    Uses:
        - QualityAssuranceAgent (Gemini 1.5 Pro)
        - requirements-quality-validation skill
        - Quality threshold from state (default 0.80)

    Updates State:
        - quality_metrics: Dict (serialized QualityMetrics)
        - validation_passed: Boolean
        - validation_issues: List[Dict] (serialized QualityIssue)
        - refinement_feedback: Optional[str] (for next iteration)
        - requires_human_review: Boolean (if threshold not met)

    Returns:
        State with quality assessment

    Special Cases:
        - Zero requirements → validation_passed=True, overall_score=1.0
    """
```

**Quality Dimensions (0.0-1.0):**

- `completeness`: All aspects covered
- `clarity`: Unambiguous language
- `testability`: Clear acceptance criteria
- `traceability`: Proper parent-child links
- `overall_score`: Average of all dimensions

---

### human_review_node()

Module: `src/nodes/human_review_node.py`

Interactive human review with approve/revise options.

```python
def human_review_node(state: DecompositionState) -> DecompositionState:
    """
    Present interactive human review interface.

    Uses:
        - Rich library for formatted display
        - Input prompts for user decisions
        - Quality metrics display

    Updates State:
        - human_feedback: Optional[str] (user feedback)
        - requires_human_review: False (cleared after review)

    Returns:
        State with human feedback

    Options:
        - [A] Approve: Continue to documentation
        - [R] Revise: Provide feedback and loop to decompose
        - [Q] Quit: Abandon workflow
    """
```

---

### document_node()

Module: `src/nodes/document_node.py`

Generates final documentation and outputs.

```python
def document_node(state: DecompositionState) -> DecompositionState:
    """
    Generate final documentation and output files.

    Creates:
        - Timestamped output directory (outputs/run_{timestamp}_{subsystem}/)
        - requirements.md (detailed requirements)
        - traceability.csv (parent-child mapping)
        - quality_report.md (quality metrics)
        - README.txt (run metadata)

    Updates State:
        - final_document_path: str (path to requirements.md)
        - traceability_matrix: Dict (serialized TraceabilityMatrix)

    Returns:
        State with final_document_path populated

    Special Cases:
        - Zero requirements → Generates allocation_report.md instead
    """
```

**Output Directory Structure:**

```
outputs/
└── run_20251102_143022_navigation/
    ├── requirements.md
    ├── traceability.csv
    ├── quality_report.md
    └── README.txt
```

---

## State Schema

Module: `src/state.py`

### DecompositionState (TypedDict)

Main state object for LangGraph workflow.

```python
class DecompositionState(TypedDict, total=False):
    """
    Main state object for the LangGraph workflow.

    All fields are optional (total=False) to allow incremental
    state building through the graph.
    """

    # Input
    spec_document_path: str
    target_subsystem: str
    review_before_decompose: bool
    quality_threshold: float
    domain_name: str                              # Phase 7: Domain context (default: "generic")
    subsystem_id: Optional[str]                   # Phase 7: Subsystem identifier within domain

    # Processing
    extracted_requirements: List[Dict[str, Any]]
    system_context: Dict[str, Any]
    decomposition_strategy: Dict[str, Any]
    decomposed_requirements: List[Dict[str, Any]]
    domain_context: Optional[Dict[str, Any]]      # Phase 7: Loaded domain context (conventions, glossary, examples)

    # Quality Control
    quality_metrics: Dict[str, Any]
    validation_passed: bool
    iteration_count: int
    max_iterations: int
    refinement_feedback: Optional[str]
    validation_issues: List[Dict[str, Any]]
    previous_attempt: Optional[List[Dict[str, Any]]]

    # Human Review
    human_feedback: Optional[str]
    requires_human_review: bool

    # Output
    final_document_path: Optional[str]
    traceability_matrix: Optional[Dict[str, Any]]

    # Error Handling
    errors: List[str]
    fallback_count: int
    error_log: List[Dict[str, Any]]
```

**Field Details:**

| Field | Type | Set By | Description |
|-------|------|--------|-------------|
| `spec_document_path` | str | User input | Path to spec document |
| `target_subsystem` | str | User input | Subsystem name |
| `review_before_decompose` | bool | User input | Optional pre-decomposition review flag |
| `quality_threshold` | float | User input | Quality gate threshold (default 0.80) |
| `domain_name` | str | User input | Domain name (default: "generic") **Phase 7** |
| `subsystem_id` | Optional[str] | User input | Subsystem identifier within domain **Phase 7** |
| `extracted_requirements` | List[Dict] | extract_node | Extracted requirements |
| `system_context` | Dict | analyze_node | System analysis |
| `decomposition_strategy` | Dict | analyze_node | Binding strategy (100% enforced) |
| `decomposed_requirements` | List[Dict] | decompose_node | Detailed requirements |
| `domain_context` | Optional[Dict] | extract_node | Loaded domain context (conventions, glossary, examples) **Phase 7** |
| `quality_metrics` | Dict | validate_node | Quality scores |
| `validation_passed` | bool | validate_node | Quality gate result |
| `iteration_count` | int | decompose_node | Current iteration (starts at 0) |
| `max_iterations` | int | User input | Max refinement attempts (default 3) |
| `refinement_feedback` | Optional[str] | validate_node | Specific improvement guidance |
| `validation_issues` | List[Dict] | validate_node | Detailed quality issues |
| `previous_attempt` | Optional[List[Dict]] | decompose_node | Previous decomposition for comparison |
| `human_feedback` | Optional[str] | human_review_node | User feedback from review |
| `requires_human_review` | bool | validate_node | Human review needed flag |
| `final_document_path` | Optional[str] | document_node | Path to generated document |
| `traceability_matrix` | Optional[Dict] | document_node | Traceability data |
| `errors` | List[str] | Any node | Simple error messages |
| `fallback_count` | int | Any node | LLM fallback counter |
| `error_log` | List[Dict] | Any node | Detailed error tracking |

---

### Pydantic Models

#### Requirement

Extracted requirement from source document.

```python
class Requirement(BaseModel):
    """A single extracted requirement."""

    id: str                          # Format: PREFIX-TYPE-NNN
    text: str                        # Requirement statement
    type: RequirementType            # FUNC, PERF, CONS, INTF
    source_section: Optional[str]    # Section in source document

    # Validation: ID must be PREFIX-TYPE-NNN with valid type
```

**Example:**

```python
from src.state import Requirement, RequirementType

req = Requirement(
    id="EXTRACT-FUNC-001",
    text="The system shall support user authentication",
    type=RequirementType.FUNCTIONAL,
    source_section="2.1 Security Requirements"
)
```

---

#### DetailedRequirement

Decomposed requirement with traceability.

```python
class DetailedRequirement(BaseModel):
    """A detailed, decomposed requirement with traceability."""

    id: str                             # Unique ID (follows naming convention)
    text: str                           # Requirement statement
    type: RequirementType               # FUNC, PERF, CONS, INTF
    parent_id: Optional[str]            # Parent requirement (traceability)
    subsystem: str                      # Allocated subsystem
    acceptance_criteria: List[str]      # Testable acceptance criteria
    rationale: Optional[str]            # Why this requirement exists
```

**Example:**

```python
from src.state import DetailedRequirement, RequirementType

detailed_req = DetailedRequirement(
    id="NAV-FUNC-001",
    text="The Navigation subsystem shall calculate optimal routes",
    type=RequirementType.FUNCTIONAL,
    parent_id="EXTRACT-FUNC-015",
    subsystem="Navigation",
    acceptance_criteria=[
        "Route calculation completes within 500ms",
        "Route considers active speed restrictions"
    ],
    rationale="Decomposed from system navigation requirement"
)
```

---

#### SystemContext

System analysis and architectural context.

```python
class SystemContext(BaseModel):
    """System-level context and architectural understanding."""

    subsystem: str                  # Target subsystem name
    description: str                # Subsystem purpose
    constraints: List[str]          # System-level constraints
    interfaces: List[str]           # External interfaces
    assumptions: List[str]          # Analysis assumptions
```

---

#### DecompositionStrategy

Binding strategy for decomposition (100% enforced).

```python
class DecompositionStrategy(BaseModel):
    """Binding strategy for requirements decomposition."""

    allocation_rules: List[str]              # Subsystem allocation rules
    traceability_rules: List[str]            # Parent-child relationship rules
    decomposition_depth: int                 # Max levels (1-3)
    naming_convention: str                   # ID format template
    acceptance_criteria_required: bool       # AC required flag
```

**Example:**

```python
strategy = DecompositionStrategy(
    allocation_rules=[
        "IF requirement involves route calculation THEN allocate to Navigation",
        "IF requirement involves authentication THEN do NOT allocate"
    ],
    traceability_rules=[
        "Every child requirement MUST have parent_id",
        "Parent ID must reference extracted requirement"
    ],
    decomposition_depth=2,
    naming_convention="NAV-{TYPE}-{NNN}",
    acceptance_criteria_required=True
)
```

---

#### QualityMetrics

Quality assessment scores and issues.

```python
class QualityMetrics(BaseModel):
    """Quality assessment scores (4 or 5 dimensions)."""

    completeness: float            # 0.0-1.0
    clarity: float                 # 0.0-1.0
    testability: float             # 0.0-1.0
    traceability: float            # 0.0-1.0
    domain_compliance: Optional[float]  # 0.0-1.0 (Phase 7: only for domain-aware)
    overall_score: float           # 0.0-1.0 (weighted average)
    issues: List[QualityIssue]     # Specific issues found
```

**Note (Phase 7):**
- **Generic (4 dimensions):** `domain_compliance` is `None`, overall_score computed from 4 dimensions
- **Domain-Aware (5 dimensions):** `domain_compliance` scored 0.0-1.0, overall_score includes 5th dimension
- Weights configurable via environment variables (default: equal weighting)

---

#### QualityIssue

Specific quality issue with severity and suggestion.

```python
class QualityIssue(BaseModel):
    """A specific quality issue."""

    severity: QualitySeverity        # CRITICAL, MAJOR, MINOR
    requirement_id: Optional[str]    # Affected requirement
    dimension: str                   # Quality dimension
    description: str                 # What is wrong
    suggestion: str                  # How to fix it
```

---

#### TraceabilityMatrix

Complete parent-child traceability.

```python
class TraceabilityMatrix(BaseModel):
    """Complete traceability matrix."""

    links: List[TraceabilityLink]          # All relationships
    orphan_requirements: List[str]          # Requirements without parents

    def get_children(self, parent_id: str) -> List[str]:
        """Get all child requirement IDs for a parent."""

    def get_parent(self, child_id: str) -> Optional[str]:
        """Get parent requirement ID for a child."""
```

---

### Helper Functions

#### create_initial_state()

Creates initial state for workflow execution.

```python
def create_initial_state(
    spec_document_path: str,
    target_subsystem: str,
    review_before_decompose: bool = False,
    quality_threshold: float = 0.80,
    max_iterations: int = 3,
    domain_name: str = "generic",              # Phase 7
    subsystem_id: Optional[str] = None         # Phase 7
) -> DecompositionState:
    """
    Create initial state object for starting a decomposition workflow.

    Args:
        spec_document_path: Path to specification document
        target_subsystem: Name of target subsystem
        review_before_decompose: Optional pre-decomposition review flag
        quality_threshold: Quality gate threshold (0.0-1.0)
        max_iterations: Maximum refinement iterations
        domain_name: Domain name for domain-aware decomposition (Phase 7)
        subsystem_id: Subsystem identifier within domain (Phase 7)

    Returns:
        Initial DecompositionState with required fields populated
    """
```

**Example:**

```python
from src.state import create_initial_state

state = create_initial_state(
    spec_document_path="examples/spec.txt",
    target_subsystem="Navigation Subsystem",
    review_before_decompose=False,
    quality_threshold=0.85,
    max_iterations=5
)
```

---

## Agent API

Module: `src/agents/`

### BaseAgent (Abstract Base Class)

Provides common functionality for all agents.

```python
class BaseAgent(ABC):
    """
    Abstract base class for all agents.

    Provides:
        - Skill loading from SKILL.md files
        - Domain context injection (Phase 7)
        - LLM instantiation with fallback logic
        - Error handling with retry/fallback
        - Execution tracking
    """

    def __init__(
        self,
        node_type: NodeType,
        skill_name: Optional[str] = None
    ):
        """
        Initialize base agent.

        Args:
            node_type: Type of workflow node (EXTRACT, ANALYZE, etc.)
            skill_name: Name of skill to load (optional)
        """

    def get_skill_content(
        self,
        domain_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Load skill content with optional domain context injection (Phase 7).

        If domain_context is provided, injects domain-specific conventions,
        glossary, and examples between methodology and generic examples.

        Args:
            domain_context: Optional domain context dict with:
                - domain_name: Domain name (e.g., "csx_dispatch")
                - conventions: Domain conventions markdown
                - glossary: Domain glossary markdown
                - examples: Domain-specific examples markdown

        Returns:
            Skill content as string with optional domain injection

        Example structure:
            [Skill Methodology]
            [Domain Conventions]  <- Injected if domain_context present
            [Domain Glossary]     <- Injected if domain_context present
            [Domain Examples]     <- Injected if domain_context present
            [Generic Examples]
        """

    def execute_with_fallback(
        self,
        execution_func: Callable,
        enable_fallback: bool = True
    ) -> Any:
        """
        Execute function with intelligent fallback handling.

        Error Taxonomy:
            - TRANSIENT: Retry same model (rate limits, timeouts)
            - CONTENT: Switch to fallback model (parse errors)
            - FATAL: Raise exception (auth failures)

        Args:
            execution_func: Function that takes LLM and returns result
            enable_fallback: Whether to enable model fallback

        Returns:
            Result from execution_func

        Raises:
            AgentError: If all retry/fallback attempts fail
        """

    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """
        Execute the agent's main task.

        Must be implemented by subclasses.
        """
```

**Error Handling Flow:**

```python
try:
    result = llm.invoke(prompt)
except RateLimitError:
    # TRANSIENT: Retry with exponential backoff
    time.sleep(delay)
    retry_attempt()
except JSONDecodeError:
    # CONTENT: Switch to fallback model
    fallback_llm = get_fallback_model()
    result = fallback_llm.invoke(prompt)
except AuthenticationError:
    # FATAL: Raise immediately
    raise AgentError("API key invalid")
```

---

### RequirementsAnalystAgent

Extracts requirements from specification documents.

```python
class RequirementsAnalystAgent(BaseAgent):
    """
    Agent for extracting requirements from specifications.

    Uses:
        - requirements-extraction skill
        - Gemini 2.5 Flash-Lite (primary)
        - Gemini 2.5 Flash (fallback)
        - 1M context window for large documents (88K+ tokens)
    """

    def __init__(self):
        """Initialize with requirements-extraction skill."""
        super().__init__(
            node_type=NodeType.EXTRACT,
            skill_name="requirements-extraction"
        )

    def execute(
        self,
        document_text: str,
        enable_fallback: bool = True
    ) -> List[Requirement]:
        """
        Extract requirements from document text.

        Args:
            document_text: Parsed specification text
            enable_fallback: Enable LLM fallback on errors

        Returns:
            List of Requirement objects

        Raises:
            AgentError: If extraction fails after retries
        """
```

---

### SystemArchitectAgent

Analyzes system context and creates decomposition strategy.

```python
class SystemArchitectAgent(BaseAgent):
    """
    Agent for system analysis and strategy creation.

    Uses:
        - system-analysis skill
        - Claude 3.5 Sonnet (primary)
        - GPT-4o (fallback)
    """

    def execute(
        self,
        extracted_requirements: List[Requirement],
        target_subsystem: str,
        enable_fallback: bool = True
    ) -> Tuple[SystemContext, DecompositionStrategy]:
        """
        Analyze system and create decomposition strategy.

        Args:
            extracted_requirements: Requirements from extract node
            target_subsystem: Target subsystem name
            enable_fallback: Enable LLM fallback

        Returns:
            Tuple of (SystemContext, DecompositionStrategy)

        Raises:
            AgentError: If analysis fails
        """
```

---

### RequirementsEngineerAgent

Decomposes requirements following binding strategy.

```python
class RequirementsEngineerAgent(BaseAgent):
    """
    Agent for decomposing requirements.

    Uses:
        - requirements-decomposition skill
        - GPT-4o (primary)
        - Claude Sonnet 4.5 (fallback)
    """

    def execute(
        self,
        system_requirements: List[Requirement],
        decomposition_strategy: DecompositionStrategy,
        target_subsystem: str,
        enable_fallback: bool = True
    ) -> List[DetailedRequirement]:
        """
        Decompose requirements following binding strategy.

        Strategy is 100% binding - violations are bugs, not quality issues.

        Args:
            system_requirements: Extracted requirements
            decomposition_strategy: Binding strategy from analyze node
            target_subsystem: Target subsystem name
            enable_fallback: Enable LLM fallback

        Returns:
            List of DetailedRequirement objects (empty list is valid)

        Raises:
            AgentError: If decomposition fails
        """
```

---

### QualityAssuranceAgent

Validates quality of decomposed requirements.

```python
class QualityAssuranceAgent(BaseAgent):
    """
    Agent for quality validation with optional domain compliance scoring (Phase 7).

    Uses:
        - requirements-quality-validation skill (with 5th dimension support)
        - Gemini 1.5 Pro (primary)
        - Claude 3.5 Sonnet (fallback)
    """

    def execute(
        self,
        decomposed_requirements: List[DetailedRequirement],
        quality_threshold: float,
        enable_fallback: bool = True,
        domain_context: Optional[Dict[str, Any]] = None   # Phase 7
    ) -> Tuple[QualityMetrics, bool]:
        """
        Validate quality of decomposed requirements.

        Scores 4 or 5 dimensions (Phase 7):
            - Completeness (0.0-1.0)
            - Clarity (0.0-1.0)
            - Testability (0.0-1.0)
            - Traceability (0.0-1.0)
            - Domain Compliance (0.0-1.0) [only if domain_context provided]

        Args:
            decomposed_requirements: Requirements to validate
            quality_threshold: Pass threshold (default 0.80)
            enable_fallback: Enable LLM fallback
            domain_context: Optional domain context for 5th dimension scoring (Phase 7)

        Returns:
            Tuple of (QualityMetrics, validation_passed)

        Overall Score Calculation:
            - Generic (4D): Equal weighted average (0.25 each)
            - Domain-Aware (5D): Equal weighted average (0.20 each by default)
            - Weights configurable via environment variables (Phase 7.3)

        Special Cases:
            - Empty list → (1.0 score, True) - valid outcome
        """
```

---

## Utility Functions

Module: `src/utils/`

### Domain Loader **NEW (Phase 7)**

Module: `src/utils/domain_loader.py`

Loads domain-specific context for domain-aware requirements decomposition.

#### DomainLoader.load_context()

Loads complete domain context with conventions, glossary, and examples.

```python
class DomainLoader:
    """Static utility class for loading domain context."""

    @staticmethod
    def load_context(
        domain_name: str,
        subsystem_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Load complete domain context for a specified domain/subsystem.

        Args:
            domain_name: Domain name (e.g., "csx_dispatch")
            subsystem_id: Optional subsystem identifier (e.g., "train_management")

        Returns:
            Dict containing:
                - domain_name: str
                - subsystem_id: Optional[str]
                - conventions: str (markdown content)
                - glossary: str (markdown content)
                - examples: str (markdown content, subsystem-specific if provided)

        Raises:
            DomainLoadError: If domain not found or files invalid

        Example:
            context = DomainLoader.load_context("csx_dispatch", "train_management")
            # Returns: {
            #     "domain_name": "csx_dispatch",
            #     "subsystem_id": "train_management",
            #     "conventions": "...",  # Layer 1: Common conventions
            #     "glossary": "...",     # Layer 1: Domain glossary
            #     "examples": "..."      # Layer 2: Train Management examples
            # }
        """
```

#### DomainLoader.list_domains()

Lists all available domains.

```python
@staticmethod
def list_domains() -> List[Dict[str, Any]]:
    """
    List all configured domains with metadata.

    Returns:
        List of domain dicts with:
            - name: Domain identifier
            - display_name: Human-readable name
            - description: Domain description
            - subsystems: List of subsystem dicts

    Example:
        domains = DomainLoader.list_domains()
        # [
        #     {
        #         "name": "csx_dispatch",
        #         "display_name": "CSX Dispatch",
        #         "description": "Train dispatch operations",
        #         "subsystems": [...]
        #     }
        # ]
    """
```

#### DomainLoader.list_subsystems()

Lists subsystems for a specific domain.

```python
@staticmethod
def list_subsystems(domain_name: str) -> List[Dict[str, str]]:
    """
    List all subsystems for a domain.

    Args:
        domain_name: Domain name (e.g., "csx_dispatch")

    Returns:
        List of subsystem dicts with:
            - id: Subsystem identifier
            - name: Human-readable name

    Raises:
        DomainLoadError: If domain not found

    Example:
        subsystems = DomainLoader.list_subsystems("csx_dispatch")
        # [
        #     {"id": "train_management", "name": "Train Management"},
        #     {"id": "movement_authority", "name": "Movement Authority"}
        # ]
    """
```

**Domain File Structure:**

```
domains/
└── <domain_name>/
    ├── domain_config.json          # Domain metadata
    ├── conventions.md              # Layer 1: Common conventions
    ├── glossary.md                 # Layer 1: Domain glossary
    └── subsystems/
        └── <subsystem_id>/
            └── examples.md         # Layer 2: Subsystem examples
```

---

### Document Parser

Module: `src/utils/document_parser.py`

#### parse_document()

Parses specification documents (txt, docx, pdf).

```python
def parse_document(file_path: str) -> Tuple[str, str]:
    """
    Parse a specification document and extract text content.

    Supported Formats:
        - .txt (plain text)
        - .docx (Microsoft Word)
        - .pdf (PDF documents)

    Args:
        file_path: Path to the specification document

    Returns:
        Tuple of (content, file_format)
        - content: Extracted text content
        - file_format: File extension (txt, docx, pdf)

    Raises:
        DocumentParseError: If file format unsupported or parsing fails
    """
```

**Example:**

```python
from src.utils.document_parser import parse_document

content, format = parse_document("examples/spec.docx")
print(f"Parsed {format} file: {len(content)} characters")
```

---

#### parse_txt()

Parses plain text files with encoding detection.

```python
def parse_txt(file_path: str) -> str:
    """
    Parse a plain text file.

    Tries multiple encodings: utf-8, latin-1, cp1252

    Args:
        file_path: Path to .txt file

    Returns:
        Extracted text content

    Raises:
        DocumentParseError: If file cannot be read
    """
```

---

#### parse_docx()

Parses Microsoft Word documents.

```python
def parse_docx(file_path: str) -> str:
    """
    Parse a Word document (.docx).

    Extracts:
        - Paragraph text
        - Table content (formatted with | separators)

    Args:
        file_path: Path to .docx file

    Returns:
        Extracted text content

    Raises:
        DocumentParseError: If file cannot be parsed
    """
```

---

#### parse_pdf()

Parses PDF documents.

```python
def parse_pdf(file_path: str) -> str:
    """
    Parse a PDF document.

    Extracts text from all pages using PyPDF2.

    Args:
        file_path: Path to .pdf file

    Returns:
        Extracted text content

    Raises:
        DocumentParseError: If file cannot be parsed
    """
```

---

### Skill Loader

Module: `src/utils/skill_loader.py`

#### load_skill()

Loads SKILL.md file content with caching.

```python
@lru_cache(maxsize=32)
def load_skill(skill_name: str, use_cache: bool = True) -> str:
    """
    Load the content of a SKILL.md file.

    Cached using lru_cache for performance - same skill loaded only once.

    Args:
        skill_name: Name of skill (e.g., 'requirements-extraction')
        use_cache: Whether to use cache (for testing)

    Returns:
        Content of SKILL.md file as string

    Raises:
        SkillLoadError: If skill directory or file not found
    """
```

**Example:**

```python
from src.utils.skill_loader import load_skill

skill_content = load_skill("requirements-extraction")
print(f"Loaded skill: {len(skill_content)} characters")
```

---

#### get_skill_path()

Gets path to specific skill's SKILL.md file.

```python
def get_skill_path(skill_name: str) -> Path:
    """
    Get path to a specific skill's SKILL.md file.

    Args:
        skill_name: Name of skill (e.g., 'requirements-extraction')

    Returns:
        Path object pointing to SKILL.md file

    Raises:
        SkillLoadError: If skill directory or file doesn't exist
    """
```

---

#### get_skills_directory()

Gets path to skills directory.

```python
def get_skills_directory() -> Path:
    """
    Get the path to the skills directory.

    Returns:
        Path object pointing to skills directory

    Raises:
        SkillLoadError: If skills directory not found
    """
```

---

### Quality Checker

Module: `src/utils/quality_checker.py`

Provides utility functions for quality assessment.

---

### Traceability

Module: `src/utils/traceability.py`

Provides traceability matrix generation and validation.

---

## Configuration

Module: `config/llm_config.py`

### Model Configuration

#### NodeType (Enum)

Workflow node types.

```python
class NodeType(str, Enum):
    """Types of workflow nodes."""
    EXTRACT = "extract"
    ANALYZE = "analyze"
    DECOMPOSE = "decompose"
    VALIDATE = "validate"
```

---

#### ModelConfig

LLM model configuration.

```python
class ModelConfig(BaseModel):
    """Configuration for a specific LLM model."""

    provider: ModelProvider       # OPENAI, ANTHROPIC, GOOGLE
    model_name: str              # Specific model ID
    temperature: float           # 0.0-1.0
    max_tokens: int              # Max output tokens
```

**Predefined Models:**

```python
GPT_4O_MINI = ModelConfig(
    provider=ModelProvider.OPENAI,
    model_name="gpt-4o-mini",
    temperature=0.0,
    max_tokens=4096
)

CLAUDE_SONNET_3_5 = ModelConfig(
    provider=ModelProvider.ANTHROPIC,
    model_name="claude-3-5-sonnet-20241022",
    temperature=0.1,
    max_tokens=8192
)

GEMINI_1_5_PRO = ModelConfig(
    provider=ModelProvider.GOOGLE,
    model_name="gemini-1.5-pro",
    temperature=0.0,
    max_tokens=8192
)
```

---

#### NODE_MODELS

Model assignment by node type.

```python
NODE_MODELS = {
    NodeType.EXTRACT: NodeModelConfig(
        primary_model=GPT_4O_MINI,
        fallback_models=[GPT_4O, CLAUDE_SONNET_4_5]
    ),
    NodeType.ANALYZE: NodeModelConfig(
        primary_model=CLAUDE_SONNET_3_5,
        fallback_models=[GPT_4O, CLAUDE_SONNET_4_5]
    ),
    NodeType.DECOMPOSE: NodeModelConfig(
        primary_model=GPT_4O,
        fallback_models=[CLAUDE_SONNET_4_5, CLAUDE_SONNET_3_5]
    ),
    NodeType.VALIDATE: NodeModelConfig(
        primary_model=GEMINI_1_5_PRO,
        fallback_models=[CLAUDE_SONNET_3_5, GPT_4O]
    )
}
```

---

### Retry Configuration

```python
RETRY_MAX_ATTEMPTS = 3              # Max retries for transient errors
RETRY_INITIAL_DELAY = 1.0           # Initial delay (seconds)
RETRY_BACKOFF_FACTOR = 2.0          # Exponential backoff multiplier
RETRY_MAX_DELAY = 60.0              # Max delay between retries
```

---

## Error Handling

### Error Taxonomy

Three categories of errors:

#### TRANSIENT Errors

**Characteristics:**
- Temporary issues
- Likely to succeed on retry
- Examples: Rate limits, timeouts, network errors

**Handling:**
- Retry same model
- Exponential backoff
- Max attempts: 3

**Examples:**

```python
RateLimitError
TimeoutError
APIConnectionError
```

---

#### CONTENT Errors

**Characteristics:**
- Invalid LLM output
- Model-specific issues
- Examples: JSON parse errors, validation failures

**Handling:**
- Switch to fallback model
- No retry on same model
- Track fallback count

**Examples:**

```python
JSONDecodeError
ValidationError
ParseError
```

---

#### FATAL Errors

**Characteristics:**
- Unrecoverable issues
- Require human intervention
- Examples: Auth failures, missing resources

**Handling:**
- Raise exception immediately
- No retry or fallback
- Log detailed error

**Examples:**

```python
AuthenticationError
PermissionError
FileNotFoundError (for skills)
```

---

### Error Logging

All errors tracked in state:

```python
state["errors"]       # List[str] - Simple messages
state["error_log"]    # List[ErrorLog] - Detailed tracking
state["fallback_count"]  # int - Fallback frequency
```

**ErrorLog Structure:**

```python
{
    "timestamp": "2025-11-02T14:30:22",
    "error_type": "CONTENT",
    "node": "decompose",
    "message": "JSON parse error",
    "details": {
        "raw_response": "...",
        "attempted_model": "gpt-4o",
        "fallback_model": "claude-sonnet-4-5"
    }
}
```

---

## Extension Examples

### Adding a New Node

1. **Create node function** (`src/nodes/my_node.py`):

```python
from src.state import DecompositionState

def my_node(state: DecompositionState) -> DecompositionState:
    """
    Execute my custom node logic.

    Args:
        state: Current state

    Returns:
        Updated state
    """
    # Node logic here
    return {
        **state,
        "my_custom_field": "value"
    }
```

2. **Update state schema** (`src/state.py`):

```python
class DecompositionState(TypedDict, total=False):
    # ... existing fields ...
    my_custom_field: str
```

3. **Add to graph** (`src/graph.py`):

```python
from src.nodes.my_node import my_node

workflow.add_node("my_node", my_node)
workflow.add_edge("previous_node", "my_node")
workflow.add_edge("my_node", "next_node")
```

---

### Adding a New Agent

1. **Create agent class** (`src/agents/my_agent.py`):

```python
from src.agents.base_agent import BaseAgent
from config.llm_config import NodeType

class MyAgent(BaseAgent):
    """My custom agent."""

    def __init__(self):
        super().__init__(
            node_type=NodeType.EXTRACT,  # Or create new NodeType
            skill_name="my-skill"  # Optional
        )

    def execute(self, input_data, enable_fallback=True):
        """Execute agent logic."""
        prompt = self._build_prompt(input_data)

        def execute_task(llm):
            response = llm.invoke(prompt)
            return self._parse_response(response.content)

        return self.execute_with_fallback(execute_task, enable_fallback)
```

2. **Use in node function**:

```python
from src.agents.my_agent import MyAgent

def my_node(state):
    agent = MyAgent()
    result = agent.execute(state["input_data"])
    return {**state, "output_data": result}
```

---

### Adding a New Skill

1. **Create skill directory**:

```bash
mkdir -p skills/my-skill/examples
```

2. **Create SKILL.md**:

```markdown
# My Skill

## Purpose
Description of what this skill does...

## Methodology
Step-by-step instructions...

## Output Format
Expected JSON structure...

## Examples
Good vs. bad examples...
```

3. **Create VERSION.txt**:

```
v1.0.0
```

4. **Load in agent**:

```python
class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            node_type=NodeType.EXTRACT,
            skill_name="my-skill"  # Will load skills/my-skill/SKILL.md
        )
```

---

## Best Practices

### State Management

1. **Never mutate state directly**:

```python
# Bad
state["field"] = "value"

# Good
return {**state, "field": "value"}
```

2. **Use type hints**:

```python
def my_node(state: DecompositionState) -> DecompositionState:
    ...
```

3. **Validate inputs**:

```python
if not state.get("required_field"):
    raise ValueError("Missing required field")
```

---

### Error Handling

1. **Use error taxonomy**:

```python
try:
    result = llm.invoke(prompt)
except RateLimitError:
    # TRANSIENT: Retry
    return retry_with_backoff()
except JSONDecodeError:
    # CONTENT: Fallback
    return execute_with_fallback_model()
except AuthenticationError:
    # FATAL: Raise
    raise AgentError("Auth failed")
```

2. **Log all errors**:

```python
state["errors"].append(f"Parse failed: {str(e)}")
state["error_log"].append({
    "timestamp": datetime.now().isoformat(),
    "error_type": "CONTENT",
    "node": "my_node",
    "message": str(e)
})
```

---

### Performance

1. **Use caching**:

```python
# Skills are cached automatically
skill = load_skill("my-skill")  # Cached after first call
```

2. **Avoid redundant LLM calls**:

```python
# Check state first
if state.get("cached_result"):
    return state["cached_result"]

# Only call LLM if needed
result = llm.invoke(prompt)
```

3. **Choose appropriate models**:

```python
# Use cheaper models for simple tasks
NodeType.EXTRACT: GPT_4O_MINI  # Cost-optimized

# Use powerful models for complex tasks
NodeType.ANALYZE: CLAUDE_SONNET_3_5  # Architectural reasoning
```

---

## Phase 5: Observability & Tracking

### Overview

Phase 5 (November 12, 2025) adds production-grade observability with real-time cost tracking, quality trend monitoring, and automated reporting capabilities.

###  Cost Tracker (`src/utils/cost_tracker.py`)

SQLite-based cost history tracking with budget management.

```python
class CostTracker:
    """
    Track LLM costs across workflow runs with budget management.

    Database Schema:
        - cost_runs: run_id, timestamp, subsystem, total_cost, cost_source
        - cost_details: run_id, node, model, input_tokens, output_tokens, cost
    """

    def __init__(self, db_path: str = "data/costs.db"):
        """Initialize cost tracker with database path."""

    def start_run(self, run_id: str, subsystem: str) -> None:
        """Start tracking a new workflow run."""

    def record_node_cost(
        self,
        run_id: str,
        node: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost_source: str = "heuristic"
    ) -> float:
        """
        Record cost for a single node execution.

        Args:
            run_id: Unique run identifier
            node: Node name (extract, analyze, decompose, validate)
            model: LLM model used
            input_tokens: Input token count
            output_tokens: Output token count
            cost_source: "langsmith" or "heuristic"

        Returns:
            Calculated cost for this node
        """

    def calculate_node_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """Calculate cost using model pricing from llm_config.py."""

    def check_budget(
        self,
        run_id: str,
        warning_threshold: float = 1.00,
        max_budget: float = 5.00
    ) -> Dict[str, Any]:
        """
        Check if budget thresholds exceeded.

        Returns:
            {
                "total_cost": float,
                "warning": bool,
                "exceeded": bool,
                "message": str
            }
        """

    def finalize_run(self, subsystem: str, source_method: str = 'heuristic') -> CostRecord:
        """
        Finalize current run and store in database.

        Args:
            subsystem: Target subsystem for this run
            source_method: 'langsmith' or 'heuristic' (default: 'heuristic')

        Returns:
            CostRecord: Complete run information including costs, tokens, and metadata
        """

    def get_recent_runs(self, days: int = 30) -> List[Dict]:
        """Retrieve recent run cost history."""

    def get_cost_trends(self, days: int = 30) -> Dict[str, Any]:
        """
        Get aggregated cost statistics.

        Returns:
            {
                "total_cost": float,
                "avg_cost": float,
                "min_cost": float,
                "max_cost": float,
                "run_count": int
            }
        """
```

### Quality Tracker (`src/utils/quality_tracker.py`)

SQLite-based quality metrics tracking across workflow runs.

```python
class QualityTracker:
    """
    Track quality metrics across workflow runs.

    Database Schema:
        - quality_runs: run_id, timestamp, subsystem, overall_score,
                       completeness, clarity, testability, traceability,
                       validation_passed, iteration_count, requirements_count
    """

    def __init__(self, db_path: str = "data/quality.db"):
        """Initialize quality tracker with database path."""

    def record_quality(
        self,
        run_id: str,
        subsystem: str,
        quality_metrics: QualityMetrics,
        iteration_count: int,
        requirements_count: int
    ) -> None:
        """
        Record quality metrics for a workflow run.

        Args:
            run_id: Unique run identifier
            subsystem: Target subsystem
            quality_metrics: QualityMetrics object from validation
            iteration_count: Number of refinement iterations
            requirements_count: Number of decomposed requirements
        """

    def get_recent_runs(self, days: int = 30) -> List[Dict]:
        """Retrieve recent run quality history."""

    def get_quality_trends(self, days: int = 30) -> Dict[str, Any]:
        """
        Get aggregated quality statistics.

        Returns:
            {
                "avg_overall_score": float,
                "avg_completeness": float,
                "avg_clarity": float,
                "avg_testability": float,
                "avg_traceability": float,
                "pass_rate": float (0.0-1.0),
                "avg_iterations": float,
                "run_count": int
            }
        """

    def get_subsystem_comparison(self, days: int = 30) -> Dict[str, Dict]:
        """
        Compare quality metrics across different subsystems.

        Returns:
            {
                "Navigation": {"avg_score": 0.92, "pass_rate": 1.0, ...},
                "Authentication": {"avg_score": 0.85, "pass_rate": 0.8, ...}
            }
        """
```

### LangSmith Integration (`src/utils/langsmith_integration.py`)

Helper utilities for extracting token counts from LLM responses.

```python
def extract_tokens_from_response(response: Any) -> Tuple[int, int]:
    """
    Extract input and output token counts from LLM response.

    Supports:
        - OpenAI: response_metadata.token_usage
        - Anthropic: response_metadata.usage
        - Google/Gemini: response_metadata.usage_metadata

    Args:
        response: LLM response object from LangChain

    Returns:
        (input_tokens, output_tokens) tuple
        Returns (0, 0) if extraction fails
    """

class LangSmithTracker:
    """
    Optional: Fetch precise costs from LangSmith API.
    Requires LANGCHAIN_API_KEY environment variable.
    """

    def get_run_costs(self, run_id: str) -> Dict[str, Any]:
        """Fetch precise token counts and costs from LangSmith."""

    def get_project_runs(self, project_name: str, limit: int = 10) -> List[Dict]:
        """List recent runs for a LangSmith project."""

    def get_aggregate_costs(
        self,
        project_name: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get aggregated costs for a project over time period."""
```

### Observability Config (`config/observability_config.py`)

Configuration for LangSmith and cost tracking.

```python
class ObservabilityConfig:
    """Configuration for observability features."""

    @staticmethod
    def is_langsmith_enabled() -> bool:
        """Check if LangSmith tracing is enabled."""

    @staticmethod
    def get_langsmith_config() -> Dict[str, str]:
        """
        Get LangSmith configuration from environment.

        Returns:
            {
                "endpoint": str,
                "api_key": str,
                "project": str,
                "enabled": bool
            }
        """

    @staticmethod
    def get_cost_config() -> Dict[str, Any]:
        """
        Get cost tracking configuration.

        Returns:
            {
                "enabled": bool,
                "warning_threshold": float,
                "max_budget": float
            }
        """
```

### Report Generation (`scripts/generate_reports.py`)

CLI tool for generating cost and quality reports.

```bash
# Generate all reports
python scripts/generate_reports.py

# Generate only cost report
python scripts/generate_reports.py --report cost

# Generate for specific time period
python scripts/generate_reports.py --days 7

# Save to file
python scripts/generate_reports.py --output reports/
```

**Example Cost Report:**
```
=== Cost Report (Last 30 Days) ===

Total Cost: $0.0342
Average Cost per Run: $0.0114
Min Cost: $0.0089
Max Cost: $0.0156
Number of Runs: 3

Recent Runs:
  run_20251112_140523 | Navigation | $0.0156 | heuristic
  run_20251112_135012 | Navigation | $0.0098 | heuristic
  run_20251112_134501 | Navigation | $0.0089 | heuristic
```

**Example Quality Report:**
```
=== Quality Report (Last 30 Days) ===

Average Overall Score: 0.94
Average Completeness: 0.92
Average Clarity: 0.95
Average Testability: 0.93
Average Traceability: 0.96

Pass Rate: 100.0%
Average Iterations: 0.67

Subsystem Comparison:
  Navigation: avg=0.94, pass_rate=100.0%, runs=3
```

---

## Version History

- **v1.2.0** (2025-11-12): Phase 5 Complete - Enhanced Observability
  - Cost tracking with SQLite-based history (`cost_tracker.py`)
  - Quality metrics tracking (`quality_tracker.py`)
  - LangSmith integration utilities (`langsmith_integration.py`)
  - Budget management with warnings and limits
  - Automated report generation scripts
  - Observability configuration module

- **v1.1.0** (2025-11-08): Phase 4 Complete - Testing & Deployment
  - Large document support (Gemini 2.5, GPT-5 Nano integration)
  - Performance timing tracking
  - Heuristic cost estimation
  - 88K+ token PDF processing capability
  - Model configuration updates

- **v1.0.0** (2025-11-02): Phase 3 Complete - Graph Assembly & UX
  - Complete Phase 3 implementation
  - All nodes, agents, and utilities documented
  - Graph assembly and state schema finalized

---

**Last Updated:** 2025-11-12
**Phase:** 5 Complete
**Status:** Production-Ready with Enhanced Observability
