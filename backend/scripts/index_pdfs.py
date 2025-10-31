"""Script to index PDF documents into the RAG vector store."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

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
        print(f"No PDF files found in {pdf_dir}")
        return

    print(f"Found {len(pdf_files)} PDF files to index")
    print("-" * 50)

    # Parse PDFs and create documents
    documents = []
    pdf_parser = PDFParser()

    for pdf_file in pdf_files:
        try:
            print(f"Processing: {pdf_file.name}...")
            
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
            print(f"  ✓ Extracted {len(text)} characters from {metadata.get('num_pages', 0)} pages")
            
        except Exception as e:
            logger.error("pdf_processing_failed", file=str(pdf_file), error=str(e))
            print(f"  ✗ Error processing {pdf_file.name}: {str(e)}")
            continue

    if not documents:
        print("No documents to index!")
        return

    print("-" * 50)
    print(f"Indexing {len(documents)} documents into RAG system...")

    # Index documents
    try:
        rag_service = RAGService()
        response = await rag_service.index_documents(documents, replace=replace)
        
        print("-" * 50)
        print("✓ Indexing completed successfully!")
        print(f"  - Documents indexed: {response.indexed_count}")
        print(f"  - Total chunks created: {response.total_chunks}")
        print(f"  - Message: {response.message}")
        
        # Get stats
        stats = await rag_service.get_stats()
        print("\nVector Store Statistics:")
        print(f"  - Total vectors: {stats.get('total_vectors', 0)}")
        print(f"  - Unique documents: {stats.get('unique_documents', 0)}")
        print(f"  - Dimension: {stats.get('dimension', 0)}")
        
    except Exception as e:
        logger.error("indexing_failed", error=str(e))
        print(f"✗ Indexing failed: {str(e)}")
        raise


async def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Index PDF documents into RAG system")
    parser.add_argument(
        "--pdf-dir",
        type=str,
        default="data/doctor_pdfs",
        help="Directory containing PDF files (default: data/doctor_pdfs)"
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Replace existing index"
    )
    
    args = parser.parse_args()
    
    # Resolve PDF directory path
    pdf_dir = Path(args.pdf_dir)
    if not pdf_dir.is_absolute():
        pdf_dir = Path(__file__).parent.parent / pdf_dir
    
    print("=" * 50)
    print("PDF Document Indexing")
    print("=" * 50)
    print(f"PDF Directory: {pdf_dir}")
    print(f"Replace existing: {args.replace}")
    print("=" * 50)
    print()
    
    try:
        await index_pdf_directory(pdf_dir, replace=args.replace)
    except Exception as e:
        print(f"\n✗ Failed to index PDFs: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
