"""Comprehensive database population script for CareConnect demo."""

import asyncio
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import delete, select

from app.core.db import async_session_maker, init_db
from app.core.security import get_password_hash
from app.models import (
    Appointment,
    AppointmentChannel,
    AppointmentStatus,
    LabTest,
    PatientTestResult,
    Provider,
    ProviderType,
    User,
    UserRole,
)
from app.schemas.rag import Document
from app.services.rag_service import RAGService
from app.services.pdf_parser import PDFParser

# Import PDF generator
from scripts.generate_provider_pdfs import generate_provider_pdf


# Patient names for demo data
PATIENT_NAMES = [
    "Emma Johnson",
    "Liam Smith",
    "Olivia Brown",
    "Noah Davis",
    "Ava Wilson",
    "Ethan Martinez",
    "Sophia Anderson",
    "Mason Taylor",
    "Isabella Thomas",
    "Lucas Moore",
    "Mia Jackson",
    "Oliver White",
    "Charlotte Harris",
    "Elijah Martin",
    "Amelia Thompson",
    "James Garcia",
    "Harper Rodriguez",
    "Benjamin Lee",
    "Evelyn Walker",
    "William Hall",
    "Abigail Allen",
    "Alexander Young",
    "Emily King",
    "Michael Wright",
    "Elizabeth Lopez",
    "Daniel Hill",
    "Sofia Scott",
    "Matthew Green",
    "Avery Adams",
    "Joseph Nelson",
]

# Appointment reasons by department
APPOINTMENT_REASONS = {
    "Cardiology": [
        "Annual heart checkup",
        "Chest pain evaluation",
        "High blood pressure follow-up",
        "Pacemaker check",
        "Heart palpitations",
        "Pre-surgical cardiac evaluation",
    ],
    "Dermatology": [
        "Skin rash examination",
        "Acne treatment",
        "Mole screening",
        "Eczema follow-up",
        "Annual skin cancer screening",
        "Cosmetic consultation",
    ],
    "Emergency Medicine": [
        "Urgent care visit",
        "Minor injury treatment",
        "Fever and infection",
        "Chest pain evaluation",
    ],
    "Endocrinology": [
        "Diabetes management",
        "Thyroid disorder follow-up",
        "Hormone imbalance",
        "A1C monitoring",
        "Insulin adjustment",
    ],
    "Gastroenterology": [
        "Stomach pain evaluation",
        "IBS management",
        "Colonoscopy follow-up",
        "GERD treatment",
        "Digestive issues",
    ],
    "General Surgery": [
        "Pre-operative consultation",
        "Post-operative follow-up",
        "Hernia evaluation",
        "Surgical procedure discussion",
    ],
    "Hematology": [
        "Anemia evaluation",
        "Blood disorder follow-up",
        "Clotting disorder management",
        "Cancer screening",
    ],
    "Infectious Disease": [
        "Infection treatment",
        "Travel medicine consultation",
        "HIV care",
        "Vaccination",
    ],
    "Internal Medicine": [
        "Annual physical exam",
        "Chronic disease management",
        "Health screening",
        "Multiple condition follow-up",
        "Preventive care visit",
    ],
    "Nephrology": [
        "Kidney function evaluation",
        "Dialysis follow-up",
        "Hypertension management",
        "Kidney stone consultation",
    ],
    "Neurology": [
        "Headache evaluation",
        "Seizure management",
        "Stroke follow-up",
        "Memory concerns",
        "Tremor evaluation",
    ],
    "Neurosurgery": [
        "Spine consultation",
        "Pre-surgical evaluation",
        "Post-surgical follow-up",
        "Back pain evaluation",
    ],
    "Obstetrics and Gynecology": [
        "Prenatal visit",
        "Annual gynecological exam",
        "Pregnancy consultation",
        "Family planning discussion",
    ],
    "Oncology": [
        "Cancer screening",
        "Chemotherapy follow-up",
        "Treatment planning",
        "Post-treatment monitoring",
    ],
    "Ophthalmology": [
        "Vision examination",
        "Eye pain evaluation",
        "Cataract consultation",
        "Diabetic eye screening",
        "Contact lens fitting",
    ],
    "Orthopedics": [
        "Joint pain evaluation",
        "Sports injury",
        "Arthritis management",
        "Post-surgical follow-up",
        "Back pain consultation",
    ],
    "Otolaryngology (ENT)": [
        "Sinus infection",
        "Hearing evaluation",
        "Throat pain",
        "Ear infection follow-up",
    ],
    "Pathology": [
        "Biopsy results discussion",
        "Lab result consultation",
    ],
    "Pediatrics": [
        "Well-child visit",
        "Vaccination appointment",
        "Sick child visit",
        "Development screening",
    ],
    "Physical Medicine and Rehabilitation": [
        "Physical therapy evaluation",
        "Pain management",
        "Injury rehabilitation",
        "Post-stroke therapy",
    ],
    "Psychiatry": [
        "Mental health evaluation",
        "Medication management",
        "Therapy session",
        "Depression treatment",
        "Anxiety management",
    ],
    "Pulmonology": [
        "Asthma management",
        "COPD follow-up",
        "Breathing difficulty evaluation",
        "Sleep study consultation",
    ],
    "Radiology": [
        "MRI scan",
        "CT scan",
        "X-ray imaging",
        "Ultrasound",
    ],
    "Rheumatology": [
        "Arthritis management",
        "Lupus follow-up",
        "Joint pain evaluation",
        "Autoimmune disease consultation",
    ],
    "Urology": [
        "Kidney stone evaluation",
        "Prostate screening",
        "Urinary issue consultation",
        "Bladder infection follow-up",
    ],
}


