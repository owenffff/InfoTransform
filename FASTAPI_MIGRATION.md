# FastAPI Migration Guide

## Overview

We've created a FastAPI version of the application (`app_fastapi.py`) alongside the existing Flask app (`app.py`). Both applications share the same functionality, processors, and UI.

## Key Differences

### Flask vs FastAPI

| Feature | Flask (`app.py`) | FastAPI (`app_fastapi.py`) |
|---------|------------------|---------------------------|
| Port | 5000 | 8000 |
| Server | Werkzeug (dev) | Uvicorn (ASGI) |
| Async | Limited | Native async/await |
| API Docs | None | Auto-generated at `/docs` |
| Performance | Good | Better (async) |

## Running the Applications

### Flask App (Original)
```bash
python app.py
# Access at http://localhost:5000
```

### FastAPI App (New)
```bash
python app_fastapi.py
# Or directly with uvicorn:
uvicorn app_fastapi:app --reload --port 8000

# Access at http://localhost:8000
# API docs at http://localhost:8000/docs
```

## Features Comparison

Both applications support:
- ✅ Single file upload and processing
- ✅ Batch file upload
- ✅ ZIP file extraction and processing
- ✅ Vision processing (images, PDFs, documents)
- ✅ Audio processing (speech-to-text)
- ✅ Markdown download
- ✅ Batch results as combined markdown or ZIP
- ✅ Same UI and user experience

## FastAPI Advantages

1. **Better Performance**: Native async support for file I/O and processing
2. **Auto Documentation**: Interactive API docs at `/docs`
3. **Type Safety**: Better request/response validation
4. **Modern Python**: Uses latest Python features
5. **Production Ready**: Uvicorn is production-grade ASGI server

## Migration Notes

### Code Changes

1. **Route Definitions**:
   ```python
   # Flask
   @app.route('/upload', methods=['POST'])
   def upload_file():
   
   # FastAPI
   @app.post('/upload')
   async def upload_file(file: UploadFile = File(...)):
   ```

2. **File Uploads**:
   ```python
   # Flask
   file = request.files['file']
   
   # FastAPI
   file: UploadFile = File(...)
   ```

3. **Async File Operations**:
   ```python
   # FastAPI uses aiofiles for async I/O
   async with aiofiles.open(file_path, 'wb') as f:
       content = await file.read()
       await f.write(content)
   ```

4. **JSON Responses**:
   ```python
   # Flask
   return jsonify(result)
   
   # FastAPI
   return JSONResponse(content=result)
   ```

## Testing Both Apps

You can run both applications simultaneously for comparison:

1. Terminal 1: `python app.py` (Flask on port 5000)
2. Terminal 2: `python app_fastapi.py` (FastAPI on port 8000)

This allows you to:
- Compare performance
- Test feature parity
- Gradually migrate
- A/B test with users

## Next Steps

1. **Test thoroughly**: Ensure all features work identically
2. **Performance testing**: Compare response times and resource usage
3. **Update deployment**: Modify deployment scripts for Uvicorn
4. **Update documentation**: Point users to new endpoints
5. **Gradual migration**: Route traffic progressively to FastAPI

## Configuration

The FastAPI app uses the same hybrid configuration:
- Sensitive data in `.env`
- Application settings in `config.yaml`
- New setting: `server.uvicorn_port` (default: 8000)

## Troubleshooting

### Common Issues

1. **Port already in use**: Change port in `config.yaml`
2. **Import errors**: Ensure all dependencies are installed
3. **File upload issues**: Check `python-multipart` is installed
4. **Template not found**: Ensure you're running from project root

### Debug Mode

FastAPI runs with auto-reload by default when using:
```bash
python app_fastapi.py
```

For production, use:
```bash
uvicorn app_fastapi:app --host 0.0.0.0 --port 8000
