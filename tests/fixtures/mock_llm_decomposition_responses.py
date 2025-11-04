"""
Mock LLM responses for requirements decomposition testing.

Provides pre-built responses for testing RequirementsEngineerAgent.
"""

# Valid decomposition response
VALID_DECOMPOSITION_RESPONSE = """```json
[
  {
    "id": "NAV-FUNC-001",
    "text": "Navigation shall calculate optimal route from origin to destination",
    "type": "FUNC",
    "parent_id": "EXTRACT-FUNC-001",
    "subsystem": "Navigation Subsystem",
    "acceptance_criteria": [
      "Given valid coordinates, returns route within 500ms",
      "Route includes turn-by-turn directions"
    ],
    "rationale": "Decomposes EXTRACT-FUNC-001 by allocating route calculation to Navigation"
  },
  {
    "id": "NAV-PERF-001",
    "text": "Navigation shall calculate routes within 500ms",
    "type": "PERF",
    "parent_id": "EXTRACT-PERF-001",
    "subsystem": "Navigation Subsystem",
    "acceptance_criteria": [
      "95th percentile under 500ms"
    ],
    "rationale": "Performance budget allocated to Navigation subsystem"
  }
]
```"""

# Plain JSON without markdown
PLAIN_JSON_DECOMPOSITION = """[
  {
    "id": "BE-FUNC-001",
    "text": "Backend shall process user authentication",
    "type": "FUNC",
    "parent_id": "SYS-FUNC-001",
    "subsystem": "Backend",
    "acceptance_criteria": ["Authenticates users via OAuth2"],
    "rationale": "Backend handles authentication logic"
  }
]"""

# Malformed JSON
MALFORMED_JSON_DECOMPOSITION = """```json
[
  {
    "id": "NAV-FUNC-001",
    "text": "Missing closing brace"
    "type": "FUNC"
]
```"""

# Not an array
NON_ARRAY_DECOMPOSITION = """```json
{
  "id": "NAV-FUNC-001",
  "text": "This is an object not an array"
}
```"""

# Missing required fields
INCOMPLETE_DECOMPOSITION = """```json
[
  {
    "id": "NAV-FUNC-001",
    "text": "Missing type and subsystem fields"
  }
]
```"""

# Empty array
EMPTY_DECOMPOSITION = """```json
[]
```"""

# Multiple requirements (complex)
COMPLEX_DECOMPOSITION_RESPONSE = """```json
[
  {
    "id": "TM-FUNC-001",
    "text": "Train Management shall create new train schedules",
    "type": "FUNC",
    "parent_id": "SYS-FUNC-010",
    "subsystem": "Train Management",
    "acceptance_criteria": [
      "Creates schedule with train_id, departure_time, arrival_time",
      "Validates departure before arrival",
      "Returns schedule_id on success"
    ],
    "rationale": "Decomposes schedule creation from SYS-FUNC-010"
  },
  {
    "id": "TM-FUNC-002",
    "text": "Train Management shall update existing train schedules",
    "type": "FUNC",
    "parent_id": "SYS-FUNC-010",
    "subsystem": "Train Management",
    "acceptance_criteria": [
      "Updates schedule with valid schedule_id",
      "Validates no conflicts before persisting"
    ],
    "rationale": "Decomposes schedule updates from SYS-FUNC-010"
  },
  {
    "id": "TM-FUNC-003",
    "text": "Train Management shall detect schedule conflicts",
    "type": "FUNC",
    "parent_id": "SYS-FUNC-010",
    "subsystem": "Train Management",
    "acceptance_criteria": [
      "Detects overlapping schedules on same track",
      "Returns conflicting schedule_ids"
    ],
    "rationale": "Decomposes conflict detection from SYS-FUNC-010"
  },
  {
    "id": "TM-PERF-001",
    "text": "Train Management shall process schedule queries within 200ms",
    "type": "PERF",
    "parent_id": "SYS-PERF-001",
    "subsystem": "Train Management",
    "acceptance_criteria": [
      "95th percentile query time under 200ms",
      "Supports 1000 concurrent users"
    ],
    "rationale": "Performance budget allocated to Train Management"
  }
]
```"""

# Missing parent_id (traceability violation)
MISSING_PARENT_ID = """```json
[
  {
    "id": "NAV-FUNC-001",
    "text": "Navigation shall calculate routes",
    "type": "FUNC",
    "subsystem": "Navigation Subsystem",
    "acceptance_criteria": ["Returns route"],
    "rationale": "Route calculation"
  }
]
```"""

# Wrong subsystem (strategy violation)
WRONG_SUBSYSTEM = """```json
[
  {
    "id": "NAV-FUNC-001",
    "text": "Navigation shall calculate routes",
    "type": "FUNC",
    "parent_id": "SYS-FUNC-001",
    "subsystem": "WrongSubsystem",
    "acceptance_criteria": ["Returns route"],
    "rationale": "Route calculation"
  }
]
```"""

# Wrong naming convention (strategy violation)
WRONG_NAMING_CONVENTION = """```json
[
  {
    "id": "Navigation-Function-1",
    "text": "Navigation shall calculate routes",
    "type": "FUNC",
    "parent_id": "SYS-FUNC-001",
    "subsystem": "Navigation Subsystem",
    "acceptance_criteria": ["Returns route"],
    "rationale": "Route calculation"
  }
]
```"""

# Missing acceptance criteria when required
MISSING_ACCEPTANCE_CRITERIA = """```json
[
  {
    "id": "NAV-FUNC-001",
    "text": "Navigation shall calculate routes",
    "type": "FUNC",
    "parent_id": "SYS-FUNC-001",
    "subsystem": "Navigation Subsystem",
    "rationale": "Route calculation"
  }
]
```"""
