"""
Vision processor for handling images and documents using Markitdown
"""

import os
import logging
from markitdown import MarkItDown

# Attempt to import a specific exception raised for password-protected PDFs.
# Older/newer MarkItDown versions might not expose it, so fall back gracefully.
try:
    from markitdown.exceptions import PDFPasswordIncorrect  # type: ignore
except Exception:  # pragma: no cover

    class PDFPasswordIncorrect(Exception):
        """Fallback placeholder when MarkItDown does not expose PDFPasswordIncorrect."""

        pass


from openai import OpenAI
from infotransform.config import config
from infotransform.processors.pdf_processor import PdfProcessor

logger = logging.getLogger(__name__)


class VisionProcessor:
    def __init__(self):
        """Initialize the vision processor with OpenAI-compatible client"""
        self.client = OpenAI(api_key=config.API_KEY, base_url=config.BASE_URL)

        # Initialize Markitdown with LLM support (no Azure - for non-PDF images only)
        self.md = MarkItDown(llm_client=self.client, llm_model=config.MODEL_NAME)

        # Initialize PDF processor for intelligent PDF handling
        self.pdf_processor = PdfProcessor()

    def process_file(self, file_path):
        """
        Process an image or document file and extract text/content

        Args:
            file_path (str): Path to the file to process

        Returns:
            dict: Processing result with text content and metadata
        """
        filename = os.path.basename(file_path)
        is_pdf = filename.lower().endswith(".pdf")

        # Route PDFs to the intelligent PDF processor
        if is_pdf:
            logger.debug(f"Routing PDF {filename} to PdfProcessor")
            return self.pdf_processor.process_pdf(file_path)

        # Process non-PDF images with markitdown
        try:
            logger.debug(f"Processing image file: {filename}")

            # Validate file exists and get basic info
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            file_size = os.path.getsize(file_path)
            logger.debug(f"File size: {file_size} bytes")

            # Convert the file using Markitdown with custom vision prompt
            logger.debug(f"Converting {filename} using Markitdown")
            result = self.md.convert(file_path, llm_prompt=config.VISION_PROMPT)

            if not hasattr(result, "text_content") or not result.text_content:
                logger.warning(f"No text content extracted from {filename}")
                return {
                    "success": False,
                    "error": "Could not extract text from image.",
                    "error_type": "ocr_failure",
                    "filename": filename,
                    "type": "vision",
                }

            logger.info(f"Successfully processed {filename} ({file_size} bytes)")

            return {
                "success": True,
                "content": result.text_content,
                "filename": filename,
                "type": "vision",
            }

        except Exception as e:
            logger.error(f"Error processing {filename}: {type(e).__name__}: {str(e)}")
            logger.debug(f"Full traceback for {filename}:", exc_info=True)

            # Categorize common error types
            error_msg = str(e).lower()
            if "corrupt" in error_msg or "invalid" in error_msg or "bad" in error_msg:
                error_type = "corrupt_file"
                pretty_msg = "File appears to be corrupted."
            else:
                error_type = "generic"
                pretty_msg = "File processing failed."

            return {
                "success": False,
                "error": pretty_msg,
                "error_type": error_type,
                "filename": filename,
                "type": "vision",
            }

    def is_supported_file(self, filename):
        """Check if the file type is supported for vision processing"""
        ext = filename.lower().split(".")[-1]
        supported_extensions = (
            config.ALLOWED_IMAGE_EXTENSIONS | config.ALLOWED_DOCUMENT_EXTENSIONS
        )
        return ext in supported_extensions
