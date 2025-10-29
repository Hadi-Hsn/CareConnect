"""RAG endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.logging import get_logger
from app.schemas.rag import IndexRequest, IndexResponse, RetrievalRequest, RetrievalResponse
from app.services.rag_service import RAGService

router = APIRouter()
logger = get_logger(__name__)


@router.post("/index", response_model=IndexResponse, status_code=status.HTTP_201_CREATED)
async def index_documents(
    request: IndexRequest, db: AsyncSession = Depends(get_db)
) -> IndexResponse:
    """
    Index documents into the vector store.

    Admin only endpoint for indexing facility documents, FAQs, etc.
    """
    try:
        rag_service = RAGService()
        response = await rag_service.index_documents(request.documents, replace=request.replace)

        logger.info(
            "documents_indexed",
            count=response.indexed_count,
            chunks=response.total_chunks,
            replace=request.replace,
        )

        return response

    except Exception as e:
        logger.error("indexing_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")


@router.post("/retrieve", response_model=RetrievalResponse)
async def retrieve_documents(
    request: RetrievalRequest, db: AsyncSession = Depends(get_db)
) -> RetrievalResponse:
    """Retrieve relevant document chunks for a query."""
    try:
        rag_service = RAGService()
        response = await rag_service.retrieve(
            request.query, top_k=request.top_k, filters=request.filters
        )

        return response

    except Exception as e:
        logger.error("retrieval_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)) -> dict:
    """Get vector store statistics."""
    try:
        rag_service = RAGService()
        stats = await rag_service.get_stats()
        return stats

    except Exception as e:
        logger.error("stats_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
