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
    file_path: Optional[str] = None  # Path to original file (for images)
    is_image: bool = False  # Flag to indicate if this is an image file

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
    """
    Handles concurrent AI processing with direct item processing and caching.

    ARCHITECTURE CHANGE (2025-10):
    ===============================
    OLD: Items collected into batches → processed in groups → results queued
    NEW: Items processed immediately as available → semaphore controls concurrency

    KEY FEATURES:
    =============
    - Direct Processing: Files process immediately after markdown conversion
    - Concurrency Control: Semaphore limits concurrent AI API calls (max_concurrent_items)
    - Result Caching: Duplicate content returns instantly from cache
    - Streaming Support: Partial results yield before final completion

    ACTIVE CONFIGURATION:
    ====================
    - max_concurrent_items: Controls parallel AI API calls (default: 10)
    - item_semaphore: Enforces concurrency limit to prevent API overload
    - timeout_per_batch: Timeout per file (despite name, applies to individual items)

    DEPRECATED METHODS (kept for backward compatibility):
    ====================================================
    - add_item(), get_result(): Legacy batch queue interface (still used by tests)
    - process_items_stream(): Old batch-based streaming (use process_item_directly() instead)

    USE IN NEW CODE:
    ===============
    Use process_item_directly() which returns an AsyncGenerator for streaming results
    without batch collection delays.
    """

    def __init__(self, structured_analyzer_agent: StructuredAnalyzerAgent):
        self.analyzer = structured_analyzer_agent
        self.cache = None  # Will be initialized in start()

        # Load configuration
        # Item-level concurrency control (limits concurrent AI API calls)
        self.max_concurrent_items = int(
            config.get_performance("ai_processing.max_concurrent_items", 10)
        )

        # Item semaphore for concurrency control
        self.item_semaphore = (
            None  # Will be initialized in start() after event loop is running
        )

        # Token usage metrics
        self.metrics = {
            "total_usage": {
                "input_tokens": 0,
                "output_tokens": 0,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "total_tokens": 0,
                "requests": 0,
            },
        }

        self._running = False

    async def start(self):
        """Start the batch processor with direct processing mode"""
        if not self._running:
            self._running = True

        # Initialize item-level semaphore (must be created in async context)
        self.item_semaphore = asyncio.Semaphore(self.max_concurrent_items)

        # Initialize cache
        self.cache = await get_result_cache()

        logger.info(
            f"BatchProcessor started (direct processing mode), "
            f"max_concurrent_items={self.max_concurrent_items}"
        )

    async def stop(self):
        """Stop the batch processor"""
        self._running = False
        logger.info("BatchProcessor stopped")

    async def process_item_directly(
        self,
        filename: str,
        markdown_content: str,
        context: ProcessingContext,
        file_path: Optional[str] = None,
        is_image: bool = False,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Process a single item directly without batch collection.

        This bypasses the batch queue and processes items immediately
        as they become available, using the item semaphore for concurrency control.

        Args:
            filename: Name of the file
            markdown_content: Markdown content to process (None for images)
            context: Processing context with model parameters
            file_path: Path to original file (for images)
            is_image: Flag indicating if this is an image file

        Yields:
            Processing results (including partial updates if streaming enabled)
        """
        start_time = time.time()
        logger.info(f"[DIRECT] Starting direct processing for {filename}")

        # Use semaphore to limit concurrent AI API calls
        async with self.item_semaphore:
            logger.info(
                f"[DIRECT] Acquired semaphore for {filename} "
                f"(active: {self.max_concurrent_items - self.item_semaphore._value}/"
                f"{self.max_concurrent_items})"
            )

            try:
                # Check cache first
                if self.cache:
                    cached_result = await self.cache.get(
                        markdown_content, context.model_key, context.ai_model
                    )

                    if cached_result:
                        # Cache hit! Return immediately
                        processing_time = time.time() - start_time
                        logger.info(
                            f"[DIRECT] Cache HIT for {filename} (retrieved in {processing_time * 1000:.1f}ms)"
                        )
                        yield {
                            "filename": filename,
                            "success": True,
                            "structured_data": cached_result,
                            "processing_time": processing_time,
                            "final": True,
                            "usage": {"cached": True},
                        }
                        return

                # Cache miss - proceed with AI processing
                log_token_count(filename, markdown_content, context="direct_processing")

                # Check if partial streaming is enabled
                enable_partial = config.get(
                    "ai_pipeline.structured_analysis.streaming.enable_partial", False
                )

                if enable_partial:
                    # Use streaming analyzer for partial results
                    async for result in self.analyzer.analyze_content_stream(
                        markdown_content,
                        context.model_key,
                        context.custom_instructions,
                        context.ai_model,
                        file_path=file_path,
                        is_image=is_image,
                    ):
                        processing_time = time.time() - start_time

                        if result["success"]:
                            # Cache successful results (only on final result)
                            if result.get("final", True) and self.cache:
                                await self.cache.set(
                                    markdown_content,
                                    context.model_key,
                                    context.ai_model,
                                    result["result"],
                                    processing_time,
                                )

                            # Update metrics on final result
                            if result.get("final", True) and result.get("usage"):
                                self._update_usage_metrics(result["usage"])

                            yield {
                                "filename": filename,
                                "success": True,
                                "structured_data": result["result"],
                                "processing_time": processing_time,
                                "final": result.get("final", True),
                                "usage": result.get("usage"),
                            }
                        else:
                            yield {
                                "filename": filename,
                                "success": False,
                                "error": result.get("error", "Analysis failed"),
                                "processing_time": processing_time,
                                "final": result.get("final", True),
                                "usage": result.get("usage"),
                            }

                        # If this was the final result or an error, we're done
                        if result.get("final", True):
                            logger.info(
                                f"[DIRECT] Completed processing for {filename} "
                                f"in {processing_time:.2f}s (success={result['success']})"
                            )
                            break
                else:
                    # Use regular analyzer (non-streaming)
                    result = await self.analyzer.analyze_content(
                        markdown_content,
                        context.model_key,
                        context.custom_instructions,
                        context.ai_model,
                        file_path=file_path,
                        is_image=is_image,
                    )

                    processing_time = time.time() - start_time
                    logger.info(
                        f"[DIRECT] Completed processing for {filename} "
                        f"in {processing_time:.2f}s (success={result['success']})"
                    )

                    if result["success"]:
                        # Cache successful results
                        if self.cache:
                            await self.cache.set(
                                markdown_content,
                                context.model_key,
                                context.ai_model,
                                result["result"],
                                processing_time,
                            )

                        # Update metrics
                        if result.get("usage"):
                            self._update_usage_metrics(result["usage"])

                        yield {
                            "filename": filename,
                            "success": True,
                            "structured_data": result["result"],
                            "processing_time": processing_time,
                            "final": True,
                            "usage": result.get("usage"),
                        }
                    else:
                        yield {
                            "filename": filename,
                            "success": False,
                            "error": result.get("error", "Analysis failed"),
                            "processing_time": processing_time,
                            "final": True,
                            "usage": result.get("usage"),
                        }

            except Exception as e:
                # Handle any exceptions
                processing_time = time.time() - start_time
                logger.error(f"[DIRECT] Error processing {filename}: {e}")
                yield {
                    "filename": filename,
                    "success": False,
                    "error": str(e),
                    "processing_time": processing_time,
                    "final": True,
                }

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
        """Get token usage and cache metrics"""
        metrics = {
            "token_usage": self.metrics["total_usage"],
        }

        # Add cache metrics if available
        if self.cache:
            metrics["cache"] = self.cache.get_metrics()

        return metrics
