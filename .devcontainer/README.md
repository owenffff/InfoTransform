# InfoTransform Dev Container

This directory contains the VS Code Dev Container configuration for InfoTransform, providing a consistent, fully-configured development environment.

## Quick Start

### Prerequisites
- Docker Desktop installed and running
- VS Code with "Dev Containers" extension (`ms-vscode-remote.remote-containers`)
- `.env` file configured (copy from `.env.example` and set `OPENAI_API_KEY`)

### Opening the Dev Container

1. **Open in VS Code**: Open the InfoTransform project folder in VS Code
2. **Reopen in Container**:
   - Press `F1` or `Ctrl+Shift+P` (Windows/Linux) / `Cmd+Shift+P` (Mac)
   - Type "Dev Containers: Reopen in Container"
   - Press Enter
3. **Wait for Build**: First launch will take 5-10 minutes to build the container
4. **Start Services**: Once inside the container, services will start automatically via the entrypoint script

### Ports

The following ports are automatically forwarded to your host machine:

- **3000**: Next.js Frontend → http://localhost:3000
- **8000**: FastAPI Backend → http://localhost:8000/docs

## What's Included

### Pre-installed Tools
- **Python 3.11.3** with UV package manager
- **Node.js 20.x** with npm
- **Git** with Oh My Zsh
- **GitHub CLI** (`gh`)
- **Document processing tools**: ffmpeg, poppler-utils, libreoffice, libmagic

### VS Code Extensions
- **Python**: Pylance, Ruff formatter, Black, debugpy, pytest
- **TypeScript/React**: ESLint, Prettier, Tailwind CSS IntelliSense
- **DevOps**: Docker, Dev Containers
- **General**: GitLens, GitHub Copilot, Error Lens, REST Client

### Development Features
- **Hot-reloading**: Changes to Python/TypeScript code reload automatically
- **IntelliSense**: Full autocomplete for Python and TypeScript
- **Debugging**: Configured debuggers for both backend and frontend
- **Testing**: Pytest configured for Python tests
- **Formatting**: Auto-format on save for Python (Ruff) and TypeScript (Prettier)
- **Linting**: Ruff for Python, ESLint for TypeScript

## Running the Application

### Automatic Start (Default)
Services start automatically via the `docker-entrypoint-dev.sh` script:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

### Manual Start (If needed)
If you need to restart services manually:

```bash
# Backend only
uv run python app.py

# Frontend only
cd frontend && npm run dev

# Both services together
/app/docker-entrypoint-dev.sh
```

### Checking Service Status
```bash
# Check if services are running
ps aux | grep -E "python|node"

# View backend logs
tail -f /tmp/backend.log

# View frontend logs
tail -f /tmp/frontend.log

# Check health
curl http://localhost:8000/health
```

## Development Workflow

### Python Backend Development
```bash
# Run linting
uv run ruff check backend/

# Run formatting
uv run ruff format backend/

# Run tests
uv run pytest tests/

# Add new dependencies
# Edit pyproject.toml, then:
uv sync
```

### Frontend Development
```bash
cd frontend

# Install new packages
npm install <package-name>

# Build production
npm run build

# Type checking
npx tsc --noEmit
```

## Debugging

### Python Debugging
1. Set breakpoints in Python files (click left margin)
2. Press `F5` or use "Run and Debug" panel
3. Select "Python: FastAPI" configuration
4. Debugger will attach to the running FastAPI server

### TypeScript Debugging
1. Set breakpoints in TypeScript files
2. Open Chrome DevTools in your browser (F12)
3. Use browser's built-in debugger
4. Or use VS Code's "Next.js: debug full stack" configuration

## Troubleshooting

### Container won't start
```bash
# Rebuild container from scratch
# Command Palette → "Dev Containers: Rebuild Container"

# Or rebuild without cache
docker-compose -f docker-compose.yml -f .devcontainer/docker-compose.yml build --no-cache
```

### Services not starting
```bash
# Check entrypoint script logs
docker logs infotransform-dev

# Manually restart services
pkill -f "python app.py"
pkill -f "next dev"
/app/docker-entrypoint-dev.sh
```

### Port conflicts
If ports 3000 or 8000 are already in use:

1. Stop conflicting services on host machine
2. Or modify `.env` file:
   ```env
   PORT=3001
   BACKEND_PORT=8001
   NEXT_PUBLIC_BACKEND_PORT=8001
   ```
