"""
Request models (Pydantic).

Defines the structure of incoming API requests.
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator


class WorkflowConfigRequest(BaseModel):
    """Configuration for a new workflow."""

    subsystem: str = Field(..., min_length=1, max_length=255, description="Target subsystem name")
    domain: str = Field(default="generic", description="Domain context")
    subsystem_id: Optional[str] = Field(default=None, description="Subsystem ID for domain-aware processing")
    review_mode: Literal["before", "after"] = Field(default="before", description="Human review timing")
    analysis_mode: Literal["standard", "thorough"] = Field(default="standard", description="Analysis depth")
    quality_threshold: float = Field(default=0.80, ge=0.7, le=0.95, description="Quality gate threshold")
    max_iterations: int = Field(default=3, ge=1, le=10, description="Maximum refinement iterations")

    @field_validator("subsystem")
    @classmethod
    def validate_subsystem(cls, v: str) -> str:
        """Validate subsystem name."""
        if not v.strip():
            raise ValueError("Subsystem name cannot be empty")
        return v.strip()


class HumanReviewRequest(BaseModel):
    """Human review feedback submission."""

    action: Literal["approve", "revise"] = Field(..., description="Review action")
    feedback: Optional[str] = Field(default=None, description="Optional revision feedback")

    @field_validator("feedback")
    @classmethod
    def validate_feedback(cls, v: Optional[str], info) -> Optional[str]:
        """Ensure feedback is provided when action is revise."""
        if info.data.get("action") == "revise" and not v:
            raise ValueError("Feedback is required when action is 'revise'")
        return v
