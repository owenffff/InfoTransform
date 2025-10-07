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

    Then, open the `.env` file and add your `OPENAI_API_KEY`. You can also adjust the port numbers if needed.

    ```env
    # .env
    OPENAI_API_KEY="your_openai_api_key_here"
    PORT=3000                          # Frontend Next.js port
    BACKEND_PORT=8000                  # Backend FastAPI port
    NEXT_PUBLIC_BACKEND_PORT=8000      # Must match BACKEND_PORT
    ```

### Running the Application

Once you've completed the setup, you can start the development server:

```bash
npm run dev
```

This single command will start both the backend API and the frontend application concurrently. The application will be available at `http://localhost:3000` (or whatever `PORT` you have set for the frontend).

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
│   ├── config.yaml           # Main configuration
│   ├── performance.yaml      # Performance settings
│   └── analysis_schemas.py   # Data extraction schemas
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
# Build CSS and JavaScript for production
npm run build

# Watch mode for development
npm run dev

# Build/watch individual assets
npm run build:css    # Build Tailwind CSS
npm run watch:css    # Watch CSS changes
npm run build:js     # Build JavaScript
npm run watch:js     # Watch JS changes

# Clean build artifacts
npm run clean
```

### Adding New document schemas

1. Edit `config/analysis_schemas.py`
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

### Main Configuration (`config/config.yaml`)

```yaml
app:
  name: "Information Transformer"
  version: "2.0.0"
  port: 8000

storage:
  upload_folder: "data/uploads"
  temp_extract_dir: "data/temp_extracts"
  max_file_size: 52428800  # 50MB
  max_zip_size: 104857600  # 100MB

models:
  ai_models:
    default_model: "gpt-4o-mini"
    models:
      gpt-4o-mini:
        max_tokens: 16000
        temperature: 0.1
      gpt-4o:
        max_tokens: 4096
        temperature: 0.1
```

### Performance Configuration (`config/performance.yaml`)

```yaml
processing:
  parallel_conversion:
    enabled: true
    max_workers: 4
  
  batch_processing:
    enabled: true
    batch_size: 5
    max_concurrent_batches: 2

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
