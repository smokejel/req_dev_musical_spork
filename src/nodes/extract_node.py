"""
Extract node for the requirements decomposition workflow.

This node:
1. Loads the specification document
2. Parses it to extract text content
3. Uses RequirementsAnalystAgent to extract requirements
4. Updates state with extracted requirements
"""

from typing import Dict, Any
from datetime import datetime

from src.state import DecompositionState, ErrorType, ErrorLog
from src.utils.document_parser import parse_document, DocumentParseError
from src.agents.requirements_analyst import RequirementsAnalystAgent, AgentError


def extract_node(state: DecompositionState) -> DecompositionState:
    """
    Extract requirements from the specification document.

    This is a LangGraph node function that processes the state and returns
    updated state with extracted requirements.

    Args:
        state: Current decomposition state

    Returns:
        Updated state with extracted_requirements populated

    State Updates:
        - extracted_requirements: List of serialized Requirement objects
        - errors: Error messages if extraction fails
        - error_log: Detailed error tracking
    """
    # Initialize errors list if not present
    errors = state.get('errors', [])
    error_log = state.get('error_log', [])

    try:
        # Validate required inputs
        if 'spec_document_path' not in state:
            raise ValueError("Missing required field: spec_document_path")

        spec_path = state['spec_document_path']

        # Load domain context if domain specified (Phase 7.2)
        domain_context = None
        domain_name = state.get('domain_name', 'generic')
        subsystem_id = state.get('subsystem_id')

        if domain_name and domain_name != 'generic':
            try:
                from src.utils.domain_loader import DomainLoader, DomainLoadError

                # Load domain context (conventions, glossary, examples)
                domain_context = DomainLoader.load_context(
                    domain_name=domain_name,
                    subsystem_id=subsystem_id
                )

                # Log successful load
                error_log.append({
                    'timestamp': datetime.utcnow().isoformat(),
                    'error_type': 'INFO',
                    'node': 'extract',
                    'message': f"Loaded domain context: {domain_name}" + (f"/{subsystem_id}" if subsystem_id else ""),
                    'details': {'domain_name': domain_name, 'subsystem_id': subsystem_id}
                })

            except DomainLoadError as e:
                # Non-fatal: fall back to generic domain
                error_log.append({
                    'timestamp': datetime.utcnow().isoformat(),
                    'error_type': 'CONTENT',
                    'node': 'extract',
                    'message': f"Domain loading failed, using generic domain: {str(e)}",
                    'details': {'requested_domain': domain_name}
                })
                domain_context = None  # Fall back to generic

        # Step 1: Parse the document
        try:
            document_text, file_type = parse_document(spec_path)

        except DocumentParseError as e:
            # Log fatal error (missing file or corrupted document)
            error_entry = ErrorLog(
                timestamp=datetime.utcnow().isoformat(),
                error_type=ErrorType.FATAL,
                node="extract",
                message=f"Document parsing failed: {str(e)}",
                details={'file_path': spec_path}
            )
            error_log.append(error_entry.model_dump())
            errors.append(f"Document parsing failed: {str(e)}")

            return {
                **state,
                'errors': errors,
                'error_log': error_log,
                'requires_human_review': True
            }

        # Step 2: Extract requirements using agent
        try:
            agent = RequirementsAnalystAgent()
            requirements = agent.extract_requirements(
                document_text=document_text,
                enable_fallback=True
            )

            # Serialize requirements to dictionaries for state
            serialized_requirements = [
                req.model_dump() for req in requirements
            ]

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
                'extracted_requirements': serialized_requirements,
                'domain_context': domain_context,  # Phase 7.2: Include loaded domain context
                'errors': errors,
                'error_log': error_log,
                'fallback_count': fallback_count
            }

        except AgentError as e:
            # Log content error (LLM or parsing issue)
            error_entry = ErrorLog(
                timestamp=datetime.utcnow().isoformat(),
                error_type=ErrorType.CONTENT,
                node="extract",
                message=f"Requirements extraction failed: {str(e)}",
                details={'document_type': file_type}
            )
            error_log.append(error_entry.model_dump())
            errors.append(f"Requirements extraction failed: {str(e)}")

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

    except Exception as e:
        # Catch-all for unexpected errors
        error_entry = ErrorLog(
            timestamp=datetime.utcnow().isoformat(),
            error_type=ErrorType.FATAL,
            node="extract",
            message=f"Unexpected error in extract node: {str(e)}",
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
