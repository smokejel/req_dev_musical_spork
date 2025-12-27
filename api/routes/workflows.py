"""
Workflow management endpoints.

Handles workflow creation, execution, status tracking, and results retrieval.
"""

from datetime import datetime
from typing import List, Optional
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    HTTPException,
    status,
    Query,
)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from api.models.database import WorkflowRun, WorkflowStatus, get_db
from api.models.requests import WorkflowConfigRequest
from api.models.responses import (
    UploadResponse,
    StartWorkflowResponse,
    WorkflowStatusResponse,
    WorkflowConfigResponse,
    RecentWorkflowsResponse,
)
from api.middleware.auth import verify_api_key, verify_api_key_query
from api.utils.file_handler import FileHandler
from api.utils.state_transformer import transform_workflow_state

# Import existing backend components
from src.state import create_initial_state
from src.graph import create_decomposition_graph

# Import Phase 2 services
from api.services.workflow_runner import get_workflow_runner
from api.services.sse_manager import get_sse_manager
from sse_starlette.sse import EventSourceResponse

# Import Phase 3 services
from api.services.export_service import ExportService

router = APIRouter(
    prefix="/api/workflows",
    tags=["Workflows"],
    # Note: Auth moved to individual endpoints to allow query param auth for SSE
)


@router.post("/upload", response_model=UploadResponse, dependencies=[Depends(verify_api_key)])
async def upload_workflow(
    file: UploadFile = File(..., description="Specification document"),
    subsystem: str = Form(..., description="Target subsystem name"),
    domain: str = Form(default="generic", description="Domain context"),
    subsystem_id: Optional[str] = Form(default=None, description="Subsystem ID for domain-aware"),
    review_mode: str = Form(default="before", description="Review timing: before or after"),
    analysis_mode: str = Form(default="standard", description="Analysis mode: standard or thorough"),
    quality_threshold: float = Form(default=0.80, description="Quality gate threshold"),
    max_iterations: int = Form(default=3, description="Maximum refinement iterations"),
    db: Session = Depends(get_db),
):
    """
    Upload specification document and create workflow.

    Creates a new workflow run record and saves the uploaded file.
    Returns the workflow ID for subsequent operations.
    """
    # Validate file
    FileHandler.validate_file(file)

    # Generate workflow ID
    workflow_id = FileHandler.generate_workflow_id()

    try:
        # Save file to disk
        file_path = await FileHandler.save_file(file, workflow_id, "spec")

        # Generate checkpoint ID (format: YYYYMMDD_HHMMSS_subsystem_slug)
        from datetime import datetime
        import re
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        subsystem_slug = re.sub(r'[^a-zA-Z0-9\s-]', '', subsystem)
        subsystem_slug = subsystem_slug.replace(' ', '_').replace('-', '_').lower()
        checkpoint_id = f"{timestamp}_{subsystem_slug}"

        # Create configuration
        config = {
            "subsystem": subsystem,
            "domain": domain,
            "subsystem_id": subsystem_id,
            "review_mode": review_mode,
            "analysis_mode": analysis_mode,
            "quality_threshold": quality_threshold,
            "max_iterations": max_iterations,
        }

        # Create workflow run record
        workflow_run = WorkflowRun(
            id=workflow_id,
            project_name=subsystem,  # Use subsystem as project name
            source_document=file.filename,
            status=WorkflowStatus.PENDING,
            config=config,
            checkpoint_id=checkpoint_id,
        )

        db.add(workflow_run)
        db.commit()
        db.refresh(workflow_run)

        return UploadResponse(workflow_id=workflow_id)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create workflow: {str(e)}",
        )


@router.post("/{workflow_id}/start", response_model=StartWorkflowResponse, dependencies=[Depends(verify_api_key)])
async def start_workflow(workflow_id: str, db: Session = Depends(get_db)):
    """
    Start workflow execution (Phase 2: Async).

    Starts workflow in background and returns immediately.
    Use /stream endpoint for real-time progress updates.
    """
    # Fetch workflow
    workflow = db.query(WorkflowRun).filter(WorkflowRun.id == workflow_id).first()
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found",
        )

    if workflow.status != WorkflowStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Workflow already {workflow.status}",
        )

    # Get spec file path
    spec_file = FileHandler.get_spec_file(workflow_id)
    if not spec_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specification file not found",
        )

    # Update status to processing
    workflow.status = WorkflowStatus.PROCESSING
    workflow.started_at = datetime.utcnow()
    db.commit()

    # Create initial state
    config = workflow.config
    initial_state = create_initial_state(
        spec_document_path=str(spec_file),
        target_subsystem=config["subsystem"],
        domain_name=config.get("domain", "generic"),
        subsystem_id=config.get("subsystem_id"),
        review_before_decompose=config.get("review_mode") == "before",
        quality_threshold=config.get("quality_threshold", 0.80),
        max_iterations=config.get("max_iterations", 3),
    )

    # Add checkpoint_id to state
    initial_state["checkpoint_id"] = workflow.checkpoint_id

    # Start workflow in background
    from api.models.database import SessionLocal
    runner = get_workflow_runner()
    await runner.start_workflow(workflow_id, initial_state, SessionLocal)

    return StartWorkflowResponse(
        workflow_id=workflow_id,
        status=WorkflowStatus.PROCESSING.value,
    )


