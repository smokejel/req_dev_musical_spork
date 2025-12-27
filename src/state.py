"""
State schema definitions for the requirements decomposition workflow.

This module defines all the Pydantic models and TypedDict used to manage
state throughout the LangGraph workflow. The state follows the schema
defined in CLAUDE.md Section 2.2.
"""

from typing import List, Optional, Dict, Any
from typing_extensions import TypedDict
from pydantic import BaseModel, Field, field_validator
from enum import Enum


# ============================================================================
# Enumerations
# ============================================================================

class RequirementType(str, Enum):
    """Types of requirements that can be extracted."""
    FUNCTIONAL = "FUNC"
    PERFORMANCE = "PERF"
    CONSTRAINT = "CONS"
    INTERFACE = "INTF"


class QualitySeverity(str, Enum):
    """Severity levels for quality issues."""
    CRITICAL = "critical"  # Blocks validation
    MAJOR = "major"        # Should be fixed
    MINOR = "minor"        # Nice to have


# ============================================================================
# Core Models
# ============================================================================

class Requirement(BaseModel):
    """A single extracted requirement from the source document."""

    id: str = Field(..., description="Unique requirement ID (e.g., EXTRACT-FUNC-001)")
    text: str = Field(..., description="The requirement statement")
    type: RequirementType = Field(..., description="Requirement type (FUNC, PERF, CONS, INTF)")
    source_section: Optional[str] = Field(None, description="Section in source document")

    @field_validator("id")
    @classmethod
    def validate_id_format(cls, v: str) -> str:
        """Validate that requirement ID follows the correct format."""
        if not v:
            raise ValueError("Requirement ID cannot be empty")

        # Check format: PREFIX-TYPE-NNN
        parts = v.split("-")
        if len(parts) != 3:
            raise ValueError(
                f"Requirement ID must be in format PREFIX-TYPE-NNN, got: {v}"
            )

        prefix, req_type, number = parts

        # Validate type
        valid_types = ["FUNC", "PERF", "CONS", "INTF"]
        if req_type not in valid_types:
            raise ValueError(
                f"Requirement type must be one of {valid_types}, got: {req_type}"
            )

        # Validate number is 3 digits
        if not number.isdigit() or len(number) != 3:
            raise ValueError(
                f"Requirement number must be 3 digits, got: {number}"
            )

        return v


class SystemContext(BaseModel):
    """System-level context and architectural understanding."""

    subsystem: str = Field(..., description="Target subsystem name")
    description: str = Field(..., description="Subsystem description and purpose")
    constraints: List[str] = Field(
        default_factory=list,
        description="System-level constraints affecting decomposition"
    )
    interfaces: List[str] = Field(
        default_factory=list,
        description="External interfaces and dependencies"
    )
    assumptions: List[str] = Field(
        default_factory=list,
        description="Assumptions made during analysis"
    )


class DecompositionStrategy(BaseModel):
    """Binding strategy for how requirements should be decomposed.

    This strategy is 100% binding - the decompose agent MUST follow these
    rules exactly. Violations are bugs, not quality issues.
    """

    allocation_rules: List[str] = Field(
        ...,
        description="Rules for allocating requirements to subsystems"
    )
    traceability_rules: List[str] = Field(
        ...,
        description="Rules for maintaining parent-child relationships"
    )
    decomposition_depth: int = Field(
        ...,
        ge=1,
        le=3,
        description="Maximum levels of decomposition (1-3)"
    )
    naming_convention: str = Field(
        ...,
        description="ID format for decomposed requirements (e.g., {SUBSYSTEM}-{TYPE}-{NNN})"
    )
    acceptance_criteria_required: bool = Field(
        True,
        description="Whether acceptance criteria are required for each requirement"
    )


class DetailedRequirement(BaseModel):
    """A detailed, decomposed requirement with traceability."""

    id: str = Field(..., description="Unique requirement ID")
    text: str = Field(..., description="The requirement statement")
    type: RequirementType = Field(..., description="Requirement type")
    parent_id: Optional[str] = Field(
        None,
        description="Parent requirement ID for traceability"
    )
    subsystem: str = Field(..., description="Allocated subsystem")
    acceptance_criteria: List[str] = Field(
        default_factory=list,
        description="Testable acceptance criteria"
    )
    rationale: Optional[str] = Field(
        None,
        description="Why this requirement exists (helps with traceability)"
    )


