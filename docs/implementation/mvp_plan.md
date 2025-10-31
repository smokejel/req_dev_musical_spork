# Requirements Decomposition System - LangGraph MVP Implementation Plan

**Project:** AI-Accelerated Requirements Engineering using LangGraph
**Target:** Streamlined MVP for system-to-subsystem requirement decomposition
**Timeline:** 4.5 weeks to working MVP (includes Phase 0 validation)
**Author:** Michael Sweatt
**Last Updated:** October 30, 2025

---

## Executive Summary

This plan outlines a phased approach to building a production-ready requirements decomposition system using LangGraph. The MVP focuses on the critical path: extract → analyze → decompose → validate. We've streamlined from 9 agents/tasks to 4 core nodes, reducing complexity while maintaining quality.

**Key Design Decisions:**
- **Phase 0 validation** of Claude Skills approach before full implementation
- Use LangGraph for explicit state management and control flow
- Implement quality gates with **iterative refinement loops that include specific feedback**
- Build modular skills (SKILL.md files) that can be referenced by LLM agents
- **Decomposition strategy is 100% binding** (not advisory)
- **Intelligent LLM fallback** with error taxonomy (transient, content, fatal)
- Start with single-subsystem decomposition, expand later
- Prioritize debugging and observability from day one
- **Human-in-the-loop** at validation failures AND optionally before decomposition

---

## MVP Scope: What We're Building

### Core Functionality
1. **Input:** System-level specification document (PDF/DOCX)
2. **Process:** Extract → Analyze → Decompose → Validate
3. **Output:** Subsystem requirements with traceability
4. **Quality Gates:** Automated validation with human review option

### Explicit Non-Goals for MVP
- ❌ Multi-subsystem optimization (do one subsystem well first)
- ❌ Complex interface definitions (ICD integration comes later)
- ❌ Full regulatory compliance checks (focus on quality standards)
- ❌ UI/dashboard (command-line execution only)
- ❌ Real-time collaboration features

---

## Streamlined Architecture

### 4-Node Graph Structure

```
┌─────────────────────────────────────────────────────────────┐
│                     LANGGRAPH WORKFLOW                      │
└─────────────────────────────────────────────────────────────┘

    START
      ↓
┌─────────────────────┐
│ 1. EXTRACT NODE     │  Input: Spec document
│    Requirements     │  Output: Parsed requirements list
│    Analyst Agent    │  Skills: requirements-extraction
└─────────────────────┘
      ↓
┌─────────────────────┐
│ 2. ANALYZE NODE     │  Input: Requirements + architecture context
│    System Context   │  Output: Decomposition strategy
│    Architect Agent   │  Skills: system-analysis, decomposition-strategy
└─────────────────────┘
      ↓
┌─────────────────────┐
│ 3. DECOMPOSE NODE   │  Input: Strategy + requirements
│    Generate SubReqs │  Output: Subsystem requirements
│    Engineer Agent    │  Skills: requirements-decomposition
└─────────────────────┘
      ↓
┌─────────────────────┐
│ 4. VALIDATE NODE    │  Input: All requirements
│    Quality Check    │  Output: Quality report + validated reqs
│    QA Agent          │  Skills: requirements-quality-validation
└─────────────────────┘
      ↓
    Quality Gate
      ├─ PASS → Generate Documentation → END
      └─ FAIL → [Human Review] → Revise → DECOMPOSE NODE
```

### State Schema

```python
from typing import TypedDict, List, Optional, Literal

class Requirement(TypedDict):
    id: str
    text: str
    type: Literal["functional", "performance", "constraint", "interface"]
    parent_id: Optional[str]
    subsystem: Optional[str]
    rationale: Optional[str]
    acceptance_criteria: Optional[str]

class DecompositionStrategy(TypedDict):
    approach: str  # "functional", "architectural", "hybrid"
    subsystem_list: List[str]
    allocation_rules: str
    templates: dict

class QualityMetrics(TypedDict):
    overall_score: float
    completeness: float
    clarity: float
    testability: float
    traceability: float
    issues: List[dict]

class DecompositionState(TypedDict):
    # Input
    spec_document_path: str
    target_subsystem: str
    
    # Intermediate results
    extracted_requirements: List[Requirement]
    system_context: str
    decomposition_strategy: DecompositionStrategy
    subsystem_requirements: List[Requirement]
    
    # Quality tracking
    quality_metrics: QualityMetrics
    validation_passed: bool
    iteration_count: int
    
    # Human review
    human_feedback: Optional[str]
    requires_human_review: bool
    
    # Output
    final_document_path: Optional[str]
    traceability_matrix: Optional[dict]
```

---

## Phase 0: Skills Architecture Validation (Days -2 to 0) ⚠️ CRITICAL

**Goal:** Validate that Claude Skills approach works reliably before committing to full implementation

### Why Phase 0 is Critical

The entire architecture depends on LLMs following SKILL.md methodology documents. If skills don't guide LLM behavior effectively, the system will produce inconsistent or low-quality outputs. **This validation de-risks the entire 4-week investment** by confirming the approach works in 2-3 days.

**Risk Without Validation:**
- Build for 2 weeks, discover skills don't work consistently
- Forced to pivot to structured prompts mid-project
- Wasted time and effort rebuilding architecture

**Investment:**
- 2-3 days now vs. 2+ weeks of potential rework
- Empirical validation with measurable success criteria
- Clear pivot strategy if validation fails

---

### Phase 0: Deliverables

**Deliverables:**
- [ ] Minimal requirements-extraction/SKILL.md (500-1000 tokens)
- [ ] 3 test specification documents (simple, medium, complex)
- [ ] Ground truth: manually extracted requirements for each spec
- [ ] Test harness to measure skill effectiveness
- [ ] Validation report with go/no-go recommendation

---

### Phase 0.1: Create Minimal Extraction Skill (Day -2, Morning)

**Task:** Write a focused requirements extraction skill for testing

**Implementation: `skills/requirements-extraction/SKILL.md` (Minimal Version)**

```markdown
# Requirements Extraction Methodology

## Purpose
Extract atomic, testable requirements from system specifications.

## Process

### Step 1: Identify Requirements
Look for statements with modal verbs (shall, must, should, may) or imperative language.

### Step 2: Categorize
- **Functional:** What the system does
- **Performance:** How well it does it (speed, accuracy, capacity)
- **Constraint:** Limitations or restrictions
- **Interface:** External system interactions

### Step 3: Extract with Metadata
Each requirement must include:
- Unique ID: `EXTRACT-{TYPE}-{NUM}`
- Full text (exact quote)
- Type classification
- Source reference (section, page)

### Step 4: Quality Check
Each requirement must be:
- ✓ Atomic (single, testable statement)
- ✓ Unambiguous (single interpretation)
- ✓ Measurable (clear acceptance criteria)

## Output Format
```json
[
  {
    "id": "EXTRACT-FUNC-001",
    "text": "[exact quote from document]",
    "type": "functional|performance|constraint|interface",
    "source_reference": "Section X.Y, Page N"
  }
]
```

## Example
**Source:** "The system shall process requests within 100ms."
**Output:**
```json
{
  "id": "EXTRACT-PERF-001",
  "text": "The system shall process requests within 100ms",
  "type": "performance",
  "source_reference": "Section 3.2, Page 15"
}
```
\`\`\`

**Tasks:**
1. Create `skills/` directory
2. Create `skills/requirements-extraction/` subdirectory
3. Write minimal SKILL.md (above)
4. Keep it focused: ~500-800 tokens

**Success Criteria:**
- ✅ Skill file created and readable
- ✅ Contains clear methodology and examples
- ✅ Under 1000 tokens (concise)

---

### Phase 0.2: Create Test Corpus (Day -2, Afternoon)

**Task:** Create 3 test specifications with known-good extractions

**Test Specification 1: Simple (Happy Path)**

Create `examples/phase0_simple_spec.txt`:
```
System Requirements Specification

3.1 Functional Requirements

REQ-001: The system shall authenticate users using OAuth2.

REQ-002: The system shall log all user actions to the audit database.

3.2 Performance Requirements

REQ-003: The system shall process login requests within 500ms.

REQ-004: The system shall support 1000 concurrent users.

3.3 Constraints

