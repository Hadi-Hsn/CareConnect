"""Abstract vector store interface."""
from abc import ABC, abstractmethod
from typing import Any

from app.schemas.rag import Document, DocumentChunk


class VectorStore(ABC):
    """Abstract vector store interface."""

    @abstractmethod
    async def upsert(self, documents: list[Document]) -> int:
        """
        Insert or update documents in the vector store.

        Args:
            documents: List of documents to index

        Returns:
            Number of chunks indexed
        """
        pass

    @abstractmethod
    async def similarity_search(
        self, query: str, k: int = 5, filters: dict[str, str] | None = None
    ) -> list[DocumentChunk]:
        """
        Perform similarity search.

        Args:
            query: Search query
            k: Number of results to return
            filters: Optional metadata filters

        Returns:
            List of relevant document chunks with scores
        """
        pass

    @abstractmethod
    async def delete_all(self) -> None:
        """Delete all documents from the store."""
        pass

    @abstractmethod
    async def get_stats(self) -> dict[str, Any]:
        """Get statistics about the vector store."""
        pass

    @abstractmethod
    async def list_documents(self) -> list[dict]:
        """List all indexed documents with metadata."""
        pass

    @abstractmethod
    async def delete_document(self, doc_id: str) -> None:
        """Delete a specific document by ID or metadata."""
        pass
