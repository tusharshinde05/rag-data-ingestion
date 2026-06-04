"""
Base class for data sources.
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional
from pathlib import Path
from types import SourceType, DocumentMetadata
from datetime import datetime


class BaseDataSource(ABC):
    """Abstract base class for data sources."""
    
    @abstractmethod
    async def list_sources(self) -> AsyncIterator[str]:
        """
        List available sources (files or URLs).
        
        Yields:
            Source identifiers
        """
        pass
    
    @abstractmethod
    async def download(self, source: str, destination: Path) -> Path:
        """
        Download or retrieve source to local path.
        
        Args:
            source: Source identifier
            destination: Local destination path
            
        Returns:
            Path to downloaded file
        """
        pass
    
    @abstractmethod
    def get_metadata(self, source: str) -> DocumentMetadata:
        """
        Get metadata for a source.
        
        Args:
            source: Source identifier
            
        Returns:
            Document metadata
        """
        pass


class SourceError(Exception):
    """Custom exception for source errors."""
    pass
