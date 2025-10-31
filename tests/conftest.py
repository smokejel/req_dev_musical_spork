"""
Pytest configuration and shared fixtures for testing.

This module provides reusable test fixtures for all test files.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any

from src.state import (
    Requirement,
    RequirementType,
    SystemContext,
    DecompositionStrategy,
    DetailedRequirement,
    QualityMetrics,
    QualityIssue,
    QualitySeverity,
    TraceabilityMatrix,
    TraceabilityLink,
    DecompositionState,
    ErrorType,
    ErrorLog,
    create_initial_state
)


# ============================================================================
# State Fixtures
# ============================================================================

@pytest.fixture
def valid_state():
    """Create a valid initial state for testing."""
    return create_initial_state(
        spec_document_path="examples/phase0_simple_spec.txt",
        target_subsystem="Test Subsystem",
        quality_threshold=0.80,
        max_iterations=3
    )


@pytest.fixture
def state_with_requirements(valid_state):
    """Create a state with extracted requirements."""
    requirements = [
        {
            "id": "EXTRACT-FUNC-001",
            "text": "The system shall authenticate users",
            "type": "functional",
            "source_section": "Section 3.1"
        },
        {
            "id": "EXTRACT-PERF-001",
            "text": "Response time shall be under 500ms",
            "type": "performance",
            "source_section": "Section 3.2"
        }
    ]

    return {
        **valid_state,
        "extracted_requirements": requirements
    }


# ============================================================================
# Model Object Fixtures
# ============================================================================

@pytest.fixture
def mock_requirement():
    """Create a mock Requirement object."""
    return Requirement(
        id="EXTRACT-FUNC-001",
        text="The system shall authenticate users",
        type=RequirementType.FUNCTIONAL,
        source_section="Section 3.1"
    )


@pytest.fixture
def mock_requirements_list():
    """Create a list of mock Requirement objects."""
    return [
        Requirement(
            id="EXTRACT-FUNC-001",
            text="The system shall authenticate users",
            type=RequirementType.FUNCTIONAL,
            source_section="Section 3.1"
        ),
        Requirement(
            id="EXTRACT-FUNC-002",
            text="The system shall log all user actions",
            type=RequirementType.FUNCTIONAL,
            source_section="Section 3.1"
        ),
        Requirement(
            id="EXTRACT-PERF-001",
            text="The system shall process requests within 500ms",
            type=RequirementType.PERFORMANCE,
            source_section="Section 3.2"
        )
    ]


@pytest.fixture
def mock_system_context():
    """Create a mock SystemContext object."""
    return SystemContext(
        subsystem="Authentication",
        description="Handles user authentication and authorization",
        constraints=["Must use OAuth2", "Max 2s login time"],
        interfaces=["User Database", "Session Store"],
        assumptions=["Network connectivity available"]
    )


# ============================================================================
# LLM Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_llm():
    """Create a mock LLM for testing."""
    mock = MagicMock()

    # Configure default successful response
    mock.invoke.return_value.content = '''```json
[
    {
        "id": "EXTRACT-FUNC-001",
        "text": "The system shall authenticate users",
        "type": "functional",
        "source_reference": "Section 3.1"
    },
    {
        "id": "EXTRACT-PERF-001",
        "text": "Response time shall be under 500ms",
        "type": "performance",
        "source_reference": "Section 3.2"
    }
]
```'''

    return mock


@pytest.fixture
def mock_llm_with_error():
    """Create a mock LLM that raises errors."""
    mock = MagicMock()
    mock.invoke.side_effect = Exception("Test error")
    return mock


# ============================================================================
# Document Text Fixtures
# ============================================================================

@pytest.fixture
def sample_document_text():
    """Sample specification document text."""
    return """
System Requirements Specification

3.1 Functional Requirements

REQ-001: The system shall authenticate users using OAuth2.

REQ-002: The system shall log all user actions to the audit database.

3.2 Performance Requirements

REQ-003: The system shall process login requests within 500ms.

REQ-004: The system shall support 1000 concurrent users.

3.3 Constraints

REQ-005: The system shall operate on Linux kernel 5.15 or later.
"""


@pytest.fixture
def empty_document_text():
    """Empty document text."""
    return ""


@pytest.fixture
def malformed_document_text():
    """Document with poor formatting."""
    return "Some text without any requirements"


# ============================================================================
# LLM Response Fixtures
# ============================================================================

@pytest.fixture
def sample_llm_json_response():
    """Sample LLM JSON response with markdown code blocks."""
    return '''```json
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
```'''


@pytest.fixture
def sample_llm_plain_response():
    """Sample LLM JSON response without markdown."""
    return '''[
    {
        "id": "EXTRACT-FUNC-001",
        "text": "Test requirement",
        "type": "functional",
        "source_reference": "Section 1"
    }
]'''


@pytest.fixture
def malformed_llm_response():
    """Malformed LLM response (invalid JSON)."""
    return "This is not valid JSON"


@pytest.fixture
def non_array_llm_response():
    """LLM response that's not a JSON array."""
    return '''{"id": "EXTRACT-FUNC-001", "text": "Test"}'''


# ============================================================================
# Error Fixtures
# ============================================================================

@pytest.fixture
def transient_error():
    """Create a transient error (rate limit)."""
    return Exception("Rate limit exceeded - 429")


@pytest.fixture
def content_error():
    """Create a content error (JSON parsing)."""
    import json
    return json.JSONDecodeError("Invalid JSON", "doc", 0)


@pytest.fixture
def fatal_error():
    """Create a fatal error (authentication)."""
    return Exception("Authentication failed - 401")


# ============================================================================
# Helper Functions
# ============================================================================

def create_mock_llm_response(content: str):
    """Helper to create a mock LLM response object."""
    mock_response = Mock()
    mock_response.content = content
    return mock_response
