"""
Factory pattern for creating appropriate extractors.
"""

from pathlib import Path
from typing import List
from extractors.base_extractor import BaseExtractor
from extractors.text_extractor import TextExtractor
from extractors.pdf_extractor import PDFExtractor
from extractors.office_extractor import DOCXExtractor, PPTXExtractor, XLSXExtractor
from extractors.data_extractor import CSVExtractor, JSONExtractor, HTMLExtractor
from extractors.image_extractor import ImageExtractor
from utils.logger import get_logger

logger = get_logger(__name__)


class ExtractorFactory:
    """Factory for creating extractors based on file type."""
    
    def __init__(self):
        """Initialize extractors."""
        self.extractors: List[BaseExtractor] = [
            PDFExtractor(),
            DOCXExtractor(),
            PPTXExtractor(),
            XLSXExtractor(),
            CSVExtractor(),
            JSONExtractor(),
            HTMLExtractor(),
            TextExtractor(),
            ImageExtractor(),
        ]
    
    def get_extractor(self, file_path: Path) -> BaseExtractor:
        """
        Get appropriate extractor for file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Appropriate extractor instance
            
        Raises:
            ValueError: If no extractor found for file type
        """
        for extractor in self.extractors:
            if extractor.can_extract(file_path):
                logger.debug(f"Selected {type(extractor).__name__} for {file_path.name}")
                return extractor
        
        raise ValueError(f"No extractor found for file: {file_path}")
    
    def get_all_supported_extensions(self) -> List[str]:
        """Get list of all supported file extensions."""
        extensions = set()
        
        for extractor in self.extractors:
            # This could be extended with a method in each extractor
            pass
        
        return sorted(list(extensions))
