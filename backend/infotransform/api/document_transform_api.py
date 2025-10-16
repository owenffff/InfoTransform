"""
Optimized streaming API with parallel processing and batch AI analysis
"""

import json
import logging
import time
import os
import zipfile
import tempfile
import shutil
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, AsyncGenerator, Optional
from fastapi import UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse

from infotransform.config import config
from infotransform.processors import StructuredAnalyzerAgent, SummarizationAgent
from infotransform.processors.async_converter import AsyncMarkdownConverter
from infotransform.processors.ai_batch_processor import BatchProcessor
from infotransform.utils.file_lifecycle import get_file_manager, ManagedStreamingResponse
from infotransform.db import get_logs_db

logger = logging.getLogger(__name__)


class StreamingProcessor:
    """Handles optimized file processing with parallel conversion and batch AI"""
    
    def __init__(self):
        self.structured_analyzer_agent = StructuredAnalyzerAgent()
        self.summarization_agent = SummarizationAgent()
        self.markdown_converter = AsyncMarkdownConverter()
        self.batch_processor = BatchProcessor(self.structured_analyzer_agent)
        self.file_manager = get_file_manager()
        self.temp_dirs = []  # Track temp directories for cleanup
        
        # Performance monitoring
        self.enable_metrics = config.get_performance('monitoring.enable_metrics', True)
        self.slow_threshold = config.get_performance(
            'monitoring.slow_operation_threshold', 5.0
        )
    
    async def start(self):
        """Start all background services"""
        await self.file_manager.start()
        await self.batch_processor.start()
        logger.info("StreamingProcessor started")
    
    async def stop(self):
        """Stop all background services"""
        await self.batch_processor.stop()
        await self.file_manager.stop()
        self.markdown_converter.shutdown()
        self._cleanup_temp_dirs()
        logger.info("StreamingProcessor stopped")
    
    def _cleanup_temp_dirs(self):
        """Clean up temporary directories"""
        for temp_dir in self.temp_dirs:
            if os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    logger.debug(f"Cleaned up temp directory: {temp_dir}")
                except Exception as e:
                    logger.warning(f"Failed to clean up temp directory {temp_dir}: {e}")
        self.temp_dirs.clear()
    
    def _is_zip_file(self, filename: str) -> bool:
        """Check if file is a ZIP archive"""
        return filename.lower().endswith('.zip')
    
    def _extract_zip_recursive(self, zip_path: str, archive_name: str) -> List[Dict[str, Any]]:
        """
        Extract ZIP file recursively, preserving directory structure
        
        Args:
            zip_path: Path to the ZIP file
            archive_name: Name of the ZIP archive (for display)
            
        Returns:
            List of file info dictionaries with path metadata
        """
        temp_dir = tempfile.mkdtemp(prefix='infotransform_zip_', dir=config.TEMP_EXTRACT_DIR)
        self.temp_dirs.append(temp_dir)
        
        extracted_files = []
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Extract all files
                zip_ref.extractall(temp_dir)
                
                # Walk through extracted files recursively
                for root, dirs, files in os.walk(temp_dir):
                    for filename in files:
                        # Skip hidden files and system files
                        if filename.startswith('.') or filename.startswith('__'):
                            continue
                        
                        full_path = os.path.join(root, filename)
                        # Get relative path from temp_dir root
                        relative_path = os.path.relpath(full_path, temp_dir)
                        
                        # Create file info with metadata
                        file_info = {
                            'file_path': full_path,
                            'filename': filename,
                            'source_archive': archive_name,
                            'relative_path': relative_path,
                            'display_name': f"{archive_name} → {relative_path}"
                        }
                        
                        extracted_files.append(file_info)
                        logger.debug(f"Extracted from ZIP: {relative_path}")
            
            logger.info(f"Extracted {len(extracted_files)} files from {archive_name}")
            
        except Exception as e:
            logger.error(f"Failed to extract ZIP file {archive_name}: {str(e)}")
            # Return empty list on failure, don't crash the whole process
            return []
        
        return extracted_files
    
    def _get_display_fields(self, structured_data: Dict[str, Any]) -> List[str]:
        """
        Extract display fields from structured data.
        For nested schemas with 'item' wrapper, extract fields from first item.
        """
        if not structured_data:
            return []
        
        # Check if this is a nested schema with single 'item' field containing a list
        if (len(structured_data) == 1 and 
            'item' in structured_data and 
            isinstance(structured_data['item'], list) and 
            len(structured_data['item']) > 0 and
            isinstance(structured_data['item'][0], dict)):
            # Return fields from the first item in the list
            return list(structured_data['item'][0].keys())
        
        # Otherwise return top-level keys
        return list(structured_data.keys())
    
    def _expand_nested_results(self, ai_result: Dict[str, Any], original_item: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Expand nested results into multiple flat results for display.
        Each item in a nested schema becomes a separate row.
        """
        structured_data = ai_result.get('structured_data', {})
        
        # Check if this is a nested schema with 'item' field containing a list
        if (structured_data and 
            len(structured_data) == 1 and 
            'item' in structured_data and 
            isinstance(structured_data['item'], list)):
            
            expanded_results = []
            items = structured_data['item']
            
            # Create a separate result for each item
            for idx, item_data in enumerate(items):
                # Use consistent filename without item number suffix
                display_name = original_item.get('display_name', ai_result['filename'])
                
                expanded_result = {
                    'success': ai_result['success'],
                    'filename': ai_result['filename'],
                    'display_name': display_name,
                    'structured_data': item_data,  # Flat data from this item
                    'model_fields': list(item_data.keys()) if isinstance(item_data, dict) else [],
                    'processing_time': ai_result.get('processing_time', 0),
                    'original_item': original_item,
                    'item_index': idx,
                    'total_items': len(items),
                    'is_primary_result': idx == 0,  # First item represents the file
                    'source_file': ai_result['filename']  # Original file identifier
                }
                
                # Preserve other fields from the original result
                if 'error' in ai_result:
                    expanded_result['error'] = ai_result['error']
                    
                expanded_results.append(expanded_result)
            
            return expanded_results
        
        # Not a nested schema, return as-is with display fields
        ai_result['display_name'] = original_item.get('display_name', ai_result['filename'])
        ai_result['model_fields'] = self._get_display_fields(structured_data)
        ai_result['original_item'] = original_item
        ai_result['is_primary_result'] = True  # Single result represents the file
        ai_result['source_file'] = ai_result['filename']
        return [ai_result]
    
    async def process_files_optimized(
        self,
        files: List[Dict[str, Any]],
        model_key: str,
        custom_instructions: str,
        ai_model: str,
        run_id: str = None
    ) -> AsyncGenerator[str, None]:
        """
        Process files with optimized pipeline

        Args:
            files: List of file info dictionaries
            model_key: Model key for structured analysis
            custom_instructions: Custom instructions
            ai_model: AI model to use
            run_id: Unique identifier for this processing run

        Yields:
            Server-sent events
        """
        # Generate run_id if not provided
        if run_id is None:
            run_id = str(uuid.uuid4())
        # Pre-process files to extract ZIP archives
        expanded_files = []
        zip_count = 0
        
        for file_info in files:
            if self._is_zip_file(file_info['filename']):
                # Extract ZIP and get all contained files
                zip_count += 1
                extracted = self._extract_zip_recursive(
                    file_info['file_path'],
                    file_info['filename']
                )
                expanded_files.extend(extracted)
                logger.info(f"Expanded ZIP {file_info['filename']}: {len(extracted)} files")
            else:
                # Regular file, add as-is
                expanded_files.append(file_info)
        
        # Update files list to include extracted files
        if zip_count > 0:
            logger.info(f"[{run_id}] Processed {zip_count} ZIP files, total files: {len(expanded_files)}")
            files = expanded_files
        
        total_files = len(files)
        start_time = time.time()
        start_timestamp = datetime.now(timezone.utc).isoformat()

        # Log run start with run_id
        logger.info(f"[{run_id}] Starting processing run: {total_files} files, model={model_key}, ai_model={ai_model}")

        # Get model information
        model_info = self.structured_analyzer_agent.get_available_models().get(model_key, {})

        # Log to database
        logs_db = get_logs_db()
        await logs_db.insert_run_start(
            run_id=run_id,
            start_timestamp=start_timestamp,
            total_files=total_files,
            model_key=model_key,
            model_name=model_info.get("name", model_key),
            ai_model_used=ai_model or config.get('models.ai_models.default_model'),
            custom_instructions=custom_instructions if custom_instructions else None
        )
        
        # Send initial event
        # Convert fields dict to array of field names for JavaScript
        fields_dict = model_info.get("fields", {})
        model_fields = list(fields_dict.keys()) if isinstance(fields_dict, dict) else []
        
        initial_event = {
            "type": "init",
            "run_id": run_id,
            "start_timestamp": start_timestamp,
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
        
        # Phase 1: Parallel markdown conversion with real-time progress
        conversion_start = time.time()
        yield f"data: {json.dumps({'type': 'phase', 'phase': 'markdown_conversion', 'status': 'started'})}\n\n"
        
        # Use file lifecycle manager to track files
        async with self.file_manager.batch_context(files) as managed_files:
            # Create conversion tasks with index tracking
            import asyncio
            
            async def convert_with_index(file_info, index):
                """Convert file and return result with index"""
                result = await self.markdown_converter.convert_file_async(file_info)
                return index, result
            
            tasks = []
            for i, file_info in enumerate(managed_files):
                task = asyncio.create_task(convert_with_index(file_info, i))
                tasks.append(task)
            
            # Process tasks as they complete and send progress
            completed = 0
            for task in asyncio.as_completed(tasks):
                index, result = await task
                completed += 1
                
                # Send progress event for each completed file
                elapsed = time.time() - conversion_start
                # Get the original file info using the index
                original_file = managed_files[index]
                event = {
                    'type': 'conversion_progress',
                    'phase': 1,
                    'current': completed,
                    'total': len(files),
                    'filename': original_file.get('display_name', result.get('filename', 'Unknown')),
                    'success': result.get('success', False),
                    'files_per_second': round(completed / elapsed if elapsed > 0 else 0, 2),
                    'phase_name': 'Converting documents'
                }
                yield f"data: {json.dumps(event)}\n\n"
            
            # Gather all results in original order
            results_with_indices = await asyncio.gather(*tasks)
            # Extract just the results, sorted by original index
            markdown_results = [None] * len(results_with_indices)
            for index, result in results_with_indices:
                markdown_results[index] = result
            
            conversion_time = time.time() - conversion_start
            logger.info(f"[{run_id}] Markdown conversion complete: {len(files)} files in {conversion_time:.2f}s")
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
                # Get the original file info to preserve metadata
                original_file = managed_files[i]

                if result['success'] and result['markdown_content']:
                    successful_conversions.append({
                        'filename': result['filename'],
                        'display_name': original_file.get('display_name', result['filename']),
                        'markdown_content': result['markdown_content'],
                        'original_index': i,
                        'file_path': original_file.get('file_path')  # Store original file path
                    })
                else:
                    failed_conversions.append({
                        'filename': result['filename'],
                        'display_name': original_file.get('display_name', result['filename']),
                        'error': result.get('error', 'Unknown error'),
                        'original_index': i,
                        'file_path': original_file.get('file_path')  # Store original file path
                    })
            
            # Identify password-protected PDFs among the failures so the UI can provide
            # a clear, user-friendly message instead of a generic “network error”.
            password_required = [
                f['filename'] for f in failed_conversions
                if f.get('error_type') == 'password_required'
            ]

            # Send conversion summary
            conversion_summary = {
                'type': 'conversion_summary',
                'successful': len(successful_conversions),
                'failed': len(failed_conversions),
                'failed_files': [f['filename'] for f in failed_conversions],
                'password_required': password_required
            }
            yield f"data: {json.dumps(conversion_summary)}\n\n"
            
            # Initialise AI-phase counters even when there are zero successful conversions
            processed_count = 0
            successful_ai = 0
            failed_ai = 0

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
                
                # Create a mapping to track original indices
                result_map = {}
                
                # Process items and stream results
                async for ai_result in self.batch_processor.process_items_stream(
                    successful_conversions,
                    model_key,
                    custom_instructions,
                    ai_model
                ):
                    # Check if this is a partial or final result
                    is_final = ai_result.get('final', True)
                    
                    # Only increment processed count for final results
                    if is_final:
                        processed_count += 1
                    
                    # Find original index
                    original_item = next(
                        (item for item in successful_conversions 
                         if item['filename'] == ai_result['filename']),
                        None
                    )
                    
                    if original_item:
                        original_index = original_item['original_index']
                        
                        # Expand nested results into multiple flat results
                        expanded_results = self._expand_nested_results(ai_result, original_item)
                        
                        # Send each expanded result as a separate event
                        for expanded_result in expanded_results:
                            if ai_result['success']:
                                if is_final:
                                    # Only count once for all expanded results from same file
                                    if expanded_result.get('item_index', 0) == 0:
                                        successful_ai += 1
                                    
                                    result_event = {
                                        "type": "result",
                                        "filename": expanded_result['display_name'],
                                        "status": "success",
                                        "markdown_content": original_item.get('original_markdown_content', original_item['markdown_content']),
                                        "structured_data": expanded_result['structured_data'],
                                        "model_fields": expanded_result['model_fields'],
                                        "processing_time": expanded_result.get('processing_time', 0),
                                        "was_summarized": original_item.get('was_summarized', False),
                                        "summarization_metrics": original_item.get('summarization_metrics', None),
                                        "is_primary_result": expanded_result.get('is_primary_result', True),
                                        "source_file": expanded_result.get('source_file', expanded_result['filename']),
                                        "file_path": original_item.get('file_path'),  # Add file path for review session
                                        "progress": {
                                            "phase": 2,
                                            "phase_name": "Analyzing with AI",
                                            "current": processed_count + len(failed_conversions),
                                            "total": total_files,
                                            "successful": successful_ai,
                                            "failed": failed_ai + len(failed_conversions)
                                        }
                                    }
                                else:
                                    # Partial result - don't update progress counters
                                    result_event = {
                                        "type": "partial",
                                        "filename": expanded_result['display_name'],
                                        "status": "success",
                                        "structured_data": expanded_result['structured_data'],
                                        "model_fields": expanded_result['model_fields'],
                                        "processing_time": expanded_result.get('processing_time', 0)
                                    }
                            else:
                                if is_final:
                                    # Only count once for all expanded results from same file
                                    if expanded_result.get('item_index', 0) == 0:
                                        failed_ai += 1
                                    result_event = {
                                        "type": "result",
                                        "filename": expanded_result['display_name'],
                                        "status": "error",
                                        "error": ai_result.get('error', 'AI processing failed'),
                                        "markdown_content": original_item['markdown_content'],
                                        "progress": {
                                            "phase": 2,
                                            "phase_name": "Analyzing with AI",
                                            "current": processed_count + len(failed_conversions),
                                            "total": total_files,
                                            "successful": successful_ai,
                                            "failed": failed_ai + len(failed_conversions)
                                        }
                                    }
                                else:
                                    # Partial error (unlikely but handle it)
                                    result_event = {
                                        "type": "partial",
                                        "filename": expanded_result['display_name'],
                                        "status": "error",
                                        "error": ai_result.get('error', 'AI processing failed')
                                    }
                            
                            yield f"data: {json.dumps(result_event)}\n\n"

                ai_time = time.time() - ai_start
                logger.info(f"[{run_id}] AI processing complete: {len(successful_conversions)} files in {ai_time:.2f}s")
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
                    'filename': failed.get('display_name', failed['filename']),
                    'status': 'error',
                    'error': failed['error'],
                    'is_primary_result': True,  # Failed files are primary results
                    'source_file': failed['filename'],
                    'file_path': failed.get('file_path'),  # Add file path for review session
                    'progress': {
                        'current': len(successful_conversions) + failed_conversions.index(failed) + 1,
                        'total': total_files,
                        'successful': successful_ai,
                        'failed': failed_ai + len(failed_conversions)
                    }
                }
                yield f"data: {json.dumps(failed_result_event)}\n\n"
            
            # Send completion event with metrics
            end_time = time.time()
            total_time = end_time - start_time
            end_timestamp = datetime.now(timezone.utc).isoformat()

            # Calculate summarization statistics
            summarized_count = sum(1 for item in successful_conversions if item.get('was_summarized', False))
            summarization_time = summarization_time if 'summarization_time' in locals() else 0

            # Get batch metrics with token usage
            batch_metrics = self.batch_processor.get_metrics()
            token_usage = batch_metrics.get('token_usage', {})

            completion_event = {
                "type": "complete",
                "run_id": run_id,
                "timestamps": {
                    "start": start_timestamp,
                    "end": end_timestamp,
                    "duration": total_time
                },
                "total_files": total_files,
                "successful": successful_ai,
                "failed": failed_ai + len(failed_conversions),
                "model_used": model_key,
                "ai_model_used": ai_model or config.get('models.ai_models.default_model'),
                "token_usage": {
                    "input_tokens": token_usage.get('input_tokens', 0),
                    "output_tokens": token_usage.get('output_tokens', 0),
                    "total_tokens": token_usage.get('total_tokens', 0),
                    "cache_read_tokens": token_usage.get('cache_read_tokens', 0),
                    "cache_write_tokens": token_usage.get('cache_write_tokens', 0),
                    "requests": token_usage.get('requests', 0)
                },
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
                    "batch_metrics": batch_metrics
                }
            }

            # Log completion with run_id
            logger.info(
                f"[{run_id}] Processing complete: {successful_ai} successful, {failed_ai + len(failed_conversions)} failed, "
                f"{total_time:.2f}s total, {token_usage.get('total_tokens', 0)} tokens"
            )

            # Update database with completion data
            await logs_db.update_run_complete(
                run_id=run_id,
                end_timestamp=end_timestamp,
                duration_seconds=total_time,
                successful_files=successful_ai,
                failed_files=failed_ai + len(failed_conversions),
                token_usage=token_usage,
                status='completed'
            )

            yield f"data: {json.dumps(completion_event)}\n\n"


# Global processor instance
_processor: Optional[StreamingProcessor] = None


async def get_processor() -> StreamingProcessor:
    """Get or create the global processor instance"""
    global _processor
    if _processor is None:
        _processor = StreamingProcessor()
        await _processor.start()
    return _processor


async def transform(
    files: List[UploadFile],
    model_key: str = Form(...),
    custom_instructions: str = Form(""),
    ai_model: Optional[str] = Form(None)
) -> StreamingResponse:
    """
    Optimized streaming endpoint with parallel processing
    
    Args:
        files: List of uploaded files
        model_key: Key of the document schema to use
        custom_instructions: Optional custom instructions
        ai_model: Optional AI model override
        
    Returns:
        StreamingResponse with server-sent events
    """
    processor = await get_processor()

    # Generate unique run ID for this request
    run_id = str(uuid.uuid4())

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
            
            logger.info(f"[{run_id}] Saved file: {file.filename} to {file_path}")

    except Exception as e:
        # Clean up any saved files on error
        for file_path in saved_files:
            if os.path.exists(file_path):
                os.remove(file_path)

        logger.error(f"[{run_id}] Error saving files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving files: {str(e)}")
    
    # Create managed streaming response
    managed_response = ManagedStreamingResponse(
        processor.process_files_optimized(
            file_infos,
            model_key,
            custom_instructions,
            ai_model,
            run_id=run_id
        ),
        saved_files,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
            "X-Run-ID": run_id  # Include run ID in response headers
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
