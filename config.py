"""
Configuration module for RAG data ingestion system.
Handles environment variables and settings management.
"""

from pathlib import Path
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field


class DataSourceConfig(BaseSettings):
    """Configuration for different data sources."""
    
    # Local file system
    LOCAL_BASE_PATH: Path = Field(default=Path("./data"), description="Base path for local files")
    
    # Cloud storage - AWS S3
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None)
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None)
    AWS_REGION: str = Field(default="us-east-1")
    AWS_S3_BUCKET: Optional[str] = Field(default=None)
    
    # Cloud storage - Google Cloud
    GCP_PROJECT_ID: Optional[str] = Field(default=None)
    GCP_CREDENTIALS_PATH: Optional[Path] = Field(default=None)
    GCP_BUCKET_NAME: Optional[str] = Field(default=None)
    
    # Cloud storage - Azure
    AZURE_STORAGE_ACCOUNT_NAME: Optional[str] = Field(default=None)
    AZURE_STORAGE_ACCOUNT_KEY: Optional[str] = Field(default=None)
    AZURE_CONTAINER_NAME: Optional[str] = Field(default=None)
    
    # Web scraping
    SELENIUM_HEADLESS: bool = Field(default=True)
    REQUEST_TIMEOUT: int = Field(default=30)
    MAX_RETRIES: int = Field(default=3)
    
    # OCR Configuration
    OCR_ENABLED: bool = Field(default=True)
    OCR_LANGUAGE: str = Field(default="en")
    OCR_GPU: bool = Field(default=False)
    
    # Processing
    CHUNK_SIZE: int = Field(default=1000)
    CHUNK_OVERLAP: int = Field(default=200)
    MAX_WORKERS: int = Field(default=4)
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(default="json")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


config = DataSourceConfig()
