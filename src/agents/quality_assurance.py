"""
Quality Assurance Agent for validating requirements quality.

This agent:
1. Loads the requirements-quality-validation skill
2. Assesses requirement quality across 4 dimensions
3. Generates quality metrics with specific issues
4. Creates actionable refinement feedback
"""

import json
import re
from typing import List, Dict, Any

from src.agents.base_agent import BaseAgent, AgentError
from src.state import QualityMetrics, QualityIssue, QualitySeverity
from config.llm_config import NodeType


class QualityAssuranceAgent(BaseAgent):
    """
    Agent responsible for validating requirements quality.

    Uses the 'requirements-quality-validation' skill to:
    - Score requirements across 4 dimensions (completeness, clarity, testability, traceability)
    - Identify quality issues with specific severity levels
    - Generate actionable refinement feedback
    - Apply quality gate threshold
    """

    def __init__(self):
        """Initialize the Quality Assurance Agent with quality validation skill."""
        super().__init__(
            node_type=NodeType.VALIDATE,
            skill_name="requirements-quality-validation"
        )

    def execute(
        self,
        requirements: List[Dict[str, Any]],
        automated_results: Dict[str, Any],
        strategy: Dict[str, Any],
        enable_fallback: bool = True,
        domain_context: Dict[str, Any] = None
    ) -> QualityMetrics:
        """
        Execute the agent's main task (assess quality).

        This is the main entry point for the agent, called by the workflow node.

        Args:
            requirements: List of requirement dicts to assess
            automated_results: Results from automated quality checker
            strategy: Decomposition strategy for context
            enable_fallback: Whether to enable model fallback on errors
            domain_context: Optional domain context for domain compliance scoring

        Returns:
            QualityMetrics object with scores and issues

        Raises:
            AgentError: If quality assessment fails
        """
        return self.assess_quality(
            requirements,
            automated_results,
            strategy,
            enable_fallback,
            domain_context
        )

    def assess_quality(
        self,
        requirements: List[Dict[str, Any]],
        automated_results: Dict[str, Any],
        strategy: Dict[str, Any],
        enable_fallback: bool = True,
        domain_context: Dict[str, Any] = None
    ) -> QualityMetrics:
        """
        Assess requirements quality using LLM-based evaluation.

        Args:
            requirements: List of requirement dicts to assess
            automated_results: Results from automated quality checker
            strategy: Decomposition strategy for context
            enable_fallback: Whether to enable model fallback on errors
            domain_context: Optional domain context for domain compliance scoring

        Returns:
            QualityMetrics object with scores and issues

        Raises:
            AgentError: If assessment fails after all retry/fallback attempts
        """
        # Validate inputs
        if not requirements:
            raise AgentError("Cannot assess quality of empty requirements list")

        if not automated_results:
            raise AgentError("Automated results are required for quality assessment")

        # Build prompt
        prompt = self._build_assessment_prompt(
            requirements,
            automated_results,
            strategy,
            domain_context
        )

        # Determine if domain context is present
        has_domain = domain_context and domain_context.get('domain_name') != 'generic'

        # Define the execution function
        def execute_assessment(llm):
            """Inner function that performs the assessment with a given LLM."""
            response = llm.invoke(prompt)
            return self._parse_assessment_response(response.content, has_domain_context=has_domain)

        # Execute with fallback support
        try:
            quality_metrics = self.execute_with_fallback(
                execute_assessment,
                enable_fallback=enable_fallback
            )
            return quality_metrics

        except Exception as e:
            raise AgentError(f"Quality assessment failed: {str(e)}")

    def _build_assessment_prompt(
        self,
        requirements: List[Dict[str, Any]],
        automated_results: Dict[str, Any],
        strategy: Dict[str, Any],
        domain_context: Dict[str, Any] = None
    ) -> str:
        """
        Build the prompt for quality assessment.

        Args:
            requirements: List of requirement dicts
            automated_results: Automated validation results
            strategy: Decomposition strategy
            domain_context: Optional domain context for domain compliance

        Returns:
            Formatted prompt string
        """
        # Format requirements for the prompt
        req_list = []
        for req in requirements:
            req_json = json.dumps(req, indent=2)
            req_list.append(req_json)

        requirements_text = ",\n".join(req_list)

        # Format automated results
        automated_text = json.dumps(automated_results, indent=2)

        # Format strategy
        strategy_text = json.dumps(strategy, indent=2)

        # Get skill content with domain context injected
        skill_content = self.get_skill_content(domain_context)

        # Determine dimensions based on domain context
        has_domain = domain_context and domain_context.get('domain_name') != 'generic'
        dimensions_text = "5 dimensions (completeness, clarity, testability, traceability, domain_compliance)" if has_domain else "4 dimensions (completeness, clarity, testability, traceability)"

        prompt = f"""You are a Quality Assurance Agent. Your task is to assess the quality of decomposed requirements across {dimensions_text} and provide detailed feedback.

{skill_content}

---

## Your Task

**Requirements to Assess**:
```json
[
{requirements_text}
]
```

**Automated Validation Results**:
```json
{automated_text}
```

**Decomposition Strategy (for context)**:
```json
{strategy_text}
```

**Instructions**:
1. Assess each requirement across all quality dimensions ({dimensions_text})
2. Consider the automated validation results in your assessment
3. Assign scores (0.0-1.0) for each dimension
4. Identify specific quality issues with severity (critical, major, minor)
5. Provide actionable suggestions for each issue
6. Return ONLY a valid JSON object with the QualityMetrics structure

**CRITICAL**:
- Use the automated results as a starting point but perform your own analysis
- Be specific in issue descriptions (reference requirement IDs)
- Provide actionable suggestions (tell how to fix, not just what's wrong)
{"- For domain_compliance: Check ID format, glossary term capitalization, requirement statement structure, and modal verbs as defined in domain context" if has_domain else ""}
- Do NOT include any markdown formatting, explanations, or additional text
- Return ONLY the JSON object

Output the JSON object now:"""

        return prompt

    def _parse_assessment_response(
        self,
        response_text: str,
        has_domain_context: bool = False
    ) -> QualityMetrics:
        """
        Parse the LLM response into a QualityMetrics object.

        Args:
            response_text: Raw LLM response
            has_domain_context: Whether domain context was provided (for score recalculation)

        Returns:
            QualityMetrics object

        Raises:
            AgentError: If parsing fails or validation fails
        """
        try:
            # Extract JSON from markdown code blocks if present
            json_text = self._extract_json_from_response(response_text)

            # Parse JSON
            data = json.loads(json_text)

            # Validate required fields
            required_fields = ['completeness', 'clarity', 'testability', 'traceability', 'overall_score']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                raise AgentError(f"Quality metrics missing fields: {missing_fields}")

            # Convert issues to QualityIssue objects
            issues = []
            for issue_dict in data.get('issues', []):
                # Map severity string to enum
                severity_str = issue_dict.get('severity', 'major').lower()
                severity_mapping = {
                    'critical': QualitySeverity.CRITICAL,
                    'major': QualitySeverity.MAJOR,
                    'minor': QualitySeverity.MINOR
                }
                severity = severity_mapping.get(severity_str, QualitySeverity.MAJOR)

                issue = QualityIssue(
                    severity=severity,
                    requirement_id=issue_dict.get('requirement_id'),
                    dimension=issue_dict.get('dimension', 'unknown'),
                    description=issue_dict.get('description', ''),
                    suggestion=issue_dict.get('suggestion', '')
                )
                issues.append(issue)

            # Recalculate overall_score using configured weights (Phase 7.3)
            from config.quality_config import QualityConfig
            overall_score = QualityConfig.compute_weighted_score(
                completeness=data['completeness'],
                clarity=data['clarity'],
                testability=data['testability'],
                traceability=data['traceability'],
                domain_compliance=data.get('domain_compliance')
            )

            # Create QualityMetrics object with recalculated overall_score
            quality_metrics = QualityMetrics(
                completeness=data['completeness'],
                clarity=data['clarity'],
                testability=data['testability'],
                traceability=data['traceability'],
                domain_compliance=data.get('domain_compliance'),
                overall_score=overall_score,  # Use recalculated score
                issues=issues
            )

            return quality_metrics

        except json.JSONDecodeError as e:
            raise AgentError(f"Invalid JSON in response: {str(e)}")
        except Exception as e:
            raise AgentError(f"Failed to parse quality assessment response: {str(e)}")

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
        # Try to find JSON object in markdown code block
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

    def generate_refinement_feedback(
        self,
        quality_metrics: QualityMetrics,
        requirements: List[Dict[str, Any]],
        strategy: Dict[str, Any]
    ) -> str:
        """
        Generate specific, actionable refinement feedback based on quality issues.

        This feedback is used to guide the next iteration of requirements decomposition.

        Args:
            quality_metrics: Quality assessment results
            requirements: List of requirements that were assessed
            strategy: Decomposition strategy for context

        Returns:
            Formatted refinement feedback string
        """
        feedback_lines = []

        # Header
        feedback_lines.append("## Quality Assessment - Refinement Needed\n")
        feedback_lines.append(f"Overall Score: {quality_metrics.overall_score:.2f} (threshold: 0.80)\n")

        # Dimension scores
        feedback_lines.append("### Dimension Scores:")
        feedback_lines.append(f"- Completeness: {quality_metrics.completeness:.2f} {'✓' if quality_metrics.completeness >= 0.80 else '⚠️'}")
        feedback_lines.append(f"- Clarity: {quality_metrics.clarity:.2f} {'✓' if quality_metrics.clarity >= 0.80 else '⚠️'}")
        feedback_lines.append(f"- Testability: {quality_metrics.testability:.2f} {'✓' if quality_metrics.testability >= 0.80 else '⚠️'}")
        feedback_lines.append(f"- Traceability: {quality_metrics.traceability:.2f} {'✓' if quality_metrics.traceability >= 0.80 else '⚠️'}\n")

        # Group issues by severity
        critical_issues = [issue for issue in quality_metrics.issues if issue.severity == QualitySeverity.CRITICAL]
        major_issues = [issue for issue in quality_metrics.issues if issue.severity == QualitySeverity.MAJOR]
        minor_issues = [issue for issue in quality_metrics.issues if issue.severity == QualitySeverity.MINOR]

        # Critical issues
        if critical_issues:
            feedback_lines.append("### CRITICAL Issues to Fix (Blocks Quality Gate):")
            for idx, issue in enumerate(critical_issues, 1):
                req_id = issue.requirement_id or "GENERAL"
                feedback_lines.append(f"{idx}. [{req_id}] {issue.description}")
                feedback_lines.append(f"   → Fix: {issue.suggestion}\n")

        # Major issues
        if major_issues:
            feedback_lines.append("### MAJOR Issues to Address:")
            for idx, issue in enumerate(major_issues, 1):
                req_id = issue.requirement_id or "GENERAL"
                feedback_lines.append(f"{idx}. [{req_id}] {issue.description}")
                feedback_lines.append(f"   → Suggestion: {issue.suggestion}\n")

        # Minor issues (limit to top 3)
        if minor_issues:
            feedback_lines.append("### MINOR Improvements (Nice to Have):")
            for idx, issue in enumerate(minor_issues[:3], 1):
                req_id = issue.requirement_id or "GENERAL"
                feedback_lines.append(f"{idx}. [{req_id}] {issue.description}")
                feedback_lines.append(f"   → Suggestion: {issue.suggestion}\n")

            if len(minor_issues) > 3:
                feedback_lines.append(f"   ... and {len(minor_issues) - 3} more minor issues\n")

        # Actionable recommendations
        feedback_lines.append("### Actionable Recommendations:")

        if quality_metrics.completeness < 0.80:
            feedback_lines.append("- Review parent requirements to ensure complete functional coverage")
            feedback_lines.append("- Check for missing CRUD operations or sub-features")

        if quality_metrics.clarity < 0.80:
            feedback_lines.append("- Replace vague terms with specific, measurable constraints")
            feedback_lines.append("- Use precise language: specify units, thresholds, and conditions")

        if quality_metrics.testability < 0.80:
            feedback_lines.append("- Add clear, measurable acceptance criteria to all requirements")
            feedback_lines.append("- Specify pass/fail conditions and test scenarios")

        if quality_metrics.traceability < 0.80:
            feedback_lines.append("- Ensure all requirements have valid parent_id")
            feedback_lines.append("- Add rationale explaining the decomposition decision")
            feedback_lines.append("- Follow naming convention exactly as specified in strategy")

        return "\n".join(feedback_lines)
