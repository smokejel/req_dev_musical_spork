"""
Quality metrics tracking and trend analysis.

Tracks quality scores across workflow runs for trend analysis and improvement.
"""

import os
import sqlite3
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
from dataclasses import dataclass, asdict

from src.state import QualityMetrics


@dataclass
class QualityRecord:
    """Record of quality metrics for a single workflow run."""
    run_id: str
    timestamp: datetime
    subsystem: str
    overall_score: float
    completeness: float
    clarity: float
    testability: float
    traceability: float
    validation_passed: bool
    iteration_count: int
    requirements_count: int


class QualityTracker:
    """
    Tracks quality metrics across workflow runs.

    Stores quality history in SQLite for trend analysis and reporting.
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize quality tracker.

        Args:
            db_path: Path to SQLite database (default: data/quality_history.db)
                    Falls back to checkpoints/quality.db for backward compatibility
        """
        if db_path is None:
            # Try environment variable first (useful for Docker)
            db_path_str = os.getenv('QUALITY_TRACKER_DB', 'data/quality_history.db')
            db_path = Path(db_path_str)

        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_db()

    def _init_db(self) -> None:
        """Initialize SQLite database for quality tracking."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quality_runs (
                    run_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    subsystem TEXT NOT NULL,
                    overall_score REAL NOT NULL,
                    completeness REAL NOT NULL,
                    clarity REAL NOT NULL,
                    testability REAL NOT NULL,
                    traceability REAL NOT NULL,
                    validation_passed INTEGER NOT NULL,
                    iteration_count INTEGER NOT NULL,
                    requirements_count INTEGER NOT NULL
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_quality_timestamp
                ON quality_runs(timestamp)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_quality_subsystem
                ON quality_runs(subsystem)
            """)

            conn.commit()

    def record_quality(
        self,
        run_id: str,
        subsystem: str,
        quality_metrics: QualityMetrics,
        validation_passed: bool,
        iteration_count: int,
        requirements_count: int
    ) -> QualityRecord:
        """
        Record quality metrics for a workflow run.

        Args:
            run_id: Unique identifier for this run
            subsystem: Target subsystem
            quality_metrics: Quality metrics object
            validation_passed: Whether validation passed quality gate
            iteration_count: Number of refinement iterations
            requirements_count: Number of decomposed requirements

        Returns:
            QualityRecord with complete information
        """
        record = QualityRecord(
            run_id=run_id,
            timestamp=datetime.now(),
            subsystem=subsystem,
            overall_score=quality_metrics.overall_score,
            completeness=quality_metrics.completeness,
            clarity=quality_metrics.clarity,
            testability=quality_metrics.testability,
            traceability=quality_metrics.traceability,
            validation_passed=validation_passed,
            iteration_count=iteration_count,
            requirements_count=requirements_count
        )

        # Store in database
        self._store_record(record)

        return record

    def _store_record(self, record: QualityRecord) -> None:
        """Store quality record in database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO quality_runs
                (run_id, timestamp, subsystem, overall_score, completeness,
                 clarity, testability, traceability, validation_passed,
                 iteration_count, requirements_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.run_id,
                    record.timestamp.isoformat(),
                    record.subsystem,
                    record.overall_score,
                    record.completeness,
                    record.clarity,
                    record.testability,
                    record.traceability,
                    1 if record.validation_passed else 0,
                    record.iteration_count,
                    record.requirements_count
                )
            )
            conn.commit()

    def get_recent_runs(self, limit: int = 10) -> List[QualityRecord]:
        """
        Get recent quality records.

        Args:
            limit: Maximum number of records to return

        Returns:
            List of QualityRecord objects, most recent first
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT run_id, timestamp, subsystem, overall_score, completeness,
                       clarity, testability, traceability, validation_passed,
                       iteration_count, requirements_count
                FROM quality_runs
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (limit,)
            )

            records = []
            for row in cursor.fetchall():
                records.append(QualityRecord(
                    run_id=row[0],
                    timestamp=datetime.fromisoformat(row[1]),
                    subsystem=row[2],
                    overall_score=row[3],
                    completeness=row[4],
                    clarity=row[5],
                    testability=row[6],
                    traceability=row[7],
                    validation_passed=bool(row[8]),
                    iteration_count=row[9],
                    requirements_count=row[10]
                ))

            return records

    def get_quality_trends(self, days: int = 30, subsystem: Optional[str] = None) -> Dict[str, any]:
        """
        Get quality trend statistics.

        Args:
            days: Number of days to analyze
            subsystem: Optional filter by subsystem

        Returns:
            Dictionary with trend statistics
        """
        with sqlite3.connect(self.db_path) as conn:
            # Build query with optional subsystem filter
            query = """
                SELECT overall_score, completeness, clarity, testability,
                       traceability, validation_passed, iteration_count
                FROM quality_runs
                WHERE datetime(timestamp) >= datetime('now', ? || ' days')
            """
            params = [-days]

            if subsystem:
                query += " AND subsystem = ?"
                params.append(subsystem)

            query += " ORDER BY timestamp"

            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

            if not rows:
                return {
                    'total_runs': 0,
                    'avg_overall_score': 0.0,
                    'avg_completeness': 0.0,
                    'avg_clarity': 0.0,
                    'avg_testability': 0.0,
                    'avg_traceability': 0.0,
                    'pass_rate': 0.0,
                    'avg_iterations': 0.0
                }

            overall_scores = [row[0] for row in rows]
            completeness_scores = [row[1] for row in rows]
            clarity_scores = [row[2] for row in rows]
            testability_scores = [row[3] for row in rows]
            traceability_scores = [row[4] for row in rows]
            passed = [row[5] for row in rows]
            iterations = [row[6] for row in rows]

            return {
                'total_runs': len(rows),
                'avg_overall_score': sum(overall_scores) / len(overall_scores),
                'avg_completeness': sum(completeness_scores) / len(completeness_scores),
                'avg_clarity': sum(clarity_scores) / len(clarity_scores),
                'avg_testability': sum(testability_scores) / len(testability_scores),
                'avg_traceability': sum(traceability_scores) / len(traceability_scores),
                'pass_rate': sum(passed) / len(passed) * 100,
                'avg_iterations': sum(iterations) / len(iterations),
                'min_score': min(overall_scores),
                'max_score': max(overall_scores)
            }

    def get_subsystem_comparison(self) -> Dict[str, Dict[str, float]]:
        """
        Compare quality metrics across different subsystems.

        Returns:
            Dictionary mapping subsystem names to their average metrics
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT subsystem,
                       AVG(overall_score) as avg_score,
                       AVG(iteration_count) as avg_iterations,
                       COUNT(*) as run_count
                FROM quality_runs
                GROUP BY subsystem
                ORDER BY avg_score DESC
            """)

            results = {}
            for row in cursor.fetchall():
                subsystem, avg_score, avg_iterations, run_count = row
                results[subsystem] = {
                    'avg_score': avg_score,
                    'avg_iterations': avg_iterations,
                    'run_count': run_count
                }

            return results


# Global quality tracker instance
_quality_tracker: Optional[QualityTracker] = None


def get_quality_tracker() -> QualityTracker:
    """Get global quality tracker instance."""
    global _quality_tracker
    if _quality_tracker is None:
        _quality_tracker = QualityTracker()
    return _quality_tracker
