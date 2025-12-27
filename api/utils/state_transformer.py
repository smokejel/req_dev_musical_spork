"""
State Transformation Utilities.

Converts backend state (snake_case) to frontend format (camelCase).
"""

from typing import Any, Dict, List, Optional
from api.models.database import WorkflowRun
from src.state import DecompositionState


def to_camel_case(snake_str: str) -> str:
    """
    Convert snake_case to camelCase.

    Args:
        snake_str: String in snake_case

    Returns:
        String in camelCase
    """
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def transform_dict(obj: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively transform dictionary keys from snake_case to camelCase.

    Args:
        obj: Dictionary with snake_case keys

    Returns:
        Dictionary with camelCase keys
    """
    if not isinstance(obj, dict):
        return obj

    result = {}
    for key, value in obj.items():
        camel_key = to_camel_case(key)

        if isinstance(value, dict):
            result[camel_key] = transform_dict(value)
        elif isinstance(value, list):
            result[camel_key] = [
                transform_dict(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[camel_key] = value

    return result


def transform_quality_metrics(metrics: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Transform quality metrics to frontend format.

    Frontend expects:
    interface QualityMetrics {
        overallScore: number;
        dimensions: DimensionScore[];
        passed: boolean;
        threshold: number;
        iterationCount: number;
    }

    interface DimensionScore {
        dimension: string;
        score: number;
        weight: number;
        issues: QualityIssue[];
    }

    Args:
        metrics: Quality metrics from state

    Returns:
        Frontend-formatted quality metrics
    """
    if not metrics:
        return None

    # Define dimensions
    dimension_names = ["completeness", "clarity", "testability", "traceability"]
    if metrics.get("domain_compliance") is not None:
        dimension_names.append("domain_compliance")

    # Construct dimensions array
    dimensions = []
    all_issues = metrics.get("issues", [])
    
    # Get weights if available, otherwise assume equal distribution
    weights = metrics.get("dimension_weights", {})
    default_weight = 1.0 / len(dimension_names) if dimension_names else 0.25

    for dim in dimension_names:
        # Filter issues for this dimension
        # Note: Issue dimension might be 'completeness', 'clarity' etc.
        dim_issues = [
            issue for issue in all_issues 
            if issue.get("dimension", "").lower() == dim.lower()
        ]

        dimensions.append({
            "dimension": to_camel_case(dim),
            "score": metrics.get(dim, 0.0),
            "weight": weights.get(dim, default_weight),
            "issues": dim_issues
        })

    return {
        "overallScore": metrics.get("overall_score", 0.0),
        "dimensions": dimensions,
        # 'passed', 'threshold', 'iterationCount' added at workflow level
    }


def transform_requirement(req: Dict[str, Any], is_decomposed: bool = False) -> Dict[str, Any]:
    """
    Transform a requirement object to frontend format.

    Args:
        req: Requirement dictionary
        is_decomposed: Whether this is a decomposed requirement (adds fields)

    Returns:
        Frontend-formatted requirement
    """
    # Map RequirementType enum to frontend category
    req_type = req.get("type", "functional")
    category_map = {
        "FUNC": "functional",
        "PERF": "performance",
        "CONS": "constraint",
        "INTF": "interface",
        "QUAL": "quality"
    }
    category = category_map.get(req_type, req_type.lower())

    transformed = {
        "id": req.get("id"),
        "text": req.get("text"),
        "category": category,
        "priority": req.get("priority", "medium"),
        
        # Extracted requirement fields
        "sourceLocation": req.get("source_section"),
        "originalText": req.get("text"), # Extracted often has original text
        
        # Decomposed requirement fields
        "subsystem": req.get("subsystem"),
        "rationale": req.get("rationale"),
        "acceptanceCriteria": req.get("acceptance_criteria", []),
        "parentId": req.get("parent_id"),
        
        # Frontend-specific aliases
        "parentRequirement": req.get("parent_id"), # Alias for DecomposedRequirement
        "derivationRationale": req.get("rationale"), # Alias for DecomposedRequirement
    }

    # Remove None values
    return {k: v for k, v in transformed.items() if v is not None}


def transform_workflow_state(
    workflow: WorkflowRun,
    state: Optional[DecompositionState] = None
) -> Dict[str, Any]:
    """
    Transform workflow and state to frontend response format.

    Args:
        workflow: WorkflowRun database record
        state: Optional final state from checkpoint

    Returns:
        Frontend-formatted workflow response
    """
    # Calculate metrics with fallbacks
    elapsed_time = workflow.elapsed_time if workflow.elapsed_time else (
        state.get("elapsed_time") if state else 0
    )
    
    total_tokens = workflow.token_count if workflow.token_count else (
        sum(
            node_tokens.get("input_tokens", 0) + node_tokens.get("output_tokens", 0)
            for node_tokens in state.get("token_usage", {}).values()
        ) if state else 0
    )

    total_cost = workflow.total_cost if workflow.total_cost else (
        state.get("total_cost") if state else 0.0
    )
    
    total_energy = workflow.energy_wh if workflow.energy_wh else (
        state.get("total_energy_wh") if state else 0.0
    )

    extracted_count = workflow.extracted_count if workflow.extracted_count else (
        len(state.get("extracted_requirements", [])) if state else 0
    )

    generated_count = workflow.generated_count if workflow.generated_count else (
        len(state.get("decomposed_requirements", [])) if state else 0
    )
    
    quality_score = workflow.quality_score if workflow.quality_score else (
        state.get("quality_metrics", {}).get("overall_score", 0.0) if state else 0.0
    )

    # Scale progress to 0-100
    progress = workflow.progress
    if progress is not None and progress <= 1.0:
        progress = progress * 100

    response = {
        "workflowId": workflow.id,  # Match frontend expected key
        "id": workflow.id,          # Keep original key just in case
        "projectName": workflow.project_name,
        "sourceDocument": workflow.source_document,
        "status": workflow.status.value,
        "dateCreated": workflow.created_at.isoformat() if workflow.created_at else None,  # Frontend expects dateCreated
        "createdAt": workflow.created_at.isoformat() if workflow.created_at else None,
        "startedAt": workflow.started_at.isoformat() if workflow.started_at else None,
        "completedAt": workflow.completed_at.isoformat() if workflow.completed_at else None,
        "currentNode": workflow.current_node,
        "progress": progress,
        
        # Metrics object matching WorkflowMetrics interface
        "metrics": {
            "elapsedTime": elapsed_time,
            "totalCost": total_cost,
            "totalEnergy": total_energy,
            "totalTokens": total_tokens,
            "requirementsExtracted": extracted_count,
            "requirementsGenerated": generated_count,
            "qualityScore": quality_score
        }
    }

    # Add configuration
    if workflow.config:
        response["config"] = {
            "domain": workflow.config.get("domain", "generic"),
            "targetSubsystem": workflow.config.get("subsystem"),
            "subsystemId": workflow.config.get("subsystem_id"),
            "qualityThreshold": workflow.config.get("quality_threshold", 0.80),
            "maxIterations": workflow.config.get("max_iterations", 3),
            "reviewMode": workflow.config.get("review_mode", "before"),
            "analysisMode": workflow.config.get("analysis_mode", "standard")
        }

    # Add state details if available
    if state:
        # Requirements
        extracted = state.get("extracted_requirements", [])
        decomposed = state.get("decomposed_requirements", [])

        response["extractedRequirements"] = [
            transform_requirement(req, is_decomposed=False) for req in extracted
        ] if extracted else []

        # Frontend expects 'decomposedRequirements' matching DecomposedRequirement interface
        response["decomposedRequirements"] = [
            transform_requirement(req, is_decomposed=True) for req in decomposed
        ] if decomposed else []

        # Keep 'requirements' for backward compatibility if needed
        response["requirements"] = response["decomposedRequirements"]

        # Add generated_count with state fallback
        response["generatedCount"] = workflow.generated_count if workflow.generated_count else (
            len(state.get("decomposed_requirements", [])) if state else 0
        )

        # Quality metrics
        metrics = transform_quality_metrics(state.get("quality_metrics"))
        if metrics:
            # Augment with workflow-level info
            metrics["passed"] = state.get("validation_passed", False)
            metrics["threshold"] = workflow.config.get("quality_threshold", 0.80) if workflow.config else 0.80
            metrics["iterationCount"] = state.get("iteration_count", 0)
            response["qualityMetrics"] = metrics

        # Validation issues
        response["issues"] = state.get("validation_issues", [])

        # Traceability
        response["traceabilityMatrix"] = state.get("traceability_matrix")

        # System context and strategy
        response["systemContext"] = state.get("system_context")
        response["decompositionStrategy"] = state.get("decomposition_strategy")

        # Iteration info
        response["iterationCount"] = state.get("iteration_count", 0)
        response["validationPassed"] = state.get("validation_passed", False)

        # Cost breakdown
        response["costBreakdown"] = state.get("cost_breakdown", {})
        response["timingBreakdown"] = state.get("timing_breakdown", {})
        response["energyBreakdown"] = state.get("energy_breakdown", {})

        # Token usage
        response["tokenUsage"] = state.get("token_usage", {})

        # Domain context (if present)
        domain_context = state.get("domain_context")
        if domain_context:
            response["domainContext"] = {
                "domainName": domain_context.get("domain_name"),
                "subsystemId": domain_context.get("subsystem_id"),
                "hasConventions": bool(domain_context.get("conventions")),
                "hasGlossary": bool(domain_context.get("glossary")),
                "hasExamples": bool(domain_context.get("examples"))
            }

        # Errors and warnings
        response["errors"] = state.get("errors", [])
        response["errorLog"] = state.get("error_log", [])
        response["fallbackCount"] = state.get("fallback_count", 0)

    # Remove None values
    return {k: v for k, v in response.items() if v is not None}