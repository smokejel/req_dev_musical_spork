#!/usr/bin/env python
"""
Generate cost and quality trend reports.

This script analyzes historical workflow runs and generates reports showing
trends in cost, quality, and performance over time.

Usage:
    # Generate all reports
    python scripts/generate_reports.py

    # Generate only cost report
    python scripts/generate_reports.py --report cost

    # Generate for specific time period
    python scripts/generate_reports.py --days 7

    # Output to specific directory
    python scripts/generate_reports.py --output reports/
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.cost_tracker import get_cost_tracker
from src.utils.quality_tracker import get_quality_tracker

console = Console()


def generate_cost_report(days: int = 30, output_dir: Optional[Path] = None) -> None:
    """
    Generate cost trend report.

    Args:
        days: Number of days to analyze
        output_dir: Output directory for report files
    """
    console.print(f"\n[bold cyan]Cost Trend Report (Last {days} days)[/bold cyan]\n")

    cost_tracker = get_cost_tracker()
    trends = cost_tracker.get_cost_trends(days=days)

    if trends['total_runs'] == 0:
        console.print("[yellow]No cost data available for this period.[/yellow]")
        return

    # Summary table
    summary_table = Table(title="Cost Summary", show_header=True, header_style="bold cyan")
    summary_table.add_column("Metric", style="cyan", width=30)
    summary_table.add_column("Value", style="white", width=20)

    summary_table.add_row("Total Runs", str(trends['total_runs']))
    summary_table.add_row("Total Cost", f"${trends['total_cost']:.4f}")
    summary_table.add_row("Average Cost per Run", f"${trends['avg_cost']:.4f}")
    summary_table.add_row("Min Cost", f"${trends['min_cost']:.4f}")
    summary_table.add_row("Max Cost", f"${trends['max_cost']:.4f}")
    summary_table.add_row("Subsystems", ", ".join(trends['subsystems']))

    console.print(summary_table)
    console.print()

    # Recent runs
    recent_runs = cost_tracker.get_recent_runs(limit=10)
    if recent_runs:
        console.print("[bold]Recent Runs:[/bold]\n")
        runs_table = Table(show_header=True, header_style="bold magenta")
        runs_table.add_column("Date", style="cyan", width=20)
        runs_table.add_column("Subsystem", style="white", width=25)
        runs_table.add_column("Total Cost", style="green", justify="right", width=15)
        runs_table.add_column("Source", style="yellow", width=15)

        for run in recent_runs:
            runs_table.add_row(
                run.timestamp.strftime("%Y-%m-%d %H:%M"),
                run.subsystem,
                f"${run.total_cost:.4f}",
                run.source_method
            )

        console.print(runs_table)
        console.print()

    # Save to file if output directory specified
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        report_file = output_dir / f"cost_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        with open(report_file, 'w') as f:
            f.write(f"Cost Trend Report (Last {days} days)\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Total Runs: {trends['total_runs']}\n")
            f.write(f"Total Cost: ${trends['total_cost']:.4f}\n")
            f.write(f"Average Cost: ${trends['avg_cost']:.4f}\n")
            f.write(f"Min Cost: ${trends['min_cost']:.4f}\n")
            f.write(f"Max Cost: ${trends['max_cost']:.4f}\n")
            f.write(f"Subsystems: {', '.join(trends['subsystems'])}\n\n")

            f.write("Recent Runs:\n")
            f.write("-" * 80 + "\n")
            for run in recent_runs:
                f.write(f"{run.timestamp.strftime('%Y-%m-%d %H:%M')} | ")
                f.write(f"{run.subsystem:<25} | ${run.total_cost:.4f} | {run.source_method}\n")

        console.print(f"[green]✓ Cost report saved to: {report_file}[/green]\n")


def generate_quality_report(days: int = 30, output_dir: Optional[Path] = None) -> None:
    """
    Generate quality trend report.

    Args:
        days: Number of days to analyze
        output_dir: Output directory for report files
    """
    console.print(f"\n[bold cyan]Quality Trend Report (Last {days} days)[/bold cyan]\n")

    quality_tracker = get_quality_tracker()
    trends = quality_tracker.get_quality_trends(days=days)

    if trends['total_runs'] == 0:
        console.print("[yellow]No quality data available for this period.[/yellow]")
        return

    # Summary table
    summary_table = Table(title="Quality Summary", show_header=True, header_style="bold cyan")
    summary_table.add_column("Metric", style="cyan", width=30)
    summary_table.add_column("Value", style="white", width=20)

    summary_table.add_row("Total Runs", str(trends['total_runs']))
    summary_table.add_row("Average Overall Score", f"{trends['avg_overall_score']:.3f}")
    summary_table.add_row("Average Completeness", f"{trends['avg_completeness']:.3f}")
    summary_table.add_row("Average Clarity", f"{trends['avg_clarity']:.3f}")
    summary_table.add_row("Average Testability", f"{trends['avg_testability']:.3f}")
    summary_table.add_row("Average Traceability", f"{trends['avg_traceability']:.3f}")
    summary_table.add_row("Pass Rate", f"{trends['pass_rate']:.1f}%")
    summary_table.add_row("Average Iterations", f"{trends['avg_iterations']:.1f}")
    summary_table.add_row("Min Score", f"{trends['min_score']:.3f}")
    summary_table.add_row("Max Score", f"{trends['max_score']:.3f}")

    console.print(summary_table)
    console.print()

    # Subsystem comparison
    subsystem_comparison = quality_tracker.get_subsystem_comparison()
    if subsystem_comparison:
        console.print("[bold]Subsystem Comparison:[/bold]\n")
        subsystem_table = Table(show_header=True, header_style="bold magenta")
        subsystem_table.add_column("Subsystem", style="cyan", width=30)
        subsystem_table.add_column("Avg Score", style="green", justify="right", width=15)
        subsystem_table.add_column("Avg Iterations", style="yellow", justify="right", width=18)
        subsystem_table.add_column("Runs", style="white", justify="right", width=10)

        for subsystem, metrics in sorted(subsystem_comparison.items(),
                                        key=lambda x: x[1]['avg_score'],
                                        reverse=True):
            subsystem_table.add_row(
                subsystem,
                f"{metrics['avg_score']:.3f}",
                f"{metrics['avg_iterations']:.1f}",
                str(int(metrics['run_count']))
            )

        console.print(subsystem_table)
        console.print()

    # Recent runs
    recent_runs = quality_tracker.get_recent_runs(limit=10)
    if recent_runs:
        console.print("[bold]Recent Runs:[/bold]\n")
        runs_table = Table(show_header=True, header_style="bold magenta")
        runs_table.add_column("Date", style="cyan", width=20)
        runs_table.add_column("Subsystem", style="white", width=25)
        runs_table.add_column("Score", style="green", justify="right", width=10)
        runs_table.add_column("Status", style="white", width=10)
        runs_table.add_column("Iterations", style="yellow", justify="right", width=12)

        for run in recent_runs:
            status = "✅ PASS" if run.validation_passed else "⚠️  FAIL"
            runs_table.add_row(
                run.timestamp.strftime("%Y-%m-%d %H:%M"),
                run.subsystem,
                f"{run.overall_score:.3f}",
                status,
                str(run.iteration_count)
            )

        console.print(runs_table)
        console.print()

    # Save to file if output directory specified
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        report_file = output_dir / f"quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        with open(report_file, 'w') as f:
            f.write(f"Quality Trend Report (Last {days} days)\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Total Runs: {trends['total_runs']}\n")
            f.write(f"Average Overall Score: {trends['avg_overall_score']:.3f}\n")
            f.write(f"Average Completeness: {trends['avg_completeness']:.3f}\n")
            f.write(f"Average Clarity: {trends['avg_clarity']:.3f}\n")
            f.write(f"Average Testability: {trends['avg_testability']:.3f}\n")
            f.write(f"Average Traceability: {trends['avg_traceability']:.3f}\n")
            f.write(f"Pass Rate: {trends['pass_rate']:.1f}%\n")
            f.write(f"Average Iterations: {trends['avg_iterations']:.1f}\n\n")

            f.write("Recent Runs:\n")
            f.write("-" * 80 + "\n")
            for run in recent_runs:
                status = "PASS" if run.validation_passed else "FAIL"
                f.write(f"{run.timestamp.strftime('%Y-%m-%d %H:%M')} | ")
                f.write(f"{run.subsystem:<25} | {run.overall_score:.3f} | ")
                f.write(f"{status:<5} | {run.iteration_count} iterations\n")

        console.print(f"[green]✓ Quality report saved to: {report_file}[/green]\n")


def main():
    """Main entry point for report generation."""
    parser = argparse.ArgumentParser(
        description="Generate cost and quality trend reports",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--report',
        choices=['cost', 'quality', 'all'],
        default='all',
        help='Type of report to generate (default: all)'
    )

    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Number of days to analyze (default: 30)'
    )

    parser.add_argument(
        '--output',
        type=Path,
        default=None,
        help='Output directory for report files (optional)'
    )

    args = parser.parse_args()

    # Display welcome
    console.print()
    console.print(Panel.fit(
        "[bold cyan]Requirements Decomposition Reports[/bold cyan]\n"
        "[dim]Cost & Quality Trend Analysis[/dim]",
        border_style="cyan"
    ))

    try:
        if args.report in ['cost', 'all']:
            generate_cost_report(days=args.days, output_dir=args.output)

        if args.report in ['quality', 'all']:
            generate_quality_report(days=args.days, output_dir=args.output)

        console.print("[bold green]✓ Report generation complete![/bold green]\n")

    except Exception as e:
        console.print(f"\n[bold red]✗ Error generating reports:[/bold red] {str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
