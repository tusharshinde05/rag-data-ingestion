"""
Main data ingestion pipeline orchestrator.
"""

import asyncio
from pathlib import Path
from typing import Optional, List, AsyncIterator, Dict, Any
from types import (
    SourceType, DocumentMetadata, FileType, ExtractedContent, 
    ProcessedDocument, ProcessingStage
)
from datetime import datetime
from extractors.extractor_factory import ExtractorFactory
from extractors.base_extractor import ExtractionError
from sources.local_source import LocalFileSource
from sources.cloud_sources import S3DataSource, GCPDataSource, AzureDataSource
from sources.web_source import WebURLSource
from sources.base_source import BaseDataSource, SourceError
from processors.preprocessor import TextPreprocessor, TextChunker
from utils.logger import get_logger
from utils.type_detector import FileTypeDetector
from config import config

logger = get_logger(__name__)


class DataIngestionPipeline:
    """
    Enterprise-level data ingestion pipeline with multi-source support.
    
    Features:
    - Automatic format detection
    - Multi-source support (local, cloud, web)
    - OCR for scanned documents
    - Async processing
    - Error handling and retry logic
    - Structured logging
    """
    
    def __init__(self):
        """Initialize the ingestion pipeline."""
        self.extractor_factory = ExtractorFactory()
        self.temp_dir = Path("./temp_downloads")
        self.temp_dir.mkdir(exist_ok=True)
        
        logger.info("DataIngestionPipeline initialized")
    
    def get_data_source(self, source_type: SourceType, **kwargs) -> BaseDataSource:
        """
        Factory method to create appropriate data source.
        
        Args:
            source_type: Type of data source
            **kwargs: Additional arguments for the source
            
        Returns:
            Data source instance
        """
        sources_map = {
            SourceType.LOCAL_FILE: lambda: LocalFileSource(config.LOCAL_BASE_PATH),
            SourceType.LOCAL_FOLDER: lambda: LocalFileSource(kwargs.get("path", config.LOCAL_BASE_PATH)),
            SourceType.AWS_S3: lambda: S3DataSource(),
            SourceType.GCP_STORAGE: lambda: GCPDataSource(),
            SourceType.AZURE_BLOB: lambda: AzureDataSource(),
            SourceType.WEB_URL: lambda: WebURLSource(
                kwargs.get("urls", []),
                recursive=kwargs.get("recursive", False),
                depth=kwargs.get("depth", 1)
            ),
        }
        
        if source_type not in sources_map:
            raise ValueError(f"Unsupported source type: {source_type}")
        
        return sources_map[source_type]()
    
    async def ingest_from_source(
        self,
        source_type: SourceType,
        process_callback: Optional[callable] = None,
        **source_kwargs
    ) -> AsyncIterator[ProcessedDocument]:
        """
        Main ingestion method - handles full pipeline.
        
        Args:
            source_type: Type of data source
            process_callback: Callback function for each processed document
            **source_kwargs: Arguments specific to the source type
            
        Yields:
            Processed documents ready for RAG
        """
        source = self.get_data_source(source_type, **source_kwargs)
        
        async for source_identifier in source.list_sources():
            try:
                # Get metadata
                metadata = source.get_metadata(source_identifier)
                
                # Download/retrieve file
                local_path = await source.download(
                    source_identifier,
                    self.temp_dir / metadata.file_name
                )
                
                # Detect file type
                file_type = FileTypeDetector.detect(local_path)
                metadata.file_type = file_type
                metadata.stage = ProcessingStage.DOWNLOADED
                
                logger.info(f"Processing file: {metadata.file_name}", extra={
                    "file_type": file_type.value,
                    "source": source_type.value
                })
                
                # Extract content
                extracted = await self._extract_content(local_path, metadata)
                extracted.metadata.stage = ProcessingStage.EXTRACTED
                
                # Preprocess
                preprocessed_text = await self._preprocess_content(extracted)
                extracted.metadata.stage = ProcessingStage.PREPROCESSED
                
                # Chunk
                chunks = await self._chunk_content(preprocessed_text)
                extracted.metadata.stage = ProcessingStage.CHUNKED
                
                # Create processed document
                doc = ProcessedDocument(
                    metadata=extracted.metadata,
                    content=preprocessed_text,
                    chunks=chunks
                )
                
                if process_callback:
                    await process_callback(doc)
                
                yield doc
                
                # Cleanup
                local_path.unlink(missing_ok=True)
                
            except (ExtractionError, SourceError) as e:
                logger.error(f"Failed to process source: {str(e)}", extra={
                    "source": source_identifier
                })
                metadata.stage = ProcessingStage.FAILED
                metadata.error_message = str(e)
                metadata.retry_count += 1
                continue
    
    async def _extract_content(self, file_path: Path, metadata: DocumentMetadata) -> ExtractedContent:
        """Extract content from file."""
        try:
            extractor = self.extractor_factory.get_extractor(file_path)
            return await extractor.extract(file_path, metadata)
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            raise ExtractionError(f"Failed to extract: {str(e)}")
    
    async def _preprocess_content(self, extracted: ExtractedContent) -> str:
        """Preprocess extracted content."""
        try:
            text = TextPreprocessor.preprocess(
                extracted.raw_text,
                remove_urls=False,
                remove_emails=False
            )
            logger.debug(f"Preprocessed text length: {len(text)}")
            return text
        except Exception as e:
            logger.error(f"Preprocessing failed: {str(e)}")
            return extracted.raw_text
    
    async def _chunk_content(self, text: str) -> List[str]:
        """Chunk preprocessed content."""
        try:
            chunks = TextChunker.chunk_by_paragraphs(
                text,
                max_chunk_size=config.CHUNK_SIZE
            )
            logger.debug(f"Created {len(chunks)} chunks")
            return chunks
        except Exception as e:
            logger.error(f"Chunking failed: {str(e)}")
            return [text]
    
    async def ingest_batch(
        self,
        sources: List[Dict[str, Any]],
        parallel_workers: int = None
    ) -> List[ProcessedDocument]:
        """
        Ingest multiple sources in parallel.
        
        Args:
            sources: List of source configurations
            parallel_workers: Number of parallel workers
            
        Returns:
            List of processed documents
        """
        if parallel_workers is None:
            parallel_workers = config.MAX_WORKERS
        
        results = []
        semaphore = asyncio.Semaphore(parallel_workers)
        
        async def ingest_with_semaphore(source_config):
            async with semaphore:
                docs = []
                async for doc in self.ingest_from_source(
                    source_config["type"],
                    **source_config.get("kwargs", {})
                ):
                    docs.append(doc)
                return docs
        
        tasks = [ingest_with_semaphore(source) for source in sources]
        batch_results = await asyncio.gather(*tasks)
        
        for batch in batch_results:
            results.extend(batch)
        
        return results
