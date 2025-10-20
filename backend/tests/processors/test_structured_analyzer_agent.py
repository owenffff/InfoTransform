"""
Unit tests for StructuredAnalyzerAgent
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pydantic import BaseModel, Field


# Mock document schema for testing
class MockInvoiceModel(BaseModel):
    """Mock invoice model for testing"""
    vendor: str = Field(description="Vendor name")
    amount: float = Field(description="Total amount")
    date: str = Field(description="Invoice date")


@pytest.mark.processor
class TestStructuredAnalyzerAgent:
    """Test StructuredAnalyzerAgent functionality"""

    @pytest.fixture
    def mock_available_models(self):
        """Mock AVAILABLE_MODELS"""
        return {
            'invoice': MockInvoiceModel
        }

    @pytest.fixture
    def analyzer(self, mock_available_models):
        """Create analyzer with mocked models"""
        with patch('infotransform.processors.structured_analyzer_agent.AVAILABLE_MODELS', mock_available_models):
            from infotransform.processors.structured_analyzer_agent import StructuredAnalyzerAgent
            return StructuredAnalyzerAgent()

    def test_analyzer_initialization(self, analyzer):
        """Test analyzer initializes correctly"""
        assert analyzer is not None
        assert analyzer.config is not None
        assert analyzer.agents == {}

    @pytest.mark.asyncio
    @patch('infotransform.processors.structured_analyzer_agent.Agent')
    async def test_analyze_content_success(self, mock_agent_class, analyzer, sample_markdown_content):
        """Test successful content analysis"""
        # Mock the agent
        mock_agent = MagicMock()
        mock_result = MagicMock()
        mock_result.output.model_dump.return_value = {
            'vendor': 'Test Vendor',
            'amount': 100.0,
            'date': '2024-01-01'
        }
        mock_result.usage.return_value = MagicMock(
            input_tokens=100,
            output_tokens=50,
            cache_read_tokens=0,
            cache_write_tokens=0,
            requests=1
        )
        mock_agent.run = AsyncMock(return_value=mock_result)
        mock_agent_class.return_value = mock_agent

        result = await analyzer.analyze_content(
            sample_markdown_content,
            'invoice',
            custom_instructions='Extract invoice data',
            ai_model='gpt-4o'
        )

        assert result['success'] is True
        assert 'result' in result
        assert result['result']['vendor'] == 'Test Vendor'
        assert result['result']['amount'] == 100.0
        assert 'usage' in result

    @pytest.mark.asyncio
    async def test_analyze_content_invalid_model(self, analyzer, sample_markdown_content):
        """Test analysis with invalid model key"""
        result = await analyzer.analyze_content(
            sample_markdown_content,
            'nonexistent_model'
        )

        assert result['success'] is False
        assert 'error' in result
        assert 'Invalid model key' in result['error']

    @pytest.mark.asyncio
    @patch('infotransform.processors.structured_analyzer_agent.Agent')
    async def test_analyze_content_with_exception(self, mock_agent_class, analyzer, sample_markdown_content):
        """Test analysis when exception occurs"""
        mock_agent = MagicMock()
        mock_agent.run = AsyncMock(side_effect=Exception("API Error"))
        mock_agent_class.return_value = mock_agent

        result = await analyzer.analyze_content(
            sample_markdown_content,
            'invoice'
        )

        assert result['success'] is False
        assert 'error' in result
        assert 'API Error' in result['error']

    @pytest.mark.asyncio
    @patch('infotransform.processors.structured_analyzer_agent.Agent')
    async def test_analyze_content_stream(self, mock_agent_class, analyzer, sample_markdown_content):
        """Test streaming content analysis"""
        # Mock the agent
        mock_agent = MagicMock()

        # Create mock streaming context
        class MockStreamContext:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

            async def stream_structured(self, debounce_by=0.01):
                # Yield partial result
                partial_message = MagicMock()
                yield partial_message, False

                # Yield final result
                final_message = MagicMock()
                yield final_message, True

            async def validate_structured_output(self, message):
                result = MagicMock()
                result.model_dump.return_value = {
                    'vendor': 'Test Vendor',
                    'amount': 100.0,
                    'date': '2024-01-01'
                }
                return result

            async def partial_structured_output(self, message):
                result = MagicMock()
                result.model_dump.return_value = {
                    'vendor': 'Test Vendor',
                    'amount': None,
                    'date': None
                }
                return result

            def usage(self):
                return MagicMock(
                    input_tokens=100,
                    output_tokens=50,
                    cache_read_tokens=0,
                    cache_write_tokens=0,
                    requests=1
                )

        mock_agent.run_stream.return_value = MockStreamContext()
        mock_agent_class.return_value = mock_agent

        results = []
        async for result in analyzer.analyze_content_stream(
            sample_markdown_content,
            'invoice'
        ):
            results.append(result)

        # Should have at least one result
        assert len(results) > 0
        # Final result should have success=True
        assert any(r['success'] and r.get('final', True) for r in results)

    def test_get_available_models(self, analyzer):
        """Test getting available models"""
        models = analyzer.get_available_models()

        assert isinstance(models, dict)
        assert 'invoice' in models
        assert 'name' in models['invoice']
        assert 'description' in models['invoice']
        assert 'fields' in models['invoice']

    def test_get_available_ai_models(self, analyzer):
        """Test getting available AI models"""
        ai_models = analyzer.get_available_ai_models()

        assert isinstance(ai_models, dict)
        assert 'default_model' in ai_models
        assert 'models' in ai_models

    def test_convert_enums_to_strings(self, analyzer):
        """Test enum conversion to strings"""
        from enum import Enum

        class TestEnum(Enum):
            VALUE1 = "value1"
            VALUE2 = "value2"

        data = {
            'simple': 'text',
            'enum': TestEnum.VALUE1,
            'nested': {
                'enum': TestEnum.VALUE2
            },
            'list': [TestEnum.VALUE1, TestEnum.VALUE2]
        }

        result = analyzer._convert_enums_to_strings(data)

        assert result['simple'] == 'text'
        assert result['enum'] == 'value1'
        assert result['nested']['enum'] == 'value2'
        assert result['list'] == ['value1', 'value2']

    @pytest.mark.asyncio
    @patch('infotransform.processors.structured_analyzer_agent.Agent')
    async def test_analyze_batch(self, mock_agent_class, analyzer, sample_markdown_content):
        """Test batch content analysis"""
        mock_agent = MagicMock()
        mock_result = MagicMock()
        mock_result.output.model_dump.return_value = {
            'vendor': 'Test Vendor',
            'amount': 100.0,
            'date': '2024-01-01'
        }
        mock_result.usage.return_value = MagicMock(
            input_tokens=100,
            output_tokens=50,
            cache_read_tokens=0,
            cache_write_tokens=0,
            requests=1
        )
        mock_agent.run = AsyncMock(return_value=mock_result)
        mock_agent_class.return_value = mock_agent

        contents = {
            'file1.txt': sample_markdown_content,
            'file2.txt': sample_markdown_content
        }

        results = await analyzer.analyze_batch(contents, 'invoice')

        assert len(results) == 2
        assert all(r['success'] for r in results)
        assert all('filename' in r for r in results)

    def test_get_or_create_agent_caching(self, analyzer):
        """Test that agents are cached"""
        with patch('infotransform.processors.structured_analyzer_agent.Agent') as mock_agent_class:
            mock_agent_class.return_value = MagicMock()

            # Create agent first time
            agent1 = analyzer._get_or_create_agent(MockInvoiceModel, 'invoice', 'gpt-4o')

            # Create agent second time - should use cache
            agent2 = analyzer._get_or_create_agent(MockInvoiceModel, 'invoice', 'gpt-4o')

            # Should be the same instance
            assert agent1 is agent2

            # Agent class should only be called once
            assert mock_agent_class.call_count == 1


@pytest.mark.unit
class TestAnalyzerConfiguration:
    """Test analyzer configuration handling"""

    def test_analyzer_uses_config(self):
        """Test that analyzer uses configuration"""
        from infotransform.processors.structured_analyzer_agent import StructuredAnalyzerAgent

        analyzer = StructuredAnalyzerAgent()

        assert analyzer.config is not None

    @pytest.mark.asyncio
    @patch('infotransform.processors.structured_analyzer_agent.Agent')
    async def test_analyzer_respects_model_settings(self, mock_agent_class, sample_markdown_content):
        """Test that analyzer respects model settings from config"""
        from infotransform.processors.structured_analyzer_agent import StructuredAnalyzerAgent

        analyzer = StructuredAnalyzerAgent()

        mock_agent = MagicMock()
        mock_result = MagicMock()
        mock_result.output.model_dump.return_value = {'field': 'value'}
        mock_result.usage.return_value = MagicMock(
            input_tokens=100,
            output_tokens=50,
            cache_read_tokens=0,
            cache_write_tokens=0,
            requests=1
        )
        mock_agent.run = AsyncMock(return_value=mock_result)
        mock_agent_class.return_value = mock_agent

        with patch('infotransform.processors.structured_analyzer_agent.AVAILABLE_MODELS', {'test': MockInvoiceModel}):
            result = await analyzer.analyze_content(
                sample_markdown_content,
                'test',
                ai_model='gpt-4o'
            )

            # Verify that run was called with model_settings
            mock_agent.run.assert_called_once()
            call_args = mock_agent.run.call_args
            assert 'model_settings' in call_args.kwargs or len(call_args.args) > 1
