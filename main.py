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
from src.utils.cost_tracker import get_cost_tracker
from src.utils.quality_tracker import get_quality_tracker
from config.observability_config import ObservabilityConfig, LANGSMITH_ACTIVE
from dotenv import load_dotenv
load_dotenv()
console = Console()

# Display LangSmith status on startup
if LANGSMITH_ACTIVE:
    console.print("[dim]✓ LangSmith tracing enabled[/dim]", style="green")
elif ObservabilityConfig.COST_TRACKING_ENABLED:
    console.print("[dim]✓ Cost tracking enabled (heuristic mode)[/dim]", style="yellow")


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

    # Domain-aware arguments (Phase 7)
    parser.add_argument(
        '--domain',
        type=str,
        help='Domain name for domain-aware decomposition (e.g., "csx_dispatch"). Default: generic'
    )

    parser.add_argument(
        '--subsystem-id',
        type=str,
        help='Subsystem identifier within domain (e.g., "train_management")'
    )

    parser.add_argument(
        '--list-domains',
        action='store_true',
        help='List all available domains and exit'
    )

    parser.add_argument(
        '--list-subsystems',
        type=str,
        metavar='DOMAIN',
        help='List subsystems for specified domain and exit'
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

    # Validate domain configuration (Phase 7)
    if args.domain:
        from config.domain_config import registry

        domain = registry.get_domain(args.domain)
        if not domain:
            console.print(f"[red]Error: Domain '{args.domain}' not found[/red]")
            console.print(f"[dim]Use --list-domains to see available domains[/dim]")
            sys.exit(1)

        # If subsystem_id specified, validate it exists in domain
        if args.subsystem_id:
            if args.subsystem_id not in domain.subsystems:
                console.print(f"[red]Error: Subsystem '{args.subsystem_id}' not found in domain '{args.domain}'[/red]")
                console.print(f"[dim]Use --list-subsystems {args.domain} to see available subsystems[/dim]")
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

    # Phase 7.2: Display domain information
    if args.domain and args.domain != "generic":
        domain_display = args.domain
        if args.subsystem_id:
            domain_display += f" / {args.subsystem_id}"
        config_table.add_row("Domain Context", domain_display)

    console.print(config_table)
    console.print()


def _display_energy_context(total_energy_wh: float):
    """
    Display contextual comparisons for energy consumption.

    Helps users understand the energy usage in everyday terms.

    Args:
        total_energy_wh: Total energy consumption in Watt-hours
    """
    # Contextual comparisons (Phase 6.1)
    # Average LED TV: ~50W → 2.5W per minute average (considering standby modes)
    # Electric car: ~0.25 kWh per km (250 Wh/km)

    tv_minutes = total_energy_wh / 2.5  # Minutes of TV usage
    car_meters = (total_energy_wh / 250) * 1000  # Meters driven by electric car

    console.print("\n[bold]💡 Energy Context:[/bold]")
    console.print(f"   • Equivalent to [yellow]~{tv_minutes:.1f} minutes[/yellow] of LED TV usage (50W average)")
    console.print(f"   • Equivalent to [yellow]~{car_meters:.1f} meters[/yellow] driven by electric car (0.25 kWh/km)")
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

    # Cost tracking (Phase 5.1 - Enhanced Observability)
    total_cost = final_state.get("total_cost")
    if total_cost is not None:
        cost_source = "LangSmith" if LANGSMITH_ACTIVE else "Heuristic (±30%)"
        summary_table.add_row("Total Cost", f"${total_cost:.4f} ({cost_source})")

    console.print(summary_table)
    console.print()

    # Performance summary (Phase 4.2 - Observability + Phase 6.1 - Energy Tracking)
    timing_breakdown = final_state.get("timing_breakdown", {})
    cost_breakdown = final_state.get("cost_breakdown", {})
    energy_breakdown = final_state.get("energy_breakdown", {})

    if timing_breakdown:
        perf_table = Table(title="Performance, Cost & Energy Breakdown", show_header=True, header_style="bold cyan")
        perf_table.add_column("Node", style="cyan", width=20)
        perf_table.add_column("Time (s)", style="white", justify="right", width=12)
        perf_table.add_column("% Time", style="yellow", justify="right", width=10)
        perf_table.add_column("Cost ($)", style="green", justify="right", width=12)
        perf_table.add_column("Energy (Wh)", style="magenta", justify="right", width=14)
        perf_table.add_column("% Energy", style="yellow", justify="right", width=10)

        total_time = sum(timing_breakdown.values())
        total_cost_sum = sum(cost_breakdown.values()) if cost_breakdown else 0
        total_energy_sum = sum(energy_breakdown.values()) if energy_breakdown else 0

        # Sort by time (slowest first)
        sorted_nodes = sorted(timing_breakdown.items(), key=lambda x: x[1], reverse=True)

        for node_name, duration in sorted_nodes:
            time_percentage = (duration / total_time * 100) if total_time > 0 else 0
            node_cost = cost_breakdown.get(node_name, 0.0) if cost_breakdown else 0.0
            node_energy = energy_breakdown.get(node_name, 0.0) if energy_breakdown else 0.0
            energy_percentage = (node_energy / total_energy_sum * 100) if total_energy_sum > 0 else 0

            perf_table.add_row(
                node_name.replace("_", " ").title(),
                f"{duration:.1f}",
                f"{time_percentage:.1f}%",
                f"${node_cost:.3f}" if node_cost > 0 else "$0.000",
                f"{node_energy:.4f}" if node_energy > 0 else "0.0000",
                f"{energy_percentage:.1f}%" if node_energy > 0 else "0.0%"
            )

        # Add total row
        perf_table.add_row(
            "[bold]TOTAL[/bold]",
            f"[bold]{total_time:.1f}[/bold]",
            "[bold]100.0%[/bold]",
            f"[bold]${total_cost_sum:.3f}[/bold]" if total_cost_sum > 0 else "[bold]$0.000[/bold]",
            f"[bold]{total_energy_sum:.4f} Wh[/bold]" if total_energy_sum > 0 else "[bold]0.0000 Wh[/bold]",
            "[bold]100.0%[/bold]" if total_energy_sum > 0 else "[bold]0.0%[/bold]"
        )

        console.print(perf_table)

        # Display energy context (Phase 6.1)
        if total_energy_sum > 0:
            _display_energy_context(total_energy_sum)

        if total_cost_sum > 0 or total_energy_sum > 0:
            if LANGSMITH_ACTIVE:
                console.print("[dim]✓ Costs/Energy calculated from LangSmith traces (precise)[/dim]")
            else:
                console.print("[dim]Note: Cost and energy estimates are heuristic-based (±30%). Enable LangSmith for precise tracking.[/dim]")
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


def handle_list_domains():
    """Display all available domains and exit."""
    from config.domain_config import registry

    domains = registry.list_domains()

    console.print("\n[bold]Available Domains:[/bold]\n")

    for domain_name in domains:
        domain = registry.get_domain(domain_name)
        console.print(f"  • [cyan]{domain_name}[/cyan]: {domain.description}")

    console.print()


def handle_list_subsystems(domain_name: str):
    """
    Display all subsystems for a given domain and exit.

    Args:
        domain_name: Domain identifier
    """
    from config.domain_config import registry

    domain = registry.get_domain(domain_name)
    if not domain:
        console.print(f"[red]Error: Domain '{domain_name}' not found[/red]")
        console.print(f"[dim]Use --list-domains to see available domains[/dim]\n")
        sys.exit(1)

    subsystems = registry.list_subsystems(domain_name)

    if not subsystems:
        console.print(f"\n[yellow]Domain '{domain_name}' has no registered subsystems[/yellow]\n")
        sys.exit(0)

    console.print(f"\n[bold]Subsystems in {domain.description}:[/bold]\n")

    for subsystem_id in subsystems:
        subsystem = domain.subsystems[subsystem_id]
        console.print(f"  • [cyan]{subsystem_id}[/cyan]: {subsystem.name}")
        console.print(f"    [dim]{subsystem.description}[/dim]")

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

    # Handle domain listing commands (Phase 7)
    if args.list_domains:
        handle_list_domains()
        sys.exit(0)

    if args.list_subsystems:
        handle_list_subsystems(args.list_subsystems)
        sys.exit(0)

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
            review_before_decompose=args.review_before_decompose,
            # Phase 7.2: Domain parameters
            domain_name=args.domain or "generic",
            subsystem_id=args.subsystem_id
        )

        # Generate checkpoint ID
        checkpoint_id = generate_checkpoint_id(initial_state)
        if not args.quiet:
            console.print(f"[dim]Checkpoint ID: {checkpoint_id}[/dim]\n")

        # Initialize cost tracking (Phase 5.1)
        if ObservabilityConfig.COST_TRACKING_ENABLED:
            cost_tracker = get_cost_tracker()
            cost_tracker.start_run(checkpoint_id)
            if not args.quiet:
                console.print(f"[dim]Cost tracking active (budget: ${ObservabilityConfig.COST_BUDGET_MAX:.2f})[/dim]\n")

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

        # Track run ID for LangSmith cost fetching
        from langchain_core.tracers.context import collect_runs

        with collect_runs() as cb:
            final_state = graph.invoke(initial_state, config=config)
            langsmith_run_id = None
            if cb.traced_runs:
                # Get the root run ID (workflow execution)
                langsmith_run_id = str(cb.traced_runs[0].id)

        if not args.quiet:
            console.print("\n[dim]Workflow execution complete[/dim]")

        # Finalize cost tracking (Phase 5.1)
        if ObservabilityConfig.COST_TRACKING_ENABLED:
            cost_tracker = get_cost_tracker()

            # Try to fetch actual costs from LangSmith if available
            langsmith_costs = None
            if LANGSMITH_ACTIVE and langsmith_run_id:
                from src.utils.langsmith_integration import get_langsmith_tracker
                langsmith_tracker = get_langsmith_tracker()

                if not args.quiet:
                    console.print("[dim]Fetching cost data from LangSmith...[/dim]")

                langsmith_costs = langsmith_tracker.get_workflow_costs(
                    workflow_run_id=langsmith_run_id,
                    max_wait_seconds=15
                )

                if langsmith_costs:
                    # Replace heuristic costs with LangSmith actuals
                    from config.llm_config import get_primary_model, NodeType

                    for node_name, token_data in langsmith_costs['node_costs'].items():
                        input_tokens = token_data['input_tokens']
                        output_tokens = token_data['output_tokens']

                        # Determine node type for cost calculation
                        try:
                            node_type = NodeType(node_name)
                            model_config = get_primary_model(node_type)
                        except:
                            # Use a default if node type unknown
                            continue

                        # Calculate cost
                        cost = cost_tracker.calculate_node_cost(
                            node_type,
                            input_tokens,
                            output_tokens,
                            model_config
                        )

                        # Update tracker with actual data
                        cost_tracker.record_node_cost(
                            node_name=node_name,
                            cost=cost,
                            input_tokens=input_tokens,
                            output_tokens=output_tokens,
                            model_name=model_config.name
                        )

                    if not args.quiet:
                        console.print(f"[dim]✓ Retrieved {langsmith_costs['total_tokens']} tokens from LangSmith[/dim]")
                        console.print("[green]✓ Costs calculated from LangSmith traces (precise)[/green]")
                elif not args.quiet:
                    console.print("[yellow]⚠ Could not fetch costs from LangSmith (using heuristic estimates)[/yellow]")

            cost_record = cost_tracker.finalize_run(
                subsystem=args.subsystem,
                source_method='langsmith' if (LANGSMITH_ACTIVE and langsmith_costs) else 'heuristic'
            )
            # Store in final state for display
            final_state['total_cost'] = cost_record.total_cost
            final_state['cost_breakdown'] = cost_record.node_costs

        # Calculate and store energy consumption (Phase 6.1)
        from src.graph import estimate_workflow_energy
        energy_data = estimate_workflow_energy(final_state)
        final_state['total_energy_wh'] = energy_data['total_energy_wh']
        final_state['energy_breakdown'] = energy_data['energy_breakdown']

        # Record quality metrics (Phase 5.1)
        quality_metrics_dict = final_state.get('quality_metrics')
        if quality_metrics_dict:
            from src.state import QualityMetrics, QualityIssue, QualitySeverity
            # Convert dict to QualityMetrics object
            # Note: validation_passed comes from state, not quality_metrics
            issues = []
            for issue_dict in quality_metrics_dict.get('issues', []):
                try:
                    issues.append(QualityIssue(
                        severity=QualitySeverity(issue_dict.get('severity', 'minor')),
                        requirement_id=issue_dict.get('requirement_id'),
                        dimension=issue_dict.get('dimension', 'unknown'),
                        description=issue_dict.get('description', ''),
                        suggestion=issue_dict.get('suggestion', '')
                    ))
                except:
                    pass  # Skip malformed issues

            quality_metrics = QualityMetrics(
                overall_score=quality_metrics_dict['overall_score'],
                completeness=quality_metrics_dict['completeness'],
                clarity=quality_metrics_dict['clarity'],
                testability=quality_metrics_dict['testability'],
                traceability=quality_metrics_dict['traceability'],
                issues=issues
            )
            quality_tracker = get_quality_tracker()
            quality_tracker.record_quality(
                run_id=checkpoint_id,
                subsystem=args.subsystem,
                quality_metrics=quality_metrics,
                validation_passed=final_state.get('validation_passed', False),
                iteration_count=final_state.get('iteration_count', 0),
                requirements_count=len(final_state.get('decomposed_requirements', []))
            )

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
