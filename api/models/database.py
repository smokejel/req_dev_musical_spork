"""
Database models for workflow run tracking.

Uses SQLAlchemy ORM to track workflow metadata, status, and results.
"""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    Enum,
    JSON,
    Index,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from api.config import APIConfig

Base = declarative_base()


class WorkflowStatus(str, enum.Enum):
    """Workflow execution status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"  # For human review


class WorkflowRun(Base):
    """
    Workflow run metadata and results.

    Tracks the lifecycle of a requirements decomposition workflow,
    linking to the LangGraph checkpoint for detailed state.
    """

    __tablename__ = "workflow_runs"

    # Primary key
    id = Column(String(36), primary_key=True)  # UUID

    # Metadata
    project_name = Column(String(255), nullable=False)
    source_document = Column(String(500), nullable=False)  # Filename
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.PENDING, nullable=False)

    # Configuration (stored as JSON)
    config = Column(JSON, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Progress tracking
    current_node = Column(String(50), nullable=True)
    progress = Column(Float, default=0.0)  # 0.0 to 1.0
    elapsed_time = Column(Float, default=0.0)  # Seconds
    token_count = Column(Integer, default=0)

    # Results summary
    extracted_count = Column(Integer, nullable=True)
    generated_count = Column(Integer, nullable=True)
    quality_score = Column(Float, nullable=True)

    # Observability
    total_cost = Column(Float, nullable=True)
    energy_wh = Column(Float, nullable=True)

    # Link to LangGraph checkpoint
    checkpoint_id = Column(String(100), nullable=False, unique=True)

    # Indexes for common queries
    __table_args__ = (
        Index("idx_status", "status"),
        Index("idx_created_at", "created_at"),
        Index("idx_checkpoint_id", "checkpoint_id"),
    )

    def __repr__(self):
        return f"<WorkflowRun(id={self.id}, status={self.status}, project={self.project_name})>"


# Database engine and session
engine = create_engine(
    APIConfig.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in APIConfig.DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """
    Dependency for getting database session.

    Usage in FastAPI:
        @app.get("/...")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
