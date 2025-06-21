import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # API Configuration
    API_KEY = os.getenv('API_KEY')
    BASE_URL = os.getenv('BASE_URL', 'https://api.openai.com/v1')
    MODEL_NAME = os.getenv('MODEL_NAME', 'gpt-4-vision-preview')
    WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'whisper-1')
    
    # Vision prompt for image analysis
    VISION_PROMPT = os.getenv('VISION_PROMPT', """Please analyze this image and provide output in the following format:

1. If the image contains text (documents, screenshots, signs, etc.):
   - Extract ALL visible text exactly as it appears
   - Preserve the original formatting, line breaks, and structure
   - Include any headers, bullet points, or special formatting
   - If there are multiple columns, process them in reading order

2. If the image contains no text or minimal text:
   - Provide a detailed description of the image content
   - Mention key visual elements, objects, people, or scenes
   - Note any important details or context

3. If the image contains both text and visual elements:
   - First extract all text content
   - Then provide a brief description of non-text elements

Format your response as clean markdown.""")
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    
    # Upload Configuration
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
    ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'm4a', 'flac', 'ogg', 'webm'}
    ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'docx', 'pptx', 'xlsx'}
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.API_KEY:
            raise ValueError("API_KEY is required. Please set it in your .env file")
        return True
