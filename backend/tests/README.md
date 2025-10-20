# InfoTransform Backend Tests

Comprehensive test suite for the InfoTransform backend using pytest.

## Overview

This test suite provides comprehensive unit and integration testing for the InfoTransform backend application. It includes tests for:

- **API Endpoints** - FastAPI routes and request handling
- **Processors** - AI agents, batch processing, and document conversion
- **Utilities** - Token counting, file lifecycle management
- **Database** - Processing logs and data persistence
- **Configuration** - Application settings and environment handling

## Test Statistics

- **Total Tests**: 111
- **Test Categories**: 6 (API, Processors, Utils, DB, Config, Integration)
- **Current Coverage**: ~17% (baseline)

## Quick Start

### Prerequisites

Ensure you have the following installed:
- Python 3.11+
- UV package manager
- All dependencies from `pyproject.toml`

### Installation

Install test dependencies:

```bash
# From project root
cd /Users/owen/Desktop/dev_projects/InfoTransform
uv sync
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_config.py

# Run specific test class
uv run pytest tests/test_main.py::TestMainEndpoints

# Run specific test
uv run pytest tests/test_config.py::TestConfig::test_config_initialization

# Run with verbose output
uv run pytest -v

# Run with coverage report
uv run pytest --cov=infotransform --cov-report=html

# Run tests by marker
uv run pytest -m unit          # Unit tests only
uv run pytest -m integration   # Integration tests only
uv run pytest -m api           # API tests only
uv run pytest -m processor     # Processor tests only
```

## Test Structure

```
backend/tests/
├── __init__.py
├── conftest.py                           # Shared fixtures and configuration
├── README.md                             # This file
├── test_main.py                          # FastAPI app tests
├── test_config.py                        # Configuration tests
├── api/
│   ├── __init__.py
│   ├── test_document_transform_api.py    # Transform API tests
│   └── test_review_api.py                # Review API tests (to be added)
├── processors/
│   ├── __init__.py
│   ├── test_structured_analyzer_agent.py # AI analyzer tests
│   ├── test_ai_batch_processor.py        # Batch processor tests
│   ├── test_async_converter.py           # Converter tests (to be added)
│   ├── test_vision.py                    # Vision processor tests (to be added)
│   └── test_audio.py                     # Audio processor tests (to be added)
├── utils/
│   ├── __init__.py
│   ├── test_token_counter.py             # Token counting tests
│   └── test_file_lifecycle.py            # File management tests
└── db/
    ├── __init__.py
    └── test_processing_logs_db.py        # Database tests
```

## Test Categories

### Unit Tests (`@pytest.mark.unit`)

Test individual components in isolation with mocked dependencies.

**Examples:**
- Configuration parsing
- Token counting
- Data class functionality

### Integration Tests (`@pytest.mark.integration`)

Test multiple components working together.

**Examples:**
- Full file processing pipeline
- End-to-end API workflows
- Database operations with real connections

### API Tests (`@pytest.mark.api`)

Test FastAPI endpoints and request/response handling.

**Examples:**
- `/api/transform` - File transformation
- `/api/models` - Model listing
- `/api/download-results` - Result export
- `/health` - Health check

### Processor Tests (`@pytest.mark.processor`)

Test document processing and AI analysis components.

**Examples:**
- Structured data extraction
- Batch processing
- Markdown conversion
- Vision and audio processing

### Database Tests (`@pytest.mark.db`)

Test database operations and persistence.

**Examples:**
- Run logging
- Query operations
- Error handling

### Slow Tests (`@pytest.mark.slow`)

Tests that take longer to execute (>5 seconds).

## Key Fixtures

### Configuration Fixtures

- `mock_env_vars` - Mock environment variables
- `test_config` - Test configuration instance
- `temp_dir` - Temporary directory for test files

### FastAPI Fixtures

- `test_client` - Synchronous test client
- `async_test_client` - Asynchronous test client

### Mock Fixtures

- `mock_openai_client` - Mocked OpenAI API
- `mock_structured_analyzer` - Mocked AI analyzer
- `mock_vision_processor` - Mocked vision processor
- `mock_audio_processor` - Mocked audio processor
- `mock_batch_processor` - Mocked batch processor
- `mock_db` - Mocked database connection

### File Fixtures

- `sample_pdf_file` - Sample PDF for testing
- `sample_text_file` - Sample text file
- `sample_image_file` - Sample PNG image
- `sample_zip_file` - Sample ZIP archive
- `sample_markdown_content` - Sample markdown text

## Configuration

