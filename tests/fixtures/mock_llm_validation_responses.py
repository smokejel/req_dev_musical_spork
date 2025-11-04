"""
Mock LLM responses for requirements quality validation testing.

Provides pre-built responses for testing QualityAssuranceAgent.
"""

# Valid validation response - all dimensions pass (> 0.80)
VALID_VALIDATION_RESPONSE = """```json
{
  "completeness": 0.95,
  "clarity": 0.90,
  "testability": 0.92,
  "traceability": 0.88,
  "overall_score": 0.9125,
  "issues": [
    {
      "severity": "minor",
      "requirement_id": "NAV-FUNC-003",
      "dimension": "testability",
      "description": "Acceptance criteria could include edge case for invalid coordinates",
      "suggestion": "Add criterion: 'Returns NAV_ERR_INVALID_COORDS when coordinates are out of range'"
    }
  ]
}
```"""

# Failed validation response - scores below threshold
FAILED_VALIDATION_RESPONSE = """```json
{
  "completeness": 0.70,
  "clarity": 0.75,
  "testability": 0.65,
  "traceability": 0.80,
  "overall_score": 0.725,
  "issues": [
    {
      "severity": "major",
      "requirement_id": "NAV-FUNC-002",
      "dimension": "clarity",
      "description": "Uses vague term 'quickly' without measurable threshold",
      "suggestion": "Replace 'quickly' with specific time constraint (e.g., 'within 500ms for 95th percentile')"
    },
    {
      "severity": "major",
      "requirement_id": "NAV-FUNC-003",
      "dimension": "testability",
      "description": "Missing acceptance criteria",
      "suggestion": "Add at least 2 testable acceptance criteria specifying input conditions, expected output, and edge cases"
    },
    {
      "severity": "major",
      "requirement_id": null,
      "dimension": "completeness",
      "description": "Missing 'delete route' functionality from parent requirement coverage",
      "suggestion": "Add NAV-FUNC-004 for deleting routes to complete CRUD coverage"
    }
  ]
}
```"""

# Validation with critical issues (blocks quality gate)
VALIDATION_WITH_CRITICAL_ISSUES = """```json
{
  "completeness": 0.85,
  "clarity": 0.88,
  "testability": 0.82,
  "traceability": 0.60,
  "overall_score": 0.7875,
  "issues": [
    {
      "severity": "critical",
      "requirement_id": "NAV-FUNC-005",
      "dimension": "traceability",
      "description": "Missing parent_id - requirement is orphaned",
      "suggestion": "Add parent_id field referencing the parent system requirement (e.g., 'SYS-FUNC-010')"
    },
    {
      "severity": "critical",
      "requirement_id": "NAV-PERF-001",
      "dimension": "traceability",
      "description": "ID does not match naming convention NAV-{TYPE}-{NNN}",
      "suggestion": "Change ID from 'NAV-Performance-1' to 'NAV-PERF-001'"
    },
    {
      "severity": "major",
      "requirement_id": "NAV-FUNC-003",
      "dimension": "clarity",
      "description": "Uses vague term 'fast' without specification",
      "suggestion": "Replace 'fast' with measurable constraint like 'within 200ms'"
    }
  ]
}
```"""

# Validation with only minor issues
VALIDATION_WITH_MINOR_ISSUES = """```json
{
  "completeness": 0.92,
  "clarity": 0.90,
  "testability": 0.88,
  "traceability": 0.90,
  "overall_score": 0.90,
  "issues": [
    {
      "severity": "minor",
      "requirement_id": "NAV-FUNC-001",
      "dimension": "testability",
      "description": "Acceptance criteria could be more specific about error handling",
      "suggestion": "Add criterion for invalid input handling"
    },
    {
      "severity": "minor",
      "requirement_id": "NAV-FUNC-002",
      "dimension": "clarity",
      "description": "Could specify units for distance measurement",
      "suggestion": "Add units: 'distance in kilometers' instead of just 'distance'"
    }
  ]
}
```"""

# Malformed JSON (for error handling tests)
MALFORMED_JSON_VALIDATION = """```json
{
  "completeness": 0.85,
  "clarity": 0.88
  "testability": 0.82,
  "overall_score": "invalid"
}
```"""

# Plain JSON without markdown
PLAIN_JSON_VALIDATION = """{
  "completeness": 0.88,
  "clarity": 0.85,
  "testability": 0.90,
  "traceability": 0.87,
  "overall_score": 0.875,
  "issues": []
}"""

# Non-object response
NON_OBJECT_VALIDATION = """```json
[
  {
    "completeness": 0.85
  }
]
```"""

