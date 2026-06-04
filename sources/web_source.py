"""
Web-based data sources (URLs, web scraping).
"""

import asyncio
from pathlib import Path
from typing import AsyncIterator, Optional, List
from urllib.parse import urljoin, urlparse
import aiohttp
from bs4 import BeautifulSoup
from types import SourceType, DocumentMetadata, ProcessingStage
from datetime import datetime
from sources.base_source import BaseDataSource, SourceError
from config import config
from utils.logger import get_logger

logger = get_logger(__name__)


class WebURLSource(BaseDataSource):
    """Web URL data source."""
    
    def __init__(self, base_urls: List[str], recursive: bool = False, depth: int = 1):
        """
        Initialize web URL source.
        
        Args:
            base_urls: Starting URLs to scrape
            recursive: Whether to follow links recursively
            depth: Maximum depth to crawl
        """
        self.base_urls = base_urls
        self.recursive = recursive
        self.depth = depth
        self.visited_urls = set()
    
    async def list_sources(self) -> AsyncIterator[str]:
        """List all URLs to process."""
        async with aiohttp.ClientSession() as session:
            queue = [(url, 0) for url in self.base_urls]
            
            while queue:
                url, current_depth = queue.pop(0)
                
                if url in self.visited_urls:
                    continue
                
                self.visited_urls.add(url)
                yield url
                
                if self.recursive and current_depth < self.depth:
                    try:
                        links = await self._extract_links(session, url)
                        for link in links:
                            if link not in self.visited_urls:
                                queue.append((link, current_depth + 1))
                    except Exception as e:
                        logger.warning(f"Failed to extract links from {url}: {str(e)}")
    
    async def _extract_links(self, session: aiohttp.ClientSession, url: str) -> List[str]:
        """Extract links from a webpage."""
        try:
            async with session.get(url, timeout=config.REQUEST_TIMEOUT) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    
                    links = []
                    base_domain = urlparse(url).netloc
                    
                    for link in soup.find_all("a", href=True):
                        abs_url = urljoin(url, link["href"])
                        # Only follow same domain links
                        if urlparse(abs_url).netloc == base_domain:
                            links.append(abs_url)
                    
                    return links
        except Exception as e:
            logger.warning(f"Failed to fetch {url}: {str(e)}")
        
        return []
    
    async def download(self, source: str, destination: Path) -> Path:
        """Download web content as HTML."""
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(source, timeout=config.REQUEST_TIMEOUT) as response:
                    if response.status == 200:
                        html = await response.text()
                        
                        with open(destination, "w", encoding="utf-8") as f:
                            f.write(html)
                        
                        logger.info(f"Downloaded web URL: {source}")
                        return destination
                    else:
                        raise SourceError(f"HTTP {response.status}")
        except Exception as e:
            logger.error(f"Failed to download web URL: {str(e)}")
            raise SourceError(f"Failed to download web URL: {str(e)}")
    
    def get_metadata(self, source: str) -> DocumentMetadata:
        """Get metadata for web URL."""
        return DocumentMetadata(
            source=source,
            source_type=SourceType.WEB_URL,
            file_type=None,  # Will be determined later
            file_name=urlparse(source).path.split("/")[-1] or "webpage.html",
            file_path=None,
            file_size=None,
            created_at=datetime.now(),
            stage=ProcessingStage.DETECTED,
            custom_metadata={"url": source}
        )
