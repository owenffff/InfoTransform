# 🔄 Information Transformer

A powerful web application that transforms any file type (images, documents, audio) into structured, actionable data using AI. Built with Microsoft's Markitdown library and Pydantic AI for intelligent data extraction.

## ✨ Features

### Core Transformation Pipeline
- **🔄 Two-Stage Processing**: Files → Markdown → Structured Data
- **🤖 AI-Powered Analysis**: Uses Pydantic AI for intelligent data extraction
- **📊 Multiple Analysis Models**: 
  - Content Compliance: Policy violation detection
  - Document Metadata: Extract titles, authors, summaries
  - Technical Analysis: Code snippets, complexity assessment

### File Processing Capabilities
- **🖼️ Image OCR**: Extract text from images (JPG, PNG, GIF, BMP, WebP)
- **📄 Document Processing**: Convert PDFs, DOCX, PPTX, and XLSX files
- **🎤 Speech-to-Text**: Transcribe audio files (MP3, WAV, M4A, FLAC, OGG, WebM)
- **📦 Batch Processing**: Process multiple files at once or upload ZIP archives
- **⚡ Async Processing**: Fast concurrent processing with progress tracking

### Output Options
- **📋 Structured JSON**: Export analysis results as JSON
- **📊 CSV Export**: Download results in spreadsheet format
- **📈 Summary Statistics**: Aggregate insights across multiple files
- **🎯 Custom Instructions**: Fine-tune analysis with specific requirements

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- An OpenAI API key (or compatible service credentials)

### Installation

1. **Clone or download this project**

2. **Install dependencies using uv (recommended)**:
   ```bash
   uv sync
   ```

   Or using pip:
   ```bash
   pip install -e .
   ```

3. **Configure your API credentials**:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your credentials:
   ```env
   API_KEY=your-api-key-here
   BASE_URL=https://api.openai.com/v1  # Or your custom endpoint
   MODEL_NAME=gpt-4-vision-preview     # Or your preferred model
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Open your browser** and navigate to:
   ```
   http://localhost:8000
   ```

   API documentation is available at:
   ```
   http://localhost:8000/docs
   ```

## 🔧 Configuration

The application uses a unified `config.yaml` file for all settings, with sensitive data in `.env`.

### Environment Variables (.env)

| Variable | Description | Default |
|----------|-------------|---------|
| `API_KEY` | Your OpenAI API key (required) | - |
| `BASE_URL` | API endpoint URL | `https://api.openai.com/v1` |
| `OPENAI_BASE_URL` | Custom OpenAI endpoint (optional) | - |
| `DOCINTEL_ENDPOINT` | Azure Document Intelligence endpoint | None |
| `PORT` | Port to run the server on | `8000` |

### Configuration File (config.yaml)

The `config.yaml` file contains:
- **AI Models**: Configure GPT-4, GPT-4-mini, or custom models
- **Analysis Prompts**: Customize prompts for different analysis types
- **Processing Settings**: Timeouts, concurrency, file size limits
- **Feature Flags**: Enable/disable specific features

### Vision Prompt Configuration

The default vision prompt is optimized to:
- Extract all text from screenshots, documents, and text-heavy images
- Provide detailed descriptions for images without text
- Handle mixed content (both text and visual elements)

You can customize the vision prompt by setting the `VISION_PROMPT` environment variable in your `.env` file. The default prompt intelligently handles both OCR and image description tasks.

### Azure Document Intelligence (Optional)

For advanced document processing, you can optionally configure Azure Document Intelligence:

1. **Set up Azure Document Intelligence**:
   - Create an Azure Cognitive Services resource
   - Get your endpoint URL (e.g., `https://your-resource.cognitiveservices.azure.com`)

2. **Configure in `.env`**:
   ```env
   DOCINTEL_ENDPOINT=https://your-resource.cognitiveservices.azure.com
   ```

3. **Benefits**:
   - Better structured data extraction from PDFs
   - Advanced table recognition
   - Form field extraction
   - Layout analysis for complex documents

When configured, Markitdown will automatically use Document Intelligence for supported document types while still using the LLM for images and other content.

### Using Alternative API Providers

This MVP works with any OpenAI-compatible endpoint. Examples:

