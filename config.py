import os
import yaml
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class Config:
    def __init__(self):
        # Load YAML configuration
        config_path = Path(__file__).parent / 'config.yaml'
        with open(config_path, 'r') as f:
            self.yaml_config = yaml.safe_load(f)
        
        # Validate on initialization
        self.validate()
    
    # Sensitive data from environment variables
    @property
    def API_KEY(self):
        return os.getenv('API_KEY')
    
    @property
    def SECRET_KEY(self):
        return os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    @property
    def BASE_URL(self):
        return os.getenv('BASE_URL', 'https://api.openai.com/v1')
    
    @property
    def DOCINTEL_ENDPOINT(self):
        return os.getenv('DOCINTEL_ENDPOINT')
    
    # Flask settings (environment-specific)
    @property
    def FLASK_ENV(self):
        return os.getenv('FLASK_ENV', 'development')
    
    @property
    def FLASK_PORT(self):
        return int(os.getenv('FLASK_PORT', 5000))
    
    # Model settings from YAML
    @property
    def MODEL_NAME(self):
        return self.yaml_config['models']['vision']
    
    @property
    def WHISPER_MODEL(self):
        return self.yaml_config['models']['whisper']
    
    @property
    def VISION_PROMPT(self):
        return self.yaml_config['prompts']['vision']
    
    # Upload settings from YAML
    @property
    def UPLOAD_FOLDER(self):
        return self.yaml_config['upload']['folder']
    
    @property
    def MAX_CONTENT_LENGTH(self):
        return self.yaml_config['upload']['max_file_size_mb'] * 1024 * 1024
    
    @property
    def ALLOWED_IMAGE_EXTENSIONS(self):
        return set(self.yaml_config['upload']['allowed_extensions']['images'])
    
    @property
    def ALLOWED_AUDIO_EXTENSIONS(self):
        return set(self.yaml_config['upload']['allowed_extensions']['audio'])
    
    @property
    def ALLOWED_DOCUMENT_EXTENSIONS(self):
        return set(self.yaml_config['upload']['allowed_extensions']['documents'])
    
    # Batch processing from YAML
    @property
    def MAX_CONCURRENT_PROCESSES(self):
        return self.yaml_config['batch_processing']['max_concurrent']
    
    @property
    def BATCH_TIMEOUT(self):
        return self.yaml_config['batch_processing']['timeout_seconds']
    
    @property
    def MAX_ZIP_SIZE(self):
        return self.yaml_config['batch_processing']['max_zip_size_mb'] * 1024 * 1024
    
    @property
    def TEMP_EXTRACT_DIR(self):
        return self.yaml_config['batch_processing']['temp_extract_dir']
    
    # Server settings from YAML
    @property
    def UVICORN_PORT(self):
        return self.yaml_config.get('server', {}).get('uvicorn_port', 8000)
    
    def validate(self):
        """Validate required configuration"""
        if not self.API_KEY:
            raise ValueError("API_KEY is required. Please set it in your .env file")
        
        # Validate YAML structure
        required_keys = ['models', 'prompts', 'upload', 'batch_processing']
        for key in required_keys:
            if key not in self.yaml_config:
                raise ValueError(f"Missing required section '{key}' in config.yaml")
        
        return True

# Create a singleton instance
config = Config()

# For backward compatibility, expose the config instance attributes at module level
# This allows existing code to continue using "from config import Config" pattern
API_KEY = config.API_KEY
SECRET_KEY = config.SECRET_KEY
BASE_URL = config.BASE_URL
DOCINTEL_ENDPOINT = config.DOCINTEL_ENDPOINT
FLASK_ENV = config.FLASK_ENV
FLASK_PORT = config.FLASK_PORT
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
