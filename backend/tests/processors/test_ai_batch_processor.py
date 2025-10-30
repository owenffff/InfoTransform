"""
Unit tests for AI Batch Processor
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from infotransform.processors.ai_batch_processor import (
    BatchProcessor,
    ProcessingContext,
    BatchItem,
    Batch,
    BatchResult,
)


@pytest.mark.processor
class TestBatchProcessor:
    """Test BatchProcessor functionality"""

    @pytest.fixture
    def mock_structured_analyzer(self):
        """Create mock structured analyzer"""
        mock_analyzer = MagicMock()

        async def mock_analyze(
            content, model_key, custom_instructions=None, ai_model=None
        ):
            return {
                "success": True,
                "result": {"field1": "value1", "field2": "value2"},
                "usage": {
                    "input_tokens": 100,
                    "output_tokens": 50,
                    "total_tokens": 150,
                    "cache_read_tokens": 0,
                    "cache_write_tokens": 0,
                    "requests": 1,
                },
            }

        mock_analyzer.analyze_content = AsyncMock(side_effect=mock_analyze)
        return mock_analyzer

    @pytest.fixture
    def batch_processor(self, mock_structured_analyzer):
        """Create batch processor with mocked analyzer"""
        return BatchProcessor(mock_structured_analyzer)

    @pytest.mark.asyncio
    async def test_batch_processor_initialization(self, batch_processor):
        """Test batch processor initializes correctly"""
        assert batch_processor is not None
        assert batch_processor.analyzer is not None
        assert batch_processor.batch_size > 0
        assert batch_processor.max_wait_time > 0

    @pytest.mark.asyncio
    async def test_batch_processor_start_stop(self, batch_processor):
        """Test batch processor lifecycle"""
        # Start processor
        await batch_processor.start()
        assert batch_processor._running is True

        # Stop processor
        await batch_processor.stop()
        assert batch_processor._running is False

    @pytest.mark.asyncio
    async def test_add_item_to_queue(self, batch_processor):
        """Test adding items to batch queue"""
        await batch_processor.start()

        context = ProcessingContext(
            model_key="invoice", custom_instructions="", ai_model="gpt-4o"
        )

        await batch_processor.add_item("test.txt", "content", context)

        # Queue should have one item
        assert batch_processor.batch_queue.qsize() == 1

        await batch_processor.stop()

    @pytest.mark.asyncio
    async def test_process_items_stream(self, batch_processor, sample_markdown_content):
        """Test streaming processing of items"""
        await batch_processor.start()

        items = [
            {"filename": "file1.txt", "markdown_content": sample_markdown_content},
            {"filename": "file2.txt", "markdown_content": sample_markdown_content},
        ]

        results = []
        async for result in batch_processor.process_items_stream(
            items, "invoice", "", "gpt-4o"
        ):
            results.append(result)

        # Should have 2 results
        assert len(results) == 2
        assert all(r["success"] for r in results)
        assert all(r["final"] for r in results)

        await batch_processor.stop()

    @pytest.mark.asyncio
    async def test_batch_metrics(self, batch_processor, sample_markdown_content):
        """Test batch processing metrics"""
        await batch_processor.start()

        items = [{"filename": "file1.txt", "markdown_content": sample_markdown_content}]

        results = []
        async for result in batch_processor.process_items_stream(
            items, "invoice", "", "gpt-4o"
        ):
            results.append(result)

        # Get metrics
        metrics = batch_processor.get_metrics()

        assert "total_batches" in metrics
        assert "total_items" in metrics
        assert "token_usage" in metrics
        assert metrics["token_usage"]["total_tokens"] > 0

        await batch_processor.stop()

    @pytest.mark.asyncio
    async def test_batch_timeout_handling(self, batch_processor):
        """Test batch processing timeout"""
        await batch_processor.start()

        # Create mock analyzer that times out
        async def slow_analyze(*args, **kwargs):
            await asyncio.sleep(10)  # Longer than timeout
            return {"success": True, "result": {}}

        batch_processor.analyzer.analyze_content = AsyncMock(side_effect=slow_analyze)

        # Set very short timeout for testing
        batch_processor.timeout_per_batch = 0.1

        items = [{"filename": "file1.txt", "markdown_content": "content"}]

        results = []
        async for result in batch_processor.process_items_stream(
            items, "invoice", "", "gpt-4o"
        ):
            results.append(result)

        # Should have error result
        assert len(results) == 1
        assert (
            results[0]["success"] is False
            or "timeout" in results[0].get("error", "").lower()
        )

        await batch_processor.stop()

    def test_get_adaptive_batch_size(self, batch_processor):
        """Test adaptive batch size calculation"""
        # With no metrics, should return configured size
        batch_size = batch_processor._get_adaptive_batch_size()
        assert batch_size == batch_processor.batch_size

        # Add some metrics
        batch_processor.metrics["recent_response_times"] = [1.0, 1.5, 2.0]
        batch_processor.metrics["current_batch_size"] = 10

        # Should calculate adaptive size
        batch_size = batch_processor._get_adaptive_batch_size()
        assert isinstance(batch_size, int)
        assert batch_size >= batch_processor.min_batch_size
        assert batch_size <= batch_processor.max_batch_size

    def test_update_metrics(self, batch_processor):
        """Test metrics updating"""
        initial_batches = batch_processor.metrics["total_batches"]
        initial_items = batch_processor.metrics["total_items"]

        batch_processor._update_metrics(5, 2.5)

        assert batch_processor.metrics["total_batches"] == initial_batches + 1
        assert batch_processor.metrics["total_items"] == initial_items + 5
        assert len(batch_processor.metrics["recent_response_times"]) > 0

    def test_update_usage_metrics(self, batch_processor):
        """Test usage metrics updating"""
        usage = {
            "input_tokens": 100,
            "output_tokens": 50,
            "cache_read_tokens": 10,
            "cache_write_tokens": 5,
            "total_tokens": 150,
            "requests": 1,
        }

        initial_tokens = batch_processor.metrics["total_usage"]["total_tokens"]
        batch_processor._update_usage_metrics(usage)

        assert (
            batch_processor.metrics["total_usage"]["total_tokens"]
            == initial_tokens + 150
        )
        assert batch_processor.metrics["total_usage"]["input_tokens"] == 100
        assert batch_processor.metrics["total_usage"]["output_tokens"] == 50


@pytest.mark.unit
class TestBatchDataClasses:
    """Test batch processing data classes"""

    def test_processing_context(self):
        """Test ProcessingContext dataclass"""
        context = ProcessingContext(
            model_key="invoice", custom_instructions="test", ai_model="gpt-4o"
        )

        assert context.model_key == "invoice"
        assert context.custom_instructions == "test"
        assert context.ai_model == "gpt-4o"

    def test_batch_item(self):
        """Test BatchItem dataclass"""
        context = ProcessingContext(
            model_key="invoice", custom_instructions="", ai_model="gpt-4o"
        )

        item = BatchItem(
            filename="test.txt", markdown_content="content", context=context
        )

        assert item.filename == "test.txt"
        assert item.markdown_content == "content"
        assert item.timestamp is not None

    def test_batch(self):
        """Test Batch dataclass"""
        context = ProcessingContext(
            model_key="invoice", custom_instructions="", ai_model="gpt-4o"
        )

        item = BatchItem(
            filename="test.txt", markdown_content="content", context=context
        )

        batch = Batch(items=[item], context=context)

        assert len(batch.items) == 1
        assert batch.created_at is not None

    def test_batch_result(self):
        """Test BatchResult dataclass"""
        result = BatchResult(
            filename="test.txt",
            success=True,
            structured_data={"field": "value"},
            processing_time=1.0,
        )

        assert result.filename == "test.txt"
        assert result.success is True
        assert result.structured_data == {"field": "value"}
        assert result.processing_time == 1.0
        assert result.final is True


@pytest.mark.integration
class TestBatchProcessorIntegration:
    """Integration tests for batch processor"""

    @pytest.mark.asyncio
    async def test_full_batch_processing_flow(
        self, mock_structured_analyzer, sample_markdown_content
    ):
        """Test complete batch processing flow"""
        processor = BatchProcessor(mock_structured_analyzer)

        await processor.start()

        # Process multiple items
        items = [
            {"filename": f"file{i}.txt", "markdown_content": sample_markdown_content}
            for i in range(5)
        ]

        results = []
        async for result in processor.process_items_stream(
            items, "invoice", "Extract invoice data", "gpt-4o"
        ):
            results.append(result)

        # Should have 5 results
        assert len(results) == 5
        assert all(r["success"] for r in results)

        # Check metrics
        metrics = processor.get_metrics()
        assert metrics["total_items"] == 5

        await processor.stop()

    @pytest.mark.asyncio
    async def test_concurrent_batch_processing(
        self, mock_structured_analyzer, sample_markdown_content
    ):
        """Test processing multiple batches concurrently"""
        processor = BatchProcessor(mock_structured_analyzer)
        processor.max_concurrent_batches = 2

        await processor.start()

        # Process many items to trigger multiple batches
        items = [
            {"filename": f"file{i}.txt", "markdown_content": sample_markdown_content}
            for i in range(20)
        ]

        results = []
        async for result in processor.process_items_stream(
            items, "invoice", "", "gpt-4o"
        ):
            results.append(result)

        # Should have 20 results
        assert len(results) == 20

        await processor.stop()

    @pytest.mark.asyncio
    @patch("infotransform.config.config.get")
    async def test_partial_streaming_enabled(
        self, mock_config_get, mock_structured_analyzer, sample_markdown_content
    ):
        """Test partial streaming when enabled"""

        # Configure partial streaming
        def config_side_effect(key, default=None):
            if key == "ai_pipeline.structured_analysis.streaming.enable_partial":
                return True
            return default

        mock_config_get.side_effect = config_side_effect

        # Mock analyzer with streaming support
        async def mock_analyze_stream(
            content, model_key, custom_instructions, ai_model
        ):
            # Yield partial result
            yield {
                "success": True,
                "result": {"field1": "value1"},
                "final": False,
                "usage": None,
            }
            # Yield final result
            yield {
                "success": True,
                "result": {"field1": "value1", "field2": "value2"},
                "final": True,
                "usage": {
                    "input_tokens": 100,
                    "output_tokens": 50,
                    "total_tokens": 150,
                },
            }

        mock_structured_analyzer.analyze_content_stream = mock_analyze_stream

        processor = BatchProcessor(mock_structured_analyzer)
        await processor.start()

        items = [{"filename": "file1.txt", "markdown_content": sample_markdown_content}]

        results = []
        async for result in processor.process_items_stream(
            items, "invoice", "", "gpt-4o"
        ):
            results.append(result)

        # Should have partial and final results
        assert len(results) >= 1
        # Final result should exist
        assert any(r["final"] for r in results)

        await processor.stop()


@pytest.mark.unit
class TestParallelProcessing:
    """Test parallel processing functionality with semaphore"""

    @pytest.fixture
    def mock_structured_analyzer_with_delay(self):
        """Create mock analyzer with simulated processing delay"""
        mock_analyzer = MagicMock()

        async def mock_analyze_with_delay(
            content, model_key, custom_instructions=None, ai_model=None, **kwargs
        ):
            # Simulate AI processing time
            await asyncio.sleep(0.1)
            return {
                "success": True,
                "result": {"field1": "value1", "field2": "value2"},
                "usage": {
                    "input_tokens": 100,
                    "output_tokens": 50,
                    "total_tokens": 150,
                    "cache_read_tokens": 0,
                    "cache_write_tokens": 0,
                    "requests": 1,
                },
            }

        mock_analyzer.analyze_content = AsyncMock(side_effect=mock_analyze_with_delay)
        return mock_analyzer

    @pytest.mark.asyncio
    async def test_semaphore_initialization(self, mock_structured_analyzer):
        """Test that item semaphore is properly initialized"""
        processor = BatchProcessor(mock_structured_analyzer)

        # Before start, semaphore should be None
        assert processor.item_semaphore is None

        # After start, semaphore should be initialized
        await processor.start()
        assert processor.item_semaphore is not None
        assert processor.item_semaphore._value == processor.max_concurrent_items

        await processor.stop()

    @pytest.mark.asyncio
    async def test_max_concurrent_items_configuration(self, mock_structured_analyzer):
        """Test that max_concurrent_items is read from configuration"""
        with patch("infotransform.config.config.get_performance") as mock_get_perf:
            mock_get_perf.return_value = 5

            processor = BatchProcessor(mock_structured_analyzer)

            # Should use the configured value
            assert processor.max_concurrent_items == 5

    @pytest.mark.asyncio
    async def test_concurrent_processing_timing(
        self, mock_structured_analyzer_with_delay, sample_markdown_content
    ):
        """Test that items are processed concurrently, not sequentially"""
        processor = BatchProcessor(mock_structured_analyzer_with_delay)
        processor.max_concurrent_items = 5

        await processor.start()

        # Process 5 items (each takes 0.1s)
        items = [
            {"filename": f"file{i}.txt", "markdown_content": sample_markdown_content}
            for i in range(5)
        ]

        import time

        start_time = time.time()

        results = []
        async for result in processor.process_items_stream(
            items, "invoice", "", "gpt-4o"
        ):
            results.append(result)

        elapsed_time = time.time() - start_time

        # If concurrent: ~0.1s (all at once)
        # If sequential: ~0.5s (5 × 0.1s)
        # Allow some overhead, but should be much less than sequential
        assert len(results) == 5
        assert all(r["success"] for r in results)

        # With 5 concurrent workers and 5 items, should complete in ~0.1-0.3s
        # (much less than 0.5s sequential time)
        assert elapsed_time < 0.4, (
            f"Processing took {elapsed_time:.2f}s, expected < 0.4s for concurrent execution. "
            f"Sequential would take ~0.5s"
        )

        await processor.stop()

    @pytest.mark.asyncio
    async def test_concurrent_processing_with_many_items(
        self, mock_structured_analyzer_with_delay, sample_markdown_content
    ):
        """Test concurrent processing with more items than workers"""
        processor = BatchProcessor(mock_structured_analyzer_with_delay)
        processor.max_concurrent_items = 3  # Limit to 3 concurrent

        await processor.start()

        # Process 9 items (3 rounds of 3)
        items = [
            {"filename": f"file{i}.txt", "markdown_content": sample_markdown_content}
            for i in range(9)
        ]

        import time

        start_time = time.time()

        results = []
        async for result in processor.process_items_stream(
            items, "invoice", "", "gpt-4o"
        ):
            results.append(result)

        elapsed_time = time.time() - start_time

        # If concurrent with 3 workers: ~0.3s (3 rounds × 0.1s)
        # If sequential: ~0.9s (9 × 0.1s)
        assert len(results) == 9
        assert all(r["success"] for r in results)

        # Should complete in ~0.3-0.5s (3 rounds), much less than 0.9s sequential
        assert elapsed_time < 0.6, (
            f"Processing took {elapsed_time:.2f}s, expected < 0.6s for concurrent execution. "
            f"Sequential would take ~0.9s"
        )

        await processor.stop()

    @pytest.mark.asyncio
    async def test_semaphore_limits_concurrency(
        self, mock_structured_analyzer, sample_markdown_content
    ):
        """Test that semaphore actually limits concurrent processing"""
        processor = BatchProcessor(mock_structured_analyzer)
        processor.max_concurrent_items = 2  # Limit to 2 concurrent

        await processor.start()

        # Track concurrent execution
        concurrent_count = 0
        max_concurrent = 0
        lock = asyncio.Lock()

        async def mock_analyze_with_tracking(*args, **kwargs):
            nonlocal concurrent_count, max_concurrent

            async with lock:
                concurrent_count += 1
                max_concurrent = max(max_concurrent, concurrent_count)

            await asyncio.sleep(0.05)  # Simulate work

            async with lock:
                concurrent_count -= 1

            return {
                "success": True,
                "result": {"field": "value"},
                "usage": {"total_tokens": 100},
            }

        processor.analyzer.analyze_content = AsyncMock(
            side_effect=mock_analyze_with_tracking
        )

        # Process 10 items
        items = [
            {"filename": f"file{i}.txt", "markdown_content": sample_markdown_content}
            for i in range(10)
        ]

        results = []
        async for result in processor.process_items_stream(
            items, "invoice", "", "gpt-4o"
        ):
            results.append(result)

        # Verify all processed
        assert len(results) == 10

        # Verify concurrency was limited to 2
        assert max_concurrent <= 2, (
            f"Max concurrent was {max_concurrent}, expected <= 2"
        )

        await processor.stop()

    @pytest.mark.asyncio
    async def test_diagnostic_logging(
        self, mock_structured_analyzer, sample_markdown_content, caplog
    ):
        """Test that diagnostic logging is present"""
        import logging

        caplog.set_level(logging.INFO)

        processor = BatchProcessor(mock_structured_analyzer)
        await processor.start()

        items = [{"filename": "test.txt", "markdown_content": sample_markdown_content}]

        results = []
        async for result in processor.process_items_stream(
            items, "invoice", "", "gpt-4o"
        ):
            results.append(result)

        # Check for concurrent logging
        log_messages = [record.message for record in caplog.records]

        # Should have logs about concurrent processing
        assert any("[CONCURRENT]" in msg for msg in log_messages), (
            "Expected [CONCURRENT] logs but didn't find any"
        )

        # Should have logs about starting AI processing
        assert any(
            "[CONCURRENT] Starting AI processing" in msg for msg in log_messages
        ), "Expected 'Starting AI processing' log"

        # Should have logs about completed AI processing
        assert any(
            "[CONCURRENT] Completed AI processing" in msg for msg in log_messages
        ), "Expected 'Completed AI processing' log"

        await processor.stop()
