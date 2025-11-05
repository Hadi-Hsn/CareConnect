"""Seed demo data for CareConnect."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.db import async_session_maker, init_db
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
                role=UserRole.PATIENT,
                hashed_password=get_password_hash("password123"),
            ),
            User(
                email="hadi.wmail@gmail.com",
                name="Admin User",
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
                department="Internal Medicine",
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
                department="Internal Medicine",
                type=ProviderType.NURSE_PRACTITIONER,
                specialty="Adult Primary Care",
                bio="Nurse practitioner focused on preventive care",
            ),
            Provider(
                name="Dr. Ahmed Hassan",
                department="Neurology",
                type=ProviderType.PHYSICIAN,
                specialty="Stroke Care",
                bio="Neurologist specializing in stroke prevention and treatment",
            ),
            Provider(
                name="Dr. Emily Taylor",
                department="Pediatrics",
                type=ProviderType.PHYSICIAN,
                specialty="General Pediatrics",
                bio="Pediatrician with expertise in child development",
            ),
            Provider(
                name="Dr. David Kim",
                department="Oncology",
                type=ProviderType.SPECIALIST,
                specialty="Medical Oncology",
                bio="Oncologist specializing in cancer treatment and care",
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
                department="Hematology",
                description="Measures different components of blood including red and white blood cells",
                prep_instructions="No special preparation required",
                estimated_duration_minutes=15,
            ),
            LabTest(
                name="Lipid Panel",
                code="LAB-LIPID",
                department="Cardiology",
                description="Measures cholesterol and triglyceride levels",
                prep_instructions="Fasting required before test",
                fasting_hours=12,
                estimated_duration_minutes=15,
            ),
            LabTest(
                name="Thyroid Function Test",
                code="LAB-THYROID",
                department="Endocrinology",
                description="Measures thyroid hormone levels (TSH, T3, T4)",
                prep_instructions="No special preparation required",
                estimated_duration_minutes=15,
            ),
            LabTest(
                name="Hemoglobin A1C",
                code="LAB-A1C",
                department="Endocrinology",
                description="Measures average blood sugar levels over 3 months",
                prep_instructions="No fasting required",
                estimated_duration_minutes=15,
            ),
            LabTest(
                name="Comprehensive Metabolic Panel",
                code="LAB-CMP",
                department="Nephrology",
                description="Measures kidney function, blood sugar, and electrolytes",
                prep_instructions="Fasting recommended",
                fasting_hours=8,
                estimated_duration_minutes=15,
            ),
            LabTest(
                name="Liver Function Test",
                code="LAB-LFT",
                department="Gastroenterology",
                description="Evaluates liver health and function",
                prep_instructions="No special preparation required",
                estimated_duration_minutes=15,
            ),
            LabTest(
                name="Urinalysis",
                code="LAB-UA",
                department="Nephrology",
                description="Analyzes urine for various health indicators",
                prep_instructions="First morning urine sample preferred",
                estimated_duration_minutes=10,
            ),
            LabTest(
                name="Chest X-Ray",
                code="RAD-CXR",
                department="Radiology",
                description="Imaging of chest, heart, and lungs",
                prep_instructions="Remove jewelry and metal objects",
                estimated_duration_minutes=30,
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
        ),
    ]

    rag_service = RAGService()
    result = await rag_service.index_documents(documents, replace=True)
    print(f"✓ Indexed {result.indexed_count} documents ({result.total_chunks} chunks)")


async def main():
    """Run all seed functions."""
    print("🌱 Starting database seeding...")
    print()

    # Initialize database
    await init_db()
    print("✓ Database initialized")

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
