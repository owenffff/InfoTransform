"""
Vision processor for handling images and documents using Markitdown
"""

import os
import logging
from markitdown import MarkItDown
from openai import OpenAI
from infotransform.config import config
from infotransform.utils.token_counter import log_token_count

logger = logging.getLogger(__name__)


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
        filename = os.path.basename(file_path)
        
        try:
            logger.debug(f"Processing file: {filename}")
            
            # Validate file exists and get basic info
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            file_size = os.path.getsize(file_path)
            logger.debug(f"File size: {file_size} bytes")
            
            # Convert the file using Markitdown with custom vision prompt
            logger.debug(f"Converting {filename} using Markitdown")
            result = self.md.convert(file_path, llm_prompt=config.VISION_PROMPT)
            
            if not hasattr(result, 'text_content') or not result.text_content:
                logger.warning(f"No text content extracted from {filename}")
                return {
                    'success': False,
                    'error': "No text content could be extracted",
                    'filename': filename,
                    'type': 'vision'
                }
            
            # Log token count for the converted content (now at DEBUG level)
            log_token_count(filename, result.text_content, context='vision_processing')
            
            logger.info(f"Successfully processed {filename} ({file_size} bytes)")
            
            return {
                'success': True,
                'content': result.text_content,
                'filename': filename,
                'type': 'vision'
            }
            
        except Exception as e:
            logger.error(f"Error processing {filename}: {type(e).__name__}: {str(e)}")
            logger.debug(f"Full traceback for {filename}:", exc_info=True)
            
            return {
                'success': False,
                'error': f"{type(e).__name__}: {str(e)}",
                'filename': filename,
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
