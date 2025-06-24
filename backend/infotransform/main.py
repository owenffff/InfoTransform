"""
FastAPI application for InfoTransform
"""

import os
import asyncio
import tempfile
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import pandas as pd
from io import BytesIO

from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Depends, status
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse, StreamingResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
import aiofiles
import uvicorn

from infotransform.config import config
from infotransform.processors import VisionProcessor, AudioProcessor, BatchProcessor, StructuredAnalyzer
from infotransform.api.models import FileTransformResult, TransformResponse
from infotransform.api.streaming_v2 import transform_stream_v2, shutdown_processor

# Setup logger
logger = logging.getLogger(__name__)

# Initialize processors
vision_processor = None
audio_processor = None
batch_processor = None
structured_analyzer = None


def init_processors():
    """Initialize processors with error handling"""
    global vision_processor, audio_processor, batch_processor, structured_analyzer
    try:
        config.validate()
        vision_processor = VisionProcessor()
        audio_processor = AudioProcessor()
        batch_processor = BatchProcessor(vision_processor, audio_processor)
        structured_analyzer = StructuredAnalyzer()
        return True
    except Exception as e:
        print(f"Error initializing processors: {e}")
        return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    # Startup
    if init_processors():
        print("✅ Processors initialized successfully")
    else:
        print("❌ Failed to initialize processors. Please check your configuration.")
    
    yield
    
    # Shutdown
    await shutdown_processor()  # Shutdown the optimized processor
    print("✅ Cleanup completed")


# Initialize FastAPI app
app = FastAPI(
    title=config.get('app.name', 'Information Transformer'),
    description=config.get('app.description', 'Transform any file type into structured, actionable data'),
    version=config.get('app.version', '2.0.0'),
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get paths relative to project root
project_root = Path(__file__).parent.parent.parent

# Mount static files
static_path = project_root / "frontend" / "dist"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Setup templates
templates_path = project_root / "frontend" / "templates"
templates = Jinja2Templates(directory=str(templates_path))

# Create necessary directories
os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(config.TEMP_EXTRACT_DIR, exist_ok=True)


def secure_filename(filename: str) -> str:
    """Secure a filename by removing potentially dangerous characters"""
    import re
    # Remove any path separators
    filename = filename.replace('/', '_').replace('\\', '_')
    # Keep only alphanumeric, dash, underscore, and dot
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    return filename


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the main page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/test-form", response_class=HTMLResponse)
async def test_form():
    """Serve test form page"""
    test_form_path = project_root / "test_form_upload.html"
    if test_form_path.exists():
        with open(test_form_path, "r") as f:
            return HTMLResponse(content=f.read())
    else:
        raise HTTPException(status_code=404, detail="Test form not found")


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
            
            download_name = f"infotransform_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
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
            
            download_name = f"infotransform_combined_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            return FileResponse(
                path=tmp_path,
                filename=download_name,
                media_type='text/markdown'
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/models")
async def list_analysis_models():
    """List available analysis models"""
    if not structured_analyzer:
        raise HTTPException(status_code=503, detail="Analyzer not initialized")
    
    return {
        "models": structured_analyzer.get_available_models(),
        "ai_models": structured_analyzer.get_available_ai_models()
    }


@app.post("/api/transform")
async def transform_file(
    file: UploadFile = File(...),
    model_key: str = Form(...),
    custom_instructions: Optional[str] = Form(""),
    ai_model: Optional[str] = Form(None)
):
    """Transform a single file to structured data"""
    # Debug logging
    print(f"Transform request - file: {file.filename if file else 'None'}, model_key: {model_key}")
    
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
        
        # Step 1: Convert to markdown
        markdown_content = None
        if vision_processor and vision_processor.is_supported_file(filename):
            result = vision_processor.process_file(file_path)
            if result['success']:
                markdown_content = result['content']
        elif audio_processor and audio_processor.is_supported_file(filename):
            result = audio_processor.process_file(file_path)
            if result['success']:
                markdown_content = result['content']
        else:
            raise HTTPException(status_code=400, detail=f'Unsupported file type: {filename}')
        
        if not markdown_content:
            raise HTTPException(status_code=500, detail="Failed to convert file to markdown")
        
        # Step 2: Extract structured data
        analysis_result = await structured_analyzer.analyze_content(
            markdown_content,
            model_key,
            custom_instructions,
            ai_model
        )
        
        if not analysis_result['success']:
            raise HTTPException(status_code=500, detail=analysis_result.get('error', 'Analysis failed'))
        
        return TransformResponse(
            model_used=analysis_result['model_used'],
            ai_model_used=analysis_result['ai_model_used'],
            total_files=1,
            successful=1,
            failed=0,
            results=[
                FileTransformResult(
                    filename=filename,
                    status="success",
                    markdown_content=markdown_content,
                    structured_data=analysis_result['result']
                )
            ]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return TransformResponse(
            model_used=model_key,
            ai_model_used=ai_model or config.get('models.ai_models.default_model'),
            total_files=1,
            successful=0,
            failed=1,
            results=[
                FileTransformResult(
                    filename=filename,
                    status="error",
                    error=str(e)
                )
            ]
        )
    finally:
        # Clean up the uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)


@app.post("/api/transform-stream")
async def transform_stream(
    files: List[UploadFile] = File(...),
    model_key: str = Form(...),
    custom_instructions: Optional[str] = Form(""),
    ai_model: Optional[str] = Form(None)
):
    """Stream transformation results using Server-Sent Events"""
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
                files_info.append({
                    'file_path': file_path,
                    'filename': filename
                })
        
        # Debug logging
        print(f"Streaming transform - files_info: {files_info}")
        print(f"Model key: {model_key}")
        print(f"Saved files: {saved_files}")
        
        # Verify files exist before streaming
        for file_info in files_info:
            if not os.path.exists(file_info['file_path']):
                print(f"ERROR: File does not exist: {file_info['file_path']}")
            else:
                print(f"File exists: {file_info['file_path']} (size: {os.path.getsize(file_info['file_path'])} bytes)")
        
        # Create a wrapper generator that handles cleanup after streaming completes
        async def stream_with_cleanup():
            try:
                async for chunk in transform_stream_v2(
                    files_info,
                    model_key,
                    custom_instructions or "",
                    ai_model,
                    vision_processor,
                    audio_processor,
                    structured_analyzer
                ):
                    yield chunk
            finally:
                # Clean up files only after streaming is complete
                logger.info("Streaming complete, cleaning up files")
                for file_path in saved_files:
                    try:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            logger.info(f"Cleaned up: {file_path}")
                    except Exception as e:
                        logger.error(f"Error cleaning up {file_path}: {e}")
        
        # Return streaming response with cleanup
        return StreamingResponse(
            stream_with_cleanup(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable nginx buffering
            }
        )
        
    except Exception as e:
        # Clean up on error
        for file_path in saved_files:
            if os.path.exists(file_path):
                os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))


