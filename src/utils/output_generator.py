"""
Output generation utilities for requirements decomposition.

This module provides functions to generate professional documentation
from the decomposition workflow outputs:
- Requirements specification document
- Traceability matrix
- Quality assessment report
"""

from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime
import csv


def generate_requirements_document(
    requirements: List[Dict[str, Any]],
    subsystem: str,
    system_context: Dict[str, Any] = None,
    quality_metrics: Dict[str, Any] = None,
    output_path: str = None
) -> str:
    """
    Generate a professional requirements specification document.

    Args:
        requirements: List of requirement dicts
        subsystem: Target subsystem name
        system_context: Optional system context from analyze node
        quality_metrics: Optional quality metrics from validate node
        output_path: Optional custom output path

    Returns:
        Path to generated markdown document
    """
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        subsystem_slug = subsystem.lower().replace(" ", "_")
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"requirements_{timestamp}_{subsystem_slug}.md"

    # Build document content
    content = _build_requirements_markdown(
        requirements=requirements,
        subsystem=subsystem,
        system_context=system_context,
        quality_metrics=quality_metrics
    )

    # Write to file
    Path(output_path).write_text(content, encoding="utf-8")

    return str(output_path)


def generate_traceability_matrix(
    traceability: Dict[str, Any],
    output_path: str = None
) -> str:
    """
    Generate a traceability matrix document.

    Args:
        traceability: Traceability matrix dict from workflow
        output_path: Optional custom output path

    Returns:
        Path to generated CSV file
    """
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"traceability_{timestamp}.csv"

    # Extract links from traceability matrix
    links = traceability.get("links", [])

    # Write CSV
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        # Header
        writer.writerow([
            "Parent ID",
            "Child ID",
            "Parent Text",
            "Child Text",
            "Relationship",
            "Rationale"
        ])

        # Data rows
        for link in links:
            writer.writerow([
                link.get("parent_id", ""),
                link.get("child_id", ""),
                link.get("parent_text", "")[:80],  # Truncate for CSV
                link.get("child_text", "")[:80],
                link.get("relationship", "decomposes_to"),
                link.get("rationale", "")[:100]
            ])

    return str(output_path)


def generate_quality_report(
    metrics: Dict[str, Any],
    output_path: str = None
) -> str:
    """
    Generate a quality assessment report.

    Args:
        metrics: Quality metrics dict from validate node
        output_path: Optional custom output path

    Returns:
        Path to generated markdown document
    """
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"quality_report_{timestamp}.md"

    # Build report content
    content = _build_quality_report_markdown(metrics)

    # Write to file
    Path(output_path).write_text(content, encoding="utf-8")

    return str(output_path)


def _build_requirements_markdown(
    requirements: List[Dict[str, Any]],
    subsystem: str,
    system_context: Dict[str, Any] = None,
    quality_metrics: Dict[str, Any] = None
) -> str:
    """Build the requirements specification markdown content."""

    lines = []

    # Header
    lines.append(f"# {subsystem} - Requirements Specification")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Total Requirements:** {len(requirements)}")
    lines.append("")

    # Quality summary (if available)
    if quality_metrics:
        overall_score = quality_metrics.get("overall_score", 0.0)
        status = "✅ PASSED" if overall_score >= 0.80 else "⚠️ NEEDS REVIEW"
        lines.append(f"**Quality Score:** {overall_score:.2f} ({status})")
        lines.append("")

    lines.append("---")
    lines.append("")

    # System Context (if available)
    if system_context:
        lines.append("## 1. System Context")
        lines.append("")

        description = system_context.get("description", "")
        if description:
            lines.append(f"**Subsystem Description:** {description}")
            lines.append("")

        constraints = system_context.get("constraints", [])
        if constraints:
            lines.append("**System Constraints:**")
            for constraint in constraints:
                lines.append(f"- {constraint}")
            lines.append("")

        interfaces = system_context.get("interfaces", [])
        if interfaces:
            lines.append("**External Interfaces:**")
            for interface in interfaces:
                lines.append(f"- {interface}")
            lines.append("")

        lines.append("---")
        lines.append("")

    # Requirements by Type
    lines.append("## 2. Requirements")
    lines.append("")

    # Group requirements by type
    functional = [r for r in requirements if r.get("type") == "FUNC"]
    performance = [r for r in requirements if r.get("type") == "PERF"]
    constraint = [r for r in requirements if r.get("type") == "CONS"]
    interface = [r for r in requirements if r.get("type") == "INTF"]

    # Functional Requirements
    if functional:
        lines.append(f"### 2.1 Functional Requirements ({len(functional)})")
        lines.append("")
        for req in functional:
            lines.extend(_format_requirement(req))
        lines.append("")

    # Performance Requirements
    if performance:
        lines.append(f"### 2.2 Performance Requirements ({len(performance)})")
        lines.append("")
        for req in performance:
            lines.extend(_format_requirement(req))
        lines.append("")

    # Constraint Requirements
    if constraint:
        lines.append(f"### 2.3 Constraint Requirements ({len(constraint)})")
        lines.append("")
        for req in constraint:
            lines.extend(_format_requirement(req))
        lines.append("")

    # Interface Requirements
    if interface:
        lines.append(f"### 2.4 Interface Requirements ({len(interface)})")
        lines.append("")
        for req in interface:
            lines.extend(_format_requirement(req))
        lines.append("")

    # Traceability Section
    lines.append("---")
    lines.append("")
    lines.append("## 3. Traceability")
    lines.append("")
    lines.append("For complete parent-child traceability, see the generated traceability matrix CSV.")
    lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append("*This document was generated by the Requirements Decomposition System.*")
    lines.append("")
    lines.append("")

    return "\n".join(lines)


