"""
Workflow Runner Service.

Handles background execution of requirements decomposition workflows.
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path

from sqlalchemy.orm import Session

from api.models.database import WorkflowRun, WorkflowStatus
from api.services.sse_manager import get_sse_manager
from src.state import DecompositionState
from src.graph import create_decomposition_graph, estimate_workflow_energy
from src.nodes.extract_node import extract_node
from src.nodes.analyze_node import analyze_node
from src.nodes.decompose_node import decompose_node
from src.nodes.validate_node import validate_node


class WorkflowRunner:
    """
    Manages background workflow execution.

    Features:
    - Async execution with asyncio.create_task()
    - SSE event emission for real-time progress
    - Graceful cancellation support
    - Error handling and recovery
    """

    def __init__(self):
        """Initialize workflow runner."""
        # Active tasks: workflow_id -> asyncio.Task
        self.active_tasks: Dict[str, asyncio.Task] = {}

        # SSE manager for event broadcasting
        self.sse_manager = get_sse_manager()

    async def start_workflow(
        self,
        workflow_id: str,
        initial_state: DecompositionState,
        db_session_maker,
    ) -> asyncio.Task:
        """
        Start workflow execution in background.

        Args:
            workflow_id: Workflow UUID
            initial_state: Initial state for workflow
            db_session_maker: SQLAlchemy session factory

        Returns:
            Async task handle
        """
        # Create background task
        task = asyncio.create_task(
            self._run_workflow(workflow_id, initial_state, db_session_maker)
        )

        # Track task
        self.active_tasks[workflow_id] = task

        return task

    async def cancel_workflow(self, workflow_id: str) -> bool:
        """
        Cancel running workflow.

        Args:
            workflow_id: Workflow UUID

        Returns:
            True if cancelled, False if not found
        """
        task = self.active_tasks.get(workflow_id)
        if not task:
            return False

        # Cancel task
        task.cancel()

        # Emit cancellation event
        self.sse_manager.emit(workflow_id, "workflow_failed", {
            "error": "Workflow cancelled by user"
        })

        # Remove from tracking
        self.active_tasks.pop(workflow_id, None)

        return True

    def is_running(self, workflow_id: str) -> bool:
        """
        Check if workflow is currently running.

        Args:
            workflow_id: Workflow UUID

        Returns:
            True if running
        """
        task = self.active_tasks.get(workflow_id)
        return task is not None and not task.done()

    async def _run_workflow(
        self,
        workflow_id: str,
        initial_state: DecompositionState,
        db_session_maker,
    ) -> None:
        """
        Execute workflow in background.

        Args:
            workflow_id: Workflow UUID
            initial_state: Initial state
            db_session_maker: Session factory
        """
        db = db_session_maker()
        start_time = time.time()

        try:
            # Emit start event
            self.sse_manager.emit(workflow_id, "workflow_started", {
                "message": "Workflow execution started"
            })
            print(f"[DEBUG] Emitted workflow_started event for {workflow_id}")

            # Initialize cost tracking (Phase 5.1)
            from src.utils.cost_tracker import get_cost_tracker
            cost_tracker = get_cost_tracker()
            cost_tracker.start_run(run_id=workflow_id)

            # Create instrumented graph
            graph = self._create_instrumented_graph(workflow_id)

            # Run graph.invoke() in thread pool (it's synchronous)
            loop = asyncio.get_event_loop()
            final_state = await loop.run_in_executor(
                None,
                graph.invoke,
                initial_state,
                {"configurable": {"thread_id": initial_state["checkpoint_id"]}},
            )

            # Calculate energy usage
            energy_est = estimate_workflow_energy(final_state)
            final_state['total_energy_wh'] = energy_est['total_energy_wh']
            final_state['energy_breakdown'] = energy_est['energy_breakdown']

            elapsed_time = time.time() - start_time

            # Update database with results
            workflow = db.query(WorkflowRun).filter(WorkflowRun.id == workflow_id).first()
            if workflow:
                workflow.status = WorkflowStatus.COMPLETED
                workflow.completed_at = datetime.utcnow()
                workflow.elapsed_time = elapsed_time
                workflow.progress = 1.0
                workflow.current_node = None

                # Extract results
                workflow.extracted_count = len(final_state.get("extracted_requirements", []))
                workflow.generated_count = len(final_state.get("decomposed_requirements", []))

                quality_metrics = final_state.get("quality_metrics")
                if quality_metrics:
                    workflow.quality_score = quality_metrics.get("overall_score")

                workflow.total_cost = final_state.get("total_cost")
                workflow.energy_wh = final_state.get("total_energy_wh")

                # Calculate total tokens
                token_usage = final_state.get("token_usage", {})
                total_tokens = sum(
                    node_tokens.get("input_tokens", 0) + node_tokens.get("output_tokens", 0)
                    for node_tokens in token_usage.values()
                )
                workflow.token_count = total_tokens

                db.commit()

            # Emit completion event
            self.sse_manager.emit(workflow_id, "workflow_completed", {
                "totalCost": final_state.get("total_cost"),
                "totalEnergy": final_state.get("total_energy_wh"),
                "elapsedTime": elapsed_time,
            })

            # Finalize cost tracking
            from src.utils.cost_tracker import get_cost_tracker
            cost_tracker = get_cost_tracker()
            # Get subsystem from workflow config
            subsystem = workflow.config.get("subsystem", "Unknown") if workflow and workflow.config else "Unknown"
            cost_tracker.finalize_run(subsystem=subsystem, source_method='heuristic')

            # Close SSE connections
            self.sse_manager.close_connection(workflow_id)

        except asyncio.CancelledError:
            # Workflow was cancelled
            workflow = db.query(WorkflowRun).filter(WorkflowRun.id == workflow_id).first()
            if workflow:
                workflow.status = WorkflowStatus.FAILED
                workflow.completed_at = datetime.utcnow()
                workflow.elapsed_time = time.time() - start_time
                db.commit()

            raise

        except Exception as e:
            # Workflow failed
            workflow = db.query(WorkflowRun).filter(WorkflowRun.id == workflow_id).first()
            if workflow:
                workflow.status = WorkflowStatus.FAILED
                workflow.completed_at = datetime.utcnow()
                workflow.elapsed_time = time.time() - start_time
                db.commit()

            # Emit failure event
            self.sse_manager.emit(workflow_id, "workflow_failed", {
                "error": str(e)
            })

            # Close connections
            self.sse_manager.close_connection(workflow_id)

        finally:
            # Cleanup
            self.active_tasks.pop(workflow_id, None)
            db.close()

    def _create_instrumented_graph(self, workflow_id: str):
        """
        Create workflow graph with SSE instrumentation.

        Args:
            workflow_id: Workflow UUID

        Returns:
            Instrumented StateGraph
        """
        # Wrap nodes to emit SSE events
        def instrumented_extract(state: DecompositionState) -> DecompositionState:
            self.sse_manager.emit(workflow_id, "node_started", {
                "node": "extract",
                "message": "Extracting requirements from document..."
            })

            self.sse_manager.emit(workflow_id, "progress_update", {
                "progress": 0.1,
                "currentNode": "extract"
            })

            start = time.time()
            result = extract_node(state)
            duration = time.time() - start

            extracted_count = len(result.get("extracted_requirements", []))

            self.sse_manager.emit(workflow_id, "node_completed", {
                "node": "extract",
                "duration": duration,
                "message": f"Extracted {extracted_count} requirements"
            })

            self.sse_manager.emit(workflow_id, "progress_update", {
                "progress": 25,
                "currentNode": "extract"
            })

            return result

        def instrumented_analyze(state: DecompositionState) -> DecompositionState:
            self.sse_manager.emit(workflow_id, "node_started", {
                "node": "analyze",
                "message": "Analyzing system context and planning decomposition..."
            })

            self.sse_manager.emit(workflow_id, "progress_update", {
                "progress": 30,
                "currentNode": "analyze"
            })

            start = time.time()
            result = analyze_node(state)
            duration = time.time() - start

            self.sse_manager.emit(workflow_id, "node_completed", {
                "node": "analyze",
                "duration": duration,
                "message": "Generated decomposition strategy"
            })

            self.sse_manager.emit(workflow_id, "progress_update", {
                "progress": 50,
                "currentNode": "analyze"
            })

            return result

        def instrumented_decompose(state: DecompositionState) -> DecompositionState:
            iteration = state.get("iteration_count", 0)
            message = f"Decomposing requirements (iteration {iteration + 1})..."

            self.sse_manager.emit(workflow_id, "node_started", {
                "node": "decompose",
                "message": message
            })

            self.sse_manager.emit(workflow_id, "progress_update", {
                "progress": 55,
                "currentNode": "decompose"
            })

            start = time.time()
            result = decompose_node(state)
            duration = time.time() - start

            decomposed_count = len(result.get("decomposed_requirements", []))

            self.sse_manager.emit(workflow_id, "node_completed", {
                "node": "decompose",
                "duration": duration,
                "message": f"Decomposed into {decomposed_count} subsystem requirements"
            })

            self.sse_manager.emit(workflow_id, "progress_update", {
                "progress": 75,
                "currentNode": "decompose"
            })

            return result

        def instrumented_validate(state: DecompositionState) -> DecompositionState:
            self.sse_manager.emit(workflow_id, "node_started", {
                "node": "validate",
                "message": "Validating requirements quality..."
            })

            self.sse_manager.emit(workflow_id, "progress_update", {
                "progress": 80,
                "currentNode": "validate"
            })

            start = time.time()
            result = validate_node(state)
            duration = time.time() - start

            quality_metrics = result.get("quality_metrics", {})
            overall_score = quality_metrics.get("overall_score", 0.0)
            validation_passed = result.get("validation_passed", False)

            status = "PASSED" if validation_passed else "NEEDS REVISION"

            self.sse_manager.emit(workflow_id, "node_completed", {
                "node": "validate",
                "duration": duration,
                "message": f"Quality score: {overall_score:.2f} ({status})"
            })

            self.sse_manager.emit(workflow_id, "progress_update", {
                "progress": 95,
                "currentNode": "validate"
            })

            return result

        # Create graph with instrumented nodes (passes SSE-emitting wrappers)
        graph = create_decomposition_graph(
            custom_extract_node=instrumented_extract,
            custom_analyze_node=instrumented_analyze,
            custom_decompose_node=instrumented_decompose,
            custom_validate_node=instrumented_validate,
        )

        return graph


# Global workflow runner instance
_workflow_runner: Optional[WorkflowRunner] = None


def get_workflow_runner() -> WorkflowRunner:
    """
    Get global workflow runner instance.

    Returns:
        WorkflowRunner singleton
    """
    global _workflow_runner
    if _workflow_runner is None:
        _workflow_runner = WorkflowRunner()
    return _workflow_runner
