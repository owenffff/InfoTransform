"""
Pytest configuration and shared fixtures for InfoTransform backend tests
"""

import asyncio
import os
import tempfile
from pathlib import Path
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Import configuration first (before app to avoid circular deps)
from infotransform.config import Config


# ============================================================================
# Pytest Configuration
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing"""
    env_vars = {
        'OPENAI_API_KEY': 'test-api-key-123',
        'OPENAI_BASE_URL': 'https://api.openai.com/v1',
        'PORT': '8000',
        'ENV': 'development',
    }

    with patch.dict(os.environ, env_vars, clear=False):
        yield env_vars


@pytest.fixture
def test_config(mock_env_vars):
    """Create a test configuration instance"""
    return Config()


# ============================================================================
# FastAPI Client Fixtures
# ============================================================================

@pytest.fixture
def test_client() -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI app"""
    # Import app here to avoid import issues
    from infotransform.main import app
    with TestClient(app) as client:
        yield client


@pytest.fixture
async def async_test_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for the FastAPI app"""
    # Import app here to avoid import issues
    from infotransform.main import app
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# ============================================================================
# Mock OpenAI Client Fixtures
# ============================================================================

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    return {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-4o",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": '{"field1": "value1", "field2": "value2"}'
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150
        }
    }


@pytest.fixture
def mock_openai_client(mock_openai_response):
    """Mock OpenAI client for testing"""
    mock_client = MagicMock()
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock()]
    mock_completion.choices[0].message.content = mock_openai_response["choices"][0]["message"]["content"]
    mock_completion.usage = MagicMock()
    mock_completion.usage.prompt_tokens = mock_openai_response["usage"]["prompt_tokens"]
    mock_completion.usage.completion_tokens = mock_openai_response["usage"]["completion_tokens"]
    mock_completion.usage.total_tokens = mock_openai_response["usage"]["total_tokens"]

    mock_client.chat.completions.create.return_value = mock_completion
    return mock_client


# ============================================================================
# File and Directory Fixtures
# ============================================================================

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_pdf_file(temp_dir) -> Path:
    """Create a sample PDF file for testing"""
    pdf_path = temp_dir / "sample.pdf"
    # Create a minimal PDF file (simplified)
    pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n%%EOF"
    pdf_path.write_bytes(pdf_content)
    return pdf_path


@pytest.fixture
def sample_text_file(temp_dir) -> Path:
    """Create a sample text file for testing"""
    text_path = temp_dir / "sample.txt"
    text_path.write_text("This is a sample text file for testing.")
    return text_path


@pytest.fixture
def sample_markdown_content() -> str:
    """Sample markdown content for testing"""
    return """# Sample Document

This is a test document with some content.

## Section 1
- Item 1
- Item 2
- Item 3

## Section 2
Some more content here.
"""


@pytest.fixture
def sample_image_file(temp_dir) -> Path:
    """Create a sample image file for testing"""
    # Create a minimal PNG file (1x1 pixel)
    image_path = temp_dir / "sample.png"
    png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    image_path.write_bytes(png_data)
    return image_path


@pytest.fixture
def sample_zip_file(temp_dir, sample_text_file) -> Path:
    """Create a sample ZIP file for testing"""
    import zipfile

    zip_path = temp_dir / "sample.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(sample_text_file, "file1.txt")
        zipf.writestr("file2.txt", "Another test file")

    return zip_path


# ============================================================================
# Mock Processor Fixtures
# ============================================================================

@pytest.fixture
def mock_structured_analyzer():
    """Mock StructuredAnalyzerAgent for testing"""
    mock_analyzer = MagicMock()

    # Mock analyze_content method
    async def mock_analyze(content, model_key, custom_instructions=None, ai_model=None):
        return {
            'success': True,
            'result': {
                'field1': 'value1',
                'field2': 'value2'
            },
            'model_used': model_key,
            'ai_model_used': ai_model or 'gpt-4o',
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

    # Mock get_available_models method
    mock_analyzer.get_available_models.return_value = {
        'invoice': {
            'name': 'InvoiceModel',
            'description': 'Extract invoice information',
            'fields': {'vendor': {'type': 'str', 'description': 'Vendor name', 'required': True}}
        }
    }

    # Mock get_available_ai_models method
    mock_analyzer.get_available_ai_models.return_value = {
        'default_model': 'gpt-4o',
        'models': {
            'gpt-4o': {'display_name': 'GPT-4o', 'temperature': 0.7, 'seed': 42}
        }
    }

    return mock_analyzer


@pytest.fixture
def mock_vision_processor():
    """Mock VisionProcessor for testing"""
    mock_processor = MagicMock()

    async def mock_process(file_path):
        return {
            'success': True,
            'markdown_content': '# Image Content\n\nThis is extracted text from the image.',
            'filename': Path(file_path).name
        }

    mock_processor.process_image = AsyncMock(side_effect=mock_process)
    return mock_processor


@pytest.fixture
def mock_audio_processor():
    """Mock AudioProcessor for testing"""
    mock_processor = MagicMock()

    async def mock_process(file_path):
        return {
            'success': True,
            'markdown_content': '# Audio Transcript\n\nThis is the transcribed audio content.',
            'filename': Path(file_path).name
        }

    mock_processor.process_audio = AsyncMock(side_effect=mock_process)
    return mock_processor


@pytest.fixture
def mock_batch_processor():
    """Mock BatchProcessor for testing"""
    mock_processor = MagicMock()

    async def mock_process_stream(items, model_key, custom_instructions, ai_model):
        for item in items:
            yield {
                'filename': item['filename'],
                'success': True,
                'structured_data': {'field1': 'value1', 'field2': 'value2'},
                'processing_time': 0.5,
                'final': True,
                'usage': {
                    'input_tokens': 100,
                    'output_tokens': 50,
                    'total_tokens': 150,
                    'cache_read_tokens': 0,
                    'cache_write_tokens': 0,
                    'requests': 1
                }
            }

    mock_processor.process_items_stream = mock_process_stream
    mock_processor.get_metrics.return_value = {
        'total_batches': 1,
        'total_items': 1,
        'average_batch_size': 1,
        'token_usage': {
            'input_tokens': 100,
            'output_tokens': 50,
            'total_tokens': 150
        }
    }

    return mock_processor


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture
def mock_db():
    """Mock database connection for testing"""
    mock_connection = MagicMock()

    async def mock_insert_run_start(*args, **kwargs):
        return True

    async def mock_update_run_complete(*args, **kwargs):
        return True

    mock_connection.insert_run_start = AsyncMock(side_effect=mock_insert_run_start)
    mock_connection.update_run_complete = AsyncMock(side_effect=mock_update_run_complete)

    return mock_connection


# ============================================================================
# Cleanup Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Automatically cleanup test files after each test"""
    yield
    # Add any cleanup logic here if needed


# ============================================================================
# Mock Pydantic AI Agent Fixtures
# ============================================================================

@pytest.fixture
def mock_pydantic_agent():
    """Mock Pydantic AI Agent for testing"""
    mock_agent = MagicMock()

    # Mock run method
    async def mock_run(prompt, model_settings=None):
        result = MagicMock()
        result.output.model_dump.return_value = {
            'field1': 'value1',
            'field2': 'value2'
        }
        result.usage.return_value = MagicMock(
            input_tokens=100,
            output_tokens=50,
            cache_read_tokens=0,
            cache_write_tokens=0,
            requests=1
        )
        return result

    mock_agent.run = AsyncMock(side_effect=mock_run)

    return mock_agent
