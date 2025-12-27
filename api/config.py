"""
API Configuration.

Loads configuration from environment variables for the FastAPI application.
"""

import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv

load_dotenv()


class APIConfig:
    """API configuration settings."""

    # API Server
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_KEY: str = os.getenv("API_KEY", "dev-key-12345")  # Change in production!

    # CORS
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS", "http://localhost:3000,http://localhost:3001"
    ).split(",")

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "sqlite:///checkpoints/workflow_runs.db"
    )

    # File Upload
    UPLOAD_DIR: Path = Path(os.getenv("UPLOAD_DIR", "uploads"))
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "20"))
    MAX_UPLOAD_SIZE_BYTES: int = MAX_UPLOAD_SIZE_MB * 1024 * 1024

    # Allowed file types
    ALLOWED_EXTENSIONS: set = {".txt", ".docx", ".pdf"}

    @classmethod
    def ensure_directories(cls):
        """Ensure required directories exist."""
        cls.UPLOAD_DIR.mkdir(exist_ok=True, parents=True)
        Path("checkpoints").mkdir(exist_ok=True, parents=True)


# Ensure directories on module import
APIConfig.ensure_directories()
