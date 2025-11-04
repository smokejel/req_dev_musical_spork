"""
Validate node for the requirements decomposition workflow.

This node:
1. Runs automated quality checks (structure, traceability, naming, etc.)
2. Uses QualityAssuranceAgent for LLM-based quality assessment
3. Combines automated + LLM scores into final quality metrics
4. Applies quality gate threshold (0.80 default)
5. Generates refinement feedback for failed validations
6. Updates state with quality metrics and validation results
"""

from typing import Dict, Any, List
from datetime import datetime

from src.state import DecompositionState, ErrorType, ErrorLog, QualityMetrics
from src.agents.quality_assurance import QualityAssuranceAgent, AgentError
from src.utils import quality_checker


def validate_node(state: DecompositionState) -> DecompositionState:
    """
    Validate decomposed requirements quality.

    This is a LangGraph node function that processes the state and returns
    updated state with quality_metrics and validation_passed.

    Args:
        state: Current decomposition state

    Returns:
        Updated state with quality metrics and validation results

    State Updates:
        - quality_metrics: Quality assessment scores and issues
        - validation_passed: Boolean indicating if quality gate passed
        - refinement_feedback: Specific feedback for iteration (if failed)
        - validation_issues: List of quality issues
        - requires_human_review: Flag if human review needed
        - errors: Error messages if validation fails
        - error_log: Detailed error tracking
    """
    # Initialize errors list if not present
    errors = state.get('errors', [])
    error_log = state.get('error_log', [])

    try:
        # Validate required inputs
        if 'decomposed_requirements' not in state:
            raise ValueError("Missing required field: decomposed_requirements")

        if 'extracted_requirements' not in state:
            raise ValueError("Missing required field: extracted_requirements")

        if 'decomposition_strategy' not in state:
            raise ValueError("Missing required field: decomposition_strategy")

        decomposed_requirements = state['decomposed_requirements']
        extracted_requirements = state['extracted_requirements']
        decomposition_strategy = state['decomposition_strategy']
        traceability_matrix = state.get('traceability_matrix', {})

        # Handle zero requirements as valid case (none allocated to subsystem)
        if not decomposed_requirements:
            # Return successful validation with perfect scores
            # This indicates correct allocation: no requirements matched the subsystem
            return {
                **state,
                'quality_metrics': {
                    'overall_score': 1.0,
                    'completeness': 1.0,
                    'clarity': 1.0,
                    'testability': 1.0,
                    'traceability': 1.0,
                    'validation_type': 'no_requirements_allocated',
                    'issues': []
                },
                'validation_passed': True,
                'validation_issues': [],
                'errors': errors,
                'error_log': error_log
            }

        # Get quality threshold (default 0.80)
        quality_threshold = state.get('quality_threshold', 0.80)

        # Step 1: Run automated quality checks
        try:
            automated_results = quality_checker.validate_all_requirements(
                requirements=decomposed_requirements,
                parent_requirements=extracted_requirements,
                traceability_matrix=traceability_matrix,
                strategy=decomposition_strategy
            )

        except Exception as e:
            error_entry = ErrorLog(
                timestamp=datetime.utcnow().isoformat(),
                error_type=ErrorType.CONTENT,
                node="validate",
                message=f"Automated quality checking failed: {str(e)}",
                details={}
            )
            error_log.append(error_entry.model_dump())
            errors.append(f"Automated validation failed: {str(e)}")

            return {
                **state,
                'errors': errors,
                'error_log': error_log,
                'requires_human_review': True
            }

        # Step 2: Run LLM-based quality assessment
        try:
            agent = QualityAssuranceAgent()
            quality_metrics = agent.assess_quality(
                requirements=decomposed_requirements,
                automated_results=automated_results,
                strategy=decomposition_strategy,
                enable_fallback=True
            )

        except AgentError as e:
            # Log content error (LLM or assessment issue)
            error_entry = ErrorLog(
                timestamp=datetime.utcnow().isoformat(),
                error_type=ErrorType.CONTENT,
                node="validate",
                message=f"Quality assessment failed: {str(e)}",
                details={}
            )
            error_log.append(error_entry.model_dump())
            errors.append(f"Quality assessment failed: {str(e)}")

            # Merge agent's error log even on failure
            try:
                agent_errors = agent.get_error_summary()
                if agent_errors['error_log']:
                    error_log.extend(agent_errors['error_log'])
            except:
                pass  # Agent may not be initialized

            return {
                **state,
                'errors': errors,
                'error_log': error_log,
                'requires_human_review': True
            }

        # Step 3: Apply quality gate
        validation_passed = apply_quality_gate(
            quality_metrics=quality_metrics,
            threshold=quality_threshold
        )

        # Step 4: Generate refinement feedback if failed
        refinement_feedback = None
        if not validation_passed:
            try:
                refinement_feedback = agent.generate_refinement_feedback(
                    quality_metrics=quality_metrics,
                    requirements=decomposed_requirements,
                    strategy=decomposition_strategy
                )
            except Exception as e:
                # Feedback generation is not critical
                error_log.append({
                    'timestamp': datetime.utcnow().isoformat(),
                    'error_type': 'CONTENT',
                    'node': 'validate',
                    'message': f"Feedback generation failed: {str(e)}",
                    'details': {}
                })

        # Step 5: Determine if human review is required
        iteration_count = state.get('iteration_count', 0)
        max_iterations = state.get('max_iterations', 3)

        requires_human_review = determine_human_review_required(
            quality_metrics=quality_metrics,
            validation_passed=validation_passed,
            iteration_count=iteration_count,
            max_iterations=max_iterations
        )

        # Serialize quality metrics for state
        quality_metrics_dict = quality_metrics.model_dump()
        validation_issues_list = [issue.model_dump() for issue in quality_metrics.issues]

        # Merge agent's error log
        agent_errors = agent.get_error_summary()
        if agent_errors['error_log']:
            error_log.extend(agent_errors['error_log'])

        # Update fallback count
        fallback_count = state.get('fallback_count', 0)
        fallback_count += agent_errors['fallback_count']

        # Success - return updated state
        return {
            **state,
            'quality_metrics': quality_metrics_dict,
            'validation_passed': validation_passed,
            'refinement_feedback': refinement_feedback,
            'validation_issues': validation_issues_list,
            'requires_human_review': requires_human_review,
            'errors': errors,
            'error_log': error_log,
            'fallback_count': fallback_count
        }

    except ValueError as e:
        # Log fatal error (missing required inputs)
        error_entry = ErrorLog(
            timestamp=datetime.utcnow().isoformat(),
            error_type=ErrorType.FATAL,
            node="validate",
            message=f"Validation error: {str(e)}",
            details={}
        )
        error_log.append(error_entry.model_dump())
        errors.append(f"Validation error: {str(e)}")

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
            node="validate",
            message=f"Unexpected error in validate node: {str(e)}",
            details={'error_type': type(e).__name__}
        )
        error_log.append(error_entry.model_dump())
        errors.append(f"Unexpected error: {str(e)}")

        return {
            **state,
            'errors': errors,
            'error_log': error_log,
            'requires_human_review': True
        }


