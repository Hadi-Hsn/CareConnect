"""FAISS vector store implementation."""
import json
import os
import pickle
import uuid
from pathlib import Path
from typing import Any

import faiss
import numpy as np
from openai import AsyncOpenAI

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.vectorstore.base import VectorStore
from app.schemas.rag import Document, DocumentChunk

logger = get_logger(__name__)
settings = get_settings()


class FAISSVectorStore(VectorStore):
    """FAISS-based vector store implementation."""

    def __init__(self) -> None:
        """Initialize FAISS vector store."""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.dimension = settings.openai_embedding_dimensions
        self.index_path = Path(settings.vector_store_path)
        self.index_path.mkdir(parents=True, exist_ok=True)

        self.index: faiss.Index | None = None
        self.metadata: list[dict[str, Any]] = []

        # Load existing index if available
        self._load_index()

    def _load_index(self) -> None:
        """Load existing FAISS index from disk."""
        index_file = self.index_path / "faiss.index"
        metadata_file = self.index_path / "metadata.pkl"

        if index_file.exists() and metadata_file.exists():
            try:
                self.index = faiss.read_index(str(index_file))
                with open(metadata_file, "rb") as f:
                    self.metadata = pickle.load(f)
                logger.info(
                    "loaded_faiss_index",
                    num_vectors=self.index.ntotal,
                    dimension=self.dimension,
                )
            except Exception as e:
                logger.error("failed_to_load_index", error=str(e))
                self._create_new_index()
        else:
            self._create_new_index()

    def _create_new_index(self) -> None:
        """Create a new FAISS index."""
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
        self.metadata = []
        logger.info("created_new_faiss_index", dimension=self.dimension)

    def _save_index(self) -> None:
        """Save FAISS index to disk."""
        if self.index is None:
            return

        index_file = self.index_path / "faiss.index"
        metadata_file = self.index_path / "metadata.pkl"

        try:
            faiss.write_index(self.index, str(index_file))
            with open(metadata_file, "wb") as f:
                pickle.dump(self.metadata, f)
            logger.info("saved_faiss_index", path=str(self.index_path))
        except Exception as e:
            logger.error("failed_to_save_index", error=str(e))

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

    async def _get_embeddings(self, texts: list[str]) -> np.ndarray:
        """
        Get embeddings from OpenAI.

        Args:
            texts: List of texts to embed

        Returns:
            Numpy array of embeddings
        """
        response = await self.client.embeddings.create(
            model=settings.openai_embedding_model,
            input=texts,
            dimensions=self.dimension,
        )

        embeddings = [item.embedding for item in response.data]
        embeddings_array = np.array(embeddings, dtype=np.float32)

        # Normalize for cosine similarity (required for IndexFlatIP)
        faiss.normalize_L2(embeddings_array)

        return embeddings_array

    async def upsert(self, documents: list[Document]) -> int:
        """Insert or update documents in the vector store."""
        if self.index is None:
            self._create_new_index()

        all_chunks: list[str] = []
        all_metadata: list[dict[str, Any]] = []

        for doc in documents:
            chunks = self._chunk_text(doc.content)
            for i, chunk in enumerate(chunks):
                chunk_id = str(uuid.uuid4())
                all_chunks.append(chunk)
                all_metadata.append(
                    {
                        "chunk_id": chunk_id,
                        "doc_title": doc.title,
                        "doc_type": doc.doc_type,
                        "chunk_index": i,
                        "content": chunk,
                        **doc.metadata,
                    }
                )

        if not all_chunks:
            return 0

        # Get embeddings in batches
        batch_size = 100
        embeddings_list = []
        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i : i + batch_size]
            batch_embeddings = await self._get_embeddings(batch)
            embeddings_list.append(batch_embeddings)

        embeddings = np.vstack(embeddings_list)

        # Add to index
        self.index.add(embeddings)
        self.metadata.extend(all_metadata)

        # Save to disk
        self._save_index()

        logger.info(
            "indexed_documents",
            num_docs=len(documents),
            num_chunks=len(all_chunks),
            total_vectors=self.index.ntotal,
        )

        return len(all_chunks)

    async def similarity_search(
        self, query: str, k: int = 5, filters: dict[str, str] | None = None
    ) -> list[DocumentChunk]:
        """Perform similarity search."""
        if self.index is None or self.index.ntotal == 0:
            logger.warning("similarity_search_on_empty_index")
            return []

        # Get query embedding
        query_embedding = await self._get_embeddings([query])

        # Search
        distances, indices = self.index.search(query_embedding, k)

        # Build results
        results: list[DocumentChunk] = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:  # FAISS returns -1 for missing results
                continue

            metadata = self.metadata[idx]

            # Apply filters if provided
            if filters:
                if not all(metadata.get(key) == value for key, value in filters.items()):
                    continue

            chunk = DocumentChunk(
                chunk_id=metadata["chunk_id"],
                doc_title=metadata["doc_title"],
                content=metadata["content"],
                metadata={
                    k: v
                    for k, v in metadata.items()
                    if k not in ["chunk_id", "doc_title", "content", "chunk_index"]
                },
                score=float(dist),
            )
            results.append(chunk)

        logger.info("similarity_search_completed", query_length=len(query), num_results=len(results))

        return results

    async def delete_all(self) -> None:
        """Delete all documents from the store."""
        self._create_new_index()
        self._save_index()
        logger.info("deleted_all_documents")

    async def get_stats(self) -> dict[str, Any]:
        """Get statistics about the vector store."""
        if self.index is None:
            return {"total_vectors": 0, "dimension": self.dimension}

        unique_docs = len(set(m["doc_title"] for m in self.metadata))

        return {
            "total_vectors": self.index.ntotal,
            "dimension": self.dimension,
            "unique_documents": unique_docs,
            "index_path": str(self.index_path),
        }

    async def list_documents(self) -> list[dict]:
        """List all indexed documents with metadata."""
        if not self.metadata:
            return []

        # Group chunks by document
        docs_map: dict[str, dict] = {}
        
        for meta in self.metadata:
            doc_title = meta.get("doc_title", "Unknown")
            
            if doc_title not in docs_map:
                docs_map[doc_title] = {
                    "id": doc_title,
                    "title": doc_title,
                    "chunks": 0,
                    "metadata": {
                        k: v for k, v in meta.items() 
                        if k not in ["chunk_id", "chunk_index", "content", "doc_title"]
                    }
                }
            
            docs_map[doc_title]["chunks"] += 1

        return list(docs_map.values())

    async def delete_document(self, doc_id: str) -> None:
        """Delete a specific document by ID (doc_title)."""
        if self.index is None or not self.metadata:
            return

        # Find indices to keep (not matching doc_id)
        indices_to_keep = []
        metadata_to_keep = []
        
        for idx, meta in enumerate(self.metadata):
            if meta.get("doc_title") != doc_id:
                indices_to_keep.append(idx)
                metadata_to_keep.append(meta)

        if len(indices_to_keep) == len(self.metadata):
            # No documents matched, nothing to delete
            logger.warning("document_not_found", doc_id=doc_id)
            return

        # Reconstruct index with remaining vectors
        if len(indices_to_keep) == 0:
            # All vectors deleted
            self._create_new_index()
        else:
            # Extract remaining vectors
            remaining_vectors = []
            for idx in indices_to_keep:
                vector = self.index.reconstruct(idx)
                remaining_vectors.append(vector)
            
            # Create new index and add remaining vectors
            self._create_new_index()
            vectors_array = np.array(remaining_vectors, dtype=np.float32)
            self.index.add(vectors_array)

        # Update metadata
        self.metadata = metadata_to_keep
        
        # Save changes
        self._save_index()
        
        logger.info("document_deleted", doc_id=doc_id, remaining_docs=len(set(m["doc_title"] for m in self.metadata)))