async def clear_existing_data():
    """Clear existing demo data (except admin user)."""
    async with async_session_maker() as session:
        # Delete test results first (foreign key constraint)
        await session.execute(delete(PatientTestResult))

        # Delete appointments (foreign key constraint)
        await session.execute(delete(Appointment))

        # Delete patients (preserve admin and hadihacan@gmail.com)
        await session.execute(
            delete(User).where(User.email.not_in(["admin@admin.com", "hadihacan@gmail.com"]))
        )

        # Delete providers
        await session.execute(delete(Provider))

        # Delete lab tests
        await session.execute(delete(LabTest))

        await session.commit()
        print("✓ Cleared existing demo data (preserved admin and hadihacan@gmail.com)")


async def ensure_admin_user():
    """Ensure admin user exists with correct credentials."""
    async with async_session_maker() as session:
        # Check if admin exists
        result = await session.execute(select(User).where(User.email == "admin@admin.com"))
        admin = result.scalar_one_or_none()

        if admin:
            # Update password to ensure it matches
            admin.hashed_password = get_password_hash("password123")
            admin.name = "Admin User"
            admin.role = UserRole.ADMIN
        else:
            # Create new admin
            admin = User(
                email="admin@admin.com",
                name="Admin User",
                role=UserRole.ADMIN,
                hashed_password=get_password_hash("password123"),
            )
            session.add(admin)

        await session.commit()
        print("✓ Admin user ensured (admin@admin.com / password123)")


async def seed_patients():
    """Seed 30 patient accounts."""
    async with async_session_maker() as session:
        # Check if hadihacan@gmail.com already exists
        result = await session.execute(select(User).where(User.email == "hadihacan@gmail.com"))
        existing_hadi = result.scalar_one_or_none()

        patients = []

        # Only add Hadi if he doesn't exist
        if not existing_hadi:
            patients.append(
                User(
                    email="hadihacan@gmail.com",
                    name="Hadi Hasan",
                    phone="+961 70 123456",
                    role=UserRole.PATIENT,
                    hashed_password=get_password_hash("patient123"),
                )
            )

        # Add demo patients (check for duplicates)
        existing_emails = set()
        if existing_hadi:
            existing_emails.add("hadihacan@gmail.com")

        # Get existing patient emails
        result = await session.execute(select(User.email).where(User.role == UserRole.PATIENT))
        existing_emails.update(result.scalars().all())

        for i, name in enumerate(PATIENT_NAMES):
            # Generate email from name
            email = name.lower().replace(" ", ".") + f"@patient.com"

            # Skip if already exists
            if email in existing_emails:
                continue

            # Generate phone number
            phone = f"+961 {random.randint(70, 79)} {random.randint(100000, 999999)}"

            patients.append(
                User(
                    email=email,
                    name=name,
                    phone=phone,
                    role=UserRole.PATIENT,
                    hashed_password=get_password_hash("patient123"),
                )
            )

        if patients:
            session.add_all(patients)
            await session.commit()
            print(
                f"✓ Seeded {len(patients)} patient accounts (including hadihacan@gmail.com if new)"
            )
        else:
            print("✓ All patient accounts already exist, skipped seeding")

        # Return all patients (existing + new)
        result = await session.execute(select(User).where(User.role == UserRole.PATIENT))
        return result.scalars().all()


