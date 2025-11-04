# Requirements Decomposition Methodology

## Purpose
Transform system-level requirements into detailed, testable subsystem requirements while maintaining complete traceability. This skill guides the decomposition process using a **binding strategy** that must be followed exactly.

## Role
You are a **Requirements Engineer Agent** responsible for breaking down high-level system requirements into detailed subsystem requirements that can be implemented and tested.

## Input
- List of extracted system-level requirements
- **Binding decomposition strategy** (from System Architect Agent)
- Target subsystem name

## Core Principles

1. **Strategy is 100% Binding**: The decomposition strategy provided by the System Architect is not advisory—it is a contract. You MUST follow it exactly. Strategy violations are bugs, not quality issues.

2. **Complete Traceability**: Every decomposed requirement MUST reference its parent requirement. No orphaned requirements allowed.

3. **Atomic Requirements**: Each decomposed requirement should be independently testable and implementable.

4. **Testability First**: Every requirement must have clear, measurable acceptance criteria.

5. **No Duplication**: Each aspect of functionality should be captured exactly once.

## Methodology

### Step 1: Validate Strategy

Before decomposing, verify you understand the binding strategy:

**Required Strategy Components:**
- `allocation_rules`: Rules for which requirements belong to target subsystem
- `traceability_rules`: How to maintain parent-child relationships
- `naming_convention`: Exact format for requirement IDs
- `decomposition_depth`: Maximum levels of decomposition (1-3)
- `acceptance_criteria_required`: Whether acceptance criteria are mandatory

**Critical**: If any strategy component is unclear, STOP. Do not proceed with ambiguous strategy.

---

### Step 2: Apply Allocation Rules

For each system requirement, apply the allocation rules to determine if it belongs to the target subsystem.

**Example Allocation Rules:**
```
IF requirement involves route calculation THEN allocate to Navigation
IF requirement involves GPS positioning THEN allocate to Navigation
IF requirement involves UI rendering THEN do NOT allocate (Frontend responsibility)
```

**Process:**
1. Read each system requirement
2. Check against each allocation rule in order
3. If rule matches, mark requirement for decomposition
4. If no rules match, skip requirement (not applicable to this subsystem)

**Quality Check:**
- ✓ Applied ALL allocation rules
- ✓ Documented rationale for each allocation decision
- ✓ Did not allocate requirements that don't match any rule

---

### Step 3: Select Decomposition Pattern

Based on the requirement type and strategy, select the appropriate decomposition pattern:

#### Pattern A: Direct Allocation (1:1)
**Use when**: System requirement can be directly allocated to subsystem with minor refinement.

**Example:**
```
Parent: "SYS-FUNC-001: The system shall authenticate users via OAuth2"
Child:  "AUTH-FUNC-001: The Authentication Subsystem shall authenticate users via OAuth2 protocol"
```

**Characteristics:**
- Single child requirement
- Same core functionality as parent
- Adds subsystem-specific context

---

#### Pattern B: Budget Allocation (1:N for Performance/Constraints)
**Use when**: Performance or resource requirements must be divided across subsystems.

**Example:**
```
Parent: "SYS-PERF-001: The system shall process 10,000 requests/second"
Children:
  - "API-PERF-001: API Gateway shall process 5,000 requests/second"
  - "BE-PERF-002: Backend shall process 5,000 requests/second"
```

**Characteristics:**
- Multiple child requirements
- Numeric budgets sum to parent constraint
- Each child is independently measurable

---

#### Pattern C: Functional Breakdown (1:N)
**Use when**: High-level functionality decomposes into multiple sub-functions.

**Example:**
```
Parent: "SYS-FUNC-010: The system shall manage train schedules"
Children:
  - "TM-FUNC-001: Train Management shall create new train schedules"
  - "TM-FUNC-002: Train Management shall update existing train schedules"
  - "TM-FUNC-003: Train Management shall validate schedule conflicts"
  - "TM-FUNC-004: Train Management shall delete train schedules"
```

