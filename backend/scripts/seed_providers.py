"""Seed providers only - at least 3 doctors per department."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import delete, select

from app.core.db import async_session_maker, init_db
from app.models import Provider, ProviderType
from app.schemas.rag import Document
from app.services.rag_service import RAGService


async def clear_providers():
    """Clear existing providers."""
    async with async_session_maker() as session:
        await session.execute(delete(Provider))
        await session.commit()
        print("✓ Cleared existing providers")


async def seed_providers():
    """Seed demo providers - at least 3 doctors per department."""
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
            
            # General Surgery (3 providers)
            Provider(
                name="Dr. Thomas Anderson",
                department="General Surgery",
                type=ProviderType.SPECIALIST,
                specialty="Abdominal Surgery",
                bio="General surgeon specializing in laparoscopic and minimally invasive procedures",
            ),
            Provider(
                name="Dr. Linda Martinez",
                department="General Surgery",
                type=ProviderType.SPECIALIST,
                specialty="Trauma Surgery",
                bio="Trauma surgeon with expertise in emergency surgical interventions",
            ),
            Provider(
                name="Dr. Kevin O'Brien",
                department="General Surgery",
                type=ProviderType.SPECIALIST,
                specialty="Colorectal Surgery",
                bio="Colorectal surgeon specializing in bowel and rectal procedures",
            ),
            
            # Hematology (3 providers)
            Provider(
                name="Dr. Elizabeth Taylor",
                department="Hematology",
                type=ProviderType.PHYSICIAN,
                specialty="Blood Disorders",
                bio="Hematologist treating anemia, clotting disorders, and blood cancers",
            ),
            Provider(
                name="Dr. Mohammed Ali",
                department="Hematology",
                type=ProviderType.SPECIALIST,
                specialty="Bone Marrow Transplant",
                bio="Specialist in bone marrow transplantation and stem cell therapy",
            ),
            Provider(
                name="Dr. Susan Clark",
                department="Hematology",
                type=ProviderType.PHYSICIAN,
                specialty="Coagulation Disorders",
                bio="Expert in hemophilia and other bleeding disorders",
            ),
            
            # Infectious Disease (3 providers)
            Provider(
                name="Dr. David Chen",
                department="Infectious Disease",
                type=ProviderType.PHYSICIAN,
                specialty="Infectious Disease",
                bio="Infectious disease specialist treating complex infections and antimicrobial resistance",
            ),
            Provider(
                name="Dr. Sarah Johnson",
                department="Infectious Disease",
                type=ProviderType.SPECIALIST,
                specialty="HIV/AIDS Care",
                bio="HIV specialist with expertise in antiretroviral therapy",
            ),
            Provider(
                name="Dr. Mark Williams",
                department="Infectious Disease",
                type=ProviderType.PHYSICIAN,
                specialty="Travel Medicine",
                bio="Travel medicine expert providing pre-travel consultations and vaccinations",
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
            
            # Nephrology (3 providers)
            Provider(
                name="Dr. Andrew Miller",
                department="Nephrology",
                type=ProviderType.PHYSICIAN,
                specialty="Kidney Disease",
                bio="Nephrologist specializing in chronic kidney disease and dialysis",
            ),
            Provider(
                name="Dr. Jennifer Lee",
                department="Nephrology",
                type=ProviderType.SPECIALIST,
                specialty="Transplant Nephrology",
                bio="Kidney transplant specialist managing pre and post-transplant care",
            ),
            Provider(
                name="Dr. Richard Kumar",
                department="Nephrology",
                type=ProviderType.PHYSICIAN,
                specialty="Hypertension",
                bio="Expert in hypertension and its effects on kidney function",
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
            
            # Neurosurgery (3 providers)
            Provider(
                name="Dr. Christopher Adams",
                department="Neurosurgery",
                type=ProviderType.SPECIALIST,
                specialty="Brain Surgery",
                bio="Neurosurgeon specializing in brain tumor removal and complex cranial procedures",
            ),
            Provider(
                name="Dr. Michelle Turner",
                department="Neurosurgery",
                type=ProviderType.SPECIALIST,
                specialty="Spine Surgery",
                bio="Spine surgeon treating herniated discs, spinal stenosis, and scoliosis",
            ),
            Provider(
                name="Dr. Victor Petrov",
                department="Neurosurgery",
                type=ProviderType.SPECIALIST,
                specialty="Pediatric Neurosurgery",
                bio="Pediatric neurosurgeon treating congenital brain and spine conditions",
            ),
            
            # Obstetrics and Gynecology (3 providers)
            Provider(
                name="Dr. Rebecca Harris",
                department="Obstetrics and Gynecology",
                type=ProviderType.PHYSICIAN,
                specialty="Obstetrics",
                bio="OB-GYN providing comprehensive prenatal care and delivery services",
            ),
            Provider(
                name="Dr. Laura Thompson",
                department="Obstetrics and Gynecology",
                type=ProviderType.SPECIALIST,
                specialty="Gynecologic Surgery",
                bio="Gynecologic surgeon performing minimally invasive procedures",
            ),
            Provider(
                name="Dr. Angela Martinez",
                department="Obstetrics and Gynecology",
                type=ProviderType.PHYSICIAN,
                specialty="Maternal-Fetal Medicine",
                bio="High-risk pregnancy specialist managing complex obstetric cases",
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
            
            # Ophthalmology (3 providers)
            Provider(
                name="Dr. Emily Carter",
                department="Ophthalmology",
                type=ProviderType.PHYSICIAN,
                specialty="Comprehensive Eye Care",
                bio="Ophthalmologist providing comprehensive eye exams and vision correction",
            ),
            Provider(
                name="Dr. Jonathan Lee",
                department="Ophthalmology",
                type=ProviderType.SPECIALIST,
                specialty="Retina Surgery",
                bio="Retinal surgeon treating macular degeneration and diabetic retinopathy",
            ),
            Provider(
                name="Dr. Maria Santos",
                department="Ophthalmology",
                type=ProviderType.PHYSICIAN,
                specialty="Cataract Surgery",
                bio="Cataract surgeon performing advanced lens replacement procedures",
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
            
            # Otolaryngology (ENT) (3 providers)
            Provider(
                name="Dr. Robert Davis",
                department="Otolaryngology (ENT)",
                type=ProviderType.PHYSICIAN,
                specialty="Ear, Nose, and Throat",
                bio="ENT specialist treating sinus conditions, hearing loss, and throat disorders",
            ),
            Provider(
                name="Dr. Lisa Wang",
                department="Otolaryngology (ENT)",
                type=ProviderType.SPECIALIST,
                specialty="Head and Neck Surgery",
                bio="Head and neck surgeon treating tumors and complex ENT conditions",
            ),
            Provider(
                name="Dr. Michael Johnson",
                department="Otolaryngology (ENT)",
                type=ProviderType.PHYSICIAN,
                specialty="Pediatric ENT",
                bio="Pediatric ENT specialist treating ear infections and tonsil conditions",
            ),
            
            # Pathology (3 providers)
            Provider(
                name="Dr. Patricia Moore",
                department="Pathology",
                type=ProviderType.PHYSICIAN,
                specialty="Anatomic Pathology",
                bio="Pathologist specializing in tissue diagnosis and cancer detection",
            ),
            Provider(
                name="Dr. George Wilson",
                department="Pathology",
                type=ProviderType.SPECIALIST,
                specialty="Clinical Pathology",
                bio="Clinical pathologist overseeing laboratory testing and diagnostics",
            ),
            Provider(
                name="Dr. Karen Thompson",
                department="Pathology",
                type=ProviderType.PHYSICIAN,
                specialty="Molecular Pathology",
                bio="Molecular pathologist using genetic testing for disease diagnosis",
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
            
            # Physical Medicine and Rehabilitation (3 providers)
            Provider(
                name="Dr. Richard Martinez",
                department="Physical Medicine and Rehabilitation",
                type=ProviderType.PHYSICIAN,
                specialty="Rehabilitation Medicine",
                bio="Physiatrist helping patients recover from injuries and disabilities",
            ),
            Provider(
                name="Dr. Anna Kowalski",
                department="Physical Medicine and Rehabilitation",
                type=ProviderType.SPECIALIST,
                specialty="Sports Rehabilitation",
                bio="Sports medicine rehabilitation specialist for athletic injuries",
            ),
            Provider(
                name="Dr. Thomas Lee",
                department="Physical Medicine and Rehabilitation",
                type=ProviderType.PHYSICIAN,
                specialty="Pain Management",
                bio="Pain management specialist treating chronic pain conditions",
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
            
            # Pulmonology (3 providers)
            Provider(
                name="Dr. Christopher Lee",
                department="Pulmonology",
                type=ProviderType.PHYSICIAN,
                specialty="Respiratory Medicine",
                bio="Pulmonologist treating asthma, COPD, and lung infections",
            ),
            Provider(
                name="Dr. Diana Rodriguez",
                department="Pulmonology",
                type=ProviderType.SPECIALIST,
                specialty="Critical Care Pulmonology",
                bio="Intensivist managing ventilator-dependent patients",
            ),
            Provider(
                name="Dr. Frank Wilson",
                department="Pulmonology",
                type=ProviderType.PHYSICIAN,
                specialty="Sleep Medicine",
                bio="Sleep medicine specialist treating sleep apnea and sleep disorders",
            ),
            
            # Radiology (3 providers)
            Provider(
                name="Dr. Omar Nassar",
                department="Radiology",
                type=ProviderType.PHYSICIAN,
                specialty="Diagnostic Imaging",
                bio="Radiologist expert in MRI, CT, and ultrasound imaging",
            ),
            Provider(
                name="Dr. Helen Chang",
                department="Radiology",
                type=ProviderType.SPECIALIST,
                specialty="Interventional Radiology",
                bio="Interventional radiologist performing minimally invasive procedures",
            ),
            Provider(
                name="Dr. Paul Mitchell",
                department="Radiology",
                type=ProviderType.PHYSICIAN,
                specialty="Neuroradiology",
                bio="Neuroradiologist specializing in brain and spine imaging",
            ),
            
            # Rheumatology (3 providers)
            Provider(
                name="Dr. Elizabeth Harris",
                department="Rheumatology",
                type=ProviderType.PHYSICIAN,
                specialty="Autoimmune Diseases",
                bio="Rheumatologist treating rheumatoid arthritis, lupus, and autoimmune conditions",
            ),
            Provider(
                name="Dr. Nathan Green",
                department="Rheumatology",
                type=ProviderType.SPECIALIST,
                specialty="Osteoarthritis",
                bio="Joint specialist managing osteoarthritis and degenerative joint disease",
            ),
            Provider(
                name="Dr. Rachel Kim",
                department="Rheumatology",
                type=ProviderType.PHYSICIAN,
                specialty="Vasculitis",
                bio="Expert in inflammatory blood vessel disorders",
            ),
            
            # Urology (3 providers)
            Provider(
                name="Dr. Benjamin Turner",
                department="Urology",
                type=ProviderType.PHYSICIAN,
                specialty="General Urology",
                bio="Urologist treating kidney stones, prostate issues, and urinary tract conditions",
            ),
            Provider(
                name="Dr. Amanda Scott",
                department="Urology",
                type=ProviderType.SPECIALIST,
                specialty="Urologic Oncology",
                bio="Urologic oncologist specializing in bladder, kidney, and prostate cancer",
            ),
            Provider(
                name="Dr. Gregory White",
                department="Urology",
                type=ProviderType.SPECIALIST,
                specialty="Minimally Invasive Urology",
                bio="Robotic surgery specialist performing advanced urologic procedures",
            ),
            
            # Laboratory (3 providers)
            Provider(
                name="Lab Services Team A",
                department="Laboratory",
                type=ProviderType.SPECIALIST,
                specialty="Diagnostic Lab Testing",
                bio="Core laboratory team handling specimen collection and diagnostic testing",
            ),
            Provider(
                name="Lab Services Team B",
                department="Laboratory",
                type=ProviderType.SPECIALIST,
                specialty="Diagnostic Lab Testing",
                bio="Experienced technologists ensuring timely turnaround for comprehensive panels",
            ),
            Provider(
                name="Lab Services Team C",
                department="Laboratory",
                type=ProviderType.SPECIALIST,
                specialty="Diagnostic Lab Testing",
                bio="Dedicated lab technicians supporting high-volume test scheduling",
            ),
        ]

        session.add_all(providers)
        await session.commit()
        print(f"✓ Seeded {len(providers)} providers across all 25 departments (3 per department)")


async def seed_doctor_documents():
    """Seed doctor profile documents for RAG."""
    # Get all providers from database
    async with async_session_maker() as session:
        result = await session.execute(select(Provider))
        providers = result.scalars().all()
        
        if not providers:
            print("⚠ No providers found - skipping doctor document indexing")
            return
        
        # Create RAG documents for each doctor
        documents = []
        for provider in providers:
            # Build a comprehensive profile document
            content = f"""
            {provider.name} - {provider.specialty}
            Department: {provider.department}
            
            ABOUT:
            {provider.bio}
            
            SPECIALTIES:
            {provider.specialty}
            
            TYPE:
            {provider.type}
            
            To book an appointment with {provider.name}, you can search for available slots in the {provider.department} department or directly by provider ID {provider.id}.
            """
            
            documents.append(
                Document(
                    title=f"{provider.name} - {provider.specialty}",
                    content=content.strip(),
                    metadata={
                        "type": "doctor_profile",
                        "department": provider.department,
                        "specialty": provider.specialty,
                        "provider_id": str(provider.id),
                        "provider_name": provider.name,
                    },
                )
            )
        
        # Index all doctor documents (replace=True to clear old doctor profiles)
        rag_service = RAGService()
        result = await rag_service.index_documents(documents, replace=False)
        print(f"✓ Indexed {result.indexed_count} doctor profiles ({result.total_chunks} chunks)")


async def main():
    """Run provider seeding."""
    print("🌱 Seeding providers...")
    print()

    # Initialize database
    await init_db()
    print("✓ Database initialized")

    # Seed providers (will add new ones, existing ones will remain)
    await seed_providers()
    
    # Index doctor documents in RAG
    await seed_doctor_documents()

    print()
    print("✅ Provider seeding completed successfully!")
    print("   Total: 75 providers (3 per department)")


if __name__ == "__main__":
    asyncio.run(main())