- **Local Models (Ollama, LM Studio)**: Set `BASE_URL` to your local endpoint
- **Alternative Providers**: Many services offer OpenAI-compatible endpoints
- **Proxy Services**: Use services that provide OpenAI-compatible interfaces for other models

## 📁 Project Structure

```
information-transformer/
├── app.py                    # FastAPI application
├── config.yaml              # Unified configuration
├── config.py                # Configuration loader
├── processors/              # File processing modules
│   ├── vision.py           # Image/document processor
│   ├── audio.py            # Audio transcription
│   ├── batch.py            # Batch processing handler
│   ├── structured_analyzer.py  # Pydantic AI analyzer
│   └── analysis_models.py  # Pydantic models for extraction
├── templates/              # HTML templates
│   └── index.html         # Main web interface
├── static/                # Static assets
│   ├── style.css         # Styling
│   └── script.js         # Frontend JavaScript
├── uploads/              # Temporary file storage
├── .env.example         # Example environment variables
└── README.md           # This file
```

## 🎯 Usage

### Information Transformation Workflow

1. **Upload Files**: 
   - Drag and drop files or click to browse
   - Support for single or multiple files
   - ZIP archives automatically extracted

2. **Configure Analysis**:
   - Select an analysis model (Compliance, Metadata, Technical)
   - Choose AI model (GPT-4, GPT-4-mini, etc.)
   - Add custom instructions (optional)

3. **Transform**:
   - Click "Transform to Structured Data"
   - Watch real-time progress for batch processing

4. **View Results**:
   - **Structured Data Tab**: Formatted, easy-to-read results
   - **Raw Results Tab**: Complete JSON output
   - **Summary Section**: Aggregate statistics for batch processing

5. **Export**:
   - **Download JSON**: Complete structured data
   - **Download CSV**: Spreadsheet-compatible format

### Batch Processing Features
- **Concurrent Processing**: Files are processed in parallel for speed
- **Progress Tracking**: See real-time progress during batch operations
- **Structure Preservation**: ZIP file directory structure is maintained
- **Mixed File Types**: Process images, documents, and audio in one batch
- **Error Handling**: Failed files don't stop the batch; see summary of successes/failures

### Supported File Types

- **Images**: JPG, PNG, GIF, BMP, WebP
- **Documents**: PDF, DOCX, PPTX, XLSX
- **Audio**: MP3, WAV, M4A, FLAC, OGG, WebM
- **Archives**: ZIP (for batch processing)

## 🛠️ Development

### Running in Development Mode

The app runs in development mode by default with auto-reload enabled:

```bash
python app.py
```

### Adding New File Types

1. Update `Config.ALLOWED_*_EXTENSIONS` in `config.py`
2. Modify the processor's `is_supported_file` method
3. Update the file input accept attribute in `index.html`

### Customizing the UI

- Styles are in `static/style.css`
- JavaScript logic is in `static/script.js`
- HTML template is in `templates/index.html`

## ⚠️ Limitations

- Maximum file size: 16MB per file
- Maximum ZIP size: 100MB for batch uploads
- Processing time depends on file size and API response time
- API rate limits apply based on your provider
- Some complex layouts may not convert perfectly
- Concurrent processing limited to 5 files at a time (configurable)

## 🔒 Security Notes

- API keys are stored locally in `.env` (never commit this file)
- Files are temporarily stored and immediately deleted after processing
- No data is permanently stored on the server

## 🐛 Troubleshooting

### "API_KEY is required" Error
- Make sure you've created a `.env` file with your API key
- Check that the `.env` file is in the same directory as `app.py`

### "Cannot connect to server" Error
- Ensure the FastAPI server is running
- Check if port 8000 is available

### Processing Fails
- Verify your API key is valid
- Check if the BASE_URL is correct
- Ensure you have credits/quota with your API provider

## 📝 License

This is an MVP project for demonstration purposes. Please ensure you comply with the terms of service of your API provider.

## 🙏 Acknowledgments

- Built with [Markitdown](https://github.com/microsoft/markitdown) by Microsoft
- Uses OpenAI's GPT-4 Vision and Whisper APIs (or compatible alternatives)
