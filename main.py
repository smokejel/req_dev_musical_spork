#!/usr/bin/env python
"""
Requirements Decomposition System - CLI Entry Point

This is the main command-line interface for the requirements decomposition workflow.

Usage:
    # Basic execution
    python main.py path/to/spec.txt --subsystem "Navigation Subsystem"

    # With custom quality threshold
    python main.py spec.docx --subsystem "Power" --quality-threshold 0.85

    # With pre-decomposition review
    python main.py spec.pdf --subsystem "Comms" --review-before-decompose

    # Resume from checkpoint (future feature)
    python main.py --resume --checkpoint-id abc123

    # Help
    python main.py --help
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.graph import create_decomposition_graph, generate_checkpoint_id, get_graph_visualization
from src.state import create_initial_state
from dotenv import load_dotenv
load_dotenv()
console = Console()


def parse_arguments():
    """
    Parse command-line arguments.

    Returns:
        Parsed argument namespace
    """
    parser = argparse.ArgumentParser(
        description="Requirements Decomposition System - Automated AI-powered requirements engineering",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Decompose requirements for Navigation subsystem
  python main.py examples/train_spec.txt --subsystem "Navigation Subsystem"

  # Use higher quality threshold
  python main.py spec.docx --subsystem "Power Management" --quality-threshold 0.90

  # Enable pre-decomposition review
  python main.py spec.pdf --subsystem "Communications" --review-before-decompose

  # Adjust iteration limit
  python main.py spec.txt --subsystem "Safety" --max-iterations 5

For more information, see docs/user_guide.md
        """
    )

    # Positional arguments
    parser.add_argument(
        'spec_path',
        type=str,
        nargs='?',  # Make optional for --visualize mode
        help='Path to specification document (.txt, .docx, or .pdf)'
    )

    # Required arguments (unless --visualize is used)
    parser.add_argument(
        '--subsystem',
        type=str,
        help='Target subsystem name (e.g., "Navigation Subsystem")'
    )

    # Optional quality parameters
    parser.add_argument(
        '--quality-threshold',
        type=float,
        default=0.80,
        help='Quality gate threshold (0.0-1.0). Default: 0.80'
    )

    parser.add_argument(
        '--max-iterations',
        type=int,
        default=3,
        help='Maximum refinement iterations before human review. Default: 3'
    )

    # Workflow options
    parser.add_argument(
        '--review-before-decompose',
        action='store_true',
        help='Enable human review after analysis, before decomposition'
    )

    # Resume functionality (placeholder for future)
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume from checkpoint (requires --checkpoint-id)'
    )

    parser.add_argument(
        '--checkpoint-id',
        type=str,
        help='Checkpoint ID to resume from'
    )

    # Display options
    parser.add_argument(
        '--visualize',
        action='store_true',
        help='Display workflow graph visualization and exit'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode with verbose logging'
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress progress output (errors only)'
    )

    return parser.parse_args()


def validate_arguments(args):
    """
    Validate parsed arguments.

    Args:
        args: Parsed argument namespace

    Raises:
        SystemExit: If validation fails
    """
    # Check required arguments (unless in visualize mode)
    if not args.visualize:
        if not args.spec_path:
            console.print(f"[red]Error: spec_path is required[/red]")
            sys.exit(1)
        if not args.subsystem:
            console.print(f"[red]Error: --subsystem is required[/red]")
            sys.exit(1)

    # Skip other validation if in visualize mode
    if args.visualize:
        return

    # Check spec file exists
    spec_path = Path(args.spec_path)
    if not spec_path.exists():
        console.print(f"[red]Error: Specification file not found: {args.spec_path}[/red]")
        sys.exit(1)

    # Check file extension
    valid_extensions = ['.txt', '.docx', '.pdf']
    if spec_path.suffix.lower() not in valid_extensions:
        console.print(f"[red]Error: Unsupported file type: {spec_path.suffix}[/red]")
        console.print(f"[yellow]Supported formats: {', '.join(valid_extensions)}[/yellow]")
        sys.exit(1)

    # Validate quality threshold
    if not 0.0 <= args.quality_threshold <= 1.0:
        console.print(f"[red]Error: Quality threshold must be between 0.0 and 1.0[/red]")
        sys.exit(1)

    # Validate max iterations
    if args.max_iterations < 1 or args.max_iterations > 10:
        console.print(f"[red]Error: Max iterations must be between 1 and 10[/red]")
        sys.exit(1)

    # Check resume functionality
    if args.resume and not args.checkpoint_id:
        console.print(f"[red]Error: --resume requires --checkpoint-id[/red]")
        sys.exit(1)


