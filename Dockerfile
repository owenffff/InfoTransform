# Multi-stage Dockerfile for InfoTransform

# Stage 1: Build frontend assets
FROM node:20-alpine AS frontend-builder

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY tailwind.config.js ./
COPY postcss.config.js ./

# Install dependencies
RUN npm ci

# Copy frontend source files
COPY frontend/src ./frontend/src
COPY frontend/templates ./frontend/templates

# Build frontend assets
RUN npm run build

# Stage 2: Python application
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Required for some Python packages
    gcc \
    g++ \
    # Required for markitdown dependencies
    libmagic1 \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python requirements
COPY pyproject.toml ./

# Install uv for faster Python package management
RUN pip install uv

# Install Python dependencies
RUN uv pip install --system -e .

# Copy application code
COPY app.py ./
COPY backend ./backend
COPY config ./config
COPY frontend/templates ./frontend/templates
COPY frontend/static ./frontend/static

# Copy built frontend assets from the frontend-builder stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create necessary directories
RUN mkdir -p data/uploads data/temp_extracts logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose the application port (default 8000)
EXPOSE 8000

# Run the application
CMD ["python", "app.py"]
