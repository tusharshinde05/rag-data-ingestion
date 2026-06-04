"""
Cloud storage data sources (AWS S3, GCP, Azure).
"""

import asyncio
from pathlib import Path
from typing import AsyncIterator, Optional
from types import SourceType, DocumentMetadata, ProcessingStage
from datetime import datetime
import boto3
from google.cloud import storage as gcs
from azure.storage.blob import BlobServiceClient
from sources.base_source import BaseDataSource, SourceError
from config import config
from utils.logger import get_logger

logger = get_logger(__name__)


class S3DataSource(BaseDataSource):
    """AWS S3 data source."""
    
    def __init__(self):
        """Initialize S3 source."""
        try:
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
                region_name=config.AWS_REGION,
            )
            self.bucket = config.AWS_S3_BUCKET
            logger.info(f"Initialized S3 source with bucket: {self.bucket}")
        except Exception as e:
            logger.error(f"Failed to initialize S3: {str(e)}")
            raise SourceError(f"Failed to initialize S3: {str(e)}")
    
    async def list_sources(self) -> AsyncIterator[str]:
        """List all objects in S3 bucket."""
        try:
            paginator = self.s3_client.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=self.bucket)
            
            for page in pages:
                if "Contents" in page:
                    for obj in page["Contents"]:
                        if not obj["Key"].endswith("/"):  # Skip folders
                            yield obj["Key"]
        except Exception as e:
            logger.error(f"Failed to list S3 sources: {str(e)}")
            raise SourceError(f"Failed to list S3 sources: {str(e)}")
    
    async def download(self, source: str, destination: Path) -> Path:
        """Download object from S3."""
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            await asyncio.to_thread(
                self.s3_client.download_file,
                self.bucket,
                source,
                str(destination)
            )
            
            logger.info(f"Downloaded S3 object: {source}")
            return destination
            
        except Exception as e:
            logger.error(f"Failed to download from S3: {str(e)}")
            raise SourceError(f"Failed to download from S3: {str(e)}")
    
    def get_metadata(self, source: str) -> DocumentMetadata:
        """Get metadata for S3 object."""
        try:
            response = self.s3_client.head_object(Bucket=self.bucket, Key=source)
            
            return DocumentMetadata(
                source=f"s3://{self.bucket}/{source}",
                source_type=SourceType.AWS_S3,
                file_type=None,  # Will be determined later
                file_name=Path(source).name,
                file_path=source,
                file_size=response["ContentLength"],
                created_at=response["LastModified"],
                stage=ProcessingStage.DETECTED
            )
        except Exception as e:
            logger.error(f"Failed to get S3 metadata: {str(e)}")
            raise SourceError(f"Failed to get S3 metadata: {str(e)}")


class GCPDataSource(BaseDataSource):
    """Google Cloud Storage data source."""
    
    def __init__(self):
        """Initialize GCP source."""
        try:
            self.client = gcs.Client(
                project=config.GCP_PROJECT_ID,
                credentials=config.GCP_CREDENTIALS_PATH
            )
            self.bucket = self.client.bucket(config.GCP_BUCKET_NAME)
            logger.info(f"Initialized GCP source with bucket: {config.GCP_BUCKET_NAME}")
        except Exception as e:
            logger.error(f"Failed to initialize GCP: {str(e)}")
            raise SourceError(f"Failed to initialize GCP: {str(e)}")
    
    async def list_sources(self) -> AsyncIterator[str]:
        """List all blobs in GCP bucket."""
        try:
            blobs = self.client.list_blobs(self.bucket.name)
            for blob in blobs:
                if not blob.name.endswith("/"):  # Skip folders
                    yield blob.name
        except Exception as e:
            logger.error(f"Failed to list GCP sources: {str(e)}")
            raise SourceError(f"Failed to list GCP sources: {str(e)}")
    
    async def download(self, source: str, destination: Path) -> Path:
        """Download blob from GCP."""
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            blob = self.bucket.blob(source)
            await asyncio.to_thread(blob.download_to_filename, str(destination))
            
            logger.info(f"Downloaded GCP blob: {source}")
            return destination
            
        except Exception as e:
            logger.error(f"Failed to download from GCP: {str(e)}")
            raise SourceError(f"Failed to download from GCP: {str(e)}")
    
    def get_metadata(self, source: str) -> DocumentMetadata:
        """Get metadata for GCP blob."""
        try:
            blob = self.bucket.blob(source)
            blob.reload()
            
            return DocumentMetadata(
                source=f"gs://{self.bucket.name}/{source}",
                source_type=SourceType.GCP_STORAGE,
                file_type=None,  # Will be determined later
                file_name=Path(source).name,
                file_path=source,
                file_size=blob.size,
                created_at=blob.updated,
                stage=ProcessingStage.DETECTED
            )
        except Exception as e:
            logger.error(f"Failed to get GCP metadata: {str(e)}")
            raise SourceError(f"Failed to get GCP metadata: {str(e)}")


class AzureDataSource(BaseDataSource):
    """Azure Blob Storage data source."""
    
    def __init__(self):
        """Initialize Azure source."""
        try:
            self.client = BlobServiceClient(
                account_name=config.AZURE_STORAGE_ACCOUNT_NAME,
                account_key=config.AZURE_STORAGE_ACCOUNT_KEY
            )
            self.container = self.client.get_container_client(config.AZURE_CONTAINER_NAME)
            logger.info(f"Initialized Azure source with container: {config.AZURE_CONTAINER_NAME}")
        except Exception as e:
            logger.error(f"Failed to initialize Azure: {str(e)}")
            raise SourceError(f"Failed to initialize Azure: {str(e)}")
    
    async def list_sources(self) -> AsyncIterator[str]:
        """List all blobs in Azure container."""
        try:
            blobs = self.container.list_blobs()
            for blob in blobs:
                if not blob.name.endswith("/"):  # Skip folders
                    yield blob.name
        except Exception as e:
            logger.error(f"Failed to list Azure sources: {str(e)}")
            raise SourceError(f"Failed to list Azure sources: {str(e)}")
    
    async def download(self, source: str, destination: Path) -> Path:
        """Download blob from Azure."""
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            blob_client = self.container.get_blob_client(source)
            data = await asyncio.to_thread(blob_client.download_blob)
            
            with open(destination, "wb") as f:
                await asyncio.to_thread(f.write, data.readall())
            
            logger.info(f"Downloaded Azure blob: {source}")
            return destination
            
        except Exception as e:
            logger.error(f"Failed to download from Azure: {str(e)}")
            raise SourceError(f"Failed to download from Azure: {str(e)}")
    
    def get_metadata(self, source: str) -> DocumentMetadata:
        """Get metadata for Azure blob."""
        try:
            blob_client = self.container.get_blob_client(source)
            properties = blob_client.get_blob_properties()
            
            return DocumentMetadata(
                source=f"az://{config.AZURE_CONTAINER_NAME}/{source}",
                source_type=SourceType.AZURE_BLOB,
                file_type=None,  # Will be determined later
                file_name=Path(source).name,
                file_path=source,
                file_size=properties.size,
                created_at=properties.creation_time,
                stage=ProcessingStage.DETECTED
            )
        except Exception as e:
            logger.error(f"Failed to get Azure metadata: {str(e)}")
            raise SourceError(f"Failed to get Azure metadata: {str(e)}")
