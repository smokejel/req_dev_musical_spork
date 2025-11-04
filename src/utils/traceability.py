"""
Traceability utilities for requirements decomposition.

Provides functions to build and validate traceability matrices,
ensuring complete parent-child linkage across requirements.
"""

from typing import List, Dict, Set, Optional, Any
from src.state import (
    Requirement,
    DetailedRequirement,
    TraceabilityMatrix,
    TraceabilityLink
)


def build_traceability_matrix(
    parent_requirements: List[Dict[str, Any]],
    child_requirements: List[Dict[str, Any]]
) -> TraceabilityMatrix:
    """
    Build a traceability matrix from parent and child requirements.

    Args:
        parent_requirements: List of parent requirement dicts
        child_requirements: List of child requirement dicts

    Returns:
        TraceabilityMatrix with all parent-child relationships

    Raises:
        ValueError: If child requirements have invalid parent references
    """
    # Extract all parent IDs
    parent_ids = {req['id'] for req in parent_requirements}

    # Build traceability links
    links = []
    orphan_requirements = []

    for child_req in child_requirements:
        child_id = child_req['id']
        parent_id = child_req.get('parent_id')

        if not parent_id:
            # Child has no parent - orphan
            orphan_requirements.append(child_id)
        elif parent_id not in parent_ids:
            # Child references non-existent parent - orphan
            orphan_requirements.append(child_id)
        else:
            # Valid parent-child relationship
            link = TraceabilityLink(
                parent_id=parent_id,
                child_id=child_id,
                relationship_type="decomposes"
            )
            links.append(link)

    return TraceabilityMatrix(
        links=links,
        orphan_requirements=orphan_requirements
    )


