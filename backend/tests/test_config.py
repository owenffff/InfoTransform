"""
Unit tests for configuration management
"""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from infotransform.config import Config


class TestConfig:
    """Test configuration loading and validation"""

    def test_config_initialization(self, mock_env_vars):
        """Test that config initializes properly"""
        config = Config()
        assert config is not None
        assert config.API_KEY == "test-api-key-123"

    def test_config_get_method(self, test_config):
        """Test config.get() method with dot notation"""
        # Test existing key
        app_name = test_config.get("app.name")
        assert app_name is not None

        # Test default value
        non_existent = test_config.get("non.existent.key", "default_value")
        assert non_existent == "default_value"

    def test_api_key_from_env(self, mock_env_vars):
        """Test API key is loaded from environment"""
        config = Config()
        assert config.API_KEY == mock_env_vars["OPENAI_API_KEY"]

    def test_port_configuration(self, mock_env_vars):
        """Test PORT configuration with different env vars"""
        config = Config()
        assert config.PORT == 8000

        # Test with BACKEND_PORT override
        with patch.dict(os.environ, {"BACKEND_PORT": "9000"}, clear=False):
            config = Config()
            assert config.PORT == 9000

    def test_base_url_configuration(self, mock_env_vars):
        """Test BASE_URL configuration"""
        config = Config()
        assert config.BASE_URL == "https://api.openai.com/v1"

    def test_upload_folder_path(self, test_config):
        """Test that upload folder path is correctly configured"""
        upload_folder = test_config.UPLOAD_FOLDER
        assert upload_folder is not None
        assert isinstance(upload_folder, str)
        assert Path(upload_folder).exists() or "data" in upload_folder

    def test_temp_extract_dir_path(self, test_config):
        """Test that temp extract directory path is correctly configured"""
        temp_dir = test_config.TEMP_EXTRACT_DIR
        assert temp_dir is not None
        assert isinstance(temp_dir, str)

    def test_allowed_extensions(self, test_config):
        """Test that allowed file extensions are loaded"""
        # Image extensions
        image_ext = test_config.ALLOWED_IMAGE_EXTENSIONS
        assert isinstance(image_ext, set)

        # Audio extensions
        audio_ext = test_config.ALLOWED_AUDIO_EXTENSIONS
        assert isinstance(audio_ext, set)

        # Document extensions
        doc_ext = test_config.ALLOWED_DOCUMENT_EXTENSIONS
        assert isinstance(doc_ext, set)

    def test_model_configuration(self, test_config):
        """Test AI model configuration"""
        model_name = test_config.MODEL_NAME
        assert model_name is not None

        whisper_model = test_config.WHISPER_MODEL
        assert whisper_model is not None

    def test_get_ai_model_config(self, test_config):
        """Test getting AI model configuration"""
        model_config = test_config.get_ai_model_config()
        assert "temperature" in model_config
        assert "seed" in model_config
        assert "streaming" in model_config

    def test_get_analysis_prompt(self, test_config):
        """Test getting analysis prompts"""
        # Default prompt
        default_prompt = test_config.get_analysis_prompt()
        assert default_prompt is not None or default_prompt == ""

    def test_feature_flags(self, test_config):
        """Test feature flag checking"""
        # Test a feature flag (may not exist, should return False)
        is_enabled = test_config.is_feature_enabled("some_feature")
        assert isinstance(is_enabled, bool)

    def test_get_performance_config(self, test_config):
        """Test getting performance configuration"""
        # Test markdown conversion workers
        max_workers = test_config.get_performance("markdown_conversion.max_workers", 10)
        assert isinstance(max_workers, int)
        assert max_workers > 0

        # Test batch size
        batch_size = test_config.get_performance("ai_processing.batch_size", 10)
        assert isinstance(batch_size, int)
        assert batch_size > 0

    def test_config_validation_requires_api_key(self):
        """Test that validation fails without API key"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                config = Config()
                config.validate()

    def test_config_validation_with_valid_config(self, test_config):
        """Test that validation passes with valid config"""
        # Should not raise any exceptions
        result = test_config.validate()
        assert result is True

    def test_env_var_substitution(self, mock_env_vars):
        """Test environment variable substitution in config"""
        config = Config()
        # API key should be substituted from env var
        assert config.API_KEY == mock_env_vars["OPENAI_API_KEY"]

    def test_max_content_length(self, test_config):
        """Test max content length configuration"""
        max_length = test_config.MAX_CONTENT_LENGTH
        assert isinstance(max_length, int)
        assert max_length > 0

    def test_max_concurrent_processes(self, test_config):
        """Test max concurrent processes configuration"""
        max_concurrent = test_config.MAX_CONCURRENT_PROCESSES
        assert isinstance(max_concurrent, int)
        assert max_concurrent > 0

    @pytest.mark.parametrize(
        "env_name,expected_default",
        [
            ("development", True),
            ("production", True),
            ("staging", True),
        ],
    )
    def test_environment_specific_configs(
        self, env_name, expected_default, mock_env_vars
    ):
        """Test loading environment-specific configurations"""
        with patch.dict(os.environ, {"ENV": env_name}, clear=False):
            config = Config()
            # Config should load without errors
            assert config is not None


class TestConfigEdgeCases:
    """Test edge cases and error handling in configuration"""

    def test_missing_config_key_returns_default(self, test_config):
        """Test that missing config keys return default value"""
        result = test_config.get("non.existent.key", "my_default")
        assert result == "my_default"

    def test_nested_config_access(self, test_config):
        """Test accessing nested configuration values"""
        # Try accessing a nested value
        app_config = test_config.get("app")
        assert isinstance(app_config, dict)

    def test_invalid_port_falls_back_to_default(self):
        """Test that invalid port values fall back to default"""
        with patch.dict(os.environ, {"PORT": "invalid_port"}, clear=False):
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=False):
                config = Config()
                # Should fall back to default port
                assert isinstance(config.PORT, int)

    def test_get_prompt_template(self, test_config):
        """Test getting prompt templates"""
        template = test_config.get_prompt_template("analysis_prompt")
        # Template may or may not exist
        assert template is None or isinstance(template, str)

    def test_performance_profile_application(self, mock_env_vars):
        """Test that performance profiles are applied if configured"""
        config = Config()
        # Should not raise errors
        assert config.performance_config is not None
