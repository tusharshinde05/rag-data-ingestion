"""
Extractor for image files with OCR support.
"""

from pathlib import Path
import easyocr
from PIL import Image
from types import ExtractedContent, DocumentMetadata
from extractors.base_extractor import BaseExtractor, ExtractionError
from config import config
from utils.logger import get_logger

logger = get_logger(__name__)


class ImageExtractor(BaseExtractor):
    """Extractor for image files with OCR."""
    
    def __init__(self):
        """Initialize image extractor."""
        self.ocr_reader = None
        if config.OCR_ENABLED:
            try:
                self.ocr_reader = easyocr.Reader(
                    [config.OCR_LANGUAGE],
                    gpu=config.OCR_GPU
                )
                logger.info("OCR reader initialized for images")
            except Exception as e:
                logger.warning(f"Failed to initialize OCR: {str(e)}")
    
    def can_extract(self, file_path: Path) -> bool:
        """Check if file is an image."""
        image_extensions = [".png", ".jpg", ".jpeg", ".gif", ".tiff", ".webp", ".bmp"]
        return file_path.suffix.lower() in image_extensions
    
    async def extract(self, file_path: Path, metadata: DocumentMetadata) -> ExtractedContent:
        """
        Extract text from image using OCR.
        
        Args:
            file_path: Path to image file
            metadata: Document metadata
            
        Returns:
            Extracted content
        """
        try:
            if not config.OCR_ENABLED or not self.ocr_reader:
                logger.warning(f"OCR not enabled, returning image metadata only")
                return ExtractedContent(
                    metadata=metadata,
                    raw_text="[Image file - OCR not enabled]"
                )
            
            # Open image
            image = Image.open(file_path)
            
            # Run OCR
            results = self.ocr_reader.readtext(image)
            
            # Extract text from results
            text_content = [text for (_, text, confidence) in results]
            text = "\n".join(text_content)
            
            logger.info(f"Extracted text from image {file_path.name}", extra={
                "text_length": len(text),
                "image_size": image.size
            })
            
            return ExtractedContent(
                metadata=metadata,
                raw_text=text
            )
            
        except Exception as e:
            logger.error(f"Failed to extract image {file_path}: {str(e)}")
            raise ExtractionError(f"Image extraction failed: {str(e)}")
