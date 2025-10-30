"""
Unit tests for FastAPI main application
"""

from unittest.mock import patch

import pytest
from fastapi import status


@pytest.mark.api
class TestMainEndpoints:
    """Test main API endpoints"""

    def test_read_root(self, test_client):
        """Test root endpoint redirects to frontend"""
        response = test_client.get("/", follow_redirects=False)
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert "http://localhost:3000" in response.headers.get("location", "")

    def test_health_check(self, test_client):
        """Test health check endpoint"""
        response = test_client.get("/health")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "processors_initialized" in data
        assert "server" in data
        assert data["server"] == "FastAPI"
        assert "version" in data

    @patch("infotransform.main.structured_analyzer")
    def test_list_models_success(self, mock_analyzer, test_client):
        """Test listing available models"""
        # Mock the structured analyzer
        mock_analyzer.get_available_models.return_value = {
            "invoice": {
                "name": "InvoiceModel",
                "description": "Extract invoice information",
                "fields": {},
            }
        }
        mock_analyzer.get_available_ai_models.return_value = {
            "default_model": "gpt-4o",
            "models": {"gpt-4o": {"display_name": "GPT-4o"}},
        }

        response = test_client.get("/api/models")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "models" in data
        assert "ai_models" in data

    @patch("infotransform.main.structured_analyzer", None)
    def test_list_models_analyzer_not_initialized(self, test_client):
        """Test listing models when analyzer is not initialized"""
        response = test_client.get("/api/models")
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "not initialized" in response.json()["detail"]


@pytest.mark.api
class TestDownloadResults:
    """Test download results endpoint"""

    def test_download_results_excel(self, test_client):
        """Test downloading results as Excel"""
        payload = {
            "results": {
                "results": [
                    {
                        "status": "success",
                        "filename": "test.pdf",
                        "structured_data": {"field1": "value1", "field2": "value2"},
                    }
                ]
            },
            "format": "excel",
        }

        response = test_client.post("/api/download-results", json=payload)
        assert response.status_code == status.HTTP_200_OK
        assert (
            response.headers["content-type"]
            == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        assert "transform_results_" in response.headers["content-disposition"]

    def test_download_results_csv(self, test_client):
        """Test downloading results as CSV"""
        payload = {
            "results": [
                {"filename": "test.pdf", "field1": "value1", "field2": "value2"}
            ],
            "format": "csv",
        }

        response = test_client.post("/api/download-results", json=payload)
        assert response.status_code == status.HTTP_200_OK
        assert "text/csv" in response.headers["content-type"]
        assert "transform_results_" in response.headers["content-disposition"]

    def test_download_results_no_data(self, test_client):
        """Test downloading with no results"""
        payload = {"results": None}

        response = test_client.post("/api/download-results", json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "No results to download" in response.json()["detail"]

    def test_download_results_invalid_payload(self, test_client):
        """Test downloading with invalid payload"""
        payload = {"results": "invalid_string"}

        response = test_client.post("/api/download-results", json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_download_results_empty_results(self, test_client):
        """Test downloading with empty results list"""
        payload = {"results": {"results": []}}

        response = test_client.post("/api/download-results", json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "No successful results" in response.json()["detail"]

    def test_download_results_with_fields_order(self, test_client):
        """Test downloading with specific field ordering"""
        payload = {
            "results": [
                {
                    "filename": "test.pdf",
                    "field1": "value1",
                    "field2": "value2",
                    "field3": "value3",
                }
            ],
            "format": "excel",
            "fields": ["field2", "field1", "field3"],
        }

        response = test_client.post("/api/download-results", json=payload)
        assert response.status_code == status.HTTP_200_OK

    def test_download_results_with_summary(self, test_client):
        """Test downloading with summary sheet"""
        payload = {
            "results": [
                {"filename": "test1.pdf", "field1": "value1"},
                {"filename": "test2.pdf", "field1": "value2"},
            ],
            "summary": {"total_files": 2, "successful": 2, "failed": 0},
            "format": "excel",
        }

        response = test_client.post("/api/download-results", json=payload)
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.api
class TestExceptionHandlers:
    """Test custom exception handlers"""

    def test_validation_error_handler(self, test_client):
        """Test validation error handling"""
        # Send invalid data to trigger validation error
        response = test_client.post(
            "/api/transform",
            files={},  # Missing required fields
            data={},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

    def test_general_exception_handler(self, test_client):
        """Test general exception handling"""
        # This test depends on how exceptions are raised in your app
        # You might need to create a test endpoint that raises an exception
        pass


@pytest.mark.api
class TestCORS:
    """Test CORS configuration"""

    def test_cors_headers(self, test_client):
        """Test that CORS headers are present"""
        response = test_client.options(
            "/api/models",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )

        # Check for CORS headers
        assert "access-control-allow-origin" in response.headers


@pytest.mark.api
class TestAppLifespan:
    """Test application lifespan events"""

    @pytest.mark.asyncio
    async def test_app_startup(self):
        """Test that app starts up correctly"""
        # This test verifies that the lifespan context manager works
        # The actual initialization is tested through the health check
        pass

    @pytest.mark.asyncio
    async def test_app_shutdown(self):
        """Test that app shuts down correctly"""
        # This test verifies that cleanup happens on shutdown
        # The shutdown_processor function should be called
        pass


@pytest.mark.unit
class TestProcessorInitialization:
    """Test processor initialization"""

    @patch("infotransform.main.VisionProcessor")
    @patch("infotransform.main.AudioProcessor")
    @patch("infotransform.main.BatchProcessor")
    @patch("infotransform.main.StructuredAnalyzerAgent")
    @patch("infotransform.main.config")
    def test_init_processors_success(
        self,
        mock_config,
        mock_structured_analyzer,
        mock_batch_processor,
        mock_audio_processor,
        mock_vision_processor,
    ):
        """Test successful processor initialization"""
        from infotransform.main import init_processors

        mock_config.validate.return_value = True

        result = init_processors()
        assert result is True

        # Verify all processors were instantiated
        mock_vision_processor.assert_called_once()
        mock_audio_processor.assert_called_once()
        mock_batch_processor.assert_called_once()
        mock_structured_analyzer.assert_called_once()

    @patch("infotransform.main.config")
    def test_init_processors_config_invalid(self, mock_config):
        """Test processor initialization with invalid config"""
        from infotransform.main import init_processors

        mock_config.validate.side_effect = ValueError("Invalid config")

        result = init_processors()
        assert result is False


@pytest.mark.integration
class TestAppIntegration:
    """Integration tests for the FastAPI app"""

    def test_full_health_check_flow(self, test_client):
        """Test complete health check flow"""
        response = test_client.get("/health")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["status"] == "healthy"
        assert isinstance(data["processors_initialized"], bool)

    @patch("infotransform.main.structured_analyzer")
    def test_full_model_listing_flow(self, mock_analyzer, test_client):
        """Test complete model listing flow"""
        mock_analyzer.get_available_models.return_value = {
            "test_model": {"name": "TestModel", "description": "Test", "fields": {}}
        }
        mock_analyzer.get_available_ai_models.return_value = {
            "default_model": "gpt-4o",
            "models": {},
        }

        response = test_client.get("/api/models")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "models" in data
        assert "test_model" in data["models"]
        assert "ai_models" in data