async def seed_providers():
    """Seed providers (3+ per department)."""
    async with async_session_maker() as session:
        providers = [
            # Cardiology (3 providers)
            Provider(
                name="Dr. Sara Haddad",
                department="Cardiology",
                type=ProviderType.PHYSICIAN,
                specialty="Interventional Cardiology",
                bio="Board-certified cardiologist with 15+ years of experience in interventional procedures",
            ),
            Provider(
                name="Dr. Michael Roberts",
                department="Cardiology",
                type=ProviderType.PHYSICIAN,
                specialty="Electrophysiology",
                bio="Cardiac electrophysiologist specializing in arrhythmia treatment and pacemaker implantation",
            ),
            Provider(
                name="Dr. Lisa Chen",
                department="Cardiology",
                type=ProviderType.SPECIALIST,
                specialty="Heart Failure",
                bio="Heart failure specialist with expertise in advanced cardiac care",
            ),
            # Dermatology (3 providers)
            Provider(
                name="Dr. Jennifer Wong",
                department="Dermatology",
                type=ProviderType.PHYSICIAN,
                specialty="Medical Dermatology",
                bio="Expert in treating skin conditions including acne, eczema, and psoriasis",
            ),
            Provider(
                name="Dr. Alexander Petrov",
                department="Dermatology",
                type=ProviderType.SPECIALIST,
                specialty="Cosmetic Dermatology",
                bio="Cosmetic dermatologist specializing in anti-aging treatments and skin rejuvenation",
            ),
            Provider(
                name="Dr. Rachel Martinez",
                department="Dermatology",
                type=ProviderType.PHYSICIAN,
                specialty="Pediatric Dermatology",
                bio="Pediatric dermatologist focused on children's skin health",
            ),
            # Emergency Medicine (3 providers)
            Provider(
                name="Dr. Robert Thompson",
                department="Emergency Medicine",
                type=ProviderType.PHYSICIAN,
                specialty="Emergency Medicine",
                bio="Board-certified emergency physician with trauma care expertise",
            ),
            Provider(
                name="Dr. Samantha Lee",
                department="Emergency Medicine",
                type=ProviderType.PHYSICIAN,
                specialty="Emergency Medicine",
                bio="Emergency medicine specialist with experience in critical care",
            ),
            Provider(
                name="Dr. Carlos Ramirez",
                department="Emergency Medicine",
                type=ProviderType.PHYSICIAN,
                specialty="Emergency Medicine",
                bio="ER physician with expertise in pediatric emergencies",
            ),
            # Endocrinology (3 providers)
            Provider(
                name="Dr. Patricia Singh",
                department="Endocrinology",
                type=ProviderType.PHYSICIAN,
                specialty="Diabetes Care",
                bio="Endocrinologist specializing in diabetes management and insulin therapy",
            ),
            Provider(
                name="Dr. Daniel Kim",
                department="Endocrinology",
                type=ProviderType.SPECIALIST,
                specialty="Thyroid Disorders",
                bio="Expert in thyroid conditions including hypothyroidism and hyperthyroidism",
            ),
            Provider(
                name="Dr. Maria Gonzalez",
                department="Endocrinology",
                type=ProviderType.PHYSICIAN,
                specialty="Metabolic Disorders",
                bio="Endocrinologist focused on metabolic syndrome and hormonal imbalances",
            ),
            # Gastroenterology (3 providers)
            Provider(
                name="Dr. James Wilson",
                department="Gastroenterology",
                type=ProviderType.PHYSICIAN,
                specialty="Digestive Disorders",
                bio="Gastroenterologist with expertise in IBS, Crohn's disease, and ulcerative colitis",
            ),
            Provider(
                name="Dr. Amy Nguyen",
                department="Gastroenterology",
                type=ProviderType.SPECIALIST,
                specialty="Hepatology",
                bio="Liver specialist treating hepatitis, cirrhosis, and fatty liver disease",
            ),
            Provider(
                name="Dr. Steven Brown",
                department="Gastroenterology",
                type=ProviderType.PHYSICIAN,
                specialty="Endoscopy",
                bio="Expert in colonoscopy and upper endoscopy procedures",
            ),
            # Internal Medicine (3 providers)
            Provider(
                name="Dr. Maria Rodriguez",
                department="Internal Medicine",
                type=ProviderType.PHYSICIAN,
                specialty="Family Medicine",
                bio="Comprehensive family healthcare provider with 20+ years of experience",
            ),
            Provider(
                name="Dr. John Davis",
                department="Internal Medicine",
                type=ProviderType.PHYSICIAN,
                specialty="Geriatric Medicine",
                bio="Internist specializing in elderly patient care",
            ),
            Provider(
                name="Sarah Johnson",
                department="Internal Medicine",
                type=ProviderType.NURSE_PRACTITIONER,
                specialty="Adult Primary Care",
                bio="Nurse practitioner focused on preventive care and chronic disease management",
            ),
            # Neurology (3 providers)
            Provider(
                name="Dr. Ahmed Hassan",
                department="Neurology",
                type=ProviderType.PHYSICIAN,
                specialty="Stroke Care",
                bio="Neurologist specializing in stroke prevention and acute stroke treatment",
            ),
            Provider(
                name="Dr. Catherine White",
                department="Neurology",
                type=ProviderType.SPECIALIST,
                specialty="Epilepsy",
                bio="Epilepsy specialist managing seizure disorders with advanced therapies",
            ),
            Provider(
                name="Dr. Brian Foster",
                department="Neurology",
                type=ProviderType.PHYSICIAN,
                specialty="Movement Disorders",
                bio="Expert in Parkinson's disease and other movement disorders",
            ),
            # Oncology (3 providers)
            Provider(
                name="Dr. David Kim",
                department="Oncology",
                type=ProviderType.SPECIALIST,
                specialty="Medical Oncology",
                bio="Medical oncologist specializing in chemotherapy and immunotherapy",
            ),
            Provider(
                name="Dr. Susan Anderson",
                department="Oncology",
                type=ProviderType.PHYSICIAN,
                specialty="Radiation Oncology",
                bio="Radiation oncologist providing advanced radiation therapy for cancer treatment",
            ),
            Provider(
                name="Dr. Peter Chang",
                department="Oncology",
                type=ProviderType.SPECIALIST,
                specialty="Hematologic Oncology",
                bio="Specialist in leukemia, lymphoma, and blood cancers",
            ),
            # Orthopedics (3 providers)
            Provider(
                name="Dr. James Chen",
                department="Orthopedics",
                type=ProviderType.SPECIALIST,
                specialty="Sports Medicine",
                bio="Orthopedic surgeon specializing in sports injuries and arthroscopic surgery",
            ),
            Provider(
                name="Dr. William Brown",
                department="Orthopedics",
                type=ProviderType.SPECIALIST,
                specialty="Joint Replacement",
                bio="Joint replacement specialist performing hip and knee replacements",
            ),
            Provider(
                name="Dr. Nicole Garcia",
                department="Orthopedics",
                type=ProviderType.PHYSICIAN,
                specialty="Pediatric Orthopedics",
                bio="Pediatric orthopedist treating childhood bone and joint conditions",
            ),
            # Pediatrics (3 providers)
            Provider(
                name="Dr. Emily Taylor",
                department="Pediatrics",
                type=ProviderType.PHYSICIAN,
                specialty="General Pediatrics",
                bio="Pediatrician with expertise in child development and preventive care",
            ),
            Provider(
                name="Dr. Samuel Green",
                department="Pediatrics",
                type=ProviderType.SPECIALIST,
                specialty="Pediatric Critical Care",
                bio="Pediatric intensivist managing critically ill children",
            ),
            Provider(
                name="Dr. Jennifer Adams",
                department="Pediatrics",
                type=ProviderType.PHYSICIAN,
                specialty="Developmental Pediatrics",
                bio="Developmental pediatrician supporting children with special needs",
            ),
            # Psychiatry (3 providers)
            Provider(
                name="Dr. Sophia Anderson",
                department="Psychiatry",
                type=ProviderType.PHYSICIAN,
                specialty="Adult Psychiatry",
                bio="Psychiatrist treating depression, anxiety, and mood disorders",
            ),
            Provider(
                name="Dr. Michael Roberts",
                department="Psychiatry",
                type=ProviderType.SPECIALIST,
                specialty="Child Psychiatry",
                bio="Child psychiatrist specializing in ADHD, autism, and behavioral issues",
            ),
            Provider(
                name="Dr. Jessica Brown",
                department="Psychiatry",
                type=ProviderType.PHYSICIAN,
                specialty="Addiction Psychiatry",
                bio="Addiction specialist treating substance use disorders",
            ),
        ]

        session.add_all(providers)
        await session.commit()
        print(f"✓ Seeded {len(providers)} providers")
        return providers


