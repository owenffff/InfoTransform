"""
Optimized streaming API v2 with parallel processing and batch AI analysis
"""

import json
import logging
import time
import os
from typing import List, Dict, Any, AsyncGenerator, Optional
from fastapi import UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse

from infotransform.config import config
from infotransform.processors import StructuredAnalyzerAgent, SummarizationAgent
from infotransform.processors.async_converter import AsyncMarkdownConverter
from infotransform.processors.batch_processor import BatchProcessor
from infotransform.utils.file_lifecycle import get_file_manager, ManagedStreamingResponse
from infotransform.utils.token_counter import log_token_count, count_tokens_quiet

logger = logging.getLogger(__name__)


class OptimizedStreamingProcessor:
    """Handles optimized file processing with parallel conversion and batch AI"""
    
    def __init__(self):
        self.structured_analyzer_agent = StructuredAnalyzerAgent()
        self.summarization_agent = SummarizationAgent()
        self.markdown_converter = AsyncMarkdownConverter()
        self.batch_processor = BatchProcessor(self.structured_analyzer_agent)
        self.file_manager = get_file_manager()
        
        # Performance monitoring
        self.enable_metrics = config.get_performance('monitoring.enable_metrics', True)
        self.slow_threshold = config.get_performance(
            'monitoring.slow_operation_threshold', 5.0
        )
    
    async def start(self):
        """Start all background services"""
        await self.file_manager.start()
        await self.batch_processor.start()
        logger.info("OptimizedStreamingProcessor started")
    
    async def stop(self):
        """Stop all background services"""
        await self.batch_processor.stop()
        await self.file_manager.stop()
        self.markdown_converter.shutdown()
        logger.info("OptimizedStreamingProcessor stopped")
    
    async def process_files_optimized(
        self,
        files: List[Dict[str, Any]],
        model_key: str,
        custom_instructions: str,
        ai_model: str
    ) -> AsyncGenerator[str, None]:
        """
        Process files with optimized pipeline
        
        Args:
            files: List of file info dictionaries
            model_key: Model key for structured analysis
            custom_instructions: Custom instructions
            ai_model: AI model to use
            
        Yields:
            Server-sent events
        """
        total_files = len(files)
        start_time = time.time()
        
        # Get model information
        model_info = self.structured_analyzer_agent.get_available_models().get(model_key, {})
        
        # Send initial event
        # Convert fields dict to array of field names for JavaScript
        fields_dict = model_info.get("fields", {})
        model_fields = list(fields_dict.keys()) if isinstance(fields_dict, dict) else []
        
        initial_event = {
            "type": "init",
            "total_files": total_files,
            "model_key": model_key,
            "model_name": model_info.get("name", model_key),
            "model_fields": model_fields,
            "ai_model": ai_model or config.get('models.ai_models.default_model'),
            "optimization": {
                "parallel_conversion": True,
                "batch_processing": True,
                "max_workers": self.markdown_converter.max_workers,
                "batch_size": self.batch_processor.batch_size
            }
        }
        yield f"data: {json.dumps(initial_event)}\n\n"
        
        # Phase 1: Parallel markdown conversion
        conversion_start = time.time()
        yield f"data: {json.dumps({'type': 'phase', 'phase': 'markdown_conversion', 'status': 'started'})}\n\n"
        
        # Use file lifecycle manager to track files
        async with self.file_manager.batch_context(files) as managed_files:
            # Convert all files to markdown in parallel
            markdown_results = await self.markdown_converter.convert_files_parallel(managed_files)
            
            conversion_time = time.time() - conversion_start
            phase_complete_event = {
                'type': 'phase',
                'phase': 'markdown_conversion',
                'status': 'completed',
                'duration': conversion_time,
                'files_per_second': len(files) / conversion_time if conversion_time > 0 else 0
            }
            yield f"data: {json.dumps(phase_complete_event)}\n\n"
            
            # Separate successful conversions from failures
            successful_conversions = []
            failed_conversions = []
            
            for i, result in enumerate(markdown_results):
                if result['success'] and result['markdown_content']:
                    # Log token count for the converted markdown
                    log_token_count(result['filename'], result['markdown_content'])
                    
                    successful_conversions.append({
                        'filename': result['filename'],
                        'markdown_content': result['markdown_content'],
                        'original_index': i
                    })
                else:
                    failed_conversions.append({
                        'filename': result['filename'],
                        'error': result.get('error', 'Unknown error'),
                        'original_index': i
                    })
            
            # Send conversion summary
            conversion_summary = {
                'type': 'conversion_summary',
                'successful': len(successful_conversions),
                'failed': len(failed_conversions),
                'failed_files': [f['filename'] for f in failed_conversions]
            }
            yield f"data: {json.dumps(conversion_summary)}\n\n"
            
            # Phase 2: Summarization (if needed) and AI processing
            if successful_conversions:
                # Check which files need summarization
                summarization_start = time.time()
                files_to_summarize = []
                files_to_analyze_directly = []
                
                for item in successful_conversions:
                    if self.summarization_agent.should_summarize(item['markdown_content']):
                        files_to_summarize.append(item)
                    else:
                        files_to_analyze_directly.append(item)
                
                # Send summarization phase event if needed
                if files_to_summarize:
                    yield f"data: {json.dumps({'type': 'phase', 'phase': 'summarization', 'status': 'started', 'files_to_summarize': len(files_to_summarize)})}\n\n"
                    
                    # Process summarizations
                    for item in files_to_summarize:
                        summary_result = await self.summarization_agent.summarize_content(
                            item['markdown_content'],
                            model_fields,
                            item['filename']
                        )
                        
                        if summary_result['success']:
                            # Replace markdown content with summary for analysis
                            item['original_markdown_content'] = item['markdown_content']
                            item['markdown_content'] = summary_result['summary']
                            item['was_summarized'] = True
                            item['summarization_metrics'] = {
                                'original_length': summary_result['original_length'],
                                'summary_length': summary_result['summary_length'],
                                'compression_ratio': summary_result['compression_ratio']
                            }
                        else:
                            # Log error but continue with original content
                            logger.warning(f"Summarization failed for {item['filename']}: {summary_result.get('error')}")
                            item['was_summarized'] = False
                    
                    summarization_time = time.time() - summarization_start
                    yield f"data: {json.dumps({'type': 'phase', 'phase': 'summarization', 'status': 'completed', 'duration': summarization_time})}\n\n"
                else:
                    # Mark all files as not summarized
                    for item in files_to_analyze_directly:
                        item['was_summarized'] = False
                
                # Phase 3: Structured Analysis
                ai_start = time.time()
                yield f"data: {json.dumps({'type': 'phase', 'phase': 'ai_processing', 'status': 'started'})}\n\n"
                
                # Process through batch processor
                processed_count = 0
                successful_ai = 0
                failed_ai = 0
                
                # Create a mapping to track original indices
                result_map = {}
                
                # Process items and stream results
                async for ai_result in self.batch_processor.process_items_stream(
                    successful_conversions,
                    model_key,
                    custom_instructions,
                    ai_model
                ):
                    processed_count += 1
                    
                    # Find original index
                    original_item = next(
                        (item for item in successful_conversions 
                         if item['filename'] == ai_result['filename']),
                        None
                    )
                    
                    if original_item:
                        original_index = original_item['original_index']
                        
                        # Prepare result event
                        if ai_result['success']:
                            successful_ai += 1
                            result_event = {
                                "type": "result",
                                "filename": ai_result['filename'],
                                "status": "success",
                                "markdown_content": original_item.get('original_markdown_content', original_item['markdown_content']),
                                "structured_data": ai_result['structured_data'],
                                "model_fields": list(ai_result['structured_data'].keys()),
                                "processing_time": ai_result.get('processing_time', 0),
                                "was_summarized": original_item.get('was_summarized', False),
                                "summarization_metrics": original_item.get('summarization_metrics', None),
                                "progress": {
                                    "current": processed_count + len(failed_conversions),
                                    "total": total_files,
                                    "successful": successful_ai,
                                    "failed": failed_ai + len(failed_conversions)
                                }
                            }
                        else:
                            failed_ai += 1
                            result_event = {
                                "type": "result",
                                "filename": ai_result['filename'],
                                "status": "error",
                                "error": ai_result.get('error', 'AI processing failed'),
                                "markdown_content": original_item['markdown_content'],
                                "progress": {
                                    "current": processed_count + len(failed_conversions),
                                    "total": total_files,
                                    "successful": successful_ai,
                                    "failed": failed_ai + len(failed_conversions)
                                }
                            }
                        
                        yield f"data: {json.dumps(result_event)}\n\n"
                
                ai_time = time.time() - ai_start
                ai_complete_event = {
                    'type': 'phase',
                    'phase': 'ai_processing',
                    'status': 'completed',
                    'duration': ai_time,
                    'files_per_second': len(successful_conversions) / ai_time if ai_time > 0 else 0
                }
                yield f"data: {json.dumps(ai_complete_event)}\n\n"
            
            # Send failed conversion results
            for failed in failed_conversions:
                failed_result_event = {
                    'type': 'result',
                    'filename': failed['filename'],
                    'status': 'error',
                    'error': failed['error'],
                    'progress': {
                        'current': len(successful_conversions) + failed_conversions.index(failed) + 1,
                        'total': total_files,
                        'successful': successful_ai,
                        'failed': failed_ai + len(failed_conversions)
                    }
                }
                yield f"data: {json.dumps(failed_result_event)}\n\n"
            
            # Send completion event with metrics
            total_time = time.time() - start_time
            
            # Calculate summarization statistics
            summarized_count = sum(1 for item in successful_conversions if item.get('was_summarized', False))
            summarization_time = summarization_time if 'summarization_time' in locals() else 0
            
            completion_event = {
                "type": "complete",
                "total_files": total_files,
                "successful": successful_ai,
                "failed": failed_ai + len(failed_conversions),
                "model_used": model_key,
                "ai_model_used": ai_model or config.get('models.ai_models.default_model'),
                "summarization": {
                    "files_summarized": summarized_count,
                    "summarization_duration": summarization_time,
                    "token_threshold": self.summarization_agent.token_threshold,
                    "summary_model": self.summarization_agent.summary_model
                },
                "performance": {
                    "total_duration": total_time,
                    "conversion_duration": conversion_time,
                    "summarization_duration": summarization_time,
                    "ai_duration": ai_time if successful_conversions else 0,
                    "files_per_second": total_files / total_time if total_time > 0 else 0,
                    "conversion_metrics": self.markdown_converter.get_metrics(),
                    "batch_metrics": self.batch_processor.get_metrics()
                }
            }
            yield f"data: {json.dumps(completion_event)}\n\n"