# Add the new optimized streaming endpoint
app.post("/api/transform-stream-v2")(transform_stream_v2)


@app.post("/api/transform-batch")
async def transform_batch(
    files: List[UploadFile] = File(...),
    model_key: str = Form(...),
    custom_instructions: Optional[str] = Form(""),
    ai_model: Optional[str] = Form(None)
):
    """Transform multiple files to structured data"""
    if not files or all(f.filename == '' for f in files):
        raise HTTPException(status_code=400, detail="No files provided")
    
    results = []
    markdown_contents = {}
    
    # Process each file
    for file in files:
        if not file.filename:
            continue
            
        filename = secure_filename(file.filename)
        file_path = os.path.join(config.UPLOAD_FOLDER, filename)
        
        try:
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # Convert to markdown
            markdown_content = None
            if vision_processor and vision_processor.is_supported_file(filename):
                result = vision_processor.process_file(file_path)
                if result['success']:
                    markdown_content = result['content']
            elif audio_processor and audio_processor.is_supported_file(filename):
                result = audio_processor.process_file(file_path)
                if result['success']:
                    markdown_content = result['content']
            
            if markdown_content:
                markdown_contents[filename] = markdown_content
            else:
                results.append(
                    FileTransformResult(
                        filename=filename,
                        status="error",
                        error="Failed to convert to markdown or unsupported file type"
                    )
                )
                
        except Exception as e:
            results.append(
                FileTransformResult(
                    filename=filename,
                    status="error",
                    error=str(e)
                )
            )
        finally:
            # Clean up
            if os.path.exists(file_path):
                os.remove(file_path)
    
    # Batch analyze markdown contents
    if markdown_contents:
        try:
            analysis_results = await structured_analyzer.analyze_batch(
                markdown_contents,
                model_key,
                custom_instructions,
                ai_model
            )
            
            for result in analysis_results:
                filename = result['filename']
                if result['success']:
                    results.append(
                        FileTransformResult(
                            filename=filename,
                            status="success",
                            markdown_content=markdown_contents[filename],
                            structured_data=result['result']
                        )
                    )
                else:
                    results.append(
                        FileTransformResult(
                            filename=filename,
                            status="error",
                            markdown_content=markdown_contents[filename],
                            error=result.get('error', 'Analysis failed')
                        )
                    )
        except Exception as e:
            # If batch analysis fails, add error for all pending files
            for filename in markdown_contents:
                if not any(r.filename == filename for r in results):
                    results.append(
                        FileTransformResult(
                            filename=filename,
                            status="error",
                            markdown_content=markdown_contents[filename],
                            error=f"Batch analysis error: {str(e)}"
                        )
                    )
    
    # Calculate summary
    successful = [r for r in results if r.status == "success"]
    failed = [r for r in results if r.status == "error"]
    
    # Generate summary from successful results
    summary = None
    if successful:
        structured_data_list = [r.structured_data for r in successful if r.structured_data]
        if structured_data_list:
            summary = generate_summary(structured_data_list)
    
    return TransformResponse(
        model_used=model_key,
        ai_model_used=ai_model or config.get('models.ai_models.default_model'),
        total_files=len(results),
        successful=len(successful),
        failed=len(failed),
        results=results,
        summary=summary
    )


