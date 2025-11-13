"""
LangSmith integration for precise token tracking and cost calculation.

Extracts token usage from LangSmith traces and provides accurate cost metrics.
"""

from typing import Dict, Optional, List, Tuple
from datetime import datetime
import time

from config.observability_config import ObservabilityConfig, LANGSMITH_ACTIVE

# LangSmith client is optional
try:
    from langsmith import Client
    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False
    Client = None


class LangSmithTracker:
    """
    Tracks LLM usage via LangSmith tracing.

    Provides precise token counts and cost calculations from actual LLM calls.
    """

    def __init__(self):
        """Initialize LangSmith tracker."""
        self.client: Optional[Client] = None
        self.active = False

        if LANGSMITH_ACTIVE and LANGSMITH_AVAILABLE:
            try:
                self.client = Client()
                self.active = True
            except Exception as e:
                print(f"Warning: Failed to initialize LangSmith client: {e}")
                self.active = False

    def is_active(self) -> bool:
        """Check if LangSmith tracking is active."""
        return self.active

    def get_run_costs(
        self,
        run_id: str,
        max_wait_seconds: int = 10
    ) -> Optional[Dict[str, any]]:
        """
        Get cost information for a LangSmith run.

        Args:
            run_id: LangSmith run ID
            max_wait_seconds: Maximum time to wait for run completion

        Returns:
            Dictionary with cost and token information, or None if unavailable
        """
        if not self.active:
            return None

        try:
            # Wait for run to complete
            start_time = time.time()
            run = None

            while time.time() - start_time < max_wait_seconds:
                try:
                    run = self.client.read_run(run_id)
                    if run.end_time is not None:
                        break
                except Exception:
                    pass
                time.sleep(0.5)

            if run is None or run.end_time is None:
                return None

            # Extract token usage
            if hasattr(run, 'outputs') and run.outputs:
                token_usage = run.outputs.get('token_usage', {})
            else:
                token_usage = {}

            # Get usage metadata
            prompt_tokens = token_usage.get('prompt_tokens', 0)
            completion_tokens = token_usage.get('completion_tokens', 0)
            total_tokens = token_usage.get('total_tokens', prompt_tokens + completion_tokens)

            return {
                'run_id': str(run_id),
                'input_tokens': prompt_tokens,
                'output_tokens': completion_tokens,
                'total_tokens': total_tokens,
                'model': self._extract_model_name(run),
                'start_time': run.start_time,
                'end_time': run.end_time,
                'duration_seconds': (run.end_time - run.start_time).total_seconds() if run.end_time and run.start_time else None
            }

        except Exception as e:
            print(f"Warning: Failed to get run costs from LangSmith: {e}")
            return None

    def get_project_runs(
        self,
        project_name: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, any]]:
        """
        Get recent runs from a LangSmith project.

        Args:
            project_name: Project name (default: from config)
            limit: Maximum number of runs to return

        Returns:
            List of run information dictionaries
        """
        if not self.active:
            return []

        try:
            if project_name is None:
                project_name = ObservabilityConfig.LANGSMITH_PROJECT

            runs = self.client.list_runs(
                project_name=project_name,
                limit=limit
            )

            return [
                {
                    'run_id': str(run.id),
                    'name': run.name,
                    'start_time': run.start_time,
                    'end_time': run.end_time,
                    'status': run.status if hasattr(run, 'status') else 'unknown'
                }
                for run in runs
            ]

        except Exception as e:
            print(f"Warning: Failed to list runs from LangSmith: {e}")
            return []

    def _extract_model_name(self, run) -> str:
        """Extract model name from LangSmith run."""
        try:
            if hasattr(run, 'extra') and run.extra:
                metadata = run.extra.get('metadata', {})
                if 'model_name' in metadata:
                    return metadata['model_name']
                if 'ls_model_name' in metadata:
                    return metadata['ls_model_name']

            # Try to get from invocation params
            if hasattr(run, 'serialized') and run.serialized:
                kwargs = run.serialized.get('kwargs', {})
                if 'model' in kwargs:
                    return kwargs['model']
                if 'model_name' in kwargs:
                    return kwargs['model_name']

            return 'unknown'

        except Exception:
            return 'unknown'

    def get_workflow_costs(
        self,
        workflow_run_id: str,
        max_wait_seconds: int = 15,
        project_name: Optional[str] = None
    ) -> Optional[Dict[str, any]]:
        """
        Get aggregated costs for a complete workflow run by querying all child runs.

        This method waits for the workflow run to complete, then fetches all
        child LLM calls and aggregates their token usage.

        Args:
            workflow_run_id: LangSmith run ID for the workflow execution
            max_wait_seconds: Maximum time to wait for traces to be available
            project_name: Project name (default: from config)

        Returns:
            Dictionary with aggregated token counts and costs per node, or None if unavailable
        """
        if not self.active:
            return None

        try:
            if project_name is None:
                project_name = ObservabilityConfig.LANGSMITH_PROJECT

            # Wait for traces to be fully processed
            time.sleep(2)  # Initial delay for trace processing

            start_time = time.time()
            workflow_run = None

            # Wait for workflow run to complete
            while time.time() - start_time < max_wait_seconds:
                try:
                    workflow_run = self.client.read_run(workflow_run_id)
                    if workflow_run.end_time is not None:
                        break
                except Exception:
                    pass
                time.sleep(1)

            if workflow_run is None:
                return None

            # Fetch all child runs (LLM calls within the workflow)
            child_runs = list(self.client.list_runs(
                project_name=project_name,
                trace_id=workflow_run.trace_id
            ))

            # Aggregate tokens by node
            node_costs = {}
            total_input_tokens = 0
            total_output_tokens = 0

            for run in child_runs:
                # Only process LLM runs
                run_type = run.run_type if hasattr(run, 'run_type') else 'unknown'
                if run_type != 'llm':
                    continue

                # LangSmith stores token data in the 'prompt_tokens' and 'completion_tokens' fields
                # These are top-level attributes on the run object for LLM runs
                input_tokens = 0
                output_tokens = 0

                # Check top-level fields (this is where LangSmith stores LLM token data)
                if hasattr(run, 'prompt_tokens') and run.prompt_tokens:
                    input_tokens = run.prompt_tokens

                if hasattr(run, 'completion_tokens') and run.completion_tokens:
                    output_tokens = run.completion_tokens

                # Fallback: Try total_tokens if available
                if input_tokens == 0 and output_tokens == 0:
                    if hasattr(run, 'total_tokens') and run.total_tokens:
                        # Estimate split (typically ~75% input, 25% output)
                        total = run.total_tokens
                        input_tokens = int(total * 0.75)
                        output_tokens = int(total * 0.25)

                if input_tokens > 0 or output_tokens > 0:
                    # Extract node name from parent run or run name
                    node_name = self._extract_node_name(run)

                    if node_name not in node_costs:
                        node_costs[node_name] = {'input_tokens': 0, 'output_tokens': 0}

                    node_costs[node_name]['input_tokens'] += input_tokens
                    node_costs[node_name]['output_tokens'] += output_tokens

                    total_input_tokens += input_tokens
                    total_output_tokens += output_tokens

            return {
                'workflow_run_id': str(workflow_run_id),
                'total_input_tokens': total_input_tokens,
                'total_output_tokens': total_output_tokens,
                'total_tokens': total_input_tokens + total_output_tokens,
                'node_costs': node_costs,
                'child_runs_count': len([r for r in child_runs if hasattr(r, 'outputs') and r.outputs])
            }

        except Exception as e:
            print(f"Warning: Failed to get workflow costs from LangSmith: {e}")
            return None

    def _extract_node_name(self, run) -> str:
        """Extract node name from LangSmith run."""
        try:
            # For LLM runs, we need to look at the parent run (the node that called the LLM)
            # LangSmith API provides parent_run_id
            if hasattr(run, 'parent_run_id') and run.parent_run_id:
                try:
                    parent_run = self.client.read_run(str(run.parent_run_id))
                    if hasattr(parent_run, 'name'):
                        parent_name = parent_run.name.lower()
                        # Check if parent name matches a node
                        for node in ['extract', 'analyze', 'decompose', 'validate']:
                            if node in parent_name:
                                return node
                except Exception:
                    pass  # Failed to fetch parent, try fallbacks

            # Fallback: Try from run name
            if hasattr(run, 'name'):
                name = run.name.lower()
                for node in ['extract', 'analyze', 'decompose', 'validate']:
                    if node in name:
                        return node

            # Try from tags
            if hasattr(run, 'tags') and run.tags:
                for tag in run.tags:
                    tag_lower = tag.lower()
                    for node in ['extract', 'analyze', 'decompose', 'validate']:
                        if node in tag_lower:
                            return node

            return 'unknown'

        except Exception:
            return 'unknown'

    def get_aggregate_costs(
        self,
        project_name: Optional[str] = None,
        since_date: Optional[datetime] = None
    ) -> Dict[str, any]:
        """
        Get aggregated cost statistics for a project.

        Args:
            project_name: Project name (default: from config)
            since_date: Only include runs after this date

        Returns:
            Dictionary with aggregated statistics
        """
        if not self.active:
            return {
                'total_runs': 0,
                'total_tokens': 0,
                'total_input_tokens': 0,
                'total_output_tokens': 0
            }

        try:
            if project_name is None:
                project_name = ObservabilityConfig.LANGSMITH_PROJECT

            # Get runs
            runs = self.client.list_runs(
                project_name=project_name,
                start_time=since_date
            )

            total_input = 0
            total_output = 0
            run_count = 0

            for run in runs:
                if run.end_time is None:
                    continue  # Skip incomplete runs

                run_costs = self.get_run_costs(str(run.id), max_wait_seconds=1)
                if run_costs:
                    total_input += run_costs['input_tokens']
                    total_output += run_costs['output_tokens']
                    run_count += 1

            return {
                'total_runs': run_count,
                'total_tokens': total_input + total_output,
                'total_input_tokens': total_input,
                'total_output_tokens': total_output
            }

        except Exception as e:
            print(f"Warning: Failed to get aggregate costs: {e}")
            return {
                'total_runs': 0,
                'total_tokens': 0,
                'total_input_tokens': 0,
                'total_output_tokens': 0
            }