async def seed_lab_tests():
    """Seed comprehensive lab tests."""
    async with async_session_maker() as session:
        lab_tests = [
            # Hematology Tests
            LabTest(
                name="Complete Blood Count (CBC)",
                code="LAB-CBC-001",
                department="Hematology",
                description="Measures different components of blood including red and white blood cells, hemoglobin, hematocrit, and platelets",
                prep_instructions="No special preparation required",
                estimated_duration_minutes=15,
            ),
            LabTest(
                name="Basic Metabolic Panel",
                code="LAB-BMP-002",
                department="Hematology",
                description="Measures glucose, calcium, and electrolytes",
                prep_instructions="Fasting recommended",
                fasting_hours=8,
                estimated_duration_minutes=15,
            ),
            LabTest(
                name="Coagulation Panel (PT/INR)",
                code="LAB-COAG-003",
                department="Hematology",
                description="Measures blood clotting time",
                prep_instructions="No special preparation required",
                estimated_duration_minutes=20,
            ),
            # Cardiology Tests
            LabTest(
                name="Lipid Panel",
                code="LAB-LIPID-004",
                department="Cardiology",
                description="Measures cholesterol (total, HDL, LDL) and triglyceride levels",
                prep_instructions="12-hour fasting required",
                fasting_hours=12,
                estimated_duration_minutes=15,
            ),
            LabTest(
                name="Cardiac Enzyme Panel (Troponin)",
                code="LAB-TROP-005",
                department="Cardiology",
                description="Measures cardiac markers for heart attack diagnosis",
                prep_instructions="No special preparation required",
                estimated_duration_minutes=30,
            ),
            LabTest(
                name="B-type Natriuretic Peptide (BNP)",
                code="LAB-BNP-006",
                department="Cardiology",
                description="Helps diagnose heart failure",
                prep_instructions="No special preparation required",
                estimated_duration_minutes=20,
            ),
            # Endocrinology Tests
            LabTest(
                name="Thyroid Function Test (TSH, T3, T4)",
                code="LAB-THYROID-007",
                department="Endocrinology",
                description="Measures thyroid hormone levels",
                prep_instructions="No special preparation required",
                estimated_duration_minutes=15,
            ),
            LabTest(
                name="Hemoglobin A1C",
                code="LAB-A1C-008",
                department="Endocrinology",
                description="Measures average blood sugar levels over 2-3 months",
                prep_instructions="No fasting required",
                estimated_duration_minutes=15,
            ),
            LabTest(
                name="Fasting Blood Glucose",
                code="LAB-FBG-009",
                department="Endocrinology",
                description="Measures blood sugar after fasting",
                prep_instructions="8-hour fasting required",
                fasting_hours=8,
                estimated_duration_minutes=10,
            ),
            LabTest(
                name="Insulin Level",
                code="LAB-INS-010",
                department="Endocrinology",
                description="Measures insulin production",
                prep_instructions="Fasting recommended",
                fasting_hours=8,
                estimated_duration_minutes=20,
            ),
            # Nephrology Tests
            LabTest(
                name="Comprehensive Metabolic Panel (CMP)",
                code="LAB-CMP-011",
                department="Nephrology",
                description="Measures kidney function, blood sugar, and electrolytes",
                prep_instructions="Fasting recommended",
                fasting_hours=8,
                estimated_duration_minutes=15,
            ),
            LabTest(
                name="Urinalysis",
                code="LAB-UA-012",
                department="Nephrology",
                description="Analyzes urine for various health indicators",
                prep_instructions="First morning urine sample preferred",
                estimated_duration_minutes=10,
            ),
            LabTest(
                name="Creatinine and GFR",
                code="LAB-CREAT-013",
                department="Nephrology",
                description="Assesses kidney function",
                prep_instructions="No special preparation required",
                estimated_duration_minutes=15,
            ),
            # Gastroenterology Tests
            LabTest(
                name="Liver Function Test (LFT)",
                code="LAB-LFT-014",
                department="Gastroenterology",
                description="Evaluates liver health and function",
                prep_instructions="No special preparation required",
                estimated_duration_minutes=15,
            ),
            LabTest(
                name="Hepatitis Panel",
                code="LAB-HEP-015",
                department="Gastroenterology",
                description="Screens for hepatitis A, B, and C",
                prep_instructions="No special preparation required",
                estimated_duration_minutes=30,
            ),
            LabTest(
                name="Amylase and Lipase",
                code="LAB-AMYL-016",
                department="Gastroenterology",
                description="Tests for pancreatic disorders",
                prep_instructions="No special preparation required",
                estimated_duration_minutes=20,
            ),
            # Radiology Imaging
            LabTest(
                name="X-Ray",
                code="RAD-XR-017",
                department="Radiology",
                description="Imaging of requested body part",
                prep_instructions="Remove jewelry and metal objects. Notify the radiologist if you have any previous surgery that involves metal implants",
                estimated_duration_minutes=30,
            ),
            LabTest(
                name="MRI Scan",
                code="RAD-MRI-018",
                department="Radiology",
                description="Detailed imaging using magnetic resonance",
                prep_instructions="Remove all metal objects; inform staff of implants",
                estimated_duration_minutes=60,
            ),
            LabTest(
                name="CT Scan",
                code="RAD-CT-019",
                department="Radiology",
                description="Computed tomography imaging",
                prep_instructions="May require fasting; follow specific instructions",
                estimated_duration_minutes=45,
            ),
            LabTest(
                name="Ultrasound",
                code="RAD-US-020",
                department="Radiology",
                description="Ultrasound imaging",
                prep_instructions="Varies by exam type; follow specific instructions",
                estimated_duration_minutes=30,
            ),
            # Oncology Tests
            LabTest(
                name="Tumor Marker Panel",
                code="LAB-TM-021",
                department="Oncology",
                description="Measures cancer markers in blood",
                prep_instructions="No special preparation required",
                estimated_duration_minutes=30,
            ),
            LabTest(
                name="PSA Test",
                code="LAB-PSA-022",
                department="Oncology",
                description="Prostate-specific antigen screening",
                prep_instructions="No special preparation required",
                estimated_duration_minutes=15,
            ),
        ]

        for lab_test in lab_tests:
            if not lab_test.code.startswith("RAD-"):
                lab_test.department = "Laboratory"

        session.add_all(lab_tests)
        await session.commit()
        print(f"✓ Seeded {len(lab_tests)} lab tests")