REQ-005: The system shall operate on Linux kernel 5.15 or later.
```

Create `examples/phase0_simple_expected.json`:
```json
[
  {
    "id": "EXTRACT-FUNC-001",
    "text": "The system shall authenticate users using OAuth2",
    "type": "functional",
    "source_reference": "Section 3.1"
  },
  {
    "id": "EXTRACT-FUNC-002",
    "text": "The system shall log all user actions to the audit database",
    "type": "functional",
    "source_reference": "Section 3.1"
  },
  {
    "id": "EXTRACT-PERF-001",
    "text": "The system shall process login requests within 500ms",
    "type": "performance",
    "source_reference": "Section 3.2"
  },
  {
    "id": "EXTRACT-PERF-002",
    "text": "The system shall support 1000 concurrent users",
    "type": "performance",
    "source_reference": "Section 3.2"
  },
  {
    "id": "EXTRACT-CONS-001",
    "text": "The system shall operate on Linux kernel 5.15 or later",
    "type": "constraint",
    "source_reference": "Section 3.3"
  }
]
```

**Test Specification 2: Medium (Ambiguity Testing)**

Create `examples/phase0_medium_spec.txt` with:
- 15 requirements
- Some compound statements (multiple requirements in one sentence)
- Ambiguous language ("quickly", "user-friendly")
- Mixed formatting (some with IDs, some without)

**Test Specification 3: Complex (Edge Cases)**

Create `examples/phase0_complex_spec.txt` with:
- 30+ requirements
- Poor formatting (no section headers)
- Implied requirements (not explicitly stated)
- Tables and lists
- Background text mixed with requirements

**Tasks:**
1. Create all 3 specs + expected outputs
2. Manually extract requirements (ground truth)
3. Document edge cases to test

**Success Criteria:**
- ✅ 3 spec files created with varying complexity
- ✅ Ground truth extractions documented
- ✅ Expected outputs in JSON format

---

### Phase 0.3: Build Test Harness (Day -1, Morning)

**Task:** Create automated testing framework for skill validation

**Implementation: `tests/test_phase0_skills.py`**

```python
"""
Phase 0: Skills Validation Test Suite

Tests whether SKILL.md files can reliably guide LLM behavior.
"""

import json
from pathlib import Path
from typing import List, Dict
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate

def load_skill(skill_name: str) -> str:
    """Load skill content from markdown file."""
    skill_path = Path(f"skills/{skill_name}/SKILL.md")
    return skill_path.read_text()

def load_spec(spec_name: str) -> str:
    """Load test specification."""
    spec_path = Path(f"examples/{spec_name}.txt")
    return spec_path.read_text()

def load_expected(spec_name: str) -> List[Dict]:
    """Load expected extraction results."""
    expected_path = Path(f"examples/{spec_name}_expected.json")
    return json.loads(expected_path.read_text())

def extract_with_skill(spec_text: str, skill_content: str) -> List[Dict]:
    """Extract requirements using skill-guided LLM."""

    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        temperature=0.0
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", f"{skill_content}\n\nApply this methodology to extract requirements."),
        ("human", f"Specification document:\n\n{spec_text}\n\nExtract all requirements as JSON array.")
    ])

    chain = prompt | llm
    response = chain.invoke({})

    # Parse JSON from response
    content = response.content
    if "```json" in content:
        json_text = content.split("```json")[1].split("```")[0].strip()
    else:
        json_text = content

    return json.loads(json_text)

def extract_without_skill(spec_text: str) -> List[Dict]:
    """Extract requirements using baseline prompt (no skill)."""

    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        temperature=0.0
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a requirements analyst. Extract all requirements from the specification."),
        ("human", f"Specification:\n\n{spec_text}\n\nExtract requirements as JSON array with fields: id, text, type, source_reference.")
    ])

    chain = prompt | llm
    response = chain.invoke({})

    content = response.content
    if "```json" in content:
        json_text = content.split("```json")[1].split("```")[0].strip()
    else:
        json_text = content

    return json.loads(json_text)

def calculate_precision_recall(extracted: List[Dict], expected: List[Dict]) -> Dict:
    """Calculate precision and recall metrics."""

    # Normalize for comparison (use text)
    extracted_texts = {req["text"].lower().strip() for req in extracted}
    expected_texts = {req["text"].lower().strip() for req in expected}

    true_positives = len(extracted_texts & expected_texts)
    false_positives = len(extracted_texts - expected_texts)
    false_negatives = len(expected_texts - extracted_texts)

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives
    }

def test_consistency(spec_text: str, skill_content: str, runs: int = 3) -> float:
    """Test output consistency across multiple runs."""

    results = []
    for i in range(runs):
        extracted = extract_with_skill(spec_text, skill_content)
        # Normalize to text only for comparison
        result_texts = sorted([req["text"].lower().strip() for req in extracted])
        results.append(result_texts)

    # Calculate pairwise agreement
    total_agreements = 0
    comparisons = 0

    for i in range(len(results)):
        for j in range(i + 1, len(results)):
            set_i = set(results[i])
            set_j = set(results[j])
            agreement = len(set_i & set_j) / len(set_i | set_j) if len(set_i | set_j) > 0 else 0
            total_agreements += agreement
            comparisons += 1

    consistency = total_agreements / comparisons if comparisons > 0 else 0
    return consistency

def run_phase0_validation():
    """Run complete Phase 0 validation suite."""

    print("="*80)
    print("PHASE 0: SKILLS ARCHITECTURE VALIDATION")
    print("="*80)

    skill_content = load_skill("requirements-extraction")

    results = {}

    for spec_name in ["phase0_simple_spec", "phase0_medium_spec", "phase0_complex_spec"]:
        print(f"\n--- Testing: {spec_name} ---")

        spec_text = load_spec(spec_name)
        expected = load_expected(spec_name)

        # Test with skill
        print("Extracting WITH skill...")
        extracted_with_skill = extract_with_skill(spec_text, skill_content)
        metrics_with_skill = calculate_precision_recall(extracted_with_skill, expected)

        # Test without skill (baseline)
        print("Extracting WITHOUT skill (baseline)...")
        extracted_without_skill = extract_without_skill(spec_text)
        metrics_without_skill = calculate_precision_recall(extracted_without_skill, expected)

        # Test consistency
        print("Testing consistency (3 runs)...")
        consistency = test_consistency(spec_text, skill_content, runs=3)

        # Calculate improvement
        improvement = ((metrics_with_skill["f1"] - metrics_without_skill["f1"]) / metrics_without_skill["f1"] * 100) if metrics_without_skill["f1"] > 0 else 0

        results[spec_name] = {
            "with_skill": metrics_with_skill,
            "without_skill": metrics_without_skill,
            "improvement_percent": improvement,
            "consistency": consistency
        }

        # Print results
        print(f"\nResults for {spec_name}:")
        print(f"  WITH Skill    - Precision: {metrics_with_skill['precision']:.2f}, Recall: {metrics_with_skill['recall']:.2f}, F1: {metrics_with_skill['f1']:.2f}")
        print(f"  WITHOUT Skill - Precision: {metrics_without_skill['precision']:.2f}, Recall: {metrics_without_skill['recall']:.2f}, F1: {metrics_without_skill['f1']:.2f}")
        print(f"  Improvement: {improvement:.1f}%")
        print(f"  Consistency: {consistency:.2%}")

    # Overall assessment
    print("\n" + "="*80)
    print("OVERALL ASSESSMENT")
    print("="*80)

    avg_improvement = sum(r["improvement_percent"] for r in results.values()) / len(results)
    avg_consistency = sum(r["consistency"] for r in results.values()) / len(results)
    avg_f1_with_skill = sum(r["with_skill"]["f1"] for r in results.values()) / len(results)

    print(f"\nAverage Improvement: {avg_improvement:.1f}%")
    print(f"Average Consistency: {avg_consistency:.2%}")
    print(f"Average F1 with Skill: {avg_f1_with_skill:.2f}")

    # Go/No-Go Decision
    print("\n" + "="*80)
    print("GO/NO-GO DECISION")
    print("="*80)

    success_criteria = {
        "Quality Improvement ≥20%": avg_improvement >= 20,
        "Consistency ≥85%": avg_consistency >= 0.85,
        "Follows Instructions": avg_f1_with_skill >= 0.70
    }

    all_passed = all(success_criteria.values())

    for criterion, passed in success_criteria.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {criterion}")

    print("\n" + "="*80)
    if all_passed:
        print("✅ GO: Skills approach is validated. Proceed with Phase 1.")
    else:
        print("❌ NO-GO: Skills approach needs refinement or pivot to structured prompts.")
    print("="*80)

    return results, all_passed

