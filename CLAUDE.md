# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

InfoTransform is a document processing application that transforms various file types (images, PDFs, documents, audio) into structured data using AI-powered analysis. The application uses FastAPI for the backend, Next.js with TypeScript and Tailwind CSS for the frontend, and integrates OpenAI's GPT models through Pydantic AI.

## Architecture

### Backend (`backend/infotransform/`)
- **Entry Point**: `app.py` - Starts the FastAPI server with uvicorn
- **Main Application**: `backend/infotransform/main.py` - FastAPI app setup, middleware, and routing
- **API Layer**: `backend/infotransform/api/document_transform_api.py` - Streaming processor for file transformations
- **Processors**: 
  - `async_converter.py` - Parallel markdown conversion using markitdown
  - `ai_batch_processor.py` - Batch processing for AI analysis
  - `structured_analyzer_agent.py` - Pydantic AI agent for structured data extraction
  - `vision.py` & `audio.py` - Specialized processors for media files
- **Configuration**: YAML-based config system (`config/`) with environment variable support

### Frontend (`frontend/`)
- **Framework**: Next.js 14 with App Router and TypeScript
- **State Management**: Zustand for global state management
- **Components**: React components in `components/` (FileUpload, AnalysisOptions, ProcessingStatus, ResultsDisplay)
- **Styling**: Tailwind CSS with PostCSS
- **API Integration**: Custom hooks and API client in `lib/`
- **Type Safety**: TypeScript types in `types/`

## Development Commands

### Backend Development
```bash
# Install dependencies (using UV package manager)
uv sync

# Run backend server only
uv run python app.py

# Run with quiet mode (reduced logging)
QUIET_MODE=true uv run python app.py

# Run linting
uv run ruff check backend/

# Run formatting
uv run ruff format backend/
```

### Frontend Development
```bash
# Install Node dependencies (from root or frontend directory)
npm install
# Or from frontend directory
cd frontend && npm install

# Development mode (runs Next.js dev server + backend)
npm run dev

# Run only Next.js frontend
npm run dev:next
# Or from frontend directory
cd frontend && npm run dev

# Build production frontend
npm run build

# Production deployment (frontend + backend with production config)
npm run start
# Or explicitly specify environment:
npm run start:production   # Uses config/config.production.yaml
npm run start:staging      # Uses config/config.staging.yaml
npm run start:development  # Uses config/config.development.yaml

# Clean build artifacts
npm run clean
```

### Testing
```bash
# Run tests (when implemented - currently no test framework set up)
# uv run pytest tests/
```

### Docker Development
```bash
# Build and start development environment with Docker
docker-compose up --build

# Start existing containers
docker-compose up

# Stop containers
docker-compose down

# View logs
docker-compose logs -f

# Rebuild after dependency changes
docker-compose up --build
```

**Docker Features:**
- Hot-reloading for both frontend and backend
- Source code mounted as volumes for live changes
- Corporate CA certificate support (place cert at `certs/corporate-ca.crt`)
- UV installed via pip for better corporate network compatibility
- All services accessible at same ports (3000, 8000)

## Key API Endpoints

### Backend API (FastAPI - Port 8000)
- `POST /api/transform` - Process files with streaming response (SSE)
- `GET /api/models` - List available document schemas  
- `POST /api/download-results` - Export results as Excel/CSV
- `GET /docs` - Swagger API documentation
- `GET /redoc` - ReDoc API documentation

### Frontend (Next.js - Port 3000)
- `/` - Main application interface
- API calls are proxied from frontend to backend

## Adding New document schemas

Edit `config/document_schemas.py`:

1. Create a Pydantic model class inheriting from BaseModel
2. Add Field descriptions for each attribute
3. Register in AVAILABLE_MODELS dictionary at the bottom of the file

Example:
```python
class YourModel(BaseModel):
    field_name: str = Field(description="Field description")
    
# In AVAILABLE_MODELS:
"your_model_key": YourModel
```

## Configuration Files

### Backend Configuration
- **Environment Variables**: Copy `.env.example` to `.env` and set:
  - `OPENAI_API_KEY` (required)
  - `PORT`, `UPLOAD_FOLDER`, `TEMP_EXTRACT_DIR` (optional)
  - `ENV` (optional) - Sets which config file to use: `development` (default), `staging`, or `production`

- **Main Config**: `config/config.yaml` - Default app settings, storage paths, model configurations
- **Environment-Specific Configs**:
  - `config/config.development.yaml` - Development environment settings
  - `config/config.staging.yaml` - Staging environment settings
  - `config/config.production.yaml` - Production environment settings
- **Performance**: `config/performance.yaml` - Parallel processing, batch sizes, monitoring

**How Environment Selection Works:**
1. The backend checks the `ENV` environment variable (defaults to `development`)
2. Loads `config/config.{ENV}.yaml` if it exists, otherwise falls back to `config/config.yaml`
3. This allows different settings for development vs production (e.g., different AI models, logging levels, resource limits)

