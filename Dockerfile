# ============================================================================
# Multi-Stage Dockerfile for InfoTransform
# ============================================================================
# Supports both development and production environments with optimized builds
# Build development: docker build --target development -t infotransform:dev .
# Build production: docker build --target production -t infotransform:prod .

# ============================================================================
# Base Stage - Common system dependencies
# ============================================================================
FROM python:3.11.10-slim-bookworm AS base

# Install system dependencies required for document processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    gnupg \
    build-essential \
    ffmpeg \
    libmagic1 \
    poppler-utils \
    libreoffice \
    && rm -rf /var/lib/apt/lists/*

# Optional: Add corporate root CA certificate support
# Place your certificate at certs/corporate-ca.crt in the repository
COPY certs/corporate-ca.crt /usr/local/share/ca-certificates/corporate-ca.crt 2>/dev/null || true
RUN update-ca-certificates || true

# Install UV package manager (more reliable in corporate environments)
RUN pip install --no-cache-dir uv || curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Install Node.js 20.x for Next.js frontend
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get update \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app


# ============================================================================
# Dependencies Stage - Install Python and Node dependencies
# ============================================================================
FROM base AS dependencies

# Copy Python dependency files
COPY pyproject.toml uv.lock ./

# Install Python dependencies using UV
RUN uv sync --frozen

# Copy frontend package files
COPY frontend/package*.json ./frontend/

# Install Node.js dependencies
RUN cd frontend && npm ci --only=production


# ============================================================================
# Builder Stage - Build Next.js frontend for production
# ============================================================================
FROM dependencies AS builder

# Copy frontend source code
COPY frontend ./frontend

# Copy configuration files needed for build
COPY config ./config
COPY .env.example .env

# Build Next.js application
WORKDIR /app/frontend
RUN npm run build

WORKDIR /app


# ============================================================================
# Development Stage - Hot-reloading environment
# ============================================================================
FROM dependencies AS development

# Install development dependencies
RUN cd frontend && npm install

# Copy application code
# Note: In development, source code is typically mounted as volumes
# This COPY ensures the container can run standalone if needed
COPY . .

# Create necessary directories for application data
RUN mkdir -p \
    data/uploads \
    data/temp_extracts \
    data/uploads/review_sessions \
    data/uploads/review_documents \
    logs \
    backend/infotransform/data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=development
ENV PORT=3000
ENV BACKEND_PORT=8000
ENV PATH="/app/.venv/bin:$PATH"

# Expose application ports
EXPOSE 3000 8000

# Copy and set up development entrypoint script
COPY docker-entrypoint-dev.sh /app/docker-entrypoint-dev.sh
RUN chmod +x /app/docker-entrypoint-dev.sh

# Health check for development
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["/app/docker-entrypoint-dev.sh"]


# ============================================================================
# Production Stage - Optimized production build
# ============================================================================
FROM base AS production

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

WORKDIR /app

# Copy Python dependencies from dependencies stage
COPY --from=dependencies --chown=appuser:appuser /app/.venv /app/.venv
COPY --from=dependencies --chown=appuser:appuser /app/pyproject.toml /app/uv.lock ./

# Copy production Next.js build from builder stage
COPY --from=builder --chown=appuser:appuser /app/frontend/.next ./frontend/.next
COPY --from=builder --chown=appuser:appuser /app/frontend/public ./frontend/public
COPY --from=builder --chown=appuser:appuser /app/frontend/package*.json ./frontend/

# Install only production Node.js dependencies
RUN cd frontend && npm ci --only=production && npm cache clean --force

# Copy application source code
COPY --chown=appuser:appuser backend ./backend
COPY --chown=appuser:appuser config ./config
COPY --chown=appuser:appuser app.py ./
COPY --chown=appuser:appuser .env.example .env

# Create necessary directories with proper permissions
RUN mkdir -p \
    data/uploads \
    data/temp_extracts \
    data/uploads/review_sessions \
    data/uploads/review_documents \
    logs \
    backend/infotransform/data && \
    chown -R appuser:appuser data logs backend/infotransform/data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=production
ENV PORT=3000
ENV BACKEND_PORT=8000
ENV PATH="/app/.venv/bin:$PATH"
ENV ENV=production

# Expose application ports
EXPOSE 3000 8000

# Copy and set up production entrypoint script
COPY --chown=appuser:appuser docker-entrypoint-prod.sh /app/docker-entrypoint-prod.sh
RUN chmod +x /app/docker-entrypoint-prod.sh

# Switch to non-root user
USER appuser

# Health check for production
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["/app/docker-entrypoint-prod.sh"]