def validate_traceability(
    traceability_matrix: TraceabilityMatrix,
    parent_requirements: List[Dict[str, Any]],
    child_requirements: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Validate traceability matrix for completeness and correctness.

    Args:
        traceability_matrix: The traceability matrix to validate
        parent_requirements: List of parent requirement dicts
        child_requirements: List of child requirement dicts

    Returns:
        Validation report with issues and statistics

    Validation Checks:
    - No orphaned child requirements
    - No broken parent references
    - All children have parents
    - Parent coverage (all parents have at least one child)
    """
    issues = []
    warnings = []

    # Check for orphaned requirements
    if traceability_matrix.orphan_requirements:
        issues.append({
            "severity": "critical",
            "type": "orphaned_requirements",
            "description": f"Found {len(traceability_matrix.orphan_requirements)} orphaned requirements",
            "affected_ids": traceability_matrix.orphan_requirements
        })

    # Check parent coverage
    parent_ids = {req['id'] for req in parent_requirements}
    parents_with_children = {link.parent_id for link in traceability_matrix.links}
    parents_without_children = parent_ids - parents_with_children

    if parents_without_children:
        warnings.append({
            "severity": "warning",
            "type": "uncovered_parents",
            "description": f"Found {len(parents_without_children)} parent requirements with no children",
            "affected_ids": list(parents_without_children)
        })

    # Calculate coverage statistics
    total_parents = len(parent_requirements)
    total_children = len(child_requirements)
    covered_parents = len(parents_with_children)
    orphaned_children = len(traceability_matrix.orphan_requirements)

    coverage_percentage = (covered_parents / total_parents * 100) if total_parents > 0 else 0

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "statistics": {
            "total_parents": total_parents,
            "total_children": total_children,
            "covered_parents": covered_parents,
            "uncovered_parents": len(parents_without_children),
            "orphaned_children": orphaned_children,
            "coverage_percentage": round(coverage_percentage, 2),
            "total_links": len(traceability_matrix.links)
        }
    }


def get_coverage_report(
    traceability_matrix: TraceabilityMatrix,
    parent_requirements: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generate a coverage report showing which parents have children.

    Args:
        traceability_matrix: The traceability matrix
        parent_requirements: List of parent requirement dicts

    Returns:
        Coverage report with per-parent statistics
    """
    # Count children per parent
    parent_child_count: Dict[str, int] = {}
    for req in parent_requirements:
        parent_child_count[req['id']] = 0

    for link in traceability_matrix.links:
        if link.parent_id in parent_child_count:
            parent_child_count[link.parent_id] += 1

    # Build coverage report
    coverage_details = []
    for req in parent_requirements:
        req_id = req['id']
        child_count = parent_child_count.get(req_id, 0)
        children = traceability_matrix.get_children(req_id)

        coverage_details.append({
            "parent_id": req_id,
            "parent_text": req.get('text', ''),
            "child_count": child_count,
            "children_ids": children,
            "covered": child_count > 0
        })

    # Calculate summary
    total_parents = len(parent_requirements)
    covered_parents = sum(1 for detail in coverage_details if detail['covered'])
    coverage_percentage = (covered_parents / total_parents * 100) if total_parents > 0 else 0

    return {
        "summary": {
            "total_parents": total_parents,
            "covered_parents": covered_parents,
            "uncovered_parents": total_parents - covered_parents,
            "coverage_percentage": round(coverage_percentage, 2)
        },
        "details": coverage_details
    }


def get_decomposition_tree(
    traceability_matrix: TraceabilityMatrix,
    parent_requirements: List[Dict[str, Any]],
    child_requirements: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Build a hierarchical tree view of the decomposition.

    Args:
        traceability_matrix: The traceability matrix
        parent_requirements: List of parent requirement dicts
        child_requirements: List of child requirement dicts

    Returns:
        List of parent requirement dicts with nested children
    """
    # Create lookup for child requirements
    children_by_id = {req['id']: req for req in child_requirements}

    # Build tree
    tree = []
    for parent_req in parent_requirements:
        parent_id = parent_req['id']
        child_ids = traceability_matrix.get_children(parent_id)

        # Get full child requirement data
        children = [
            children_by_id[child_id]
            for child_id in child_ids
            if child_id in children_by_id
        ]

        tree_node = {
            **parent_req,
            "children": children,
            "child_count": len(children)
        }
        tree.append(tree_node)

    return tree


def find_broken_links(
    traceability_matrix: TraceabilityMatrix,
    parent_requirements: List[Dict[str, Any]]
) -> List[Dict[str, str]]:
    """
    Find traceability links that reference non-existent parents.

    Args:
        traceability_matrix: The traceability matrix
        parent_requirements: List of parent requirement dicts

    Returns:
        List of broken links with details
    """
    parent_ids = {req['id'] for req in parent_requirements}
    broken_links = []

    for link in traceability_matrix.links:
        if link.parent_id not in parent_ids:
            broken_links.append({
                "child_id": link.child_id,
                "invalid_parent_id": link.parent_id,
                "issue": f"Child {link.child_id} references non-existent parent {link.parent_id}"
            })

    return broken_links


def export_traceability_matrix_csv(
    traceability_matrix: TraceabilityMatrix,
    parent_requirements: List[Dict[str, Any]],
    child_requirements: List[Dict[str, Any]]
) -> str:
    """
    Export traceability matrix to CSV format.

    Args:
        traceability_matrix: The traceability matrix
        parent_requirements: List of parent requirement dicts
        child_requirements: List of child requirement dicts

    Returns:
        CSV string representation of the traceability matrix
    """
    # Create lookups
    parent_lookup = {req['id']: req for req in parent_requirements}
    child_lookup = {req['id']: req for req in child_requirements}

    # Build CSV
    lines = ["Parent ID,Parent Text,Child ID,Child Text,Relationship Type"]

    for link in traceability_matrix.links:
        parent_req = parent_lookup.get(link.parent_id, {})
        child_req = child_lookup.get(link.child_id, {})

        parent_text = parent_req.get('text', 'Unknown').replace(',', ';')
        child_text = child_req.get('text', 'Unknown').replace(',', ';')

        line = f'"{link.parent_id}","{parent_text}","{link.child_id}","{child_text}","{link.relationship_type}"'
        lines.append(line)

    return '\n'.join(lines)