if __name__ == "__main__":
    results, passed = run_phase0_validation()
```

**Tasks:**
1. Create test harness script
2. Implement skill loading
3. Implement LLM calling (with and without skill)
4. Implement metrics calculation
5. Implement consistency testing

**Success Criteria:**
- ✅ Test harness runs without errors
- ✅ Measures precision, recall, F1
- ✅ Tests consistency across 3 runs
- ✅ Compares with/without skill
- ✅ Outputs clear go/no-go recommendation

---

### Phase 0.4: Run Validation and Decide (Day -1, Afternoon)

**Task:** Execute validation tests and make go/no-go decision

**Execution:**
```bash
# Setup environment
python -m venv venv
source venv/bin/activate
pip install langchain langchain-anthropic python-dotenv

# Set API key
export ANTHROPIC_API_KEY=your_key_here

# Run validation
python tests/test_phase0_skills.py
```

**Expected Output:**
```
================================================================================
PHASE 0: SKILLS ARCHITECTURE VALIDATION
================================================================================

--- Testing: phase0_simple_spec ---
Extracting WITH skill...
Extracting WITHOUT skill (baseline)...
Testing consistency (3 runs)...

Results for phase0_simple_spec:
  WITH Skill    - Precision: 0.95, Recall: 1.00, F1: 0.97
  WITHOUT Skill - Precision: 0.80, Recall: 0.90, F1: 0.85
  Improvement: 14.1%
  Consistency: 92%

[... similar for medium and complex specs ...]

================================================================================
OVERALL ASSESSMENT
================================================================================

Average Improvement: 25.3%
Average Consistency: 88%
Average F1 with Skill: 0.89

================================================================================
GO/NO-GO DECISION
================================================================================

✅ PASS - Quality Improvement ≥20%
✅ PASS - Consistency ≥85%
✅ PASS - Follows Instructions

================================================================================
✅ GO: Skills approach is validated. Proceed with Phase 1.
================================================================================
```

**Decision Matrix:**

| Scenario | Avg Improvement | Consistency | Action |
|----------|----------------|-------------|--------|
| **Best Case** | ≥30% | ≥90% | ✅ GO - Skills work great, proceed confidently |
| **Good Case** | ≥20% | ≥85% | ✅ GO - Skills work well, proceed as planned |
| **Marginal** | 10-20% | 75-85% | ⚠️ REFINE - Improve skill, re-test |
| **Failure** | <10% | <75% | ❌ PIVOT - Use structured prompts instead |

**Pivot Strategy (if validation fails):**

If skills don't meet success criteria:
1. **Option A:** Refine skill and re-test (1 day)
   - Add more examples
   - Clarify methodology
   - Simplify instructions
2. **Option B:** Hybrid approach (use skills + few-shot examples)
3. **Option C:** Pivot to structured prompts with function calling
   - Define Pydantic schemas for outputs
   - Use JSON mode for LLM calls
   - Hardcode methodology in system prompts

**Tasks:**
1. Run validation script
2. Analyze results
3. Make go/no-go decision
4. Document findings
5. If GO → Proceed to Phase 1
6. If NO-GO → Execute pivot strategy

**Success Criteria:**
- ✅ Validation completes without errors
- ✅ Clear metrics for all test specs
- ✅ Go/no-go decision documented
- ✅ If NO-GO, pivot strategy selected

---

## Phase 1: Foundation (Week 1)

**Goal:** Set up project structure, implement state management, and create first node

### Phase 1.1: Project Setup (Days 1-2)

**Deliverables:**
- [ ] Project directory structure
- [ ] Virtual environment with dependencies
- [ ] Configuration management
- [ ] Logging and observability setup

**Directory Structure:**
```
requirements_decomposition_langgraph/
├── README.md
├── requirements.txt
├── .env.example
├── config/
│   ├── __init__.py
│   ├── llm_config.py          # LLM provider configs
│   └── settings.py            # App settings
├── src/
│   ├── __init__.py
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── state.py           # State schema definitions
│   │   ├── graph.py           # LangGraph definition
│   │   └── nodes.py           # Node implementations
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py      # Base agent class
│   │   └── specialized_agents.py  # Specific agent implementations
│   ├── skills/
│   │   ├── __init__.py
│   │   └── skill_loader.py    # Skills loading utility
│   └── utils/
│       ├── __init__.py
│       ├── document_parser.py # Parse PDF/DOCX
│       ├── quality_checker.py # Quality validation logic
│       └── output_generator.py # Document generation
├── skills/                     # Skills library
│   ├── requirements-extraction/
│   │   └── SKILL.md
│   ├── system-analysis/
│   │   └── SKILL.md
│   ├── requirements-decomposition/
│   │   └── SKILL.md
│   └── requirements-quality-validation/
│       └── SKILL.md
├── tests/
│   ├── __init__.py
│   ├── test_nodes.py
│   ├── test_agents.py
│   └── test_integration.py
├── examples/
│   ├── sample_spec.md
│   └── expected_output.md
└── outputs/                    # Generated artifacts
```

**Key Dependencies:**
```txt
langgraph>=0.0.40
langchain>=0.1.0
langchain-openai>=0.0.5
langchain-anthropic>=0.1.0
langchain-google-genai>=0.0.5
python-docx>=1.0.0
PyPDF2>=3.0.0
pydantic>=2.5.0
python-dotenv>=1.0.0
pytest>=7.4.0
rich>=13.0.0  # For nice console output
```

**Tasks:**
1. Create directory structure
2. Set up virtual environment
3. Install dependencies
4. Configure LangSmith for observability (optional but recommended)
5. Create basic logging infrastructure
6. Write configuration loader

**Success Criteria:**
- ✅ Can import all packages without errors
- ✅ Configuration loads from .env file
- ✅ Logging outputs to console and file
- ✅ pytest discovers and runs basic tests

---

### Phase 1.2: State Schema Implementation (Day 3)

**Deliverables:**
- [ ] Complete state schema with type hints
- [ ] State validation logic
- [ ] State serialization/deserialization
- [ ] Unit tests for state management

**Implementation: `src/graph/state.py`**

```python
from typing import TypedDict, List, Optional, Literal, Annotated
from pydantic import BaseModel, Field, validator
import operator

# Pydantic models for validation
class Requirement(BaseModel):
    id: str = Field(..., description="Unique requirement identifier")
    text: str = Field(..., min_length=10, description="Requirement text")
    type: Literal["functional", "performance", "constraint", "interface"]
    parent_id: Optional[str] = None
    subsystem: Optional[str] = None
    rationale: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    
    @validator('id')
    def validate_id_format(cls, v):
        # Enforce naming convention: SYS-FUNC-001
        if not v or len(v.split('-')) < 3:
            raise ValueError("ID must follow format: {SYSTEM}-{TYPE}-{NUM}")
        return v

class DecompositionStrategy(BaseModel):
    approach: Literal["functional", "architectural", "hybrid"]
    subsystem_list: List[str]
    allocation_rules: str
    templates: dict = Field(default_factory=dict)

class QualityIssue(BaseModel):
    requirement_id: str
    severity: Literal["critical", "major", "minor"]
    category: str
    description: str
    suggestion: str

class QualityMetrics(BaseModel):
    overall_score: float = Field(ge=0.0, le=1.0)
    completeness: float = Field(ge=0.0, le=1.0)
    clarity: float = Field(ge=0.0, le=1.0)
    testability: float = Field(ge=0.0, le=1.0)
    traceability: float = Field(ge=0.0, le=1.0)
    issues: List[QualityIssue] = Field(default_factory=list)