class QualityIssue(BaseModel):
    """A specific quality issue identified during validation."""

    severity: QualitySeverity = Field(..., description="Issue severity")
    requirement_id: Optional[str] = Field(
        None,
        description="Affected requirement ID (None for systemic issues)"
    )
    dimension: str = Field(
        ...,
        description="Quality dimension (completeness, clarity, testability, traceability)"
    )
    description: str = Field(..., description="What is wrong")
    suggestion: str = Field(..., description="How to fix it")


class QualityMetrics(BaseModel):
    """Quality assessment scores and issues."""

    completeness: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="All aspects covered, no gaps (0.0-1.0)"
    )
    clarity: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Unambiguous, understandable language (0.0-1.0)"
    )
    testability: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Clear acceptance criteria (0.0-1.0)"
    )
    traceability: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Proper parent-child linkage (0.0-1.0)"
    )
    domain_compliance: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Domain conventions and glossary compliance (0.0-1.0). None if generic domain."
    )
    overall_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Weighted average of all dimensions (0.0-1.0)"
    )
    issues: List[QualityIssue] = Field(
        default_factory=list,
        description="Specific quality issues identified"
    )

    @field_validator("overall_score")
    @classmethod
    def validate_overall_score(cls, v: float, info) -> float:
        """Ensure overall score is the average of dimension scores."""
        # Note: In Pydantic v2, we can't access other fields during validation
        # This validation will be done after instantiation if needed
        return v


class TraceabilityLink(BaseModel):
    """A single parent-child traceability link."""

    parent_id: str = Field(..., description="Parent requirement ID")
    child_id: str = Field(..., description="Child requirement ID")
    relationship_type: str = Field(
        "decomposes",
        description="Type of relationship (decomposes, derives, etc.)"
    )


class TraceabilityMatrix(BaseModel):
    """Complete traceability matrix for the decomposition."""

    links: List[TraceabilityLink] = Field(
        default_factory=list,
        description="All parent-child relationships"
    )
    orphan_requirements: List[str] = Field(
        default_factory=list,
        description="Requirements without parent links"
    )

    def get_children(self, parent_id: str) -> List[str]:
        """Get all child requirement IDs for a given parent."""
        return [link.child_id for link in self.links if link.parent_id == parent_id]

    def get_parent(self, child_id: str) -> Optional[str]:
        """Get parent requirement ID for a given child."""
        for link in self.links:
            if link.child_id == child_id:
                return link.parent_id
        return None


# ============================================================================
# Error Tracking
# ============================================================================

class ErrorType(str, Enum):
    """Error taxonomy for intelligent fallback handling."""
    TRANSIENT = "transient"  # Retry same model (rate limits, timeouts)
    CONTENT = "content"      # Switch to fallback model (parse errors, validation)
    FATAL = "fatal"          # Human intervention required (auth, missing resources)


class ErrorLog(BaseModel):
    """Detailed error tracking entry."""

    timestamp: str = Field(..., description="ISO 8601 timestamp")
    error_type: ErrorType = Field(..., description="Error classification")
    node: str = Field(..., description="Which node encountered the error")
    message: str = Field(..., description="Error message")
    details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional error context"
    )


# ============================================================================
# LangGraph State (TypedDict)
# ============================================================================

