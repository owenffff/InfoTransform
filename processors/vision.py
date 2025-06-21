"""
Vision processor for handling images and documents using Markitdown
"""

import os
from markitdown import MarkItDown
from openai import OpenAI
from config import config


class VisionProcessor:
    def __init__(self):
        """Initialize the vision processor with OpenAI-compatible client"""
        self.client = OpenAI(
            api_key=config.API_KEY,
            base_url=config.BASE_URL
        )
        
        # Initialize Markitdown with LLM support and optional Azure Document Intelligence
        init_params = {
            'llm_client': self.client,
            'llm_model': config.MODEL_NAME
        }
        
        # Add Azure Document Intelligence endpoint if configured
        if config.DOCINTEL_ENDPOINT:
            init_params['docintel_endpoint'] = config.DOCINTEL_ENDPOINT
            print(f"✓ Azure Document Intelligence enabled: {config.DOCINTEL_ENDPOINT}")
        
        self.md = MarkItDown(**init_params)
    
    def process_file(self, file_path):
        """
        Process an image or document file and extract text/content
        
        Args:
            file_path (str): Path to the file to process
            
        Returns:
            dict: Processing result with text content and metadata
        """
        try:
            # Convert the file using Markitdown with custom vision prompt
            result = self.md.convert(file_path, llm_prompt=config.VISION_PROMPT)
            
            return {
                'success': True,
                'content': result.text_content,
                'filename': os.path.basename(file_path),
                'type': 'vision'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'filename': os.path.basename(file_path),
                'type': 'vision'
            }
    
    def is_supported_file(self, filename):
        """Check if the file type is supported for vision processing"""
        ext = filename.lower().split('.')[-1]
        supported_extensions = (
            config.ALLOWED_IMAGE_EXTENSIONS | 
            config.ALLOWED_DOCUMENT_EXTENSIONS
        )
        return ext in supported_extensions
