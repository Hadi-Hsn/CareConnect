"""Seed demo data for CareConnect.

This script is now optional. By default it will not modify the database.
Pass `--seed` or set the environment variable `SEED_DB=true` to force seeding.
When seeding with `--force` the database tables will be truncated (cleared)
before inserting seed data.
"""
import argparse
import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent.parent / "backend"))

from sqlalchemy import text

from app.core.db import async_session_maker, init_db, Base
from app.core.security import get_password_hash
from app.models import (
    User,
    UserRole,
    Provider,
    ProviderType,
    LabTest,
)
from app.schemas.rag import Document
from app.services.rag_service import RAGService


async def seed_users():
    """Seed demo users."""
    async with async_session_maker() as session:
        users = [
            User(
                email="hadihacan@gmail.com",
                name="John Doe",
                phone="+1-555-123-4567",
                role=UserRole.PATIENT,
                hashed_password=get_password_hash("password123"),
            ),
            User(
                email="hadi.wmail@gmail.com",
                name="Admin User",
                phone="+1-555-999-8888",
                role=UserRole.ADMIN,
                hashed_password=get_password_hash("admin123"),
            ),
        ]

        session.add_all(users)
        await session.commit()
        print(f"✓ Seeded {len(users)} users")


async def seed_providers():
    """Seed demo providers."""
    async with async_session_maker() as session:
        providers = [
            Provider(
                name="Dr. Sara Haddad",
                department="Cardiology",
                type=ProviderType.PHYSICIAN,
                specialty="Interventional Cardiology",
                bio="Board-certified cardiologist with 15+ years of experience",
            ),
            Provider(
                name="Dr. Omar Nassar",
                department="Radiology",
                type=ProviderType.PHYSICIAN,
                specialty="Diagnostic Imaging",
                bio="Expert in MRI and CT imaging",
            ),
            Provider(
                name="Dr. Maria Rodriguez",
                department="Primary Care",
                type=ProviderType.PHYSICIAN,
                specialty="Family Medicine",
                bio="Comprehensive family healthcare provider",
            ),
            Provider(
                name="Dr. James Chen",
                department="Orthopedics",
                type=ProviderType.SPECIALIST,
                specialty="Sports Medicine",
                bio="Specializing in sports injuries and joint replacement",
            ),
            Provider(
                name="Sarah Johnson",
                department="Primary Care",
                type=ProviderType.NURSE_PRACTITIONER,
                specialty="Adult Primary Care",
                bio="Nurse practitioner focused on preventive care",
            ),
        ]

        session.add_all(providers)
        await session.commit()
        print(f"✓ Seeded {len(providers)} providers")


async def seed_lab_tests():
    """Seed demo lab tests."""
    async with async_session_maker() as session:
        lab_tests = [
            LabTest(
                name="Complete Blood Count (CBC)",
                code="LAB-CBC",
                department="Laboratory",
                description="Measures different components of blood including red and white blood cells",
                prep_instructions="No special preparation required",
                estimated_duration_minutes=15,
            ),
            LabTest(
                name="Lipid Panel",
                code="LAB-LIPID",
                department="Laboratory",
                description="Measures cholesterol and triglyceride levels",
                prep_instructions="Fasting required before test",
                fasting_hours=12,
                estimated_duration_minutes=15,
            ),
            LabTest(
                name="Thyroid Function Test",
                code="LAB-THYROID",
                department="Laboratory",
                description="Measures thyroid hormone levels (TSH, T3, T4)",
                prep_instructions="No special preparation required",
                estimated_duration_minutes=15,
            ),
            LabTest(
                name="Hemoglobin A1C",
                code="LAB-A1C",
                department="Laboratory",
                description="Measures average blood sugar levels over 3 months",
                prep_instructions="No fasting required",
                estimated_duration_minutes=15,
            ),
            LabTest(
                name="Comprehensive Metabolic Panel",
                code="LAB-CMP",
                department="Laboratory",
                description="Measures kidney function, blood sugar, and electrolytes",
                prep_instructions="Fasting recommended",
                fasting_hours=8,
                estimated_duration_minutes=15,
            ),
        ]

        session.add_all(lab_tests)
        await session.commit()
        print(f"✓ Seeded {len(lab_tests)} lab tests")


