"""
Main entry point and CLI interface for the RAG data ingestion system.
"""

import asyncio
import argparse
from pathlib import Path
from typing import List, Dict, Any
from ingestion_pipeline import DataIngestionPipeline
from types import SourceType
from utils.logger import get_logger

logger = get_logger(__name__)


class DataIngestionCLI:
    """Command-line interface for the ingestion system."""
    
    def __init__(self):
        """Initialize CLI."""
        self.pipeline = DataIngestionPipeline()
    
    async def ingest_local(self, path: str, output: str = None):
        """Ingest from local folder."""
        logger.info(f"Starting local ingestion from: {path}")
        
        docs = []
        async for doc in self.pipeline.ingest_from_source(
            SourceType.LOCAL_FOLDER,
            path=Path(path)
        ):
            docs.append(doc)
            logger.info(f"✓ Processed: {doc.metadata.file_name}")
        
        logger.info(f"Successfully ingested {len(docs)} documents")
        return docs
    
    async def ingest_s3(self, output: str = None):
        """Ingest from AWS S3."""
        logger.info("Starting S3 ingestion")
        
        docs = []
        async for doc in self.pipeline.ingest_from_source(SourceType.AWS_S3):
            docs.append(doc)
            logger.info(f"✓ Processed: {doc.metadata.file_name}")
        
        logger.info(f"Successfully ingested {len(docs)} documents")
        return docs
    
    async def ingest_web(self, urls: List[str], recursive: bool = False, depth: int = 1):
        """Ingest from web URLs."""
        logger.info(f"Starting web ingestion from: {urls}")
        
        docs = []
        async for doc in self.pipeline.ingest_from_source(
            SourceType.WEB_URL,
            urls=urls,
            recursive=recursive,
            depth=depth
        ):
            docs.append(doc)
            logger.info(f"✓ Processed: {doc.metadata.file_name}")
        
        logger.info(f"Successfully ingested {len(docs)} documents")
        return docs


async def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Enterprise RAG Data Ingestion System"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Local ingestion
    local_parser = subparsers.add_parser("local", help="Ingest from local folder")
    local_parser.add_argument("path", help="Path to local folder")
    local_parser.add_argument("--output", help="Output file path")
    
    # S3 ingestion
    s3_parser = subparsers.add_parser("s3", help="Ingest from AWS S3")
    s3_parser.add_argument("--output", help="Output file path")
    
    # Web ingestion
    web_parser = subparsers.add_parser("web", help="Ingest from web URLs")
    web_parser.add_argument("urls", nargs="+", help="URLs to ingest")
    web_parser.add_argument("--recursive", action="store_true", help="Recursive crawling")
    web_parser.add_argument("--depth", type=int, default=1, help="Crawl depth")
    web_parser.add_argument("--output", help="Output file path")
    
    args = parser.parse_args()
    cli = DataIngestionCLI()
    
    if args.command == "local":
        await cli.ingest_local(args.path, args.output)
    elif args.command == "s3":
        await cli.ingest_s3(args.output)
    elif args.command == "web":
        await cli.ingest_web(args.urls, args.recursive, args.depth)
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