async def seed_appointments(patients, providers):
    """Seed diverse appointments for patients."""
    async with async_session_maker() as session:
        appointments = []
        now = datetime.now(timezone.utc)

        statuses = [
            AppointmentStatus.CONFIRMED,
            AppointmentStatus.COMPLETED,
        ]

        channels = [
            AppointmentChannel.WEB,
            AppointmentChannel.PHONE,
            AppointmentChannel.AGENT,
        ]

        # Create appointments for each patient
        for patient in patients:
            # Each patient gets 2-5 appointments
            num_appointments = random.randint(2, 5)

            for _ in range(num_appointments):
                # Random provider
                provider = random.choice(providers)
                department = provider.department

                # Random time between 60 days ago and 30 days in future
                days_offset = random.randint(-60, 30)
                appointment_date = now + timedelta(days=days_offset)

                # Random time during business hours (8 AM - 5 PM)
                hour = random.randint(8, 16)
                appointment_date = appointment_date.replace(
                    hour=hour, minute=random.choice([0, 15, 30, 45]), second=0, microsecond=0
                )

                # Duration: 15, 30, 45, or 60 minutes
                duration = random.choice([15, 30, 45, 60])
                end_time = appointment_date + timedelta(minutes=duration)

                # Status based on date
                if days_offset < -7:
                    status = AppointmentStatus.COMPLETED
                elif days_offset < 0:
                    status = random.choice(
                        [AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED]
                    )
                else:
                    status = AppointmentStatus.CONFIRMED

                # Get appropriate reason for department
                reasons = APPOINTMENT_REASONS.get(department, ["General consultation"])
                reason = random.choice(reasons)

                # Channel
                channel = random.choice(channels)

                # Notes for completed appointments
                notes = None
                if status == AppointmentStatus.COMPLETED:
                    notes_options = [
                        "Patient responded well to treatment. Follow-up scheduled.",
                        "Vital signs normal. Discussed treatment plan.",
                        "Patient education provided. Prescription updated.",
                        "Labs ordered. Will review results at next visit.",
                        "Symptoms improving. Continue current medication.",
                    ]
                    notes = random.choice(notes_options)

                appointments.append(
                    Appointment(
                        user_id=patient.id,
                        provider_id=provider.id,
                        time_start=appointment_date,
                        time_end=end_time,
                        status=status,
                        channel=channel,
                        reason=reason,
                        notes=notes,
                        confirmation_code=f"CONF-{random.randint(100000, 999999)}",
                    )
                )

        session.add_all(appointments)
        await session.commit()
        print(f"✓ Seeded {len(appointments)} appointments")


