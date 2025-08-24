# ==========================================
# KOREI ASSISTANT - PRODUCTION DOCKERFILE
# Multi-stage build for optimized production
# ==========================================

# ============================================
# STAGE 1: Build stage (dependencies)
# ============================================
FROM python:3.11-slim as builder

LABEL maintainer="Korei Assistant Team"
LABEL version="2.0.0"
LABEL description="WhatsApp AI Assistant with Gemini integration"

# Set build environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# ============================================
# STAGE 2: Production stage
# ============================================
FROM python:3.11-slim as production

# Set production environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/opt/venv/bin:$PATH"
ENV ENVIRONMENT=production

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create app directory
WORKDIR /app

# Create non-root user for security
RUN groupadd -r korei && \
    useradd -r -g korei -d /app -s /bin/bash korei

# Create necessary directories
RUN mkdir -p logs temp && \
    chown -R korei:korei /app

# Copy application code (exclude unnecessary files)
COPY --chown=korei:korei main.py .
COPY --chown=korei:korei app/ ./app/
COPY --chown=korei:korei api/ ./api/
COPY --chown=korei:korei core/ ./core/
COPY --chown=korei:korei handlers/ ./handlers/
COPY --chown=korei:korei services/ ./services/
# COPY --chown=korei:korei middleware/ ./middleware/ # Directory does not exist

# Switch to non-root user
USER korei

# Expose port (dynamic for DigitalOcean App Platform)
EXPOSE 8000
ENV PORT=8000

# Health check with dynamic port
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Run application with Gunicorn for production (dynamic port)
CMD gunicorn main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT} --timeout 120