# LangGraph State (uses TypedDict for graph)
class DecompositionState(TypedDict):
    # Input
    spec_document_path: str
    target_subsystem: str
    knowledge_base_path: Optional[str]
    review_before_decompose: bool  # NEW: Optional pre-decomposition review

    # Intermediate results
    extracted_requirements: Annotated[List[dict], operator.add]
    system_context: str
    decomposition_strategy: Optional[dict]  # BINDING CONTRACT - must be followed exactly
    subsystem_requirements: Annotated[List[dict], operator.add]

    # Quality tracking & refinement feedback
    quality_metrics: Optional[dict]
    validation_passed: bool
    iteration_count: int
    max_iterations: int
    refinement_feedback: Optional[str]  # NEW: Specific feedback for improvement
    validation_issues: List[dict]  # NEW: Detailed quality issues
    previous_attempt: Optional[List[dict]]  # NEW: Last decomposition for comparison

    # Human review
    human_feedback: Optional[str]
    requires_human_review: bool

    # Output
    final_document_path: Optional[str]
    traceability_matrix: Optional[dict]

    # Error handling & fallback tracking
    errors: Annotated[List[str], operator.add]
    fallback_count: int  # NEW: Track LLM fallback frequency
    error_log: List[dict]  # NEW: Detailed error tracking for analysis
```

**Tasks:**
1. Define all state types using Pydantic for validation
2. Add validators for requirement ID format, score ranges
3. Implement state serialization (to/from JSON)
4. Write unit tests for state validation
5. Create helper functions for state manipulation

**Success Criteria:**
- ✅ State schema passes type checking (mypy)
- ✅ Invalid states raise appropriate validation errors
- ✅ State can be serialized/deserialized without data loss
- ✅ All unit tests pass

---

### Phase 1.3: First Node - Requirements Extraction (Days 4-5)

**Deliverables:**
- [ ] Document parser utility (PDF/DOCX → text)
- [ ] Requirements extraction skill (SKILL.md)
- [ ] Base agent implementation
- [ ] Requirements extraction node
- [ ] Integration test with sample document

**Implementation: `skills/requirements-extraction/SKILL.md`**

```markdown
# Requirements Extraction Methodology

## Purpose
Extract and categorize requirements from system specification documents.

## Input
- System specification document (text)
- Optional: System architecture context

## Process

### 1. Document Analysis
- Identify requirement-bearing sections
- Distinguish requirements from:
  - Background information
  - Explanatory text
  - Examples
  - Non-normative content

### 2. Requirement Identification
Look for requirement indicators:
- Modal verbs: "shall", "must", "should", "may"
- Imperative statements
- Quantified performance criteria
- Constraint statements

### 3. Categorization
Classify each requirement:
- **Functional:** What the system does
- **Performance:** How well it does it (speed, accuracy, capacity)
- **Constraint:** Limitations and restrictions
- **Interface:** External system interactions

### 4. Extraction Format
Each requirement must include:
- Unique ID (temporary: EXTRACT-{TYPE}-{NUM})
- Full text (exact quote from source)
- Type classification
- Source reference (section/page number)

### 5. Quality Checks
Each extracted requirement should:
✓ Be a single, atomic statement
✓ Contain a clear subject and action
✓ Avoid vague language ("adequate", "user-friendly")
✓ Be unambiguous

## Output Format
```json
{
  "id": "EXTRACT-FUNC-001",
  "text": "The system shall process train location updates within 100ms",
  "type": "performance",
  "source_reference": "Section 3.2.1",
  "confidence": 0.95
}
```

## Common Pitfalls
- Extracting descriptive text as requirements
- Splitting compound requirements incorrectly
- Missing implicit requirements
- Over-extracting (treating everything as a requirement)
```

**Implementation: `src/graph/nodes.py` (Extraction Node)**

```python
from langchain_openai import ChatOpenAI
from src.agents.specialized_agents import RequirementsAnalystAgent
from src.utils.document_parser import parse_document
from src.skills.skill_loader import load_skill

def requirements_extraction_node(state: DecompositionState) -> dict:
    """
    Extract requirements from specification document.
    
    Returns state updates with extracted requirements.
    """
    try:
        # Parse document
        doc_text = parse_document(state["spec_document_path"])
        
        # Load skill
        extraction_skill = load_skill("requirements-extraction")
        
        # Initialize agent with skill
        agent = RequirementsAnalystAgent(
            model="gpt-4o",
            temperature=0.1,
            skill_content=extraction_skill
        )
        
        # Extract requirements
        requirements = agent.extract_requirements(
            document_text=doc_text,
            target_subsystem=state.get("target_subsystem", "")
        )
        
        return {
            "extracted_requirements": requirements,
            "iteration_count": state.get("iteration_count", 0) + 1
        }
        
    except Exception as e:
        return {
            "errors": [f"Extraction failed: {str(e)}"],
            "requires_human_review": True
        }
```

**Tasks:**
1. Implement document parser (PDF/DOCX → text)
2. Write requirements extraction skill
3. Create base agent class with skill loading
4. Implement RequirementsAnalystAgent
5. Build extraction node with error handling
6. Write integration test with sample specification
7. Add logging and debugging output

**Success Criteria:**
- ✅ Parser handles PDF and DOCX files
- ✅ Agent successfully loads and uses skill
- ✅ Extracts ≥90% of requirements from test document
- ✅ Correctly categorizes requirement types
- ✅ Generates valid requirement IDs
- ✅ Integration test passes

---

## Phase 2: Core Decomposition Logic (Week 2)

**Goal:** Implement analyze and decompose nodes with quality validation

### Phase 2.1: System Analysis Node (Days 6-7)

**Deliverables:**
- [ ] System analysis skill
- [ ] Decomposition strategy skill
- [ ] System Architect agent
- [ ] Analysis node implementation
- [ ] Strategy validation logic

**Implementation: `skills/system-analysis/SKILL.md`**

```markdown
# System Analysis and Decomposition Strategy

## Purpose
Analyze system architecture and develop optimal decomposition strategy.

## Input
- Extracted requirements list
- System architecture documentation (optional)
- Target subsystem specification

## Process

### 1. Architecture Analysis
Identify:
- System boundaries
- Major subsystems
- Interface points
- Dependencies

### 2. Requirement Clustering
Group requirements by:
- Functional area
- Subsystem allocation
- Dependency relationships
- Performance characteristics

### 3. Decomposition Approach Selection

**Functional Decomposition:**
- Use when: Clear functional boundaries exist
- Allocate by: What each subsystem does
- Example: "Train Tracking" vs "Dispatch Planning"

**Architectural Decomposition:**
- Use when: Physical/logical architecture is primary driver
- Allocate by: Where functionality resides
- Example: "Server-side" vs "Client-side"

**Hybrid Decomposition:**
- Use when: Both functional and architectural boundaries matter
- Combines both approaches

### 4. Allocation Rules
Define clear rules:
```
IF requirement involves real-time data processing
  THEN allocate to Backend subsystem
ELSE IF requirement involves user interaction
  THEN allocate to Frontend subsystem
```

### 5. Template Definition
Create requirement templates for target subsystem:
```
Functional: "{Subsystem} shall {action} {object} {condition}"
Performance: "{Subsystem} shall {action} within {time/accuracy}"
Interface: "{Subsystem} shall {send/receive} {data} to/from {external system}"
```

## Output
DecompositionStrategy containing:
- Selected approach with rationale
- Subsystem list
- Allocation rules (pseudo-code)
- Requirement templates
```

**Implementation: `src/graph/nodes.py` (Analysis Node)**

```python
def system_analysis_node(state: DecompositionState) -> dict:
    """
    Analyze system context and develop decomposition strategy.
    """
    try:
        # Load skills
        analysis_skill = load_skill("system-analysis")
        strategy_skill = load_skill("decomposition-strategy")
        
        # Initialize agent
        agent = SystemArchitectAgent(
            model="gemini-1.5-pro",
            temperature=0.2,
            skill_content=analysis_skill + "\n\n" + strategy_skill
        )
        
        # Analyze and strategize
        strategy = agent.develop_strategy(
            requirements=state["extracted_requirements"],
            target_subsystem=state["target_subsystem"],
            architecture_context=state.get("system_context", "")
        )
        
        return {
            "decomposition_strategy": strategy,
            "system_context": strategy.get("architecture_summary", "")
        }
        
    except Exception as e:
        return {
            "errors": [f"Analysis failed: {str(e)}"],
            "requires_human_review": True
        }
