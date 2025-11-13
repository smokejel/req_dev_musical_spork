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
