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
        
        # Load performance configuration
        perf_config_path = Path(__file__).parent.parent.parent / 'config' / 'performance.yaml'
        if perf_config_path.exists():
            with open(perf_config_path, 'r') as f:
                self.performance_config = yaml.safe_load(f)
        else:
            logger.info("Performance config not found, using defaults")
            self.performance_config = self._get_default_performance_config()
        
        # Pattern for environment variable substitution
        self._env_pattern = re.compile(r'\$\{([^}]+)\}')
        
        # Process environment variables in configs
        self.yaml_config = self._process_env_vars(self.yaml_config)
        self.performance_config = self._process_env_vars(self.performance_config)
        
        # Apply performance profile if specified
        self._apply_performance_profile()
        
        # Validate on initialization
        self.validate()
    
    def _process_env_vars(self, config: Any) -> Any:
        """Recursively process environment variables in configuration"""
        if isinstance(config, dict):
            return {k: self._process_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._process_env_vars(item) for item in config]
        elif isinstance(config, str):
            # Replace ${VAR_NAME} or ${VAR_NAME:-default} with environment variable value
            def replace_env_var(match):
                var_expr = match.group(1)
                # Check if it has a default value (VAR:-default syntax)
                if ':-' in var_expr:
                    var_name, default_value = var_expr.split(':-', 1)
                    value = os.getenv(var_name.strip())
                    if value is None:
                        # Use the default value
                        return default_value
                else:
                    var_name = var_expr.strip()
                    value = os.getenv(var_name)
                    if value is None and var_name in ['OPENAI_API_KEY', 'OPENAI_BASE_URL']:
                        # Don't fail for optional env vars
                        return None
                    if value is None:
                        # Return the original expression if no value found
                        return match.group(0)
                return value
            
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
    
    # Model settings from YAML - updated for new structure
    @property
    def MODEL_NAME(self):
        return self.get('ai_pipeline.markdown_conversion.vision_model', 'azure.gpt-4o')
    
    @property
    def WHISPER_MODEL(self):
        return self.get('ai_pipeline.markdown_conversion.audio_model', 'whisper-1')
    
    @property
    def VISION_PROMPT(self):
        return self.get('ai_pipeline.markdown_conversion.vision_prompt', '')
    
    # AI Model Configuration - updated for new structure
    def get_ai_model_config(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """Get configuration for a specific AI model"""
        if model_name is None:
            model_name = self.get('ai_pipeline.structured_analysis.default_model', 'azure.gpt-4o')
        
        # Return structured analysis config for the model
        config = {
            'temperature': self.get('ai_pipeline.structured_analysis.temperature', 0.7),
            'seed': self.get('ai_pipeline.structured_analysis.seed', 42),
            'streaming': self.get('ai_pipeline.structured_analysis.streaming', {}),
        }
        
        # Add connection settings
        connection_config = self.get('ai_connection.api_config', {})
        config.update(connection_config)
        
        return config
    
    def get_analysis_prompt(self, model_key: Optional[str] = None) -> str:
        """Get system prompt for analysis"""
        if model_key:
            model_prompt = self.get(f'ai_pipeline.structured_analysis.prompts.{model_key}')
            if model_prompt:
                return model_prompt
        
        return self.get('ai_pipeline.structured_analysis.prompts.default', '')
    
    def get_prompt_template(self, template_name: str) -> Optional[str]:
        """Get a specific prompt template"""
        if template_name == 'analysis_prompt':
            return self.get('ai_pipeline.structured_analysis.prompt_template')
        return None
    
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
    
    def _get_default_performance_config(self) -> Dict[str, Any]:
        """Get default performance configuration"""
        return {
            'markdown_conversion': {
                'max_workers': 10,
                'worker_type': 'thread',
                'queue_size': 100,
                'timeout_per_file': 30
            },
            'ai_processing': {
                'batch_size': 10,
                'max_wait_time': 2.0,
                'max_concurrent_batches': 3,
                'timeout_per_batch': 60,
                'retry_attempts': 3
            },
            'file_management': {
                'cleanup_strategy': 'stream_complete',
                'max_file_retention': 300,
                'cleanup_check_interval': 10
            },
            'resource_limits': {
                'max_memory_per_file_mb': 100,
                'max_total_memory_mb': 1000,
                'cpu_limit_percentage': 80
            },
            'monitoring': {
                'enable_metrics': True,
                'metrics_interval': 60,
                'slow_operation_threshold': 5.0,
                'enable_profiling': False
            }
        }
    
    def _apply_performance_profile(self):
        """Apply performance profile if specified"""
        profile_name = os.getenv('PERFORMANCE_PROFILE')
        if not profile_name:
            return
        
        profiles = self.performance_config.get('profiles', {})
        if profile_name not in profiles:
            logger.warning(f"Performance profile '{profile_name}' not found")
            return
        
        logger.info(f"Applying performance profile: {profile_name}")
        profile = profiles[profile_name]
        
        # Apply profile settings
        for key_path, value in profile.items():
            keys = key_path.split('.')
            target = self.performance_config
            
            # Navigate to the parent of the target key
            for key in keys[:-1]:
                if key not in target:
                    target[key] = {}
                target = target[key]
            
            # Set the value
            target[keys[-1]] = value
    
    def get_performance(self, key_path: str, default: Any = None) -> Any:
        """
        Get performance configuration value using dot notation
        
        Args:
            key_path: Dot-separated path to configuration value
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.performance_config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def validate(self):
        """Validate required configuration"""
        if not self.API_KEY:
            raise ValueError("OPENAI_API_KEY is required. Please set it in your .env file")
        
        # Validate YAML structure - updated for new structure
        required_sections = ['app', 'ai_pipeline', 'processing']
        for section in required_sections:
            if section not in self.yaml_config:
                raise ValueError(f"Missing required section '{section}' in config.yaml")
        
        # Validate AI pipeline structure
        ai_pipeline = self.yaml_config.get('ai_pipeline', {})
        required_ai_sections = ['markdown_conversion', 'summarization', 'structured_analysis']
        for section in required_ai_sections:
            if section not in ai_pipeline:
                raise ValueError(f"Missing required AI pipeline section '{section}' in config.yaml")
        
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