```

**Tasks:**
1. Write system analysis skill
2. Write decomposition strategy skill
3. Implement SystemArchitectAgent
4. Build analysis node
5. Add strategy validation logic
6. Test with various requirement sets

**Success Criteria:**
- ✅ Selects appropriate decomposition approach
- ✅ Generates clear allocation rules
- ✅ Creates valid requirement templates
- ✅ Strategy is executable by decomposition node

---

### Phase 2.2: Requirements Decomposition Node (Days 8-10)

**Deliverables:**
- [ ] Requirements decomposition skill
- [ ] Requirements Engineer agent
- [ ] Decomposition node with traceability
- [ ] Quality validation integration

**Implementation: `skills/requirements-decomposition/SKILL.md`**

```markdown
# Requirements Decomposition Methodology

## Purpose
Transform system-level requirements into detailed subsystem requirements.

## Input
- System requirements list
- Decomposition strategy
- Target subsystem

## Process

### 1. Requirement Selection
For each system requirement:
- Check if it applies to target subsystem
- Apply allocation rules from strategy

### 2. Decomposition Patterns

**Direct Allocation (1:1):**
System: "The system shall authenticate users"
Subsystem: "The Auth Service shall authenticate users via OAuth2"

**Budget Allocation (1:N for performance):**
System: "The system shall process 10,000 requests/second"
Subsystem 1: "API Gateway shall process 5,000 requests/second"
Subsystem 2: "Backend shall process 5,000 requests/second"

**Functional Breakdown (1:N):**
System: "The system shall manage train schedules"
Subsystem Reqs:
- "Train Management shall create train schedules"
- "Train Management shall update train schedules"
- "Train Management shall validate schedule conflicts"

### 3. Requirement Formulation
Use templates from strategy:
- Apply subsystem-specific terminology
- Add implementation constraints
- Specify acceptance criteria

### 4. Traceability
Each child requirement MUST:
- Reference parent requirement ID
- Maintain semantic link to parent
- Include allocation rationale

### 5. Quality Self-Check
Each requirement should:
✓ Be implementable by target subsystem
✓ Have clear acceptance criteria
✓ Be independently testable
✓ Not duplicate other requirements
✓ Use precise, measurable language

## Output Format
```json
{
  "id": "TM-FUNC-001",
  "text": "Train Management shall create train schedules with departure times, arrival times, and station sequences",
  "type": "functional",
  "parent_id": "SYS-FUNC-015",
  "subsystem": "Train Management",
  "rationale": "Direct allocation based on functional decomposition",
  "acceptance_criteria": "System creates valid schedule with all required fields; validates against business rules"
}
```

## Common Pitfalls
- Copying parent requirement verbatim (add subsystem context)
- Vague acceptance criteria
- Missing traceability links
- Over-decomposing (too granular)
- Under-decomposing (too high-level)
```

**Implementation: `src/graph/nodes.py` (Decomposition Node)**

```python
def requirements_decomposition_node(state: DecompositionState) -> dict:
    """
    Decompose system requirements into subsystem requirements.
    """
    try:
        # Load skill
        decomposition_skill = load_skill("requirements-decomposition")
        
        # Initialize agent
        agent = RequirementsEngineerAgent(
            model="gpt-4o",
            temperature=0.0,
            skill_content=decomposition_skill
        )
        
        # Decompose requirements
        subsystem_reqs = agent.decompose_requirements(
            system_requirements=state["extracted_requirements"],
            strategy=state["decomposition_strategy"],
            target_subsystem=state["target_subsystem"]
        )
        
        # Build traceability matrix
        traceability = build_traceability_matrix(
            parent_reqs=state["extracted_requirements"],
            child_reqs=subsystem_reqs
        )
        
        return {
            "subsystem_requirements": subsystem_reqs,
            "traceability_matrix": traceability
        }
        
    except Exception as e:
        return {
            "errors": [f"Decomposition failed: {str(e)}"],
            "requires_human_review": True
        }
```

**Tasks:**
1. Write decomposition skill with patterns
2. Implement RequirementsEngineerAgent
3. Build decomposition node
4. Implement traceability matrix builder
5. Add self-validation logic
6. Test with various requirement types

**Success Criteria:**
- ✅ Decomposes all applicable system requirements
- ✅ Maintains correct parent-child traceability
- ✅ Generates valid requirement IDs
- ✅ Includes clear acceptance criteria
- ✅ No duplicate requirements

---

### Phase 2.3: Quality Validation Node (Days 11-12)

**Deliverables:**
- [ ] Requirements quality validation skill
- [ ] Quality checker utility
- [ ] QA Agent implementation
- [ ] Validation node with scoring
- [ ] Quality gate logic

**Implementation: `skills/requirements-quality-validation/SKILL.md`**

```markdown
# Requirements Quality Validation

## Purpose
Validate decomposed requirements against quality standards.

## Quality Criteria

### 1. Completeness (25%)
- All parent requirements have child allocations
- No orphaned child requirements
- Coverage matrix is complete

### 2. Clarity (25%)
- Requirement uses precise language
- No ambiguous terms ("user-friendly", "adequate", "fast")
- Single interpretation possible
- Clear subject, action, object

### 3. Testability (25%)
- Measurable acceptance criteria
- Observable behavior specified
- Test approach is clear
- Pass/fail conditions defined

### 4. Traceability (25%)
- Valid parent-child links
- Rationale provided
- Subsystem assignment correct
- ID format follows convention

## Validation Process

### Step 1: Automated Checks
Run programmatic validation:
```python
def validate_requirement(req):
    checks = {
        "has_id": bool(req.get("id")),
        "has_text": len(req.get("text", "")) > 10,
        "has_parent": bool(req.get("parent_id")),
        "has_criteria": bool(req.get("acceptance_criteria")),
        "id_format_valid": validate_id_format(req["id"])
    }
    return checks
```

### Step 2: LLM-Based Quality Assessment
For each requirement, evaluate:
- **Clarity Score (0-1):** Is the requirement unambiguous?
- **Testability Score (0-1):** Can it be verified?
- **Completeness Score (0-1):** Does it include necessary details?

### Step 3: Issue Identification
Flag requirements with:
- **Critical:** Missing mandatory fields, invalid traceability
- **Major:** Unclear acceptance criteria, ambiguous language
- **Minor:** Style issues, suggestions for improvement

### Step 4: Overall Scoring
```
Overall Score = (Completeness + Clarity + Testability + Traceability) / 4
```

**Quality Gate Threshold:** 0.80

## Output Format
```json
{
  "overall_score": 0.85,
  "completeness": 0.90,
  "clarity": 0.82,
  "testability": 0.88,
  "traceability": 0.80,
  "issues": [
    {
      "requirement_id": "TM-FUNC-003",
      "severity": "major",
      "category": "clarity",
      "description": "Uses ambiguous term 'quickly'",
      "suggestion": "Specify maximum time constraint (e.g., 'within 500ms')"
    }
  ]
}
```

## Decision Logic
- Score ≥ 0.80 AND no critical issues: **PASS**
- Score < 0.80 OR has critical issues: **FAIL → Revision needed**
- Score < 0.60: **FAIL → Human review required**
```

**Implementation: `src/graph/nodes.py` (Validation Node)**

```python
def quality_validation_node(state: DecompositionState) -> dict:
    """
    Validate all requirements against quality standards.
    """
    try:
        # Load skill
        validation_skill = load_skill("requirements-quality-validation")
        
        # Initialize utilities
        quality_checker = QualityChecker()
        
        # Initialize agent
        agent = QualityAssuranceAgent(
            model="claude-sonnet-4-20250514",
            temperature=0.0,
            skill_content=validation_skill
        )
        
        # Run automated checks
        automated_results = quality_checker.validate_requirements(
            requirements=state["subsystem_requirements"],
            traceability=state["traceability_matrix"]
        )
        
        # Run LLM-based quality assessment
        llm_assessment = agent.assess_quality(
            requirements=state["subsystem_requirements"],
            automated_results=automated_results
        )
        
        # Compute quality metrics
        metrics = compute_quality_metrics(
            automated_results=automated_results,
            llm_assessment=llm_assessment
        )
        
        # Apply quality gate
        validation_passed = (
            metrics["overall_score"] >= 0.80 and
            not has_critical_issues(metrics["issues"])
        )
        
        # Determine if human review needed
        requires_human = (
            metrics["overall_score"] < 0.60 or
            state.get("iteration_count", 0) >= state.get("max_iterations", 3)
        )
        
        return {
            "quality_metrics": metrics,
            "validation_passed": validation_passed,
            "requires_human_review": requires_human
        }
        
    except Exception as e:
        return {
            "errors": [f"Validation failed: {str(e)}"],
            "requires_human_review": True
        }