async def seed_patient_test_results(patients, providers):
    """Seed patient test results."""
    async with async_session_maker() as session:
        # Get all lab tests
        result = await session.execute(select(LabTest))
        lab_tests = list(result.scalars().all())

        test_results = []
        now = datetime.now(timezone.utc)

        # Create test results for random patients
        num_patients_with_tests = min(15, len(patients))  # 15 patients get test results
        selected_patients = random.sample(patients, num_patients_with_tests)

        for patient in selected_patients:
            # Each patient gets 1-4 test results
            num_tests = random.randint(1, 4)
            patient_tests = random.sample(lab_tests, min(num_tests, len(lab_tests)))

            for lab_test in patient_tests:
                # Random provider from cardiology, internal medicine, or endocrinology
                appropriate_providers = [
                    p
                    for p in providers
                    if p.department
                    in ["Cardiology", "Internal Medicine", "Endocrinology", lab_test.department]
                ]
                ordered_by = (
                    random.choice(appropriate_providers)
                    if appropriate_providers
                    else random.choice(providers)
                )

                # Test date between 90 days ago and 7 days ago
                days_ago = random.randint(7, 90)
                test_date = now - timedelta(days=days_ago)

                # Status
                status = random.choice(
                    ["completed", "completed", "completed", "pending"]
                )  # 75% completed

                # Generate realistic results based on test type
                result_value = None
                result_unit = None
                reference_range = None
                notes = None

                if status == "completed":
                    if "CBC" in lab_test.name:
                        result_value = f"WBC: {random.uniform(4.5, 11.0):.1f}, RBC: {random.uniform(4.2, 5.9):.1f}"
                        result_unit = "x10^9/L"
                        reference_range = "WBC: 4.5-11.0, RBC: 4.2-5.9"
                        notes = "Values within normal limits"
                    elif "Glucose" in lab_test.name or "A1C" in lab_test.name:
                        if "A1C" in lab_test.name:
                            result_value = f"{random.uniform(4.5, 7.5):.1f}"
                            result_unit = "%"
                            reference_range = "4.0-5.6%"
                        else:
                            result_value = f"{random.uniform(70, 140):.0f}"
                            result_unit = "mg/dL"
                            reference_range = "70-100 mg/dL"
                        if (
                            float(result_value) > 120
                            if "Glucose" in lab_test.name
                            else float(result_value) > 5.7
                        ):
                            notes = "Elevated - recommend follow-up"
                        else:
                            notes = "Normal range"
                    elif "Lipid" in lab_test.name:
                        total_chol = random.uniform(150, 250)
                        result_value = f"Total: {total_chol:.0f}, HDL: {random.uniform(40, 80):.0f}, LDL: {random.uniform(70, 160):.0f}"
                        result_unit = "mg/dL"
                        reference_range = "Total <200, HDL >40, LDL <130"
                        if total_chol > 200:
                            notes = "Borderline high - diet/lifestyle modifications recommended"
                        else:
                            notes = "Optimal levels"
                    elif "Thyroid" in lab_test.name:
                        result_value = f"TSH: {random.uniform(0.5, 4.5):.2f}"
                        result_unit = "mIU/L"
                        reference_range = "0.5-4.5 mIU/L"
                        notes = "Normal thyroid function"
                    else:
                        result_value = "See detailed report"
                        notes = "All values within normal limits"

                test_results.append(
                    PatientTestResult(
                        user_id=patient.id,
                        lab_test_id=lab_test.id,
                        ordered_by_provider_id=ordered_by.id,
                        test_date=test_date,
                        result_value=result_value,
                        result_unit=result_unit,
                        reference_range=reference_range,
                        status=status,
                        notes=notes,
                    )
                )

        session.add_all(test_results)
        await session.commit()
        print(
            f"✓ Seeded {len(test_results)} patient test results for {num_patients_with_tests} patients"
        )


