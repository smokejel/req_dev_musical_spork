"""
System Architect Agent for analyzing system context and creating decomposition strategy.

This agent:
1. Loads the system-analysis skill
2. Analyzes extracted requirements to understand system architecture
3. Creates a binding decomposition strategy for the Requirements Engineer
"""

import json
import re
from typing import List, Tuple, Dict, Any

from src.agents.base_agent import BaseAgent, AgentError
from src.state import (
    Requirement,
    SystemContext,
    DecompositionStrategy
)
from config.llm_config import NodeType


class SystemArchitectAgent(BaseAgent):
    """
    Agent responsible for system analysis and decomposition strategy creation.

    Uses the 'system-analysis' skill to:
    - Understand system architecture from requirements
    - Identify subsystem boundaries
    - Create binding allocation rules
    - Define naming conventions and traceability rules
    """

    def __init__(self):
        """Initialize the System Architect Agent with system-analysis skill."""
        super().__init__(
            node_type=NodeType.ANALYZE,
            skill_name="system-analysis"
        )

    def execute(
        self,
        requirements: List[Dict[str, Any]],
        target_subsystem: str,
        enable_fallback: bool = True
    ) -> Tuple[SystemContext, DecompositionStrategy]:
        """
        Execute the agent's main task (analyze system and create strategy).

        This is the main entry point for the agent, called by the workflow node.

        Args:
            requirements: List of extracted requirement dicts
            target_subsystem: Name of the target subsystem for decomposition
            enable_fallback: Whether to enable model fallback on errors

        Returns:
            Tuple of (SystemContext, DecompositionStrategy)

        Raises:
            AgentError: If analysis fails after all retry/fallback attempts
        """
        return self.analyze_system(requirements, target_subsystem, enable_fallback)

    def analyze_system(
        self,
        requirements: List[Dict[str, Any]],
        target_subsystem: str,
        enable_fallback: bool = True
    ) -> Tuple[SystemContext, DecompositionStrategy]:
        """
        Analyze system requirements and create decomposition strategy.

        Args:
            requirements: List of extracted requirement dicts
            target_subsystem: Name of the target subsystem for decomposition
            enable_fallback: Whether to enable model fallback on errors

        Returns:
            Tuple of (SystemContext, DecompositionStrategy)

        Raises:
            AgentError: If analysis fails after all retry/fallback attempts
        """
        # Validate inputs
        if not requirements:
            raise AgentError("Cannot analyze system with empty requirements list")

        if not target_subsystem or not target_subsystem.strip():
            raise AgentError("Target subsystem must be specified")

        # Build prompt
        prompt = self._build_analysis_prompt(requirements, target_subsystem)

        # Define the execution function
        def execute_analysis(llm):
            """Inner function that performs the analysis with a given LLM."""
            response = llm.invoke(prompt)
            return self._parse_analysis_response(response.content)

        # Execute with fallback support
        try:
            system_context, decomposition_strategy = self.execute_with_fallback(
                execute_analysis,
                enable_fallback=enable_fallback
            )
            return system_context, decomposition_strategy

        except Exception as e:
            raise AgentError(f"System analysis failed: {str(e)}")

    def _build_analysis_prompt(
        self,
        requirements: List[Dict[str, Any]],
        target_subsystem: str
    ) -> str:
        """
        Build the prompt for system analysis.

        Args:
            requirements: List of requirement dicts
            target_subsystem: Target subsystem name

        Returns:
            Formatted prompt string
        """
        # Format requirements for the prompt
        req_list = []
        for req in requirements:
            req_str = f"- {req['id']}: {req['text']} (Type: {req['type']})"
            if req.get('source_section'):
                req_str += f" [Source: {req['source_section']}]"
            req_list.append(req_str)

        requirements_text = "\n".join(req_list)

        # Get skill content (domain context not needed for system analysis, so pass None)
        skill_content = self.get_skill_content(None)

        prompt = f"""You are a System Architect Agent. Your task is to analyze system-level requirements and create a binding decomposition strategy for the target subsystem.

{skill_content}

---

## Your Task

**Target Subsystem**: {target_subsystem}

**Extracted System Requirements**:
{requirements_text}

**Instructions**:
1. Analyze the requirements to understand the system architecture
2. Identify what functionality belongs to the "{target_subsystem}" subsystem
3. Create a binding decomposition strategy following the SKILL.md methodology
4. Return ONLY a valid JSON object with "system_context" and "decomposition_strategy"

**Important**:
- The decomposition strategy you create is 100% binding (not advisory)
- Allocation rules must be clear and executable (no ambiguity)
- Naming convention must be specific (e.g., "NAV-{{TYPE}}-{{NNN}}")
- Do NOT include any markdown formatting, explanations, or additional text
- Return ONLY the JSON object

Output the JSON object now:"""

        return prompt

    def _parse_analysis_response(
        self,
        response_text: str
    ) -> Tuple[SystemContext, DecompositionStrategy]:
        """
        Parse the LLM response into SystemContext and DecompositionStrategy objects.

        Args:
            response_text: Raw LLM response

        Returns:
            Tuple of (SystemContext, DecompositionStrategy)

        Raises:
            AgentError: If parsing fails or validation fails
        """
        try:
            # Extract JSON from markdown code blocks if present
            json_text = self._extract_json_from_response(response_text)

            # Parse JSON
            data = json.loads(json_text)

            # Validate structure
            if "system_context" not in data:
                raise AgentError("Response missing 'system_context' field")
            if "decomposition_strategy" not in data:
                raise AgentError("Response missing 'decomposition_strategy' field")

            # Parse system context
            system_context = SystemContext(**data["system_context"])

            # Parse decomposition strategy
            decomposition_strategy = DecompositionStrategy(**data["decomposition_strategy"])

            return system_context, decomposition_strategy

        except json.JSONDecodeError as e:
            raise AgentError(f"Invalid JSON in response: {str(e)}")
        except Exception as e:
            raise AgentError(f"Failed to parse analysis response: {str(e)}")

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
        # Try to find JSON in markdown code block
        json_block_pattern = r"```(?:json)?\s*(\{.*?\})\s*```"
        match = re.search(json_block_pattern, response_text, re.DOTALL)

        if match:
            return match.group(1)

        # Try to find raw JSON object
        json_pattern = r"\{.*\}"
        match = re.search(json_pattern, response_text, re.DOTALL)

        if match:
            return match.group(0)

        raise AgentError("No JSON object found in response")
