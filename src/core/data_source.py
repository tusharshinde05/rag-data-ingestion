"""
Base classes for data source handling in enterprise RAG system
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class DataSourceType(Enum):
    """Supported data source types"""
    API = "api"
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    WEB = "web"
    CLOUD_STORAGE = "cloud_storage"
    MESSAGE_QUEUE = "message_queue"
    DATABASE_STREAM = "database_stream"


class DataFormat(Enum):
    """Supported data formats"""
    JSON = "json"
    CSV = "csv"
    PARQUET = "parquet"
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    XML = "xml"
    AVRO = "avro"
    PROTOBUF = "protobuf"
    HTML = "html"
    MARKDOWN = "markdown"
    EXCEL = "excel"


@dataclass
class DataChunk:
    """Represents a chunk of ingested data"""
    content: str
    metadata: Dict[str, Any]
    source: str
    format: str
    chunk_id: str
    timestamp: str
    tags: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'content': self.content,
            'metadata': self.metadata,
            'source': self.source,
            'format': self.format,
            'chunk_id': self.chunk_id,
            'timestamp': self.timestamp,
            'tags': self.tags or []
        }


@dataclass
class IngestionConfig:
    """Configuration for data ingestion"""
    batch_size: int = 1000
    chunk_size: int = 1024
    max_retries: int = 3
    retry_delay: int = 5
    timeout: int = 30
    parallel_workers: int = 4
    enable_deduplication: bool = True
    enable_validation: bool = True
    enable_compression: bool = False
    deduplicate_strategy: str = "content_hash"  # content_hash, url, id
    
    
class DataSource(ABC):
    """Abstract base class for all data sources"""
    
    def __init__(self, config: IngestionConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the data source"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to the data source"""
        pass
    
    @abstractmethod
    async def fetch_data(self, query: Optional[str] = None) -> Iterator[DataChunk]:
        """Fetch data from the source"""
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """Validate source configuration"""
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of the data source"""
        return {
            "status": "unknown",
            "connected": False,
            "last_check": None
        }


class DataSourceFactory:
    """Factory for creating data source instances"""
    
    _sources = {}
    
    @classmethod
    def register(cls, source_type: str, source_class):
        """Register a new data source type"""
        cls._sources[source_type] = source_class
        logger.info(f"Registered data source: {source_type}")
    
    @classmethod
    def create(cls, source_type: str, config: IngestionConfig, **kwargs) -> DataSource:
        """Create a data source instance"""
        if source_type not in cls._sources:
            raise ValueError(f"Unknown source type: {source_type}")
        return cls._sources[source_type](config, **kwargs)
    
    @classmethod
    def list_sources(cls) -> List[str]:
        """List all registered sources"""
        return list(cls._sources.keys())
