"""
Base extractor interface for all content extraction strategies.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from types import ExtractedContent, DocumentMetadata


class BaseExtractor(ABC):
    """Abstract base class for content extractors."""
    
    @abstractmethod
    def can_extract(self, file_path: Path) -> bool:
        """
        Check if this extractor can handle the file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if extractor can handle this file
        """
        pass
    
    @abstractmethod
    async def extract(self, file_path: Path, metadata: DocumentMetadata) -> ExtractedContent:
        """
        Extract content from the file.
        
        Args:
            file_path: Path to the file
            metadata: Document metadata
            
        Returns:
            Extracted content
        """
        pass


class ExtractionError(Exception):
    """Custom exception for extraction errors."""
    pass