@router.get("/{workflow_id}/status", response_model=WorkflowStatusResponse, dependencies=[Depends(verify_api_key)])
async def get_workflow_status(workflow_id: str, db: Session = Depends(get_db)):
    """
    Get workflow status and progress.

    Returns current status, progress metrics, and results summary.
    """
    workflow = db.query(WorkflowRun).filter(WorkflowRun.id == workflow_id).first()
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found",
        )

    # Build configuration response
    config_response = None
    if workflow.config:
        config_response = WorkflowConfigResponse(
            domain=workflow.config.get("domain", "generic"),
            target_subsystem=workflow.config.get("subsystem"),
            quality_threshold=workflow.config.get("quality_threshold", 0.80),
            max_iterations=workflow.config.get("max_iterations", 3),
            review_mode=workflow.config.get("review_mode", "before"),
            analysis_mode=workflow.config.get("analysis_mode", "standard"),
        )

    return WorkflowStatusResponse(
        id=workflow.id,
        project_name=workflow.project_name,
        source_document=workflow.source_document,
        status=workflow.status.value,
        config=config_response,
        created_at=workflow.created_at,
        started_at=workflow.started_at,
        completed_at=workflow.completed_at,
        current_node=workflow.current_node,
        progress=workflow.progress,
        elapsed_time=workflow.elapsed_time,
        token_count=workflow.token_count,
        extracted_count=workflow.extracted_count,
        generated_count=workflow.generated_count,
        quality_score=workflow.quality_score,
        total_cost=workflow.total_cost,
        energy_wh=workflow.energy_wh,
    )


@router.get("/recent", response_model=RecentWorkflowsResponse, dependencies=[Depends(verify_api_key)])
async def get_recent_workflows(
    limit: int = Query(default=10, ge=1, le=100, description="Maximum number of workflows to return"),
    db: Session = Depends(get_db),
):
    """
    Get recent workflows.

    Returns a list of recent workflows ordered by creation date.
    """
    workflows = (
        db.query(WorkflowRun)
        .order_by(WorkflowRun.created_at.desc())
        .limit(limit)
        .all()
    )

    workflow_responses = []
    for workflow in workflows:
        config_response = None
        if workflow.config:
            config_response = WorkflowConfigResponse(
                domain=workflow.config.get("domain", "generic"),
                target_subsystem=workflow.config.get("subsystem"),
                quality_threshold=workflow.config.get("quality_threshold", 0.80),
                max_iterations=workflow.config.get("max_iterations", 3),
                review_mode=workflow.config.get("review_mode", "before"),
                analysis_mode=workflow.config.get("analysis_mode", "standard"),
            )

        workflow_responses.append(
            WorkflowStatusResponse(
                id=workflow.id,
                project_name=workflow.project_name,
                source_document=workflow.source_document,
                status=workflow.status.value,
                config=config_response,
                created_at=workflow.created_at,
                started_at=workflow.started_at,
                completed_at=workflow.completed_at,
                current_node=workflow.current_node,
                progress=workflow.progress,
                elapsed_time=workflow.elapsed_time,
                token_count=workflow.token_count,
                extracted_count=workflow.extracted_count,
                generated_count=workflow.generated_count,
                quality_score=workflow.quality_score,
                total_cost=workflow.total_cost,
                energy_wh=workflow.energy_wh,
            )
        )

    return RecentWorkflowsResponse(workflows=workflow_responses)


@router.get("/{workflow_id}/stream", dependencies=[Depends(verify_api_key_query)])
async def stream_workflow_progress(workflow_id: str, db: Session = Depends(get_db)):
    """
    Stream workflow progress via Server-Sent Events (Phase 2).

    Returns real-time events during workflow execution:
    - node_started, node_completed
    - progress_update
    - workflow_completed, workflow_failed

    Connect to this endpoint to receive live updates.

    Note: Uses query parameter authentication (?auth=<api_key>) because
    EventSource doesn't support custom headers.
    """
    # Verify workflow exists
    workflow = db.query(WorkflowRun).filter(WorkflowRun.id == workflow_id).first()
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found",
        )

    # Get SSE manager
    sse_manager = get_sse_manager()

    # Return SSE stream
    return EventSourceResponse(sse_manager.connect(workflow_id))


