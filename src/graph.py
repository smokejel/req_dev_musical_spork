"""
LangGraph workflow assembly for requirements decomposition.

This module defines the complete state graph that orchestrates the
4-node workflow: Extract → Analyze → Decompose → Validate.

The graph includes:
- Conditional routing based on validation results
- Human-in-the-loop review points
- State persistence with disk-based checkpointing
- Error handling and recovery
"""

import time
import sqlite3
from pathlib import Path
from typing import Literal, Dict, Any, Callable
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from rich.console import Console
from rich.panel import Panel

from src.state import DecompositionState
from src.nodes.extract_node import extract_node
from src.nodes.analyze_node import analyze_node
from src.nodes.decompose_node import decompose_node
from src.nodes.validate_node import validate_node
from src.nodes.human_review_node import human_review_node
from src.nodes.document_node import document_node
from src.utils.cost_tracker import get_cost_tracker
from config.observability_config import ObservabilityConfig, LANGSMITH_ACTIVE

console = Console()


def estimate_workflow_cost(state: DecompositionState) -> Dict[str, float]:
    """
    Estimate workflow cost based on document size and iterations.

    This provides a rough cost estimate when precise token tracking isn't available.
    Uses heuristics based on typical token usage patterns.

    Args:
        state: Final decomposition state

    Returns:
        Dict with 'total_cost' and 'cost_breakdown' by node

    Note:
        For precise cost tracking, enable LangSmith integration.
    """
    from config.llm_config import (
        GEMINI_2_5_FLASH_LITE, CLAUDE_SONNET_3_5,
        GPT_5_NANO, GEMINI_2_5_FLASH
    )

    # Estimate token usage based on state data
    extracted_count = len(state.get('extracted_requirements', []))
    decomposed_count = len(state.get('decomposed_requirements', []))
    iteration_count = state.get('iteration_count', 0)

    # Cost estimation heuristics (based on observed patterns)
    # These are rough estimates - actual costs may vary ±30%

    costs = {}

    # Extract node (Gemini 2.5 Flash-Lite)
    # ~1K input tokens per requirement + 200 output tokens per requirement
    extract_input_tokens = extracted_count * 1000
    extract_output_tokens = extracted_count * 200
    costs['extract'] = (
        (extract_input_tokens / 1000) * GEMINI_2_5_FLASH_LITE.cost_per_1k_input +
        (extract_output_tokens / 1000) * GEMINI_2_5_FLASH_LITE.cost_per_1k_output
    )

    # Analyze node (Claude Sonnet 3.5)
    # ~5K input tokens + ~2K output tokens
    analyze_input_tokens = 5000
    analyze_output_tokens = 2000
    costs['analyze'] = (
        (analyze_input_tokens / 1000) * CLAUDE_SONNET_3_5.cost_per_1k_input +
        (analyze_output_tokens / 1000) * CLAUDE_SONNET_3_5.cost_per_1k_output
    )

    # Decompose node (GPT-5 Nano) - multiply by iterations
    # ~3K input tokens per decomposed requirement + 500 output tokens
    decompose_input_tokens = decomposed_count * 3000 * (iteration_count + 1)
    decompose_output_tokens = decomposed_count * 500 * (iteration_count + 1)
    costs['decompose'] = (
        (decompose_input_tokens / 1000) * GPT_5_NANO.cost_per_1k_input +
        (decompose_output_tokens / 1000) * GPT_5_NANO.cost_per_1k_output
    )

    # Validate node (Gemini 2.5 Flash) - multiply by iterations
    # ~2K input tokens per decomposed requirement + 300 output tokens
    validate_input_tokens = decomposed_count * 2000 * (iteration_count + 1)
    validate_output_tokens = decomposed_count * 300 * (iteration_count + 1)
    costs['validate'] = (
        (validate_input_tokens / 1000) * GEMINI_2_5_FLASH.cost_per_1k_input +
        (validate_output_tokens / 1000) * GEMINI_2_5_FLASH.cost_per_1k_output
    )

    # Document node (minimal cost, mostly I/O)
    costs['document'] = 0.001  # Negligible

    total_cost = sum(costs.values())

    return {
        'total_cost': total_cost,
        'cost_breakdown': costs
    }