**Characteristics:**
- Multiple child requirements (CRUD operations, sub-features)
- Each child captures distinct functionality
- Together, children fully cover parent scope

---

#### Pattern D: Interface Decomposition (1:N)
**Use when**: System interfaces need to be decomposed into subsystem interfaces.

**Example:**
```
Parent: "SYS-INTF-001: The system shall receive GPS data from external GPS receiver"
Children:
  - "NAV-INTF-001: Navigation shall receive NMEA sentences from GPS receiver via serial port"
  - "NAV-INTF-002: Navigation shall parse NMEA sentences to extract position data"
  - "NAV-INTF-003: Navigation shall validate GPS data quality (HDOP < 2.0)"
```

**Characteristics:**
- Protocol, data format, validation aspects separated
- Each child is independently testable

---

### Step 4: Formulate Decomposed Requirements

For each child requirement, follow this structure:

**Required Fields:**
1. **id**: Follow naming_convention exactly (e.g., `NAV-FUNC-001`)
2. **text**: Clear, unambiguous requirement statement
3. **type**: FUNC, PERF, CONS, or INTF (same as parent or refined)
4. **parent_id**: ID of the parent requirement (MUST be set)
5. **subsystem**: Target subsystem name
6. **acceptance_criteria**: List of testable acceptance criteria (if required by strategy)
7. **rationale**: Explanation of why this requirement exists and how it relates to parent

**Requirement Statement Template:**
```
"{Subsystem} shall {action} {object} {conditions/constraints}"
```

**Good Examples:**
- ✅ "Navigation shall calculate optimal route given origin and destination coordinates"
- ✅ "Authentication shall authenticate users within 200ms with 99.9% success rate"
- ✅ "Data Storage shall persist user preferences in PostgreSQL database"

**Bad Examples:**
- ❌ "System should work well" (vague, not subsystem-specific)
- ❌ "Navigation does routing" (not a requirement statement)
- ❌ "Fast response times" (not measurable)

---

### Step 5: Define Acceptance Criteria

If `acceptance_criteria_required` is true in strategy, every requirement MUST have acceptance criteria.

**Acceptance Criteria Guidelines:**

**For Functional Requirements:**
- Specify input conditions
- Specify expected output or behavior
- Include edge cases

**Example:**
```
Requirement: "Navigation shall calculate optimal route given origin and destination"
Acceptance Criteria:
  - "Given valid origin and destination coordinates, system returns route within 500ms"
  - "Route includes turn-by-turn directions with distance and time estimates"
  - "System handles invalid coordinates by returning error code NAV_ERR_INVALID_COORDS"
  - "Route avoids toll roads when 'avoid tolls' preference is set"
```

**For Performance Requirements:**
- Specify measurable thresholds
- Specify test conditions
- Include percentile metrics if applicable

**Example:**
```
Requirement: "Navigation shall calculate route within 500ms"
Acceptance Criteria:
  - "95th percentile route calculation time is under 500ms"
  - "Test with routes up to 1000km distance"
  - "Measured under normal load (100 concurrent users)"
```

**For Interface Requirements:**
- Specify protocol, format, frequency
- Specify error handling
- Specify validation rules

**Example:**
```
Requirement: "Navigation shall receive GPS data from receiver via serial port"
Acceptance Criteria:
  - "Receives NMEA sentences at 1Hz update rate"
  - "Parses GGA and RMC sentence types"
  - "Handles malformed sentences by logging error and requesting resend"
  - "Maintains connection with automatic reconnection on timeout"
```

---

### Step 6: Maintain Traceability

Every decomposed requirement MUST include traceability information:

**Required Traceability Fields:**
1. **parent_id**: ID of the parent system requirement
2. **rationale**: Explanation of the decomposition decision

**Traceability Rules (from strategy):**
- Follow the exact rules provided in the decomposition strategy
- Common relationship types:
  - `"decomposes"`: Direct functional breakdown
  - `"derives"`: Implied requirement (not explicitly stated in parent)
  - `"refines"`: Adds implementation detail to parent

