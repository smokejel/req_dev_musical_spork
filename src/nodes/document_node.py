"""
Documentation generation node for the requirements decomposition workflow.

This node:
1. Generates professional requirements specification document
2. Generates traceability matrix (CSV)
3. Generates quality assessment report
4. Saves all outputs to the outputs/ directory
5. Updates state with final document paths
"""

from typing import Dict, Any
from datetime import datetime
from pathlib import Path
from rich.console import Console

from src.state import DecompositionState, ErrorType, ErrorLog
from src.utils.output_generator import (
    generate_requirements_document,
    generate_traceability_matrix,
    generate_quality_report
)

console = Console()


def document_node(state: DecompositionState) -> DecompositionState:
    """
    Generate final documentation package from decomposition results.

    This is the final node in the workflow. It produces three documents:
    1. Requirements specification (Markdown)
    2. Traceability matrix (CSV)
    3. Quality assessment report (Markdown)

    Args:
        state: Current decomposition state

    Returns:
        Updated state with final_document_path and output paths

    State Updates:
        - final_document_path: Path to requirements specification
        - errors: Error messages if generation fails
        - error_log: Detailed error tracking
    """
    # Initialize errors list if not present
    errors = state.get('errors', [])
    error_log = state.get('error_log', [])

    try:
        # Get basic info
        decomposed_requirements = state.get('decomposed_requirements', [])
        target_subsystem = state.get('target_subsystem', 'Unknown')
        system_context = state.get('system_context')
        quality_metrics = state.get('quality_metrics')
        traceability_matrix = state.get('traceability_matrix')
        spec_document_path = state.get('spec_document_path', '')

        # Create timestamped output directory for this run
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        subsystem_slug = target_subsystem.lower().replace(" ", "_")
        run_id = f"{timestamp}_{subsystem_slug}"
        output_dir = Path(f"outputs/run_{run_id}")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Handle zero requirements case - generate allocation report
        if not decomposed_requirements:
            return _generate_no_allocation_report(state, output_dir, errors, error_log)

        # Create README.txt with run metadata
        readme_content = f"""Requirements Decomposition Run
==============================
Run ID: {run_id}
Spec: {spec_document_path}
Subsystem: {target_subsystem}
Quality Score: {quality_metrics.get('overall_score', 'N/A') if quality_metrics else 'N/A'}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Generated Files:
- requirements.md: Requirements specification document
- traceability.csv: Parent-child traceability matrix
- quality_report.md: Quality assessment report
"""
        (output_dir / "README.txt").write_text(readme_content, encoding="utf-8")

        # Display progress
        console.print("\n[bold blue]Generating Documentation...[/bold blue]\n")
        console.print(f"[dim]Output directory: {output_dir}[/dim]\n")

        # Generate requirements specification document
        try:
            console.print("[cyan]→ Generating requirements specification...[/cyan]")
            req_doc_path = generate_requirements_document(
                requirements=decomposed_requirements,
                subsystem=target_subsystem,
                system_context=system_context,
                quality_metrics=quality_metrics,
                output_path=str(output_dir / "requirements.md")
            )
            console.print(f"[green]  ✓ Requirements document: {req_doc_path}[/green]")

        except Exception as e:
            error_entry = ErrorLog(
                timestamp=datetime.utcnow().isoformat(),
                error_type=ErrorType.CONTENT,
                node="document",
                message=f"Requirements document generation failed: {str(e)}",
                details={}
            )
            error_log.append(error_entry.model_dump())
            errors.append(f"Requirements document generation failed: {str(e)}")
            req_doc_path = None

        # Generate traceability matrix
        trace_path = None
        if traceability_matrix:
            try:
                console.print("[cyan]→ Generating traceability matrix...[/cyan]")
                trace_path = generate_traceability_matrix(
                    traceability=traceability_matrix,
                    output_path=str(output_dir / "traceability.csv")
                )
                console.print(f"[green]  ✓ Traceability matrix: {trace_path}[/green]")

            except Exception as e:
                error_entry = ErrorLog(
                    timestamp=datetime.utcnow().isoformat(),
                    error_type=ErrorType.CONTENT,
                    node="document",
                    message=f"Traceability matrix generation failed: {str(e)}",
                    details={}
                )
                error_log.append(error_entry.model_dump())
                errors.append(f"Traceability matrix generation failed: {str(e)}")

        # Generate quality report
        quality_path = None
        if quality_metrics:
            try:
                console.print("[cyan]→ Generating quality assessment report...[/cyan]")
                quality_path = generate_quality_report(
                    metrics=quality_metrics,
                    output_path=str(output_dir / "quality_report.md")
                )
                console.print(f"[green]  ✓ Quality report: {quality_path}[/green]")

            except Exception as e:
                error_entry = ErrorLog(
                    timestamp=datetime.utcnow().isoformat(),
                    error_type=ErrorType.CONTENT,
                    node="document",
                    message=f"Quality report generation failed: {str(e)}",
                    details={}
                )
                error_log.append(error_entry.model_dump())
                errors.append(f"Quality report generation failed: {str(e)}")

        # Display summary
        console.print("\n[bold green]✓ Documentation Generation Complete[/bold green]\n")

        if req_doc_path:
            console.print(f"[bold]Requirements Specification:[/bold] {req_doc_path}")
        if trace_path:
            console.print(f"[bold]Traceability Matrix:[/bold] {trace_path}")
        if quality_path:
            console.print(f"[bold]Quality Report:[/bold] {quality_path}")

        console.print("\n" + "=" * 80 + "\n")

        # Estimate workflow cost (Phase 4.2 - Observability)
        from src.graph import estimate_workflow_cost
        cost_data = estimate_workflow_cost(state)

        # Return updated state
        return {
            **state,
            'final_document_path': req_doc_path,
            'total_cost': cost_data['total_cost'],
            'cost_breakdown': cost_data['cost_breakdown'],
            'errors': errors,
            'error_log': error_log
        }

    except ValueError as e:
        # Log fatal error (missing required data)
        error_entry = ErrorLog(
            timestamp=datetime.utcnow().isoformat(),
            error_type=ErrorType.FATAL,
            node="document",
            message=f"Documentation generation error: {str(e)}",
            details={}
        )
        error_log.append(error_entry.model_dump())
        errors.append(f"Documentation error: {str(e)}")

        console.print(f"\n[bold red]✗ Documentation Generation Failed[/bold red]")
        console.print(f"[red]{str(e)}[/red]\n")

        return {
            **state,
            'errors': errors,
            'error_log': error_log,
            'requires_human_review': True
        }

    except Exception as e:
        # Catch-all for unexpected errors
        error_entry = ErrorLog(
            timestamp=datetime.utcnow().isoformat(),
            error_type=ErrorType.FATAL,
            node="document",
            message=f"Unexpected error in document node: {str(e)}",
            details={'error_type': type(e).__name__}
        )
        error_log.append(error_entry.model_dump())
        errors.append(f"Unexpected error: {str(e)}")

        console.print(f"\n[bold red]✗ Unexpected Error[/bold red]")
        console.print(f"[red]{str(e)}[/red]\n")

        return {
            **state,
            'errors': errors,
            'error_log': error_log,
            'requires_human_review': True
        }