async def seed_documents():
    """Seed facility documents for RAG."""
    documents = [
        Document(
            title="Parking Guide",
            content="""
            CareConnect Medical Center Parking Information
            
            VISITOR PARKING:
            - North Lot: Open 24/7, closest to main entrance, $5/day
            - South Lot: Free parking, open 6 AM - 10 PM
            - Valet Service: Available at main entrance, $10/day
            
            HANDICAPPED PARKING:
            - Available in all lots near entrances
            - Designated spaces are clearly marked
            
            VALIDATION:
            - Patients can get parking validated at registration
            - Validation covers up to 3 hours
            
            DIRECTIONS TO PARKING:
            From Highway 101: Take Exit 23, turn left on Medical Center Drive. 
            North Lot entrance is on the right, South Lot entrance is on the left.
            """,
            metadata={"type": "parking", "department": "facilities"},
            doc_type="text",
        ),
        Document(
            title="Department Hours",
            content="""
            CareConnect Medical Center Department Hours
            
            EMERGENCY DEPARTMENT: Open 24/7
            
            PRIMARY CARE: Monday-Friday 7:00 AM - 6:00 PM, Saturday 8:00 AM - 2:00 PM
            
            CARDIOLOGY: Monday-Friday 8:00 AM - 5:00 PM
            
            RADIOLOGY: Monday-Friday 7:00 AM - 7:00 PM, Saturday 8:00 AM - 4:00 PM
            
            LABORATORY: Monday-Friday 6:00 AM - 6:00 PM, Saturday 7:00 AM - 1:00 PM
            
            ORTHOPEDICS: Monday-Friday 8:00 AM - 5:00 PM
            
            PHARMACY: Monday-Friday 8:00 AM - 7:00 PM, Saturday 9:00 AM - 5:00 PM
            
            For appointments outside these hours, please call our 24/7 scheduling line at (555) 123-4567.
            """,
            metadata={"type": "hours", "department": "all"},
            doc_type="text",
        ),
        Document(
            title="Lab Test Preparation",
            content="""
            Laboratory Test Preparation Guidelines
            
            FASTING TESTS (Lipid Panel, Glucose, Metabolic Panels):
            - No food or drinks except water for 8-12 hours before test
            - Take regular medications unless instructed otherwise
            - Morning appointments recommended
            
            NON-FASTING TESTS (CBC, Thyroid, A1C):
            - No special preparation needed
            - Eat and drink normally
            - Continue regular medications
            
            GENERAL TIPS:
            - Wear comfortable, short-sleeved clothing
            - Stay hydrated (drink water)
            - Bring your insurance card and ID
            - Arrive 15 minutes early to check in
            
            If you have questions about preparation, call the lab at (555) 123-4570.
            """,
            metadata={"type": "preparation", "department": "laboratory"},
            doc_type="text",
        ),
        Document(
            title="Facility Directions",
            content="""
            CareConnect Medical Center Location & Directions
            
            ADDRESS:
            1234 Medical Center Drive
            Healthville, ST 12345
            
            FROM NORTH:
            Take Highway 101 South to Exit 23 (Medical Center Drive)
            Turn right at the light
            Medical Center is 0.5 miles on the left
            
            FROM SOUTH:
            Take Highway 101 North to Exit 23 (Medical Center Drive)
            Turn left at the light
            Medical Center is 0.5 miles on the left
            
            FROM EAST:
            Take Route 50 West to Highway 101 North
            Follow directions from south
            
            FROM WEST:
            Take Route 50 East to Highway 101 South
            Follow directions from north
            
            PUBLIC TRANSPORTATION:
            Bus routes 15 and 32 stop at the Medical Center entrance
            Light rail Green Line: Medical Center Station (5-minute walk)
            
            LANDMARKS:
            Across from City Park
            Next to Healthville Shopping Center
            """,
            metadata={"type": "directions", "department": "facilities"},
            doc_type="text",
        ),
        Document(
            title="Patient Check-in FAQs",
            content="""
            Frequently Asked Questions - Patient Check-in
            
            Q: How early should I arrive?
            A: Please arrive 15 minutes before your appointment for check-in.
            
            Q: What do I need to bring?
            A: Bring your insurance card, photo ID, list of current medications, 
            and any relevant medical records.
            
            Q: What if I'm running late?
            A: Call us as soon as possible. We'll do our best to accommodate you, 
            but you may need to reschedule.
            
            Q: Can I check in online?
            A: Yes! Use our patient portal to check in up to 2 hours before 
            your appointment.
            
            Q: Where do I check in?
            A: Check in at the main registration desk on the first floor, 
            just inside the main entrance.
            
            Q: What if I need to cancel?
            A: Please call us at least 24 hours in advance at (555) 123-4567 
            or use the patient portal.
            """,
            metadata={"type": "faq", "department": "registration"},
            doc_type="text",
        ),
    ]

    try:
        rag_service = RAGService()
        result = await rag_service.index_documents(documents, replace=False)
        print(f"✓ Indexed {result.indexed_count} documents ({result.total_chunks} chunks)")
    except Exception as e:
        # Make indexing non-fatal during setup (OpenAI key or vectorstore might be missing)
        print(f"⚠️  RAG indexing failed: {e}")
        print("⚠️  Continuing without RAG index. Ensure OPENAI_API_KEY and vector store are configured for full functionality.")


