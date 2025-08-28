FROM python:3.13-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV UV_SYSTEM_PYTHON=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV
RUN pip install uv

# Copy dependency files and README
COPY pyproject.toml uv.lock* README.md ./

# Install Python dependencies
RUN uv sync --frozen

# Copy application code
COPY src/ ./src/
COPY tests/ ./tests/
COPY .env* ./

# Copy scripts
COPY scripts.py ./

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Default command
CMD ["python", "scripts.py", "start"]
