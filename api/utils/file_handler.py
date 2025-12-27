"""
File upload handling utilities.

Manages file uploads, validation, and storage.
"""

import shutil
import uuid
from pathlib import Path
from typing import Optional, List

from fastapi import UploadFile, HTTPException, status

from api.config import APIConfig


class FileHandler:
    """Handles file upload operations."""

    @staticmethod
    def validate_file(file: UploadFile) -> None:
        """
        Validate uploaded file.

        Args:
            file: Uploaded file

        Raises:
            HTTPException: If file is invalid
        """
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )

        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in APIConfig.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file_ext} not allowed. Allowed types: {', '.join(APIConfig.ALLOWED_EXTENSIONS)}"
            )

    @staticmethod
    async def save_file(
        file: UploadFile,
        workflow_id: str,
        prefix: str = "spec"
    ) -> Path:
        """
        Save uploaded file to disk.

        Args:
            file: Uploaded file
            workflow_id: Workflow UUID
            prefix: Filename prefix (default: 'spec')

        Returns:
            Path to saved file

        Raises:
            HTTPException: If save fails
        """
        try:
            # Create workflow directory
            workflow_dir = APIConfig.UPLOAD_DIR / workflow_id
            workflow_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename
            file_ext = Path(file.filename).suffix
            file_path = workflow_dir / f"{prefix}{file_ext}"

            # Save file
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            return file_path

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file: {str(e)}"
            )

    @staticmethod
    async def save_multiple_files(
        files: List[UploadFile],
        workflow_id: str,
        prefix: str = "context"
    ) -> List[Path]:
        """
        Save multiple uploaded files.

        Args:
            files: List of uploaded files
            workflow_id: Workflow UUID
            prefix: Filename prefix

        Returns:
            List of paths to saved files
        """
        saved_paths = []
        for i, file in enumerate(files):
            file_ext = Path(file.filename).suffix
            numbered_prefix = f"{prefix}_{i+1}"
            path = await FileHandler.save_file(file, workflow_id, numbered_prefix)
            saved_paths.append(path)

        return saved_paths

    @staticmethod
    def generate_workflow_id() -> str:
        """Generate unique workflow ID."""
        return str(uuid.uuid4())

    @staticmethod
    def get_workflow_dir(workflow_id: str) -> Path:
        """Get workflow upload directory."""
        return APIConfig.UPLOAD_DIR / workflow_id

    @staticmethod
    def get_spec_file(workflow_id: str) -> Optional[Path]:
        """
        Get specification file path for a workflow.

        Args:
            workflow_id: Workflow UUID

        Returns:
            Path to spec file, or None if not found
        """
        workflow_dir = FileHandler.get_workflow_dir(workflow_id)
        if not workflow_dir.exists():
            return None

        # Look for spec file with any allowed extension
        for ext in APIConfig.ALLOWED_EXTENSIONS:
            spec_file = workflow_dir / f"spec{ext}"
            if spec_file.exists():
                return spec_file

        return None
