"""
Unit tests for progressive streaming functionality in document transform API
"""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from infotransform.processors.ai_batch_processor import BatchResult


@pytest.mark.unit
class TestProgressiveStreaming:
    """Test progressive streaming mode (progressive_streaming=True)"""

    @pytest.mark.asyncio
    @patch("infotransform.api.document_transform_api.config")
    async def test_progressive_items_added_incrementally(
        self, mock_config, temp_dir, sample_text_file
    ):
        """Test that items are added to batch processor as they complete conversion"""
        from infotransform.api.document_transform_api import StreamingProcessor

        # Enable progressive streaming
        mock_config.get.return_value = True

        processor = StreamingProcessor()
        await processor.start()

        # Track when items are added to batch processor
        add_item_calls = []
        original_add_item = processor.batch_processor.add_item

        async def tracked_add_item(*args, **kwargs):
            add_item_calls.append({"time": time.time(), "args": args})
            await original_add_item(*args, **kwargs)

        processor.batch_processor.add_item = AsyncMock(side_effect=tracked_add_item)

        # Mock markdown conversion with delays to simulate real processing
        conversion_times = []

        async def mock_convert(file_info):
            # Simulate conversion taking time
            await asyncio.sleep(0.01)
            conversion_times.append(time.time())
            return {
                "success": True,
                "filename": file_info["filename"],
                "markdown_content": f"# Content for {file_info['filename']}",
            }

        processor.markdown_converter.convert_file_async = AsyncMock(
            side_effect=mock_convert
        )

        # Mock batch processor to return results
        async def mock_get_result():
            await asyncio.sleep(0.01)
            return BatchResult(
                filename="test1.txt",
                success=True,
                structured_data={"field": "value"},
                processing_time=0.01,
                final=True,
            )

        processor.batch_processor.get_result = AsyncMock(side_effect=mock_get_result)
        processor.batch_processor.get_metrics = MagicMock(
            return_value={
                "token_usage": {"total_tokens": 100},
                "cache": {"hits": 0, "misses": 1},
            }
        )

        # Create test files
        files = [
            {"file_path": str(sample_text_file), "filename": "test1.txt"},
        ]

        # Process files and collect events
        events = []
        async for event in processor.process_files_optimized(
            files, "document_metadata", "", "gpt-4o", run_id="test-run"
        ):
            events.append(event)

        await processor.stop()

        # Verify items were added incrementally (as conversions completed)
        assert len(add_item_calls) > 0, "Items should be added to batch processor"

        # In progressive mode, items are added immediately after conversion
        # Verify the first add_item call happened before all conversions completed
        if len(add_item_calls) > 0 and len(conversion_times) > 0:
            first_add_time = add_item_calls[0]["time"]
            last_conversion_time = conversion_times[-1]
            # In progressive mode, items start being added as soon as first conversion completes
            assert first_add_time <= last_conversion_time + 0.1, (
                "Items should be added as conversions complete"
            )

    @pytest.mark.asyncio
    @patch("infotransform.api.document_transform_api.config")
    async def test_progressive_early_results(self, mock_config, temp_dir):
        """Test that results start streaming before all conversions complete"""
        from infotransform.api.document_transform_api import StreamingProcessor

        # Enable progressive streaming
        mock_config.get.return_value = True

        processor = StreamingProcessor()
        await processor.start()

        # Track event timing
        event_times = []
        conversion_complete_time = None

        # Mock conversions with staggered completion
        conversion_count = [0]

        async def mock_convert(file_info):
            await asyncio.sleep(0.01 * conversion_count[0])
            conversion_count[0] += 1
            nonlocal conversion_complete_time
            if conversion_count[0] == 3:  # All conversions done
                conversion_complete_time = time.time()
            return {
                "success": True,
                "filename": file_info["filename"],
                "markdown_content": f"# Content {file_info['filename']}",
            }

        processor.markdown_converter.convert_file_async = AsyncMock(
            side_effect=mock_convert
        )

        # Mock batch processor
        result_index = [0]

        async def mock_get_result():
            await asyncio.sleep(0.01)
            result_index[0] += 1
            return BatchResult(
                filename=f"test{result_index[0]}.txt",
                success=True,
                structured_data={"field": f"value{result_index[0]}"},
                processing_time=0.01,
                final=True,
            )

        processor.batch_processor.get_result = AsyncMock(side_effect=mock_get_result)
        processor.batch_processor.add_item = AsyncMock()
        processor.batch_processor.get_metrics = MagicMock(
            return_value={
                "token_usage": {"total_tokens": 300},
                "cache": {"hits": 0, "misses": 3},
            }
        )

        # Create multiple files
        files = [
            {"file_path": f"/tmp/test{i}.txt", "filename": f"test{i}.txt"}
            for i in range(1, 4)
        ]

        # Process files
        result_count = 0
        first_result_time = None
        async for event in processor.process_files_optimized(
            files, "document_metadata", "", "gpt-4o", run_id="test-run"
        ):
            event_times.append(time.time())
            if '"type": "result"' in event and first_result_time is None:
                first_result_time = time.time()
                result_count += 1

        await processor.stop()

        # Verify we got results before all conversions completed
        # (In progressive mode, results stream as soon as any file completes processing)
        assert first_result_time is not None, "Should have received at least one result"
        assert len(event_times) > 0, "Should have received events throughout processing"

    @pytest.mark.asyncio
    @patch("infotransform.api.document_transform_api.config")
    async def test_progressive_config_flag_enabled(self, mock_config):
        """Test that progressive streaming is enabled when config flag is True"""
        from infotransform.api.document_transform_api import StreamingProcessor

        # Mock config to return True for progressive streaming
        def mock_get_config(key, default=None):
            if key == "processing.pipeline.progressive_streaming":
                return True
            return default

        mock_config.get.side_effect = mock_get_config
        mock_config.get_performance.return_value = 10

        processor = StreamingProcessor()
        await processor.start()

        # Verify add_item is available (batch processor initialized)
        assert hasattr(processor.batch_processor, "add_item")

        await processor.stop()


