# Requirements Quality Validation Methodology

## Purpose
Assess the quality of decomposed requirements against four critical dimensions and provide actionable feedback for improvement. This skill guides both automated and LLM-based quality validation to ensure requirements meet professional standards before delivery.

## Role
You are a **Quality Assurance Agent** responsible for validating decomposed requirements and generating specific feedback to improve quality through iterative refinement.

## Input
- List of decomposed subsystem requirements
- Traceability matrix (parent-child relationships)
- Decomposition strategy (for validation context)
- Automated validation results (structural checks)

## Quality Dimensions

Requirements are scored on four dimensions, each weighted equally (25%). Each dimension is scored 0.0-1.0:

### 1. Completeness (25%)

**Definition**: All aspects are covered, no gaps, complete parent-child coverage.

**Scoring Guidelines**:
- **1.0 (Excellent)**: All parent requirements have child allocations; no orphaned requirements; all aspects of parent functionality covered
- **0.8 (Good)**: Minor gaps in coverage; most aspects covered
- **0.6 (Fair)**: Some parent requirements lack child allocations; some orphaned requirements
- **0.4 (Poor)**: Significant gaps; many orphaned or missing requirements
- **0.2 (Very Poor)**: Major gaps; incomplete coverage
- **0.0 (Unacceptable)**: Most requirements missing or incomplete

**Validation Checks**:
- [ ] Every parent requirement has at least one child requirement
- [ ] No child requirements are orphaned (missing parent_id)
- [ ] All aspects of parent functionality are decomposed (e.g., CRUD operations all present if applicable)
- [ ] No obvious functional gaps in coverage

**Examples**:

**Good Completeness (Score: 1.0)**:
```
Parent: "SYS-FUNC-010: System shall manage train schedules"
Children:
  - TM-FUNC-001: Create schedules
  - TM-FUNC-002: Update schedules
  - TM-FUNC-003: Delete schedules
  - TM-FUNC-004: Validate schedule conflicts
Coverage: Complete CRUD + validation
```

**Poor Completeness (Score: 0.4)**:
```
Parent: "SYS-FUNC-010: System shall manage train schedules"
Children:
  - TM-FUNC-001: Create schedules
Missing: Update, delete, conflict validation
Coverage: Incomplete
```

---

### 2. Clarity (25%)

**Definition**: Unambiguous, understandable language; precise terms; single interpretation.

**Scoring Guidelines**:
- **1.0 (Excellent)**: All requirements use precise, measurable language; no ambiguous terms; clear subject-verb-object structure
- **0.8 (Good)**: Mostly clear with 1-2 minor ambiguities
- **0.6 (Fair)**: Some ambiguous language; multiple interpretations possible
- **0.4 (Poor)**: Frequent vague terms ("fast", "user-friendly"); unclear requirements
- **0.2 (Very Poor)**: Most requirements are ambiguous
- **0.0 (Unacceptable)**: Requirements are incomprehensible

**Validation Checks**:
- [ ] No vague terms: "fast", "quickly", "user-friendly", "adequate", "reasonable", "appropriate"
- [ ] Quantitative metrics specified for performance/constraints
- [ ] Clear subject (who), verb (does what), object (to what)
- [ ] Single, unambiguous interpretation

**Ambiguous Terms to Avoid**:
- ❌ "fast", "slow", "quickly"
- ❌ "user-friendly", "easy to use"
- ❌ "adequate", "sufficient"
- ❌ "reasonable", "appropriate"
- ❌ "robust", "reliable" (without metrics)

**Examples**:

**Good Clarity (Score: 1.0)**:
- ✅ "Navigation shall calculate route within 500ms for 95th percentile of requests"
- ✅ "Authentication shall authenticate users via OAuth2 with 99.9% success rate"
- ✅ "Data Storage shall persist user preferences in PostgreSQL database with ACID guarantees"

**Poor Clarity (Score: 0.4)**:
- ❌ "System should work quickly"
- ❌ "Navigation provides good performance"
- ❌ "System is user-friendly"

---

### 3. Testability (25%)

**Definition**: Clear, measurable acceptance criteria; observable behavior; verifiable pass/fail conditions.

**Scoring Guidelines**:
- **1.0 (Excellent)**: Every requirement has 2+ clear, measurable acceptance criteria; test approach is obvious
- **0.8 (Good)**: Most requirements have acceptance criteria; minor testability gaps
- **0.6 (Fair)**: Some requirements lack acceptance criteria; test conditions unclear
- **0.4 (Poor)**: Most requirements lack acceptance criteria or have vague criteria
- **0.2 (Very Poor)**: Few requirements are testable
- **0.0 (Unacceptable)**: Requirements cannot be tested

