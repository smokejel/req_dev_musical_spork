"""
Response models (Pydantic).

Defines the structure of API responses with camelCase field aliases
for frontend compatibility.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from api.models.database import WorkflowStatus


class UploadResponse(BaseModel):
    """Response after successful file upload."""

    workflow_id: str = Field(..., alias="workflowId", description="Generated workflow ID")
    message: str = Field(default="Workflow created successfully", description="Success message")

    model_config = ConfigDict(populate_by_name=True)


class StartWorkflowResponse(BaseModel):
    """Response after starting workflow execution."""

    workflow_id: str = Field(..., alias="workflowId")
    status: str

    model_config = ConfigDict(populate_by_name=True)


class WorkflowConfigResponse(BaseModel):
    """Workflow configuration (camelCase for frontend)."""

    domain: str
    target_subsystem: str = Field(..., alias="targetSubsystem")
    quality_threshold: float = Field(..., alias="qualityThreshold")
    max_iterations: int = Field(..., alias="maxIterations")
    review_mode: str = Field(..., alias="reviewMode")
    analysis_mode: str = Field(..., alias="analysisMode")

    model_config = ConfigDict(populate_by_name=True)


class WorkflowStatusResponse(BaseModel):
    """Workflow status and progress."""

    id: str
    project_name: str = Field(..., alias="projectName")
    source_document: str = Field(..., alias="sourceDocument")
    status: str
    config: Optional[WorkflowConfigResponse] = None

    created_at: datetime = Field(..., alias="createdAt")
    started_at: Optional[datetime] = Field(None, alias="startedAt")
    completed_at: Optional[datetime] = Field(None, alias="completedAt")

    current_node: Optional[str] = Field(None, alias="currentNode")
    progress: float = 0.0
    elapsed_time: float = Field(0.0, alias="elapsedTime")
    token_count: int = Field(0, alias="tokenCount")

    extracted_count: Optional[int] = Field(None, alias="extractedCount")
    generated_count: Optional[int] = Field(None, alias="generatedCount")
    quality_score: Optional[float] = Field(None, alias="qualityScore")

    total_cost: Optional[float] = Field(None, alias="totalCost")
    energy_wh: Optional[float] = Field(None, alias="energyWh")

    model_config = ConfigDict(populate_by_name=True)


class QualityMetricsResponse(BaseModel):
    """Quality metrics (camelCase)."""

    overall_score: float = Field(..., alias="overallScore")
    completeness: float
    clarity: float
    testability: float
    traceability: float
    domain_compliance: Optional[float] = Field(None, alias="domainCompliance")

    model_config = ConfigDict(populate_by_name=True)


class WorkflowResultsResponse(BaseModel):
    """Complete workflow results."""

    id: str
    status: str
    requirements: Optional[List[Dict[str, Any]]] = None
    quality_metrics: Optional[QualityMetricsResponse] = Field(None, alias="qualityMetrics")
    issues: Optional[List[Dict[str, Any]]] = None
    traceability_matrix: Optional[Dict[str, Any]] = Field(None, alias="traceabilityMatrix")
    total_cost: Optional[float] = Field(None, alias="totalCost")
    energy_wh: Optional[float] = Field(None, alias="energyWh")

    model_config = ConfigDict(populate_by_name=True)


class RecentWorkflowsResponse(BaseModel):
    """List of recent workflows."""

    workflows: List[WorkflowStatusResponse]