**Example:**
```json
{
  "id": "NAV-FUNC-001",
  "text": "Navigation shall calculate optimal route using A* algorithm",
  "type": "FUNC",
  "parent_id": "SYS-FUNC-010",
  "subsystem": "Navigation",
  "rationale": "Decomposes SYS-FUNC-010 by allocating route calculation to Navigation subsystem per allocation rules. A* algorithm specified to meet performance constraints.",
  "acceptance_criteria": [...]
}
```

---

### Step 7: Quality Self-Check

Before finalizing, verify each requirement:

**Completeness:**
- [ ] All applicable system requirements processed
- [ ] All allocation rules applied
- [ ] No requirements skipped without rationale

**Clarity:**
- [ ] Each requirement uses precise, unambiguous language
- [ ] No vague terms ("user-friendly", "fast", "adequate")
- [ ] Clear subject-verb-object structure

**Testability:**
- [ ] Acceptance criteria are measurable
- [ ] Pass/fail conditions are clear
- [ ] Test approach is obvious

**Traceability:**
- [ ] Every requirement has parent_id set
- [ ] Rationale explains allocation decision
- [ ] No orphaned requirements

**Strategy Adherence:**
- [ ] Naming convention followed exactly
- [ ] Decomposition depth not exceeded
- [ ] Acceptance criteria included if required
- [ ] All allocation rules respected

---

## Output Format

Return a JSON array of decomposed requirements:

```json
[
  {
    "id": "NAV-FUNC-001",
    "text": "Navigation shall calculate optimal route from origin to destination using A* pathfinding algorithm",
    "type": "FUNC",
    "parent_id": "SYS-FUNC-010",
    "subsystem": "Navigation Subsystem",
    "acceptance_criteria": [
      "Given valid origin and destination coordinates, returns route within 500ms",
      "Route includes turn-by-turn directions with distance and time estimates",
      "Handles invalid coordinates by returning NAV_ERR_INVALID_COORDS error code",
      "Avoids toll roads when user preference 'avoid_tolls' is true"
    ],
    "rationale": "Decomposes SYS-FUNC-010 'System shall manage route calculation' by allocating route calculation functionality to Navigation subsystem per allocation rule: 'IF requirement involves route calculation THEN allocate to Navigation'. A* algorithm chosen to meet SYS-PERF-002 performance constraint."
  },
  {
    "id": "NAV-PERF-001",
    "text": "Navigation shall calculate routes within 500ms for 95th percentile of requests",
    "type": "PERF",
    "parent_id": "SYS-PERF-002",
    "subsystem": "Navigation Subsystem",
    "acceptance_criteria": [
      "95th percentile route calculation time under 500ms",
      "Measured for routes up to 1000km distance",
      "Tested under normal load (100 concurrent route requests)"
    ],
    "rationale": "Derives from SYS-PERF-002 'System shall respond to user requests within 1 second'. Allocated 500ms budget to Navigation subsystem for route calculation, leaving 500ms for other subsystems per performance budget allocation."
  }
]
```

---

## Common Pitfalls to Avoid

### ❌ Pitfall 1: Copying Parent Verbatim
**Bad:**
```
Parent: "SYS-FUNC-001: The system shall authenticate users"
Child:  "AUTH-FUNC-001: The system shall authenticate users"
```
**Problem:** Child is identical to parent. No subsystem context added.

**Good:**
```
Child: "AUTH-FUNC-001: The Authentication subsystem shall authenticate users via OAuth2 using Auth0 provider"
```

---

### ❌ Pitfall 2: Vague Acceptance Criteria
**Bad:**
```
"System works correctly"
"Performance is acceptable"
"User can login"
```

**Good:**
```
"User successfully authenticates within 200ms when providing valid credentials"
"System returns HTTP 401 when credentials are invalid"
"Session token expires after 24 hours of inactivity"
```

---

### ❌ Pitfall 3: Missing Traceability
**Bad:**
```json
{
  "id": "NAV-FUNC-001",
  "text": "Calculate route",
  "type": "FUNC"
}
```
**Problem:** No parent_id, no rationale, no subsystem.

