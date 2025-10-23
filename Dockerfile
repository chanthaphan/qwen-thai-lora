# Thai Language Model API - Docker Container
# Multi-stage build for optimization

# Stage 1: Base image with CUDA support
FROM nvidia/cuda:11.8-runtime-ubuntu22.04 as base

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    git \
    curl \
    wget \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create symlink for python
RUN ln -s /usr/bin/python3 /usr/bin/python

# Set working directory
WORKDIR /app

# Stage 2: Dependencies
FROM base as dependencies

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Application
FROM dependencies as application

# Copy project structure
COPY src/ ./src/
COPY models/ ./models/
COPY config/ ./config/

# Copy startup scripts
COPY start_api.sh .
RUN chmod +x start_api.sh

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose API port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Default command
CMD ["python", "src/hosting/fastapi_server.py"]

# Alternative commands available:
# docker run thai-model-api python src/testing/test_simple.py
# docker run thai-model-api ./start_api.sh