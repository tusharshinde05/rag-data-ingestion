"""
Text preprocessing for extracted content.
"""

import re
from typing import List
from utils.logger import get_logger

logger = get_logger(__name__)


class TextPreprocessor:
    """Handles text preprocessing and cleaning."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]", "", text)
        
        # Fix common encoding issues
        text = text.encode("utf-8", "ignore").decode("utf-8")
        
        return text.strip()
    
    @staticmethod
    def remove_duplicates(text: str) -> str:
        """Remove duplicate lines."""
        lines = text.split("\n")
        unique_lines = []
        seen = set()
        
        for line in lines:
            if line.strip() not in seen:
                seen.add(line.strip())
                unique_lines.append(line)
        
        return "\n".join(unique_lines)
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalize whitespace in text."""
        # Replace multiple spaces with single space
        text = re.sub(r" +", " ", text)
        
        # Replace multiple newlines with double newline
        text = re.sub(r"\n{3,}", "\n\n", text)
        
        return text
    
    @staticmethod
    def remove_urls(text: str) -> str:
        """Remove URLs from text."""
        url_pattern = r"https?://[^\s]+"
        return re.sub(url_pattern, "[URL]", text)
    
    @staticmethod
    def remove_emails(text: str) -> str:
        """Remove email addresses from text."""
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        return re.sub(email_pattern, "[EMAIL]", text)
    
    @staticmethod
    def preprocess(text: str, remove_urls: bool = False, remove_emails: bool = False) -> str:
        """
        Apply full preprocessing pipeline.
        
        Args:
            text: Raw text
            remove_urls: Whether to remove URLs
            remove_emails: Whether to remove emails
            
        Returns:
            Preprocessed text
        """
        text = TextPreprocessor.clean_text(text)
        text = TextPreprocessor.normalize_whitespace(text)
        text = TextPreprocessor.remove_duplicates(text)
        
        if remove_urls:
            text = TextPreprocessor.remove_urls(text)
        
        if remove_emails:
            text = TextPreprocessor.remove_emails(text)
        
        return text


class TextChunker:
    """Handles text chunking for RAG systems."""
    
    @staticmethod
    def chunk_by_size(text: str, chunk_size: int, overlap: int) -> List[str]:
        """
        Chunk text by character size with overlap.
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk
            overlap: Number of overlapping characters
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            start = end - overlap if overlap > 0 else end
        
        return [chunk for chunk in chunks if len(chunk.strip()) > 0]
    
    @staticmethod
    def chunk_by_sentences(text: str, sentences_per_chunk: int = 5, overlap: int = 1) -> List[str]:
        """
        Chunk text by sentences.
        
        Args:
            text: Text to chunk
            sentences_per_chunk: Number of sentences per chunk
            overlap: Number of overlapping sentences
            
        Returns:
            List of text chunks
        """
        # Simple sentence splitting (can be improved with nltk)
        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        for i in range(0, len(sentences), sentences_per_chunk - overlap):
            chunk = " ".join(sentences[i:i + sentences_per_chunk])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks
    
    @staticmethod
    def chunk_by_paragraphs(text: str, max_chunk_size: int = 1000) -> List[str]:
        """
        Chunk text by paragraphs with maximum size fallback.
        
        Args:
            text: Text to chunk
            max_chunk_size: Maximum chunk size
            
        Returns:
            List of text chunks
        """
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) < max_chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return [chunk for chunk in chunks if len(chunk.strip()) > 0]
