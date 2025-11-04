"""
Human review node for the requirements decomposition workflow.

This node:
1. Pauses workflow execution for human review
2. Displays quality metrics and issues in formatted CLI
3. Allows human to approve or request revision
4. Captures feedback for next iteration
5. Updates state with human decision
"""

from typing import Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from src.state import DecompositionState

console = Console()


def human_review_node(state: DecompositionState) -> DecompositionState:
    """
    Pause workflow for human review and feedback.

    This node interrupts the workflow and presents quality metrics,
    validation issues, and requirement details to the human reviewer.
    The reviewer can approve, request revisions, or inspect details.

    Args:
        state: Current decomposition state

    Returns:
        Updated state with human_feedback and decision flags

    State Updates:
        - human_feedback: Human reviewer's decision and comments
        - requires_human_review: Set to False after review
        - (workflow resumes based on feedback)
    """
    # Display header
    console.print("\n" + "=" * 80, style="bold blue")
    console.print("HUMAN REVIEW REQUIRED", style="bold yellow", justify="center")
    console.print("=" * 80 + "\n", style="bold blue")

    # Display iteration context
    iteration_count = state.get("iteration_count", 0)
    max_iterations = state.get("max_iterations", 3)
    console.print(
        f"[yellow]Iteration {iteration_count}/{max_iterations}[/yellow]\n"
    )

    # Display quality metrics if available
    quality_metrics = state.get("quality_metrics")
    if quality_metrics:
        _display_quality_metrics(quality_metrics)

    # Display validation issues if available
    validation_issues = state.get("validation_issues", [])
    if validation_issues:
        _display_validation_issues(validation_issues)

    # Display errors if any
    errors = state.get("errors", [])
    if errors:
        _display_errors(errors)

    # Display subsystem requirements summary
    subsystem_requirements = state.get("subsystem_requirements", [])
    if subsystem_requirements:
        _display_requirements_summary(subsystem_requirements)

    # Get human decision
    console.print("\n" + "-" * 80)
    console.print("[bold]Review Options:[/bold]")
    console.print("  1. [green]Approve[/green] - Accept requirements as-is and generate documentation")
    console.print("  2. [yellow]Revise[/yellow] - Send back for revision with feedback")
    console.print("  3. [blue]View Details[/blue] - Inspect specific requirements")
    console.print("  4. [magenta]View Strategy[/magenta] - Review decomposition strategy")

    human_feedback = ""
    decision_approved = False

    while True:
        choice = Prompt.ask(
            "\n[bold cyan]Enter choice (1-4)[/bold cyan]",
            choices=["1", "2", "3", "4"],
            show_choices=False
        )

        if choice == "1":
            # Approve
            confirm = Confirm.ask("[green]Confirm approval?[/green]")
            if confirm:
                human_feedback = "approved"
                decision_approved = True
                console.print("\n[green]✓ Requirements approved. Proceeding to documentation generation.[/green]")
                break

        elif choice == "2":
            # Revise with feedback
            console.print("\n[yellow]Please provide revision guidance:[/yellow]")
            console.print("(Describe what needs to be fixed or improved)")
            feedback_text = Prompt.ask("[yellow]Feedback[/yellow]")

            if feedback_text.strip():
                human_feedback = f"revise: {feedback_text}"
                decision_approved = False
                console.print("\n[yellow]✓ Feedback captured. Requirements will be revised.[/yellow]")
                break
            else:
                console.print("[red]Feedback cannot be empty. Please provide guidance.[/red]")

        elif choice == "3":
            # View details
            _display_requirements_detail(subsystem_requirements)
            continue

        elif choice == "4":
            # View strategy
            strategy = state.get("decomposition_strategy")
            if strategy:
                _display_strategy_detail(strategy)
            else:
                console.print("[red]No decomposition strategy available.[/red]")
            continue

    # Return updated state
    return {
        **state,
        "human_feedback": human_feedback,
        "requires_human_review": False
    }


