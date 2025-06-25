"""
Batch processor for efficient AI processing with dynamic batching
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, AsyncGenerator
from dataclasses import dataclass

from infotransform.config import config
from infotransform.processors.structured_analyzer_agent import StructuredAnalyzerAgent
from infotransform.utils.token_counter import log_token_count

logger = logging.getLogger(__name__)


@dataclass
class BatchItem:
    """Item to be processed in a batch"""
    filename: str
    markdown_content: str
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


@dataclass
class BatchResult:
    """Result from batch processing"""
    filename: str
    success: bool
    structured_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: float = 0.0


class BatchProcessor:
    """Handles batch processing of markdown content for AI analysis"""
    
    def __init__(self, structured_analyzer_agent: StructuredAnalyzerAgent):
        self.analyzer = structured_analyzer_agent
        
        # Load configuration
        self.batch_size = int(config.get_performance('ai_processing.batch_size', 10))
        self.max_wait_time = float(config.get_performance('ai_processing.max_wait_time', 2.0))
        self.max_concurrent_batches = int(config.get_performance(
            'ai_processing.max_concurrent_batches', 3
        ))
        self.timeout_per_batch = float(config.get_performance(
            'ai_processing.timeout_per_batch', 60
        ))
        
        # Adaptive batching configuration
        self.adaptive_enabled = config.get_performance(
            'ai_processing.adaptive_batching.enabled', True
        )
        self.min_batch_size = int(config.get_performance(
            'ai_processing.adaptive_batching.min_batch_size', 5
        ))
        self.max_batch_size = int(config.get_performance(
            'ai_processing.adaptive_batching.max_batch_size', 20
        ))
        self.target_response_time = float(config.get_performance(
            'ai_processing.adaptive_batching.target_response_time', 5.0
        ))
        
        # Batch queue and processing state
        self.batch_queue: asyncio.Queue = asyncio.Queue()
        self.result_queue: asyncio.Queue = asyncio.Queue()
        self.processing_semaphore = asyncio.Semaphore(self.max_concurrent_batches)
        
        # Metrics for adaptive batching
        self.metrics = {
            'total_batches': 0,
            'total_items': 0,
            'total_time': 0.0,
            'recent_response_times': [],  # Last 10 batch response times
            'current_batch_size': self.batch_size
        }
        
        # Background tasks
        self.batch_collector_task: Optional[asyncio.Task] = None
        self.batch_processor_tasks: List[asyncio.Task] = []
        self._running = False
    
    async def start(self):
        """Start the batch processor"""
        if not self._running:
            self._running = True
            
        # Start batch collector
        self.batch_collector_task = asyncio.create_task(self._batch_collector())
        
        # Start multiple batch processors
        for i in range(self.max_concurrent_batches):
            task = asyncio.create_task(self._batch_processor(i))
            self.batch_processor_tasks.append(task)
        
        logger.info(f"BatchProcessor started with {self.max_concurrent_batches} workers")
    
    async def stop(self):
        """Stop the batch processor"""
        self._running = False
        
        # Cancel all tasks
        if self.batch_collector_task:
            self.batch_collector_task.cancel()
        
        for task in self.batch_processor_tasks:
            task.cancel()
        
        # Wait for cancellation
        all_tasks = [self.batch_collector_task] + self.batch_processor_tasks
        await asyncio.gather(*all_tasks, return_exceptions=True)
        
        logger.info("BatchProcessor stopped")
    
    async def add_item(self, filename: str, markdown_content: str) -> None:
        """
        Add an item for batch processing
        
        Args:
            filename: Name of the file
            markdown_content: Markdown content to process
        """
        item = BatchItem(filename=filename, markdown_content=markdown_content)
        await self.batch_queue.put(item)
    
    async def get_result(self) -> BatchResult:
        """Get a processing result"""
        return await self.result_queue.get()
    
    async def process_items_stream(
        self,
        items: List[Dict[str, Any]],
        model_key: str,
        custom_instructions: str,
        ai_model: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Process items and yield results as they complete
        
        Args:
            items: List of items with filename and markdown_content
            model_key: Model key for structured analysis
            custom_instructions: Custom instructions for analysis
            ai_model: AI model to use
            
        Yields:
            Processing results as they complete
        """
        # Store processing parameters for the batch
        self._current_model_key = model_key
        self._current_custom_instructions = custom_instructions
        self._current_ai_model = ai_model
        
        # Add all items to the queue
        for item in items:
            await self.add_item(item['filename'], item['markdown_content'])
        
        # Collect results
        results_received = 0
        while results_received < len(items):
            result = await self.get_result()
            
            # Convert to expected format
            yield {
                'filename': result.filename,
                'success': result.success,
                'structured_data': result.structured_data,
                'error': result.error,
                'processing_time': result.processing_time
            }
            
            results_received += 1
    
    async def _batch_collector(self):
        """Collect items into batches and send for processing"""
        while self._running:
            try:
                batch = []
                batch_start_time = time.time()
                
                # Determine current batch size (adaptive)
                current_batch_size = self._get_adaptive_batch_size()
                
                # Collect items until batch is full or timeout
                while len(batch) < current_batch_size:
                    try:
                        # Calculate remaining wait time
                        elapsed = time.time() - batch_start_time
                        remaining_wait = max(0, self.max_wait_time - elapsed)
                        
                        if remaining_wait <= 0 and batch:
                            # Timeout reached and we have items
                            break
                        
                        # Wait for item with timeout
                        item = await asyncio.wait_for(
                            self.batch_queue.get(),
                            timeout=min(remaining_wait, 0.1) if batch else None
                        )
                        batch.append(item)
                        
                    except asyncio.TimeoutError:
                        if batch:
                            # We have items and timeout reached
                            break
                        # No items yet, continue waiting
                
                if batch:
                    # Send batch for processing
                    await self._process_batch(batch)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in batch collector: {e}")
    
    async def _batch_processor(self, worker_id: int):
        """Process batches of items"""
        logger.debug(f"Batch processor {worker_id} started")
        
        while self._running:
            try:
                # This will be called by _process_batch
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in batch processor {worker_id}: {e}")
        
        logger.debug(f"Batch processor {worker_id} stopped")
    
    async def _process_batch(self, batch: List[BatchItem]):
        """Process a batch of items"""
        async with self.processing_semaphore:
            start_time = time.time()
            batch_size = len(batch)
            
            logger.info(f"Processing batch of {batch_size} items")
            
            try:
                # Process all items in the batch concurrently
                tasks = []
                for item in batch:
                    task = self._process_single_item(item)
                    tasks.append(task)
                
                # Wait for all with timeout
                results = await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=self.timeout_per_batch
                )
                
                # Send results to result queue
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        # Handle exception
                        await self.result_queue.put(BatchResult(
                            filename=batch[i].filename,
                            success=False,
                            error=str(result)
                        ))
                    else:
                        await self.result_queue.put(result)
                
                # Update metrics
                processing_time = time.time() - start_time
                self._update_metrics(batch_size, processing_time)
                
                logger.info(
                    f"Batch processed: {batch_size} items in {processing_time:.2f}s "
                    f"({processing_time/batch_size:.2f}s per item)"
                )
                
            except asyncio.TimeoutError:
                logger.error(f"Batch processing timeout after {self.timeout_per_batch}s")
                
                # Send timeout errors for all items
                for item in batch:
                    await self.result_queue.put(BatchResult(
                        filename=item.filename,
                        success=False,
                        error="Batch processing timeout"
                    ))
            
            except Exception as e:
                logger.error(f"Error processing batch: {e}")
                
                # Send errors for all items
                for item in batch:
                    await self.result_queue.put(BatchResult(
                        filename=item.filename,
                        success=False,
                        error=str(e)
                    ))
    
    async def _process_single_item(self, item: BatchItem) -> BatchResult:
        """Process a single item"""
        start_time = time.time()
        
        try:
            # Get the current processing parameters from the batch context
            # Note: In a full implementation, these would be passed through the batch
            # For now, we'll use defaults
            model_key = getattr(self, '_current_model_key', 'content_compliance')
            custom_instructions = getattr(self, '_current_custom_instructions', '')
            ai_model = getattr(self, '_current_ai_model', None)
            
            # Log token count for the markdown content with context
            log_token_count(item.filename, item.markdown_content, context='batch_analysis')
            
            # Use the actual analyzer
            result = await self.analyzer.analyze_content(
                item.markdown_content,
                model_key,
                custom_instructions,
                ai_model
            )
            
            processing_time = time.time() - start_time
            
            if result['success']:
                return BatchResult(
                    filename=item.filename,
                    success=True,
                    structured_data=result['result'],
                    processing_time=processing_time
                )
            else:
                return BatchResult(
                    filename=item.filename,
                    success=False,
                    error=result.get('error', 'Analysis failed'),
                    processing_time=processing_time
                )
            
        except Exception as e:
            return BatchResult(
                filename=item.filename,
                success=False,
                error=str(e),
                processing_time=time.time() - start_time
            )
    
    def _get_adaptive_batch_size(self) -> int:
        """Calculate adaptive batch size based on recent performance"""
        if not self.adaptive_enabled:
            return self.batch_size
        
        if len(self.metrics['recent_response_times']) < 3:
            # Not enough data, use configured size
            return self.metrics['current_batch_size']
        
        # Calculate average response time per item
        avg_response_time = sum(self.metrics['recent_response_times']) / len(
            self.metrics['recent_response_times']
        )
        
        # Adjust batch size to meet target response time
        if avg_response_time > self.target_response_time:
            # Decrease batch size
            new_size = max(
                self.min_batch_size,
                int(self.metrics['current_batch_size'] * 0.8)
            )
        elif avg_response_time < self.target_response_time * 0.5:
            # Increase batch size
            new_size = min(
                self.max_batch_size,
                int(self.metrics['current_batch_size'] * 1.2)
            )
        else:
            # Keep current size
            new_size = self.metrics['current_batch_size']
        
        if new_size != self.metrics['current_batch_size']:
            logger.info(
                f"Adjusting batch size from {self.metrics['current_batch_size']} "
                f"to {new_size} (avg response time: {avg_response_time:.2f}s)"
            )
            self.metrics['current_batch_size'] = new_size
        
        return new_size
    
    def _update_metrics(self, batch_size: int, processing_time: float):
        """Update processing metrics"""
        self.metrics['total_batches'] += 1
        self.metrics['total_items'] += batch_size
        self.metrics['total_time'] += processing_time
        
        # Update recent response times (keep last 10)
        response_time_per_item = processing_time / batch_size
        self.metrics['recent_response_times'].append(response_time_per_item)
        if len(self.metrics['recent_response_times']) > 10:
            self.metrics['recent_response_times'].pop(0)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get processing metrics"""
        avg_batch_size = (
            self.metrics['total_items'] / self.metrics['total_batches']
            if self.metrics['total_batches'] > 0
            else 0
        )
        
        avg_time_per_batch = (
            self.metrics['total_time'] / self.metrics['total_batches']
            if self.metrics['total_batches'] > 0
            else 0
        )
        
        avg_time_per_item = (
            self.metrics['total_time'] / self.metrics['total_items']
            if self.metrics['total_items'] > 0
            else 0
        )
        
        return {
            'total_batches': self.metrics['total_batches'],
            'total_items': self.metrics['total_items'],
            'average_batch_size': avg_batch_size,
            'current_batch_size': self.metrics['current_batch_size'],
            'average_time_per_batch': avg_time_per_batch,
            'average_time_per_item': avg_time_per_item,
            'total_processing_time': self.metrics['total_time']
        }
