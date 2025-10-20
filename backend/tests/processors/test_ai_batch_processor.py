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
    BatchResult
)


@pytest.mark.processor
class TestBatchProcessor:
    """Test BatchProcessor functionality"""

    @pytest.fixture
    def mock_structured_analyzer(self):
        """Create mock structured analyzer"""
        mock_analyzer = MagicMock()

        async def mock_analyze(content, model_key, custom_instructions=None, ai_model=None):
            return {
                'success': True,
                'result': {'field1': 'value1', 'field2': 'value2'},
                'usage': {
                    'input_tokens': 100,
                    'output_tokens': 50,
                    'total_tokens': 150,
                    'cache_read_tokens': 0,
                    'cache_write_tokens': 0,
                    'requests': 1
                }
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
            model_key='invoice',
            custom_instructions='',
            ai_model='gpt-4o'
        )

        await batch_processor.add_item('test.txt', 'content', context)

        # Queue should have one item
        assert batch_processor.batch_queue.qsize() == 1

        await batch_processor.stop()

    @pytest.mark.asyncio
    async def test_process_items_stream(self, batch_processor, sample_markdown_content):
        """Test streaming processing of items"""
        await batch_processor.start()

        items = [
            {'filename': 'file1.txt', 'markdown_content': sample_markdown_content},
            {'filename': 'file2.txt', 'markdown_content': sample_markdown_content}
        ]

        results = []
        async for result in batch_processor.process_items_stream(
            items,
            'invoice',
            '',
            'gpt-4o'
        ):
            results.append(result)

        # Should have 2 results
        assert len(results) == 2
        assert all(r['success'] for r in results)
        assert all(r['final'] for r in results)

        await batch_processor.stop()

    @pytest.mark.asyncio
    async def test_batch_metrics(self, batch_processor, sample_markdown_content):
        """Test batch processing metrics"""
        await batch_processor.start()

        items = [
            {'filename': 'file1.txt', 'markdown_content': sample_markdown_content}
        ]

        results = []
        async for result in batch_processor.process_items_stream(
            items,
            'invoice',
            '',
            'gpt-4o'
        ):
            results.append(result)

        # Get metrics
        metrics = batch_processor.get_metrics()

        assert 'total_batches' in metrics
        assert 'total_items' in metrics
        assert 'token_usage' in metrics
        assert metrics['token_usage']['total_tokens'] > 0

        await batch_processor.stop()

    @pytest.mark.asyncio
    async def test_batch_timeout_handling(self, batch_processor):
        """Test batch processing timeout"""
        await batch_processor.start()

        # Create mock analyzer that times out
        async def slow_analyze(*args, **kwargs):
            await asyncio.sleep(10)  # Longer than timeout
            return {'success': True, 'result': {}}

        batch_processor.analyzer.analyze_content = AsyncMock(side_effect=slow_analyze)

        # Set very short timeout for testing
        batch_processor.timeout_per_batch = 0.1

        items = [
            {'filename': 'file1.txt', 'markdown_content': 'content'}
        ]

        results = []
        async for result in batch_processor.process_items_stream(
            items,
            'invoice',
            '',
            'gpt-4o'
        ):
            results.append(result)

        # Should have error result
        assert len(results) == 1
        assert results[0]['success'] is False or 'timeout' in results[0].get('error', '').lower()

        await batch_processor.stop()

    def test_get_adaptive_batch_size(self, batch_processor):
        """Test adaptive batch size calculation"""
        # With no metrics, should return configured size
        batch_size = batch_processor._get_adaptive_batch_size()
        assert batch_size == batch_processor.batch_size

        # Add some metrics
        batch_processor.metrics['recent_response_times'] = [1.0, 1.5, 2.0]
        batch_processor.metrics['current_batch_size'] = 10

        # Should calculate adaptive size
        batch_size = batch_processor._get_adaptive_batch_size()
        assert isinstance(batch_size, int)
        assert batch_size >= batch_processor.min_batch_size
        assert batch_size <= batch_processor.max_batch_size

    def test_update_metrics(self, batch_processor):
        """Test metrics updating"""
        initial_batches = batch_processor.metrics['total_batches']
        initial_items = batch_processor.metrics['total_items']

        batch_processor._update_metrics(5, 2.5)

        assert batch_processor.metrics['total_batches'] == initial_batches + 1
        assert batch_processor.metrics['total_items'] == initial_items + 5
        assert len(batch_processor.metrics['recent_response_times']) > 0

    def test_update_usage_metrics(self, batch_processor):
        """Test usage metrics updating"""
        usage = {
            'input_tokens': 100,
            'output_tokens': 50,
            'cache_read_tokens': 10,
            'cache_write_tokens': 5,
            'total_tokens': 150,
            'requests': 1
        }

        initial_tokens = batch_processor.metrics['total_usage']['total_tokens']
        batch_processor._update_usage_metrics(usage)

        assert batch_processor.metrics['total_usage']['total_tokens'] == initial_tokens + 150
        assert batch_processor.metrics['total_usage']['input_tokens'] == 100
        assert batch_processor.metrics['total_usage']['output_tokens'] == 50


