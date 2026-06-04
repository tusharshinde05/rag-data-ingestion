# Enterprise RAG Data Ingestion System

A production-ready, enterprise-level data ingestion system designed specifically for RAG (Retrieval Augmented Generation) pipelines. Supports automatic format detection, multi-source data ingestion (local, cloud, web), OCR processing, and intelligent text preprocessing.

## 🎯 Features

### Multi-Source Support
- **Local File System**: Recursive folder traversal with automatic format detection
- **AWS S3**: Seamless integration with S3 buckets
- **Google Cloud Storage**: GCS bucket support
- **Azure Blob Storage**: Azure container support
- **Web URLs**: HTTP/HTTPS URLs with optional recursive crawling

### Format Support
- **Documents**: PDF (with OCR fallback), DOCX, PPTX, XLSX
- **Data Formats**: CSV, JSON, HTML
- **Text**: TXT, Markdown
- **Images**: PNG, JPG, JPEG, GIF, TIFF, WebP, BMP (with OCR)

### Advanced Processing
- **Automatic Format Detection**: Detects file type by extension and MIME type
- **OCR Integration**: EasyOCR for scanned documents and images
- **Text Preprocessing**: Cleaning, normalization, duplicate removal
- **Intelligent Chunking**: Multiple chunking strategies (size, sentences, paragraphs)
- **Encoding Detection**: Automatic character encoding detection

### Enterprise Features
- **Async/Await**: Non-blocking async processing for high performance
- **Parallel Processing**: Concurrent batch ingestion with configurable workers
- **Structured Logging**: JSON-formatted logs for easy parsing
- **Error Handling**: Comprehensive error handling with retry logic
- **Type Safety**: Full type hints with Pydantic models
- **Configuration Management**: Environment-based configuration

## 📦 Installation

### Prerequisites
- Python 3.11+
- Tesseract OCR (for OCR support)

### Setup

```bash
# Clone repository
git clone https://github.com/tusharshinde05/rag-data-ingestion.git
cd rag-data-ingestion

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Configure .env with your settings
```

### System Dependencies (Optional - for OCR)

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr libtesseract-dev
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Download from [GitHub Tesseract releases](https://github.com/UB-Mannheim/tesseract/wiki)

## 🚀 Quick Start

### CLI Usage

```bash
# Ingest from local folder
python main.py local ./documents

# Ingest from AWS S3
python main.py s3

# Ingest from web URLs
python main.py web https://example.com https://docs.example.com --recursive --depth 2
```

### Python API Usage

```python
import asyncio
from pathlib import Path
from ingestion_pipeline import DataIngestionPipeline
from types import SourceType

async def main():
    pipeline = DataIngestionPipeline()
    
    # Ingest from local folder
    async for doc in pipeline.ingest_from_source(
        SourceType.LOCAL_FOLDER,
        path=Path("./documents")
    ):
        print(f"File: {doc.metadata.file_name}")
        print(f"Chunks: {len(doc.chunks)}")
        print(f"Content: {doc.content[:200]}...")

asyncio.run(main())
```

### Batch Ingestion

```python
async def batch_example():
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
        print(f"Processed: {doc.metadata.file_name}")

asyncio.run(batch_example())
```

## 📋 Configuration

Configure via `.env` file:

```env
# Local
LOCAL_BASE_PATH=./data

# AWS S3
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
AWS_S3_BUCKET=your_bucket

# Google Cloud
GCP_PROJECT_ID=your_project
GCP_CREDENTIALS_PATH=/path/to/creds.json
GCP_BUCKET_NAME=your_bucket

# Azure
AZURE_STORAGE_ACCOUNT_NAME=your_account
AZURE_STORAGE_ACCOUNT_KEY=your_key
AZURE_CONTAINER_NAME=your_container

# OCR
OCR_ENABLED=true
OCR_LANGUAGE=en
OCR_GPU=false

# Processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_WORKERS=4

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

## 🏗️ Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────┐
│           DataIngestionPipeline (Orchestrator)          │
└─────────────────────────────────────────────────────────┘
                            |
        ┌───────────────────┼───────────────────┐
        |                   |                   |
        v                   v                   v
   ┌─────────┐        ┌─────────┐        ┌─────────┐
   │ Sources │        │Extractors│       │Processors│
   ├─────────┤        ├─────────┤        ├─────────┤
   │ Local   │        │ PDF     │        │ Text    │
   │ S3      │        │ DOCX    │        │ Chunking│
   │ GCP     │        │ PPTX    │        │ Prep    │
   │ Azure   │        │ XLSX    │        │         │
   │ Web     │        │ CSV     │        │         │
   │         │        │ JSON    │        │         │
   │         │        │ HTML    │        │         │
   │         │        │ Image   │        │         │
   └─────────┘        └─────────┘        └─────────┘
```

### Processing Pipeline

```
Source Detection
    ↓
Download/Retrieve
    ↓
File Type Detection
    ↓
Content Extraction
    ↓
Text Preprocessing
    ↓
Text Chunking
    ↓
ProcessedDocument (Ready for RAG)
```

## 📊 Data Structures

### DocumentMetadata
Contains information about the source document.

### ExtractedContent
Raw extracted content with structural information.

### ProcessedDocument
Final processed document ready for RAG systems.

## 🐳 Docker Usage

```bash
# Build image
docker build -t rag-ingestion .

# Run container
docker run -v $(pwd)/data:/app/data rag-ingestion python main.py local ./data
```

## 📝 Logging

Logs are structured as JSON for easy parsing:

```json
{
  "timestamp": "2024-01-10T10:30:45.123Z",
  "level": "INFO",
  "logger": "ingestion_pipeline",
  "message": "Extracted PDF from document.pdf",
  "file_type": "pdf",
  "source": "local_folder"
}
```

## 🔧 Advanced Usage

### Custom Processing Callback

```python
async def save_to_database(doc):
    """Save processed document to database."""
    # Custom logic here
    pass

async for doc in pipeline.ingest_from_source(
    SourceType.LOCAL_FOLDER,
    process_callback=save_to_database,
    path=Path("./documents")
):
    pass
```

### Multiple Chunking Strategies

```python
from processors.preprocessor import TextChunker

# By size
chunks = TextChunker.chunk_by_size(text, 1000, 200)

# By sentences
chunks = TextChunker.chunk_by_sentences(text, 5, 1)

# By paragraphs
chunks = TextChunker.chunk_by_paragraphs(text, 1000)
```

## 🧪 Testing

```bash
pytest tests/ -v
```

## 📄 License

MIT License

## 🤝 Contributing

Contributions welcome! Please see CONTRIBUTING.md

## 📧 Support

For issues and questions, please open a GitHub issue.
