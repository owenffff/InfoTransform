import os
import re
import yaml
from dotenv import load_dotenv
from pathlib import Path
from typing import Any, Dict, Optional
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class Config:
    def __init__(self):
        # Load YAML configuration
        # Look for config.yaml in the project root (two levels up from this file)
        config_path = Path(__file__).parent.parent.parent / 'config' / 'config.yaml'
        if not config_path.exists():
            # Fallback to old location for backward compatibility
            config_path = Path(__file__).parent.parent.parent / 'config.yaml'
        
        with open(config_path, 'r') as f:
            self.yaml_config = yaml.safe_load(f)
        
        # Pattern for environment variable substitution
        self._env_pattern = re.compile(r'\$\{([^}]+)\}')
        
        # Process environment variables in config
        self.yaml_config = self._process_env_vars(self.yaml_config)
        
        # Validate on initialization
        self.validate()
    
    def _process_env_vars(self, config: Any) -> Any:
        """Recursively process environment variables in configuration"""
        if isinstance(config, dict):
            return {k: self._process_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._process_env_vars(item) for item in config]
        elif isinstance(config, str):
            # Replace ${VAR_NAME} with environment variable value
            def replace_env_var(match):
                var_name = match.group(1)
                value = os.getenv(var_name)
                if value is None and var_name in ['OPENAI_API_KEY', 'OPENAI_BASE_URL']:
                    # Don't fail for optional env vars
                    return None
                return value if value is not None else match.group(0)
            
            result = self._env_pattern.sub(replace_env_var, config)
            return None if result is None else result
        else:
            return config
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        
        Args:
            key_path: Dot-separated path to configuration value (e.g., 'api.port')
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.yaml_config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    # Sensitive data from environment variables
    @property
    def API_KEY(self):
        # Use OPENAI_API_KEY as the standard
        return os.getenv('OPENAI_API_KEY')
    
    @property
    def SECRET_KEY(self):
        return os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    @property
    def BASE_URL(self):
        # Use OPENAI_BASE_URL as the standard, with fallback to OpenAI's default
        return os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
    
    @property
    def DOCINTEL_ENDPOINT(self):
        # Use standardized Azure Document Intelligence endpoint name
        return os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')
    
    # Server settings (environment-specific)
    @property
    def PORT(self):
        return int(os.getenv('PORT', self.get('api.port', 8000)))
    
    # Model settings from YAML
    @property
    def MODEL_NAME(self):
        return self.get('models.vision', 'gpt-4-vision-preview')
    
    @property
    def WHISPER_MODEL(self):
        return self.get('models.whisper', 'whisper-1')
    
    @property
    def VISION_PROMPT(self):
        return self.get('prompts.vision', '')
    
    # AI Model Configuration
    def get_ai_model_config(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """Get configuration for a specific AI model"""
        if model_name is None:
            model_name = self.get('models.ai_models.default_model', 'gpt-4o-mini')
        
        models = self.get('models.ai_models.models', {})
        return models.get(model_name, {})
    
    def get_analysis_prompt(self, model_key: Optional[str] = None) -> str:
        """Get system prompt for analysis"""
        if model_key:
            model_prompt = self.get(f'prompts.analysis.model_specific.{model_key}')
            if model_prompt:
                return model_prompt
        
        return self.get('prompts.analysis.default', '')
    
    def get_prompt_template(self, template_name: str) -> Optional[str]:
        """Get a specific prompt template"""
        return self.get(f'prompts.analysis.templates.{template_name}')
    
    # Upload settings from YAML
    @property
    def UPLOAD_FOLDER(self):
        # Use data directory in project root
        folder = self.get('processing.upload.folder', 'uploads')
        return str(Path(__file__).parent.parent.parent / 'data' / folder)
    
    @property
    def MAX_CONTENT_LENGTH(self):
        return self.get('processing.upload.max_file_size_mb', 16) * 1024 * 1024
    
    @property
    def ALLOWED_IMAGE_EXTENSIONS(self):
        return set(self.get('processing.upload.allowed_extensions.images', []))
    
    @property
    def ALLOWED_AUDIO_EXTENSIONS(self):
        return set(self.get('processing.upload.allowed_extensions.audio', []))
    
    @property
    def ALLOWED_DOCUMENT_EXTENSIONS(self):
        return set(self.get('processing.upload.allowed_extensions.documents', []))
    
    # Batch processing from YAML
    @property
    def MAX_CONCURRENT_PROCESSES(self):
        return self.get('processing.batch.max_concurrent', 5)
    
    @property
    def BATCH_TIMEOUT(self):
        return self.get('processing.batch.timeout_seconds', 300)
    
    @property
    def MAX_ZIP_SIZE(self):
        return self.get('processing.batch.max_zip_size_mb', 100) * 1024 * 1024
    
    @property
    def TEMP_EXTRACT_DIR(self):
        # Use data directory in project root
        folder = self.get('processing.batch.temp_extract_dir', 'temp_extracts')
        return str(Path(__file__).parent.parent.parent / 'data' / folder)
    
    # Feature flags
    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled"""
        return self.get(f'features.{feature_name}', False)
    
    def is_experimental_feature_enabled(self, feature_name: str) -> bool:
        """Check if an experimental feature is enabled"""
        return self.get(f'features.experimental.{feature_name}', False)
    
    
    def validate(self):
        """Validate required configuration"""
        if not self.API_KEY:
            raise ValueError("OPENAI_API_KEY is required. Please set it in your .env file")
        
        # Validate YAML structure - updated for new structure
        required_sections = ['app', 'models', 'prompts', 'processing']
        for section in required_sections:
            if section not in self.yaml_config:
                raise ValueError(f"Missing required section '{section}' in config.yaml")
        
        return True

# Create a singleton instance
config = Config()

# For backward compatibility, expose the config instance attributes at module level
# This allows existing code to continue using "from config import Config" pattern
API_KEY = config.API_KEY
SECRET_KEY = config.SECRET_KEY
BASE_URL = config.BASE_URL
DOCINTEL_ENDPOINT = config.DOCINTEL_ENDPOINT
PORT = config.PORT
MODEL_NAME = config.MODEL_NAME
WHISPER_MODEL = config.WHISPER_MODEL
VISION_PROMPT = config.VISION_PROMPT
UPLOAD_FOLDER = config.UPLOAD_FOLDER
MAX_CONTENT_LENGTH = config.MAX_CONTENT_LENGTH
ALLOWED_IMAGE_EXTENSIONS = config.ALLOWED_IMAGE_EXTENSIONS
ALLOWED_AUDIO_EXTENSIONS = config.ALLOWED_AUDIO_EXTENSIONS
ALLOWED_DOCUMENT_EXTENSIONS = config.ALLOWED_DOCUMENT_EXTENSIONS
MAX_CONCURRENT_PROCESSES = config.MAX_CONCURRENT_PROCESSES
BATCH_TIMEOUT = config.BATCH_TIMEOUT
MAX_ZIP_SIZE = config.MAX_ZIP_SIZE
TEMP_EXTRACT_DIR = config.TEMP_EXTRACT_DIR