Test configuration is defined in `pytest.ini`:

```ini
[pytest]
# Test discovery
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Asyncio support
asyncio_mode = auto

# Python path
pythonpath = . ..

# Coverage options
addopts = --verbose --cov=infotransform --cov-report=html

# Test markers
markers =
    unit: Unit tests
    integration: Integration tests
    api: API tests
    processor: Processor tests
    slow: Slow tests
    db: Database tests
```

## Writing New Tests

### Test Naming Convention

- Test files: `test_<module_name>.py`
- Test classes: `Test<Feature>`
- Test functions: `test_<behavior>`

### Example Test Structure

```python
"""
Unit tests for <module_name>
"""

import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.unit
class TestFeature:
    """Test <feature> functionality"""

    def test_basic_functionality(self):
        """Test basic functionality"""
        # Arrange
        input_data = "test"

        # Act
        result = some_function(input_data)

        # Assert
        assert result == expected_output

    @pytest.mark.asyncio
    async def test_async_functionality(self):
        """Test asynchronous functionality"""
        result = await async_function()
        assert result is not None
```

### Using Fixtures

```python
def test_with_fixtures(test_config, temp_dir, sample_text_file):
    """Test using multiple fixtures"""
    config = test_config
    test_file = sample_text_file

    # Use fixtures in your test
    assert config is not None
    assert test_file.exists()
```

### Mocking External Dependencies

```python
@patch('module.external_api_call')
def test_with_mocked_api(mock_api_call):
    """Test with mocked external API"""
    mock_api_call.return_value = {"status": "success"}

    result = function_that_calls_api()

    assert result["status"] == "success"
    mock_api_call.assert_called_once()
```

## Common Testing Patterns

### Testing FastAPI Endpoints

```python
def test_endpoint(test_client):
    """Test FastAPI endpoint"""
    response = test_client.get("/api/endpoint")

    assert response.status_code == 200
    assert "expected_field" in response.json()
```

### Testing Async Functions

```python
@pytest.mark.asyncio
async def test_async_function(async_test_client):
    """Test async functionality"""
    result = await async_function()
    assert result is not None
```

### Testing Exception Handling

```python
def test_exception_handling():
    """Test that exceptions are handled correctly"""
    with pytest.raises(ValueError, match="error message"):
        function_that_raises_error()
```

### Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("input1", "output1"),
    ("input2", "output2"),
    ("input3", "output3"),
])
def test_multiple_cases(input, expected):
    """Test multiple cases with parametrize"""
    result = function(input)
    assert result == expected
```

## Coverage Reports

### Generating Coverage Reports

```bash
# HTML report (opens in browser)
uv run pytest --cov=infotransform --cov-report=html
open htmlcov/index.html

# Terminal report
uv run pytest --cov=infotransform --cov-report=term-missing

# XML report (for CI/CD)
uv run pytest --cov=infotransform --cov-report=xml
```

### Coverage Goals

- **Current**: ~17%
- **Target**: 70%+
- **Critical modules**: 80%+

### Improving Coverage

Priority areas for additional tests:
1. ✅ Config module (high coverage)
2. ❌ Vision processor
3. ❌ Audio processor
4. ❌ Async converter
5. ❌ File lifecycle manager
6. ❌ API endpoints

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Install UV
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Install dependencies
        run: uv sync

      - name: Run tests
        run: uv run pytest --cov=infotransform --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Troubleshooting

### Common Issues

**Import Errors:**
```bash
# Ensure Python path is set correctly
export PYTHONPATH=/path/to/backend:$PYTHONPATH
```

**Async Test Warnings:**
```bash
# Install pytest-asyncio
uv add pytest-asyncio
```

**Missing Dependencies:**
```bash
# Reinstall all dependencies
uv sync
```

**Test Discovery Issues:**
```bash
# Verify test file naming
# Must be test_*.py or *_test.py
```

## Best Practices

1. **Keep tests isolated** - Each test should be independent
2. **Use descriptive names** - Test names should describe what they test
3. **One assertion per test** - Focus on testing one thing at a time
4. **Mock external dependencies** - Don't rely on external services
5. **Use fixtures for setup** - Avoid repetitive setup code
6. **Test edge cases** - Include boundary conditions and error cases
7. **Keep tests fast** - Mark slow tests with `@pytest.mark.slow`
8. **Document complex tests** - Add docstrings explaining non-obvious tests

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain or improve coverage
4. Add appropriate markers
5. Update this README if needed

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

## Contact

For questions or issues with tests, please contact the development team or open an issue in the repository.