# Global processor instance
_processor: Optional[OptimizedStreamingProcessor] = None


async def get_processor() -> OptimizedStreamingProcessor:
    """Get or create the global processor instance"""
    global _processor
    if _processor is None:
        _processor = OptimizedStreamingProcessor()
        await _processor.start()
    return _processor


async def transform_stream_v2(
    files: List[UploadFile],
    model_key: str = Form(...),
    custom_instructions: str = Form(""),
    ai_model: Optional[str] = Form(None)
) -> StreamingResponse:
    """
    Optimized streaming endpoint with parallel processing
    
    Args:
        files: List of uploaded files
        model_key: Key of the analysis model to use
        custom_instructions: Optional custom instructions
        ai_model: Optional AI model override
        
    Returns:
        StreamingResponse with server-sent events
    """
    processor = await get_processor()
    
    # Validate inputs
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    # Check if model exists
    available_models = processor.structured_analyzer_agent.get_available_models()
    if model_key not in available_models:
        raise HTTPException(
            status_code=400,
            detail=f"Model '{model_key}' not found. Available models: {list(available_models.keys())}"
        )
    
    # Save uploaded files
    saved_files = []
    file_infos = []
    
    try:
        for file in files:
            # Save file
            file_path = os.path.join(config.UPLOAD_FOLDER, file.filename)
            
            # Read file content
            content = await file.read()
            
            # Save to disk
            with open(file_path, 'wb') as f:
                f.write(content)
            
            saved_files.append(file_path)
            file_infos.append({
                'file_path': file_path,
                'filename': file.filename
            })
            
            logger.info(f"Saved file: {file.filename} to {file_path}")
    
    except Exception as e:
        # Clean up any saved files on error
        for file_path in saved_files:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        logger.error(f"Error saving files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving files: {str(e)}")
    
    # Create managed streaming response
    managed_response = ManagedStreamingResponse(
        processor.process_files_optimized(
            file_infos,
            model_key,
            custom_instructions,
            ai_model
        ),
        saved_files,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )
    
    return managed_response.create_response()


# Cleanup on shutdown
async def shutdown_processor():
    """Shutdown the processor on app shutdown"""
    global _processor
    if _processor:
        await _processor.stop()
        _processor = None
