# Requirements Decomposition System - Docker Image
# Production-ready containerization with multi-stage build
# Phase 5 - Enhanced Docker Deployment

# ============================================================================
# Stage 1: Builder - Install dependencies
# ============================================================================
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Install system dependencies for PDF parsing
# poppler-utils provides pdftotext for PyPDF2
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies to /app/.venv
# Using a virtual environment allows us to copy only necessary files to runtime stage
RUN python -m venv /app/.venv && \
    /app/.venv/bin/pip install --no-cache-dir --upgrade pip && \
    /app/.venv/bin/pip install --no-cache-dir -r requirements.txt

# ============================================================================
# Stage 2: Runtime - Minimal production image
# ============================================================================
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install only runtime system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY src/ src/
COPY config/ config/
COPY skills/ skills/
COPY main.py .

# Create directories for outputs, checkpoints, and data
RUN mkdir -p outputs checkpoints data

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PATH="/app/.venv/bin:$PATH"

# Default command shows help
CMD ["python", "main.py", "--help"]

# ============================================================================
# Usage Examples
# ============================================================================
#
# RECOMMENDED: Use docker-compose for easier orchestration
#
# 1. Build and run with docker-compose:
#    docker-compose build
#    docker-compose run req-decomp python main.py examples/phase0_simple_spec.txt --subsystem "Authentication"
#
# 2. Interactive shell:
#    docker-compose run req-decomp /bin/bash
#
# 3. Show help:
#    docker-compose run req-decomp
#
# ALTERNATIVE: Direct docker commands (manual volume mounting)
#
# 1. Build image:
#    docker build -t req-decomp:latest .
#
# 2. Run with environment file:
#    docker run --rm \
#      --env-file .env \
#      -v $(pwd)/examples:/app/examples:ro \
#      -v $(pwd)/outputs:/app/outputs \
#      -v $(pwd)/checkpoints:/app/checkpoints \
#      -v $(pwd)/data:/app/data \
#      req-decomp:latest \
#      python main.py examples/phase0_simple_spec.txt --subsystem "Authentication"
#
# 3. Interactive mode with human review:
#    docker run --rm -it \
#      --env-file .env \
#      -v $(pwd)/examples:/app/examples:ro \
#      -v $(pwd)/outputs:/app/outputs \
#      -v $(pwd)/checkpoints:/app/checkpoints \
#      -v $(pwd)/data:/app/data \
#      req-decomp:latest \
#      python main.py examples/spec.txt --subsystem "Power" --review-before-decompose
#
# 4. Resume from checkpoint:
#    docker run --rm \
#      --env-file .env \
#      -v $(pwd)/checkpoints:/app/checkpoints \
#      -v $(pwd)/outputs:/app/outputs \
#      req-decomp:latest \
#      python main.py --resume --checkpoint-id 20251109_143022_nav
#
# ============================================================================
# Volume Mounts
# ============================================================================
# - /app/examples     (read-only)  - Input specification documents
# - /app/outputs      (read-write) - Generated requirements, traceability, reports
# - /app/checkpoints  (read-write) - Workflow state persistence (SQLite)
# - /app/data         (read-write) - Cost & quality tracking databases (Phase 5)
# - /app/scripts      (read-only)  - Optional: reporting scripts
#
# ============================================================================
# Environment Variables (Required)
# ============================================================================
# Create a .env file with:
# - ANTHROPIC_API_KEY  - Claude Sonnet 3.5 (Analyze node)
# - OPENAI_API_KEY     - GPT-5 Nano (Decompose node)
# - GOOGLE_API_KEY     - Gemini 2.5 (Extract, Validate nodes)
#
# Optional (LangSmith tracing for precise cost tracking):
# - LANGCHAIN_TRACING_V2=true
# - LANGCHAIN_API_KEY
# - LANGCHAIN_PROJECT=requirements-decomposition
#
# ============================================================================
# Image Details
# ============================================================================
# - Base: Python 3.11-slim
# - Build: Multi-stage (builder + runtime)
# - Size: ~400MB (optimized from ~500MB single-stage)
# - System deps: poppler-utils (PDF parsing)
# - Python deps: LangChain, LangGraph, Pydantic, Rich, etc.
