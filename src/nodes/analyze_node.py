"""
Analyze node for the requirements decomposition workflow.

This node:
1. Validates that requirements have been extracted
2. Uses SystemArchitectAgent to analyze system architecture
3. Creates a binding decomposition strategy
4. Updates state with system context and strategy
"""

from typing import Dict, Any
from datetime import datetime

from src.state import DecompositionState, ErrorType, ErrorLog
from src.agents.system_architect import SystemArchitectAgent, AgentError


def analyze_node(state: DecompositionState) -> DecompositionState:
    """
    Analyze system architecture and create decomposition strategy.

    This is a LangGraph node function that processes the state and returns
    updated state with system_context and decomposition_strategy.

    Args:
        state: Current decomposition state

    Returns:
        Updated state with system_context and decomposition_strategy populated

    State Updates:
        - system_context: System architecture understanding
        - decomposition_strategy: Binding strategy for decomposition
        - errors: Error messages if analysis fails
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

        if 'target_subsystem' not in state:
            raise ValueError("Missing required field: target_subsystem")

        extracted_requirements = state['extracted_requirements']
        target_subsystem = state['target_subsystem']

        # Validate extracted_requirements is not empty
        if not extracted_requirements:
            raise ValueError("Cannot analyze system with no extracted requirements")

        # Step 1: Analyze system using agent
        try:
            agent = SystemArchitectAgent()
            system_context, decomposition_strategy = agent.analyze_system(
                requirements=extracted_requirements,
                target_subsystem=target_subsystem,
                enable_fallback=True
            )

            # Serialize to dictionaries for state
            system_context_dict = system_context.model_dump()
            decomposition_strategy_dict = decomposition_strategy.model_dump()

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
                'system_context': system_context_dict,
                'decomposition_strategy': decomposition_strategy_dict,
                'errors': errors,
                'error_log': error_log,
                'fallback_count': fallback_count
            }

        except AgentError as e:
            # Log content error (LLM or parsing issue)
            error_entry = ErrorLog(
                timestamp=datetime.utcnow().isoformat(),
                error_type=ErrorType.CONTENT,
                node="analyze",
                message=f"System analysis failed: {str(e)}",
                details={'target_subsystem': target_subsystem}
            )
            error_log.append(error_entry.model_dump())
            errors.append(f"System analysis failed: {str(e)}")

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
            node="analyze",
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
            node="analyze",
            message=f"Unexpected error in analyze node: {str(e)}",
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
