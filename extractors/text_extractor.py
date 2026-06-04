"""
Extractor for plain text and markdown files.
"""

import chardet
from pathlib import Path
from types import ExtractedContent, DocumentMetadata, FileType
from extractors.base_extractor import BaseExtractor, ExtractionError
from utils.logger import get_logger

logger = get_logger(__name__)


class TextExtractor(BaseExtractor):
    """Extractor for .txt and .md files."""
    
    def can_extract(self, file_path: Path) -> bool:
        """Check if file is text or markdown."""
        suffix = file_path.suffix.lower()
        return suffix in [".txt", ".md", ".markdown"]
    
    async def extract(self, file_path: Path, metadata: DocumentMetadata) -> ExtractedContent:
        """
        Extract text from plain text or markdown files.
        
        Args:
            file_path: Path to the text file
            metadata: Document metadata
            
        Returns:
            Extracted content
        """
        try:
            # Detect encoding
            with open(file_path, "rb") as f:
                raw_data = f.read()
                detected = chardet.detect(raw_data)
                encoding = detected.get("encoding", "utf-8")
            
            # Read file with detected encoding
            with open(file_path, "r", encoding=encoding, errors="ignore") as f:
                content = f.read()
            
            logger.info(f"Extracted text from {file_path.name}", extra={
                "file_size": file_path.stat().st_size,
                "encoding": encoding
            })
            
            return ExtractedContent(
                metadata=metadata,
                raw_text=content,
                language="markdown" if metadata.file_type == FileType.MD else "text"
            )
            
        except Exception as e:
            logger.error(f"Failed to extract text from {file_path}: {str(e)}")
            raise ExtractionError(f"Text extraction failed: {str(e)}")
