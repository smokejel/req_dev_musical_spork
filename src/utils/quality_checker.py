"""
Quality checker utility for automated requirements validation.

This module provides programmatic validation functions for:
- Structural validation (required fields, format)
- Traceability validation (parent-child links)
- Naming convention validation
- Acceptance criteria validation
- Duplicate detection
"""

import re
from typing import List, Dict, Any, Set


def validate_requirement_structure(requirement: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate that a requirement has all required fields and proper structure.

    Args:
        requirement: Requirement dict to validate

    Returns:
        Dict with validation results:
        - valid: bool
        - missing_fields: List[str]
        - issues: List[str]
    """
    required_fields = ['id', 'text', 'type', 'subsystem']
    recommended_fields = ['parent_id', 'acceptance_criteria', 'rationale']

    missing_required = [field for field in required_fields if field not in requirement]
    missing_recommended = [field for field in recommended_fields if field not in requirement or not requirement[field]]

    issues = []

    # Check required fields
    if missing_required:
        issues.append(f"Missing required fields: {', '.join(missing_required)}")

    # Check recommended fields
    if missing_recommended:
        issues.append(f"Missing recommended fields: {', '.join(missing_recommended)}")

    # Check text length
    if 'text' in requirement and len(requirement['text']) < 10:
        issues.append("Requirement text is too short (< 10 characters)")

    # Check type validity
    valid_types = ['FUNC', 'PERF', 'CONS', 'INTF']
    if 'type' in requirement:
        req_type = requirement['type']
        # Handle RequirementType enum
        if hasattr(req_type, 'value'):
            req_type_str = req_type.value
        else:
            req_type_str = str(req_type)

        if req_type_str not in valid_types:
            issues.append(f"Invalid type '{req_type_str}'. Must be one of: {', '.join(valid_types)}")

    return {
        'valid': len(missing_required) == 0,
        'missing_fields': missing_required,
        'issues': issues
    }


def check_naming_convention(
    req_id: str,
    naming_convention: str
) -> Dict[str, Any]:
    """
    Validate that a requirement ID matches the naming convention.

    Args:
        req_id: Requirement ID to validate
        naming_convention: Pattern like "NAV-{TYPE}-{NNN}"

    Returns:
        Dict with validation results:
        - valid: bool
        - pattern: str (regex pattern used)
        - issue: str (if invalid)
    """
    # Convert naming convention to regex
    # Example: "NAV-{TYPE}-{NNN}" -> "NAV-(FUNC|PERF|CONS|INTF)-\\d{3}"
    pattern = naming_convention.replace('{TYPE}', '(FUNC|PERF|CONS|INTF)')
    pattern = pattern.replace('{NNN}', r'\d{3}')
    pattern = f"^{pattern}$"

    matches = bool(re.match(pattern, req_id))

    return {
        'valid': matches,
        'pattern': pattern,
        'issue': f"ID '{req_id}' does not match naming convention '{naming_convention}'" if not matches else None
    }


def check_traceability(
    requirements: List[Dict[str, Any]],
    parent_requirements: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Validate traceability relationships between requirements.

    Args:
        requirements: List of child requirements to validate
        parent_requirements: List of parent requirements

    Returns:
        Dict with validation results:
        - valid: bool
        - orphaned_requirements: List[str] (IDs without parent_id)
        - broken_links: List[str] (parent_id references that don't exist)
        - uncovered_parents: List[str] (parents with no children)
    """
    orphaned = []
    broken_links = []

    # Build set of valid parent IDs
    parent_ids = {req['id'] for req in parent_requirements if 'id' in req}

    # Track which parents have children
    parents_with_children = set()

    for req in requirements:
        req_id = req.get('id', 'UNKNOWN')
        parent_id = req.get('parent_id')

        if not parent_id:
            orphaned.append(req_id)
        elif parent_id not in parent_ids:
            broken_links.append(f"{req_id} references non-existent parent '{parent_id}'")
        else:
            parents_with_children.add(parent_id)

    # Find parents without children
    uncovered_parents = list(parent_ids - parents_with_children)

    return {
        'valid': len(orphaned) == 0 and len(broken_links) == 0,
        'orphaned_requirements': orphaned,
        'broken_links': broken_links,
        'uncovered_parents': uncovered_parents
    }


def check_acceptance_criteria(
    requirement: Dict[str, Any],
    required: bool = True
) -> Dict[str, Any]:
    """
    Validate acceptance criteria for a requirement.

    Args:
        requirement: Requirement to validate
        required: Whether acceptance criteria are required by strategy

    Returns:
        Dict with validation results:
        - valid: bool
        - has_criteria: bool
        - criteria_count: int
        - issues: List[str]
    """
    acceptance_criteria = requirement.get('acceptance_criteria', [])
    has_criteria = bool(acceptance_criteria) and len(acceptance_criteria) > 0

    issues = []

    if required and not has_criteria:
        issues.append(f"Missing required acceptance criteria for {requirement.get('id', 'UNKNOWN')}")

    if has_criteria:
        # Check for vague criteria
        vague_terms = ['correctly', 'properly', 'adequately', 'appropriately', 'well']
        for criterion in acceptance_criteria:
            criterion_lower = criterion.lower()
            for term in vague_terms:
                if term in criterion_lower:
                    issues.append(f"Acceptance criterion contains vague term '{term}': {criterion}")

    return {
        'valid': len(issues) == 0,
        'has_criteria': has_criteria,
        'criteria_count': len(acceptance_criteria) if has_criteria else 0,
        'issues': issues
    }


def detect_orphans(requirements: List[Dict[str, Any]]) -> List[str]:
    """
    Detect requirements without parent_id.

    Args:
        requirements: List of requirements

    Returns:
        List of requirement IDs that are orphaned (no parent_id)
    """
    orphans = []
    for req in requirements:
        if not req.get('parent_id'):
            orphans.append(req.get('id', 'UNKNOWN'))
    return orphans


def detect_duplicates(requirements: List[Dict[str, Any]]) -> Dict[str, List[int]]:
    """
    Detect duplicate requirement IDs.

    Args:
        requirements: List of requirements

    Returns:
        Dict mapping duplicate ID to list of indices where it appears
    """
    id_map: Dict[str, List[int]] = {}

    for idx, req in enumerate(requirements):
        req_id = req.get('id', 'UNKNOWN')
        if req_id not in id_map:
            id_map[req_id] = []
        id_map[req_id].append(idx)

    # Filter to only duplicates
    duplicates = {req_id: indices for req_id, indices in id_map.items() if len(indices) > 1}

    return duplicates


def detect_vague_language(requirement_text: str) -> List[str]:
    """
    Detect vague or ambiguous terms in requirement text.

    Args:
        requirement_text: Requirement text to analyze

    Returns:
        List of vague terms found
    """
    vague_terms = [
        'fast', 'slow', 'quickly', 'slowly',
        'user-friendly', 'easy', 'simple',
        'adequate', 'sufficient', 'reasonable', 'appropriate',
        'robust', 'reliable', 'stable',
        'good', 'bad', 'better', 'best',
        'efficient', 'optimal',
        'minimal', 'maximum',
        'as needed', 'if necessary'
    ]

    text_lower = requirement_text.lower()
    found_terms = []

    for term in vague_terms:
        # Use word boundaries to avoid false positives
        pattern = r'\b' + re.escape(term) + r'\b'
        if re.search(pattern, text_lower):
            found_terms.append(term)

    return found_terms


def calculate_automated_scores(
    requirements: List[Dict[str, Any]],
    parent_requirements: List[Dict[str, Any]],
    strategy: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculate automated quality scores based on structural validation.

    Args:
        requirements: List of child requirements
        parent_requirements: List of parent requirements
        strategy: Decomposition strategy dict

    Returns:
        Dict with automated quality metrics:
        - structure_score: float (0.0-1.0)
        - traceability_score: float (0.0-1.0)
        - naming_score: float (0.0-1.0)
        - acceptance_criteria_score: float (0.0-1.0)
        - issues: List[Dict]
    """
    issues = []
    total_reqs = len(requirements)

    if total_reqs == 0:
        return {
            'structure_score': 0.0,
            'traceability_score': 0.0,
            'naming_score': 0.0,
            'acceptance_criteria_score': 0.0,
            'issues': [{'severity': 'critical', 'description': 'No requirements to validate'}]
        }

    # Structure validation
    structure_valid_count = 0
    for req in requirements:
        result = validate_requirement_structure(req)
        if result['valid']:
            structure_valid_count += 1
        else:
            for issue in result['issues']:
                issues.append({
                    'severity': 'critical' if result['missing_fields'] else 'major',
                    'requirement_id': req.get('id', 'UNKNOWN'),
                    'dimension': 'structure',
                    'description': issue
                })

    structure_score = structure_valid_count / total_reqs

    # Traceability validation
    trace_result = check_traceability(requirements, parent_requirements)

    orphan_count = len(trace_result['orphaned_requirements'])
    broken_count = len(trace_result['broken_links'])
    traceability_issues = orphan_count + broken_count

    traceability_score = max(0.0, 1.0 - (traceability_issues / total_reqs))

    for orphan_id in trace_result['orphaned_requirements']:
        issues.append({
            'severity': 'critical',
            'requirement_id': orphan_id,
            'dimension': 'traceability',
            'description': 'Missing parent_id (orphaned requirement)'
        })

    for broken_link in trace_result['broken_links']:
        issues.append({
            'severity': 'critical',
            'requirement_id': None,
            'dimension': 'traceability',
            'description': broken_link
        })

    # Naming convention validation
    naming_convention = strategy.get('naming_convention', '')
    naming_valid_count = 0

    if naming_convention:
        for req in requirements:
            req_id = req.get('id', '')
            result = check_naming_convention(req_id, naming_convention)
            if result['valid']:
                naming_valid_count += 1
            else:
                issues.append({
                    'severity': 'critical',
                    'requirement_id': req_id,
                    'dimension': 'traceability',
                    'description': result['issue']
                })

        naming_score = naming_valid_count / total_reqs
    else:
        naming_score = 1.0  # No convention to enforce

    # Acceptance criteria validation
    ac_required = strategy.get('acceptance_criteria_required', True)
    ac_valid_count = 0

    for req in requirements:
        result = check_acceptance_criteria(req, required=ac_required)
        if result['valid']:
            ac_valid_count += 1
        else:
            for issue in result['issues']:
                issues.append({
                    'severity': 'major' if ac_required else 'minor',
                    'requirement_id': req.get('id', 'UNKNOWN'),
                    'dimension': 'testability',
                    'description': issue
                })

    acceptance_criteria_score = ac_valid_count / total_reqs

    return {
        'structure_score': structure_score,
        'traceability_score': traceability_score,
        'naming_score': naming_score,
        'acceptance_criteria_score': acceptance_criteria_score,
        'issues': issues
    }


def validate_all_requirements(
    requirements: List[Dict[str, Any]],
    parent_requirements: List[Dict[str, Any]],
    traceability_matrix: Dict[str, Any],
    strategy: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Run comprehensive validation on all requirements.

    This is the main entry point for automated validation.

    Args:
        requirements: List of child requirements to validate
        parent_requirements: List of parent requirements
        traceability_matrix: Traceability matrix dict
        strategy: Decomposition strategy

    Returns:
        Comprehensive validation results with scores and issues
    """
    # Calculate automated scores
    automated_scores = calculate_automated_scores(
        requirements,
        parent_requirements,
        strategy
    )

    # Detect duplicates
    duplicates = detect_duplicates(requirements)
    if duplicates:
        for req_id, indices in duplicates.items():
            automated_scores['issues'].append({
                'severity': 'critical',
                'requirement_id': req_id,
                'dimension': 'structure',
                'description': f"Duplicate requirement ID found at indices {indices}"
            })

    # Detect vague language
    for req in requirements:
        vague_terms = detect_vague_language(req.get('text', ''))
        if vague_terms:
            automated_scores['issues'].append({
                'severity': 'major',
                'requirement_id': req.get('id', 'UNKNOWN'),
                'dimension': 'clarity',
                'description': f"Contains vague terms: {', '.join(vague_terms)}"
            })

    return automated_scores
