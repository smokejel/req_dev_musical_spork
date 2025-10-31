"""
Requirements Analyst Agent for extracting requirements from specification documents.

Uses the requirements-extraction skill to parse documents and extract
atomic, testable requirements with proper IDs and categorization.
"""

import json
from typing import List, Dict, Any
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.base_agent import BaseAgent, AgentError
from src.state import Requirement, RequirementType
from config.llm_config import NodeType


class RequirementsAnalystAgent(BaseAgent):
    """
    Agent responsible for extracting requirements from source documents.

    Uses the requirements-extraction skill to guide LLM behavior.
    Outputs a list of Requirement objects with proper IDs, types, and text.
    """

    def __init__(self):
        """Initialize the Requirements Analyst Agent with extraction skill."""
        super().__init__(
            node_type=NodeType.EXTRACT,
            skill_name="requirements-extraction"
        )

    def _parse_llm_response(self, response_text: str) -> List[Dict[str, Any]]:
        """
        Parse the LLM's JSON response into a list of requirement dictionaries.

        Args:
            response_text: Raw text response from LLM

        Returns:
            List of requirement dictionaries

        Raises:
            AgentError: If JSON parsing fails or format is invalid
        """
        # Clean the response - remove markdown code blocks if present
        cleaned = response_text.strip()

        # Remove ```json and ``` markers if present
        if cleaned.startswith('```'):
            lines = cleaned.split('\n')
            # Remove first line (```json or ```)
            lines = lines[1:]
            # Remove last line if it's ```
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            cleaned = '\n'.join(lines).strip()

        try:
            parsed = json.loads(cleaned)

            # Ensure it's a list
            if not isinstance(parsed, list):
                raise AgentError(
                    f"Expected JSON array, got {type(parsed).__name__}"
                )

            # Validate each requirement has required fields
            for idx, req in enumerate(parsed):
                if not isinstance(req, dict):
                    raise AgentError(
                        f"Requirement {idx} is not a dictionary: {req}"
                    )

                required_fields = ['id', 'text', 'type']
                missing_fields = [f for f in required_fields if f not in req]

                if missing_fields:
                    raise AgentError(
                        f"Requirement {idx} missing fields: {missing_fields}"
                    )

            return parsed

        except json.JSONDecodeError as e:
            raise AgentError(
                f"Failed to parse JSON response: {str(e)}. "
                f"Response: {cleaned[:200]}..."
            )

    def _validate_and_convert_requirements(
        self,
        req_dicts: List[Dict[str, Any]]
    ) -> List[Requirement]:
        """
        Validate and convert requirement dictionaries to Requirement objects.

        Args:
            req_dicts: List of requirement dictionaries from LLM

        Returns:
            List of validated Requirement objects

        Raises:
            AgentError: If validation fails
        """
        requirements = []

        for idx, req_dict in enumerate(req_dicts):
            try:
                # Map type string to enum
                req_type_str = req_dict.get('type', '').upper()

                # Handle different type formats
                if req_type_str in ['FUNC', 'FUNCTIONAL']:
                    req_type = RequirementType.FUNCTIONAL
                elif req_type_str in ['PERF', 'PERFORMANCE']:
                    req_type = RequirementType.PERFORMANCE
                elif req_type_str in ['CONS', 'CONSTRAINT']:
                    req_type = RequirementType.CONSTRAINT
                elif req_type_str in ['INTF', 'INTERFACE']:
                    req_type = RequirementType.INTERFACE
                else:
                    raise ValueError(
                        f"Invalid requirement type: {req_type_str}. "
                        f"Must be FUNC, PERF, CONS, or INTF"
                    )

                # Create Requirement object (this validates ID format)
                requirement = Requirement(
                    id=req_dict['id'],
                    text=req_dict['text'],
                    type=req_type,
                    source_section=req_dict.get('source_section')
                )

                requirements.append(requirement)

            except Exception as e:
                raise AgentError(
                    f"Failed to validate requirement {idx} ({req_dict.get('id', 'unknown')}): {str(e)}"
                )

        return requirements

    def extract_requirements(
        self,
        document_text: str,
        enable_fallback: bool = True
    ) -> List[Requirement]:
        """
        Extract requirements from document text.

        Args:
            document_text: Full text content of the specification document
            enable_fallback: Whether to enable model fallback on errors

        Returns:
            List of extracted Requirement objects

        Raises:
            AgentError: If extraction fails
        """
        if not document_text or not document_text.strip():
            raise AgentError("Document text is empty")

        # Define the execution function
        def _execute_extraction(llm: BaseChatModel) -> List[Requirement]:
            """Inner function that performs the extraction with a given LLM."""

            # Build the prompt
            system_prompt = f"""You are a requirements extraction expert. Your task is to analyze a specification document and extract individual, atomic requirements.

{self.get_skill_content()}

IMPORTANT: Return ONLY a valid JSON array. Do not include any explanatory text before or after the JSON."""

            user_prompt = f"""Extract all requirements from the following specification document:

{document_text}

Return the requirements as a JSON array following the format specified in the skill."""

            # Create messages
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]

            # Invoke LLM
            response = llm.invoke(messages)

            # Parse response
            response_text = response.content

            # Parse JSON
            req_dicts = self._parse_llm_response(response_text)

            # Validate and convert to Requirement objects
            requirements = self._validate_and_convert_requirements(req_dicts)

            return requirements

        # Execute with fallback handling
        try:
            requirements = self.execute_with_fallback(
                execution_func=_execute_extraction,
                enable_fallback=enable_fallback
            )

            if not requirements:
                raise AgentError("No requirements extracted from document")

            return requirements

        except Exception as e:
            raise AgentError(f"Requirements extraction failed: {str(e)}")

    def execute(
        self,
        document_text: str,
        enable_fallback: bool = True
    ) -> List[Requirement]:
        """
        Execute the agent's main task (extract requirements).

        This is the main entry point for the agent, called by the workflow node.

        Args:
            document_text: Full text content of the specification document
            enable_fallback: Whether to enable model fallback on errors

        Returns:
            List of extracted Requirement objects

        Raises:
            AgentError: If extraction fails
        """
        return self.extract_requirements(
            document_text=document_text,
            enable_fallback=enable_fallback
        )