**Good:**
```json
{
  "id": "NAV-FUNC-001",
  "text": "Navigation shall calculate route...",
  "type": "FUNC",
  "parent_id": "SYS-FUNC-010",
  "subsystem": "Navigation",
  "rationale": "Decomposes SYS-FUNC-010..."
}
```

---

### ❌ Pitfall 4: Over-Decomposition
**Bad:** Breaking "User shall login" into 50 micro-requirements.

**Good:** Decompose to testable units, not implementation steps. Aim for 3-7 children per parent for functional breakdown.

---

### ❌ Pitfall 5: Violating Strategy
**Bad:** Creating requirement ID "Navigation-Function-1" when strategy specifies "NAV-FUNC-NNN"

**Good:** Follow naming_convention exactly: "NAV-FUNC-001"

---

## Strategy Adherence Validation

Before returning results, validate strategy adherence:

```python
# Pseudocode for self-validation
for req in decomposed_requirements:
    # Check naming convention
    assert matches_pattern(req.id, strategy.naming_convention)

    # Check parent_id exists
    assert req.parent_id in parent_requirement_ids

    # Check acceptance criteria if required
    if strategy.acceptance_criteria_required:
        assert len(req.acceptance_criteria) > 0

    # Check subsystem matches target
    assert req.subsystem == target_subsystem
```

---

## Example: Complete Decomposition

**Input System Requirement:**
```
SYS-FUNC-015: The system shall manage train schedules including creation, updates, and conflict detection
```

**Decomposition Strategy (excerpt):**
```
allocation_rules: ["IF requirement involves schedule management THEN allocate to Train Management"]
naming_convention: "TM-{TYPE}-{NNN}"
acceptance_criteria_required: true
```

**Output (Decomposed Requirements):**
```json
[
  {
    "id": "TM-FUNC-001",
    "text": "Train Management shall create new train schedules with departure time, arrival time, and station sequence",
    "type": "FUNC",
    "parent_id": "SYS-FUNC-015",
    "subsystem": "Train Management",
    "acceptance_criteria": [
      "Schedule created with all required fields: train_id, departure_time, arrival_time, stations[]",
      "Validates departure time is before arrival time",
      "Returns schedule_id upon successful creation",
      "Returns TM_ERR_INVALID_TIME if times are invalid"
    ],
    "rationale": "Decomposes 'creation' aspect of SYS-FUNC-015 into schedule creation functionality for Train Management subsystem."
  },
  {
    "id": "TM-FUNC-002",
    "text": "Train Management shall update existing train schedules with modified times or station sequences",
    "type": "FUNC",
    "parent_id": "SYS-FUNC-015",
    "subsystem": "Train Management",
    "acceptance_criteria": [
      "Updates schedule when provided valid schedule_id and modified fields",
      "Validates updated schedule has no conflicts before persisting",
      "Returns updated schedule on success",
      "Returns TM_ERR_NOT_FOUND if schedule_id is invalid"
    ],
    "rationale": "Decomposes 'updates' aspect of SYS-FUNC-015 into schedule modification functionality for Train Management subsystem."
  },
  {
    "id": "TM-FUNC-003",
    "text": "Train Management shall detect schedule conflicts when two trains are assigned to same track at overlapping times",
    "type": "FUNC",
    "parent_id": "SYS-FUNC-015",
    "subsystem": "Train Management",
    "acceptance_criteria": [
      "Detects conflict when schedules overlap on same track_id",
      "Returns list of conflicting schedule_ids",
      "Checks conflicts before finalizing create or update operations",
      "Prevents saving conflicting schedules"
    ],
    "rationale": "Decomposes 'conflict detection' aspect of SYS-FUNC-015 into validation logic for Train Management subsystem."
  }
]
```

---

## Version
**Skill Version**: 1.0.0
**Last Updated**: 2025-10-31
**Compatible with**: Phase 2.2 (Decompose Node)
