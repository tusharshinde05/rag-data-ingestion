"""
Automatic file type detection system.
"""

import mimetypes
from pathlib import Path
from typing import Tuple, Optional
from types import FileType


class FileTypeDetector:
    """Detects file types by extension and MIME type."""
    
    # File extension mappings
    EXTENSION_MAP = {
        ".pdf": FileType.PDF,
        ".doc": FileType.DOCX,
        ".docx": FileType.DOCX,
        ".ppt": FileType.PPTX,
        ".pptx": FileType.PPTX,
        ".xls": FileType.XLSX,
        ".xlsx": FileType.XLSX,
        ".csv": FileType.CSV,
        ".json": FileType.JSON,
        ".txt": FileType.TXT,
        ".md": FileType.MD,
        ".markdown": FileType.MD,
        ".html": FileType.HTML,
        ".htm": FileType.HTML,
        ".png": FileType.IMAGE,
        ".jpg": FileType.IMAGE,
        ".jpeg": FileType.IMAGE,
        ".gif": FileType.IMAGE,
        ".tiff": FileType.IMAGE,
        ".tif": FileType.IMAGE,
        ".webp": FileType.IMAGE,
        ".bmp": FileType.IMAGE,
    }
    
    MIME_TYPE_MAP = {
        "application/pdf": FileType.PDF,
        "application/msword": FileType.DOCX,
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": FileType.DOCX,
        "application/vnd.ms-powerpoint": FileType.PPTX,
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": FileType.PPTX,
        "application/vnd.ms-excel": FileType.XLSX,
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": FileType.XLSX,
        "text/csv": FileType.CSV,
        "application/json": FileType.JSON,
        "text/plain": FileType.TXT,
        "text/markdown": FileType.MD,
        "text/html": FileType.HTML,
        "image/png": FileType.IMAGE,
        "image/jpeg": FileType.IMAGE,
        "image/gif": FileType.IMAGE,
        "image/tiff": FileType.IMAGE,
        "image/webp": FileType.IMAGE,
        "image/bmp": FileType.IMAGE,
    }
    
    @staticmethod
    def detect(file_path: Path) -> FileType:
        """
        Detect file type by extension and MIME type.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Detected FileType
        """
        # Try extension first
        extension = file_path.suffix.lower()
        if extension in FileTypeDetector.EXTENSION_MAP:
            return FileTypeDetector.EXTENSION_MAP[extension]
        
        # Try MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type and mime_type in FileTypeDetector.MIME_TYPE_MAP:
            return FileTypeDetector.MIME_TYPE_MAP[mime_type]
        
        return FileType.UNKNOWN
    
    @staticmethod
    def is_text_format(file_type: FileType) -> bool:
        """Check if file type is text-based."""
        return file_type in [
            FileType.TXT, FileType.MD, FileType.JSON,
            FileType.CSV, FileType.HTML
        ]
    
    @staticmethod
    def is_document_format(file_type: FileType) -> bool:
        """Check if file type is a document (PDF, Word, etc.)."""
        return file_type in [
            FileType.PDF, FileType.DOCX, FileType.PPTX, FileType.XLSX
        ]
    
    @staticmethod
    def is_image_format(file_type: FileType) -> bool:
        """Check if file type is an image."""
        return file_type == FileType.IMAGE