def _generate_no_allocation_report(state: DecompositionState, output_dir: Path, errors: list, error_log: list) -> DecompositionState:
    """
    Generate allocation report when no requirements are allocated to subsystem.

    Args:
        state: Current state
        output_dir: Output directory for reports
        errors: Error list
        error_log: Error log list

    Returns:
        Updated state with allocation report path
    """
    target_subsystem = state.get('target_subsystem', 'Unknown')
    extracted_count = len(state.get('extracted_requirements', []))
    strategy = state.get('decomposition_strategy', {})
    spec_document_path = state.get('spec_document_path', '')

    # Create allocation report content
    report_content = f"""# Allocation Report: {target_subsystem}

**Status:** No Requirements Allocated

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Summary

- **Specification Document:** `{spec_document_path}`
- **Target Subsystem:** {target_subsystem}
- **Total Requirements Extracted:** {extracted_count}
- **Requirements Allocated to {target_subsystem}:** 0

## Reason

No extracted requirements matched the allocation rules for the **{target_subsystem}** subsystem.

This is a **valid outcome** - it indicates that the specification document does not contain requirements applicable to this subsystem based on the decomposition strategy's allocation rules.

---

## Allocation Rules Applied

```
{strategy.get('allocation_rules', 'No allocation rules specified')}
```

---

## Recommendations

### 1. Verify Subsystem Name
Ensure `"{target_subsystem}"` is the correct subsystem identifier. Check for:
- Spelling variations
- Alternative names
- Abbreviations

### 2. Review Allocation Rules
The allocation rules may be too restrictive. Consider if they accurately reflect the subsystem's responsibilities.

### 3. Check Specification Content
Verify that the specification document (`{spec_document_path}`) contains requirements for this subsystem.

### 4. Review Extracted Requirements
Check the `{extracted_count}` extracted requirements to see if any should have been allocated to {target_subsystem}.

---

## Next Steps

1. **Try a different subsystem:** Run the decomposition again with a different `--subsystem` parameter
2. **Adjust allocation rules:** Modify the system analysis skill if rules are too restrictive
3. **Check specification:** Ensure the source document contains requirements for this subsystem
4. **Review extraction:** Verify that all requirements were correctly extracted from the source

---

**Note:** This is not an error. The system correctly determined that no requirements from the specification apply to the {target_subsystem} subsystem.
"""

    # Write allocation report
    report_path = output_dir / "allocation_report.md"
    report_path.write_text(report_content, encoding="utf-8")

    # Create README
    readme_content = f"""Requirements Decomposition Run
==============================
Run ID: {output_dir.name.replace('run_', '')}
Spec: {spec_document_path}
Subsystem: {target_subsystem}
Status: No requirements allocated
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Result:
No requirements from the specification were allocated to the {target_subsystem} subsystem.
This is a valid outcome indicating the specification does not contain requirements
applicable to this subsystem.

Generated Files:
- allocation_report.md: Detailed explanation and recommendations

See allocation_report.md for details and next steps.
"""
    (output_dir / "README.txt").write_text(readme_content, encoding="utf-8")

    # Display message
    console.print(f"\n[yellow]ℹ No requirements allocated to {target_subsystem} subsystem[/yellow]")
    console.print(f"[dim]  See allocation report for details: {report_path}[/dim]\n")
    console.print("\n[bold green]✓ Allocation Report Generated[/bold green]\n")
    console.print(f"[bold]Allocation Report:[/bold] {report_path}")
    console.print(f"[bold]Run Info:[/bold] {output_dir / 'README.txt'}")
    console.print("\n" + "=" * 80 + "\n")

    # Estimate workflow cost (Phase 4.2 - Observability)
    from src.graph import estimate_workflow_cost
    cost_data = estimate_workflow_cost(state)

    return {
        **state,
        'final_document_path': str(report_path),
        'total_cost': cost_data['total_cost'],
        'cost_breakdown': cost_data['cost_breakdown'],
        'errors': errors,
        'error_log': error_log
    }
