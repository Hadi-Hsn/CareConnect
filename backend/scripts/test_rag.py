"""Test script for RAG system."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.logging import get_logger
from app.services.rag_service import RAGService

logger = get_logger(__name__)


async def test_rag_system():
    """Test the RAG system with sample queries."""
    print("=" * 60)
    print("RAG System Test")
    print("=" * 60)
    print()

    try:
        rag_service = RAGService()

        # Get stats
        print("1. Checking RAG system status...")
        stats = await rag_service.get_stats()
        print(f"   ✓ Total vectors: {stats.get('total_vectors', 0)}")
        print(f"   ✓ Unique documents: {stats.get('unique_documents', 0)}")
        print(f"   ✓ Dimension: {stats.get('dimension', 0)}")
        print()

        if stats.get('total_vectors', 0) == 0:
            print("   ⚠ Warning: No documents indexed yet!")
            print("   Run: python scripts/index_pdfs.py")
            return

        # Test queries
        test_queries = [
            ("cardiologist with heart failure experience", 3),
            ("pediatrician who speaks Spanish", 3),
            ("orthopedic surgeon for sports injuries", 3),
            ("dermatologist for skin cancer screening", 2),
        ]

        print("2. Testing semantic search...")
        print("-" * 60)

        for i, (query, top_k) in enumerate(test_queries, 1):
            print(f"\n   Query {i}: '{query}'")
            print(f"   Retrieving top {top_k} results...")

            response = await rag_service.retrieve(query, top_k=top_k)

            print(f"   ✓ Found {len(response.chunks)} results in {response.retrieval_time_ms:.1f}ms")

            for j, chunk in enumerate(response.chunks, 1):
                print(f"\n   Result {j}:")
                print(f"     - Title: {chunk.doc_title}")
                print(f"     - Score: {chunk.score:.4f}")
                print(f"     - Preview: {chunk.content[:150]}...")

        print()
        print("=" * 60)
        print("✓ All tests completed successfully!")
        print("=" * 60)

    except Exception as e:
        logger.error("test_failed", error=str(e))
        print(f"\n✗ Test failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_rag_system())
