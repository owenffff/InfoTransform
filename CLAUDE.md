# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

InfoTransform is a document processing application that transforms various file types (images, PDFs, documents, audio) into structured data using AI-powered analysis. The application uses FastAPI for the backend, vanilla JavaScript with Tailwind CSS for the frontend, and integrates OpenAI's GPT models through Pydantic AI.

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
- **Modular JavaScript**: ES6 modules in `src/js/modules/` (api, dom, events, state, ui)
- **Build System**: Tailwind CSS + esbuild for bundling
- **Static Assets**: Fonts and images in `frontend/static/`
- **Templates**: Jinja2 templates in `frontend/templates/`

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
# Install Node dependencies
npm install

# Build all frontend assets
npm run build

# Development mode (watches files and runs backend with uv)
npm run dev

# Watch frontend only (CSS + JS)
npm run dev:frontend

# Individual build commands
npm run build:css    # Build Tailwind CSS
npm run build:js     # Bundle JavaScript
npm run watch:css    # Watch CSS changes
npm run watch:js     # Watch JS changes

# Clean build artifacts
npm run clean
```

### Testing
```bash
# Run tests (when implemented - currently no test framework set up)
# uv run pytest tests/
```

## Key API Endpoints

- `GET /` - Main web interface
- `POST /api/transform` - Process files with streaming response
- `GET /api/models` - List available analysis models  
- `POST /api/download-results` - Export results as Excel/CSV
- `GET /docs` - Swagger API documentation
- `GET /redoc` - ReDoc API documentation

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

- **Environment Variables**: Copy `.env.example` to `.env` and set:
  - `OPENAI_API_KEY` (required)
  - `PORT`, `UPLOAD_FOLDER`, `TEMP_EXTRACT_DIR` (optional)
  
- **Main Config**: `config/config.yaml` - App settings, storage paths, model configurations
- **Performance**: `config/performance.yaml` - Parallel processing, batch sizes, monitoring

## File Processing Pipeline

1. **Upload**: Files uploaded to `data/uploads/`
2. **Conversion**: Parallel markdown conversion using AsyncMarkdownConverter
3. **AI Analysis**: Batch processing through Pydantic AI agents
4. **Streaming**: Results streamed back via Server-Sent Events
5. **Cleanup**: Automatic file lifecycle management

## Important Patterns

- **Streaming Architecture**: Uses SSE for real-time progress updates
- **Parallel Processing**: Configurable workers for markdown conversion
- **Batch AI Processing**: Groups files for efficient API calls
- **Error Handling**: Graceful degradation with fallback processors
- **File Lifecycle**: Automatic cleanup of temporary files

## Dependencies

- **Python**: FastAPI, Pydantic AI, markitdown, OpenAI, pandas, uvicorn
- **Node.js**: Tailwind CSS, esbuild, concurrently
- **Package Managers**: UV for Python, npm for Node.js

## Performance Considerations

- Default parallel workers: 4 for markdown conversion
- Default batch size: 5 files for AI processing
- Configurable via `config/performance.yaml`
- Monitor slow operations threshold: 5 seconds

## Security Notes

- API keys stored in `.env` file (never commit)
- CORS configured for all origins (restrict in production)
- File size limits: 50MB single file, 100MB for ZIP archives
- Automatic cleanup of uploaded files after processing