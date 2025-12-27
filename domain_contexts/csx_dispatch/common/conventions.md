# CSX Dispatch Requirements Template Conventions

## Standard Requirement Format

All subsystem requirements shall follow this template:

```
[SUBSYSTEM]-[TYPE]-[NUMBER]: [Title in Title Case]

The [Subsystem Name] shall [action verb] [object] [conditions/constraints].

[Optional: Additional clarification or context]
```

**Example:**
```
TM-FUNC-001: Display Active Train List

The Train Management subsystem shall display a list of all active trains when the operator accesses the Train Management view.
```

## Formatting Rules

### 1. Requirement IDs

- **Format**: `[SUBSYSTEM]-[TYPE]-[NUMBER]`
  - SUBSYSTEM: 2-3 letter prefix (TM, TC, BC, etc.)
  - TYPE: FUNC (Functional), PERF (Performance), INTF (Interface), CONS (Constraint)
  - NUMBER: Zero-padded 3-digit sequence (001, 002, etc.)
- **Examples**: `TM-FUNC-001`, `TC-PERF-042`, `BC-INTF-003`
- IDs must be unique within subsystem

### 2. Requirement Titles

- Use Title Case (capitalize first letter of major words)
- Describe the requirement function, not implementation
- Keep concise (typically 3-7 words)
- **Examples**:
  - ✅ "Display Active Train List"
  - ✅ "Validate Train Consist Data"
  - ❌ "display trains" (not Title Case)
  - ❌ "The system needs to show a list of trains to the user" (too verbose)

### 3. Requirement Statement Structure

- Start with "The [Subsystem Name] shall..."
- Use active voice and present tense
- One requirement per statement (no compound "and" requirements)
- Be specific about actors, actions, and conditions
- **Examples**:
  - ✅ "The Train Management subsystem shall display train status."
  - ✅ "The Traffic Control subsystem shall send signal commands to field devices within 100ms."
  - ❌ "System displays trains." (missing actor)
  - ❌ "The Train Management subsystem shall display trains and update status." (compound requirement)

### 4. Glossary Term Usage

- Always use canonical capitalization from domain glossary
- **Examples**:
  - ✅ "Train Management Function" (not "train management function")
  - ✅ "Use Case" (not "use case")
  - ✅ "Control Point" (not "control point")
  - ✅ "Authorized User" (not "authorized user")

## Modal Verbs

Use precise modal verbs to indicate requirement priority:

- **shall**: Mandatory requirement (MUST implement)
- **should**: Recommended requirement (SHOULD implement)
- **may**: Optional requirement (MAY implement)
- **must**: Absolute constraint (non-negotiable, typically for safety/regulatory)

## Prohibited Language

❌ **Do NOT use vague terms**:
- "fast," "slow," "quickly," "efficient"
- "user-friendly," "easy," "intuitive"
- "adequate," "sufficient," "appropriate"
- "reasonable," "typical," "normal"

✅ **Use specific, measurable terms**:
- "within 500ms," "at 95th percentile"
- "with 99.9% uptime," "for 1000 concurrent users"
- "compliant with IEEE 12207 standard"
- "at a refresh rate of 1Hz"

## Subsystem Abbreviations

| Subsystem | Abbreviation | Full Name |
|-----------|--------------|-----------|
| TM | TM | Train Management |
| TC | TC | Traffic Control |
| BC | BC | Bridge Control |

## Example Requirements

### Good Examples

**TM-FUNC-001: Display Train List**

The Train Management subsystem shall display a list of all active trains with their current status when an Authorized User accesses the Train List view.

---

**TC-PERF-005: Signal Command Response Time**

The Traffic Control subsystem shall send signal control commands to field devices within 100 milliseconds of receiving a command from the Dispatcher.

---

**BC-INTF-010: Bridge Status Interface**

The Bridge Control subsystem shall provide bridge status information to the Traffic Control subsystem via a RESTful API endpoint updated at 1Hz.

### Poor Examples

❌ **BAD-001: show trains**

The system shows trains to the user quickly.

**Issues**:
- ID format incorrect (should be TM-FUNC-001)
- Title not in Title Case
- Missing subsystem name in statement
- Vague term "quickly"
- Not specific about which user or what triggers display

---

❌ **TM-FUNC-999: Train Management Features**

The train management function shall display trains and update their status and allow filtering and sorting.

**Issues**:
- Glossary term not capitalized ("train management function" should be "Train Management Function")
- Compound requirement (contains multiple "and" clauses)
- Missing trigger condition
- Should be split into 4 separate requirements
