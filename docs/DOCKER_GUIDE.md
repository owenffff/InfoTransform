# Docker Guide for InfoTransform

This guide explains how to containerize and run InfoTransform using Docker, and how to maintain the containerization as you develop.

## Overview

The project includes multiple Docker configurations:
- **Production**: Optimized multi-stage build for deployment
- **Development**: Hot-reload enabled setup for active development

## Files Created

1. **`Dockerfile`** - Production-ready multi-stage build
2. **`Dockerfile.dev`** - Development image with hot-reload support
3. **`.dockerignore`** - Excludes unnecessary files from Docker context
4. **`docker-compose.yml`** - Production orchestration
5. **`docker-compose.dev.yml`** - Development orchestration with volume mounts

## Quick Start

### Prerequisites
- Docker installed on your system
- Docker Compose (usually comes with Docker Desktop)
- `.env` file with your configuration (copy from `.env.example`)

### Production Deployment

1. Build and run the production container:
```bash
docker-compose up --build
```

2. Access the application:
- Main app: http://localhost:8000
- API docs: http://localhost:8000/docs

3. Stop the container:
```bash
docker-compose down
```

### Development with Hot-Reload

1. Run the development container:
```bash
docker-compose -f docker-compose.dev.yml up --build
```

2. Edit your code - changes will be reflected immediately:
- Python files: FastAPI auto-reloads on save
- Frontend files: Tailwind and esbuild watch for changes

3. Stop the development container:
```bash
docker-compose -f docker-compose.dev.yml down
```

## How It Works

### Production Build (Dockerfile)

The production Dockerfile uses a multi-stage build:

1. **Stage 1 (frontend-builder)**:
   - Uses Node.js Alpine image
   - Installs npm dependencies
   - Builds CSS with Tailwind and JS with esbuild
   - Outputs minified production assets

2. **Stage 2 (Python app)**:
   - Uses Python 3.11 slim image
   - Installs system dependencies (gcc, g++, libmagic1)
   - Installs Python dependencies using `uv` for speed
   - Copies application code and built frontend assets
   - Creates necessary directories
   - Runs the FastAPI application

### Development Setup (Dockerfile.dev)

The development setup:
- Installs both Python and Node.js in the same container
- Mounts your local code as volumes
- Runs both frontend watchers and the Python server
- Enables hot-reload for immediate feedback

## Keeping Docker Updated

### When You Change Code

**Development Mode**: Code changes are automatically reflected due to volume mounts. No rebuild needed!

**Production Mode**: You need to rebuild when you:
- Change Python dependencies in `pyproject.toml`
- Change Node dependencies in `package.json`
- Modify Docker configuration files

Rebuild command:
```bash
docker-compose build --no-cache
docker-compose up
```

### When You Add Dependencies

1. **Python Dependencies**:
   ```bash
   # Add to pyproject.toml, then:
   docker-compose build
   ```

2. **Node Dependencies**:
   ```bash
   # Add to package.json, then:
   docker-compose build
   ```

### Best Practices

1. **Use Development Mode** for active development:
   ```bash
   docker-compose -f docker-compose.dev.yml up
   ```

2. **Test Production Build** before deploying:
   ```bash
   docker-compose up --build
   ```

3. **Clean Up** unused images periodically:
   ```bash
   docker system prune -a
   ```

4. **Volume Management**:
   - Data persists in `./data/` directory
   - Logs persist in `./logs/` directory
   - These are mounted as volumes in both dev and prod

## Common Commands

### Build Commands
```bash
# Build production image
docker build -t infotransform:latest .

# Build development image
docker build -f Dockerfile.dev -t infotransform:dev .

# Build with no cache
docker build --no-cache -t infotransform:latest .
```

### Run Commands
```bash
# Run production
docker-compose up -d  # -d for detached mode

# Run development
docker-compose -f docker-compose.dev.yml up

# View logs
docker-compose logs -f

# Stop containers
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Debugging Commands
```bash
# Enter running container
docker-compose exec app bash

# View running containers
docker ps

# Inspect container
docker inspect <container_id>

# View container logs
docker logs <container_id>
```

## Environment Variables

The Docker setup respects all environment variables in your `.env` file:
- `OPENAI_API_KEY` - Required for AI features
- `PORT` - Application port (default: 8000)
- `QUIET_MODE` - Reduce logging output

## Troubleshooting

### Container won't start
1. Check logs: `docker-compose logs`
2. Ensure `.env` file exists with required variables
3. Verify ports aren't already in use

### Changes not reflecting
1. In development: Ensure you're using `docker-compose.dev.yml`
2. In production: Rebuild the image
3. Clear browser cache for frontend changes

### Permission issues
- Ensure data directories have proper permissions
- On Linux, you might need to adjust user permissions in Dockerfile

### Out of space
```bash
# Clean up Docker system
docker system prune -a --volumes
```

## Advanced Usage

### Custom Port
```bash
# In .env file
PORT=3000

# Or override at runtime
PORT=3000 docker-compose up
```

### Production Optimization
For production, consider:
1. Using specific version tags instead of `latest`
2. Implementing health checks
3. Setting resource limits
4. Using Docker secrets for sensitive data

### CI/CD Integration
The Dockerfile is designed to work with CI/CD pipelines:
```yaml
# Example GitHub Actions
- name: Build and push
  run: |
    docker build -t myregistry/infotransform:${{ github.sha }} .
    docker push myregistry/infotransform:${{ github.sha }}
```

## Summary

The Docker setup provides:
- **Consistency**: Same environment everywhere
- **Isolation**: No system pollution
- **Easy deployment**: Single command to run
- **Development efficiency**: Hot-reload for rapid iteration
- **Production readiness**: Optimized multi-stage builds

For development, use `docker-compose -f docker-compose.dev.yml up` and edit freely.
For production, use `docker-compose up --build` for a clean, optimized deployment.