### Frontend Configuration
- **Next.js Config**: `frontend/next.config.js` - Next.js configuration
- **TypeScript**: `frontend/tsconfig.json` - TypeScript compiler options
- **Tailwind**: `frontend/tailwind.config.js` - Tailwind CSS configuration
- **PostCSS**: `frontend/postcss.config.mjs` - PostCSS plugins

## Frontend Components

### Core Components
- **FileUpload**: Drag-and-drop file upload with react-dropzone
- **AnalysisOptions**: Model selection and configuration UI
- **ProcessingStatus**: Real-time SSE progress display
- **ResultsDisplay**: Results viewer with export functionality
- **Toast**: Notification system for user feedback

### State Management (Zustand Store)
- Files management
- Processing state tracking
- Results storage
- Error handling

## File Processing Pipeline

1. **Upload**: Files uploaded via Next.js frontend
2. **API Call**: Frontend sends files to FastAPI backend
3. **Conversion**: Parallel markdown conversion using AsyncMarkdownConverter
4. **AI Analysis**: Batch processing through Pydantic AI agents
5. **Streaming**: Results streamed back via Server-Sent Events
6. **Display**: Real-time updates in React components
7. **Export**: Download results as Excel/CSV
8. **Cleanup**: Automatic file lifecycle management

## Important Patterns

- **Streaming Architecture**: Uses SSE for real-time progress updates
- **Parallel Processing**: Configurable workers for markdown conversion
- **Batch AI Processing**: Groups files for efficient API calls
- **Error Handling**: Graceful degradation with fallback processors
- **File Lifecycle**: Automatic cleanup of temporary files

## Dependencies

### Backend
- **Python**: FastAPI, Pydantic AI, markitdown, OpenAI, pandas, uvicorn
- **Package Manager**: UV

### Frontend
- **Framework**: Next.js 14, React 18, TypeScript 5
- **UI Libraries**: Tailwind CSS, lucide-react, react-dropzone
- **State Management**: Zustand
- **Utilities**: clsx, tailwind-merge
- **Package Manager**: npm

Note: Excel/CSV export is handled server-side by the Python backend using pandas.

## Performance Considerations

- Default parallel workers: 4 for markdown conversion
- Default batch size: 5 files for AI processing
- Configurable via `config/performance.yaml`
- Monitor slow operations threshold: 5 seconds

## Development Ports

- **Frontend (Next.js)**: http://localhost:3000
- **Backend (FastAPI)**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Security Notes

- API keys stored in `.env` file (never commit)
- CORS configured for all origins (restrict in production)
- File size limits: 50MB single file, 100MB for ZIP archives
- Automatic cleanup of uploaded files after processing

## Cross-Platform Compatibility

### Platform Support
InfoTransform is designed to run on **Windows**, **WSL**, and **macOS/Linux**. The codebase uses cross-platform tools and conventions:

- **Path Handling**: Backend uses `pathlib.Path` throughout for OS-agnostic path operations
- **Environment Variables**: Uses `dotenv-cli` for loading `.env` files on all platforms
- **npm Scripts**: All scripts work cross-platform without bash-specific syntax
- **Python Execution**: Uses `uv run python` which works on all platforms
- **Directory Operations**: Uses `os.makedirs(..., exist_ok=True)` and pathlib for cross-platform compatibility

### Platform-Specific Notes

#### Windows Users
- **Recommended**: Use provided batch files for convenience:
  - `setup.bat` - One-time setup script (installs dependencies, creates .env)
  - `dev.bat` - Start development server
- **PowerShell/CMD**: Standard `npm run dev` works in PowerShell and CMD
- Ensure Python is accessible as `python` command
- Copy `.env.example` to `.env` and configure `OPENAI_API_KEY`
- All npm scripts are PowerShell-compatible (no bash syntax used)

#### WSL Users  
- Follow Linux setup instructions
- Ensure LF line endings (not CRLF)
- May need additional system dependencies for markitdown

#### macOS/Linux Users
- No special considerations needed
- Use standard bash/zsh commands

### Known Compatibility Issues (Resolved)

**PowerShell Variable Substitution (Fixed)**: Earlier versions used bash-style `${VAR:-default}` syntax in npm scripts, which failed in PowerShell. This has been resolved:
- npm scripts now rely on `.env` file for default values via `dotenv-cli`
- Python config has fallback logic for invalid environment variables
- All scripts tested on Windows PowerShell, CMD, and Unix shells

### When Making Changes
- Always use `pathlib.Path` for file operations in Python, never hardcoded paths
- Use `os.path.join()` or Path operators (`/`) instead of string concatenation
- Use `os.makedirs()` with `exist_ok=True` for directory creation
- Avoid bash-specific syntax in npm scripts (use `&&` not `;`, avoid `$VAR` expansion)
- Use cross-platform npm packages (`concurrently`, `dotenv-cli`)
- Test changes on both Windows and Unix if modifying paths or environment handling