# Global LangSmith tracker instance
_langsmith_tracker: Optional[LangSmithTracker] = None


def get_langsmith_tracker() -> LangSmithTracker:
    """Get global LangSmith tracker instance."""
    global _langsmith_tracker
    if _langsmith_tracker is None:
        _langsmith_tracker = LangSmithTracker()
    return _langsmith_tracker


def extract_tokens_from_response(response) -> Tuple[int, int]:
    """
    Extract token counts from LLM response.

    Args:
        response: LLM response object

    Returns:
        Tuple of (input_tokens, output_tokens)
    """
    try:
        # Try to extract from response metadata
        if hasattr(response, 'response_metadata'):
            metadata = response.response_metadata

            # OpenAI format
            if 'token_usage' in metadata:
                usage = metadata['token_usage']
                return (
                    usage.get('prompt_tokens', 0),
                    usage.get('completion_tokens', 0)
                )

            # Anthropic format
            if 'usage' in metadata:
                usage = metadata['usage']
                return (
                    usage.get('input_tokens', 0),
                    usage.get('output_tokens', 0)
                )

            # Google/Gemini format
            if 'usage_metadata' in metadata:
                usage = metadata['usage_metadata']
                return (
                    usage.get('prompt_token_count', 0),
                    usage.get('candidates_token_count', 0)
                )

        # Fallback: try direct attributes
        if hasattr(response, 'usage_metadata'):
            usage = response.usage_metadata
            return (
                getattr(usage, 'prompt_token_count', 0),
                getattr(usage, 'candidates_token_count', 0)
            )

    except Exception:
        pass

    # Unable to extract tokens
    return (0, 0)