def generate_summary(data_list: List[dict]) -> dict:
    """Generate summary statistics from structured data"""
    if not data_list:
        return {}
    
    summary = {
        "total_analyzed": len(data_list),
    }
    
    # Aggregate by field type
    for field_name in data_list[0].keys():
        values = [row.get(field_name) for row in data_list if row.get(field_name) is not None]
        
        if not values:
            continue
        
        # Boolean fields - count true/false
        if all(isinstance(v, bool) for v in values):
            true_count = sum(1 for v in values if v)
            summary[f"{field_name}_true_count"] = true_count
            summary[f"{field_name}_false_count"] = len(values) - true_count
        
        # Numeric fields - basic stats
        elif all(isinstance(v, (int, float)) for v in values):
            summary[f"{field_name}_total"] = sum(values)
            summary[f"{field_name}_average"] = sum(values) / len(values)
            summary[f"{field_name}_min"] = min(values)
            summary[f"{field_name}_max"] = max(values)
        
        # List fields - aggregate unique values
        elif all(isinstance(v, list) for v in values):
            all_items = [item for sublist in values for item in sublist]
            unique_items = list(set(all_items))
            summary[f"{field_name}_unique_values"] = unique_items[:20]  # Limit to 20
            summary[f"{field_name}_unique_count"] = len(unique_items)
    
    return summary


@app.post("/api/download-results")
async def download_results(request: Request):
    """Download transformation results as Excel or CSV"""
    data = await request.json()
    results_data = data.get('results', {})
    format_type = data.get('format', 'excel')
    
    if not results_data:
        raise HTTPException(status_code=400, detail="No results to download")
    
    try:
        if format_type == 'excel':
            # Extract successful results
            results = results_data.get('results', [])
            successful_results = [r for r in results if r.get('status') == 'success' and r.get('structured_data')]
            
            if not successful_results:
                raise HTTPException(status_code=400, detail="No successful results to export")
            
            # Prepare data for DataFrame
            rows = []
            for result in successful_results:
                row = {'filename': result['filename']}
                row.update(result['structured_data'])
                rows.append(row)
            
            # Create DataFrame
            df = pd.DataFrame(rows)
            
            # Create Excel file in memory
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Results', index=False)
                
                # Get the workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets['Results']
                
                # Format the header row
                for cell in worksheet[1]:
                    cell.font = cell.font.copy(bold=True)
                    cell.fill = cell.fill.copy(fgColor="E0E0E0")
                
                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
                
                # Add summary sheet if multiple files
                if len(successful_results) > 1 and results_data.get('summary'):
                    summary_df = pd.DataFrame([results_data['summary']])
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)
                    
                    # Format summary sheet
                    summary_sheet = writer.sheets['Summary']
                    for cell in summary_sheet[1]:
                        cell.font = cell.font.copy(bold=True)
                        cell.fill = cell.fill.copy(fgColor="E0E0E0")
                    
                    # Auto-adjust summary columns
                    for column in summary_sheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        summary_sheet.column_dimensions[column_letter].width = adjusted_width
            
            output.seek(0)
            
            # Return Excel file
            return StreamingResponse(
                output,
                media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                headers={
                    'Content-Disposition': f'attachment; filename=transform_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
                }
            )
            
        else:
            # CSV format (fallback, though this is handled client-side)
            raise HTTPException(status_code=400, detail="CSV format should be handled client-side")
            
    except Exception as e:
        logger.error(f"Error generating download: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "processors_initialized": all([
            vision_processor is not None,
            audio_processor is not None,
            structured_analyzer is not None
        ]),
        "server": "FastAPI",
        "version": config.get('app.version', '2.0.0')
    }


@app.post("/api/debug-form")
async def debug_form(request: Request):
    """Debug endpoint to see what's being sent"""
    try:
        form = await request.form()
        
        form_data = {}
        for key in form:
            value = form[key]
            if hasattr(value, 'filename'):
                form_data[key] = f"File: {value.filename}"
            else:
                form_data[key] = str(value)
        
        return {
            "form_keys": list(form.keys()),
            "form_data": form_data,
            "content_type": request.headers.get("content-type"),
        }
    except Exception as e:
        return {
            "error": str(e),
            "content_type": request.headers.get("content-type"),
        }


@app.post("/api/test-transform")
async def test_transform(
    file: UploadFile = File(...),
    model_key: str = Form(...)
):
    """Simplified test endpoint"""
    return {
        "file": file.filename,
        "model_key": model_key,
        "success": True
    }


# Custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append({
            "loc": error["loc"],
            "msg": error["msg"],
            "type": error["type"]
        })
    
    print(f"Validation errors: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": errors, "body": str(exc.body) if hasattr(exc, 'body') else None}
    )

# Custom exception handler for better error responses
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": str(exc)}
    )


if __name__ == "__main__":
    # Run the FastAPI app with Uvicorn
    print(f"🚀 Starting server on http://localhost:{config.PORT}")
    print(f"📚 API documentation available at http://localhost:{config.PORT}/docs")
    
    uvicorn.run(
        "infotransform.main:app",
        host="0.0.0.0",
        port=config.PORT,
        reload=True,
        log_level="info"
    )
