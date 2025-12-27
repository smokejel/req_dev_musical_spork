"""
FastAPI Application Entry Point.

Main application setup with middleware, routes, and exception handlers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.config import APIConfig
from api.models.database import init_db
from api.routes import health, workflows
from api.middleware import error_handler

# Create FastAPI app
app = FastAPI(
    title="ReqDecompose API",
    description="AI-powered requirements decomposition system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=APIConfig.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(StarletteHTTPException, error_handler.http_exception_handler)
app.add_exception_handler(RequestValidationError, error_handler.validation_exception_handler)
app.add_exception_handler(Exception, error_handler.generic_exception_handler)

# Include routers
app.include_router(health.router)
app.include_router(workflows.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    print("✓ Database initialized")
    print(f"✓ API server ready on {APIConfig.API_HOST}:{APIConfig.API_PORT}")
    print(f"✓ CORS origins: {', '.join(APIConfig.CORS_ORIGINS)}")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "ReqDecompose API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host=APIConfig.API_HOST,
        port=APIConfig.API_PORT,
        reload=True,
    )
