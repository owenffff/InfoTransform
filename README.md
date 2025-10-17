# 🔄 InfoTransform

Transform any file type into structured, actionable data using AI-powered analysis.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Node.js](https://img.shields.io/badge/node.js-18+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal.svg)
![License](https://img.shields.io/badge/license-MIT-purple.svg)

## 📋 Overview

InfoTransform is a powerful document processing tool that converts various file formats (images, PDFs, documents, audio files) into structured data using AI. It leverages OpenAI's GPT models and Pydantic for intelligent content extraction and analysis.

### ✨ Key Features

- **Multi-format Support**: Process images (JPG, PNG, etc.), PDFs, Office documents (DOCX, PPTX, XLSX), audio files, and more
- **AI-Powered Analysis**: Extract structured data using customizable AI models
- **Batch Processing**: Handle multiple files simultaneously with progress tracking
- **Streaming Results**: Real-time processing updates for large batches
- **Custom Schemas**: Define your own data extraction schemas
- **Export Options**: Download results as Excel or CSV files
- **Modern UI**: Clean, responsive interface built with Tailwind CSS

## 🚀 Getting Started

This guide will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

*   **Node.js**: Version 18 or higher.
*   **Python**: Version 3.11 or higher.
*   **uv**: A fast Python package installer. You can install it by following the instructions [here](https://github.com/astral-sh/uv).

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/owenffff/InfoTransform.git
    cd InfoTransform
    ```

2.  **Set up the Backend (Python):**

    ```bash
    # Create a virtual environment
    uv venv

    # Activate the virtual environment
    # On macOS/Linux:
    source .venv/bin/activate
    # On Windows (Command Prompt):
    .venv\Scripts\activate.bat
    # On Windows (PowerShell):
    .venv\Scripts\Activate.ps1

    # Install Python dependencies
    uv sync
    ```

3.  **Set up the Frontend (Node.js):**

    ```bash
    # Install Node.js dependencies
    npm install
    ```

4.  **Configure Environment Variables:**

    Create a `.env` file in the root of the project by copying the example file:

    ```bash
    # On macOS/Linux:
    cp .env.example .env

    # On Windows (Command Prompt):
    copy .env.example .env

    # On Windows (PowerShell):
    Copy-Item .env.example .env
    ```

    Then, open the `.env` file and add your `OPENAI_API_KEY`. You can also adjust the port numbers and environment if needed.

    ```env
    # .env
    OPENAI_API_KEY="your_openai_api_key_here"
    PORT=3000                          # Frontend Next.js port
    BACKEND_PORT=8000                  # Backend FastAPI port
    NEXT_PUBLIC_BACKEND_PORT=8000      # Must match BACKEND_PORT
    ENV=development                    # Environment: development, staging, or production
    ```

### Running the Application

#### Development Mode

For local development with hot-reloading:

```bash
npm run dev
```

This single command will start both the backend API and the frontend application concurrently with live reloading. The application will be available at `http://localhost:3000`.

#### Production Mode

For production deployment:

```bash
# 1. Build the frontend
npm run build

# 2. Start in production mode
npm run start
```

**Environment-Specific Deployment:**

You can run the application in different environments (development, staging, production):

```bash
# Production (uses config/config.production.yaml)
npm run start:production

# Staging (uses config/config.staging.yaml)
npm run start:staging

# Development with production build (uses config/config.development.yaml)
npm run start:development
```

Each environment command:
- Automatically loads the correct configuration file
- Starts both the Next.js frontend and FastAPI backend
- Uses optimized production builds for better performance

## 📁 Project Structure

```
InfoTransform/
├── backend/                    # Python backend code
│   └── infotransform/
│       ├── api/               # API endpoints
│       ├── processors/        # File processors
│       └── utils/             # Utility functions
├── frontend/                   # Frontend assets
│   ├── src/                   # Source files
│   │   ├── css/              # Tailwind CSS input
│   │   └── js/               # JavaScript source
│   ├── dist/                  # Built files (gitignored)
│   │   ├── css/              # Compiled CSS
│   │   └── js/               # Bundled JavaScript
│   └── templates/             # HTML templates
├── config/                     # Configuration files
│   ├── config.yaml           # Default configuration
│   ├── config.development.yaml   # Development environment config
│   ├── config.staging.yaml      # Staging environment config
│   ├── config.production.yaml   # Production environment config
│   ├── performance.yaml      # Performance settings
│   └── document_schemas.py   # Data extraction schemas
├── data/                      # Data directories
│   ├── uploads/              # Uploaded files (temporary)
│   └── temp_extracts/        # Extracted files (temporary)
├── docs/                      # Documentation
├── tests/                     # Test files
├── .env.example              # Environment variables template
├── app.py                    # Application entry point
├── package.json              # Node.js dependencies
├── pyproject.toml            # Python dependencies
└── README.md                 # This file
```

## 🛠️ Development

### Available NPM Scripts

```bash
# Development
npm run dev                   # Start development server (hot-reload enabled)

# Production
npm run build                 # Build frontend for production
npm run start                 # Start production server (default: production env)
npm run start:production      # Start with production config
npm run start:staging         # Start with staging config
npm run start:development     # Start with development config

# Utilities
npm run clean                 # Clean build artifacts
```

### Adding New document schemas

1. Edit `config/document_schemas.py`
2. Add your model configuration:
   ```python
   "your_model_key": {
       "name": "Your Model Name",
       "description": "Model description",
       "fields": {
           "field_name": {
               "type": "string",
               "description": "Field description",
               "required": True
           }
       }
   }
   ```

### Supported File Types

- **Images**: JPG, JPEG, PNG, GIF, BMP, WEBP
- **Documents**: PDF, DOCX, PPTX, XLSX, MD, TXT
- **Audio**: MP3, WAV, M4A, FLAC, OGG, WEBM
- **Archives**: ZIP (for batch processing)

## 🔧 Configuration

InfoTransform uses a flexible configuration system with environment-specific settings.

### Environment Configuration

The application supports three environments: **development**, **staging**, and **production**. Each environment can have its own configuration file:

- `config/config.yaml` - Default/fallback configuration
- `config/config.development.yaml` - Development-specific settings
- `config/config.staging.yaml` - Staging-specific settings
- `config/config.production.yaml` - Production-specific settings

**How it works:**
1. Set the `ENV` environment variable (defaults to `development`)
2. The backend automatically loads `config/config.{ENV}.yaml`
3. If no environment-specific file exists, falls back to `config/config.yaml`

**Example configurations for different environments:**

```yaml
# config/config.production.yaml
app:
  name: "Information Transformer"
  environment: "production"    # Used by application logic

ai_pipeline:
  structured_analysis:
    default_model: "openai.gpt-5-2025-08-07"  # Use premium model in production

processing:
  analysis:
    max_concurrent: 20         # More workers for production
  conversion:
    max_concurrent: 20
```

```yaml
# config/config.development.yaml
app:
  name: "Information Transformer"
  environment: "development"

ai_pipeline:
  structured_analysis:
    default_model: "openai.gpt-5-mini-2025-08-07"  # Use cheaper model for dev

processing:
  analysis:
    max_concurrent: 5          # Fewer workers for local dev
  conversion:
    max_concurrent: 5
```

### Performance Configuration (`config/performance.yaml`)

Controls processing performance across all environments:

```yaml
markdown_conversion:
  max_workers: 10              # Parallel markdown conversion
  timeout_per_file: 120

ai_processing:
  batch_size: 10               # Files per AI batch
  max_concurrent_batches: 3
  timeout_per_batch: 300

monitoring:
  enable_metrics: true
  slow_operation_threshold: 5.0
```

## 📚 API Documentation

Once the application is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key Endpoints

- `GET /` - Main web interface
- `POST /api/transform` - Transform single file
- `POST /api/transform` - Stream transformation for multiple files
- `GET /api/models` - List available document schemas
- `POST /api/download-results` - Download results as Excel/CSV

## 🐛 Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Ensure you've activated the virtual environment
   - Run `uv sync` to install all dependencies

2. **Frontend assets not loading**
   - Run `npm run build` to compile assets
   - Check that `frontend/dist/` directory exists

3. **API key errors**
   - Verify your `.env` file contains valid API keys
   - Ensure the `.env` file is in the project root

4. **File upload failures**
   - Check file size limits in configuration
   - Ensure `data/uploads/` directory exists and is writable

5. **Windows-specific issues**
   - If `npm run dev` fails, ensure you have `uv` installed and in PATH
   - On PowerShell, you may need to run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
   - If you get "command not found" errors, try running commands with explicit `npx` prefix
   - For WSL users: ensure all files use LF line endings, not CRLF

### Platform-Specific Notes

#### Windows
- The project uses `cross-env` to ensure environment variables work across platforms
- Make sure Python is accessible as `python` (not just `python3`)
- If using Windows Command Prompt, some npm scripts may need adjustments

#### WSL (Windows Subsystem for Linux)
- Follow Linux instructions for setup
- Ensure file permissions are correct: `chmod +x app.py`
- May need to install additional system dependencies for markitdown

#### macOS/Linux
- No special considerations needed
- Ensure execute permissions on Python files if needed

### Environment Configuration Issues

If you need to manually control which config is loaded:

```bash
# macOS/Linux:
export ENV=production
npm run start

# Windows Command Prompt:
set ENV=production
npm run start

# Windows PowerShell:
$env:ENV="production"
npm run start

# Or add to .env file:
ENV=production
```

The backend will log which config file it loads on startup.

### Debug Mode

For detailed logging, set the environment variable:
```bash
# macOS/Linux:
export QUIET_MODE=false

# Windows Command Prompt:
set QUIET_MODE=false

# Windows PowerShell:
$env:QUIET_MODE="false"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint for JavaScript
- Write tests for new features
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- UI powered by [Tailwind CSS](https://tailwindcss.com/)
- AI capabilities via [OpenAI](https://openai.com/) and [Pydantic AI](https://ai.pydantic.dev/)
- Document processing with [markitdown](https://github.com/microsoft/markitdown)

## 📞 Support

For issues and feature requests, please use the [GitHub Issues](https://github.com/yourusername/InfoTransform/issues) page.

---

Made with ❤️ by the InfoTransform team