def route_after_validation(state: DecompositionState) -> Literal["pass", "revise", "human_review"]:
    """
    Route based on validation results.

    Routing Logic:
    1. If errors exist → human_review
    2. If iteration limit reached → human_review
    3. If validation passed → pass (to documentation)
    4. If human review explicitly requested → human_review
    5. Otherwise → revise (back to decompose)

    Args:
        state: Current decomposition state

    Returns:
        Routing decision: "pass", "revise", or "human_review"
    """
    # Check for fatal errors
    errors = state.get("errors", [])
    if errors and len(errors) > 0:
        return "human_review"

    # Check iteration limit
    iteration_count = state.get("iteration_count", 0)
    max_iterations = state.get("max_iterations", 3)
    if iteration_count >= max_iterations:
        return "human_review"

    # Check quality gate
    validation_passed = state.get("validation_passed", False)
    if validation_passed:
        return "pass"

    # Check if human review explicitly requested
    requires_human = state.get("requires_human_review", False)
    if requires_human:
        return "human_review"

    # Default: revise (send back to decompose)
    return "revise"


def route_after_human_review(state: DecompositionState) -> Literal["approved", "revise", "decompose"]:
    """
    Route based on human decision after review.

    Context-aware routing:
    - If decomposition hasn't occurred yet (pre-decomposition review), route to decompose
    - If decomposition has occurred (post-validation review), route to document
    - If revision requested, always route to decompose

    Args:
        state: Current decomposition state

    Returns:
        "approved" if human approved post-validation (route to document)
        "decompose" if human approved pre-decomposition (route to decompose)
        "revise" if human requested changes
    """
    human_feedback = state.get("human_feedback", "").lower()

    # Check for explicit revision request first (takes priority)
    if "revise" in human_feedback:
        return "revise"

    # Check for approval keywords
    if any(keyword in human_feedback for keyword in ["approve", "accept", "good", "ok"]):
        # Context-aware routing: check if decomposition has occurred
        decomposed_reqs = state.get("decomposed_requirements", [])

        if not decomposed_reqs:
            # Pre-decomposition review - route to decompose node
            return "decompose"
        else:
            # Post-validation review - route to document node
            return "approved"

    # Default: revise (safer to assume revision needed if unclear)
    return "revise"


def route_after_analyze(state: DecompositionState) -> Literal["decompose", "human_review"]:
    """
    Route after analysis - optionally allow human review before decomposition.

    Args:
        state: Current decomposition state

    Returns:
        "human_review" if review_before_decompose is True, else "decompose"
    """
    # Check if pre-decomposition review is requested
    review_before = state.get("review_before_decompose", False)
    if review_before:
        return "human_review"

    return "decompose"


def _get_node_completion_details(node_name: str, state: Dict[str, Any]) -> str:
    """
    Extract meaningful completion details from state for progress display.

    Args:
        node_name: Name of the node that completed
        state: State dict after node execution

    Returns:
        Human-readable completion message
    """
    if node_name == "extract":
        count = len(state.get("extracted_requirements", []))
        return f"Extracted {count} requirements"

    elif node_name == "analyze":
        strategy = state.get("decomposition_strategy", {})
        if strategy:
            return "Generated decomposition strategy"
        return "Analysis complete"

    elif node_name == "decompose":
        count = len(state.get("decomposed_requirements", []))
        if count == 0:
            return "No requirements allocated to subsystem"
        return f"Decomposed {count} requirements"

    elif node_name == "validate":
        metrics = state.get("quality_metrics", {})
        score = metrics.get("overall_score", 0.0)
        passed = state.get("validation_passed", False)
        status = "PASSED" if passed else "NEEDS REVIEW"
        return f"Quality score: {score:.2f} ({status})"

    elif node_name == "document":
        return "Documentation complete"

    return "Complete"