def display_welcome():
    """Display welcome banner."""
    console.print()
    console.print(Panel.fit(
        "[bold cyan]Requirements Decomposition System[/bold cyan]\n"
        "[dim]AI-Powered Requirements Engineering[/dim]",
        border_style="cyan"
    ))
    console.print()


def display_configuration(args):
    """
    Display workflow configuration.

    Args:
        args: Parsed arguments
    """
    config_table = Table(title="Workflow Configuration", show_header=False, box=None)
    config_table.add_column("Parameter", style="cyan", width=30)
    config_table.add_column("Value", style="white")

    config_table.add_row("Specification Document", str(args.spec_path))
    config_table.add_row("Target Subsystem", args.subsystem)
    config_table.add_row("Quality Threshold", f"{args.quality_threshold:.2f}")
    config_table.add_row("Max Iterations", str(args.max_iterations))
    config_table.add_row("Pre-Decomposition Review", "Yes" if args.review_before_decompose else "No")

    console.print(config_table)
    console.print()


def display_results(final_state):
    """
    Display workflow results summary.

    Args:
        final_state: Final state after workflow completion
    """
    console.print("\n" + "=" * 80)
    console.print("[bold green]✓ Workflow Complete[/bold green]")
    console.print("=" * 80 + "\n")

    # Summary table
    summary_table = Table(title="Results Summary", show_header=True, header_style="bold magenta")
    summary_table.add_column("Metric", style="cyan", width=40)
    summary_table.add_column("Value", style="white", width=35)

    # Extracted requirements
    extracted_count = len(final_state.get("extracted_requirements", []))
    summary_table.add_row("Extracted Requirements", str(extracted_count))

    # Decomposed requirements
    decomposed_count = len(final_state.get("decomposed_requirements", []))
    if decomposed_count == 0:
        summary_table.add_row("Decomposed Requirements", "0 (None allocated)")
    else:
        summary_table.add_row("Decomposed Requirements", str(decomposed_count))

    # Quality metrics
    quality_metrics = final_state.get("quality_metrics")
    if quality_metrics:
        overall_score = quality_metrics.get("overall_score", 0.0)
        status = "✅ PASSED" if overall_score >= 0.80 else "⚠️ NEEDS REVIEW"
        summary_table.add_row("Quality Score", f"{overall_score:.2f} ({status})")

    # Iterations
    iterations = final_state.get("iteration_count", 0)
    summary_table.add_row("Refinement Iterations", str(iterations))

    # Human review
    human_review = final_state.get("requires_human_review", False)
    summary_table.add_row("Human Review Required", "Yes" if human_review else "No")

    # Fallback count
    fallback_count = final_state.get("fallback_count", 0)
    if fallback_count > 0:
        summary_table.add_row("LLM Fallbacks", f"{fallback_count} (check error_log)")

    # Estimated cost (Phase 4.2 - Observability)
    total_cost = final_state.get("total_cost")
    if total_cost is not None:
        summary_table.add_row("Estimated Cost", f"${total_cost:.3f} (±30%)")

    console.print(summary_table)
    console.print()

    # Performance summary (Phase 4.2 - Observability)
    timing_breakdown = final_state.get("timing_breakdown", {})
    cost_breakdown = final_state.get("cost_breakdown", {})

    if timing_breakdown:
        perf_table = Table(title="Performance & Cost Breakdown", show_header=True, header_style="bold cyan")
        perf_table.add_column("Node", style="cyan", width=25)
        perf_table.add_column("Time (s)", style="white", justify="right", width=15)
        perf_table.add_column("% Time", style="yellow", justify="right", width=15)
        perf_table.add_column("Cost ($)", style="green", justify="right", width=15)

        total_time = sum(timing_breakdown.values())
        total_cost_sum = sum(cost_breakdown.values()) if cost_breakdown else 0

        # Sort by time (slowest first)
        sorted_nodes = sorted(timing_breakdown.items(), key=lambda x: x[1], reverse=True)

        for node_name, duration in sorted_nodes:
            time_percentage = (duration / total_time * 100) if total_time > 0 else 0
            node_cost = cost_breakdown.get(node_name, 0.0) if cost_breakdown else 0.0

            perf_table.add_row(
                node_name.replace("_", " ").title(),
                f"{duration:.1f}",
                f"{time_percentage:.1f}%",
                f"${node_cost:.3f}" if node_cost > 0 else "$0.000"
            )

        # Add total row
        perf_table.add_row(
            "[bold]TOTAL[/bold]",
            f"[bold]{total_time:.1f}[/bold]",
            "[bold]100.0%[/bold]",
            f"[bold]${total_cost_sum:.3f}[/bold]" if total_cost_sum > 0 else "[bold]$0.000[/bold]"
        )

        console.print(perf_table)
        if total_cost_sum > 0:
            console.print("[dim]Note: Cost estimates are approximate (±30%). Enable LangSmith for precise tracking.[/dim]")
        console.print()

    # Output files
    final_doc = final_state.get("final_document_path")
    if final_doc:
        console.print("[bold]Generated Documents:[/bold]")
        console.print(f"  📄 Requirements: {final_doc}")

        # Check for other outputs in the same directory
        from pathlib import Path
        doc_path = Path(final_doc)
        output_dir = doc_path.parent

        trace_file = output_dir / "traceability.csv"
        if trace_file.exists():
            console.print(f"  📊 Traceability: {trace_file}")

        quality_file = output_dir / "quality_report.md"
        if quality_file.exists():
            console.print(f"  📈 Quality Report: {quality_file}")

        readme_file = output_dir / "README.txt"
        if readme_file.exists():
            console.print(f"  📋 Run Info: {readme_file}")

        console.print()

    # Errors
    errors = final_state.get("errors", [])
    if errors:
        console.print("[bold red]⚠️ Errors Encountered:[/bold red]")
        for error in errors[:5]:  # Show first 5
            console.print(f"  • {error}")
        if len(errors) > 5:
            console.print(f"  [dim]... and {len(errors) - 5} more errors[/dim]")
        console.print()