def _display_quality_metrics(metrics: Dict[str, Any]) -> None:
    """Display quality metrics in a formatted table."""
    console.print("[bold]Quality Assessment:[/bold]\n")

    # Create metrics table
    table = Table(title="Quality Metrics", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan", width=20)
    table.add_column("Score", style="white", width=10, justify="right")
    table.add_column("Status", style="white", width=10, justify="center")

    # Overall score
    overall_score = metrics.get("overall_score", 0.0)
    overall_status = "✅ PASS" if overall_score >= 0.80 else "❌ FAIL"
    overall_style = "green" if overall_score >= 0.80 else "red"
    table.add_row("Overall Score", f"{overall_score:.2f}", overall_status, style=overall_style)

    # Dimension scores
    dimensions = [
        ("Completeness", "completeness"),
        ("Clarity", "clarity"),
        ("Testability", "testability"),
        ("Traceability", "traceability")
    ]

    for display_name, key in dimensions:
        score = metrics.get(key, 0.0)
        status = "✓" if score >= 0.80 else "⚠"
        style = "green" if score >= 0.80 else "yellow"
        table.add_row(display_name, f"{score:.2f}", status, style=style)

    console.print(table)
    console.print()


def _display_validation_issues(issues: list) -> None:
    """Display validation issues grouped by severity."""
    console.print("[bold]Validation Issues:[/bold]\n")

    # Group by severity
    critical = [i for i in issues if i.get("severity") == "critical"]
    major = [i for i in issues if i.get("severity") == "major"]
    minor = [i for i in issues if i.get("severity") == "minor"]

    # Display critical issues
    if critical:
        console.print(f"[bold red]CRITICAL Issues ({len(critical)}):[/bold red]")
        for idx, issue in enumerate(critical[:5], 1):
            req_id = issue.get("requirement_id", "GENERAL")
            desc = issue.get("description", "")
            sugg = issue.get("suggestion", "")
            console.print(f"  {idx}. [[{req_id}]] {desc}")
            if sugg:
                console.print(f"     [dim]→ Fix: {sugg}[/dim]")
        if len(critical) > 5:
            console.print(f"     [dim]... and {len(critical) - 5} more critical issues[/dim]")
        console.print()

    # Display major issues
    if major:
        console.print(f"[bold yellow]MAJOR Issues ({len(major)}):[/bold yellow]")
        for idx, issue in enumerate(major[:5], 1):
            req_id = issue.get("requirement_id", "GENERAL")
            desc = issue.get("description", "")
            console.print(f"  {idx}. [[{req_id}]] {desc}")
        if len(major) > 5:
            console.print(f"     [dim]... and {len(major) - 5} more major issues[/dim]")
        console.print()

    # Display minor issues (limited)
    if minor and len(minor) <= 3:
        console.print(f"[bold blue]MINOR Issues ({len(minor)}):[/bold blue]")
        for idx, issue in enumerate(minor, 1):
            req_id = issue.get("requirement_id", "GENERAL")
            desc = issue.get("description", "")
            console.print(f"  {idx}. [[{req_id}]] {desc}")
        console.print()
    elif minor:
        console.print(f"[dim]({len(minor)} minor issues not shown)[/dim]\n")


def _display_errors(errors: list) -> None:
    """Display error messages."""
    console.print("[bold red]Errors:[/bold red]\n")
    for idx, error in enumerate(errors, 1):
        console.print(f"  {idx}. [red]{error}[/red]")
    console.print()


def _display_requirements_summary(requirements: list) -> None:
    """Display summary of subsystem requirements."""
    console.print(f"[bold]Generated Requirements:[/bold] {len(requirements)} total\n")

    # Count by type
    type_counts = {}
    for req in requirements:
        req_type = req.get("type", "unknown")
        type_counts[req_type] = type_counts.get(req_type, 0) + 1

    console.print("[dim]Breakdown by type:[/dim]")
    for req_type, count in sorted(type_counts.items()):
        console.print(f"  - {req_type}: {count}")
    console.print()


def _display_requirements_detail(requirements: list) -> None:
    """Display detailed requirement information."""
    console.print("\n[bold]Subsystem Requirements Detail:[/bold]\n")

    num_to_show = min(10, len(requirements))
    console.print(f"[dim]Showing first {num_to_show} of {len(requirements)} requirements[/dim]\n")

    for idx, req in enumerate(requirements[:num_to_show], 1):
        req_id = req.get("id", "UNKNOWN")
        req_type = req.get("type", "unknown")
        req_text = req.get("text", "")
        parent_id = req.get("parent_id", "N/A")
        criteria = req.get("acceptance_criteria", "N/A")

        panel = Panel(
            f"[cyan]ID:[/cyan] {req_id}\n"
            f"[cyan]Type:[/cyan] {req_type}\n"
            f"[cyan]Parent:[/cyan] {parent_id}\n"
            f"[cyan]Text:[/cyan] {req_text}\n"
            f"[cyan]Acceptance Criteria:[/cyan] {criteria}",
            title=f"[bold]Requirement {idx}/{num_to_show}[/bold]",
            border_style="blue"
        )
        console.print(panel)

    if len(requirements) > num_to_show:
        console.print(f"\n[dim]... and {len(requirements) - num_to_show} more requirements[/dim]\n")

    console.print("[yellow]Press Enter to return to review options...[/yellow]")
    input()


def _display_strategy_detail(strategy: Dict[str, Any]) -> None:
    """Display decomposition strategy details."""
    console.print("\n[bold]Decomposition Strategy:[/bold]\n")

    approach = strategy.get("approach", "unknown")
    subsystem_list = strategy.get("subsystem_list", [])
    naming_convention = strategy.get("naming_convention", "N/A")
    allocation_rules = strategy.get("allocation_rules", "N/A")

    panel = Panel(
        f"[cyan]Approach:[/cyan] {approach}\n"
        f"[cyan]Target Subsystem:[/cyan] {subsystem_list[0] if subsystem_list else 'N/A'}\n"
        f"[cyan]Naming Convention:[/cyan] {naming_convention}\n"
        f"[cyan]Allocation Rules:[/cyan]\n{allocation_rules}",
        title="[bold]Strategy Details[/bold]",
        border_style="magenta"
    )
    console.print(panel)

    console.print("\n[yellow]Press Enter to return to review options...[/yellow]")
    input()
