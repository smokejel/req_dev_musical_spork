"""
Decompose node for the requirements decomposition workflow.

This node:
1. Validates that requirements and strategy exist in state
2. Uses RequirementsEngineerAgent to decompose requirements
3. Validates strategy adherence programmatically
4. Builds traceability matrix
5. Updates state with decomposed requirements and traceability
"""

from typing import Dict, Any
from datetime import datetime
import re

from src.state import DecompositionState, ErrorType, ErrorLog, DetailedRequirement
from src.agents.requirements_engineer import RequirementsEngineerAgent, AgentError
from src.utils.traceability import build_traceability_matrix, validate_traceability


def decompose_node(state: DecompositionState) -> DecompositionState:
    """
    Decompose system requirements into subsystem requirements.

    This is a LangGraph node function that processes the state and returns
    updated state with decomposed_requirements and traceability_matrix.

    Args:
        state: Current decomposition state

    Returns:
        Updated state with decomposed_requirements and traceability_matrix populated

    State Updates:
        - decomposed_requirements: List of serialized DetailedRequirement objects
        - traceability_matrix: Traceability matrix dict
        - errors: Error messages if decomposition fails
        - error_log: Detailed error tracking
        - fallback_count: Incremented if fallback model used
    """
    # Initialize errors list if not present
    errors = state.get('errors', [])
    error_log = state.get('error_log', [])

    try:
        # Validate required inputs
        if 'extracted_requirements' not in state:
            raise ValueError("Missing required field: extracted_requirements")

        if 'decomposition_strategy' not in state:
            raise ValueError("Missing required field: decomposition_strategy")

        if 'target_subsystem' not in state:
            raise ValueError("Missing required field: target_subsystem")

        extracted_requirements = state['extracted_requirements']
        decomposition_strategy = state['decomposition_strategy']
        target_subsystem = state['target_subsystem']

        # Validate inputs are not empty
        if not extracted_requirements:
            raise ValueError("Cannot decompose with no extracted requirements")

        if not decomposition_strategy:
            raise ValueError("Decomposition strategy cannot be empty")

        # Step 1: Decompose requirements using agent
        try:
            agent = RequirementsEngineerAgent()
            detailed_requirements = agent.decompose_requirements(
                system_requirements=extracted_requirements,
                decomposition_strategy=decomposition_strategy,
                target_subsystem=target_subsystem,
                enable_fallback=True
            )

            # Step 2: Validate strategy adherence
            strategy_violations = validate_strategy_adherence(
                requirements=detailed_requirements,
                strategy=decomposition_strategy,
                target_subsystem=target_subsystem
            )

            if strategy_violations:
                # Strategy violations are BUGS, not quality issues
                error_entry = ErrorLog(
                    timestamp=datetime.utcnow().isoformat(),
                    error_type=ErrorType.FATAL,
                    node="decompose",
                    message=f"Agent violated decomposition strategy: {len(strategy_violations)} violations",
                    details={'violations': strategy_violations}
                )
                error_log.append(error_entry.model_dump())
                errors.append(f"Strategy violations detected: {strategy_violations}")

                return {
                    **state,
                    'errors': errors,
                    'error_log': error_log,
                    'requires_human_review': True
                }

            # Step 3: Build traceability matrix
            detailed_reqs_dicts = [req.model_dump() for req in detailed_requirements]
            traceability_matrix = build_traceability_matrix(
                parent_requirements=extracted_requirements,
                child_requirements=detailed_reqs_dicts
            )

            # Step 4: Validate traceability
            trace_validation = validate_traceability(
                traceability_matrix=traceability_matrix,
                parent_requirements=extracted_requirements,
                child_requirements=detailed_reqs_dicts
            )

            if not trace_validation['valid']:
                # Traceability issues
                error_entry = ErrorLog(
                    timestamp=datetime.utcnow().isoformat(),
                    error_type=ErrorType.CONTENT,
                    node="decompose",
                    message=f"Traceability validation failed: {trace_validation['issues']}",
                    details=trace_validation
                )
                error_log.append(error_entry.model_dump())
                errors.append(f"Traceability validation failed")

                return {
                    **state,
                    'errors': errors,
                    'error_log': error_log,
                    'requires_human_review': True
                }

            # Serialize for state
            decomposed_reqs_serialized = detailed_reqs_dicts
            traceability_matrix_dict = traceability_matrix.model_dump()

            # Merge agent's error log with state error log
            agent_errors = agent.get_error_summary()
            if agent_errors['error_log']:
                error_log.extend(agent_errors['error_log'])

            # Update fallback count
            fallback_count = state.get('fallback_count', 0)
            fallback_count += agent_errors['fallback_count']

            # Success - return updated state
            return {
                **state,
                'decomposed_requirements': decomposed_reqs_serialized,
                'traceability_matrix': traceability_matrix_dict,
                'errors': errors,
                'error_log': error_log,
                'fallback_count': fallback_count
            }

        except AgentError as e:
            # Log content error (LLM or decomposition issue)
            error_entry = ErrorLog(
                timestamp=datetime.utcnow().isoformat(),
                error_type=ErrorType.CONTENT,
                node="decompose",
                message=f"Requirements decomposition failed: {str(e)}",
                details={'target_subsystem': target_subsystem}
            )
            error_log.append(error_entry.model_dump())
            errors.append(f"Requirements decomposition failed: {str(e)}")

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

    except ValueError as e:
        # Log fatal error (missing required inputs)
        error_entry = ErrorLog(
            timestamp=datetime.utcnow().isoformat(),
            error_type=ErrorType.FATAL,
            node="decompose",
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
            node="decompose",
            message=f"Unexpected error in decompose node: {str(e)}",
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


def validate_strategy_adherence(
    requirements: list,
    strategy: Dict[str, Any],
    target_subsystem: str
) -> list:
    """
    Validate that decomposed requirements adhere to the binding strategy.

    This is programmatic validation - strategy violations are BUGS, not quality issues.

    Args:
        requirements: List of DetailedRequirement objects
        strategy: Decomposition strategy dict
        target_subsystem: Expected target subsystem

    Returns:
        List of violation descriptions (empty if no violations)
    """
    violations = []
    naming_convention = strategy.get('naming_convention', '')
    acceptance_criteria_required = strategy.get('acceptance_criteria_required', False)

    for req in requirements:
        # Validate naming convention
        if naming_convention and not validate_naming_convention(req.id, naming_convention):
            violations.append(
                f"Requirement {req.id} does not match naming convention {naming_convention}"
            )

        # Validate subsystem assignment
        if req.subsystem != target_subsystem:
            violations.append(
                f"Requirement {req.id} assigned to '{req.subsystem}' instead of '{target_subsystem}'"
            )

        # Validate acceptance criteria if required
        if acceptance_criteria_required and not req.acceptance_criteria:
            violations.append(
                f"Requirement {req.id} missing acceptance criteria (required by strategy)"
            )

        # Validate parent_id exists
        if not req.parent_id:
            violations.append(
                f"Requirement {req.id} missing parent_id (traceability required)"
            )

    return violations


def validate_naming_convention(req_id: str, convention: str) -> bool:
    """
    Validate that a requirement ID matches the naming convention.

    Args:
        req_id: Requirement ID to validate
        convention: Naming convention pattern (e.g., "NAV-{TYPE}-{NNN}" or verbose form)

    Returns:
        True if ID matches convention, False otherwise
    """
    # Extract just the pattern if convention includes verbose description
    # E.g., "NAV-{TYPE}-{NNN} where TYPE is ..." -> "NAV-{TYPE}-{NNN}"
    pattern_match = re.match(r'^([A-Z\-\{\}]+)\s+where', convention)
    if pattern_match:
        base_pattern = pattern_match.group(1)
    else:
        base_pattern = convention.split()[0]  # Take first word if space-separated

    # Convert convention pattern to regex
    # Example: "NAV-{TYPE}-{NNN}" -> "NAV-(FUNC|PERF|CONS|INTF)-\d{3}"
    pattern = base_pattern.replace('{TYPE}', '(FUNC|PERF|CONS|INTF)')
    pattern = pattern.replace('{NNN}', r'\d{3}')
    pattern = f"^{pattern}$"

    return bool(re.match(pattern, req_id))