def _execute_node_with_progress(
    node_name: str,
    node_func: Callable,
    state: Dict[str, Any],
    node_num: int,
    total_nodes: int
) -> Dict[str, Any]:
    """
    Execute a workflow node with progress feedback.

    Args:
        node_name: Name of the node for display
        node_func: The node function to execute
        state: Current state
        node_num: Current node number (for progress display)
        total_nodes: Total number of nodes (for progress display)

    Returns:
        Updated state after node execution
    """
    # Node name mapping for user-friendly display
    display_names = {
        "extract": "Extracting Requirements",
        "analyze": "Analyzing System Context",
        "decompose": "Decomposing Requirements",
        "validate": "Validating Quality",
        "human_review": "Human Review",
        "document": "Generating Documentation"
    }

    display_name = display_names.get(node_name, node_name.title())

    # Check budget before execution (Phase 5.1 - Cost Management)
    if ObservabilityConfig.COST_TRACKING_ENABLED:
        cost_tracker = get_cost_tracker()
        is_ok, warning = cost_tracker.check_budget()

        if not is_ok:
            console.print(f"\n[bold red]{warning}[/bold red]")
            raise RuntimeError(f"Budget exceeded: {warning}")

        if warning:
            console.print(f"[yellow]{warning}[/yellow]")

    # Start message
    console.print(f"\n[bold cyan][{node_num}/{total_nodes}] {display_name}...[/bold cyan]")

    # Track timing
    start_time = time.time()

    try:
        # Execute node
        result = node_func(state)

        # Calculate duration
        duration = time.time() - start_time

        # Store timing in state (Phase 4.2 - Observability)
        timing_breakdown = result.get('timing_breakdown', {})
        timing_breakdown[node_name] = duration
        result['timing_breakdown'] = timing_breakdown

        # Get current cost for display (Phase 5.1)
        cost_display = ""
        if ObservabilityConfig.COST_TRACKING_ENABLED:
            cost_tracker = get_cost_tracker()
            current_total = cost_tracker.get_current_total()
            if current_total > 0:
                cost_display = f" | ${current_total:.4f}"

        # Success message with context-specific details
        details = _get_node_completion_details(node_name, result)
        console.print(f"[green]  ✓ {details} ({duration:.1f}s{cost_display})[/green]")

        return result

    except Exception as e:
        duration = time.time() - start_time
        console.print(f"[red]  ✗ Failed: {str(e)[:100]} ({duration:.1f}s)[/red]")
        raise


def create_decomposition_graph() -> StateGraph:
    """
    Create the complete LangGraph workflow for requirements decomposition.

    Graph Structure:

        START
          ↓
        extract (RequirementsAnalystAgent)
          ↓
        analyze (SystemArchitectAgent)
          ↓
        [Optional: human_review if review_before_decompose=True]
          ↓
        decompose (RequirementsEngineerAgent)
          ↓
        validate (QualityAssuranceAgent)
          ↓
        [Conditional Routing]
          ├─ pass → document → END
          ├─ revise → decompose (loop)
          └─ human_review → [approved → document, revise → decompose]

    Returns:
        Compiled StateGraph with checkpointing enabled
    """
    # Initialize graph with state schema
    workflow = StateGraph(DecompositionState)

    # Add all nodes with progress tracking
    # Note: human_review doesn't get wrapped (it has its own interactive UI)
    workflow.add_node("extract", lambda s: _execute_node_with_progress("extract", extract_node, s, 1, 5))
    workflow.add_node("analyze", lambda s: _execute_node_with_progress("analyze", analyze_node, s, 2, 5))
    workflow.add_node("decompose", lambda s: _execute_node_with_progress("decompose", decompose_node, s, 3, 5))
    workflow.add_node("validate", lambda s: _execute_node_with_progress("validate", validate_node, s, 4, 5))
    workflow.add_node("human_review", human_review_node)
    workflow.add_node("document", lambda s: _execute_node_with_progress("document", document_node, s, 5, 5))

    # Set entry point
    workflow.set_entry_point("extract")

    # Add sequential edges
    workflow.add_edge("extract", "analyze")

    # Optional pre-decomposition review
    workflow.add_conditional_edges(
        "analyze",
        route_after_analyze,
        {
            "decompose": "decompose",
            "human_review": "human_review"
        }
    )

    # Decompose → validate
    workflow.add_edge("decompose", "validate")

    # Conditional routing after validation
    workflow.add_conditional_edges(
        "validate",
        route_after_validation,
        {
            "pass": "document",
            "revise": "decompose",  # Loop back to decompose
            "human_review": "human_review"
        }
    )

    # Human review routing
    workflow.add_conditional_edges(
        "human_review",
        route_after_human_review,
        {
            "approved": "document",    # Post-validation approval → document
            "revise": "decompose",     # Revision request → decompose
            "decompose": "decompose"   # Pre-decomposition approval → decompose
        }
    )

    # Document generation ends workflow
    workflow.add_edge("document", END)

    # Set up state persistence with disk-based checkpointing (Phase 4.1)
    # SqliteSaver enables resume functionality and persistent state across sessions
    checkpoint_dir = Path("checkpoints")
    checkpoint_dir.mkdir(exist_ok=True)

    # Create SQLite connection for checkpointing
    db_path = str(checkpoint_dir / "decomposition_state.db")
    conn = sqlite3.connect(db_path, check_same_thread=False)

    # Create SqliteSaver with the connection
    checkpointer = SqliteSaver(conn)

    # Compile and return graph
    return workflow.compile(checkpointer=checkpointer)


