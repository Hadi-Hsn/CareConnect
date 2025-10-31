"""Initialize RAG system with PDFs on container startup."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.logging import get_logger
from app.services.rag_service import RAGService

logger = get_logger(__name__)


async def check_and_initialize_rag():
    """Check if RAG is initialized and index PDFs if needed."""
    try:
        rag_service = RAGService()
        
        # Check if vector store has data
        stats = await rag_service.get_stats()
        total_vectors = stats.get('total_vectors', 0)
        
        logger.info("rag_init_check", total_vectors=total_vectors)
        
        if total_vectors > 0:
            logger.info("rag_already_initialized", stats=stats)
            print(f"✓ RAG system already initialized with {total_vectors} vectors")
            return
        
        # No data in vector store, try to index PDFs
        print("RAG system not initialized. Looking for PDFs to index...")
        
        pdf_dir = Path("/data/doctor_pdfs")
        if not pdf_dir.exists() or not list(pdf_dir.glob("*.pdf")):
            logger.warning("no_pdfs_found", path=str(pdf_dir))
            print("No PDFs found. Skipping RAG initialization.")
            return
        
        # Import here to avoid circular dependencies
        from scripts.index_pdfs import index_pdf_directory
        
        print(f"Found PDFs in {pdf_dir}. Starting indexing...")
        await index_pdf_directory(pdf_dir, replace=False)
        
        logger.info("rag_initialization_complete")
        
    except Exception as e:
        logger.error("rag_initialization_failed", error=str(e))
        print(f"Warning: RAG initialization failed: {str(e)}")
        # Don't exit with error - allow the service to start anyway


if __name__ == "__main__":
    asyncio.run(check_and_initialize_rag())
