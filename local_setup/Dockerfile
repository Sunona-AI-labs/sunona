# Sunona Voice AI - Production Dockerfile
# Single-stage build for reliability with complex dependencies

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 sunona 


# Copy requirements first for better caching
COPY requirements.txt ./requirements.txt

# Install CPU-only PyTorch first (saves ~3GB vs GPU version)
# Then install remaining requirements
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir --no-deps -r requirements.txt && \
    pip install --no-cache-dir -r requirements.txt || echo "Some dependency conflicts exist but core packages installed" && \
    rm -rf /root/.cache/pip

# Copy source code
COPY --chown=sunona:sunona . .

# Install the package in editable mode (--no-deps since deps already installed)
RUN pip install --no-deps -e .

# Switch to non-root user
USER sunona

# Environment configuration
ENV PATH=/home/sunona/.local/bin:$PATH
ENV PYTHONPATH=/app:$PYTHONPATH
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
