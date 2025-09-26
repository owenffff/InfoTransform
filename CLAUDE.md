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
# Or
npm run build:next

# Start production Next.js server (from frontend directory)
cd frontend && npm run start

# Clean build artifacts
npm run clean
```

### Testing
```bash
# Run tests (when implemented - currently no test framework set up)
# uv run pytest tests/
```

## Key API Endpoints

### Backend API (FastAPI - Port 8000)
- `POST /api/transform` - Process files with streaming response (SSE)
- `GET /api/models` - List available analysis models  
- `POST /api/download-results` - Export results as Excel/CSV
- `GET /docs` - Swagger API documentation
- `GET /redoc` - ReDoc API documentation

### Frontend (Next.js - Port 3000)
- `/` - Main application interface
- API calls are proxied from frontend to backend

## Adding New Analysis Models

Edit `config/analysis_schemas.py`:

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
  
- **Main Config**: `config/config.yaml` - App settings, storage paths, model configurations
- **Performance**: `config/performance.yaml` - Parallel processing, batch sizes, monitoring

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
- **Utilities**: clsx, tailwind-merge, xlsx
- **Package Manager**: npm

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

## Legacy Frontend

The project maintains a legacy vanilla JavaScript frontend in `frontend-legacy/` directory. To use the legacy frontend:
```bash
# Build and run legacy frontend
npm run dev:legacy
# Or build only
npm run build:legacy
```