# Sunona Voice AI - Production Dockerfile
# Optimized with BuildKit for faster builds
# Enable BuildKit: set DOCKER_BUILDKIT=1

# syntax=docker/dockerfile:1.4

# ==========================================================================
# Stage 1: Dependencies (cached layer)
# ==========================================================================
FROM python:3.14-slim AS deps

WORKDIR /app

# Install build dependencies
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with pip cache
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --user -r requirements.txt

# ==========================================================================
# Stage 2: Production image
# ==========================================================================
FROM python:3.14-slim AS production

WORKDIR /app

# Install runtime dependencies with cache
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 sunona

# Copy Python packages from deps stage
COPY --from=deps /root/.local /home/sunona/.local

# Copy source code (use .dockerignore to exclude unnecessary files)
COPY --chown=sunona:sunona . .

# Install the package
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -e .

# Switch to non-root user
USER sunona

# Add local packages to PATH
ENV PATH=/home/sunona/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV SUNONA_HOST=0.0.0.0
ENV SUNONA_PORT=8000

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run server with uvicorn
CMD ["python", "-m", "uvicorn", "sunona.server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