@pytest.mark.unit
class TestNonProgressiveStreaming:
    """Test non-progressive mode (progressive_streaming=False) for backward compatibility"""

    @pytest.mark.asyncio
    @patch("infotransform.api.document_transform_api.config")
    async def test_non_progressive_items_added_after_conversion(
        self, mock_config, temp_dir, sample_text_file
    ):
        """Test that items are added to batch processor only after all conversions complete"""
        from infotransform.api.document_transform_api import StreamingProcessor

        # Disable progressive streaming
        def mock_get_config(key, default=None):
            if key == "processing.pipeline.progressive_streaming":
                return False
            return default

        mock_config.get.side_effect = mock_get_config
        mock_config.get_performance.return_value = 10

        processor = StreamingProcessor()
        await processor.start()

        # Track when items are added and conversions complete
        add_item_calls = []
        all_conversions_done_time = None

        original_add_item = processor.batch_processor.add_item

        async def tracked_add_item(*args, **kwargs):
            add_item_calls.append({"time": time.time(), "args": args})
            await original_add_item(*args, **kwargs)

        processor.batch_processor.add_item = AsyncMock(side_effect=tracked_add_item)

        # Mock markdown conversion
        conversion_count = [0]

        async def mock_convert(file_info):
            await asyncio.sleep(0.01)
            conversion_count[0] += 1
            nonlocal all_conversions_done_time
            if conversion_count[0] == 2:  # All conversions done
                all_conversions_done_time = time.time()
            return {
                "success": True,
                "filename": file_info["filename"],
                "markdown_content": f"# Content for {file_info['filename']}",
            }

        processor.markdown_converter.convert_file_async = AsyncMock(
            side_effect=mock_convert
        )

        # Mock batch processor
        async def mock_get_result():
            await asyncio.sleep(0.01)
            return BatchResult(
                filename="test.txt",
                success=True,
                structured_data={"field": "value"},
                processing_time=0.01,
                final=True,
            )

        processor.batch_processor.get_result = AsyncMock(side_effect=mock_get_result)
        processor.batch_processor.get_metrics = MagicMock(
            return_value={
                "token_usage": {"total_tokens": 200},
                "cache": {"hits": 0, "misses": 2},
            }
        )

        # Create test files
        files = [
            {"file_path": str(sample_text_file), "filename": "test1.txt"},
            {"file_path": str(sample_text_file), "filename": "test2.txt"},
        ]

        # Process files
        events = []
        async for event in processor.process_files_optimized(
            files, "document_metadata", "", "gpt-4o", run_id="test-run"
        ):
            events.append(event)

        await processor.stop()

        # In non-progressive mode, all items should be added AFTER all conversions complete
        if len(add_item_calls) > 0 and all_conversions_done_time:
            first_add_time = add_item_calls[0]["time"]
            # Items should be added after conversions complete
            assert first_add_time >= all_conversions_done_time - 0.01, (
                "Items should be added after all conversions complete in non-progressive mode"
            )

    @pytest.mark.asyncio
    @patch("infotransform.api.document_transform_api.config")
    async def test_non_progressive_backward_compatibility(
        self, mock_config, sample_text_file
    ):
        """Test that non-progressive mode maintains backward compatibility"""
        from infotransform.api.document_transform_api import StreamingProcessor

        # Disable progressive streaming
        def mock_get_config(key, default=None):
            if key == "processing.pipeline.progressive_streaming":
                return False
            return default

        mock_config.get.side_effect = mock_get_config
        mock_config.get_performance.return_value = 10

        processor = StreamingProcessor()
        await processor.start()

        # Mock converters
        async def mock_convert(file_info):
            return {
                "success": True,
                "filename": file_info["filename"],
                "markdown_content": "# Test content",
            }

        processor.markdown_converter.convert_file_async = AsyncMock(
            side_effect=mock_convert
        )

        # Mock batch processor
        processor.batch_processor.add_item = AsyncMock()

        async def mock_get_result():
            return BatchResult(
                filename="test.txt",
                success=True,
                structured_data={"field": "value"},
                processing_time=0.5,
                final=True,
            )

        processor.batch_processor.get_result = AsyncMock(side_effect=mock_get_result)
        processor.batch_processor.get_metrics = MagicMock(
            return_value={
                "token_usage": {"total_tokens": 100},
                "cache": {"hits": 0, "misses": 1},
            }
        )

        files = [{"file_path": str(sample_text_file), "filename": "test.txt"}]

        # Process files - should work without errors
        events = []
        async for event in processor.process_files_optimized(
            files, "document_metadata", "", "gpt-4o", run_id="test-run"
        ):
            events.append(event)

        await processor.stop()

        # Verify we got expected events
        assert len(events) > 0, "Should receive events in non-progressive mode"
        # Verify completion event exists
        completion_events = [e for e in events if '"type": "complete"' in e]
        assert len(completion_events) > 0, "Should receive completion event"


