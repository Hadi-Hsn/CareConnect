"""PDF parsing service for extracting text from PDF documents."""
import io
from pathlib import Path
from typing import BinaryIO

from pypdf import PdfReader

from app.core.logging import get_logger

logger = get_logger(__name__)


class PDFParser:
    """Service for parsing PDF documents."""

    @staticmethod
    def extract_text_from_file(file_path: Path | str) -> str:
        """
        Extract text content from a PDF file.

        Args:
            file_path: Path to the PDF file

        Returns:
            Extracted text content

        Raises:
            FileNotFoundError: If the file doesn't exist
            Exception: If PDF parsing fails
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        try:
            with open(file_path, "rb") as f:
                return PDFParser.extract_text_from_bytes(f)
        except Exception as e:
            logger.error("pdf_extraction_failed", file=str(file_path), error=str(e))
            raise Exception(f"Failed to extract text from PDF: {str(e)}")

    @staticmethod
    def extract_text_from_bytes(file_content: BinaryIO | bytes) -> str:
        """
        Extract text content from PDF bytes.

        Args:
            file_content: Binary content of the PDF file

        Returns:
            Extracted text content

        Raises:
            Exception: If PDF parsing fails
        """
        try:
            # Handle bytes input
            if isinstance(file_content, bytes):
                file_content = io.BytesIO(file_content)

            reader = PdfReader(file_content)
            
            # Extract text from all pages
            text_parts = []
            for page_num, page in enumerate(reader.pages):
                try:
                    text = page.extract_text()
                    if text.strip():
                        text_parts.append(text)
                except Exception as e:
                    logger.warning(
                        "page_extraction_failed",
                        page_num=page_num,
                        error=str(e)
                    )
                    continue

            full_text = "\n\n".join(text_parts)
            
            logger.info(
                "pdf_text_extracted",
                num_pages=len(reader.pages),
                text_length=len(full_text)
            )
            
            return full_text

        except Exception as e:
            logger.error("pdf_extraction_failed", error=str(e))
            raise Exception(f"Failed to extract text from PDF: {str(e)}")

    @staticmethod
    def get_metadata(file_path: Path | str) -> dict:
        """
        Extract metadata from a PDF file.

        Args:
            file_path: Path to the PDF file

        Returns:
            Dictionary containing PDF metadata
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        try:
            with open(file_path, "rb") as f:
                reader = PdfReader(f)
                metadata = reader.metadata or {}
                
                return {
                    "title": metadata.get("/Title", ""),
                    "author": metadata.get("/Author", ""),
                    "subject": metadata.get("/Subject", ""),
                    "creator": metadata.get("/Creator", ""),
                    "producer": metadata.get("/Producer", ""),
                    "num_pages": len(reader.pages),
                }
        except Exception as e:
            logger.error("metadata_extraction_failed", file=str(file_path), error=str(e))
            return {}