def main():
    """
    Main CLI entry point.

    Workflow:
    1. Parse and validate arguments
    2. Create initial state
    3. Initialize LangGraph workflow
    4. Execute graph
    5. Display results
    """
    # Parse arguments
    args = parse_arguments()

    # Handle visualize mode
    if args.visualize:
        console.print(get_graph_visualization())
        sys.exit(0)

    # Validate arguments
    validate_arguments(args)

    # Display welcome
    if not args.quiet:
        display_welcome()
        display_configuration(args)

    # Check resume mode
    if args.resume:
        console.print("[yellow]⚠️ Resume functionality not yet implemented[/yellow]")
        console.print("[dim]This feature will be available in a future release[/dim]\n")
        sys.exit(1)

    try:
        # Create initial state
        initial_state = create_initial_state(
            spec_document_path=args.spec_path,
            target_subsystem=args.subsystem,
            quality_threshold=args.quality_threshold,
            max_iterations=args.max_iterations,
            review_before_decompose=args.review_before_decompose
        )

        # Generate checkpoint ID
        checkpoint_id = generate_checkpoint_id(initial_state)
        if not args.quiet:
            console.print(f"[dim]Checkpoint ID: {checkpoint_id}[/dim]\n")

        # Create graph
        if not args.quiet:
            console.print("[bold]Initializing workflow...[/bold]")
        graph = create_decomposition_graph()

        # Execute workflow
        if not args.quiet:
            console.print("[bold cyan]Executing Requirements Decomposition Workflow[/bold cyan]\n")
            console.print("[dim]Starting workflow execution...[/dim]\n")

        # Execute graph (nodes provide their own progress output)
        # No spinner here to avoid interfering with human review prompts
        config = {"configurable": {"thread_id": checkpoint_id}}
        final_state = graph.invoke(initial_state, config=config)

        if not args.quiet:
            console.print("\n[dim]Workflow execution complete[/dim]")

        # Display results
        if not args.quiet:
            display_results(final_state)
        else:
            # In quiet mode, just print the output path
            final_doc = final_state.get("final_document_path")
            if final_doc:
                console.print(final_doc)

        # Check for errors
        errors = final_state.get("errors", [])
        if errors:
            console.print("[yellow]⚠️ Workflow completed with errors. Review error_log for details.[/yellow]")
            sys.exit(2)

        # Success
        if not args.quiet:
            console.print("[bold green]✓ Decomposition complete![/bold green]\n")
        sys.exit(0)

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Workflow interrupted by user[/yellow]")
        sys.exit(130)

    except Exception as e:
        console.print(f"\n[bold red]✗ Fatal Error:[/bold red] {str(e)}")
        if args.debug:
            import traceback
            console.print("\n[dim]Traceback:[/dim]")
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