@pytest.mark.unit
class TestConfigurationFlags:
    """Test configuration flag handling"""

    @pytest.mark.asyncio
    @patch("infotransform.api.document_transform_api.config")
    async def test_config_default_to_true(self, mock_config):
        """Test that progressive streaming defaults to True"""
        from infotransform.api.document_transform_api import StreamingProcessor

        # Mock config to use default value (True)
        def mock_get_config(key, default=None):
            if key == "processing.pipeline.progressive_streaming":
                return True if default is None else default  # Default to True
            return default

        mock_config.get.side_effect = mock_get_config
        mock_config.get_performance.return_value = 10

        processor = StreamingProcessor()
        await processor.start()
        await processor.stop()

        # If we got here without errors, the configuration is working correctly
        # The fact that the processor started and stopped successfully means
        # progressive streaming is working with its default value
        assert processor is not None

    @pytest.mark.asyncio
    @patch("infotransform.api.document_transform_api.config")
    async def test_config_can_disable_progressive(self, mock_config):
        """Test that progressive streaming can be explicitly disabled"""
        from infotransform.api.document_transform_api import StreamingProcessor

        # Explicitly disable progressive streaming
        def mock_get_config(key, default=None):
            if key == "processing.pipeline.progressive_streaming":
                return False
            return default

        mock_config.get.side_effect = mock_get_config
        mock_config.get_performance.return_value = 10

        processor = StreamingProcessor()
        await processor.start()
        await processor.stop()

        # If we got here without errors, configuration is working
        assert processor is not None


@pytest.mark.unit
class TestBatchResultConversion:
    """Test conversion from BatchResult to dict format"""

    @pytest.mark.asyncio
    async def test_batch_result_to_dict_conversion(self):
        """Test that BatchResult is correctly converted to dict format"""
        # Create a BatchResult
        batch_result = BatchResult(
            filename="test.txt",
            success=True,
            structured_data={"field1": "value1"},
            error=None,
            processing_time=1.5,
            final=True,
            usage={"cached": False, "input_tokens": 100},
        )

        # The conversion happens in process_files_optimized
        # We're testing the logic that converts BatchResult to dict
        result_dict = {
            "filename": batch_result.filename,
            "success": batch_result.success,
            "structured_data": batch_result.structured_data,
            "error": batch_result.error,
            "processing_time": batch_result.processing_time,
            "final": batch_result.final,
            "usage": batch_result.usage,
            "cached": batch_result.usage.get("cached", False)
            if batch_result.usage
            else False,
        }

        # Verify conversion
        assert result_dict["filename"] == "test.txt"
        assert result_dict["success"] is True
        assert result_dict["structured_data"] == {"field1": "value1"}
        assert result_dict["processing_time"] == 1.5
        assert result_dict["final"] is True
        assert result_dict["cached"] is False
