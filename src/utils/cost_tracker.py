"""
Cost tracking and budget management for LLM operations.

Provides precise cost calculation using LangSmith token counts when available,
or falls back to heuristic estimates.
"""

import os
import sqlite3
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict

from config.llm_config import ModelConfig, get_primary_model, NodeType
from config.observability_config import ObservabilityConfig, LANGSMITH_ACTIVE


@dataclass
class CostRecord:
    """Record of costs for a single workflow run."""
    run_id: str
    timestamp: datetime
    total_cost: float
    node_costs: Dict[str, float]
    token_counts: Dict[str, Dict[str, int]]
    subsystem: str
    source_method: str  # 'langsmith' or 'heuristic'


class CostTracker:
    """
    Tracks LLM costs across workflow runs.

    Stores cost history in SQLite for trend analysis and reporting.
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize cost tracker.

        Args:
            db_path: Path to SQLite database (default: data/cost_history.db)
                    Falls back to checkpoints/costs.db for backward compatibility
        """
        if db_path is None:
            # Try environment variable first (useful for Docker)
            db_path_str = os.getenv('COST_TRACKER_DB', 'data/cost_history.db')
            db_path = Path(db_path_str)

        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_db()

        # Current run tracking
        self.current_run_id: Optional[str] = None
        self.current_costs: Dict[str, float] = {}
        self.current_tokens: Dict[str, Dict[str, int]] = {}

    def _init_db(self) -> None:
        """Initialize SQLite database for cost tracking."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cost_runs (
                    run_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    total_cost REAL NOT NULL,
                    subsystem TEXT NOT NULL,
                    source_method TEXT NOT NULL
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS node_costs (
                    run_id TEXT NOT NULL,
                    node_name TEXT NOT NULL,
                    cost REAL NOT NULL,
                    input_tokens INTEGER,
                    output_tokens INTEGER,
                    model_name TEXT,
                    FOREIGN KEY (run_id) REFERENCES cost_runs(run_id)
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp
                ON cost_runs(timestamp)
            """)

            conn.commit()

    def start_run(self, run_id: str) -> None:
        """
        Start tracking a new workflow run.

        Args:
            run_id: Unique identifier for this run
        """
        self.current_run_id = run_id
        self.current_costs = {}
        self.current_tokens = {}

    def record_node_cost(
        self,
        node_name: str,
        cost: float,
        input_tokens: int,
        output_tokens: int,
        model_name: str
    ) -> None:
        """
        Record cost for a single node execution.

        Args:
            node_name: Name of the workflow node
            cost: Cost in dollars
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model_name: Model identifier
        """
        if self.current_run_id is None:
            raise ValueError("No active run. Call start_run() first.")

        self.current_costs[node_name] = cost
        self.current_tokens[node_name] = {
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'model': model_name
        }

    def calculate_node_cost(
        self,
        node_type: NodeType,
        input_tokens: int,
        output_tokens: int,
        model_config: Optional[ModelConfig] = None
    ) -> float:
        """
        Calculate cost for a node execution.

        Args:
            node_type: Type of workflow node
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model_config: Model configuration (if None, uses primary model for node)

        Returns:
            Cost in dollars
        """
        if model_config is None:
            model_config = get_primary_model(node_type)

        input_cost = (input_tokens / 1000) * model_config.cost_per_1k_input
        output_cost = (output_tokens / 1000) * model_config.cost_per_1k_output

        return input_cost + output_cost

    def get_current_total(self) -> float:
        """Get total cost for current run."""
        return sum(self.current_costs.values())

    def check_budget(self) -> Tuple[bool, Optional[str]]:
        """
        Check if current costs exceed budget thresholds.

        Returns:
            Tuple of (is_ok, warning_message)
            - is_ok: False if max budget exceeded
            - warning_message: Warning message if threshold exceeded
        """
        if not ObservabilityConfig.COST_TRACKING_ENABLED:
            return True, None

        current_total = self.get_current_total()

        # Check max budget
        if current_total >= ObservabilityConfig.COST_BUDGET_MAX:
            return False, (
                f"⚠️  BUDGET EXCEEDED: ${current_total:.4f} >= "
                f"${ObservabilityConfig.COST_BUDGET_MAX:.2f} (stopping execution)"
            )

        # Check warning threshold
        if current_total >= ObservabilityConfig.COST_BUDGET_WARNING_THRESHOLD:
            return True, (
                f"⚠️  Cost Warning: ${current_total:.4f} "
                f"(threshold: ${ObservabilityConfig.COST_BUDGET_WARNING_THRESHOLD:.2f})"
            )

        return True, None

    def finalize_run(self, subsystem: str, source_method: str = 'heuristic') -> CostRecord:
        """
        Finalize current run and store in database.

        Args:
            subsystem: Target subsystem for this run
            source_method: 'langsmith' or 'heuristic'

        Returns:
            CostRecord with complete run information
        """
        if self.current_run_id is None:
            raise ValueError("No active run to finalize.")

        record = CostRecord(
            run_id=self.current_run_id,
            timestamp=datetime.now(),
            total_cost=self.get_current_total(),
            node_costs=self.current_costs.copy(),
            token_counts=self.current_tokens.copy(),
            subsystem=subsystem,
            source_method=source_method
        )

        # Store in database
        self._store_record(record)

        # Reset current run
        self.current_run_id = None
        self.current_costs = {}
        self.current_tokens = {}

        return record

    def _store_record(self, record: CostRecord) -> None:
        """Store cost record in database."""
        with sqlite3.connect(self.db_path) as conn:
            # Insert run record
            conn.execute(
                """
                INSERT INTO cost_runs (run_id, timestamp, total_cost, subsystem, source_method)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    record.run_id,
                    record.timestamp.isoformat(),
                    record.total_cost,
                    record.subsystem,
                    record.source_method
                )
            )

            # Insert node cost records
            for node_name, cost in record.node_costs.items():
                tokens = record.token_counts.get(node_name, {})
                conn.execute(
                    """
                    INSERT INTO node_costs
                    (run_id, node_name, cost, input_tokens, output_tokens, model_name)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.run_id,
                        node_name,
                        cost,
                        tokens.get('input_tokens', 0),
                        tokens.get('output_tokens', 0),
                        tokens.get('model', 'unknown')
                    )
                )

            conn.commit()

    def get_recent_runs(self, limit: int = 10) -> List[CostRecord]:
        """
        Get recent cost records.

        Args:
            limit: Maximum number of records to return

        Returns:
            List of CostRecord objects, most recent first
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT run_id, timestamp, total_cost, subsystem, source_method
                FROM cost_runs
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (limit,)
            )

            records = []
            for row in cursor.fetchall():
                run_id, timestamp_str, total_cost, subsystem, source_method = row

                # Get node costs for this run
                node_cursor = conn.execute(
                    """
                    SELECT node_name, cost, input_tokens, output_tokens, model_name
                    FROM node_costs
                    WHERE run_id = ?
                    """,
                    (run_id,)
                )

                node_costs = {}
                token_counts = {}
                for node_row in node_cursor.fetchall():
                    node_name, cost, input_tok, output_tok, model = node_row
                    node_costs[node_name] = cost
                    token_counts[node_name] = {
                        'input_tokens': input_tok,
                        'output_tokens': output_tok,
                        'model': model
                    }

                records.append(CostRecord(
                    run_id=run_id,
                    timestamp=datetime.fromisoformat(timestamp_str),
                    total_cost=total_cost,
                    node_costs=node_costs,
                    token_counts=token_counts,
                    subsystem=subsystem,
                    source_method=source_method
                ))

            return records

    def get_cost_trends(self, days: int = 30) -> Dict[str, any]:
        """
        Get cost trend statistics.

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with trend statistics
        """
        with sqlite3.connect(self.db_path) as conn:
            # Get runs from last N days
            cursor = conn.execute(
                """
                SELECT total_cost, timestamp, subsystem
                FROM cost_runs
                WHERE datetime(timestamp) >= datetime('now', ? || ' days')
                ORDER BY timestamp
                """,
                (-days,)
            )

            rows = cursor.fetchall()
            if not rows:
                return {
                    'total_runs': 0,
                    'total_cost': 0.0,
                    'avg_cost': 0.0,
                    'min_cost': 0.0,
                    'max_cost': 0.0
                }

            costs = [row[0] for row in rows]

            return {
                'total_runs': len(costs),
                'total_cost': sum(costs),
                'avg_cost': sum(costs) / len(costs),
                'min_cost': min(costs),
                'max_cost': max(costs),
                'subsystems': list(set(row[2] for row in rows))
            }


# Global cost tracker instance
_cost_tracker: Optional[CostTracker] = None


def get_cost_tracker() -> CostTracker:
    """Get global cost tracker instance."""
    global _cost_tracker
    if _cost_tracker is None:
        _cost_tracker = CostTracker()
    return _cost_tracker
