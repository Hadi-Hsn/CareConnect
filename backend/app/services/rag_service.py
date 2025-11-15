"""RAG service for retrieval-augmented generation."""
import time
from typing import Any

from app.core.logging import get_logger
from app.core.vectorstore import get_vector_store
from app.core.vectorstore.base import VectorStore
from app.schemas.rag import Document, DocumentChunk, IndexResponse, RetrievalResponse

logger = get_logger(__name__)


class RAGService:
    """RAG service for document indexing and retrieval."""

    def __init__(self) -> None:
        """Initialize RAG service."""
        self.vector_store: VectorStore = get_vector_store()

    async def index_documents(
        self, documents: list[Document], replace: bool = False
    ) -> IndexResponse:
        """
        Index documents into the vector store.

        Args:
            documents: List of documents to index
            replace: If True, replace existing index

        Returns:
            Index response with statistics
        """
        if replace:
            await self.vector_store.delete_all()
            logger.info("cleared_vector_store")

        total_chunks = await self.vector_store.upsert(documents)

        return IndexResponse(
            indexed_count=len(documents),
            total_chunks=total_chunks,
            message=f"Successfully indexed {len(documents)} documents ({total_chunks} chunks)",
        )

    async def retrieve(
        self, query: str, top_k: int = 5, filters: dict[str, str] | None = None
    ) -> RetrievalResponse:
        """
        Retrieve relevant document chunks for a query.

        Args:
            query: Search query
            top_k: Number of results to return
            filters: Optional metadata filters

        Returns:
            Retrieval response with chunks and timing
        """
        start_time = time.perf_counter()

        chunks = await self.vector_store.similarity_search(query, k=top_k, filters=filters)

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            "retrieval_completed",
            query_length=len(query),
            num_results=len(chunks),
            latency_ms=elapsed_ms,
        )

        return RetrievalResponse(
            query=query,
            chunks=chunks,
            retrieval_time_ms=elapsed_ms,
        )

    async def get_stats(self) -> dict[str, Any]:
        """Get vector store statistics."""
        return await self.vector_store.get_stats()

    async def list_documents(self) -> list[dict]:
        """
        List all indexed documents.
        
        Returns:
            List of documents with their metadata
        """
        return await self.vector_store.list_documents()

    async def delete_document(self, doc_id: str) -> None:
        """
        Delete a specific document from the vector store.
        
        Args:
            doc_id: The document ID or metadata to identify the document
        """
        await self.vector_store.delete_document(doc_id)
