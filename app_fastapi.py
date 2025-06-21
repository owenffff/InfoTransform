"""
FastAPI application for Markitdown MVP
"""

import os
import asyncio
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
import aiofiles
import uvicorn

from config import config
from processors import VisionProcessor, AudioProcessor, BatchProcessor


# Initialize FastAPI app
app = FastAPI(
    title="Markitdown MVP",
    description="OCR and Speech-to-Text using Markitdown with OpenAI-compatible APIs",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Create necessary directories
os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(config.TEMP_EXTRACT_DIR, exist_ok=True)

# Initialize processors
vision_processor = None
audio_processor = None
batch_processor = None


def init_processors():
    """Initialize processors with error handling"""
    global vision_processor, audio_processor, batch_processor
    try:
        config.validate()
        vision_processor = VisionProcessor()
        audio_processor = AudioProcessor()
        batch_processor = BatchProcessor(vision_processor, audio_processor)
        return True
    except Exception as e:
        print(f"Error initializing processors: {e}")
        return False


def secure_filename(filename: str) -> str:
    """Secure a filename by removing potentially dangerous characters"""
    import re
    # Remove any path separators
    filename = filename.replace('/', '_').replace('\\', '_')
    # Keep only alphanumeric, dash, underscore, and dot
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    return filename


@app.on_event("startup")
async def startup_event():
    """Initialize processors on startup"""
    if init_processors():
        print("✅ Processors initialized successfully")
    else:
        print("❌ Failed to initialize processors. Please check your configuration.")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the main page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Handle file upload and processing"""
    if not file or file.filename == '':
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Secure the filename
    filename = secure_filename(file.filename)
    file_path = os.path.join(config.UPLOAD_FOLDER, filename)
    
    try:
        # Save the uploaded file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Determine which processor to use
        if vision_processor and vision_processor.is_supported_file(filename):
            result = vision_processor.process_file(file_path)
        elif audio_processor and audio_processor.is_supported_file(filename):
            result = audio_processor.process_file(file_path)
        else:
            result = {
                'success': False,
                'error': f'Unsupported file type: {filename}'
            }
        
        return JSONResponse(content=result)
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={'success': False, 'error': str(e)}
        )
    finally:
        # Clean up the uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)


@app.post("/download")
async def download_markdown(request: Request):
    """Generate and download markdown file"""
    data = await request.json()
    content = data.get('content', '')
    filename = data.get('filename', 'output.md')
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as tmp_file:
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    # Generate download filename
    base_name = os.path.splitext(filename)[0]
    download_name = f"{base_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    return FileResponse(
        path=tmp_path,
        filename=download_name,
        media_type='text/markdown'
    )


@app.post("/upload-batch")
async def upload_batch(files: List[UploadFile] = File(...)):
    """Handle multiple file uploads and batch processing"""
    if not files or all(f.filename == '' for f in files):
        raise HTTPException(status_code=400, detail="No files provided")
    
    # Save uploaded files temporarily
    saved_files = []
    files_info = []
    
    try:
        for file in files:
            if file.filename:
                filename = secure_filename(file.filename)
                file_path = os.path.join(config.UPLOAD_FOLDER, filename)
                
                # Save file asynchronously
                async with aiofiles.open(file_path, 'wb') as f:
                    content = await file.read()
                    await f.write(content)
                
                saved_files.append(file_path)
                
                # Check if it's a ZIP file
                if batch_processor.is_zip_file(filename):
                    # Check ZIP file size
                    if os.path.getsize(file_path) > config.MAX_ZIP_SIZE:
                        raise Exception(f"ZIP file {filename} exceeds maximum size of {config.MAX_ZIP_SIZE // (1024*1024)}MB")
                    
                    # Extract ZIP and get file info
                    extracted_files = batch_processor.extract_zip_with_structure(file_path)
                    files_info.extend(extracted_files)
                else:
                    # Regular file
                    files_info.append({
                        'path': filename,
                        'full_path': file_path,
                        'filename': filename
                    })
        
        # Process files asynchronously
        result = await batch_processor.process_multiple_files(files_info)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={'success': False, 'error': str(e)}
        )
    finally:
        # Clean up uploaded files
        for file_path in saved_files:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Clean up extracted files
        batch_processor.cleanup_temp_dirs()


@app.post("/download-batch")
async def download_batch(request: Request):
    """Download batch processing results as combined markdown or ZIP"""
    data = await request.json()
    results = data.get('results', [])
    format_type = data.get('format', 'markdown')
    
    if not results:
        raise HTTPException(status_code=400, detail="No results to download")
    
    try:
        if format_type == 'zip':
            # Create ZIP archive with individual markdown files
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_file:
                zip_path = batch_processor.create_zip_archive(results, tmp_file.name)
            
            download_name = f"markitdown_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            return FileResponse(
                path=zip_path,
                filename=download_name,
                media_type='application/zip'
            )
        else:
            # Create combined markdown file
            combined_content = batch_processor.create_combined_markdown(results)
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as tmp_file:
                tmp_file.write(combined_content)
                tmp_path = tmp_file.name
            
            download_name = f"markitdown_combined_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            return FileResponse(
                path=tmp_path,
                filename=download_name,
                media_type='text/markdown'
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "processors_initialized": vision_processor is not None and audio_processor is not None,
        "server": "FastAPI"
    }


# Custom exception handler for better error responses
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": str(exc)}
    )


if __name__ == "__main__":
    # Run the FastAPI app with Uvicorn
    print(f"🚀 Starting FastAPI server on http://localhost:{config.UVICORN_PORT}")
    print(f"📚 API documentation available at http://localhost:{config.UVICORN_PORT}/docs")
    
    uvicorn.run(
        "app_fastapi:app",
        host="0.0.0.0",
        port=config.UVICORN_PORT,
        reload=True,
        log_level="info"
    )
