"""
Health check endpoint.

Simple endpoint to verify API is running.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns:
        Status and version information
    """
    return {
        "status": "healthy",
        "service": "ReqDecompose API",
        "version": "1.0.0",
    }
