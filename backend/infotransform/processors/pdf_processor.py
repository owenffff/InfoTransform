"""
PDF processor with intelligent detection for text-based vs image-based PDFs

This module provides cost-efficient PDF processing by:
1. Quickly analyzing PDFs to detect text content
2. Using markitdown for text-based PDFs (fast, free)
3. Routing image-based/scanned PDFs to Azure Document Intelligence (OCR)
"""

import os
import logging
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

from markitdown import MarkItDown
from openai import OpenAI
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
from io import StringIO

from infotransform.config import config

logger = logging.getLogger(__name__)


class PdfAnalyzer:
    """Analyzes PDFs to determine if they are text-based or image-based"""

    def __init__(self):
        self.min_chars_per_page = config.get(
            "processing.pdf.detection.min_chars_per_page", 50
        )
        self.text_page_threshold_percent = config.get(
            "processing.pdf.detection.text_page_threshold_percent", 70
        )

    def analyze_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a PDF to determine if it needs OCR

        Args:
            file_path: Path to the PDF file

        Returns:
            Dictionary with analysis results:
            - needs_ocr: bool - Whether the PDF needs OCR
            - total_pages: int - Total number of pages
            - text_pages: int - Number of pages with sufficient text
            - scanned_pages: int - Number of pages that appear scanned
            - text_page_percentage: float - Percentage of pages with text
            - reason: str - Explanation of the decision
        """
        try:
            logger.info(f"Analyzing PDF: {os.path.basename(file_path)}")

            # Extract text from all pages using pdfminer.six
            page_texts = self._extract_page_texts(file_path)
            total_pages = len(page_texts)

            if total_pages == 0:
                return {
                    "needs_ocr": True,
                    "total_pages": 0,
                    "text_pages": 0,
                    "scanned_pages": 0,
                    "text_page_percentage": 0.0,
                    "reason": "Could not read PDF pages",
                }

            # Analyze each page
            text_pages = 0
            scanned_pages = 0

            for i, text in enumerate(page_texts):
                char_count = len(text.strip())
                if char_count >= self.min_chars_per_page:
                    text_pages += 1
                    logger.debug(
                        f"Page {i+1}: {char_count} chars - text-based"
                    )
                else:
                    scanned_pages += 1
                    logger.debug(
                        f"Page {i+1}: {char_count} chars - likely scanned/image"
                    )

            text_page_percentage = (text_pages / total_pages) * 100

            # Decision logic: threshold-based approach
            needs_ocr = text_page_percentage < self.text_page_threshold_percent

            if needs_ocr:
                reason = (
                    f"Only {text_page_percentage:.1f}% of pages have sufficient text "
                    f"(threshold: {self.text_page_threshold_percent}%). "
                    f"Routing to OCR for complete extraction."
                )
            else:
                reason = (
                    f"{text_page_percentage:.1f}% of pages have sufficient text. "
                    f"Using standard text extraction (skipping {scanned_pages} scanned pages)."
                )

            result = {
                "needs_ocr": needs_ocr,
                "total_pages": total_pages,
                "text_pages": text_pages,
                "scanned_pages": scanned_pages,
                "text_page_percentage": text_page_percentage,
                "reason": reason,
            }

            logger.info(
                f"PDF Analysis: {os.path.basename(file_path)} - "
                f"{text_pages}/{total_pages} text pages ({text_page_percentage:.1f}%) - "
                f"Needs OCR: {needs_ocr}"
            )

            return result

        except Exception as e:
            logger.error(f"Error analyzing PDF {file_path}: {str(e)}", exc_info=True)
            return {
                "needs_ocr": True,  # Default to OCR on error
                "total_pages": 0,
                "text_pages": 0,
                "scanned_pages": 0,
                "text_page_percentage": 0.0,
                "reason": f"Analysis failed: {str(e)}. Defaulting to OCR.",
            }

    def _extract_page_texts(self, file_path: str) -> List[str]:
        """
        Extract text from each page of a PDF

        Args:
            file_path: Path to the PDF file

        Returns:
            List of text content for each page
        """
        page_texts = []

        try:
            from pdfminer.pdfpage import PDFPage
            from pdfminer.converter import TextConverter
            from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter

            # Create resource manager
            rsrcmgr = PDFResourceManager()

            with open(file_path, "rb") as fp:
                # Process each page individually
                for page_num, page in enumerate(PDFPage.get_pages(fp)):
                    output = StringIO()
                    device = TextConverter(
                        rsrcmgr, output, laparams=LAParams()
                    )
                    interpreter = PDFPageInterpreter(rsrcmgr, device)

                    try:
                        interpreter.process_page(page)
                        text = output.getvalue()
                        page_texts.append(text)
                    except Exception as e:
                        logger.warning(
                            f"Could not extract text from page {page_num + 1}: {str(e)}"
                        )
                        page_texts.append("")
                    finally:
                        device.close()
                        output.close()

            return page_texts

        except Exception as e:
            logger.error(f"Error extracting page texts: {str(e)}", exc_info=True)
            return []


class PdfProcessor:
    """
    Processes PDFs using intelligent routing between text extraction and OCR
    """

    def __init__(self):
        """Initialize the PDF processor with OpenAI-compatible client"""
        self.client = OpenAI(api_key=config.API_KEY, base_url=config.BASE_URL)
        self.analyzer = PdfAnalyzer()

        # Initialize markitdown instances
        # One without Azure (for quick text extraction)
        self.md_text = MarkItDown(
            llm_client=self.client, llm_model=config.MODEL_NAME
        )

        # One with Azure (for OCR when needed)
        if config.DOCINTEL_ENDPOINT:
            self.md_ocr = MarkItDown(
                llm_client=self.client,
                llm_model=config.MODEL_NAME,
                docintel_endpoint=config.DOCINTEL_ENDPOINT,
            )
            logger.info(
                f"Azure Document Intelligence enabled: {config.DOCINTEL_ENDPOINT}"
            )
        else:
            self.md_ocr = None
            logger.warning(
                "Azure Document Intelligence not configured. "
                "Scanned PDFs will fail without AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT."
            )

    def process_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Process a PDF file with intelligent routing

        Args:
            file_path: Path to the PDF file

        Returns:
            Dictionary with processing result
        """
        filename = os.path.basename(file_path)

        try:
            # Step 1: Analyze the PDF to determine if it needs OCR
            analysis = self.analyzer.analyze_pdf(file_path)

            logger.info(
                f"PDF {filename}: {analysis['reason']}"
            )

            # Step 2: Route to appropriate processor
            if analysis["needs_ocr"]:
                return self._process_with_ocr(file_path, filename, analysis)
            else:
                return self._process_with_text_extraction(
                    file_path, filename, analysis
                )

        except Exception as e:
            logger.error(f"Error processing PDF {filename}: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"PDF processing failed: {str(e)}",
                "error_type": "pdf_processing_error",
                "filename": filename,
                "type": "pdf",
            }

    def _process_with_text_extraction(
        self, file_path: str, filename: str, analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process PDF using standard text extraction (markitdown without Azure)

        Args:
            file_path: Path to the PDF file
            filename: Name of the file
            analysis: Analysis results from PdfAnalyzer

        Returns:
            Processing result dictionary
        """
        try:
            logger.info(
                f"Processing {filename} with text extraction (FREE) - "
                f"{analysis['text_pages']}/{analysis['total_pages']} pages"
            )

            # Use markitdown WITHOUT Azure Document Intelligence
            result = self.md_text.convert(file_path, llm_prompt=config.VISION_PROMPT)

            if not hasattr(result, "text_content") or not result.text_content:
                logger.warning(f"No text content extracted from {filename}")
                return {
                    "success": False,
                    "error": "Could not extract text from PDF.",
                    "error_type": "text_extraction_failure",
                    "filename": filename,
                    "type": "pdf",
                    "analysis": analysis,
                }

            logger.info(
                f"Successfully extracted text from {filename} "
                f"({len(result.text_content)} chars)"
            )

            return {
                "success": True,
                "content": result.text_content,
                "filename": filename,
                "type": "pdf",
                "extraction_method": "text_extraction",
                "cost": "free",
                "analysis": analysis,
            }

        except Exception as e:
            logger.error(
                f"Text extraction failed for {filename}: {str(e)}", exc_info=True
            )
            return {
                "success": False,
                "error": f"Text extraction failed: {str(e)}",
                "error_type": "text_extraction_error",
                "filename": filename,
                "type": "pdf",
                "analysis": analysis,
            }

    def _process_with_ocr(
        self, file_path: str, filename: str, analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process PDF using Azure Document Intelligence OCR

        Args:
            file_path: Path to the PDF file
            filename: Name of the file
            analysis: Analysis results from PdfAnalyzer

        Returns:
            Processing result dictionary
        """
        # Check if Azure is configured
        if not self.md_ocr:
            error_msg = (
                f"PDF '{filename}' appears to be image-based/scanned "
                f"({analysis['scanned_pages']}/{analysis['total_pages']} pages have insufficient text). "
                f"Azure Document Intelligence is required but not configured. "
                f"Set AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT in your .env file. "
                f"See README.md for setup instructions."
            )
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "error_type": "ocr_not_configured",
                "filename": filename,
                "type": "pdf",
                "azure_configured": False,
                "analysis": analysis,
            }

        try:
            logger.info(
                f"Processing {filename} with Azure OCR ($$$) - "
                f"{analysis['scanned_pages']}/{analysis['total_pages']} scanned pages"
            )

            # Use markitdown WITH Azure Document Intelligence
            result = self.md_ocr.convert(file_path, llm_prompt=config.VISION_PROMPT)

            if not hasattr(result, "text_content") or not result.text_content:
                logger.warning(f"No text content extracted from {filename} via OCR")
                return {
                    "success": False,
                    "error": "OCR extraction returned no content.",
                    "error_type": "ocr_failure",
                    "filename": filename,
                    "type": "pdf",
                    "azure_configured": True,
                    "analysis": analysis,
                }

            logger.info(
                f"Successfully extracted text from {filename} via OCR "
                f"({len(result.text_content)} chars)"
            )

            return {
                "success": True,
                "content": result.text_content,
                "filename": filename,
                "type": "pdf",
                "extraction_method": "azure_ocr",
                "cost": "paid",
                "analysis": analysis,
                "azure_configured": True,
            }

        except Exception as e:
            logger.error(f"OCR failed for {filename}: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"OCR processing failed: {str(e)}",
                "error_type": "ocr_error",
                "filename": filename,
                "type": "pdf",
                "azure_configured": True,
                "analysis": analysis,
            }

    def is_supported_file(self, filename: str) -> bool:
        """Check if the file is a PDF"""
        return filename.lower().endswith(".pdf")
