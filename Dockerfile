# Requirements Decomposition System - Docker Image
# Production-ready containerization for MVP deployment
# Phase 4.3 - Testing & Deployment

FROM python:3.11-slim

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

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ src/
COPY config/ config/
COPY skills/ skills/
COPY main.py .

# Create directories for outputs and checkpoints
RUN mkdir -p outputs checkpoints

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Default command shows help
CMD ["python", "main.py", "--help"]

# Usage Examples:
#
# 1. Build image:
#    docker build -t req-decomp:latest .
#
# 2. Run with environment file:
#    docker run --rm \
#      --env-file .env \
#      -v $(pwd)/examples:/app/examples:ro \
#      -v $(pwd)/outputs:/app/outputs \
#      req-decomp:latest \
#      python main.py examples/phase0_simple_spec.txt --subsystem "Authentication"
#
# 3. Interactive mode:
#    docker run --rm -it \
#      --env-file .env \
#      -v $(pwd)/examples:/app/examples:ro \
#      -v $(pwd)/outputs:/app/outputs \
#      req-decomp:latest \
#      /bin/bash
#
# 4. With checkpoints (resume support):
#    docker run --rm \
#      --env-file .env \
#      -v $(pwd)/examples:/app/examples:ro \
#      -v $(pwd)/outputs:/app/outputs \
#      -v $(pwd)/checkpoints:/app/checkpoints \
#      req-decomp:latest \
#      python main.py --resume --checkpoint-id 20251109_143022_nav
#
# Notes:
# - .env file must contain API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY)
# - Mount examples directory read-only for security
# - Mount outputs directory for result persistence
# - Mount checkpoints directory for resume capability
# - Image size: ~500MB (Python 3.11 + dependencies)
