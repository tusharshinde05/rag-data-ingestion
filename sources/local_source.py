"""
Local file system data source.
"""

import asyncio
from pathlib import Path
from typing import AsyncIterator, Optional
from types import SourceType, DocumentMetadata, ProcessingStage
from datetime import datetime
from sources.base_source import BaseDataSource, SourceError
from utils.logger import get_logger

logger = get_logger(__name__)


class LocalFileSource(BaseDataSource):
    """Data source for local file system."""
    
    def __init__(self, base_path: Path):
        """
        Initialize local file source.
        
        Args:
            base_path: Base path for local files
        """
        self.base_path = Path(base_path)
        if not self.base_path.exists():
            self.base_path.mkdir(parents=True, exist_ok=True)
    
    async def list_sources(self) -> AsyncIterator[str]:
        """List all files in base path recursively."""
        try:
            for file_path in self.base_path.rglob("*"):
                if file_path.is_file():
                    yield str(file_path)
        except Exception as e:
            logger.error(f"Failed to list sources: {str(e)}")
            raise SourceError(f"Failed to list sources: {str(e)}")
    
    async def download(self, source: str, destination: Path) -> Path:
        """
        Copy local file to destination.
        
        Args:
            source: Source file path
            destination: Destination path
            
        Returns:
            Path to file
        """
        try:
            source_path = Path(source)
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # For local files, we can just return the source or copy if needed
            logger.info(f"Processing local file: {source}")
            return source_path
            
        except Exception as e:
            logger.error(f"Failed to download local file: {str(e)}")
            raise SourceError(f"Failed to process local file: {str(e)}")
    
    def get_metadata(self, source: str) -> DocumentMetadata:
        """Get metadata for local file."""
        file_path = Path(source)
        
        return DocumentMetadata(
            source=source,
            source_type=SourceType.LOCAL_FILE,
            file_type=None,  # Will be determined later
            file_name=file_path.name,
            file_path=str(file_path),
            file_size=file_path.stat().st_size,
            created_at=datetime.fromtimestamp(file_path.stat().st_ctime),
            stage=ProcessingStage.DETECTED
        )