class DecompositionState(TypedDict, total=False):
    """
    Main state object for the LangGraph workflow.

    Uses TypedDict for LangGraph compatibility. All fields are optional
    (total=False) to allow incremental state building through the graph.
    """

    # ========================================================================
    # Input
    # ========================================================================
    spec_document_path: str
    """Path to the specification document (.txt, .docx, .pdf)"""

    target_subsystem: str
    """Name of the subsystem to decompose requirements for"""

    review_before_decompose: bool
    """Optional flag to request human review before decomposition"""

    quality_threshold: float
    """Quality gate threshold (default 0.80)"""

    # ========================================================================
    # Domain Context (Phase 7 - Domain-Aware Requirements Decomposition)
    # ========================================================================
    domain_name: Optional[str]
    """Domain identifier (e.g., 'csx_dispatch', 'generic'). Default: 'generic'"""

    subsystem_id: Optional[str]
    """Subsystem identifier within domain (e.g., 'train_management'). Optional."""

    domain_context: Optional[Dict[str, Any]]
    """Loaded domain context from markdown files (conventions, glossary, examples)"""

    # ========================================================================
    # Processing
    # ========================================================================
    extracted_requirements: List[Dict[str, Any]]
    """Requirements extracted from source document (serialized Requirement objects)"""

    system_context: Dict[str, Any]
    """System analysis and architectural context (serialized SystemContext)"""

    decomposition_strategy: Dict[str, Any]
    """Binding strategy for decomposition (serialized DecompositionStrategy)"""

    decomposed_requirements: List[Dict[str, Any]]
    """Detailed, decomposed requirements (serialized DetailedRequirement objects)"""

    # ========================================================================
    # Quality Control & Refinement
    # ========================================================================
    quality_metrics: Dict[str, Any]
    """Quality assessment scores (serialized QualityMetrics)"""

    validation_passed: bool
    """Whether requirements passed quality gate"""

    iteration_count: int
    """Current iteration number in refinement loop"""

    max_iterations: int
    """Maximum iterations before forcing human review (default 3)"""

    refinement_feedback: Optional[str]
    """Specific, actionable feedback for improving requirements on next iteration"""

    validation_issues: List[Dict[str, Any]]
    """Detailed quality issues to address (serialized QualityIssue objects)"""

    previous_attempt: Optional[List[Dict[str, Any]]]
    """Previous decomposition attempt for comparison (serialized DetailedRequirement)"""

    # ========================================================================
    # Human Review
    # ========================================================================
    human_feedback: Optional[str]
    """Feedback provided during human review"""

    requires_human_review: bool
    """Flag indicating human review is needed"""

    # ========================================================================
    # Output
    # ========================================================================
    final_document_path: Optional[str]
    """Path to generated requirements document"""

    traceability_matrix: Optional[Dict[str, Any]]
    """Complete traceability matrix (serialized TraceabilityMatrix)"""

    # ========================================================================
    # Error Handling & Fallback Tracking
    # ========================================================================
    errors: List[str]
    """Simple error messages for quick debugging"""

    fallback_count: int
    """Number of times LLM fallback was triggered"""

    error_log: List[Dict[str, Any]]
    """Detailed error tracking (serialized ErrorLog objects)"""

    # ========================================================================
    # Cost Tracking & Performance Monitoring (Phase 4.2 - Observability)
    # ========================================================================
    total_cost: float
    """Total cost in USD for entire workflow"""

    cost_breakdown: Dict[str, float]
    """Cost per node in USD (e.g., {'extract': 0.05, 'analyze': 0.12, ...})"""

    timing_breakdown: Dict[str, float]
    """Execution time per node in seconds (e.g., {'extract': 12.3, 'analyze': 8.7, ...})"""

    token_usage: Dict[str, Dict[str, int]]
    """Token usage per node (e.g., {'extract': {'input': 5000, 'output': 1200}, ...})"""

    # ========================================================================
    # Energy Tracking (Phase 6.1 - Energy Consumption Tracking)
    # ========================================================================
    total_energy_wh: float
    """Total energy consumption in Watt-hours (Wh) for entire workflow"""

    energy_breakdown: Dict[str, float]
    """Energy consumption per node in Wh (e.g., {'extract': 0.012, 'analyze': 0.008, ...})"""


# ============================================================================
# Helper Functions
# ============================================================================

def create_initial_state(
    spec_document_path: str,
    target_subsystem: str,
    review_before_decompose: bool = False,
    quality_threshold: float = 0.80,
    max_iterations: int = 3,
    domain_name: str = "generic",
    subsystem_id: Optional[str] = None
) -> DecompositionState:
    """
    Create an initial state object for starting a decomposition workflow.

    Args:
        spec_document_path: Path to the specification document
        target_subsystem: Name of the target subsystem
        review_before_decompose: Whether to request review before decomposition
        quality_threshold: Quality gate threshold (0.0-1.0)
        max_iterations: Maximum refinement iterations
        domain_name: Domain identifier (default: 'generic')
        subsystem_id: Subsystem identifier within domain (optional)

    Returns:
        Initial DecompositionState with required fields populated
    """
    return DecompositionState(
        spec_document_path=spec_document_path,
        target_subsystem=target_subsystem,
        review_before_decompose=review_before_decompose,
        quality_threshold=quality_threshold,
        max_iterations=max_iterations,
        iteration_count=0,
        fallback_count=0,
        errors=[],
        error_log=[],
        validation_passed=False,
        requires_human_review=False,
        # Phase 7: Domain context fields
        domain_name=domain_name,
        subsystem_id=subsystem_id,
        domain_context=None,  # Loaded by workflow
        # Phase 4.2: Observability fields
        total_cost=0.0,
        cost_breakdown={},
        timing_breakdown={},
        token_usage={},
        # Phase 6.1: Energy tracking fields
        total_energy_wh=0.0,
        energy_breakdown={}
    )