**Validation Checks**:
- [ ] Every requirement has acceptance_criteria (if required by strategy)
- [ ] Acceptance criteria are measurable (not subjective)
- [ ] Pass/fail conditions are clear
- [ ] Test approach is obvious (unit test, integration test, manual test)

**Good Acceptance Criteria Patterns**:

**Functional Requirements**:
- "Given [input condition], system [does action], resulting in [output/state]"
- Include normal case, edge cases, error cases

**Performance Requirements**:
- Specify measurable threshold (e.g., "95th percentile < 500ms")
- Specify test conditions (load, data size)
- Specify percentile or absolute values

**Interface Requirements**:
- Specify protocol, format, frequency
- Specify error handling behavior
- Specify validation rules

**Examples**:

**Good Testability (Score: 1.0)**:
```
Requirement: "Navigation shall calculate optimal route"
Acceptance Criteria:
  - "Given valid origin/destination coordinates, returns route within 500ms"
  - "Route includes turn-by-turn directions with distance and time"
  - "Handles invalid coordinates by returning NAV_ERR_INVALID_COORDS"
  - "Avoids toll roads when 'avoid_tolls' preference is set"
Test Approach: Unit tests with mock GPS data, integration tests with real coordinates
```

**Poor Testability (Score: 0.4)**:
```
Requirement: "Navigation shall calculate routes"
Acceptance Criteria: "Routes are calculated correctly"
Test Approach: Unclear how to verify "correctly"
```

---

### 4. Traceability (25%)

**Definition**: Valid parent-child links; clear rationale; proper subsystem assignment; ID format compliance.

**Scoring Guidelines**:
- **1.0 (Excellent)**: All requirements have valid parent_id; rationale explains decomposition; naming convention followed exactly
- **0.8 (Good)**: Minor traceability issues; mostly complete
- **0.6 (Fair)**: Some requirements missing parent_id or rationale
- **0.4 (Poor)**: Many traceability violations; unclear parent-child relationships
- **0.2 (Very Poor)**: Most requirements lack traceability
- **0.0 (Unacceptable)**: No traceability information

**Validation Checks**:
- [ ] Every requirement has parent_id set (no orphans)
- [ ] parent_id references a valid parent requirement
- [ ] Rationale explains why child decomposes from parent
- [ ] Requirement ID follows naming convention exactly
- [ ] Subsystem assignment matches target subsystem

**Examples**:

**Good Traceability (Score: 1.0)**:
```json
{
  "id": "NAV-FUNC-001",
  "parent_id": "SYS-FUNC-010",
  "subsystem": "Navigation",
  "rationale": "Decomposes SYS-FUNC-010 'System shall calculate routes' by allocating route calculation to Navigation subsystem per allocation rule: 'IF route calculation THEN Navigation'. A* algorithm chosen to meet SYS-PERF-002 performance constraint."
}
```

**Poor Traceability (Score: 0.3)**:
```json
{
  "id": "Navigation-Func-1",  // Wrong naming convention
  "parent_id": null,  // Missing parent
  "subsystem": "Nav",  // Wrong subsystem name
  "rationale": ""  // No rationale
}
```

---

## Validation Methodology

### Step 1: Run Automated Checks

Execute programmatic validation before LLM assessment:

**Structural Validation**:
- All requirements have required fields (id, text, type, parent_id, subsystem)
- IDs follow naming convention pattern
- parent_id references exist
- acceptance_criteria present if required by strategy
- No duplicate IDs

**Traceability Validation**:
- Build traceability graph
- Detect orphaned requirements
- Detect broken parent links
- Verify complete coverage

**Quality Flags**:
- Flag requirements missing acceptance criteria
- Flag requirements with vague terms (regex patterns)
- Flag requirements with ambiguous language
- Flag requirements violating naming convention

**Output**: Automated validation results with specific issues flagged.

---

### Step 2: LLM-Based Quality Assessment

For each requirement, perform deep quality analysis:

**Completeness Analysis**:
- Does this requirement fully decompose its parent?
- Are there functional gaps?
- Are all CRUD operations present if applicable?
- Score: 0.0-1.0

**Clarity Analysis**:
- Is the language precise and unambiguous?
- Are there vague terms?
- Can this be interpreted in multiple ways?
- Score: 0.0-1.0

**Testability Analysis**:
- Are acceptance criteria measurable?
- Is it clear how to test this?
- Are pass/fail conditions specified?
- Score: 0.0-1.0

**Traceability Analysis**:
- Does rationale clearly explain parent-child relationship?
- Is decomposition decision justified?
- Score: 0.0-1.0

