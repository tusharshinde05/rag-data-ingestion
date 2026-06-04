"""
Type definitions and enums for the data ingestion system.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime


class SourceType(str, Enum):
    """Supported data source types."""
    LOCAL_FILE = "local_file"
    LOCAL_FOLDER = "local_folder"
    AWS_S3 = "aws_s3"
    GCP_STORAGE = "gcp_storage"
    AZURE_BLOB = "azure_blob"
    WEB_URL = "web_url"
    WEB_FOLDER = "web_folder"


class FileType(str, Enum):
    """Supported file formats."""
    PDF = "pdf"
    DOCX = "docx"
    PPTX = "pptx"
    XLSX = "xlsx"
    CSV = "csv"
    JSON = "json"
    TXT = "txt"
    MD = "md"
    HTML = "html"
    IMAGE = "image"  # PNG, JPG, JPEG, GIF, TIFF
    UNKNOWN = "unknown"


class ProcessingStage(str, Enum):
    """Stages of document processing."""
    DETECTED = "detected"
    DOWNLOADED = "downloaded"
    EXTRACTED = "extracted"
    PREPROCESSED = "preprocessed"
    CHUNKED = "chunked"
    EMBEDDED = "embedded"
    STORED = "stored"
    FAILED = "failed"


@dataclass
class DocumentMetadata:
    """Metadata for processed documents."""
    source: str
    source_type: SourceType
    file_type: FileType
    file_name: str
    file_path: Optional[str]
    file_size: Optional[int]
    created_at: datetime
    processed_at: Optional[datetime] = None
    stage: ProcessingStage = ProcessingStage.DETECTED
    tags: Dict[str, str] = None
    custom_metadata: Dict[str, Any] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}
        if self.custom_metadata is None:
            self.custom_metadata = {}


@dataclass
class ExtractedContent:
    """Container for extracted document content."""
    metadata: DocumentMetadata
    raw_text: str
    structured_data: Optional[Dict[str, Any]] = None
    pages: Optional[int] = None
    language: Optional[str] = None
    has_images: bool = False
    has_tables: bool = False
    
    
@dataclass
class ProcessedDocument:
    """Final processed document ready for RAG."""
    metadata: DocumentMetadata
    content: str
    chunks: List[str]
    embedding: Optional[List[float]] = None
    summary: Optional[str] = None