@pytest.mark.unit
class TestBatchDataClasses:
    """Test batch processing data classes"""

    def test_processing_context(self):
        """Test ProcessingContext dataclass"""
        context = ProcessingContext(
            model_key='invoice',
            custom_instructions='test',
            ai_model='gpt-4o'
        )

        assert context.model_key == 'invoice'
        assert context.custom_instructions == 'test'
        assert context.ai_model == 'gpt-4o'

    def test_batch_item(self):
        """Test BatchItem dataclass"""
        context = ProcessingContext(
            model_key='invoice',
            custom_instructions='',
            ai_model='gpt-4o'
        )

        item = BatchItem(
            filename='test.txt',
            markdown_content='content',
            context=context
        )

        assert item.filename == 'test.txt'
        assert item.markdown_content == 'content'
        assert item.timestamp is not None

    def test_batch(self):
        """Test Batch dataclass"""
        context = ProcessingContext(
            model_key='invoice',
            custom_instructions='',
            ai_model='gpt-4o'
        )

        item = BatchItem(
            filename='test.txt',
            markdown_content='content',
            context=context
        )

        batch = Batch(
            items=[item],
            context=context
        )

        assert len(batch.items) == 1
        assert batch.created_at is not None

    def test_batch_result(self):
        """Test BatchResult dataclass"""
        result = BatchResult(
            filename='test.txt',
            success=True,
            structured_data={'field': 'value'},
            processing_time=1.0
        )

        assert result.filename == 'test.txt'
        assert result.success is True
        assert result.structured_data == {'field': 'value'}
        assert result.processing_time == 1.0
        assert result.final is True


@pytest.mark.integration
class TestBatchProcessorIntegration:
    """Integration tests for batch processor"""

    @pytest.mark.asyncio
    async def test_full_batch_processing_flow(self, mock_structured_analyzer, sample_markdown_content):
        """Test complete batch processing flow"""
        processor = BatchProcessor(mock_structured_analyzer)

        await processor.start()

        # Process multiple items
        items = [
            {'filename': f'file{i}.txt', 'markdown_content': sample_markdown_content}
            for i in range(5)
        ]

        results = []
        async for result in processor.process_items_stream(
            items,
            'invoice',
            'Extract invoice data',
            'gpt-4o'
        ):
            results.append(result)

        # Should have 5 results
        assert len(results) == 5
        assert all(r['success'] for r in results)

        # Check metrics
        metrics = processor.get_metrics()
        assert metrics['total_items'] == 5

        await processor.stop()

    @pytest.mark.asyncio
    async def test_concurrent_batch_processing(self, mock_structured_analyzer, sample_markdown_content):
        """Test processing multiple batches concurrently"""
        processor = BatchProcessor(mock_structured_analyzer)
        processor.max_concurrent_batches = 2

        await processor.start()

        # Process many items to trigger multiple batches
        items = [
            {'filename': f'file{i}.txt', 'markdown_content': sample_markdown_content}
            for i in range(20)
        ]

        results = []
        async for result in processor.process_items_stream(
            items,
            'invoice',
            '',
            'gpt-4o'
        ):
            results.append(result)

        # Should have 20 results
        assert len(results) == 20

        await processor.stop()

    @pytest.mark.asyncio
    @patch('infotransform.config.config.get')
    async def test_partial_streaming_enabled(self, mock_config_get, mock_structured_analyzer, sample_markdown_content):
        """Test partial streaming when enabled"""
        # Configure partial streaming
        def config_side_effect(key, default=None):
            if key == 'ai_pipeline.structured_analysis.streaming.enable_partial':
                return True
            return default

        mock_config_get.side_effect = config_side_effect

        # Mock analyzer with streaming support
        async def mock_analyze_stream(content, model_key, custom_instructions, ai_model):
            # Yield partial result
            yield {
                'success': True,
                'result': {'field1': 'value1'},
                'final': False,
                'usage': None
            }
            # Yield final result
            yield {
                'success': True,
                'result': {'field1': 'value1', 'field2': 'value2'},
                'final': True,
                'usage': {'input_tokens': 100, 'output_tokens': 50, 'total_tokens': 150}
            }

        mock_structured_analyzer.analyze_content_stream = mock_analyze_stream

        processor = BatchProcessor(mock_structured_analyzer)
        await processor.start()

        items = [{'filename': 'file1.txt', 'markdown_content': sample_markdown_content}]

        results = []
        async for result in processor.process_items_stream(items, 'invoice', '', 'gpt-4o'):
            results.append(result)

        # Should have partial and final results
        assert len(results) >= 1
        # Final result should exist
        assert any(r['final'] for r in results)

        await processor.stop()
