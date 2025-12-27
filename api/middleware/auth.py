"""
Authentication middleware.

Simple API key authentication for internal tool usage.
"""

from typing import Optional
from fastapi import Header, HTTPException, status, Query

from api.config import APIConfig


async def verify_api_key(authorization: str = Header(None, description="Bearer token")):
    """
    Verify API key from Authorization header.

    Args:
        authorization: Authorization header value (Bearer {key})

    Raises:
        HTTPException: If API key is missing or invalid

    Usage:
        @app.get("/protected", dependencies=[Depends(verify_api_key)])
        def protected_endpoint():
            ...
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Use: Bearer <api_key>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    api_key = authorization.replace("Bearer ", "")

    if api_key != APIConfig.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def verify_api_key_query(
    auth: Optional[str] = Query(None, description="API key for SSE (EventSource can't send headers)")
):
    """
    Verify API key from query parameter.

    Used for SSE endpoints where EventSource can't send custom headers.

    Args:
        auth: API key passed as query parameter

    Raises:
        HTTPException: If API key is missing or invalid

    Usage:
        @app.get("/stream", dependencies=[Depends(verify_api_key_query)])
        def stream_endpoint():
            ...
    """
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key in query parameter",
        )

    if auth != APIConfig.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