async def clear_database():
    """Truncate all tables in the metadata (RESTART IDENTITY CASCADE).

    This will completely wipe user data and reset sequences. Use only when
    intentionally re-seeding (for demos/tests).
    """
    tables = list(Base.metadata.tables.keys())
    if not tables:
        print("⚠️  No tables found in metadata to truncate.")
        return

    truncate_stmt = "TRUNCATE TABLE " + ", ".join([f'\"{t}\"' for t in tables]) + " RESTART IDENTITY CASCADE"
    async with async_session_maker() as session:
        print(f"⚠️  Clearing database tables: {', '.join(tables)}")
        await session.execute(text(truncate_stmt))
        await session.commit()
        print("✓ Database cleared")


async def main():
    """Run seeding optionally.

    Behavior:
    - Always run migrations (init_db())
    - Only seed when `--seed` / `--force` is passed or env var `SEED_DB=true`.
    - When `--force` is used the database is cleared before seeding.
    """

    parser = argparse.ArgumentParser(description="Seed demo data (optional)")
    parser.add_argument("--seed", action="store_true", help="Run seeding (does not clear DB)")
    parser.add_argument("--force", action="store_true", help="Clear DB and then seed")
    args = parser.parse_args()

    env_seed = os.getenv("SEED_DB", "false").lower() in ("1", "true", "yes")
    should_seed = args.seed or args.force or env_seed

    print("🌱 Starting database seed task (optional)")
    print()

    # Initialize database (always)
    await init_db()
    print("✓ Database initialized")

    if not should_seed:
        print("ℹ️  Skipping seeding (use --seed or set SEED_DB=true to enable)")
        return

    if args.force:
        await clear_database()

    # Seed data
    await seed_users()
    await seed_providers()
    await seed_lab_tests()
    await seed_documents()

    print()
    print("✅ Database seeding completed successfully!")
    print()
    print("Demo credentials:")
    print("  Patient: hadihacan@gmail.com / password123")
    print("  Admin:   hadi.wmail@gmail.com / admin123")


if __name__ == "__main__":
    asyncio.run(main())