```

**Tasks:**
1. Write quality validation skill
2. Implement automated quality checker utility
3. Implement QualityAssuranceAgent
4. Build validation node with scoring
5. Implement quality gate logic
6. Add issue categorization and reporting

**Success Criteria:**
- ✅ Detects incomplete requirements
- ✅ Identifies ambiguous language
- ✅ Validates traceability links
- ✅ Computes accurate quality scores
- ✅ Quality gate correctly routes to pass/fail

---

## Phase 3: Graph Assembly and Control Flow (Week 3)

**Goal:** Assemble complete graph with conditional routing and human-in-loop

### Phase 3.1: Graph Construction (Days 13-14)

**Deliverables:**
- [ ] Complete graph definition
- [ ] Conditional routing logic
- [ ] Human review integration
- [ ] State persistence
- [ ] Graph visualization

**Implementation: `src/graph/graph.py`**

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from src.graph.state import DecompositionState
from src.graph.nodes import (
    requirements_extraction_node,
    system_analysis_node,
    requirements_decomposition_node,
    quality_validation_node,
    documentation_generation_node,
    human_review_node
)

def create_decomposition_graph():
    """
    Create the requirements decomposition LangGraph.
    """
    
    # Initialize graph with state schema
    workflow = StateGraph(DecompositionState)
    
    # Add nodes
    workflow.add_node("extract", requirements_extraction_node)
    workflow.add_node("analyze", system_analysis_node)
    workflow.add_node("decompose", requirements_decomposition_node)
    workflow.add_node("validate", quality_validation_node)
    workflow.add_node("human_review", human_review_node)
    workflow.add_node("document", documentation_generation_node)
    
    # Set entry point
    workflow.set_entry_point("extract")
    
    # Add sequential edges
    workflow.add_edge("extract", "analyze")
    workflow.add_edge("analyze", "decompose")
    workflow.add_edge("decompose", "validate")
    
    # Add conditional routing after validation
    workflow.add_conditional_edges(
        "validate",
        route_after_validation,
        {
            "pass": "document",
            "revise": "decompose",
            "human_review": "human_review"
        }
    )
    
    # Human review can go back to decompose or forward to document
    workflow.add_conditional_edges(
        "human_review",
        route_after_human_review,
        {
            "approved": "document",
            "revise": "decompose"
        }
    )
    
    # Document generation ends the workflow
    workflow.add_edge("document", END)
    
    # Add state persistence (checkpointing)
    memory = SqliteSaver.from_conn_string(":memory:")
    
    return workflow.compile(checkpointer=memory)

def route_after_validation(state: DecompositionState) -> str:
    """
    Route based on validation results.
    """
    # Check for fatal errors
    if state.get("errors") and len(state["errors"]) > 0:
        return "human_review"
    
    # Check iteration limit
    if state.get("iteration_count", 0) >= state.get("max_iterations", 3):
        return "human_review"
    
    # Check quality gate
    if state.get("validation_passed", False):
        return "pass"
    
    # Check if human review explicitly requested
    if state.get("requires_human_review", False):
        return "human_review"
    
    # Default: revise
    return "revise"

def route_after_human_review(state: DecompositionState) -> str:
    """
    Route based on human decision.
    """
    feedback = state.get("human_feedback", "").lower()
    
    if "approve" in feedback or "accept" in feedback:
        return "approved"
    else:
        return "revise"
```

**Tasks:**
1. Implement complete graph structure
2. Add all nodes to graph
3. Implement conditional routing functions
4. Add state persistence (checkpointing)
5. Create graph visualization utility
6. Test graph execution end-to-end

**Success Criteria:**
- ✅ Graph compiles without errors
- ✅ All nodes are reachable
- ✅ Conditional routing works correctly
- ✅ State persists across interrupts
- ✅ Can visualize graph structure

---

### Phase 3.2: Human-in-the-Loop (Days 15-16)

**Deliverables:**
- [ ] Human review node implementation
- [ ] Interactive CLI for review
- [ ] Feedback integration
- [ ] Resume from checkpoint

**Implementation: `src/graph/nodes.py` (Human Review Node)**

```python
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def human_review_node(state: DecompositionState) -> dict:
    """
    Pause for human review and feedback.
    
    In production, this would integrate with a UI.
    For MVP, uses CLI interaction.
    """
    
    console.print("\n" + "="*80, style="bold blue")
    console.print("HUMAN REVIEW REQUIRED", style="bold yellow", justify="center")
    console.print("="*80 + "\n", style="bold blue")
    
    # Display quality metrics
    metrics = state.get("quality_metrics", {})
    
    metrics_table = Table(title="Quality Metrics")
    metrics_table.add_column("Metric", style="cyan")
    metrics_table.add_column("Score", style="magenta")
    metrics_table.add_column("Status", style="green")
    
    for metric, value in metrics.items():
        if isinstance(value, float):
            status = "✓ PASS" if value >= 0.8 else "✗ FAIL"
            metrics_table.add_row(
                metric.replace("_", " ").title(),
                f"{value:.2f}",
                status
            )
    
    console.print(metrics_table)
    
    # Display issues
    issues = metrics.get("issues", [])
    if issues:
        console.print(f"\n[bold red]Found {len(issues)} issues:[/bold red]")
        for i, issue in enumerate(issues[:5], 1):  # Show top 5
            console.print(f"\n{i}. [{issue['severity'].upper()}] {issue['description']}")
            console.print(f"   Suggestion: {issue['suggestion']}")
    
    # Display iteration info
    iteration = state.get("iteration_count", 0)
    max_iter = state.get("max_iterations", 3)
    console.print(f"\n[yellow]Iteration {iteration}/{max_iter}[/yellow]")
    
    # Get human decision
    console.print("\n" + "-"*80)
    console.print("[bold]Review Options:[/bold]")
    console.print("  1. [green]Approve[/green] - Accept requirements as-is")
    console.print("  2. [yellow]Revise[/yellow] - Send back for revision with feedback")
    console.print("  3. [blue]View Details[/blue] - See specific requirements")
    
    while True:
        choice = console.input("\n[bold cyan]Enter choice (1-3): [/bold cyan]")
        
        if choice == "1":
            feedback = "approved"
            break
        elif choice == "2":
            feedback = console.input("\n[yellow]Enter revision guidance: [/yellow]")
            break
        elif choice == "3":
            display_requirements_detail(state["subsystem_requirements"])
            continue
        else:
            console.print("[red]Invalid choice. Try again.[/red]")
    
    return {
        "human_feedback": feedback,
        "requires_human_review": False
    }

def display_requirements_detail(requirements: list):
    """Display detailed requirement information."""
    console.print("\n[bold]Subsystem Requirements:[/bold]\n")
    
    for req in requirements[:10]:  # Show first 10
        panel = Panel(
            f"[cyan]ID:[/cyan] {req['id']}\n"
            f"[cyan]Type:[/cyan] {req['type']}\n"
            f"[cyan]Text:[/cyan] {req['text']}\n"
            f"[cyan]Parent:[/cyan] {req.get('parent_id', 'N/A')}\n"
            f"[cyan]Criteria:[/cyan] {req.get('acceptance_criteria', 'N/A')}",
            title=f"Requirement {req['id']}",
            border_style="blue"
        )
        console.print(panel)
```

**Tasks:**
1. Implement human review node with rich CLI
2. Create requirement detail viewer
3. Implement feedback capture
4. Test interrupt/resume workflow
5. Add state inspection utilities

**Success Criteria:**
- ✅ Human review pauses execution
- ✅ Displays clear quality metrics
- ✅ Captures human feedback
- ✅ Can resume from saved state
- ✅ Feedback influences next iteration

---

### Phase 3.3: Documentation Generation (Day 17)

