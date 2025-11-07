"""File upload endpoints for PDFs."""
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.logging import get_logger
from app.core.security import require_admin
from app.schemas.rag import Document, IndexResponse
from app.services.pdf_parser import PDFParser
from app.services.rag_service import RAGService

router = APIRouter()
logger = get_logger(__name__)


@router.post("/upload-pdf", response_model=IndexResponse, status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    file: UploadFile = File(...),
    doc_type: str = "document",
    provider_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin),
) -> IndexResponse:
    """
    Upload and index a PDF document.

    Admin only endpoint for uploading PDF documents to the RAG system.
    """
    # Validate file type
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )

    try:
        # Read file content
        content = await file.read()
        
        # Parse PDF
        pdf_parser = PDFParser()
        text = pdf_parser.extract_text_from_bytes(content)
        
        if not text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PDF appears to be empty or could not be parsed"
            )
        
        # Create document metadata and include provider linkage when provided
        metadata = {
            "source": file.filename,
            "doc_type": doc_type,
            "upload_type": "api",
        }
        if provider_id is not None:
            metadata["provider_id"] = str(provider_id)

        # Create document
        document = Document(
            title=file.filename.replace('.pdf', '').replace('_', ' ').replace('.PDF', '').title(),
            content=text,
            metadata=metadata,
            doc_type="pdf",
        )
        
        # Index document
        rag_service = RAGService()
        response = await rag_service.index_documents([document], replace=False)
        
        logger.info(
            "pdf_uploaded_and_indexed",
            filename=file.filename,
            doc_type=doc_type,
            text_length=len(text),
            chunks=response.total_chunks
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("pdf_upload_failed", filename=file.filename, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process PDF: {str(e)}"
        )
