# Sunona Voice AI - Production Dockerfile
# Build: docker build -f local_setup/Dockerfile -t sunona-api:latest .

FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 sunona

# Copy requirements
COPY requirements-docker.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY --chown=sunona:sunona sunona/ ./sunona/
COPY --chown=sunona:sunona pyproject.toml ./
COPY --chown=sunona:sunona README.md ./

# Install the package
RUN pip install --no-cache-dir -e .

# Switch to non-root user
USER sunona

# Environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV SUNONA_HOST=0.0.0.0
ENV SUNONA_PORT=8000

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run server
CMD ["python", "-m", "uvicorn", "sunona.server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