async def seed_rag_documents(providers):
    """Seed facility and doctor documents for RAG."""
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
    ]

    # Generate and add doctor PDF profiles
    print("Generating PDF profiles for providers...")
    pdf_parser = PDFParser()

    for i, provider in enumerate(providers, 1):
        try:
            # Generate PDF
            pdf_bytes = generate_provider_pdf(provider)

            # Extract text from PDF
            pdf_text = pdf_parser.extract_text_from_bytes(pdf_bytes)

            # Create document with PDF content
            provider_type = provider.type if hasattr(provider.type, "value") else provider.type

            documents.append(
                Document(
                    title=f"Dr. {provider.name} - Complete Profile",
                    content=pdf_text,
                    metadata={
                        "type": "doctor_profile_pdf",
                        "department": provider.department,
                        "specialty": provider.specialty or "",
                        "provider_id": str(provider.id),
                        "provider_name": provider.name,
                        "provider_type": provider_type,
                        "source": "generated_pdf",
                    },
                    doc_type="pdf",
                )
            )

            print(f"  ✓ Generated PDF for {provider.name} ({i}/{len(providers)})")

        except Exception as e:
            print(f"  ✗ Failed to generate PDF for {provider.name}: {str(e)}")
            continue

    # Index all documents
    rag_service = RAGService()
    result = await rag_service.index_documents(documents, replace=True)
    print(f"✓ Indexed {result.indexed_count} documents ({result.total_chunks} chunks)")
    print(f"  - {len(providers)} provider PDF profiles included")


