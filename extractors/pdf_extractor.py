"""
Extractor for PDF files with OCR support.
"""

import asyncio
from pathlib import Path
from typing import Optional
import PyPDF2
import pytesseract
from pdf2image import convert_from_path
import easyocr
from types import ExtractedContent, DocumentMetadata
from extractors.base_extractor import BaseExtractor, ExtractionError
from config import config
from utils.logger import get_logger

logger = get_logger(__name__)


class PDFExtractor(BaseExtractor):
    """Extractor for PDF files with OCR fallback."""
    
    def __init__(self):
        """Initialize PDF extractor."""
        self.ocr_reader = None
        if config.OCR_ENABLED:
            try:
                self.ocr_reader = easyocr.Reader(
                    [config.OCR_LANGUAGE],
                    gpu=config.OCR_GPU
                )
                logger.info("OCR reader initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize OCR: {str(e)}")
    
    def can_extract(self, file_path: Path) -> bool:
        """Check if file is PDF."""
        return file_path.suffix.lower() == ".pdf"
    
    async def extract(self, file_path: Path, metadata: DocumentMetadata) -> ExtractedContent:
        """
        Extract content from PDF with OCR fallback.
        
        Args:
            file_path: Path to PDF file
            metadata: Document metadata
            
        Returns:
            Extracted content
        """
        try:
            # Try standard PDF text extraction first
            text = await self._extract_text(file_path)
            
            # If very little text, use OCR
            if len(text.strip()) < 100 and config.OCR_ENABLED:
                logger.info(f"Low text content detected in {file_path.name}, using OCR")
                text = await self._extract_with_ocr(file_path)
            
            # Get page count
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                page_count = len(pdf_reader.pages)
            
            logger.info(f"Extracted PDF from {file_path.name}", extra={
                "pages": page_count,
                "text_length": len(text)
            })
            
            return ExtractedContent(
                metadata=metadata,
                raw_text=text,
                pages=page_count
            )
            
        except Exception as e:
            logger.error(f"Failed to extract PDF {file_path}: {str(e)}")
            raise ExtractionError(f"PDF extraction failed: {str(e)}")
    
    async def _extract_text(self, file_path: Path) -> str:
        """Extract text from PDF using PyPDF2."""
        text_content = []
        
        try:
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
            
            return "\n".join(text_content)
            
        except Exception as e:
            logger.warning(f"PyPDF2 extraction failed: {str(e)}")
            return ""
    
    async def _extract_with_ocr(self, file_path: Path) -> str:
        """Extract text using OCR."""
        text_content = []
        
        try:
            # Convert PDF to images
            images = convert_from_path(str(file_path))
            
            # Run OCR on each image
            for image in images:
                if self.ocr_reader:
                    results = self.ocr_reader.readtext(image)
                    text = "\n".join([text for (_, text, _) in results])
                    text_content.append(text)
            
            return "\n".join(text_content)
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            return ""