def generate_checkpoint_id(state: DecompositionState) -> str:
    """
    Generate a unique checkpoint ID for state persistence.

    Format: {timestamp}_{subsystem_slug}
    Example: 20251031_143022_train_management

    Args:
        state: Current decomposition state

    Returns:
        Unique checkpoint ID string (alphanumeric + underscores only)
    """
    from datetime import datetime
    import re

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    subsystem = state.get("target_subsystem", "unknown")

    # Remove all special characters except spaces and hyphens, then convert to underscores
    subsystem_slug = re.sub(r'[^a-zA-Z0-9\s\-]', '', subsystem)  # Remove special chars
    subsystem_slug = subsystem_slug.lower().replace(" ", "_").replace("-", "_")

    return f"{timestamp}_{subsystem_slug}"


def get_graph_visualization() -> str:
    """
    Generate a text-based visualization of the graph structure.

    Returns:
        ASCII art representation of the workflow graph
    """
    visualization = """
    ┌────────────────────────────────────────────────────────────────┐
    │           Requirements Decomposition Workflow (LangGraph)      │
    └────────────────────────────────────────────────────────────────┘

                                START
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │   EXTRACT NODE          │
                    │   RequirementsAnalyst   │
                    │   Parses spec document  │
                    └─────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │   ANALYZE NODE          │
                    │   SystemArchitect       │
                    │   Creates strategy      │
                    └─────────────────────────┘
                                  │
                  ┌───────────────┴───────────────┐
                  │ review_before_decompose?      │
                  └───────────────┬───────────────┘
                          YES │   │ NO
                              │   ▼
                              │ ┌─────────────────────────┐
                              │ │   DECOMPOSE NODE        │
                              │ │   RequirementsEngineer  │
                              │ │   Creates detailed reqs │
                              │ └─────────────────────────┘
                              │           │
                              │           ▼
                              │ ┌─────────────────────────┐
                              │ │   VALIDATE NODE         │
                              │ │   QualityAssurance      │
                              │ │   Checks quality gate   │
                              │ └─────────────────────────┘
                              │           │
                              │   ┌───────┴───────┐
                              │   │  Quality OK?  │
                              │   └───┬───────┬───┘
                              │       │       │
                              │    PASS    FAIL
                              │       │       │
                              │       │       ├─── iterations < max? ──► REVISE (loop back)
                              │       │       │
                              │       │       └─── iterations ≥ max ──► HUMAN REVIEW
                              │       │
                              └───────┼─────────────────┐
                                      │                 │
                                      ▼                 ▼
                        ┌─────────────────────┐  ┌─────────────────────┐
                        │   DOCUMENT NODE     │  │   HUMAN REVIEW      │
                        │   Generate outputs  │  │   Interactive CLI   │
                        └─────────────────────┘  └─────────────────────┘
                                      │                 │
                                      │        ┌────────┴────────┐
                                      │        │   Approved?     │
                                      │        └────┬────────┬───┘
                                      │          YES│        │NO
                                      │             │        └──► REVISE (loop back)
                                      │             │
                                      ▼             ▼
                                    END           END

    Key Features:
    - Iterative refinement loop (validate → decompose)
    - Human-in-the-loop at quality gate failures
    - Optional pre-decomposition review
    - State persistence with SQLite checkpointing
    - Error handling with graceful degradation
    """
    return visualization


# Export main functions
__all__ = [
    "create_decomposition_graph",
    "route_after_validation",
    "route_after_human_review",
    "route_after_analyze",
    "generate_checkpoint_id",
    "get_graph_visualization"
]
