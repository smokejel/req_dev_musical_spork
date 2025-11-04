"""
Requirements Engineer Agent for decomposing system requirements into subsystem requirements.

This agent:
1. Loads the requirements-decomposition skill
2. Takes system requirements and a binding decomposition strategy
3. Decomposes requirements following the strategy exactly
4. Maintains complete traceability
"""

import json
import re
from typing import List, Tuple, Dict, Any

from src.agents.base_agent import BaseAgent, AgentError
from src.state import DetailedRequirement, RequirementType
from config.llm_config import NodeType


class RequirementsEngineerAgent(BaseAgent):
    """
    Agent responsible for decomposing system requirements into detailed subsystem requirements.

    Uses the 'requirements-decomposition' skill to:
    - Apply decomposition strategy (binding contract)
    - Break down requirements using appropriate patterns
    - Maintain complete traceability
    - Generate testable acceptance criteria
    """

    def __init__(self):
        """Initialize the Requirements Engineer Agent with requirements-decomposition skill."""
        super().__init__(
            node_type=NodeType.DECOMPOSE,
            skill_name="requirements-decomposition"
        )

    def execute(
        self,
        system_requirements: List[Dict[str, Any]],
        decomposition_strategy: Dict[str, Any],
        target_subsystem: str,
        enable_fallback: bool = True
    ) -> List[DetailedRequirement]:
        """
        Execute the agent's main task (decompose requirements).

        This is the main entry point for the agent, called by the workflow node.

        Args:
            system_requirements: List of system requirement dicts
            decomposition_strategy: Binding strategy from analyze node
            target_subsystem: Name of the target subsystem
            enable_fallback: Whether to enable model fallback on errors

        Returns:
            List of DetailedRequirement objects

        Raises:
            AgentError: If decomposition fails
        """
        return self.decompose_requirements(
            system_requirements,
            decomposition_strategy,
            target_subsystem,
            enable_fallback
        )

    def decompose_requirements(
        self,
        system_requirements: List[Dict[str, Any]],
        decomposition_strategy: Dict[str, Any],
        target_subsystem: str,
        enable_fallback: bool = True
    ) -> List[DetailedRequirement]:
        """
        Decompose system requirements into subsystem requirements.

        Args:
            system_requirements: List of system requirement dicts
            decomposition_strategy: Binding strategy (allocation rules, naming convention, etc.)
            target_subsystem: Name of the target subsystem
            enable_fallback: Whether to enable model fallback on errors

        Returns:
            List of DetailedRequirement objects

        Raises:
            AgentError: If decomposition fails after all retry/fallback attempts
        """
        # Validate inputs
        if not system_requirements:
            raise AgentError("Cannot decompose with empty requirements list")

        if not decomposition_strategy:
            raise AgentError("Decomposition strategy is required")

        if not target_subsystem or not target_subsystem.strip():
            raise AgentError("Target subsystem must be specified")

        # Build prompt
        prompt = self._build_decomposition_prompt(
            system_requirements,
            decomposition_strategy,
            target_subsystem
        )

        # Define the execution function
        def execute_decomposition(llm):
            """Inner function that performs the decomposition with a given LLM."""
            response = llm.invoke(prompt)
            return self._parse_decomposition_response(response.content)

        # Execute with fallback support
        try:
            detailed_requirements = self.execute_with_fallback(
                execute_decomposition,
                enable_fallback=enable_fallback
            )
            return detailed_requirements

        except Exception as e:
            raise AgentError(f"Requirements decomposition failed: {str(e)}")

    def _build_decomposition_prompt(
        self,
        system_requirements: List[Dict[str, Any]],
        decomposition_strategy: Dict[str, Any],
        target_subsystem: str
    ) -> str:
        """
        Build the prompt for requirements decomposition.

        Args:
            system_requirements: List of requirement dicts
            decomposition_strategy: Strategy dict
            target_subsystem: Target subsystem name

        Returns:
            Formatted prompt string
        """
        # Format requirements for the prompt
        req_list = []
        for req in system_requirements:
            req_str = f"- {req['id']}: {req['text']} (Type: {req.get('type', 'FUNC')})"
            if req.get('source_section'):
                req_str += f" [Source: {req['source_section']}]"
            req_list.append(req_str)

        requirements_text = "\n".join(req_list)

        # Format strategy for the prompt
        strategy_text = json.dumps(decomposition_strategy, indent=2)

        prompt = f"""You are a Requirements Engineer Agent. Your task is to decompose system-level requirements into detailed subsystem requirements following a BINDING decomposition strategy.

{self.skill_content}

---

## Your Task

**Target Subsystem**: {target_subsystem}

**System Requirements to Decompose**:
{requirements_text}

**BINDING Decomposition Strategy** (MUST be followed exactly):
```json
{strategy_text}
```

**Instructions**:
1. Apply the allocation rules to determine which requirements belong to "{target_subsystem}"
2. For each applicable requirement, decompose using the appropriate pattern (1:1, 1:N, etc.)
3. Follow the naming convention EXACTLY: {decomposition_strategy.get('naming_convention', 'SUBSYSTEM-TYPE-NNN')}
4. Maintain complete traceability (every child MUST have parent_id)
5. Include acceptance criteria if required by strategy
6. Return ONLY a valid JSON array of decomposed requirements

**CRITICAL**:
- The decomposition strategy is 100% BINDING. Violations are bugs, not quality issues.
- Do NOT create requirements that don't match allocation rules.
- Do NOT deviate from the naming convention.
- Do NOT include any markdown formatting, explanations, or additional text.
- Return ONLY the JSON array.

Output the JSON array now:"""

        return prompt

    def _parse_decomposition_response(
        self,
        response_text: str
    ) -> List[DetailedRequirement]:
        """
        Parse the LLM response into DetailedRequirement objects.

        Args:
            response_text: Raw LLM response

        Returns:
            List of DetailedRequirement objects

        Raises:
            AgentError: If parsing fails or validation fails
        """
        try:
            # Extract JSON from markdown code blocks if present
            json_text = self._extract_json_from_response(response_text)

            # Parse JSON
            data = json.loads(json_text)

            # Validate it's an array
            if not isinstance(data, list):
                raise AgentError("Expected JSON array of requirements")

            # Convert to DetailedRequirement objects
            detailed_requirements = []
            for req_dict in data:
                # Validate required fields
                required_fields = ['id', 'text', 'type', 'subsystem']
                missing_fields = [field for field in required_fields if field not in req_dict]
                if missing_fields:
                    raise AgentError(f"Requirement missing fields: {missing_fields}")

                # Map type to enum if needed
                req_type = req_dict['type']
                if isinstance(req_type, str):
                    # Handle both short forms (FUNC) and full forms (functional)
                    type_mapping = {
                        'FUNC': RequirementType.FUNCTIONAL,
                        'PERF': RequirementType.PERFORMANCE,
                        'CONS': RequirementType.CONSTRAINT,
                        'INTF': RequirementType.INTERFACE,
                        'functional': RequirementType.FUNCTIONAL,
                        'performance': RequirementType.PERFORMANCE,
                        'constraint': RequirementType.CONSTRAINT,
                        'interface': RequirementType.INTERFACE
                    }
                    req_dict['type'] = type_mapping.get(req_type, req_type)

                # Create DetailedRequirement
                detailed_req = DetailedRequirement(**req_dict)
                detailed_requirements.append(detailed_req)

            # Return empty list if no requirements allocated
            # This is valid - it means no requirements matched the allocation rules
            return detailed_requirements

        except json.JSONDecodeError as e:
            raise AgentError(f"Invalid JSON in response: {str(e)}")
        except Exception as e:
            raise AgentError(f"Failed to parse decomposition response: {str(e)}")

    def _extract_json_from_response(self, response_text: str) -> str:
        """
        Extract JSON from response, handling markdown code blocks.

        Args:
            response_text: Raw response text

        Returns:
            Cleaned JSON string

        Raises:
            AgentError: If JSON cannot be extracted
        """
        # Try to find JSON array in markdown code block
        json_block_pattern = r"```(?:json)?\s*(\[.*?\])\s*```"
        match = re.search(json_block_pattern, response_text, re.DOTALL)

        if match:
            return match.group(1)

        # Try to find raw JSON array
        json_pattern = r"\[.*\]"
        match = re.search(json_pattern, response_text, re.DOTALL)

        if match:
            return match.group(0)

        raise AgentError("No JSON array found in response")
