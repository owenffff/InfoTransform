# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
```bash
# Start the FastAPI server
python app.py
# Server runs on http://localhost:8000 with auto-reload
```

### Running Tests
```bash
# Run configuration tests
python tests/test_env_config.py

# Run all tests
python -m pytest tests/
```

### Development Setup
```bash
# Install in development mode
pip install -e .

# Copy environment template
cp .env.example .env
# Edit .env and add your OpenAI API key
```

## Architecture Overview

### Core Components

**FastAPI Application** (`src/infotransform/main.py`):
- Main web server handling file uploads and API requests
- Processors are initialized at startup via lifespan context manager
- Routes for single file, batch processing, and structured analysis

**Configuration System** (`src/infotransform/config.py` + `config/config.yaml`):
- Hybrid configuration: sensitive data in `.env`, settings in YAML
- Environment variables override YAML values where applicable
- Centralized access via config singleton

**Processing Pipeline**:
1. **Vision/Audio Processors** → Convert files to markdown
2. **Structured Analyzer** → Extract structured data using Pydantic AI
3. **Batch Processor** → Handle multiple files and ZIP archives

### Key Processors

**VisionProcessor** (`src/infotransform/processors/vision.py`):
- Handles images, PDFs, documents via OpenAI vision models
- Converts visual content to structured markdown

**AudioProcessor** (`src/infotransform/processors/audio.py`):
- Transcribes audio files using Whisper
- Supports MP3, WAV, M4A, FLAC, OGG, WebM

**StructuredAnalyzer** (`src/infotransform/processors/structured_analyzer.py`):
- Uses Pydantic AI agents to extract structured data from markdown
- Supports streaming responses and concurrent batch processing
- Analysis models defined in `analysis_models.py`

**BatchProcessor** (`src/infotransform/processors/batch.py`):
- Handles ZIP archives and multiple file uploads
- Manages temporary file extraction and cleanup

### Analysis Models

Analysis models are Pydantic schemas in `src/infotransform/processors/analysis_models.py`:
- `AVAILABLE_MODELS` dict maps keys to model classes
- Custom prompts configured in `config.yaml` under `prompts.analysis.model_specific`
- Models support streaming and batch analysis

### Configuration Structure

**Environment Variables** (`.env`):
- `OPENAI_API_KEY` - Required for AI processing
- `OPENAI_BASE_URL` - Optional custom endpoint
- `PORT` - Server port (default: 8000)

**YAML Configuration** (`config/config.yaml`):
- AI model settings, prompts, file limits
- Processing timeouts and concurrent limits
- Feature flags for streaming, caching, etc.

## Development Patterns

### Adding New Analysis Models
1. Define Pydantic model in `analysis_models.py`
2. Add to `AVAILABLE_MODELS` dictionary
3. Optional: Add custom system prompt in `config.yaml`

### File Processing Flow
1. File upload → temporary storage in `data/uploads/`
2. Format detection → route to appropriate processor
3. Markdown conversion → structured analysis (if requested)
4. Results returned → temporary files cleaned up

### Error Handling
- Processors return standardized `{'success': bool, 'error': str, 'content': str}` format
- FastAPI exception handlers provide consistent error responses
- Timeout handling for both single files and batch processing

### Concurrent Processing
- Batch analysis uses semaphore-controlled concurrency
- Configurable limits in `config.yaml` under `processing.analysis.max_concurrent_analyses`
- Streaming responses support real-time updates

## Important Files

- `app.py` - Application entry point
- `src/infotransform/main.py` - FastAPI application and routes
- `src/infotransform/config.py` - Configuration loader
- `config/config.yaml` - Application settings
- `src/infotransform/processors/` - Core processing logic
- `static/` - Frontend assets
- `templates/index.html` - Web interface