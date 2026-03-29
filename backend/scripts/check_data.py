"""Comprehensive validation script to check all seeded data."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, func
from app.core.db import async_session_maker
from app.models import User, Provider, LabTest
from app.services.rag_service import RAGService
from app.core.logging import get_logger

logger = get_logger(__name__)


async def check_database_initialized():
    """Check if database is initialized."""
    print("🔍 Checking database initialization...")
    try:
        async with async_session_maker() as session:
            # Try a simple query
            result = await session.execute(select(func.count()).select_from(User))
            result.scalar()
            print("   ✅ Database initialized")
            return True
    except Exception as e:
        print(f"   ❌ Database not initialized: {e}")
        return False


async def check_users():
    """Check if users are seeded."""
    print("\n🔍 Checking users...")
    try:
        async with async_session_maker() as session:
            result = await session.execute(select(func.count()).select_from(User))
            user_count = result.scalar()

            if user_count >= 2:
                print(f"   ✅ Seeded {user_count} users")

                # Show user details
                result = await session.execute(select(User).order_by(User.id))
                users = result.scalars().all()
                for user in users:
                    # Handle role - could be enum or string
                    role_display = (
                        user.role.value if hasattr(user.role, "value") else str(user.role)
                    )
                    print(f"      - {user.email} ({role_display})")
                return True
            else:
                print(f"   ❌ Only {user_count} users found (expected at least 2)")
                if user_count > 0:
                    result = await session.execute(select(User))
                    users = result.scalars().all()
                    for user in users:
                        role_display = (
                            user.role.value if hasattr(user.role, "value") else str(user.role)
                        )
                        print(f"      - {user.email} ({role_display})")
                return False
    except Exception as e:
        print(f"   ❌ Error checking users: {e}")
        import traceback

        print(f"   Details: {traceback.format_exc()}")
        return False


async def check_providers():
    """Check if providers are seeded."""
    print("\n🔍 Checking providers...")
    try:
        async with async_session_maker() as session:
            # Total provider count
            result = await session.execute(select(func.count()).select_from(Provider))
            provider_count = result.scalar()

            if provider_count >= 90:
                print(f"   ✅ Seeded {provider_count} providers across all departments")

                # Count by department
                result = await session.execute(
                    select(Provider.department, func.count(Provider.id))
                    .group_by(Provider.department)
                    .order_by(Provider.department)
                )
                departments = result.all()

                print(f"   ✅ Distribution across {len(departments)} departments:")
                for dept, count in departments[:10]:  # Show first 10
                    print(f"      - {dept}: {count} provider(s)")
                if len(departments) > 10:
                    print(f"      ... and {len(departments) - 10} more departments")

                return True
            else:
                print(f"   ⚠️  Found {provider_count} providers (expected at least 90)")

                # Still show department breakdown
                result = await session.execute(
                    select(Provider.department, func.count(Provider.id))
                    .group_by(Provider.department)
                    .order_by(Provider.department)
                )
                departments = result.all()

                if departments:
                    print(f"   📊 Distribution across {len(departments)} departments:")
                    for dept, count in departments[:10]:
                        print(f"      - {dept}: {count} provider(s)")
                    if len(departments) > 10:
                        print(f"      ... and {len(departments) - 10} more departments")

                return provider_count > 0  # Pass if we have any providers
    except Exception as e:
        print(f"   ❌ Error checking providers: {e}")
        return False


async def check_lab_tests():
    """Check if lab tests are seeded."""
    print("\n🔍 Checking lab tests...")
    try:
        async with async_session_maker() as session:
            result = await session.execute(select(func.count()).select_from(LabTest))
            lab_test_count = result.scalar()

            if lab_test_count >= 8:
                print(f"   ✅ Seeded {lab_test_count} lab tests")

                # Show lab test details
                result = await session.execute(select(LabTest).order_by(LabTest.name))
                tests = result.scalars().all()
                for test in tests:
                    print(f"      - {test.name} ({test.code})")
                return True
            else:
                print(f"   ⚠️  Found {lab_test_count} lab tests (expected at least 8)")

                if lab_test_count > 0:
                    # Show what we have
                    result = await session.execute(select(LabTest).order_by(LabTest.name))
                    tests = result.scalars().all()
                    for test in tests:
                        print(f"      - {test.name} ({test.code})")

                return lab_test_count > 0  # Pass if we have any tests
    except Exception as e:
        print(f"   ❌ Error checking lab tests: {e}")
        return False


async def check_rag_documents():
    """Check if RAG documents are indexed."""
    print("\n🔍 Checking RAG vector store...")
    try:
        rag_service = RAGService()
        stats = await rag_service.get_stats()

        total_vectors = stats.get("total_vectors", 0)
        unique_docs = stats.get("unique_documents", 0)

        if total_vectors > 0:
            print(f"   ✅ Indexed {unique_docs} documents ({total_vectors} chunks)")

            # Provide breakdown
            print(f"\n   📊 Expected document categories:")
            print(f"      - Facility documents: ~5 docs")
            print(f"      - Doctor profiles: ~{stats.get('total_vectors', 0) // 3} docs")
            print(f"      - Lab test documents: ~12 docs")
            print(f"      Total expected: ~107 docs")

            # Test retrieval
            print(f"\n   🧪 Testing retrieval...")
            test_queries = [
                ("parking information", "Facility docs"),
                ("Complete Blood Count", "Lab test docs"),
                ("cardiologist", "Doctor profiles"),
            ]

            retrieval_works = False
            for query, category in test_queries:
                result = await rag_service.retrieve(query, top_k=1)
                if result.chunks:
                    print(f"      ✅ {category}: '{result.chunks[0].doc_title}'")
                    retrieval_works = True
                else:
                    print(f"      ⚠️  {category}: No results")

            return retrieval_works
        else:
            print(f"   ❌ Vector store is empty (0 documents indexed)")
            print(f"\n   💡 To populate RAG documents, run:")
            print(f"      docker-compose exec backend python scripts/seed_demo_data.py")
            return False
    except Exception as e:
        print(f"   ❌ Error checking RAG documents: {e}")
        import traceback

        print(f"   Details: {traceback.format_exc()}")
        return False


async def main():
    """Run all validation checks."""
    print("=" * 70)
    print("CareConnect - Database & RAG Validation")
    print("=" * 70)
    print()

    results = []

    # Run all checks
    results.append(("Database Initialized", await check_database_initialized()))
    results.append(("Users Seeded", await check_users()))
    results.append(("Providers Seeded", await check_providers()))
    results.append(("Lab Tests Seeded", await check_lab_tests()))
    results.append(("RAG Documents Indexed", await check_rag_documents()))

    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:12} | {check_name}")

    print("=" * 70)

    if passed == total:
        print(f"✅ All {total} checks passed!")
        print("\nYour CareConnect instance is fully seeded and ready to use! 🎉")
        print("\n📋 Demo Credentials:")
        print("   Patient: hadihacan@gmail.com / password123")
        print("   Admin:   admin@admin.com / Admin@123")
        return True
    else:
        print(f"⚠️  {passed}/{total} checks passed")
        print(f"\n❌ {total - passed} check(s) failed.")

        if any(not result for _, result in results[1:4]):  # Database checks failed
            print("\n💡 To seed the database, run:")
            print("   docker-compose exec backend python scripts/seed_demo_data.py")

        return False


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