@router.post("/{workflow_id}/cancel", dependencies=[Depends(verify_api_key)])
async def cancel_workflow(workflow_id: str, db: Session = Depends(get_db)):
    """
    Cancel running workflow (Phase 2).

    Stops workflow execution and updates status to FAILED.
    """
    # Verify workflow exists
    workflow = db.query(WorkflowRun).filter(WorkflowRun.id == workflow_id).first()
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found",
        )

    if workflow.status != WorkflowStatus.PROCESSING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel workflow with status {workflow.status}",
        )

    # Cancel via runner
    runner = get_workflow_runner()
    cancelled = await runner.cancel_workflow(workflow_id)

    if not cancelled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not currently running",
        )

    # Update database
    workflow.status = WorkflowStatus.FAILED
    workflow.completed_at = datetime.utcnow()
    db.commit()

    return {"message": "Workflow cancelled successfully", "workflowId": workflow_id}


@router.get("/{workflow_id}/results", dependencies=[Depends(verify_api_key)])
async def get_workflow_results(workflow_id: str, db: Session = Depends(get_db)):
    """
    Get full workflow results (Phase 3).

    Returns complete workflow details including requirements, quality metrics,
    traceability matrix, and observability data.
    """
    # Fetch workflow
    workflow = db.query(WorkflowRun).filter(WorkflowRun.id == workflow_id).first()
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found",
        )

    # Only return results if workflow is completed
    if workflow.status not in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Workflow is still {workflow.status}. Results not yet available.",
        )

    # Load final state from checkpoint
    final_state = None
    try:
        # Create graph to access checkpoint
        graph = create_decomposition_graph()

        # Get state from checkpoint
        config = {"configurable": {"thread_id": workflow.checkpoint_id}}
        state_snapshot = graph.get_state(config)

        if state_snapshot and state_snapshot.values:
            final_state = state_snapshot.values
            print(f"[DEBUG] Loaded checkpoint state keys: {list(final_state.keys())}")
        else:
            print(f"[DEBUG] No state found in checkpoint for thread_id: {workflow.checkpoint_id}")

    except Exception as e:
        # Log error but don't fail - return partial results
        print(f"Warning: Could not load checkpoint state: {e}")

    # Transform to frontend format
    response = transform_workflow_state(workflow, final_state)

    return response


@router.get("/{workflow_id}/export", dependencies=[Depends(verify_api_key)])
async def export_workflow(
    workflow_id: str,
    format: str = Query(..., description="Export format: md, docx, csv, json, zip"),
    db: Session = Depends(get_db)
):
    """
    Export workflow results in specified format (Phase 3).

    Supported formats:
    - md: Markdown report
    - docx: Word document
    - csv: Requirements table
    - json: Full state dump
    - zip: All formats bundled
    """
    # Validate format
    valid_formats = ["md", "docx", "csv", "json", "zip"]
    if format.lower() not in valid_formats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid format. Must be one of: {', '.join(valid_formats)}",
        )

    # Fetch workflow
    workflow = db.query(WorkflowRun).filter(WorkflowRun.id == workflow_id).first()
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found",
        )

    # Only export if workflow is completed
    if workflow.status != WorkflowStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Workflow must be completed to export. Current status: {workflow.status}",
        )

    # Load final state from checkpoint
    try:
        graph = create_decomposition_graph()
        config = {"configurable": {"thread_id": workflow.checkpoint_id}}
        state_snapshot = graph.get_state(config)

        if not state_snapshot or not state_snapshot.values:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow state not found in checkpoint",
            )

        final_state = state_snapshot.values

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load workflow state: {str(e)}",
        )

    # Generate export
    import io

    format_lower = format.lower()

    if format_lower == "md":
        content = ExportService.export_markdown(workflow, final_state)
        media_type = "text/markdown"
        filename = f"{workflow.project_name}_report.md"
        return StreamingResponse(
            io.BytesIO(content.encode()),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    elif format_lower == "docx":
        content = ExportService.export_docx(workflow, final_state)
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = f"{workflow.project_name}_report.docx"
        return StreamingResponse(
            io.BytesIO(content),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    elif format_lower == "csv":
        content = ExportService.export_csv(workflow, final_state)
        media_type = "text/csv"
        filename = f"{workflow.project_name}_requirements.csv"
        return StreamingResponse(
            io.BytesIO(content.encode()),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    elif format_lower == "json":
        content = ExportService.export_json(workflow, final_state)
        media_type = "application/json"
        filename = f"{workflow.project_name}_full_data.json"
        return StreamingResponse(
            io.BytesIO(content.encode()),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    elif format_lower == "zip":
        content = ExportService.export_zip(workflow, final_state)
        media_type = "application/zip"
        filename = f"{workflow.project_name}_export.zip"
        return StreamingResponse(
            io.BytesIO(content),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