**Deliverables:**
- [ ] Documentation generation node
- [ ] Output formatting utilities
- [ ] Traceability matrix generator
- [ ] Professional markdown templates

**Implementation: `src/graph/nodes.py` (Documentation Node)**

```python
from src.utils.output_generator import (
    generate_requirements_document,
    generate_traceability_matrix,
    generate_quality_report
)

def documentation_generation_node(state: DecompositionState) -> dict:
    """
    Generate final documentation package.
    """
    try:
        output_dir = "outputs"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate requirements document
        req_doc_path = generate_requirements_document(
            requirements=state["subsystem_requirements"],
            subsystem=state["target_subsystem"],
            output_path=f"{output_dir}/requirements_{timestamp}.md"
        )
        
        # Generate traceability matrix
        trace_path = generate_traceability_matrix(
            traceability=state["traceability_matrix"],
            output_path=f"{output_dir}/traceability_{timestamp}.md"
        )
        
        # Generate quality report
        quality_path = generate_quality_report(
            metrics=state["quality_metrics"],
            output_path=f"{output_dir}/quality_report_{timestamp}.md"
        )
        
        console.print(f"\n[green]✓ Documentation generated:[/green]")
        console.print(f"  - Requirements: {req_doc_path}")
        console.print(f"  - Traceability: {trace_path}")
        console.print(f"  - Quality Report: {quality_path}")
        
        return {
            "final_document_path": req_doc_path
        }
        
    except Exception as e:
        return {
            "errors": [f"Documentation generation failed: {str(e)}"]
        }
```

**Tasks:**
1. Implement documentation generator
2. Create markdown templates
3. Build traceability matrix formatter
4. Add quality report generator
5. Test output formatting

**Success Criteria:**
- ✅ Generates professional markdown documents
- ✅ Traceability matrix is clear and complete
- ✅ Quality report includes all metrics
- ✅ Documents are stakeholder-ready

---

## Phase 4: Testing, Optimization, and Deployment (Week 4)

**Goal:** Comprehensive testing, performance optimization, and deployment readiness

### Phase 4.1: Integration Testing (Days 18-19)

**Deliverables:**
- [ ] End-to-end integration tests
- [ ] Test fixtures and sample data
- [ ] Performance benchmarks
- [ ] Error scenario tests

**Test Cases:**

```python
# tests/test_integration.py

def test_happy_path_decomposition():
    """Test successful decomposition without intervention."""
    
    # Setup
    initial_state = {
        "spec_document_path": "examples/sample_spec.md",
        "target_subsystem": "Train Management",
        "iteration_count": 0,
        "max_iterations": 3,
        "validation_passed": False
    }
    
    # Execute
    graph = create_decomposition_graph()
    final_state = graph.invoke(initial_state)
    
    # Assert
    assert final_state["validation_passed"] == True
    assert len(final_state["subsystem_requirements"]) > 0
    assert final_state["quality_metrics"]["overall_score"] >= 0.8
    assert final_state["final_document_path"] is not None

def test_quality_gate_failure_and_revision():
    """Test revision loop when quality gate fails."""
    
    # Setup with requirements that will fail quality
    initial_state = {
        "spec_document_path": "examples/poor_quality_spec.md",
        "target_subsystem": "Train Management",
        "iteration_count": 0,
        "max_iterations": 3
    }
    
    # Execute
    graph = create_decomposition_graph()
    
    # Should trigger at least one revision
    final_state = graph.invoke(initial_state)
    
    # Assert
    assert final_state["iteration_count"] > 1
    # Eventually should pass or require human review
    assert (
        final_state["validation_passed"] == True or
        final_state["requires_human_review"] == True
    )

def test_human_review_interrupt():
    """Test that human review properly interrupts execution."""
    
    initial_state = {
        "spec_document_path": "examples/sample_spec.md",
        "target_subsystem": "Train Management",
        "iteration_count": 0,
        "max_iterations": 1,  # Force human review quickly
        "validation_passed": False
    }
    
    graph = create_decomposition_graph()
    
    # Should interrupt at human review node
    # (In actual test, mock the human input)
    
def test_error_handling():
    """Test graceful error handling."""
    
    initial_state = {
        "spec_document_path": "nonexistent_file.md",
        "target_subsystem": "Train Management",
        "iteration_count": 0,
        "max_iterations": 3
    }
    
    graph = create_decomposition_graph()
    final_state = graph.invoke(initial_state)
    
    # Should capture error and request human review
    assert len(final_state["errors"]) > 0
    assert final_state["requires_human_review"] == True
```

**Tasks:**
1. Write comprehensive integration tests
2. Create test fixtures (sample specifications)
3. Implement test mocks for LLM calls (cost control)
4. Add performance benchmarks
5. Test error scenarios and edge cases
6. Measure end-to-end execution time

**Success Criteria:**
- ✅ All integration tests pass
- ✅ Happy path completes successfully
- ✅ Quality gate revision loop works
- ✅ Error handling is graceful
- ✅ End-to-end execution < 5 minutes for typical spec

---

### Phase 4.2: Optimization and Observability (Days 20-21)

**Deliverables:**
- [ ] LangSmith integration for tracing
- [ ] Cost tracking and optimization
- [ ] Caching for repeated operations
- [ ] Performance profiling
- [ ] Monitoring dashboard setup

**Optimization Strategies:**

```python
# config/llm_config.py

LLM_COST_OPTIMIZATION = {
    "extract": {
        "model": "gemini-1.5-pro",  # Cost-effective for extraction
        "temperature": 0.1,
        "fallback": "gpt-4o-mini"
    },
    "analyze": {
        "model": "gemini-1.5-pro",  # Good reasoning at lower cost
        "temperature": 0.2,
        "fallback": "claude-3-5-sonnet"
    },
    "decompose": {
        "model": "gpt-4o",  # Critical quality step
        "temperature": 0.0,
        "fallback": "gpt-4o-mini"
    },
    "validate": {
        "model": "claude-sonnet-4",  # Best quality assessment
        "temperature": 0.0,
        "fallback": "claude-3-5-haiku"
    }
}

# Implement caching
from langchain.cache import SQLiteCache
import langchain
langchain.llm_cache = SQLiteCache(database_path=".langchain.db")
```

**LangSmith Integration:**

```python
# Enable tracing
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "requirements-decomposition-mvp"

# Add custom callbacks for metrics
from langchain.callbacks import LangChainTracer

tracer = LangChainTracer(
    project_name="requirements-decomposition-mvp",
    tags=["mvp", "production"]
)
```

**Tasks:**
1. Integrate LangSmith tracing
2. Implement cost tracking per run
3. Add caching for repeated LLM calls
4. Profile execution time per node
5. Optimize slow nodes
6. Create monitoring dashboard

**Success Criteria:**
- ✅ Full execution traces in LangSmith
- ✅ Cost per run tracked accurately
- ✅ Caching reduces redundant LLM calls by 30%+
- ✅ Node execution times measured
- ✅ Total cost per decomposition < $2

---

### Phase 4.3: Documentation and Deployment (Days 22-23)

**Deliverables:**
- [ ] Complete README with setup instructions
- [ ] User guide with examples
- [ ] API documentation
- [ ] Docker containerization
- [ ] CI/CD pipeline (optional)

**README.md Structure:**

```markdown
# Requirements Decomposition System

AI-powered system for decomposing system-level requirements into 
subsystem requirements using LangGraph.

## Quick Start

\`\`\`bash
# Clone repository
git clone https://github.com/your-org/requirements-decomposition

# Setup environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run example
python main.py examples/sample_spec.md --subsystem "Train Management"
\`\`\`

## Usage

### Basic Execution
[Commands and examples]

### Human Review Mode
[How to use interactive review]

### Configuration
[LLM settings, quality thresholds]

## Architecture

[Diagram and explanation]

## Skills

[How skills work and how to customize]

## Development

[How to add new nodes, modify skills, extend functionality]
```

**Deployment Options:**

1. **Local CLI Tool** (MVP)
   - Python script execution
   - Local state persistence
   - Manual invocation

