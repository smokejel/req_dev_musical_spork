FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    poppler-utils \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install API-specific dependencies
RUN pip install --no-cache-dir -r requirements-api.txt

# Copy application code
COPY src/ src/
COPY config/ config/
COPY skills/ skills/
COPY domain_contexts/ domain_contexts/
COPY main.py .
COPY api/ api/

# Create necessary directories
RUN mkdir -p checkpoints uploads

# Set environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Expose API port
EXPOSE 8000

# Run uvicorn server
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
