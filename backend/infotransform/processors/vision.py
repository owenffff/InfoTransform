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

logger = logging.getLogger(__name__)


class VisionProcessor:
    def __init__(self):
        """Initialize the vision processor with OpenAI-compatible client"""
        self.client = OpenAI(api_key=config.API_KEY, base_url=config.BASE_URL)

        # Initialize Markitdown with LLM support and optional Azure Document Intelligence
        init_params = {"llm_client": self.client, "llm_model": config.MODEL_NAME}

        # Add Azure Document Intelligence endpoint if configured
        if config.DOCINTEL_ENDPOINT:
            init_params["docintel_endpoint"] = config.DOCINTEL_ENDPOINT
            print(
                f"[OK] Azure Document Intelligence enabled: {config.DOCINTEL_ENDPOINT}"
            )

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
        is_pdf = filename.lower().endswith(".pdf")

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

            if not hasattr(result, "text_content") or not result.text_content:
                logger.warning(f"No text content extracted from {filename}")

                # Provide specific guidance for PDFs
                if is_pdf:
                    if not config.DOCINTEL_ENDPOINT:
                        error_msg = (
                            "Could not extract text from PDF. This may be an image-based (scanned) PDF. "
                            "To process scanned PDFs, configure Azure Document Intelligence by setting "
                            "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT in your .env file. "
                            "See README.md for setup instructions."
                        )
                    else:
                        error_msg = "Could not extract text from PDF. The file may be corrupted or in an unsupported format."
                else:
                    error_msg = "Could not extract text from image."

                return {
                    "success": False,
                    "error": error_msg,
                    "error_type": "ocr_failure",
                    "filename": filename,
                    "type": "vision",
                    "azure_configured": bool(config.DOCINTEL_ENDPOINT),
                }

            # Check if extracted content is suspiciously short for a PDF (might be image-based)
            if is_pdf and len(result.text_content.strip()) < 100:
                logger.warning(
                    f"PDF {filename} extracted very little text ({len(result.text_content)} chars). "
                    f"This may be an image-based PDF. Azure Document Intelligence: {'enabled' if config.DOCINTEL_ENDPOINT else 'not configured'}"
                )

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

            # Categorise common error types so upper layers can react properly
            error_msg = str(e).lower()
            if isinstance(e, PDFPasswordIncorrect) or "password" in error_msg:
                error_type = "password_required"
                pretty_msg = "PDF is password-protected."
            elif "corrupt" in error_msg or "invalid" in error_msg or "bad" in error_msg:
                error_type = "corrupt_file"
                pretty_msg = "File appears to be corrupted."
            else:
                error_type = "generic"
                # Provide Azure guidance for PDFs if not configured
                if is_pdf and not config.DOCINTEL_ENDPOINT:
                    pretty_msg = (
                        "File processing failed. For scanned/image-based PDFs, configure Azure Document Intelligence. "
                        "Set AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT in your .env file. See README.md for details."
                    )
                else:
                    pretty_msg = "File processing failed."

            return {
                "success": False,
                "error": pretty_msg,
                "error_type": error_type,
                "filename": filename,
                "type": "vision",
                "azure_configured": bool(config.DOCINTEL_ENDPOINT),
            }

    def is_supported_file(self, filename):
        """Check if the file type is supported for vision processing"""
        ext = filename.lower().split(".")[-1]
        supported_extensions = (
            config.ALLOWED_IMAGE_EXTENSIONS | config.ALLOWED_DOCUMENT_EXTENSIONS
        )
        return ext in supported_extensions
