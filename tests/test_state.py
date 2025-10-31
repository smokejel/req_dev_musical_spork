"""
Unit tests for state schema definitions.

Tests all Pydantic models and the TypedDict state object.
"""

import pytest
from pydantic import ValidationError

from src.state import (
    Requirement,
    RequirementType,
    SystemContext,
    DecompositionStrategy,
    DetailedRequirement,
    QualityIssue,
    QualitySeverity,
    QualityMetrics,
    TraceabilityLink,
    TraceabilityMatrix,
    ErrorType,
    ErrorLog,
    DecompositionState,
    create_initial_state
)


# ============================================================================
# Requirement Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.phase1
class TestRequirement:
    """Test the Requirement model."""

    def test_valid_requirement(self):
        """Test creating a valid requirement."""
        req = Requirement(
            id="EXTRACT-FUNC-001",
            text="The system shall process user input",
            type=RequirementType.FUNCTIONAL,
            source_section="Section 3.1"
        )

        assert req.id == "EXTRACT-FUNC-001"
        assert req.text == "The system shall process user input"
        assert req.type == RequirementType.FUNCTIONAL
        assert req.source_section == "Section 3.1"

    def test_requirement_without_source_section(self):
        """Test requirement without optional source_section."""
        req = Requirement(
            id="EXTRACT-PERF-042",
            text="Response time shall be under 100ms",
            type=RequirementType.PERFORMANCE
        )

        assert req.source_section is None

    def test_invalid_id_format(self):
        """Test that invalid ID format raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Requirement(
                id="REQ-001",  # Wrong format
                text="Test",
                type=RequirementType.FUNCTIONAL
            )

        assert "PREFIX-TYPE-NNN" in str(exc_info.value)

    def test_invalid_id_type(self):
        """Test that invalid type in ID raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Requirement(
                id="EXTRACT-INVALID-001",
                text="Test",
                type=RequirementType.FUNCTIONAL
            )

        # Check that the error mentions the valid types (format may vary)
        error_str = str(exc_info.value)
        assert "FUNC" in error_str and "PERF" in error_str and "CONS" in error_str and "INTF" in error_str

    def test_invalid_id_number_format(self):
        """Test that invalid number format raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Requirement(
                id="EXTRACT-FUNC-1",  # Not 3 digits
                text="Test",
                type=RequirementType.FUNCTIONAL
            )

        assert "3 digits" in str(exc_info.value)

    def test_empty_id(self):
        """Test that empty ID raises validation error."""
        with pytest.raises(ValidationError):
            Requirement(
                id="",
                text="Test",
                type=RequirementType.FUNCTIONAL
            )


# ============================================================================
# SystemContext Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.phase1
class TestSystemContext:
    """Test the SystemContext model."""

    def test_valid_system_context(self):
        """Test creating a valid system context."""
        context = SystemContext(
            subsystem="Navigation Subsystem",
            description="Handles GPS and route planning",
            constraints=["Must work offline", "Max 2s route calculation"],
            interfaces=["GPS Module", "Map Database"],
            assumptions=["GPS signal available 95% of time"]
        )

        assert context.subsystem == "Navigation Subsystem"
        assert len(context.constraints) == 2
        assert len(context.interfaces) == 2
        assert len(context.assumptions) == 1

    def test_empty_lists_default(self):
        """Test that optional lists default to empty."""
        context = SystemContext(
            subsystem="Test",
            description="Test subsystem"
        )

        assert context.constraints == []
        assert context.interfaces == []
        assert context.assumptions == []


# ============================================================================
# DecompositionStrategy Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.phase1
class TestDecompositionStrategy:
    """Test the DecompositionStrategy model."""

    def test_valid_strategy(self):
        """Test creating a valid decomposition strategy."""
        strategy = DecompositionStrategy(
            allocation_rules=["All FUNC requirements go to software layer"],
            traceability_rules=["Each child must reference parent ID"],
            decomposition_depth=2,
            naming_convention="NAV-{TYPE}-{NNN}",
            acceptance_criteria_required=True
        )

        assert len(strategy.allocation_rules) == 1
        assert strategy.decomposition_depth == 2
        assert strategy.acceptance_criteria_required is True

    def test_invalid_depth_too_low(self):
        """Test that depth < 1 raises validation error."""
        with pytest.raises(ValidationError):
            DecompositionStrategy(
                allocation_rules=["Rule 1"],
                traceability_rules=["Rule 1"],
                decomposition_depth=0,  # Too low
                naming_convention="TEST-{TYPE}-{NNN}"
            )

    def test_invalid_depth_too_high(self):
        """Test that depth > 3 raises validation error."""
        with pytest.raises(ValidationError):
            DecompositionStrategy(
                allocation_rules=["Rule 1"],
                traceability_rules=["Rule 1"],
                decomposition_depth=4,  # Too high
                naming_convention="TEST-{TYPE}-{NNN}"
            )


# ============================================================================
# QualityMetrics Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.phase1
class TestQualityMetrics:
    """Test the QualityMetrics model."""

    def test_valid_metrics(self):
        """Test creating valid quality metrics."""
        metrics = QualityMetrics(
            completeness=0.85,
            clarity=0.90,
            testability=0.80,
            traceability=0.95,
            overall_score=0.875,
            issues=[]
        )

        assert metrics.completeness == 0.85
        assert metrics.overall_score == 0.875

    def test_score_out_of_range(self):
        """Test that scores outside [0, 1] raise validation error."""
        with pytest.raises(ValidationError):
            QualityMetrics(
                completeness=1.5,  # Too high
                clarity=0.9,
                testability=0.8,
                traceability=0.9,
                overall_score=0.9
            )


# ============================================================================
# TraceabilityMatrix Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.phase1
class TestTraceabilityMatrix:
    """Test the TraceabilityMatrix model."""

    def test_get_children(self):
        """Test getting children of a parent requirement."""
        matrix = TraceabilityMatrix(
            links=[
                TraceabilityLink(parent_id="SYS-FUNC-001", child_id="NAV-FUNC-001"),
                TraceabilityLink(parent_id="SYS-FUNC-001", child_id="NAV-FUNC-002"),
                TraceabilityLink(parent_id="SYS-FUNC-002", child_id="NAV-FUNC-003"),
            ]
        )

        children = matrix.get_children("SYS-FUNC-001")
        assert len(children) == 2
        assert "NAV-FUNC-001" in children
        assert "NAV-FUNC-002" in children

    def test_get_parent(self):
        """Test getting parent of a child requirement."""
        matrix = TraceabilityMatrix(
            links=[
                TraceabilityLink(parent_id="SYS-FUNC-001", child_id="NAV-FUNC-001"),
            ]
        )

        parent = matrix.get_parent("NAV-FUNC-001")
        assert parent == "SYS-FUNC-001"

    def test_get_parent_not_found(self):
        """Test getting parent when child has no parent."""
        matrix = TraceabilityMatrix(links=[])

        parent = matrix.get_parent("NAV-FUNC-999")
        assert parent is None


# ============================================================================
# ErrorLog Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.phase1
class TestErrorLog:
    """Test the ErrorLog model."""

    def test_valid_error_log(self):
        """Test creating a valid error log entry."""
        log = ErrorLog(
            timestamp="2025-10-30T12:00:00Z",
            error_type=ErrorType.TRANSIENT,
            node="extract",
            message="Rate limit exceeded",
            details={"retry_after": 60}
        )

        assert log.error_type == ErrorType.TRANSIENT
        assert log.node == "extract"
        assert log.details["retry_after"] == 60


# ============================================================================
# DecompositionState Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.phase1
class TestDecompositionState:
    """Test the DecompositionState TypedDict."""

    def test_create_initial_state(self):
        """Test creating an initial state with helper function."""
        state = create_initial_state(
            spec_document_path="/path/to/spec.txt",
            target_subsystem="Navigation",
            review_before_decompose=True,
            quality_threshold=0.85,
            max_iterations=5
        )

        assert state['spec_document_path'] == "/path/to/spec.txt"
        assert state['target_subsystem'] == "Navigation"
        assert state['review_before_decompose'] is True
        assert state['quality_threshold'] == 0.85
        assert state['max_iterations'] == 5
        assert state['iteration_count'] == 0
        assert state['fallback_count'] == 0
        assert state['validation_passed'] is False
        assert state['requires_human_review'] is False
        assert state['errors'] == []
        assert state['error_log'] == []

    def test_state_with_default_values(self):
        """Test creating state with default values."""
        state = create_initial_state(
            spec_document_path="/path/to/spec.txt",
            target_subsystem="Power"
        )

        assert state['quality_threshold'] == 0.80  # Default
        assert state['max_iterations'] == 3  # Default
        assert state['review_before_decompose'] is False  # Default


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.phase1
class TestModelIntegration:
    """Test integration between different models."""

    def test_requirement_to_detailed_requirement(self):
        """Test converting Requirement to DetailedRequirement."""
        base_req = Requirement(
            id="SYS-FUNC-001",
            text="System shall authenticate users",
            type=RequirementType.FUNCTIONAL
        )

        detailed_req = DetailedRequirement(
            id="AUTH-FUNC-001",
            text="Authentication module shall validate username and password",
            type=RequirementType.FUNCTIONAL,
            parent_id=base_req.id,
            subsystem="Authentication",
            acceptance_criteria=[
                "Username must be valid email format",
                "Password must meet complexity requirements"
            ],
            rationale="Derived from system-level authentication requirement"
        )

        assert detailed_req.parent_id == base_req.id
        assert detailed_req.type == base_req.type
        assert len(detailed_req.acceptance_criteria) == 2

    def test_full_traceability_chain(self):
        """Test a complete traceability chain."""
        # Create traceability matrix
        matrix = TraceabilityMatrix(
            links=[
                TraceabilityLink(parent_id="SYS-FUNC-001", child_id="NAV-FUNC-001"),
                TraceabilityLink(parent_id="NAV-FUNC-001", child_id="NAV-FUNC-001-A"),
                TraceabilityLink(parent_id="NAV-FUNC-001", child_id="NAV-FUNC-001-B"),
            ]
        )

        # Verify two-level hierarchy
        level_1_children = matrix.get_children("SYS-FUNC-001")
        assert len(level_1_children) == 1
        assert "NAV-FUNC-001" in level_1_children

        level_2_children = matrix.get_children("NAV-FUNC-001")
        assert len(level_2_children) == 2
        assert "NAV-FUNC-001-A" in level_2_children
        assert "NAV-FUNC-001-B" in level_2_children

        # Verify parent lookup
        assert matrix.get_parent("NAV-FUNC-001-A") == "NAV-FUNC-001"
        assert matrix.get_parent("NAV-FUNC-001") == "SYS-FUNC-001"
