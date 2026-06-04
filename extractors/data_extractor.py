"""
Extractors for data formats (CSV, JSON, HTML).
"""

import json
from pathlib import Path
from typing import Dict, Any
from bs4 import BeautifulSoup
import pandas as pd
from types import ExtractedContent, DocumentMetadata
from extractors.base_extractor import BaseExtractor, ExtractionError
from utils.logger import get_logger

logger = get_logger(__name__)


class CSVExtractor(BaseExtractor):
    """Extractor for CSV files."""
    
    def can_extract(self, file_path: Path) -> bool:
        """Check if file is CSV."""
        return file_path.suffix.lower() == ".csv"
    
    async def extract(self, file_path: Path, metadata: DocumentMetadata) -> ExtractedContent:
        """Extract content from CSV file."""
        try:
            df = pd.read_csv(file_path)
            
            # Convert to readable text format
            text_content = []
            text_content.append(f"CSV File: {file_path.name}\n")
            text_content.append("Columns: " + ", ".join(df.columns))
            text_content.append(f"Rows: {len(df)}\n")
            text_content.append(df.to_string())
            
            text = "\n".join(text_content)
            
            logger.info(f"Extracted CSV from {file_path.name}", extra={
                "rows": len(df),
                "columns": len(df.columns)
            })
            
            return ExtractedContent(
                metadata=metadata,
                raw_text=text,
                structured_data={"shape": (len(df), len(df.columns))},
                has_tables=True
            )
            
        except Exception as e:
            logger.error(f"Failed to extract CSV {file_path}: {str(e)}")
            raise ExtractionError(f"CSV extraction failed: {str(e)}")


class JSONExtractor(BaseExtractor):
    """Extractor for JSON files."""
    
    def can_extract(self, file_path: Path) -> bool:
        """Check if file is JSON."""
        return file_path.suffix.lower() == ".json"
    
    async def extract(self, file_path: Path, metadata: DocumentMetadata) -> ExtractedContent:
        """Extract content from JSON file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Convert to readable text
            text = json.dumps(data, indent=2)
            
            logger.info(f"Extracted JSON from {file_path.name}")
            
            return ExtractedContent(
                metadata=metadata,
                raw_text=text,
                structured_data=data if isinstance(data, dict) else {"data": data}
            )
            
        except Exception as e:
            logger.error(f"Failed to extract JSON {file_path}: {str(e)}")
            raise ExtractionError(f"JSON extraction failed: {str(e)}")


class HTMLExtractor(BaseExtractor):
    """Extractor for HTML files."""
    
    def can_extract(self, file_path: Path) -> bool:
        """Check if file is HTML."""
        return file_path.suffix.lower() in [".html", ".htm"]
    
    async def extract(self, file_path: Path, metadata: DocumentMetadata) -> ExtractedContent:
        """Extract content from HTML file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text(separator="\n", strip=True)
            
            logger.info(f"Extracted HTML from {file_path.name}")
            
            return ExtractedContent(
                metadata=metadata,
                raw_text=text
            )
            
        except Exception as e:
            logger.error(f"Failed to extract HTML {file_path}: {str(e)}")
            raise ExtractionError(f"HTML extraction failed: {str(e)}")
