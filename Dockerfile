# ============================================================================
# Multi-stage Dockerfile for InfoTransform
# ============================================================================
# Optimized Docker build for both Next.js frontend and Python FastAPI backend
# with minimal image size and improved build caching.

# ============================================================================
# Stage 1: Build Next.js Frontend
# ============================================================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files for dependency installation
COPY frontend/package*.json ./

# Install dependencies with clean install
RUN npm ci

# Copy frontend source code
COPY frontend/ ./

# Build arguments for Next.js
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
ENV NODE_ENV=production

# Build Next.js application with standalone output
RUN npm run build

# ============================================================================
# Stage 2: Python Backend Dependencies
# ============================================================================
FROM python:3.11-slim AS backend-builder

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install UV package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

WORKDIR /app

# Copy Python dependency files
COPY pyproject.toml uv.lock ./

# Install Python dependencies (production only)
RUN uv sync --frozen --no-dev

# ============================================================================
# Stage 3: Final Runtime Image
# ============================================================================
FROM python:3.11-slim

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ffmpeg \
    libmagic1 \
    poppler-utils \
    libreoffice \
    && rm -rf /var/lib/apt/lists/*

# Install UV for running Python app
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Install Node.js for Next.js frontend
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python virtual environment from builder
COPY --from=backend-builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy Python application files
COPY pyproject.toml uv.lock ./
COPY backend/ ./backend/
COPY config/ ./config/
COPY app.py ./

# Copy Next.js build artifacts from frontend builder
COPY --from=frontend-builder /app/frontend/.next/standalone ./frontend
COPY --from=frontend-builder /app/frontend/.next/static ./frontend/.next/static
COPY --from=frontend-builder /app/frontend/public ./frontend/public
COPY frontend/next.config.js ./frontend/

# Create necessary directories for application data
RUN mkdir -p data/uploads data/temp_extracts logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=production
ENV PORT=8000
ENV FRONTEND_PORT=3000

# Expose application ports
EXPOSE 8000 3000

# Copy and set up entrypoint script
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Health check to ensure services are running
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:${PORT:-8000}/docs || exit 1

# Use entrypoint script to start both services
ENTRYPOINT ["/app/docker-entrypoint.sh"]
