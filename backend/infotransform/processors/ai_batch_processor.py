"""
Batch processor for efficient AI processing with dynamic batching and caching
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, AsyncGenerator
from dataclasses import dataclass

from infotransform.config import config
from infotransform.processors.structured_analyzer_agent import StructuredAnalyzerAgent
from infotransform.utils.token_counter import log_token_count
from infotransform.utils.result_cache import get_result_cache

logger = logging.getLogger(__name__)


@dataclass
class ProcessingContext:
    """Processing parameters for a batch"""

    model_key: str
    custom_instructions: str
    ai_model: str


@dataclass
class BatchItem:
    """Item to be processed in a batch"""

    filename: str
    markdown_content: str
    context: ProcessingContext
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


@dataclass
class Batch:
    """A batch of items with shared processing context"""

    items: List["BatchItem"]
    context: ProcessingContext
    created_at: float = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()


@dataclass
class BatchResult:
    """Result from batch processing"""

    filename: str
    success: bool
    structured_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: float = 0.0
    final: bool = True  # Indicates if this is the final result or a partial update
    usage: Optional[Dict[str, Any]] = None  # Token usage information


class BatchProcessor:
    """Handles batch processing of markdown content for AI analysis with caching"""

    def __init__(self, structured_analyzer_agent: StructuredAnalyzerAgent):
        self.analyzer = structured_analyzer_agent
        self.cache = None  # Will be initialized in start()

        # Load configuration
        self.batch_size = int(config.get_performance("ai_processing.batch_size", 10))
        self.max_wait_time = float(
            config.get_performance("ai_processing.max_wait_time", 2.0)
        )
        self.max_concurrent_batches = int(
            config.get_performance("ai_processing.max_concurrent_batches", 3)
        )
        self.timeout_per_batch = float(
            config.get_performance("ai_processing.timeout_per_batch", 60)
        )

        # Adaptive batching configuration
        self.adaptive_enabled = config.get_performance(
            "ai_processing.adaptive_batching.enabled", True
        )
        self.min_batch_size = int(
            config.get_performance("ai_processing.adaptive_batching.min_batch_size", 5)
        )
        self.max_batch_size = int(
            config.get_performance("ai_processing.adaptive_batching.max_batch_size", 20)
        )
        self.target_response_time = float(
            config.get_performance(
                "ai_processing.adaptive_batching.target_response_time", 5.0
            )
        )

        # Batch queue and processing state
        self.batch_queue: asyncio.Queue[BatchItem] = asyncio.Queue()
        self.result_queue: asyncio.Queue[BatchResult] = asyncio.Queue()
        self.processing_semaphore = asyncio.Semaphore(self.max_concurrent_batches)

        # Metrics for adaptive batching
        self.metrics = {
            "total_batches": 0,
            "total_items": 0,
            "total_time": 0.0,
            "recent_response_times": [],  # Last 10 batch response times
            "current_batch_size": self.batch_size,
            "total_usage": {
                "input_tokens": 0,
                "output_tokens": 0,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "total_tokens": 0,
                "requests": 0,
            },
        }

        # Background tasks
        self.batch_collector_task: Optional[asyncio.Task] = None
        self.batch_processor_tasks: List[asyncio.Task] = []
        self._running = False

    async def start(self):
        """Start the batch processor"""
        if not self._running:
            self._running = True

        # Initialize cache
        self.cache = await get_result_cache()

        # Start batch collector
        self.batch_collector_task = asyncio.create_task(self._batch_collector())

        # Start multiple batch processors
        for i in range(self.max_concurrent_batches):
            task = asyncio.create_task(self._batch_processor(i))
            self.batch_processor_tasks.append(task)

        logger.info(
            f"BatchProcessor started with {self.max_concurrent_batches} workers"
        )

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

    async def add_item(
        self, filename: str, markdown_content: str, context: ProcessingContext
    ) -> None:
        """
        Add an item for batch processing

        Args:
            filename: Name of the file
            markdown_content: Markdown content to process
            context: Processing context with model parameters
        """
        item = BatchItem(
            filename=filename, markdown_content=markdown_content, context=context
        )
        await self.batch_queue.put(item)

    async def get_result(self) -> BatchResult:
        """Get a processing result"""
        return await self.result_queue.get()

    async def process_items_stream(
        self,
        items: List[Dict[str, Any]],
        model_key: str,
        custom_instructions: str,
        ai_model: str,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Process items and yield results as they complete

        Args:
            items: List of items with filename and markdown_content
            model_key: Model key for structured analysis
            custom_instructions: Custom instructions for analysis
            ai_model: AI model to use

        Yields:
            Processing results as they complete (including partial updates)
        """
        # Create processing context
        context = ProcessingContext(
            model_key=model_key,
            custom_instructions=custom_instructions,
            ai_model=ai_model,
        )

        # Add all items to the queue with context
        for item in items:
            await self.add_item(item["filename"], item["markdown_content"], context)

        # Track which files have sent their final result
        final_results_received = set()
        total_final_results_needed = len(items)

        # Collect results (including partial updates)
        while len(final_results_received) < total_final_results_needed:
            result = await self.get_result()

            # Convert to expected format
            yield_result = {
                "filename": result.filename,
                "success": result.success,
                "structured_data": result.structured_data,
                "error": result.error,
                "processing_time": result.processing_time,
                "final": result.final,
                "usage": result.usage,
            }

            # Aggregate usage for final results
            if result.final and result.usage:
                self._update_usage_metrics(result.usage)

            # Track final results
            if result.final:
                final_results_received.add(result.filename)

            yield yield_result

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
                            timeout=min(remaining_wait, 0.1) if batch else None,
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

            # Get model key from first item for logging (all items in batch should have same context)
            model_key = batch[0].context.model_key if batch else "unknown"
            logger.info(
                f"Processing batch of {batch_size} items with model: {model_key}"
            )

            try:
                # Process all items in the batch concurrently and stream results as they complete
                tasks = []
                for item in batch:
                    task = self._process_and_enqueue_item(item)
                    tasks.append(task)

                # Wait for all with timeout
                await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=self.timeout_per_batch,
                )

                # Update metrics
                processing_time = time.time() - start_time
                self._update_metrics(batch_size, processing_time)

                logger.info(
                    f"Batch processed: {batch_size} items in {processing_time:.2f}s "
                    f"({processing_time / batch_size:.2f}s per item)"
                )

            except asyncio.TimeoutError:
                logger.error(
                    f"Batch processing timeout after {self.timeout_per_batch}s"
                )

                # Send timeout errors for any remaining items
                # (items that completed will have already been enqueued)
                for item in batch:
                    await self.result_queue.put(
                        BatchResult(
                            filename=item.filename,
                            success=False,
                            error="Batch processing timeout",
                        )
                    )

            except Exception as e:
                logger.error(f"Error processing batch: {e}")

                # Send errors for all items
                for item in batch:
                    await self.result_queue.put(
                        BatchResult(filename=item.filename, success=False, error=str(e))
                    )

    async def _process_and_enqueue_item(self, item: BatchItem):
        """Process a single item and immediately enqueue the result (with caching)"""
        start_time = time.time()

        try:
            # Extract processing parameters from the item's context
            context = item.context

            # Check cache first
            if self.cache:
                cached_result = await self.cache.get(
                    item.markdown_content, context.model_key, context.ai_model
                )

                if cached_result:
                    # Cache hit! Return immediately
                    processing_time = time.time() - start_time
                    await self.result_queue.put(
                        BatchResult(
                            filename=item.filename,
                            success=True,
                            structured_data=cached_result,
                            processing_time=processing_time,
                            final=True,
                            usage={"cached": True},  # Special flag for cache hits
                        )
                    )
                    logger.info(
                        f"Cache HIT for {item.filename} (retrieved in {processing_time * 1000:.1f}ms)"
                    )
                    return

            # Cache miss - proceed with AI processing
            # Log token count for the markdown content with context
            log_token_count(
                item.filename, item.markdown_content, context="batch_analysis"
            )

            # Check if partial streaming is enabled
            enable_partial = config.get(
                "ai_pipeline.structured_analysis.streaming.enable_partial", False
            )

            if enable_partial:
                # Use streaming analyzer for partial results
                async for result in self.analyzer.analyze_content_stream(
                    item.markdown_content,
                    context.model_key,
                    context.custom_instructions,
                    context.ai_model,
                ):
                    processing_time = time.time() - start_time

                    if result["success"]:
                        # Cache successful results (only on final result)
                        if result.get("final", True) and self.cache:
                            await self.cache.set(
                                item.markdown_content,
                                context.model_key,
                                context.ai_model,
                                result["result"],
                                processing_time,
                            )

                        await self.result_queue.put(
                            BatchResult(
                                filename=item.filename,
                                success=True,
                                structured_data=result["result"],
                                processing_time=processing_time,
                                final=result.get("final", True),
                                usage=result.get("usage"),
                            )
                        )
                    else:
                        await self.result_queue.put(
                            BatchResult(
                                filename=item.filename,
                                success=False,
                                error=result.get("error", "Analysis failed"),
                                processing_time=processing_time,
                                final=result.get("final", True),
                                usage=result.get("usage"),
                            )
                        )

                    # If this was the final result or an error, we're done
                    if result.get("final", True):
                        break
            else:
                # Use regular analyzer (non-streaming)
                result = await self.analyzer.analyze_content(
                    item.markdown_content,
                    context.model_key,
                    context.custom_instructions,
                    context.ai_model,
                )

                processing_time = time.time() - start_time

                if result["success"]:
                    # Cache successful results
                    if self.cache:
                        await self.cache.set(
                            item.markdown_content,
                            context.model_key,
                            context.ai_model,
                            result["result"],
                            processing_time,
                        )

                    await self.result_queue.put(
                        BatchResult(
                            filename=item.filename,
                            success=True,
                            structured_data=result["result"],
                            processing_time=processing_time,
                            final=True,
                            usage=result.get("usage"),
                        )
                    )
                else:
                    await self.result_queue.put(
                        BatchResult(
                            filename=item.filename,
                            success=False,
                            error=result.get("error", "Analysis failed"),
                            processing_time=processing_time,
                            final=True,
                            usage=result.get("usage"),
                        )
                    )

        except Exception as e:
            # Handle any exceptions and enqueue error result
            await self.result_queue.put(
                BatchResult(
                    filename=item.filename,
                    success=False,
                    error=str(e),
                    processing_time=time.time() - start_time,
                    final=True,
                )
            )

    async def _process_single_item(self, item: BatchItem) -> BatchResult:
        """Process a single item with its processing context"""
        start_time = time.time()

        try:
            # Extract processing parameters from the item's context
            context = item.context

            # Log token count for the markdown content with context
            log_token_count(
                item.filename, item.markdown_content, context="batch_analysis"
            )

            # Use the actual analyzer with context parameters
            result = await self.analyzer.analyze_content(
                item.markdown_content,
                context.model_key,
                context.custom_instructions,
                context.ai_model,
            )

            processing_time = time.time() - start_time

            if result["success"]:
                return BatchResult(
                    filename=item.filename,
                    success=True,
                    structured_data=result["result"],
                    processing_time=processing_time,
                )
            else:
                return BatchResult(
                    filename=item.filename,
                    success=False,
                    error=result.get("error", "Analysis failed"),
                    processing_time=processing_time,
                )

        except Exception as e:
            return BatchResult(
                filename=item.filename,
                success=False,
                error=str(e),
                processing_time=time.time() - start_time,
            )

    def _get_adaptive_batch_size(self) -> int:
        """Calculate adaptive batch size based on recent performance"""
        if not self.adaptive_enabled:
            return self.batch_size

        if len(self.metrics["recent_response_times"]) < 3:
            # Not enough data, use configured size
            return self.metrics["current_batch_size"]

        # Calculate average response time per item
        avg_response_time = sum(self.metrics["recent_response_times"]) / len(
            self.metrics["recent_response_times"]
        )

        # Adjust batch size to meet target response time
        if avg_response_time > self.target_response_time:
            # Decrease batch size
            new_size = max(
                self.min_batch_size, int(self.metrics["current_batch_size"] * 0.8)
            )
        elif avg_response_time < self.target_response_time * 0.5:
            # Increase batch size
            new_size = min(
                self.max_batch_size, int(self.metrics["current_batch_size"] * 1.2)
            )
        else:
            # Keep current size
            new_size = self.metrics["current_batch_size"]

        if new_size != self.metrics["current_batch_size"]:
            logger.info(
                f"Adjusting batch size from {self.metrics['current_batch_size']} "
                f"to {new_size} (avg response time: {avg_response_time:.2f}s)"
            )
            self.metrics["current_batch_size"] = new_size

        return new_size

    def _update_metrics(self, batch_size: int, processing_time: float):
        """Update processing metrics"""
        self.metrics["total_batches"] += 1
        self.metrics["total_items"] += batch_size
        self.metrics["total_time"] += processing_time

        # Update recent response times (keep last 10)
        response_time_per_item = processing_time / batch_size
        self.metrics["recent_response_times"].append(response_time_per_item)
        if len(self.metrics["recent_response_times"]) > 10:
            self.metrics["recent_response_times"].pop(0)

    def _update_usage_metrics(self, usage: Dict[str, Any]):
        """Update token usage metrics"""
        if not usage:
            return

        total_usage = self.metrics["total_usage"]
        total_usage["input_tokens"] += usage.get("input_tokens", 0)
        total_usage["output_tokens"] += usage.get("output_tokens", 0)
        total_usage["cache_read_tokens"] += usage.get("cache_read_tokens", 0)
        total_usage["cache_write_tokens"] += usage.get("cache_write_tokens", 0)
        total_usage["total_tokens"] += usage.get("total_tokens", 0)
        total_usage["requests"] += usage.get("requests", 0)

    def get_metrics(self) -> Dict[str, Any]:
        """Get processing metrics including cache statistics"""
        avg_batch_size = (
            self.metrics["total_items"] / self.metrics["total_batches"]
            if self.metrics["total_batches"] > 0
            else 0
        )

        avg_time_per_batch = (
            self.metrics["total_time"] / self.metrics["total_batches"]
            if self.metrics["total_batches"] > 0
            else 0
        )

        avg_time_per_item = (
            self.metrics["total_time"] / self.metrics["total_items"]
            if self.metrics["total_items"] > 0
            else 0
        )

        metrics = {
            "total_batches": self.metrics["total_batches"],
            "total_items": self.metrics["total_items"],
            "average_batch_size": avg_batch_size,
            "current_batch_size": self.metrics["current_batch_size"],
            "average_time_per_batch": avg_time_per_batch,
            "average_time_per_item": avg_time_per_item,
            "total_processing_time": self.metrics["total_time"],
            "token_usage": self.metrics["total_usage"],
        }

        # Add cache metrics if available
        if self.cache:
            metrics["cache"] = self.cache.get_metrics()

        return metrics
