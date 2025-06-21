"""
Vision processor for handling images and documents using Markitdown
"""

import os
from markitdown import MarkItDown
from openai import OpenAI
from config import Config


class VisionProcessor:
    def __init__(self):
        """Initialize the vision processor with OpenAI-compatible client"""
        self.client = OpenAI(
            api_key=Config.API_KEY,
            base_url=Config.BASE_URL
        )
        
        # Initialize Markitdown with LLM support for image descriptions
        self.md = MarkItDown(
            llm_client=self.client,
            llm_model=Config.MODEL_NAME
        )
    
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
            result = self.md.convert(file_path, llm_prompt=Config.VISION_PROMPT)
            
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
            Config.ALLOWED_IMAGE_EXTENSIONS | 
            Config.ALLOWED_DOCUMENT_EXTENSIONS
        )
        return ext in supported_extensions