def _format_requirement(req: Dict[str, Any]) -> List[str]:
    """Format a single requirement as markdown."""
    lines = []

    req_id = req.get("id", "UNKNOWN")
    req_text = req.get("text", "")
    parent_id = req.get("parent_id", "")
    subsystem = req.get("subsystem", "")
    rationale = req.get("rationale", "")
    acceptance_criteria = req.get("acceptance_criteria", "")

    # Requirement header
    lines.append(f"#### {req_id}")
    lines.append("")

    # Requirement text
    lines.append(f"**Requirement:** {req_text}")
    lines.append("")

    # Parent (traceability)
    if parent_id:
        lines.append(f"**Parent:** {parent_id}")
        lines.append("")

    # Subsystem
    if subsystem:
        lines.append(f"**Subsystem:** {subsystem}")
        lines.append("")

    # Acceptance Criteria
    if acceptance_criteria:
        lines.append("**Acceptance Criteria:**")
        # Handle both string and list formats
        if isinstance(acceptance_criteria, list):
            for criterion in acceptance_criteria:
                lines.append(f"- {criterion}")
        else:
            lines.append(f"{acceptance_criteria}")
        lines.append("")

    # Rationale
    if rationale:
        lines.append(f"**Rationale:** {rationale}")
        lines.append("")

    lines.append("---")
    lines.append("")

    return lines


def _build_quality_report_markdown(metrics: Dict[str, Any]) -> str:
    """Build the quality report markdown content."""

    lines = []

    # Header
    lines.append("# Requirements Quality Assessment Report")
    lines.append("")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    overall_score = metrics.get("overall_score", 0.0)
    validation_passed = overall_score >= 0.80

    # Overall Assessment
    lines.append("## Overall Assessment")
    lines.append("")
    lines.append(f"**Overall Quality Score:** {overall_score:.2f} / 1.00")
    lines.append("")

    if validation_passed:
        lines.append("**Status:** ✅ PASSED - Requirements meet quality threshold")
    else:
        lines.append("**Status:** ⚠️ NEEDS IMPROVEMENT - Requirements below quality threshold")

    lines.append("")
    lines.append("**Quality Threshold:** 0.80")
    lines.append("")

    lines.append("---")
    lines.append("")

    # Dimension Scores
    lines.append("## Quality Dimensions")
    lines.append("")
    lines.append("| Dimension | Score | Status |")
    lines.append("|-----------|-------|--------|")

    dimensions = [
        ("Completeness", "completeness"),
        ("Clarity", "clarity"),
        ("Testability", "testability"),
        ("Traceability", "traceability")
    ]

    for display_name, key in dimensions:
        score = metrics.get(key, 0.0)
        status = "✅ Pass" if score >= 0.80 else "⚠️ Needs Work"
        lines.append(f"| {display_name} | {score:.2f} | {status} |")

    lines.append("")
    lines.append("---")
    lines.append("")

    # Issues
    issues = metrics.get("issues", [])
    if issues:
        lines.append("## Quality Issues")
        lines.append("")

        # Group by severity
        critical = [i for i in issues if i.get("severity") == "critical"]
        major = [i for i in issues if i.get("severity") == "major"]
        minor = [i for i in issues if i.get("severity") == "minor"]

        # Critical Issues
        if critical:
            lines.append(f"### Critical Issues ({len(critical)})")
            lines.append("")
            lines.append("**These issues must be addressed:**")
            lines.append("")
            for idx, issue in enumerate(critical, 1):
                req_id = issue.get("requirement_id", "GENERAL")
                dimension = issue.get("dimension", "unknown")
                description = issue.get("description", "")
                suggestion = issue.get("suggestion", "")

                lines.append(f"{idx}. **[{req_id}]** ({dimension})")
                lines.append(f"   - **Issue:** {description}")
                if suggestion:
                    lines.append(f"   - **Suggestion:** {suggestion}")
                lines.append("")

        # Major Issues
        if major:
            lines.append(f"### Major Issues ({len(major)})")
            lines.append("")
            lines.append("**These issues should be addressed:**")
            lines.append("")
            for idx, issue in enumerate(major, 1):
                req_id = issue.get("requirement_id", "GENERAL")
                dimension = issue.get("dimension", "unknown")
                description = issue.get("description", "")

                lines.append(f"{idx}. **[{req_id}]** ({dimension}): {description}")

            lines.append("")

        # Minor Issues (summary only)
        if minor:
            lines.append(f"### Minor Issues ({len(minor)})")
            lines.append("")
            lines.append("Minor issues have been identified and can be addressed in future revisions.")
            lines.append("")

    else:
        lines.append("## Quality Issues")
        lines.append("")
        lines.append("✅ No quality issues identified.")
        lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append("*This report was generated by the Requirements Decomposition System.*")
    lines.append("")

    return "\n".join(lines)


# Export main functions
__all__ = [
    "generate_requirements_document",
    "generate_traceability_matrix",
    "generate_quality_report"
]
