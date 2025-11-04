"""
Mock LLM responses for system analysis testing.

Provides pre-built responses for testing SystemArchitectAgent.
"""

# Valid analysis response
VALID_ANALYSIS_RESPONSE = """```json
{
  "system_context": {
    "subsystem": "Navigation Subsystem",
    "description": "Responsible for route calculation, GPS positioning, and map rendering",
    "constraints": [
      "Must operate on embedded Linux platform",
      "Real-time response required (< 1 second)"
    ],
    "interfaces": [
      "GPS receiver (NMEA protocol)",
      "Display system (CAN bus)"
    ],
    "assumptions": [
      "GPS signal is available 95% of the time",
      "Map data is pre-loaded locally"
    ]
  },
  "decomposition_strategy": {
    "allocation_rules": [
      "IF requirement involves route calculation THEN allocate to Navigation",
      "IF requirement involves GPS positioning THEN allocate to Navigation",
      "IF requirement involves map rendering THEN allocate to Navigation"
    ],
    "traceability_rules": [
      "Every decomposed requirement must reference parent_id",
      "Rationale must explain allocation decision"
    ],
    "decomposition_depth": 1,
    "naming_convention": "NAV-{TYPE}-{NNN}",
    "acceptance_criteria_required": true
  }
}
```"""

# Plain JSON without markdown
PLAIN_JSON_ANALYSIS = """{
  "system_context": {
    "subsystem": "Backend Subsystem",
    "description": "Handles data processing and business logic",
    "constraints": [],
    "interfaces": ["Database", "API Gateway"],
    "assumptions": []
  },
  "decomposition_strategy": {
    "allocation_rules": [
      "IF requirement involves database THEN allocate to Backend"
    ],
    "traceability_rules": ["Must have parent_id"],
    "decomposition_depth": 1,
    "naming_convention": "BE-{TYPE}-{NNN}",
    "acceptance_criteria_required": true
  }
}"""

# Malformed JSON
MALFORMED_JSON_ANALYSIS = """```json
{
  "system_context": {
    "subsystem": "Test",
    "description": "Missing closing braces"
  "decomposition_strategy": {
}
```"""

# Missing system_context
MISSING_SYSTEM_CONTEXT = """```json
{
  "decomposition_strategy": {
    "allocation_rules": ["Rule 1"],
    "traceability_rules": ["Rule 1"],
    "decomposition_depth": 1,
    "naming_convention": "TEST-{TYPE}-{NNN}",
    "acceptance_criteria_required": true
  }
}
```"""

# Missing decomposition_strategy
MISSING_DECOMPOSITION_STRATEGY = """```json
{
  "system_context": {
    "subsystem": "Test Subsystem",
    "description": "Test description",
    "constraints": [],
    "interfaces": [],
    "assumptions": []
  }
}
```"""

# Invalid decomposition_depth (too high)
INVALID_DECOMPOSITION_DEPTH = """```json
{
  "system_context": {
    "subsystem": "Test Subsystem",
    "description": "Test description",
    "constraints": [],
    "interfaces": [],
    "assumptions": []
  },
  "decomposition_strategy": {
    "allocation_rules": ["Rule 1"],
    "traceability_rules": ["Rule 1"],
    "decomposition_depth": 5,
    "naming_convention": "TEST-{TYPE}-{NNN}",
    "acceptance_criteria_required": true
  }
}
```"""

# Missing required fields in decomposition_strategy
INCOMPLETE_STRATEGY = """```json
{
  "system_context": {
    "subsystem": "Test Subsystem",
    "description": "Test description",
    "constraints": [],
    "interfaces": [],
    "assumptions": []
  },
  "decomposition_strategy": {
    "allocation_rules": ["Rule 1"],
    "decomposition_depth": 1
  }
}
```"""

# Complex valid response with multiple rules
COMPLEX_ANALYSIS_RESPONSE = """```json
{
  "system_context": {
    "subsystem": "Train Management Subsystem",
    "description": "Manages train schedules, tracking, and dispatch operations",
    "constraints": [
      "Must support 1000+ trains concurrently",
      "Response time < 200ms for schedule queries",
      "Must integrate with legacy dispatch system"
    ],
    "interfaces": [
      "GPS tracking system (real-time updates)",
      "Dispatch control panel (WebSocket)",
      "Schedule database (PostgreSQL)",
      "Legacy dispatch system (SOAP/XML)"
    ],
    "assumptions": [
      "GPS data is accurate within 10 meters",
      "Network latency is < 50ms",
      "Database is properly indexed"
    ]
  },
  "decomposition_strategy": {
    "allocation_rules": [
      "IF requirement involves schedule creation THEN allocate to Train Management",
      "IF requirement involves schedule updates THEN allocate to Train Management",
      "IF requirement involves train tracking THEN allocate to Train Management",
      "IF requirement involves dispatch coordination THEN allocate to Train Management",
      "IF requirement involves GPS data processing THEN allocate to Train Management",
      "IF requirement involves UI rendering THEN do NOT allocate",
      "IF requirement involves network infrastructure THEN do NOT allocate"
    ],
    "traceability_rules": [
      "Every decomposed requirement MUST reference parent_id",
      "Rationale must explain why requirement belongs to Train Management",
      "Use relationship_type='decomposes' for direct allocation",
      "Use relationship_type='derives' for implied requirements"
    ],
    "decomposition_depth": 2,
    "naming_convention": "TM-{TYPE}-{NNN} where TYPE in [FUNC, PERF, CONS, INTF] and NNN is 001-999",
    "acceptance_criteria_required": true
  }
}
```"""
