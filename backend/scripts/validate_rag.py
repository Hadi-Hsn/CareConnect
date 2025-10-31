"""Startup validation script to check RAG system configuration."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def validate_environment():
    """Validate required environment variables."""
    print("🔍 Validating environment configuration...")
    
    settings = get_settings()
    issues = []
    
    # Check OpenAI API key
    if not settings.openai_api_key or settings.openai_api_key == "":
        issues.append("❌ OPENAI_API_KEY is not set")
    else:
        print(f"   ✓ OPENAI_API_KEY: {'*' * 20}{settings.openai_api_key[-4:]}")
    
    # Check embedding configuration
    print(f"   ✓ Embedding model: {settings.openai_embedding_model}")
    print(f"   ✓ Embedding dimensions: {settings.openai_embedding_dimensions}")
    
    # Check vector store path
    vector_store_path = Path(settings.vector_store_path)
    if not vector_store_path.exists():
        print(f"   ℹ Vector store path doesn't exist yet: {vector_store_path}")
        print(f"     (Will be created automatically)")
    else:
        print(f"   ✓ Vector store path: {vector_store_path}")
    
    return issues


def validate_directories():
    """Validate required directories exist."""
    print("\n🔍 Validating directories...")
    
    directories = [
        Path("/data/faiss_index"),
        Path("/data/doctor_pdfs"),
    ]
    
    issues = []
    for directory in directories:
        if not directory.exists():
            issues.append(f"❌ Directory missing: {directory}")
        else:
            file_count = len(list(directory.glob("*")))
            print(f"   ✓ {directory} ({file_count} files)")
    
    return issues


async def validate_rag_system():
    """Validate RAG system is operational."""
    print("\n🔍 Validating RAG system...")
    
    try:
        from app.services.rag_service import RAGService
        
        rag_service = RAGService()
        stats = await rag_service.get_stats()
        
        print(f"   ✓ Vector store initialized")
        print(f"   ✓ Total vectors: {stats.get('total_vectors', 0)}")
        print(f"   ✓ Unique documents: {stats.get('unique_documents', 0)}")
        print(f"   ✓ Dimension: {stats.get('dimension', 0)}")
        
        if stats.get('total_vectors', 0) == 0:
            return ["⚠ Warning: No documents indexed yet"]
        
        return []
        
    except Exception as e:
        return [f"❌ RAG system error: {str(e)}"]


def validate_pdf_files():
    """Validate PDF files exist."""
    print("\n🔍 Validating PDF files...")
    
    pdf_dir = Path("/data/doctor_pdfs")
    
    if not pdf_dir.exists():
        return ["⚠ PDF directory doesn't exist yet"]
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        return ["⚠ No PDF files found"]
    
    print(f"   ✓ Found {len(pdf_files)} PDF files:")
    for pdf_file in pdf_files:
        size_kb = pdf_file.stat().st_size / 1024
        print(f"     - {pdf_file.name} ({size_kb:.1f} KB)")
    
    return []


async def main():
    """Run all validation checks."""
    print("=" * 60)
    print("CareConnect RAG System - Startup Validation")
    print("=" * 60)
    print()
    
    all_issues = []
    warnings = []
    
    # Run checks
    all_issues.extend(validate_environment())
    all_issues.extend(validate_directories())
    all_issues.extend(validate_pdf_files())
    rag_issues = await validate_rag_system()
    
    # Separate errors and warnings
    for issue in rag_issues:
        if issue.startswith("⚠"):
            warnings.append(issue)
        else:
            all_issues.append(issue)
    
    print()
    print("=" * 60)
    
    if all_issues:
        print("❌ Validation failed with errors:")
        for issue in all_issues:
            print(f"   {issue}")
        print()
        print("Please fix these issues and restart the service.")
        print("=" * 60)
        return False
    
    if warnings:
        print("⚠ Validation completed with warnings:")
        for warning in warnings:
            print(f"   {warning}")
        print()
        print("The system will start, but some features may not work.")
        print("=" * 60)
        return True
    
    print("✅ All validation checks passed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
