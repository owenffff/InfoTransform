# InfoTransform

Transform any file type into structured, actionable data using AI-powered analysis.

## Features

- **Multi-format Support**: Process images, PDFs, audio files, and documents
- **AI-Powered Analysis**: Extract structured data using customizable Pydantic models
- **Batch Processing**: Handle multiple files and ZIP archives efficiently
- **RESTful API**: Easy integration with FastAPI backend
- **Web Interface**: User-friendly interface for file uploads and downloads

## Project Structure

```
infotransform/
├── src/
│   └── infotransform/
│       ├── __init__.py
│       ├── main.py              # FastAPI application
│       ├── config.py            # Configuration management
│       ├── api/
│       │   ├── __init__.py
│       │   └── models.py        # Pydantic API models
│       ├── processors/
│       │   ├── __init__.py
│       │   ├── vision.py        # Vision/document processor
│       │   ├── audio.py         # Audio processor
│       │   ├── batch.py         # Batch processing
│       │   ├── structured_analyzer.py  # AI analysis
│       │   └── analysis_models.py      # Data extraction models
│       └── utils/
│           └── __init__.py
├── config/
│   ├── config.yaml              # Main configuration
│   └── .env.example             # Environment variables template
├── data/
│   ├── uploads/                 # Uploaded files (gitignored)
│   └── temp_extracts/           # Temporary extraction directory
├── static/                      # Frontend assets
│   ├── script.js
│   └── style.css
├── templates/
│   └── index.html               # Web interface
├── tests/
│   └── test_env_config.py       # Configuration tests
├── scripts/
│   └── demo.py                  # Demo script
├── docs/                        # Documentation
├── app.py                       # Application entry point
├── pyproject.toml               # Project dependencies
└── README.md
```

## Quick Start

### 1. Clone the repository

```bash
git clone <repository-url>
cd infotransform
```

### 2. Set up environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### 3. Configure environment variables

```bash
cp config/.env.example .env
# Edit .env and add your OpenAI API key
```

### 4. Run the application

```bash
python app.py
```

The application will be available at `http://localhost:8000`

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Required
OPENAI_API_KEY=your-api-key-here

# Optional
OPENAI_BASE_URL=https://api.openai.com/v1
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=your-azure-endpoint
PORT=8000
```

### Configuration File

Edit `config/config.yaml` to customize:
- Model settings
- Processing limits
- File type restrictions
- Analysis prompts

## API Documentation

Once the server is running, visit:
- Interactive API docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Usage Examples

### Web Interface

1. Open `http://localhost:8000` in your browser
2. Select files to upload
3. Choose an analysis model
4. Download results as Markdown or structured JSON

### API Usage

```python
import requests

# Transform a single file
with open('document.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/transform',
        files={'file': f},
        data={
            'model_key': 'content_compliance',
            'custom_instructions': 'Focus on regulatory requirements'
        }
    )
    result = response.json()
```

### Command Line Demo

```bash
python scripts/demo.py
```

## Development

### Running Tests

```bash
python tests/test_env_config.py
```

### Adding New Analysis Models

1. Define your Pydantic model in `src/infotransform/processors/analysis_models.py`
2. Add it to the `AVAILABLE_MODELS` dictionary
3. Optionally add a custom prompt in `config/config.yaml`

## Troubleshooting

### Common Issues

1. **"OpenAIModel.__init__() got an unexpected keyword argument 'model'"**
   - This error indicates the pydantic-ai library needs to be updated
   - The model name should be passed to OpenAIModel directly, not as a keyword argument

2. **File upload errors**
   - Check file size limits in `config/config.yaml`
   - Ensure the file type is supported

3. **API key errors**
   - Verify your OpenAI API key is set correctly in `.env`
   - Check if you need to set a custom base URL

## License

[Your License Here]

## Contributing

[Contributing guidelines]
