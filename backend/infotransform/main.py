"""
FastAPI application for InfoTransform
"""

import os
import logging
from datetime import datetime
from pathlib import Path
import pandas as pd
from io import BytesIO

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
import uvicorn

from infotransform.config import config
from infotransform.processors import VisionProcessor, AudioProcessor, BatchProcessor, StructuredAnalyzerAgent
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
        structured_analyzer = StructuredAnalyzerAgent()
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
# Mount dist for compiled assets (CSS, JS bundles)
dist_path = project_root / "frontend" / "dist"
if dist_path.exists():
    app.mount("/static", StaticFiles(directory=str(dist_path)), name="static")

# Mount frontend/static for fonts, favicon, and other static assets
static_assets_path = project_root / "frontend" / "static"
if static_assets_path.exists():
    app.mount("/assets", StaticFiles(directory=str(static_assets_path)), name="assets")

# Mount src as fallback for development
src_path = project_root / "frontend" / "src"
app.mount("/src", StaticFiles(directory=str(src_path)), name="src")

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




@app.get("/api/models")
async def list_analysis_models():
    """List available analysis models"""
    if not structured_analyzer:
        raise HTTPException(status_code=503, detail="Analyzer not initialized")
    
    return {
        "models": structured_analyzer.get_available_models(),
        "ai_models": structured_analyzer.get_available_ai_models()
    }




# Add the new optimized streaming endpoint
app.post("/api/transform-stream-v2")(transform_stream_v2)




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
                            max_length = len(str(cell.value))
                        except Exception as e:
                            logger.warning(f"Could not determine length of cell value: {e}")
                            value_length = 0
                        if value_length > max_length:
                            max_length = value_length
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
                                value_length = len(str(cell.value))
                            except Exception:
                                value_length = 0
                            if value_length > max_length:
                                max_length = value_length
                            
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
        app,
        host=config.get('api.host', '0.0.0.0'),
        port=config.PORT,
        reload=True,
        log_level="info"
    )
