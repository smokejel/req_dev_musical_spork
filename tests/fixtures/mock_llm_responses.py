"""
Pre-built mock LLM responses for various test scenarios.

This module contains realistic LLM response data for testing without
making actual API calls.
"""

# Successful extraction responses
VALID_EXTRACTION_RESPONSE = '''```json
[
    {
        "id": "EXTRACT-FUNC-001",
        "text": "The system shall authenticate users using OAuth2",
        "type": "functional",
        "source_reference": "Section 3.1"
    },
    {
        "id": "EXTRACT-PERF-001",
        "text": "The system shall process requests within 500ms",
        "type": "performance",
        "source_reference": "Section 3.2"
    }
]
```'''

# Response with alternative type formats
ALTERNATIVE_TYPE_FORMAT_RESPONSE = '''```json
[
    {
        "id": "EXTRACT-FUNC-001",
        "text": "Test requirement",
        "type": "FUNCTIONAL",
        "source_reference": "Section 1"
    },
    {
        "id": "EXTRACT-PERF-001",
        "text": "Test performance",
        "type": "PERFORMANCE",
        "source_reference": "Section 2"
    }
]
```'''

# Empty results
EMPTY_EXTRACTION_RESPONSE = '''```json
[]
```'''

# Malformed JSON responses
MALFORMED_JSON = "This is not valid JSON at all"

INCOMPLETE_JSON = '''```json
[
    {
        "id": "EXTRACT-FUNC-001",
        "text": "Missing type field"
    }
]
```'''

NON_ARRAY_RESPONSE = '''```json
{
    "id": "EXTRACT-FUNC-001",
    "text": "Not an array",
    "type": "functional"
}
```'''

# Response without markdown blocks
PLAIN_JSON_RESPONSE = '''[
    {
        "id": "EXTRACT-FUNC-001",
        "text": "Plain JSON without markdown",
        "type": "functional",
        "source_reference": "Section 1"
    }
]'''

# Large response (multiple requirements)
LARGE_EXTRACTION_RESPONSE = '''```json
[
    {
        "id": "EXTRACT-FUNC-001",
        "text": "Requirement 1",
        "type": "functional",
        "source_reference": "Section 1"
    },
    {
        "id": "EXTRACT-FUNC-002",
        "text": "Requirement 2",
        "type": "functional",
        "source_reference": "Section 1"
    },
    {
        "id": "EXTRACT-FUNC-003",
        "text": "Requirement 3",
        "type": "functional",
        "source_reference": "Section 1"
    },
    {
        "id": "EXTRACT-PERF-001",
        "text": "Performance requirement 1",
        "type": "performance",
        "source_reference": "Section 2"
    },
    {
        "id": "EXTRACT-PERF-002",
        "text": "Performance requirement 2",
        "type": "performance",
        "source_reference": "Section 2"
    },
    {
        "id": "EXTRACT-CONS-001",
        "text": "Constraint requirement 1",
        "type": "constraint",
        "source_reference": "Section 3"
    },
    {
        "id": "EXTRACT-INTF-001",
        "text": "Interface requirement 1",
        "type": "interface",
        "source_reference": "Section 4"
    }
]
```'''
