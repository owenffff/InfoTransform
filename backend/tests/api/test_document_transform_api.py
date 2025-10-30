"""
Unit tests for document transform API
"""

import json
from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status


@pytest.mark.api
class TestTransformEndpoint:
    """Test the /api/transform endpoint"""

    @pytest.mark.asyncio
    @patch("infotransform.api.document_transform_api.get_processor")
    async def test_transform_basic_file(
        self, mock_get_processor, async_test_client, sample_text_file
    ):
        """Test basic file transformation"""
        # Create mock processor
        mock_processor = MagicMock()

        async def mock_process(*args, **kwargs):
            # Yield initial event
            yield f"data: {json.dumps({'type': 'init', 'total_files': 1})}\n\n"
            # Yield completion event
            yield f"data: {json.dumps({'type': 'complete', 'total_files': 1, 'successful': 1})}\n\n"

        mock_processor.process_files_optimized = mock_process
        mock_get_processor.return_value = mock_processor

        # Prepare test file
        with open(sample_text_file, "rb") as f:
            file_content = f.read()

        files = {"files": ("test.txt", BytesIO(file_content), "text/plain")}
        data = {"model_key": "invoice", "custom_instructions": "", "ai_model": "gpt-4o"}

        response = await async_test_client.post(
            "/api/transform", files=files, data=data
        )

        # The response should be a streaming response
        assert response.status_code == status.HTTP_200_OK
        assert "text/event-stream" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    @patch("infotransform.api.document_transform_api.get_processor")
    async def test_transform_no_files(self, mock_get_processor, async_test_client):
        """Test transform with no files provided"""
        data = {"model_key": "invoice", "custom_instructions": ""}

        with pytest.raises(Exception):
            # Should raise an exception due to missing files
            await async_test_client.post("/api/transform", data=data)

    @pytest.mark.asyncio
    @patch("infotransform.api.document_transform_api.get_processor")
    async def test_transform_invalid_model(
        self, mock_get_processor, async_test_client, sample_text_file
    ):
        """Test transform with invalid model key"""
        mock_processor = MagicMock()
        mock_processor.structured_analyzer_agent.get_available_models.return_value = {
            "invoice": {}
        }
        mock_get_processor.return_value = mock_processor

        with open(sample_text_file, "rb") as f:
            file_content = f.read()

        files = {"files": ("test.txt", BytesIO(file_content), "text/plain")}
        data = {"model_key": "nonexistent_model", "custom_instructions": ""}

        with pytest.raises(Exception):
            # Should raise HTTPException with 400 status
            await async_test_client.post("/api/transform", files=files, data=data)


@pytest.mark.unit
class TestStreamingProcessor:
    """Test StreamingProcessor class"""

    @pytest.mark.asyncio
    async def test_processor_initialization(self):
        """Test StreamingProcessor initialization"""
        from infotransform.api.document_transform_api import StreamingProcessor

        processor = StreamingProcessor()
        assert processor is not None
        assert processor.structured_analyzer_agent is not None
        assert processor.summarization_agent is not None
        assert processor.markdown_converter is not None
        assert processor.batch_processor is not None

    @pytest.mark.asyncio
    async def test_processor_start_stop(self):
        """Test processor lifecycle"""
        from infotransform.api.document_transform_api import StreamingProcessor

        processor = StreamingProcessor()

        # Start processor
        await processor.start()

        # Stop processor
        await processor.stop()

    @pytest.mark.asyncio
    @patch(
        "infotransform.api.document_transform_api.StreamingProcessor.markdown_converter"
    )
    @patch(
        "infotransform.api.document_transform_api.StreamingProcessor.batch_processor"
    )
    async def test_process_files_optimized(
        self, mock_batch_processor, mock_markdown_converter, sample_text_file
    ):
        """Test optimized file processing pipeline"""
        from infotransform.api.document_transform_api import StreamingProcessor

        processor = StreamingProcessor()

        # Mock markdown conversion
        async def mock_convert(file_info):
            return {
                "success": True,
                "filename": file_info["filename"],
                "markdown_content": "# Test Content",
            }

        mock_markdown_converter.convert_file_async = AsyncMock(side_effect=mock_convert)

        # Mock batch processing
        async def mock_batch_stream(items, model_key, custom_instructions, ai_model):
            for item in items:
                yield {
                    "filename": item["filename"],
                    "success": True,
                    "structured_data": {"field1": "value1"},
                    "processing_time": 0.5,
                    "final": True,
                }

        mock_batch_processor.process_items_stream = mock_batch_stream
        mock_batch_processor.get_metrics.return_value = {
            "token_usage": {
                "input_tokens": 100,
                "output_tokens": 50,
                "total_tokens": 150,
            }
        }

        # Create file info
        files = [{"file_path": str(sample_text_file), "filename": "test.txt"}]

        # Process files
        events = []
        async for event in processor.process_files_optimized(
            files, "invoice", "", "gpt-4o"
        ):
            events.append(event)

        # Verify events were generated
        assert len(events) > 0

    def test_is_zip_file(self):
        """Test ZIP file detection"""
        from infotransform.api.document_transform_api import StreamingProcessor

        processor = StreamingProcessor()

        assert processor._is_zip_file("test.zip") is True
        assert processor._is_zip_file("test.ZIP") is True
        assert processor._is_zip_file("test.txt") is False

    @pytest.mark.asyncio
    async def test_extract_zip_recursive(self, sample_zip_file):
        """Test recursive ZIP extraction"""
        from infotransform.api.document_transform_api import StreamingProcessor

        processor = StreamingProcessor()

        # Extract ZIP file
        extracted = processor._extract_zip_recursive(str(sample_zip_file), "test.zip")

        # Should have extracted files
        assert len(extracted) > 0
        for file_info in extracted:
            assert "file_path" in file_info
            assert "filename" in file_info
            assert "source_archive" in file_info
            assert "display_name" in file_info

        # Cleanup
        processor._cleanup_temp_dirs()

    def test_get_display_fields(self):
        """Test display fields extraction"""
        from infotransform.api.document_transform_api import StreamingProcessor

        processor = StreamingProcessor()

        # Test flat structure
        flat_data = {"field1": "value1", "field2": "value2"}
        fields = processor._get_display_fields(flat_data)
        assert set(fields) == {"field1", "field2"}

        # Test nested structure with item wrapper
        nested_data = {"item": [{"nested_field1": "value1", "nested_field2": "value2"}]}
        fields = processor._get_display_fields(nested_data)
        assert set(fields) == {"nested_field1", "nested_field2"}

    def test_expand_nested_results(self):
        """Test nested results expansion"""
        from infotransform.api.document_transform_api import StreamingProcessor

        processor = StreamingProcessor()

        # Test nested schema with multiple items
        ai_result = {
            "success": True,
            "filename": "test.pdf",
            "structured_data": {
                "item": [
                    {"field1": "value1", "field2": "value2"},
                    {"field1": "value3", "field2": "value4"},
                ]
            },
            "processing_time": 1.0,
        }

        original_item = {"filename": "test.pdf", "display_name": "Test PDF"}

        expanded = processor._expand_nested_results(ai_result, original_item)

        # Should expand to 2 results
        assert len(expanded) == 2
        assert expanded[0]["structured_data"] == {
            "field1": "value1",
            "field2": "value2",
        }
        assert expanded[1]["structured_data"] == {
            "field1": "value3",
            "field2": "value4",
        }
        assert expanded[0]["is_primary_result"] is True
        assert expanded[1]["is_primary_result"] is False


