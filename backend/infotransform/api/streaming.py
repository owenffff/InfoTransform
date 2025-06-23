"""
Streaming API endpoints for real-time transformation results
"""

import json
import asyncio
from typing import List, Dict, Any, AsyncGenerator
from fastapi import UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse
import aiofiles

from infotransform.config import config
from infotransform.processors import VisionProcessor, AudioProcessor, StructuredAnalyzer


async def process_file_for_streaming(
    file_path: str,
    filename: str,
    vision_processor: VisionProcessor,
    audio_processor: AudioProcessor,
    structured_analyzer: StructuredAnalyzer,
    model_key: str,
    custom_instructions: str,
    ai_model: str
) -> Dict[str, Any]:
    """Process a single file and return the result"""
    try:
        # Step 1: Convert to markdown
        markdown_content = None
        error_detail = None
        
        # Debug: Check if file exists
        import os
        if not os.path.exists(file_path):
            error_detail = f"File not found at path: {file_path}"
        elif vision_processor and vision_processor.is_supported_file(filename):
            print(f"Processing {filename} with vision processor at {file_path}")
            result = vision_processor.process_file(file_path)
            if result['success']:
                markdown_content = result['content']
            else:
                error_detail = f"Vision processing failed: {result.get('error', 'Unknown error')}"
        elif audio_processor and audio_processor.is_supported_file(filename):
            result = audio_processor.process_file(file_path)
            if result['success']:
                markdown_content = result['content']
            else:
                error_detail = f"Audio processing failed: {result.get('error', 'Unknown error')}"
        else:
            # Check which processor should handle it
            ext = filename.lower().split('.')[-1]
            error_detail = f"No processor available for .{ext} files"
        
        if not markdown_content:
            return {
                "type": "result",
                "filename": filename,
                "status": "error",
                "error": error_detail or "Failed to convert to markdown"
            }
        
        # Step 2: Extract structured data
        analysis_result = await structured_analyzer.analyze_content(
            markdown_content,
            model_key,
            custom_instructions,
            ai_model
        )
        
        if analysis_result['success']:
            return {
                "type": "result",
                "filename": filename,
                "status": "success",
                "markdown_content": markdown_content,
                "structured_data": analysis_result['result'],
                "model_fields": list(analysis_result['result'].keys())
            }
        else:
            return {
                "type": "result",
                "filename": filename,
                "status": "error",
                "error": analysis_result.get('error', 'Analysis failed'),
                "markdown_content": markdown_content
            }
            
    except Exception as e:
        return {
            "type": "result",
            "filename": filename,
            "status": "error",
            "error": str(e)
        }


async def generate_transform_stream(
    files: List[Dict[str, Any]],
    model_key: str,
    custom_instructions: str,
    ai_model: str,
    vision_processor: VisionProcessor,
    audio_processor: AudioProcessor,
    structured_analyzer: StructuredAnalyzer
) -> AsyncGenerator[str, None]:
    """Generate Server-Sent Events for file transformation"""
    total_files = len(files)
    successful = 0
    failed = 0
    
    # Send initial event with model information
    model_info = structured_analyzer.get_available_models().get(model_key, {})
    initial_event = {
        "type": "init",
        "total_files": total_files,
        "model_key": model_key,
        "model_name": model_info.get("name", model_key),
        "model_fields": model_info.get("fields", []),
        "ai_model": ai_model or config.get('models.ai_models.default_model')
    }
    yield f"data: {json.dumps(initial_event)}\n\n"
    
    # Process files one by one
    for index, file_info in enumerate(files):
        # Send progress update
        progress_event = {
            "type": "progress",
            "current": index,
            "total": total_files,
            "percentage": (index / total_files) * 100
        }
        yield f"data: {json.dumps(progress_event)}\n\n"
        
        # Process the file
        result = await process_file_for_streaming(
            file_info['file_path'],
            file_info['filename'],
            vision_processor,
            audio_processor,
            structured_analyzer,
            model_key,
            custom_instructions,
            ai_model
        )
        
        # Update counters
        if result['status'] == 'success':
            successful += 1
        else:
            failed += 1
        
        # Add progress info to result
        result['progress'] = {
            "current": index + 1,
            "total": total_files,
            "successful": successful,
            "failed": failed
        }
        
        # Send result event
        yield f"data: {json.dumps(result)}\n\n"
        
        # Small delay to prevent overwhelming the client
        await asyncio.sleep(0.1)
    
    # Send completion event with summary
    completion_event = {
        "type": "complete",
        "total_files": total_files,
        "successful": successful,
        "failed": failed,
        "model_used": model_key,
        "ai_model_used": ai_model or config.get('models.ai_models.default_model')
    }
    yield f"data: {json.dumps(completion_event)}\n\n"