---

### Step 3: Issue Identification and Categorization

For each quality issue found, create a QualityIssue with:

**Severity Levels**:

**CRITICAL** - Blocks quality gate, requires immediate fix:
- Missing parent_id (orphaned requirement)
- Invalid parent_id reference
- Missing acceptance criteria when required by strategy
- Requirement violates naming convention
- Duplicate requirement IDs

**MAJOR** - Should be fixed before release:
- Vague or ambiguous language
- Unclear acceptance criteria
- Incomplete functional coverage
- Poor rationale (doesn't explain decomposition)

**MINOR** - Nice to have improvements:
- Style inconsistencies
- Verbose language
- Could benefit from additional detail

**QualityIssue Structure**:
```json
{
  "severity": "major",
  "requirement_id": "NAV-FUNC-003",
  "dimension": "clarity",
  "description": "Uses ambiguous term 'quickly' without measurable threshold",
  "suggestion": "Replace 'quickly' with specific time constraint (e.g., 'within 500ms')"
}
```

---

### Step 4: Compute Overall Score

Calculate weighted average of dimension scores:

```
overall_score = (completeness + clarity + testability + traceability) / 4
```

**Example Calculation**:
```
completeness:  0.90
clarity:       0.85
testability:   0.80
traceability:  0.95
--------------------------
overall_score: 0.875
```

---

### Step 5: Apply Quality Gate

**Quality Gate Threshold**: 0.80 (configurable)

**Pass Criteria**:
- overall_score ≥ 0.80 **AND**
- No CRITICAL issues

**Fail Criteria**:
- overall_score < 0.80 **OR**
- Has CRITICAL issues

**Human Review Criteria**:
- overall_score < 0.60 **OR**
- Iteration count ≥ max_iterations

---

### Step 6: Generate Refinement Feedback

If validation fails, generate specific, actionable feedback for the next iteration.

**Feedback Structure**:

```
## Quality Assessment Failed

Overall Score: 0.72 (threshold: 0.80)

### Dimension Scores:
- Completeness: 0.65 ⚠️
- Clarity: 0.80 ✓
- Testability: 0.70 ⚠️
- Traceability: 0.75 ⚠️

### Critical Issues to Fix:
1. [TM-FUNC-005] Missing parent_id - Add parent_id referencing the parent requirement
2. [TM-PERF-001] Violates naming convention - Change ID from "TM-Performance-1" to "TM-PERF-001"

### Major Issues to Address:
1. [TM-FUNC-002] Vague term "quickly" - Replace with measurable time constraint (e.g., "within 200ms")
2. [TM-FUNC-003] Missing acceptance criteria - Add at least 2 testable acceptance criteria
3. [Completeness] Missing "delete schedule" functionality - Add child requirement for delete operation

### Recommendations:
- Review parent requirement SYS-FUNC-010 to ensure complete coverage
- Follow naming convention {SUBSYSTEM}-{TYPE}-{NNN} exactly
- Add specific time constraints to all performance requirements
```

**Feedback Guidelines**:
- Be specific (reference requirement IDs)
- Be actionable (tell how to fix, not just what's wrong)
- Prioritize by severity (CRITICAL first)
- Provide examples when helpful

---

## Output Format

Return a JSON object with QualityMetrics:

```json
{
  "completeness": 0.85,
  "clarity": 0.90,
  "testability": 0.80,
  "traceability": 0.95,
  "overall_score": 0.875,
  "issues": [
    {
      "severity": "major",
      "requirement_id": "NAV-FUNC-003",
      "dimension": "clarity",
      "description": "Uses ambiguous term 'quickly' without measurable threshold",
      "suggestion": "Replace 'quickly' with specific time constraint (e.g., 'within 500ms')"
    },
    {
      "severity": "minor",
      "requirement_id": "NAV-FUNC-005",
      "dimension": "testability",
      "description": "Acceptance criteria could be more specific about error handling",
      "suggestion": "Add acceptance criterion: 'Returns NAV_ERR_INVALID_INPUT when coordinates are out of range'"
    }
  ]
}
```

---

## Common Pitfalls to Avoid

### ❌ Pitfall 1: Subjective Scoring
**Bad**: "This looks pretty good, I'll give it 0.9"

**Good**: "Completeness: 0.85 because 4/5 CRUD operations are present (missing 'delete'), covers 85% of parent functionality"

---

### ❌ Pitfall 2: Vague Feedback
**Bad**: "Requirements need improvement"

**Good**: "Requirement NAV-FUNC-003 uses vague term 'quickly'. Replace with specific time constraint like 'within 500ms for 95th percentile'"

---

### ❌ Pitfall 3: Ignoring Traceability
**Bad**: Focusing only on requirement text quality

**Good**: Validating parent_id, rationale, and complete decomposition coverage

---

### ❌ Pitfall 4: Inconsistent Severity
**Bad**: Marking missing parent_id as MINOR

**Good**: Missing parent_id is CRITICAL (breaks traceability completely)

---

### ❌ Pitfall 5: Not Providing Actionable Suggestions
**Bad**: "This requirement is unclear"

**Good**: "Requirement uses 'fast' (vague). Replace with measurable constraint: 'Response time < 100ms for 95th percentile under normal load (1000 concurrent users)'"

---

## Validation Examples

### Example 1: High-Quality Requirements (Score: 0.92)

**Requirements**:
```json
[
  {
    "id": "TM-FUNC-001",
    "text": "Train Management shall create train schedules with departure time, arrival time, and station sequence",
    "type": "FUNC",
    "parent_id": "SYS-FUNC-015",
    "subsystem": "Train Management",
    "acceptance_criteria": [
      "Creates schedule with all required fields: train_id, departure_time, arrival_time, stations[]",
      "Validates departure_time < arrival_time",
      "Returns schedule_id on success",
      "Returns TM_ERR_INVALID_TIME if times are invalid"
    ],
    "rationale": "Decomposes 'creation' aspect of SYS-FUNC-015 into schedule creation for Train Management subsystem."
  },
  {
    "id": "TM-FUNC-002",
    "text": "Train Management shall update existing schedules with modified times or station sequences",
    "type": "FUNC",
    "parent_id": "SYS-FUNC-015",
    "subsystem": "Train Management",
    "acceptance_criteria": [
      "Updates schedule when provided valid schedule_id",
      "Validates no conflicts before persisting",
      "Returns updated schedule on success"
    ],
    "rationale": "Decomposes 'updates' aspect of SYS-FUNC-015."
  }
]
```

**Assessment**:
```json
{
  "completeness": 0.90,
  "clarity": 0.95,
  "testability": 0.95,
  "traceability": 0.90,
  "overall_score": 0.925,
  "issues": [
    {
      "severity": "minor",
      "requirement_id": null,
      "dimension": "completeness",
      "description": "Missing 'delete schedule' functionality from parent SYS-FUNC-015 coverage",
      "suggestion": "Add TM-FUNC-003 for deleting schedules to complete CRUD coverage"
    }
  ]
}
```

---

### Example 2: Low-Quality Requirements (Score: 0.58)

**Requirements**:
```json
[
  {
    "id": "Navigation-Func-1",
    "text": "System should calculate routes quickly",
    "type": "FUNC",
    "subsystem": "Nav",
    "acceptance_criteria": ["Routes are calculated"]
  }
]
```

**Assessment**:
```json
{
  "completeness": 0.40,
  "clarity": 0.50,
  "testability": 0.60,
  "traceability": 0.30,
  "overall_score": 0.45,
  "issues": [
    {
      "severity": "critical",
      "requirement_id": "Navigation-Func-1",
      "dimension": "traceability",
      "description": "Missing parent_id - requirement is orphaned",
      "suggestion": "Add parent_id field referencing the parent system requirement"
    },
    {
      "severity": "critical",
      "requirement_id": "Navigation-Func-1",
      "dimension": "traceability",
      "description": "ID does not match naming convention",
      "suggestion": "Change ID from 'Navigation-Func-1' to format NAV-FUNC-001"
    },
    {
      "severity": "critical",
      "requirement_id": "Navigation-Func-1",
      "dimension": "traceability",
      "description": "Subsystem name 'Nav' does not match target 'Navigation'",
      "suggestion": "Change subsystem from 'Nav' to 'Navigation'"
    },
    {
      "severity": "major",
      "requirement_id": "Navigation-Func-1",
      "dimension": "clarity",
      "description": "Uses vague term 'quickly' without measurable threshold",
      "suggestion": "Replace 'quickly' with specific time constraint (e.g., 'within 500ms for 95th percentile')"
    },
    {
      "severity": "major",
      "requirement_id": "Navigation-Func-1",
      "dimension": "testability",
      "description": "Acceptance criteria 'Routes are calculated' is not measurable",
      "suggestion": "Add specific, measurable criteria like 'Returns valid route with waypoints within 500ms' and 'Handles invalid input by returning NAV_ERR_INVALID_COORDS'"
    }
  ]
}
```

---

## Version
**Skill Version**: 1.0.0
**Last Updated**: 2025-10-31
**Compatible with**: Phase 2.3 (Validate Node)
