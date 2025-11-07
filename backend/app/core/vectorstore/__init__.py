"""Vector store factory."""
from app.core.config import get_settings
from app.core.vectorstore.base import VectorStore
from app.core.vectorstore.chroma_store import ChromaVectorStore

settings = get_settings()


def get_vector_store() -> VectorStore:
    """Get vector store instance based on configuration."""
    if settings.vector_store_type == "chromadb":
        return ChromaVectorStore()
    elif settings.vector_store_type == "faiss":
        try:
            from app.core.vectorstore.faiss_store import FAISSVectorStore
            return FAISSVectorStore()
        except ImportError:
            raise ImportError(
                "FAISS is not installed. Install with: pip install faiss-cpu"
            )
    elif settings.vector_store_type == "pgvector":
        # Placeholder for future implementation
        raise NotImplementedError("pgvector not yet implemented")
    elif settings.vector_store_type == "weaviate":
        # Placeholder for future implementation
        raise NotImplementedError("Weaviate not yet implemented")
    else:
        raise ValueError(f"Unknown vector store type: {settings.vector_store_type}")