def apply_quality_gate(
    quality_metrics: QualityMetrics,
    threshold: float = 0.80
) -> bool:
    """
    Apply quality gate to determine if requirements pass.

    Args:
        quality_metrics: Quality assessment results
        threshold: Minimum overall score required (default 0.80)

    Returns:
        True if quality gate passes, False otherwise

    Quality Gate Rules:
        - overall_score must be >= threshold
        - AND no CRITICAL issues present
    """
    # Check overall score
    if quality_metrics.overall_score < threshold:
        return False

    # Check for critical issues
    from src.state import QualitySeverity
    critical_issues = [
        issue for issue in quality_metrics.issues
        if issue.severity == QualitySeverity.CRITICAL
    ]

    if critical_issues:
        return False

    return True


def determine_human_review_required(
    quality_metrics: QualityMetrics,
    validation_passed: bool,
    iteration_count: int,
    max_iterations: int
) -> bool:
    """
    Determine if human review is required.

    Args:
        quality_metrics: Quality assessment results
        validation_passed: Whether validation passed quality gate
        iteration_count: Current iteration count
        max_iterations: Maximum iterations allowed

    Returns:
        True if human review is required, False otherwise

    Human Review Triggers:
        - overall_score < 0.60 (very low quality)
        - iteration_count >= max_iterations (exhausted attempts)
    """
    # Very low quality score
    if quality_metrics.overall_score < 0.60:
        return True

    # Exhausted iteration limit
    if iteration_count >= max_iterations:
        return True

    return False


def compute_quality_metrics(
    automated_results: Dict[str, Any],
    llm_assessment: QualityMetrics
) -> QualityMetrics:
    """
    Combine automated and LLM assessment results into final quality metrics.

    This function is currently a pass-through since the QualityAssuranceAgent
    already considers automated results. In future, this could implement
    weighted averaging or other combination strategies.

    Args:
        automated_results: Automated validation results
        llm_assessment: LLM-based quality assessment

    Returns:
        Combined quality metrics
    """
    # For now, trust the LLM assessment which already considers automated results
    return llm_assessment


def generate_refinement_guidance(
    issues: List[Dict[str, Any]],
    requirements: List[Dict[str, Any]],
    strategy: Dict[str, Any]
) -> str:
    """
    Generate specific, actionable refinement guidance.

    This is a helper function that can be called independently of the
    QualityAssuranceAgent for testing or manual guidance generation.

    Args:
        issues: List of quality issues
        requirements: List of requirements
        strategy: Decomposition strategy

    Returns:
        Formatted refinement guidance string
    """
    feedback_lines = []

    feedback_lines.append("## Refinement Guidance\n")

    # Group issues by severity
    critical = [i for i in issues if i.get('severity') == 'critical']
    major = [i for i in issues if i.get('severity') == 'major']
    minor = [i for i in issues if i.get('severity') == 'minor']

    if critical:
        feedback_lines.append("### CRITICAL Issues (Must Fix):")
        for issue in critical:
            req_id = issue.get('requirement_id', 'GENERAL')
            desc = issue.get('description', '')
            sugg = issue.get('suggestion', '')
            feedback_lines.append(f"- [{req_id}] {desc}")
            if sugg:
                feedback_lines.append(f"  → {sugg}")
        feedback_lines.append("")

    if major:
        feedback_lines.append("### MAJOR Issues (Should Fix):")
        for issue in major:
            req_id = issue.get('requirement_id', 'GENERAL')
            desc = issue.get('description', '')
            sugg = issue.get('suggestion', '')
            feedback_lines.append(f"- [{req_id}] {desc}")
            if sugg:
                feedback_lines.append(f"  → {sugg}")
        feedback_lines.append("")

    if minor and len(minor) <= 5:
        feedback_lines.append("### MINOR Issues (Nice to Have):")
        for issue in minor:
            req_id = issue.get('requirement_id', 'GENERAL')
            desc = issue.get('description', '')
            feedback_lines.append(f"- [{req_id}] {desc}")
        feedback_lines.append("")

    return "\n".join(feedback_lines)