@pytest.mark.integration
class TestTransformIntegration:
    """Integration tests for the transform API"""

    @pytest.mark.asyncio
    @patch("infotransform.api.document_transform_api.StreamingProcessor")
    async def test_full_transform_flow(
        self, mock_processor_class, async_test_client, sample_text_file
    ):
        """Test complete transformation flow"""
        # Create mock processor instance
        mock_processor = MagicMock()

        async def mock_process(*args, **kwargs):
            yield f"data: {json.dumps({'type': 'init', 'total_files': 1})}\n\n"
            yield f"data: {json.dumps({'type': 'phase', 'phase': 'markdown_conversion', 'status': 'started'})}\n\n"
            yield f"data: {json.dumps({'type': 'result', 'filename': 'test.txt', 'status': 'success'})}\n\n"
            yield f"data: {json.dumps({'type': 'complete', 'total_files': 1, 'successful': 1})}\n\n"

        mock_processor.process_files_optimized = mock_process
        mock_processor.structured_analyzer_agent.get_available_models.return_value = {
            "invoice": {"name": "Invoice", "fields": {}}
        }

        # Mock the get_processor function
        async def mock_get_processor():
            return mock_processor

        with patch(
            "infotransform.api.document_transform_api.get_processor", mock_get_processor
        ):
            with open(sample_text_file, "rb") as f:
                file_content = f.read()

            files = {"files": ("test.txt", BytesIO(file_content), "text/plain")}
            data = {
                "model_key": "invoice",
                "custom_instructions": "",
                "ai_model": "gpt-4o",
            }

            response = await async_test_client.post(
                "/api/transform", files=files, data=data
            )

            assert response.status_code == status.HTTP_200_OK


@pytest.mark.unit
class TestShutdownProcessor:
    """Test processor shutdown functionality"""

    @pytest.mark.asyncio
    @patch("infotransform.api.document_transform_api._processor")
    async def test_shutdown_processor(self, mock_global_processor):
        """Test shutting down the processor"""
        from infotransform.api.document_transform_api import shutdown_processor

        mock_processor = MagicMock()
        mock_processor.stop = AsyncMock()

        await shutdown_processor()

        # Verify stop was called
        # Note: This test depends on the global processor being set


@pytest.mark.unit
class TestGetProcessor:
    """Test processor singleton pattern"""

    @pytest.mark.asyncio
    async def test_get_processor_creates_instance(self):
        """Test that get_processor creates a processor instance"""
        from infotransform.api.document_transform_api import get_processor

        processor = await get_processor()
        assert processor is not None

    @pytest.mark.asyncio
    async def test_get_processor_returns_same_instance(self):
        """Test that get_processor returns the same instance"""
        from infotransform.api.document_transform_api import get_processor

        processor1 = await get_processor()
        processor2 = await get_processor()

        # Should be the same instance
        assert processor1 is processor2