2. **Docker Container** (Production-ready)
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["python", "main.py"]
   ```

3. **API Service** (Future)
   - FastAPI wrapper
   - REST endpoints
   - Job queue integration

**Tasks:**
1. Write comprehensive README
2. Create user guide with examples
3. Document all configuration options
4. Create Dockerfile
5. Set up basic CI/CD (GitHub Actions)
6. Create deployment guide

**Success Criteria:**
- ✅ New user can set up and run in < 15 minutes
- ✅ All features documented
- ✅ Docker image builds successfully
- ✅ Examples run without errors

---

### Phase 4.4: MVP Review and Handoff (Days 24)

**Deliverables:**
- [ ] MVP demonstration
- [ ] Known limitations documented
- [ ] Roadmap for future enhancements
- [ ] Handoff documentation

**MVP Capabilities:**
✅ Extract requirements from specification documents  
✅ Analyze system architecture and develop strategy  
✅ Decompose system requirements to subsystem level  
✅ Validate quality with automated scoring  
✅ Support iterative refinement with quality gates  
✅ Enable human review at critical checkpoints  
✅ Generate professional documentation  
✅ Maintain complete traceability  
✅ Handle errors gracefully  
✅ Persist state across interrupts  

**Known Limitations:**
- Single subsystem decomposition only (no multi-subsystem optimization)
- Limited interface requirement handling (basic ICD integration)
- CLI-only interaction (no web UI)
- English language only
- Requires manual knowledge base setup

**Future Enhancements (Post-MVP):**
1. Multi-subsystem decomposition with interface optimization
2. Advanced ICD parsing and interface generation
3. Web-based UI for collaboration
4. Integration with Polarion/DOORS
5. Compliance checking (DO-178C, ISO 26262, etc.)
6. Multi-language support
7. Advanced analytics and metrics dashboard
8. Template library for common domains

---

## Success Metrics

### Technical Metrics
- ✅ **Quality Score:** ≥ 0.85 average for generated requirements
- ✅ **Traceability:** 100% parent-child coverage
- ✅ **Performance:** < 5 minutes end-to-end for typical specification
- ✅ **Cost:** < $2 per decomposition run
- ✅ **Reliability:** ≥ 95% success rate without errors

### Business Metrics
- ✅ **Time Savings:** 70% reduction vs. manual decomposition
- ✅ **Consistency:** Reduced variance in requirement quality
- ✅ **Scalability:** Can process 100+ system requirements
- ✅ **Usability:** Non-experts can use with < 1 hour training

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| LLM API outages | Medium | High | Implement fallback models, retry logic |
| Poor quality output | Medium | High | Multi-stage validation, human review gates |
| Cost overruns | Low | Medium | Caching, cost tracking, model optimization |
| Integration complexity | Low | Medium | Start simple, iterate based on feedback |
| Skill maintenance | Low | Low | Version control skills, document rationale |

---

## Appendix: Command Reference

### Running the System

```bash
# Basic execution
python main.py <spec_path> --subsystem "<subsystem_name>"

# With custom configuration
python main.py <spec_path> \
  --subsystem "Train Management" \
  --max-iterations 5 \
  --quality-threshold 0.85 \
  --knowledge-base ./knowledge_base

# Resume from checkpoint
python main.py --resume <checkpoint_id>

# Generate only (skip execution)
python main.py --from-state saved_state.json --document-only
```

### Viewing Results

```bash
# View generated documentation
cat outputs/requirements_<timestamp>.md

# View traceability matrix
cat outputs/traceability_<timestamp>.md

# View quality report
cat outputs/quality_report_<timestamp>.md
```

### Development Commands

```bash
# Run tests
pytest tests/ -v

# Run with profiling
python -m cProfile -o profile.stats main.py <spec_path>

# View LangSmith traces
# Visit: https://smith.langchain.com/
```

---

## Contact and Support

**Project Lead:** Michael Sweatt  
**Email:** mdsweatt@gmail.com  
**Website:** https://www.mikescorner.io/  

For questions, issues, or contributions, please refer to the project repository.

---

---

## Appendix B: Critical Implementation Requirements

### 1. Refinement Feedback Loop (MANDATORY)

**Problem:** Without feedback, iteration cannot improve quality.

**Solution:**
```python
# In validate node - generate specific feedback
if not validation_passed:
    feedback = generate_refinement_guidance(
        issues=metrics["issues"],
        requirements=state["subsystem_requirements"],
        strategy=state["decomposition_strategy"]
    )
    return {
        "refinement_feedback": feedback,  # Actionable instructions
        "validation_issues": metrics["issues"],
        "previous_attempt": state["subsystem_requirements"]
    }

# In decompose node - consume feedback
if state.get("refinement_feedback"):
    subsystem_reqs = agent.decompose_with_refinement(
        requirements=state["extracted_requirements"],
        strategy=state["decomposition_strategy"],
        previous_attempt=state.get("previous_attempt"),
        feedback=state["refinement_feedback"]  # Tell agent what to fix
    )
```

### 2. LLM Fallback with Error Taxonomy (MANDATORY)

**Error Classification:**
```python
class ErrorType(Enum):
    TRANSIENT = "transient"  # RateLimitError, TimeoutError, APIError
    CONTENT = "content"      # ValidationError, JSONDecodeError, ParseError
    FATAL = "fatal"          # AuthError, MissingResourceError

# Transient → Retry with exponential backoff (same model)
# Content → Switch to fallback model
# Fatal → Stop execution, human intervention
```

**Implementation:**
```python
class LLMFallbackHandler:
    def call_with_fallback(self, primary_model, fallback_model, prompt, max_retries=3):
        for attempt in range(max_retries):
            try:
                return primary_model.invoke(prompt)
            except Exception as e:
                error_type = self.classify_error(e)
                if error_type == ErrorType.TRANSIENT:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                elif error_type == ErrorType.CONTENT:
                    self.fallback_count += 1
                    return fallback_model.invoke(prompt)
                else:  # FATAL
                    raise
```

### 3. Binding Strategy Execution (MANDATORY)

**Requirement:** Decomposition strategy is 100% binding (not advisory).

**Implementation:**
```python
def requirements_decomposition_node(state: DecompositionState) -> dict:
    strategy = state["decomposition_strategy"]

    # Execute decomposition strictly following strategy
    subsystem_reqs = agent.decompose_requirements(
        requirements=state["extracted_requirements"],
        strategy=strategy,  # Must follow exactly
        strict_mode=True
    )

    # Validate strategy adherence
    adherence_check = validate_strategy_adherence(
        requirements=subsystem_reqs,
        strategy=strategy
    )

    if not adherence_check["passed"]:
        # Strategy violation is a BUG, not a quality issue
        return {
            "errors": [f"Agent violated strategy: {adherence_check['violations']}"],
            "requires_human_review": True
        }

    return {"subsystem_requirements": subsystem_reqs}
```

### 4. State Persistence Fix (MANDATORY)

**Problem:** Plan uses `:memory:` which doesn't persist to disk.

**Solution:**
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

# Checkpoint ID generation
def generate_checkpoint_id(state: DecompositionState) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    subsystem = state["target_subsystem"].replace(" ", "_")
    return f"{timestamp}_{subsystem}"
```

### 5. Pre-Decomposition Human Review (OPTIONAL BUT RECOMMENDED)

**Implementation:**
```python
# Add routing after analyze node
workflow.add_conditional_edges(
    "analyze",
    route_after_analysis,
    {
        "decompose": "decompose",
        "human_review": "human_review_extraction"  # Optional review
    }
)

def route_after_analysis(state: DecompositionState) -> str:
    if state.get("review_before_decompose", False):
        return "human_review"
    return "decompose"
```

---

## Appendix C: Phase 0 Success Criteria Summary

**Must Pass ALL Three:**
1. ✅ **Quality Improvement ≥20%** (F1 score with skill vs. without skill)
2. ✅ **Consistency ≥85%** (Agreement across 3 runs on same input)
3. ✅ **Follows Instructions** (F1 score ≥0.70 with skill)

**If Phase 0 Fails:**
- Option A: Refine skill (add examples, clarify steps) and re-test
- Option B: Hybrid approach (skills + few-shot examples)
- Option C: Pivot to structured prompts with Pydantic schemas

**Timeline Impact:**
- Phase 0 GO → 4-week implementation as planned
- Phase 0 refinement → +2-3 days
- Phase 0 pivot → +1 week (architecture changes needed)

---

**END OF IMPLEMENTATION PLAN**
