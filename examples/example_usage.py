"""
Example usage of the RAG data ingestion system.
"""

import asyncio
from pathlib import Path
from ingestion_pipeline import DataIngestionPipeline
from types import SourceType
from utils.logger import get_logger

logger = get_logger(__name__)


async def example_local_ingestion():
    """Example: Ingest from local folder."""
    pipeline = DataIngestionPipeline()
    
    async for doc in pipeline.ingest_from_source(
        SourceType.LOCAL_FOLDER,
        path=Path("./documents")
    ):
        logger.info(f"Processed document: {doc.metadata.file_name}")
        logger.info(f"Content chunks: {len(doc.chunks)}")
        print(f"\nMetadata: {doc.metadata}")
        print(f"First chunk: {doc.chunks[0][:200]}...")


async def example_s3_ingestion():
    """Example: Ingest from AWS S3."""
    pipeline = DataIngestionPipeline()
    
    async for doc in pipeline.ingest_from_source(SourceType.AWS_S3):
        logger.info(f"Processed S3 document: {doc.metadata.file_name}")


async def example_web_ingestion():
    """Example: Ingest from web URLs."""
    pipeline = DataIngestionPipeline()
    
    async for doc in pipeline.ingest_from_source(
        SourceType.WEB_URL,
        urls=["https://example.com"],
        recursive=True,
        depth=2
    ):
        logger.info(f"Processed web document: {doc.metadata.file_name}")


async def example_batch_ingestion():
    """Example: Ingest from multiple sources in parallel."""
    pipeline = DataIngestionPipeline()
    
    sources = [
        {
            "type": SourceType.LOCAL_FOLDER,
            "kwargs": {"path": Path("./documents")}
        },
        {
            "type": SourceType.AWS_S3,
            "kwargs": {}
        }
    ]
    
    docs = await pipeline.ingest_batch(sources, parallel_workers=2)
    
    for doc in docs:
        logger.info(f"Processed: {doc.metadata.file_name}")


async def example_with_callback():
    """Example: Ingest with processing callback."""
    pipeline = DataIngestionPipeline()
    
    async def process_document(doc):
        """Custom processing for each document."""
        logger.info(f"Custom processing: {doc.metadata.file_name}")
        # Could save to database, send for embedding, etc.
    
    async for doc in pipeline.ingest_from_source(
        SourceType.LOCAL_FOLDER,
        process_callback=process_document,
        path=Path("./documents")
    ):
        pass


if __name__ == "__main__":
    # Run examples (uncomment one)
    # asyncio.run(example_local_ingestion())
    # asyncio.run(example_s3_ingestion())
    # asyncio.run(example_web_ingestion())
    # asyncio.run(example_batch_ingestion())
    asyncio.run(example_with_callback())