# Missing required fields
INCOMPLETE_VALIDATION = """```json
{
  "completeness": 0.85,
  "clarity": 0.88,
  "overall_score": 0.865
}
```"""

# Empty issues array
EMPTY_ISSUES_VALIDATION = """```json
{
  "completeness": 1.0,
  "clarity": 1.0,
  "testability": 1.0,
  "traceability": 1.0,
  "overall_score": 1.0,
  "issues": []
}
```"""

# Complex validation with many issues
COMPLEX_VALIDATION_RESPONSE = """```json
{
  "completeness": 0.72,
  "clarity": 0.68,
  "testability": 0.70,
  "traceability": 0.75,
  "overall_score": 0.7125,
  "issues": [
    {
      "severity": "critical",
      "requirement_id": "TM-FUNC-005",
      "dimension": "traceability",
      "description": "Missing parent_id",
      "suggestion": "Add parent_id referencing SYS-FUNC-015"
    },
    {
      "severity": "critical",
      "requirement_id": "TM-FUNC-006",
      "dimension": "traceability",
      "description": "Parent ID 'SYS-FUNC-999' does not exist",
      "suggestion": "Change parent_id to valid system requirement ID"
    },
    {
      "severity": "major",
      "requirement_id": "TM-FUNC-001",
      "dimension": "clarity",
      "description": "Uses vague term 'efficiently'",
      "suggestion": "Replace with measurable performance constraint"
    },
    {
      "severity": "major",
      "requirement_id": "TM-FUNC-002",
      "dimension": "testability",
      "description": "Acceptance criteria 'works correctly' is not measurable",
      "suggestion": "Specify exact pass/fail conditions"
    },
    {
      "severity": "major",
      "requirement_id": "TM-FUNC-003",
      "dimension": "completeness",
      "description": "Missing error handling specification",
      "suggestion": "Add acceptance criteria for error cases"
    },
    {
      "severity": "major",
      "requirement_id": null,
      "dimension": "completeness",
      "description": "Missing 'delete schedule' functionality",
      "suggestion": "Add requirement for delete operation to complete CRUD"
    },
    {
      "severity": "minor",
      "requirement_id": "TM-FUNC-004",
      "dimension": "clarity",
      "description": "Could specify database table name",
      "suggestion": "Add detail about persistence layer"
    }
  ]
}
```"""

# Very low quality (triggers human review)
VERY_LOW_QUALITY_VALIDATION = """```json
{
  "completeness": 0.45,
  "clarity": 0.50,
  "testability": 0.40,
  "traceability": 0.35,
  "overall_score": 0.425,
  "issues": [
    {
      "severity": "critical",
      "requirement_id": "NAV-FUNC-001",
      "dimension": "traceability",
      "description": "Missing parent_id",
      "suggestion": "Add parent_id"
    },
    {
      "severity": "critical",
      "requirement_id": "NAV-FUNC-002",
      "dimension": "traceability",
      "description": "Missing parent_id",
      "suggestion": "Add parent_id"
    },
    {
      "severity": "critical",
      "requirement_id": "NAV-FUNC-003",
      "dimension": "testability",
      "description": "No acceptance criteria",
      "suggestion": "Add measurable acceptance criteria"
    },
    {
      "severity": "major",
      "requirement_id": "NAV-FUNC-001",
      "dimension": "clarity",
      "description": "Extremely vague language",
      "suggestion": "Rewrite with specific, measurable terms"
    },
    {
      "severity": "major",
      "requirement_id": "NAV-FUNC-002",
      "dimension": "clarity",
      "description": "Ambiguous requirement text",
      "suggestion": "Clarify what 'process data' means specifically"
    },
    {
      "severity": "major",
      "requirement_id": null,
      "dimension": "completeness",
      "description": "Major functional gaps in coverage",
      "suggestion": "Review parent requirements and add missing functionality"
    }
  ]
}
```"""

# Edge case: all scores exactly at threshold
AT_THRESHOLD_VALIDATION = """```json
{
  "completeness": 0.80,
  "clarity": 0.80,
  "testability": 0.80,
  "traceability": 0.80,
  "overall_score": 0.80,
  "issues": []
}
```"""

# Edge case: barely fails
BARELY_FAILS_VALIDATION = """```json
{
  "completeness": 0.82,
  "clarity": 0.85,
  "testability": 0.75,
  "traceability": 0.78,
  "overall_score": 0.79,
  "issues": [
    {
      "severity": "major",
      "requirement_id": "NAV-FUNC-001",
      "dimension": "testability",
      "description": "Acceptance criteria need more detail",
      "suggestion": "Add specific test scenarios for edge cases"
    }
  ]
}
```"""
