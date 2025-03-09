# Use multi-stage builds for development and production

# Base stage with common dependencies
FROM python:3.9-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements.txt .
COPY requirements-dev.txt .

# Create a non-root user
RUN adduser --disabled-password --gecos "" appuser && \
    mkdir -p /app/config /app/logs /tmp/mcp_temp && \
    chown -R appuser:appuser /app /tmp/mcp_temp

# Development stage
FROM base as development

# Install development dependencies
RUN pip install -r requirements-dev.txt

# Copy the application code
COPY . .

# Set permissions
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose the port
EXPOSE 5000

# Command to run the server
CMD ["python", "src/mcp_server.py"]

# Production stage
FROM base as production

# Install production dependencies only
RUN pip install -r requirements.txt

# Copy the application code
COPY . .

# Set permissions
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose the port
EXPOSE 5000

# Command to run the server with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--access-logfile", "-", "src.mcp_server:app"]
