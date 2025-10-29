"""RAG and document schemas."""
from datetime import datetime

from pydantic import BaseModel, Field


class Document(BaseModel):
    """Document schema."""

    title: str = Field(..., min_length=1)
    content: str
    metadata: dict[str, str] = {}
    doc_type: str = "text"  # text, markdown, pdf


class DocumentChunk(BaseModel):
    """Document chunk with embedding."""

    chunk_id: str
    doc_title: str
    content: str
    metadata: dict[str, str]
    score: float | None = None


class IndexRequest(BaseModel):
    """Index documents request."""

    documents: list[Document]
    replace: bool = False  # Replace existing index


class IndexResponse(BaseModel):
    """Index response."""

    indexed_count: int
    total_chunks: int
    message: str


class RetrievalRequest(BaseModel):
    """Retrieval request."""

    query: str
    top_k: int = Field(5, ge=1, le=20)
    filters: dict[str, str] = {}


class RetrievalResponse(BaseModel):
    """Retrieval response."""

    query: str
    chunks: list[DocumentChunk]
    retrieval_time_ms: float