3. Rebuild container: "Dev Containers: Rebuild Container"

### Volume permission issues
```bash
# Ensure directories exist with proper permissions
mkdir -p data/uploads data/temp_extracts logs
mkdir -p data/uploads/review_sessions data/uploads/review_documents
mkdir -p backend/infotransform/data
chmod -R 755 data/ logs/ backend/infotransform/data/
```

### Corporate certificate issues
If you're behind a corporate firewall:

1. Place your CA certificate at `certs/corporate-ca.crt` in the project root
2. Rebuild container: "Dev Containers: Rebuild Container"
3. The certificate will be automatically installed during build

### Python dependencies not found
```bash
# Ensure virtual environment is activated
source /app/.venv/bin/activate

# Or use uv run prefix
uv run python app.py
```

### Frontend modules not found
```bash
cd /app/frontend
npm install
```

## Data Persistence

The following directories are persisted across container rebuilds:

- `data/uploads` - Uploaded files
- `data/temp_extracts` - Temporary extraction directory
- `data/uploads/review_sessions` - Review workspace sessions
- `data/uploads/review_documents` - Review documents
- `backend/infotransform/data` - SQLite databases (processing logs)
- `logs` - Application logs

These are mounted as volumes from your host machine, so data survives container recreation.

## Performance Tips

### Speed up rebuilds
- The devcontainer uses layer caching - only changed layers rebuild
- Keep `pyproject.toml` and `package.json` changes separate from code changes
- Use `uv sync --frozen` to avoid dependency resolution

### Reduce disk usage
```bash
# Clean up old containers and images
docker system prune -a

# Remove unused volumes (WARNING: deletes data)
docker volume prune
```

### Faster file watching
The container uses volumes for hot-reloading. If file changes aren't detected:

```bash
# Restart file watcher (frontend)
cd frontend && npm run dev

# Restart uvicorn (backend)
pkill -f "python app.py" && uv run python app.py
```

## VS Code Integration

### Recommended Shortcuts
- `Ctrl+\`` (backtick): Toggle terminal
- `Ctrl+Shift+P`: Command palette
- `F5`: Start debugging
- `Ctrl+Shift+B`: Run build task
- `Ctrl+K Ctrl+O`: Open folder in container

### Workspace Settings
All Python and TypeScript settings are pre-configured in `devcontainer.json`. Changes persist across container rebuilds.

### Tasks
Create `.vscode/tasks.json` for common operations:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start Backend",
      "type": "shell",
      "command": "uv run python app.py",
      "problemMatcher": []
    },
    {
      "label": "Start Frontend",
      "type": "shell",
      "command": "cd frontend && npm run dev",
      "problemMatcher": []
    }
  ]
}
```

## Environment Configuration

The devcontainer uses the **development** environment by default (`ENV=development`).

To use different environments:
```bash
# Staging
ENV=staging uv run python app.py

# Production (use docker-compose.prod.yml instead)
# Not recommended in devcontainer
```

Configuration files:
- `config/config.development.yaml` - Development settings
- `config/config.staging.yaml` - Staging settings
- `config/config.production.yaml` - Production settings

## Corporate Environment Notes

### Proxy Configuration
If behind a corporate proxy, add to `.env`:
```env
HTTP_PROXY=http://proxy.company.com:8080
HTTPS_PROXY=http://proxy.company.com:8080
NO_PROXY=localhost,127.0.0.1
```

### Private NPM Registry
Add to `frontend/.npmrc`:
```
registry=https://npm.company.com/
```

### Private PyPI Registry
Add to `pyproject.toml`:
```toml
[[tool.uv.index]]
url = "https://pypi.company.com/simple"
```

## Comparison: Dev Container vs Docker Compose

| Feature | Dev Container | Docker Compose |
|---------|--------------|----------------|
| **VS Code Integration** | Full IDE integration | External terminal required |
| **Extensions** | Auto-installed | Manual setup |
| **Debugging** | Built-in debugger | Manual configuration |
| **Port Forwarding** | Automatic | Manual mapping |
| **Git Integration** | Seamless | SSH key mapping needed |
| **Terminal** | VS Code integrated | External terminal |
| **Use Case** | Daily development | Testing, CI/CD, quick runs |

## Additional Resources

- [VS Code Dev Containers Documentation](https://code.visualstudio.com/docs/devcontainers/containers)
- [Docker Documentation](https://docs.docker.com/)
- [InfoTransform README](../README.md)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