async def populate_database():
    """Main function to populate entire database."""
    print("🌱 Starting comprehensive database population...")
    print()

    # Initialize database
    await init_db()
    print("✓ Database initialized")

    # Clear existing data
    await clear_existing_data()

    # Ensure admin exists
    await ensure_admin_user()

    # Seed all data
    patients = await seed_patients()
    providers = await seed_providers()
    await seed_lab_tests()

    # Get actual patient and provider objects from database
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.role == UserRole.PATIENT))
        patients = list(result.scalars().all())

        result = await session.execute(select(Provider))
        providers = list(result.scalars().all())

    await seed_appointments(patients, providers)
    await seed_patient_test_results(patients, providers)
    await seed_rag_documents(providers)

    print()
    print("✅ Database population completed successfully!")
    print()
    print(f"Summary:")
    print(f"  - 1 Admin user (admin@admin.com / password123)")
    print(f"  - {len(patients)} Patient accounts (password: patient123)")
    print(f"    • Hadi Hasan (hadihacan@gmail.com)")
    print(f"    • 30 demo patients")
    print(f"  - {len(providers)} Providers across multiple departments")
    print(f"  - 22 Lab tests")
    print(f"  - Patient test results with realistic values")
    print(f"  - Appointments distributed across past, present, and future")
    print(f"  - PDF profiles generated for all providers and indexed in RAG")
    print()
    print("🔑 Login credentials:")
    print(f"  Admin: admin@admin.com / password123")
    print(f"  Patient (Hadi): hadihacan@gmail.com / patient123")
    print()


if __name__ == "__main__":
    asyncio.run(populate_database())
