# 📝 Markitdown MVP - OCR & Speech-to-Text

A web-based MVP that uses Microsoft's Markitdown library to convert images, documents, and audio files to Markdown format. Supports any OpenAI-compatible API endpoint for maximum flexibility.

## ✨ Features

- **🖼️ Image OCR**: Extract text from images (JPG, PNG, GIF, BMP, WebP)
- **📄 Document Processing**: Convert PDFs, DOCX, PPTX, and XLSX files to Markdown
- **🎤 Speech-to-Text**: Transcribe audio files (MP3, WAV, M4A, FLAC, OGG, WebM)
- **🔌 OpenAI-Compatible**: Works with any OpenAI-compatible API endpoint
- **💾 Download Results**: Save processed content as Markdown files
- **🎨 Clean Web Interface**: Simple drag-and-drop file upload

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
   http://localhost:5000
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_KEY` | Your OpenAI API key (required) | - |
| `BASE_URL` | API endpoint URL | `https://api.openai.com/v1` |
| `MODEL_NAME` | Vision model to use | `gpt-4-vision-preview` |
| `WHISPER_MODEL` | Audio transcription model | `whisper-1` |
| `VISION_PROMPT` | Custom prompt for image analysis | Smart OCR + description prompt |
| `DOCINTEL_ENDPOINT` | Azure Document Intelligence endpoint | None (uses LLM-only mode) |
| `FLASK_PORT` | Port to run the server on | `5000` |

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
markitdown-mvp/
├── app.py              # Flask application
├── config.py           # Configuration management
├── processors/         # File processing modules
│   ├── vision.py       # Image/document processor
│   └── audio.py        # Audio transcription
├── templates/          # HTML templates
│   └── index.html      # Main web interface
├── static/             # Static assets
│   ├── style.css       # Styling
│   └── script.js       # Frontend JavaScript
├── uploads/            # Temporary file storage
├── .env.example        # Example configuration
└── README.md           # This file
```

## 🎯 Usage

1. **Upload a File**: Drag and drop or click to browse
2. **Wait for Processing**: The file will be automatically processed
3. **View Results**: See the Markdown output in the preview area
4. **Download**: Click "Download Markdown" to save the result

### Supported File Types

- **Images**: JPG, PNG, GIF, BMP, WebP
- **Documents**: PDF, DOCX, PPTX, XLSX
- **Audio**: MP3, WAV, M4A, FLAC, OGG, WebM

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

- Maximum file size: 16MB
- Processing time depends on file size and API response time
- API rate limits apply based on your provider
- Some complex layouts may not convert perfectly

## 🔒 Security Notes

- API keys are stored locally in `.env` (never commit this file)
- Files are temporarily stored and immediately deleted after processing
- No data is permanently stored on the server

## 🐛 Troubleshooting

### "API_KEY is required" Error
- Make sure you've created a `.env` file with your API key
- Check that the `.env` file is in the same directory as `app.py`

### "Cannot connect to server" Error
- Ensure the Flask server is running
- Check if port 5000 is available

### Processing Fails
- Verify your API key is valid
- Check if the BASE_URL is correct
- Ensure you have credits/quota with your API provider

## 📝 License

This is an MVP project for demonstration purposes. Please ensure you comply with the terms of service of your API provider.

## 🙏 Acknowledgments

- Built with [Markitdown](https://github.com/microsoft/markitdown) by Microsoft
- Uses OpenAI's GPT-4 Vision and Whisper APIs (or compatible alternatives)
