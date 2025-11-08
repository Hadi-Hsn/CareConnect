"""ChromaDB vector store implementation."""
import uuid
from typing import Any

import chromadb
from openai import AsyncOpenAI

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.vectorstore.base import VectorStore
from app.schemas.rag import Document, DocumentChunk

logger = get_logger(__name__)
settings = get_settings()


class ChromaVectorStore(VectorStore):
    """ChromaDB-based vector store implementation."""

    def __init__(self) -> None:
        """Initialize ChromaDB vector store."""
        self.client_openai = AsyncOpenAI(api_key=settings.openai_api_key)
        self.dimension = settings.openai_embedding_dimensions
        
        # Connect to ChromaDB server using simple HttpClient
        # For chromadb 0.4.24, avoid tenant/database params
        try:
            self.client = chromadb.HttpClient(
                host=settings.chroma_host,
                port=settings.chroma_port,
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=settings.chroma_collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            
            logger.info(
                "initialized_chromadb",
                host=settings.chroma_host,
                port=settings.chroma_port,
                collection=settings.chroma_collection_name,
                count=self.collection.count(),
            )
        except Exception as e:
            logger.error("chromadb_initialization_failed", error=str(e), error_type=type(e).__name__)
            # Create a fallback - use in-memory client for development
            logger.warning("using_ephemeral_chromadb_client")
            self.client = chromadb.EphemeralClient()
            self.collection = self.client.get_or_create_collection(
                name=settings.chroma_collection_name,
                metadata={"hnsw:space": "cosine"},
            )

    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
        """
        Split text into overlapping chunks.

        Args:
            text: Text to chunk
            chunk_size: Maximum chunk size in characters
            overlap: Overlap between chunks

        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]

            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind(". ")
                if last_period > chunk_size // 2:
                    chunk = chunk[: last_period + 1]
                    end = start + last_period + 1

            chunks.append(chunk)
            start = end - overlap if end < len(text) else end

        return chunks

    async def _get_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Get embeddings from OpenAI.

        Args:
            texts: List of texts to embed

        Returns:
            List of embeddings
        """
        response = await self.client_openai.embeddings.create(
            model=settings.openai_embedding_model,
            input=texts,
            dimensions=self.dimension,
        )

        embeddings = [item.embedding for item in response.data]
        return embeddings

    async def upsert(self, documents: list[Document]) -> int:
        """Insert or update documents in the vector store."""
        all_chunks: list[str] = []
        all_metadata: list[dict[str, Any]] = []
        all_ids: list[str] = []

        for doc in documents:
            chunks = self._chunk_text(doc.content)
            for i, chunk in enumerate(chunks):
                chunk_id = str(uuid.uuid4())
                all_chunks.append(chunk)
                all_ids.append(chunk_id)
                all_metadata.append(
                    {
                        "chunk_id": chunk_id,
                        "doc_title": doc.title,
                        "doc_type": doc.doc_type,
                        "chunk_index": str(i),  # ChromaDB requires string metadata
                        **{k: str(v) for k, v in doc.metadata.items()},  # Convert all to strings
                    }
                )

        if not all_chunks:
            return 0

        # Get embeddings in batches
        batch_size = 100
        all_embeddings = []
        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i : i + batch_size]
            batch_embeddings = await self._get_embeddings(batch)
            all_embeddings.extend(batch_embeddings)

        # Add to ChromaDB
        self.collection.add(
            embeddings=all_embeddings,
            documents=all_chunks,
            metadatas=all_metadata,
            ids=all_ids,
        )

        logger.info(
            "indexed_documents",
            num_docs=len(documents),
            num_chunks=len(all_chunks),
            total_vectors=self.collection.count(),
        )

        return len(all_chunks)

    async def similarity_search(
        self, query: str, k: int = 5, filters: dict[str, str] | None = None
    ) -> list[DocumentChunk]:
        """Perform similarity search."""
        if self.collection.count() == 0:
            logger.warning("similarity_search_on_empty_collection")
            return []

        # Get query embedding
        query_embedding = await self._get_embeddings([query])

        # Build where clause for filters
        where = None
        if filters:
            where = {key: {"$eq": value} for key, value in filters.items()}

        # Search
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        # Build response
        chunks: list[DocumentChunk] = []
        if results["ids"] and len(results["ids"]) > 0:
            for i in range(len(results["ids"][0])):
                metadata = results["metadatas"][0][i]
                
                # Convert score (distance) to similarity score
                # ChromaDB returns distance, lower is better
                # We convert to similarity where higher is better
                distance = results["distances"][0][i]
                similarity = 1.0 - distance  # Simple conversion

                chunk = DocumentChunk(
                    chunk_id=metadata["chunk_id"],
                    doc_title=metadata["doc_title"],
                    content=results["documents"][0][i],
                    metadata={
                        k: v
                        for k, v in metadata.items()
                        if k not in ["chunk_id", "doc_title", "chunk_index"]
                    },
                    score=float(similarity),
                )
                chunks.append(chunk)

        logger.info(
            "similarity_search_completed",
            query_length=len(query),
            num_results=len(chunks),
        )

        return chunks

    async def delete_all(self) -> None:
        """Delete all documents from the store."""
        # Delete the collection and recreate it
        try:
            self.client.delete_collection(name=settings.chroma_collection_name)
        except Exception as e:
            logger.warning("collection_delete_failed", error=str(e))
        
        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        
        logger.info("deleted_all_documents")

    async def get_stats(self) -> dict[str, Any]:
        """Get statistics about the vector store."""
        count = self.collection.count()
        
        # Get unique documents by counting unique doc_titles
        unique_docs = 0
        if count > 0:
            # Sample metadata to count unique titles
            sample_results = self.collection.get(limit=count, include=["metadatas"])
            if sample_results["metadatas"]:
                unique_titles = set(m["doc_title"] for m in sample_results["metadatas"])
                unique_docs = len(unique_titles)

        return {
            "total_vectors": count,
            "dimension": self.dimension,
            "unique_documents": unique_docs,
            "collection_name": settings.chroma_collection_name,
            "backend": "chromadb",
        }
