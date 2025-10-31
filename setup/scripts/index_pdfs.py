"""Script to index PDF documents into the RAG vector store."""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent.parent / "backend"))

from app.core.logging import get_logger
from app.schemas.rag import Document
from app.services.pdf_parser import PDFParser
from app.services.rag_service import RAGService

logger = get_logger(__name__)


async def index_pdf_directory(pdf_dir: Path, replace: bool = False) -> None:
    """
    Index all PDF files from a directory into the RAG system.

    Args:
        pdf_dir: Directory containing PDF files
        replace: Whether to replace existing index
    """
    if not pdf_dir.exists():
        logger.error("pdf_directory_not_found", path=str(pdf_dir))
        raise FileNotFoundError(f"PDF directory not found: {pdf_dir}")

    # Find all PDF files
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning("no_pdf_files_found", path=str(pdf_dir))
        print(f"   No PDF files found in {pdf_dir}")
        return

    print(f"   Found {len(pdf_files)} PDF files")
    print()

    # Parse PDFs and create documents
    documents = []
    pdf_parser = PDFParser()

    for pdf_file in pdf_files:
        try:
            # Extract text
            text = pdf_parser.extract_text_from_file(pdf_file)
            
            # Extract metadata
            metadata = pdf_parser.get_metadata(pdf_file)
            
            # Determine document type based on directory/filename
            doc_type = "doctor_profile" if "doctor" in str(pdf_file).lower() else "document"
            
            # Extract doctor name from filename (e.g., "sarah_johnson.pdf" -> "Sarah Johnson")
            doctor_name = pdf_file.stem.replace("_", " ").title()
            
            # Create document
            document = Document(
                title=f"Dr. {doctor_name}" if doc_type == "doctor_profile" else pdf_file.stem,
                content=text,
                metadata={
                    "source": pdf_file.name,
                    "doc_type": doc_type,
                    "file_path": str(pdf_file),
                    "num_pages": str(metadata.get("num_pages", 0)),
                },
                doc_type="pdf"
            )
            
            documents.append(document)
            print(f"   ✓ Parsed: {pdf_file.name} ({len(text)} chars, {metadata.get('num_pages', 0)} pages)")
            
        except Exception as e:
            logger.error("pdf_processing_failed", file=str(pdf_file), error=str(e))
            print(f"   ✗ Error processing {pdf_file.name}: {str(e)}")
            continue

    if not documents:
        print("   No documents to index!")
        return

    print()
    print(f"   Indexing {len(documents)} documents...")

    # Index documents
    try:
        rag_service = RAGService()
        response = await rag_service.index_documents(documents, replace=replace)
        
        print(f"   ✓ Documents indexed: {response.indexed_count}")
        print(f"   ✓ Total chunks: {response.total_chunks}")
        
        # Get stats
        stats = await rag_service.get_stats()
        print()
        print(f"   Vector Store: {stats.get('total_vectors', 0)} vectors, {stats.get('unique_documents', 0)} documents")
        
    except Exception as e:
        logger.error("indexing_failed", error=str(e))
        print(f"   ✗ Indexing failed: {str(e)}")
        raise


async def main():
    """Main function."""
    # PDF directory - shared volume with backend
    pdf_dir = Path("/app/data/doctor_pdfs")
    
    print("🔍 Indexing PDF documents...")
    print(f"   Source: {pdf_dir}")
    print()
    
    try:
        await index_pdf_directory(pdf_dir, replace=False)
        print()
        print("✅ PDF indexing completed!")
    except Exception as e:
        print(f"\n✗ Failed to index PDFs: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
