"""Seed demo data for CareConnect."""
import asyncio
import json
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import select, delete

from app.core.db import async_session_maker, init_db
from app.core.security import get_password_hash
from app.models import (
    User,
    UserRole,
    Provider,
    ProviderType,
    LabTest,
    Appointment,
    AppointmentStatus,
    AppointmentChannel,
    HandoverIncident,
    IncidentPriority,
    IncidentStatus,
)
from app.schemas.rag import Document
from app.services.rag_service import RAGService


async def clear_database():
    """Clear all seeded data from the database."""
    async with async_session_maker() as session:
        # Delete in order to respect foreign key constraints
        # Delete handover incidents first
        await session.execute(delete(HandoverIncident))
        # Delete appointments
        await session.execute(delete(Appointment))
        # Delete providers
        await session.execute(delete(Provider))
        # Delete lab tests
        await session.execute(delete(LabTest))
        # Delete non-admin users for fresh start
        await session.execute(delete(User).where(User.role != UserRole.ADMIN))
        await session.commit()
        print("✓ Cleared existing demo data from database")


async def seed_users():
    """Seed demo users - realistic patient population."""
    async with async_session_maker() as session:
        # Define all users to seed
        users_data = [
            # Main demo patient
            {
                "email": "patient@gmail.com",
                "name": "Sarah Mitchell",
                "phone": "71123456",
                "country_code": "+961",
                "role": UserRole.PATIENT,
            },
            # Additional realistic patients
            {
                "email": "ahmad.hassan@gmail.com",
                "name": "Ahmad Hassan",
                "phone": "70234567",
                "country_code": "+961",
                "role": UserRole.PATIENT,
            },
            {
                "email": "maya.khoury@hotmail.com",
                "name": "Maya Khoury",
                "phone": "76345678",
                "country_code": "+961",
                "role": UserRole.PATIENT,
            },
            {
                "email": "omar.farah@gmail.com",
                "name": "Omar Farah",
                "phone": "03456789",
                "country_code": "+961",
                "role": UserRole.PATIENT,
            },
            {
                "email": "layla.nassar@outlook.com",
                "name": "Layla Nassar",
                "phone": "71567890",
                "country_code": "+961",
                "role": UserRole.PATIENT,
            },
            {
                "email": "rami.abboud@gmail.com",
                "name": "Rami Abboud",
                "phone": "70678901",
                "country_code": "+961",
                "role": UserRole.PATIENT,
            },
            {
                "email": "nadia.saleh@yahoo.com",
                "name": "Nadia Saleh",
                "phone": "76789012",
                "country_code": "+961",
                "role": UserRole.PATIENT,
            },
            {
                "email": "khalil.hanna@gmail.com",
                "name": "Khalil Hanna",
                "phone": "03890123",
                "country_code": "+961",
                "role": UserRole.PATIENT,
            },
            {
                "email": "rita.gemayel@hotmail.com",
                "name": "Rita Gemayel",
                "phone": "71901234",
                "country_code": "+961",
                "role": UserRole.PATIENT,
            },
            {
                "email": "fadi.moussa@gmail.com",
                "name": "Fadi Moussa",
                "phone": "70012345",
                "country_code": "+961",
                "role": UserRole.PATIENT,
            },
            # Admin user
            {
                "email": "admin@aub.com",
                "name": "Dr. Administrator",
                "phone": "01350000",
                "country_code": "+961",
                "role": UserRole.ADMIN,
            },
        ]
        
        # Check existing users
        all_emails = [u["email"] for u in users_data]
        result = await session.execute(
            select(User).where(User.email.in_(all_emails))
        )
        existing_users = result.scalars().all()
        existing_emails = {user.email for user in existing_users}
        
        users_to_add = []
        for user_data in users_data:
            if user_data["email"] not in existing_emails:
                users_to_add.append(
                    User(
                        email=user_data["email"],
                        name=user_data["name"],
                        phone=user_data["phone"],
                        country_code=user_data["country_code"],
                        role=user_data["role"],
                        hashed_password=get_password_hash("password123" if user_data["role"] == UserRole.PATIENT else "Admin@123"),
                    )
                )
        
        if users_to_add:
            session.add_all(users_to_add)
            await session.commit()
            print(f"✓ Seeded {len(users_to_add)} users (10 patients + 1 admin)")
        else:
            print(f"✓ Users already exist, skipped seeding")


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
                bio="Fellowship-trained interventional cardiologist performing cardiac catheterizations, stent placements, and complex coronary interventions. Dedicated to providing cutting-edge heart care.",
            ),
            Provider(
                name="Dr. Marcus Webb",
                department="Cardiology",
                type=ProviderType.PHYSICIAN,
                specialty="Electrophysiology",
                bio="Cardiac electrophysiologist with expertise in diagnosing and treating heart rhythm disorders. Performs pacemaker and defibrillator implantations with precision and care.",
            ),
            Provider(
                name="Dr. Lisa Chen",
                department="Cardiology",
                type=ProviderType.SPECIALIST,
                specialty="Heart Failure",
                bio="Heart failure specialist focused on advanced cardiac therapies and helping patients manage complex heart conditions to improve quality of life.",
            ),
            
            # Dermatology (3 providers)
            Provider(
                name="Dr. Jennifer Wong",
                department="Dermatology",
                type=ProviderType.PHYSICIAN,
                specialty="Medical Dermatology",
                bio="Board-certified dermatologist treating a wide range of skin conditions including acne, eczema, psoriasis, and skin cancer screenings. Passionate about healthy skin for all ages.",
            ),
            Provider(
                name="Dr. Alexander Petrov",
                department="Dermatology",
                type=ProviderType.SPECIALIST,
                specialty="Cosmetic Dermatology",
                bio="Expert in aesthetic dermatology offering Botox, fillers, laser treatments, and personalized anti-aging solutions to help patients look and feel their best.",
            ),
            Provider(
                name="Dr. Rachel Martinez",
                department="Dermatology",
                type=ProviderType.PHYSICIAN,
                specialty="Pediatric Dermatology",
                bio="Pediatric dermatologist specializing in children's skin health, from birthmarks and rashes to eczema and genetic skin conditions. Gentle care for young patients.",
            ),
            
            # Emergency Medicine (3 providers)
            Provider(
                name="Dr. Robert Thompson",
                department="Emergency Medicine",
                type=ProviderType.PHYSICIAN,
                specialty="Trauma Care",
                bio="Board-certified emergency physician with Level 1 trauma center experience. Skilled in rapid assessment and life-saving interventions for critical patients.",
            ),
            Provider(
                name="Dr. Samantha Lee",
                department="Emergency Medicine",
                type=ProviderType.PHYSICIAN,
                specialty="Critical Care",
                bio="Emergency medicine physician with additional training in critical care. Expert in managing severely ill patients and coordinating complex resuscitations.",
            ),
            Provider(
                name="Dr. Carlos Ramirez",
                department="Emergency Medicine",
                type=ProviderType.PHYSICIAN,
                specialty="Pediatric Emergency",
                bio="Emergency physician with specialized training in pediatric emergencies. Compassionate care for children and families during stressful medical situations.",
            ),
            
            # Endocrinology (3 providers)
            Provider(
                name="Dr. Patricia Singh",
                department="Endocrinology",
                type=ProviderType.PHYSICIAN,
                specialty="Diabetes Care",
                bio="Endocrinologist dedicated to comprehensive diabetes management including insulin pump therapy, CGM technology, and personalized treatment plans for optimal glucose control.",
            ),
            Provider(
                name="Dr. Daniel Kim",
                department="Endocrinology",
                type=ProviderType.SPECIALIST,
                specialty="Thyroid Disorders",
                bio="Thyroid specialist with expertise in diagnosing and treating hypothyroidism, hyperthyroidism, thyroid nodules, and thyroid cancer. Uses advanced ultrasound diagnostics.",
            ),
            Provider(
                name="Dr. Maria Gonzalez",
                department="Endocrinology",
                type=ProviderType.PHYSICIAN,
                specialty="Metabolic Disorders",
                bio="Endocrinologist specializing in metabolic syndrome, obesity medicine, and hormonal imbalances. Focuses on holistic approaches to restore hormonal health.",
            ),
            
            # Gastroenterology (3 providers)
            Provider(
                name="Dr. James Wilson",
                department="Gastroenterology",
                type=ProviderType.PHYSICIAN,
                specialty="Digestive Disorders",
                bio="Gastroenterologist treating IBS, inflammatory bowel disease, GERD, and other digestive conditions. Committed to improving gut health through evidence-based care.",
            ),
            Provider(
                name="Dr. Amy Nguyen",
                department="Gastroenterology",
                type=ProviderType.SPECIALIST,
                specialty="Hepatology",
                bio="Liver specialist treating hepatitis, cirrhosis, fatty liver disease, and liver cancer. Provides comprehensive care from diagnosis through transplant evaluation.",
            ),
            Provider(
                name="Dr. Steven Brown",
                department="Gastroenterology",
                type=ProviderType.PHYSICIAN,
                specialty="Therapeutic Endoscopy",
                bio="Advanced endoscopist performing colonoscopies, upper endoscopies, and complex therapeutic procedures including polyp removal and stent placement.",
            ),
            
            # General Surgery (3 providers)
            Provider(
                name="Dr. Thomas Anderson",
                department="General Surgery",
                type=ProviderType.SPECIALIST,
                specialty="Minimally Invasive Surgery",
                bio="General surgeon specializing in laparoscopic and robotic surgery for gallbladder, hernia, and abdominal conditions. Faster recovery through smaller incisions.",
            ),
            Provider(
                name="Dr. Linda Martinez",
                department="General Surgery",
                type=ProviderType.SPECIALIST,
                specialty="Trauma Surgery",
                bio="Trauma and acute care surgeon providing emergency surgical interventions. Experienced in managing complex injuries and critical surgical conditions.",
            ),
            Provider(
                name="Dr. Kevin O'Brien",
                department="General Surgery",
                type=ProviderType.SPECIALIST,
                specialty="Colorectal Surgery",
                bio="Colorectal surgeon treating colon cancer, diverticulitis, and inflammatory bowel disease. Expert in both open and minimally invasive techniques.",
            ),
            
            # Hematology (3 providers)
            Provider(
                name="Dr. Elizabeth Taylor",
                department="Hematology",
                type=ProviderType.PHYSICIAN,
                specialty="Blood Disorders",
                bio="Hematologist treating anemia, clotting disorders, and benign blood conditions. Provides thorough diagnostic workups and personalized treatment plans.",
            ),
            Provider(
                name="Dr. Mohammed Ali",
                department="Hematology",
                type=ProviderType.SPECIALIST,
                specialty="Bone Marrow Transplant",
                bio="Transplant hematologist specializing in bone marrow and stem cell transplantation for blood cancers and severe blood disorders. Leader in cellular therapy.",
            ),
            Provider(
                name="Dr. Susan Clark",
                department="Hematology",
                type=ProviderType.PHYSICIAN,
                specialty="Coagulation Disorders",
                bio="Expert in bleeding and clotting disorders including hemophilia, von Willebrand disease, and thrombophilia. Provides comprehensive coagulation management.",
            ),
            
            # Infectious Disease (3 providers)
            Provider(
                name="Dr. David Chen",
                department="Infectious Disease",
                type=ProviderType.PHYSICIAN,
                specialty="Complex Infections",
                bio="Infectious disease specialist treating complex bacterial, viral, and fungal infections. Expert in antibiotic stewardship and antimicrobial resistance.",
            ),
            Provider(
                name="Dr. Aisha Patel",
                department="Infectious Disease",
                type=ProviderType.SPECIALIST,
                specialty="HIV/AIDS Care",
                bio="HIV specialist providing comprehensive care including antiretroviral therapy, prevention strategies, and support for patients living with HIV.",
            ),
            Provider(
                name="Dr. Mark Williams",
                department="Infectious Disease",
                type=ProviderType.PHYSICIAN,
                specialty="Travel Medicine",
                bio="Travel medicine expert offering pre-travel consultations, vaccinations, and post-travel illness evaluation. Helps travelers stay healthy worldwide.",
            ),
            
            # Internal Medicine (3 providers)
            Provider(
                name="Dr. Maria Rodriguez",
                department="Internal Medicine",
                type=ProviderType.PHYSICIAN,
                specialty="Primary Care",
                bio="Internist providing comprehensive adult primary care with focus on preventive medicine, chronic disease management, and building lasting patient relationships.",
            ),
            Provider(
                name="Dr. John Davis",
                department="Internal Medicine",
                type=ProviderType.PHYSICIAN,
                specialty="Geriatric Medicine",
                bio="Geriatrician specializing in the unique healthcare needs of older adults. Expert in managing multiple conditions, medications, and promoting healthy aging.",
            ),
            Provider(
                name="Emily Watson, NP",
                department="Internal Medicine",
                type=ProviderType.NURSE_PRACTITIONER,
                specialty="Adult Primary Care",
                bio="Nurse practitioner focused on preventive care, health screenings, and chronic disease management. Partners with patients for optimal wellness.",
            ),
            
            # Nephrology (3 providers)
            Provider(
                name="Dr. Andrew Miller",
                department="Nephrology",
                type=ProviderType.PHYSICIAN,
                specialty="Chronic Kidney Disease",
                bio="Nephrologist specializing in chronic kidney disease management, slowing progression, and preparing patients for dialysis or transplant when needed.",
            ),
            Provider(
                name="Dr. Jennifer Lee",
                department="Nephrology",
                type=ProviderType.SPECIALIST,
                specialty="Transplant Nephrology",
                bio="Transplant nephrologist managing kidney transplant patients before and after surgery. Dedicated to maximizing transplant success and longevity.",
            ),
            Provider(
                name="Dr. Richard Kumar",
                department="Nephrology",
                type=ProviderType.PHYSICIAN,
                specialty="Hypertensive Kidney Disease",
                bio="Expert in hypertension and its effects on kidney function. Specializes in resistant hypertension and renovascular disease management.",
            ),
            
            # Neurology (3 providers)
            Provider(
                name="Dr. Ahmed Hassan",
                department="Neurology",
                type=ProviderType.PHYSICIAN,
                specialty="Stroke Care",
                bio="Vascular neurologist specializing in stroke prevention, acute stroke treatment, and recovery. Certified in advanced stroke interventions.",
            ),
            Provider(
                name="Dr. Catherine White",
                department="Neurology",
                type=ProviderType.SPECIALIST,
                specialty="Epilepsy",
                bio="Epileptologist managing seizure disorders with the latest medications and advanced therapies including surgical options for drug-resistant epilepsy.",
            ),
            Provider(
                name="Dr. Brian Foster",
                department="Neurology",
                type=ProviderType.PHYSICIAN,
                specialty="Movement Disorders",
                bio="Movement disorder specialist treating Parkinson's disease, tremors, and dystonia. Offers deep brain stimulation programming and Botox therapy.",
            ),
            
            # Neurosurgery (3 providers)
            Provider(
                name="Dr. Christopher Adams",
                department="Neurosurgery",
                type=ProviderType.SPECIALIST,
                specialty="Brain Tumor Surgery",
                bio="Neurosurgeon specializing in brain tumor removal using advanced imaging guidance and microsurgical techniques for optimal outcomes.",
            ),
            Provider(
                name="Dr. Michelle Turner",
                department="Neurosurgery",
                type=ProviderType.SPECIALIST,
                specialty="Spine Surgery",
                bio="Spine surgeon treating herniated discs, spinal stenosis, and deformities. Expert in minimally invasive and complex reconstructive spine procedures.",
            ),
            Provider(
                name="Dr. Victor Petrov",
                department="Neurosurgery",
                type=ProviderType.SPECIALIST,
                specialty="Pediatric Neurosurgery",
                bio="Pediatric neurosurgeon treating congenital brain and spine conditions in children. Gentle approach with focus on long-term developmental outcomes.",
            ),
            
            # Obstetrics and Gynecology (3 providers)
            Provider(
                name="Dr. Rebecca Harris",
                department="Obstetrics and Gynecology",
                type=ProviderType.PHYSICIAN,
                specialty="Obstetrics",
                bio="OB-GYN providing comprehensive prenatal care, labor and delivery, and postpartum support. Dedicated to healthy pregnancies and positive birth experiences.",
            ),
            Provider(
                name="Dr. Laura Thompson",
                department="Obstetrics and Gynecology",
                type=ProviderType.SPECIALIST,
                specialty="Gynecologic Surgery",
                bio="Gynecologic surgeon performing minimally invasive hysterectomies, myomectomies, and endometriosis surgery with focus on fertility preservation.",
            ),
            Provider(
                name="Dr. Angela Martinez",
                department="Obstetrics and Gynecology",
                type=ProviderType.PHYSICIAN,
                specialty="Maternal-Fetal Medicine",
                bio="Perinatologist managing high-risk pregnancies including multiple gestations, preeclampsia, and fetal abnormalities with expert care and monitoring.",
            ),
            
            # Oncology (3 providers)
            Provider(
                name="Dr. David Park",
                department="Oncology",
                type=ProviderType.SPECIALIST,
                specialty="Medical Oncology",
                bio="Medical oncologist providing chemotherapy, immunotherapy, and targeted therapies. Partners with patients through every step of their cancer journey.",
            ),
            Provider(
                name="Dr. Susan Anderson",
                department="Oncology",
                type=ProviderType.PHYSICIAN,
                specialty="Radiation Oncology",
                bio="Radiation oncologist using advanced techniques including IMRT and stereotactic radiosurgery to target tumors precisely while protecting healthy tissue.",
            ),
            Provider(
                name="Dr. Peter Chang",
                department="Oncology",
                type=ProviderType.SPECIALIST,
                specialty="Hematologic Oncology",
                bio="Hematologic oncologist treating leukemia, lymphoma, and myeloma with cutting-edge therapies including CAR-T cell therapy and clinical trials.",
            ),
            
            # Ophthalmology (3 providers)
            Provider(
                name="Dr. Emily Carter",
                department="Ophthalmology",
                type=ProviderType.PHYSICIAN,
                specialty="Comprehensive Eye Care",
                bio="Ophthalmologist providing complete eye exams, glaucoma management, and vision correction. Committed to preserving and improving patients' sight.",
            ),
            Provider(
                name="Dr. Jonathan Lee",
                department="Ophthalmology",
                type=ProviderType.SPECIALIST,
                specialty="Retina Surgery",
                bio="Vitreoretinal surgeon treating macular degeneration, diabetic retinopathy, and retinal detachments with advanced surgical and injection therapies.",
            ),
            Provider(
                name="Dr. Maria Santos",
                department="Ophthalmology",
                type=ProviderType.PHYSICIAN,
                specialty="Cataract Surgery",
                bio="Cataract surgeon performing advanced lens replacement including premium IOLs for reduced dependence on glasses after surgery.",
            ),
            
            # Orthopedics (3 providers)
            Provider(
                name="Dr. James Chen",
                department="Orthopedics",
                type=ProviderType.SPECIALIST,
                specialty="Sports Medicine",
                bio="Sports medicine orthopedist treating ACL tears, rotator cuff injuries, and athletic conditions. Gets athletes back to peak performance safely.",
            ),
            Provider(
                name="Dr. William Brown",
                department="Orthopedics",
                type=ProviderType.SPECIALIST,
                specialty="Joint Replacement",
                bio="Joint replacement surgeon performing hip, knee, and shoulder arthroplasty. Uses latest implant technology for improved mobility and reduced pain.",
            ),
            Provider(
                name="Dr. Nicole Garcia",
                department="Orthopedics",
                type=ProviderType.PHYSICIAN,
                specialty="Pediatric Orthopedics",
                bio="Pediatric orthopedist treating fractures, scoliosis, and developmental conditions in children. Specialized care for growing bones and joints.",
            ),
            
            # Otolaryngology (ENT) (3 providers)
            Provider(
                name="Dr. Robert Davis",
                department="Otolaryngology (ENT)",
                type=ProviderType.PHYSICIAN,
                specialty="General ENT",
                bio="ENT physician treating sinus disorders, hearing loss, and throat conditions. Offers both medical management and surgical solutions.",
            ),
            Provider(
                name="Dr. Lisa Wang",
                department="Otolaryngology (ENT)",
                type=ProviderType.SPECIALIST,
                specialty="Head and Neck Surgery",
                bio="Head and neck surgeon treating thyroid nodules, salivary gland tumors, and throat cancers with expertise in reconstructive techniques.",
            ),
            Provider(
                name="Dr. Michael Johnson",
                department="Otolaryngology (ENT)",
                type=ProviderType.PHYSICIAN,
                specialty="Pediatric ENT",
                bio="Pediatric ENT specialist treating ear infections, tonsillitis, and airway problems in children with a gentle, kid-friendly approach.",
            ),
            
            # Pathology (3 providers)
            Provider(
                name="Dr. Patricia Moore",
                department="Pathology",
                type=ProviderType.PHYSICIAN,
                specialty="Surgical Pathology",
                bio="Surgical pathologist providing accurate tissue diagnoses for cancer and other conditions. Expert in frozen sections and consultation services.",
            ),
            Provider(
                name="Dr. George Wilson",
                department="Pathology",
                type=ProviderType.SPECIALIST,
                specialty="Clinical Pathology",
                bio="Clinical pathologist overseeing laboratory operations and ensuring accurate, timely test results. Leader in quality assurance and lab diagnostics.",
            ),
            Provider(
                name="Dr. Karen Thompson",
                department="Pathology",
                type=ProviderType.PHYSICIAN,
                specialty="Molecular Pathology",
                bio="Molecular pathologist using genetic and genomic testing to guide personalized cancer treatment and diagnose inherited conditions.",
            ),
            
            # Pediatrics (3 providers)
            Provider(
                name="Dr. Emily Taylor",
                department="Pediatrics",
                type=ProviderType.PHYSICIAN,
                specialty="General Pediatrics",
                bio="Pediatrician providing well-child care, immunizations, and illness management from newborn through adolescence. Partner in your child's health journey.",
            ),
            Provider(
                name="Dr. Samuel Green",
                department="Pediatrics",
                type=ProviderType.SPECIALIST,
                specialty="Pediatric Critical Care",
                bio="Pediatric intensivist caring for critically ill children in the ICU. Expert in complex medical management and life-saving interventions.",
            ),
            Provider(
                name="Dr. Jennifer Adams",
                department="Pediatrics",
                type=ProviderType.PHYSICIAN,
                specialty="Developmental Pediatrics",
                bio="Developmental pediatrician evaluating and treating ADHD, autism, and developmental delays. Helps children reach their full potential.",
            ),
            
            # Physical Medicine and Rehabilitation (3 providers)
            Provider(
                name="Dr. Richard Martinez",
                department="Physical Medicine and Rehabilitation",
                type=ProviderType.PHYSICIAN,
                specialty="Rehabilitation Medicine",
                bio="Physiatrist helping patients recover function after stroke, spinal cord injury, and brain injury. Focuses on maximizing independence and quality of life.",
            ),
            Provider(
                name="Dr. Anna Kowalski",
                department="Physical Medicine and Rehabilitation",
                type=ProviderType.SPECIALIST,
                specialty="Sports Rehabilitation",
                bio="Sports medicine physiatrist treating athletic injuries without surgery when possible. Uses injections, therapy, and innovative treatments for recovery.",
            ),
            Provider(
                name="Dr. Thomas Liu",
                department="Physical Medicine and Rehabilitation",
                type=ProviderType.PHYSICIAN,
                specialty="Pain Management",
                bio="Interventional pain specialist treating chronic back pain, neck pain, and joint pain with injections, nerve blocks, and comprehensive pain programs.",
            ),
            
            # Psychiatry (3 providers)
            Provider(
                name="Dr. Sophia Anderson",
                department="Psychiatry",
                type=ProviderType.PHYSICIAN,
                specialty="Adult Psychiatry",
                bio="Psychiatrist treating depression, anxiety, bipolar disorder, and other mental health conditions with medication management and supportive therapy.",
            ),
            Provider(
                name="Dr. Nathan Reynolds",
                department="Psychiatry",
                type=ProviderType.SPECIALIST,
                specialty="Child & Adolescent Psychiatry",
                bio="Child psychiatrist specializing in ADHD, anxiety, depression, and behavioral issues in children and teens. Family-centered approach to mental wellness.",
            ),
            Provider(
                name="Dr. Jessica Brown",
                department="Psychiatry",
                type=ProviderType.PHYSICIAN,
                specialty="Addiction Psychiatry",
                bio="Addiction psychiatrist treating substance use disorders with evidence-based medications and therapy. Compassionate support for recovery.",
            ),
            
            # Pulmonology (3 providers)
            Provider(
                name="Dr. Christopher Lee",
                department="Pulmonology",
                type=ProviderType.PHYSICIAN,
                specialty="Respiratory Medicine",
                bio="Pulmonologist treating asthma, COPD, and interstitial lung disease. Uses advanced diagnostics including bronchoscopy and pulmonary function testing.",
            ),
            Provider(
                name="Dr. Diana Rodriguez",
                department="Pulmonology",
                type=ProviderType.SPECIALIST,
                specialty="Critical Care Pulmonology",
                bio="Pulmonary critical care physician managing respiratory failure and ventilator-dependent patients. Expert in ICU care and lung recovery.",
            ),
            Provider(
                name="Dr. Frank Wilson",
                department="Pulmonology",
                type=ProviderType.PHYSICIAN,
                specialty="Sleep Medicine",
                bio="Sleep medicine specialist diagnosing and treating sleep apnea, insomnia, and other sleep disorders. Helps patients achieve restful, healthy sleep.",
            ),
            
            # Radiology (3 providers)
            Provider(
                name="Dr. Omar Nassar",
                department="Radiology",
                type=ProviderType.PHYSICIAN,
                specialty="Diagnostic Imaging",
                bio="Diagnostic radiologist interpreting MRI, CT, ultrasound, and X-ray studies. Provides timely, accurate imaging interpretation for clinical teams.",
            ),
            Provider(
                name="Dr. Helen Chang",
                department="Radiology",
                type=ProviderType.SPECIALIST,
                specialty="Interventional Radiology",
                bio="Interventional radiologist performing minimally invasive image-guided procedures including biopsies, drain placements, and vascular interventions.",
            ),
            Provider(
                name="Dr. Paul Mitchell",
                department="Radiology",
                type=ProviderType.PHYSICIAN,
                specialty="Neuroradiology",
                bio="Neuroradiologist specialized in brain and spine imaging. Expert in diagnosing strokes, tumors, and neurological conditions.",
            ),
            
            # Rheumatology (3 providers)
            Provider(
                name="Dr. Elizabeth Harris",
                department="Rheumatology",
                type=ProviderType.PHYSICIAN,
                specialty="Autoimmune Diseases",
                bio="Rheumatologist treating rheumatoid arthritis, lupus, and autoimmune conditions with the latest biologic therapies and personalized care plans.",
            ),
            Provider(
                name="Dr. Nathan Green",
                department="Rheumatology",
                type=ProviderType.SPECIALIST,
                specialty="Osteoarthritis",
                bio="Rheumatologist specializing in osteoarthritis and degenerative joint disease. Offers joint injections and comprehensive management strategies.",
            ),
            Provider(
                name="Dr. Rachel Kim",
                department="Rheumatology",
                type=ProviderType.PHYSICIAN,
                specialty="Vasculitis",
                bio="Expert in inflammatory blood vessel disorders including giant cell arteritis and ANCA vasculitis. Skilled in complex immunosuppressive management.",
            ),
            
            # Urology (3 providers)
            Provider(
                name="Dr. Benjamin Turner",
                department="Urology",
                type=ProviderType.PHYSICIAN,
                specialty="General Urology",
                bio="Urologist treating kidney stones, enlarged prostate, and urinary conditions. Offers both medical and surgical treatment options.",
            ),
            Provider(
                name="Dr. Amanda Scott",
                department="Urology",
                type=ProviderType.SPECIALIST,
                specialty="Urologic Oncology",
                bio="Urologic oncologist specializing in bladder, kidney, and prostate cancer. Performs robotic surgery and coordinates multidisciplinary cancer care.",
            ),
            Provider(
                name="Dr. Gregory White",
                department="Urology",
                type=ProviderType.SPECIALIST,
                specialty="Minimally Invasive Urology",
                bio="Robotic surgery specialist performing advanced urologic procedures with smaller incisions, less pain, and faster recovery times.",
            ),
            
            # Laboratory (3 providers for lab test appointments - named generically for patient convenience)
            Provider(
                name="Laboratory Services",
                department="Laboratory",
                type=ProviderType.SPECIALIST,
                specialty="Diagnostic Lab Testing",
                bio="Our laboratory team handles specimen collection and diagnostic testing including blood work, urinalysis, and comprehensive metabolic panels. Available for CBC, lipid panels, thyroid tests, and more.",
            ),
            Provider(
                name="Laboratory Services - Morning",
                department="Laboratory",
                type=ProviderType.SPECIALIST,
                specialty="Diagnostic Lab Testing",
                bio="Morning laboratory services ensuring timely turnaround for fasting tests like lipid profiles, glucose tests, and metabolic panels.",
            ),
            Provider(
                name="Laboratory Services - Afternoon",
                department="Laboratory",
                type=ProviderType.SPECIALIST,
                specialty="Diagnostic Lab Testing",
                bio="Afternoon laboratory services for non-fasting tests including CBC, A1C, liver function tests, and other routine laboratory services.",
            ),
        ]

        session.add_all(providers)
        await session.commit()
        print(f"✓ Seeded {len(providers)} providers across all departments")


async def seed_lab_tests():
    """Seed demo lab tests."""
    async with async_session_maker() as session:
        desired_tests = {
            "LAB-CBC": dict(
                name="Complete Blood Count (CBC)",
                department="Laboratory",
                description="Measures different components of blood including red and white blood cells",
                prep_instructions="No special preparation required",
                fasting_hours=None,
                estimated_duration_minutes=15,
            ),
            "LAB-LIPID": dict(
                name="Lipid Panel",
                department="Laboratory",
                description="Measures cholesterol and triglyceride levels",
                prep_instructions="Fasting required before test",
                fasting_hours=12,
                estimated_duration_minutes=15,
            ),
            "LAB-THYROID": dict(
                name="Thyroid Function Test",
                department="Laboratory",
                description="Measures thyroid hormone levels (TSH, T3, T4)",
                prep_instructions="No special preparation required",
                fasting_hours=None,
                estimated_duration_minutes=15,
            ),
            "LAB-A1C": dict(
                name="Hemoglobin A1C",
                department="Laboratory",
                description="Measures average blood sugar levels over 3 months",
                prep_instructions="No fasting required",
                fasting_hours=None,
                estimated_duration_minutes=15,
            ),
            "LAB-CMP": dict(
                name="Comprehensive Metabolic Panel",
                department="Laboratory",
                description="Measures kidney function, blood sugar, and electrolytes",
                prep_instructions="Fasting recommended",
                fasting_hours=8,
                estimated_duration_minutes=15,
            ),
            "LAB-LFT": dict(
                name="Liver Function Test",
                department="Laboratory",
                description="Evaluates liver health and function",
                prep_instructions="No special preparation required",
                fasting_hours=None,
                estimated_duration_minutes=15,
            ),
            "LAB-UA": dict(
                name="Urinalysis",
                department="Laboratory",
                description="Analyzes urine for various health indicators",
                prep_instructions="First morning urine sample preferred",
                fasting_hours=None,
                estimated_duration_minutes=10,
            ),
            "RAD-XR": dict(
                name="X-Ray",
                department="Radiology",
                description="Imaging of requested body part",
                prep_instructions="Remove jewelry and metal objects",
                fasting_hours=None,
                estimated_duration_minutes=30,
            ),
            "RAD-MRI": dict(
                name="MRI Scan",
                department="Radiology",
                description="Detailed imaging using magnetic resonance",
                prep_instructions="Remove all metal objects; inform staff of implants",
                fasting_hours=None,
                estimated_duration_minutes=30,
            )
        }

        # Add all lab tests (database was cleared first)
        lab_tests = [
            LabTest(code=code, **data)
            for code, data in desired_tests.items()
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
    print(f"✓ Indexed {result.indexed_count} facility documents ({result.total_chunks} chunks)")


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
            # Handle provider.type which may be enum or string
            provider_type = provider.type.value if hasattr(provider.type, 'value') else str(provider.type)
            
            # Build a comprehensive profile document
            content = f"""
            {provider.name} - {provider.specialty}
            Department: {provider.department}
            
            ABOUT:
            {provider.bio}
            
            SPECIALTIES:
            {provider.specialty}
            
            TYPE:
            {provider_type}
            
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
        
        # Index all doctor documents
        rag_service = RAGService()
        result = await rag_service.index_documents(documents, replace=False)
        print(f"✓ Indexed {result.indexed_count} doctor profiles ({result.total_chunks} chunks)")


async def seed_lab_test_documents():
    """Seed lab test preparation documents for RAG."""
    from scripts.populate_lab_tests import LAB_TESTS, generate_lab_test_pdf
    from app.services.pdf_parser import PDFParser
    
    print("Generating lab test preparation documents...")
    
    rag_service = RAGService()
    pdf_parser = PDFParser()
    
    # Create documents from lab test PDFs
    documents = []
    
    for test_name, test_info in LAB_TESTS.items():
        # Generate PDF
        pdf_bytes = generate_lab_test_pdf(test_name, test_info)
        
        # Extract text from PDF
        pdf_text = pdf_parser.extract_text_from_bytes(pdf_bytes)
        
        # Create Document object
        documents.append(
            Document(
                title=test_name,
                content=pdf_text,
                metadata={
                    "type": "lab_test_prep",
                    "category": test_info["category"],
                    "test_name": test_name,
                },
            )
        )
    
    # Index all lab test documents
    result = await rag_service.index_documents(documents, replace=False)
    print(f"✓ Indexed {len(LAB_TESTS)} lab test documents ({result.total_chunks} chunks)")


async def seed_patient_test_results():
    """Seed sample patient test results for the demo user."""
    from datetime import datetime, timezone, timedelta
    from io import BytesIO
    from app.models import PatientTestResult
    
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    except ImportError:
        print("⚠ reportlab not installed, skipping test result PDF generation")
        return
    
    print("Seeding patient test results...")
    
    async with async_session_maker() as session:
        # Get the demo patient user
        result = await session.execute(
            select(User).where(User.email == "patient@gmail.com")
        )
        patient = result.scalar_one_or_none()
        
        if not patient:
            print("⚠ Demo patient not found, skipping test results")
            return
        
        # Get a provider for ordering
        provider_result = await session.execute(
            select(Provider).where(Provider.department == "Internal Medicine").limit(1)
        )
        provider = provider_result.scalar_one_or_none()
        
        def generate_test_result_pdf(test_name: str, result_value: str, unit: str, reference: str, notes: str) -> bytes:
            """Generate a sample test result PDF."""
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#840132'),
                spaceAfter=20,
            )
            story.append(Paragraph("AUB Medical Center", title_style))
            story.append(Paragraph("Laboratory Test Report", styles['Heading2']))
            story.append(Spacer(1, 20))
            
            # Patient Info
            story.append(Paragraph(f"<b>Patient:</b> {patient.name}", styles['Normal']))
            story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Test Results Table
            data = [
                ['Test Name', 'Result', 'Unit', 'Reference Range'],
                [test_name, result_value, unit, reference],
            ]
            table = Table(data, colWidths=[180, 100, 80, 140])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#840132')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f5f5')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dddddd')),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 11),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ]))
            story.append(table)
            story.append(Spacer(1, 20))
            
            # Notes
            if notes:
                story.append(Paragraph("<b>Notes:</b>", styles['Normal']))
                story.append(Paragraph(notes, styles['Normal']))
            
            story.append(Spacer(1, 30))
            story.append(Paragraph("This is an official laboratory report from AUB Medical Center.", styles['Normal']))
            
            doc.build(story)
            return buffer.getvalue()
        
        # Sample test results
        test_results_data = [
            {
                "test_name": "Complete Blood Count (CBC)",
                "test_category": "Blood",
                "test_date": datetime.now(timezone.utc) - timedelta(days=7),
                "result_value": "14.2",
                "result_unit": "g/dL",
                "reference_range": "12.0 - 16.0 g/dL",
                "status": "completed",
                "notes": "Hemoglobin levels are within normal range. All blood cell counts are healthy.",
            },
            {
                "test_name": "Lipid Panel",
                "test_category": "Blood",
                "test_date": datetime.now(timezone.utc) - timedelta(days=14),
                "result_value": "185",
                "result_unit": "mg/dL",
                "reference_range": "< 200 mg/dL",
                "status": "completed",
                "notes": "Total cholesterol is within healthy limits. Continue current diet and exercise regimen.",
            },
            {
                "test_name": "Thyroid Function Test (TSH)",
                "test_category": "Blood",
                "test_date": datetime.now(timezone.utc) - timedelta(days=21),
                "result_value": "2.5",
                "result_unit": "mIU/L",
                "reference_range": "0.4 - 4.0 mIU/L",
                "status": "reviewed",
                "notes": "Thyroid function is normal. No thyroid medication adjustment needed.",
            },
            {
                "test_name": "Chest X-Ray",
                "test_category": "Imaging",
                "test_date": datetime.now(timezone.utc) - timedelta(days=30),
                "result_value": "Normal",
                "result_unit": "",
                "reference_range": "No abnormalities",
                "status": "completed",
                "notes": "Lungs are clear. Heart size is normal. No evidence of pneumonia or other abnormalities.",
            },
            {
                "test_name": "HbA1c (Glycated Hemoglobin)",
                "test_category": "Blood",
                "test_date": datetime.now(timezone.utc) - timedelta(days=45),
                "result_value": "5.4",
                "result_unit": "%",
                "reference_range": "< 5.7%",
                "status": "reviewed",
                "notes": "Blood sugar control is excellent. No signs of diabetes or pre-diabetes.",
            },
        ]
        
        for test_data in test_results_data:
            # Generate PDF
            pdf_data = generate_test_result_pdf(
                test_data["test_name"],
                test_data["result_value"],
                test_data["result_unit"],
                test_data["reference_range"],
                test_data["notes"],
            )
            
            test_result = PatientTestResult(
                user_id=patient.id,
                ordered_by_provider_id=provider.id if provider else None,
                test_name=test_data["test_name"],
                test_category=test_data["test_category"],
                test_date=test_data["test_date"],
                result_value=test_data["result_value"],
                result_unit=test_data["result_unit"],
                reference_range=test_data["reference_range"],
                status=test_data["status"],
                notes=test_data["notes"],
                pdf_data=pdf_data,
                pdf_filename=f"{test_data['test_name'].replace(' ', '_').replace('(', '').replace(')', '')}_Report.pdf",
            )
            session.add(test_result)
        
        await session.commit()
        print(f"✓ Seeded {len(test_results_data)} test results for demo patient")


def generate_confirmation_code():
    """Generate a realistic confirmation code."""
    import string
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=8))


async def seed_appointments():
    """Seed realistic appointment history for all patients."""
    print("Seeding appointment history...")
    
    async with async_session_maker() as session:
        # Get all patients
        result = await session.execute(
            select(User).where(User.role == UserRole.PATIENT)
        )
        patients = result.scalars().all()
        
        # Get all providers
        result = await session.execute(select(Provider))
        providers = result.scalars().all()
        
        if not patients or not providers:
            print("⚠ No patients or providers found, skipping appointments")
            return
        
        # Group providers by department for realistic booking
        providers_by_dept = {}
        for p in providers:
            if p.department not in providers_by_dept:
                providers_by_dept[p.department] = []
            providers_by_dept[p.department].append(p)
        
        appointments = []
        now = datetime.now(timezone.utc)
        
        # Appointment reasons by department
        reasons = {
            "Cardiology": ["Annual heart checkup", "Follow-up for blood pressure", "Chest discomfort evaluation", "ECG review"],
            "Dermatology": ["Skin rash examination", "Mole check", "Acne treatment follow-up", "Annual skin screening"],
            "Orthopedics": ["Knee pain consultation", "Back pain evaluation", "Sports injury follow-up", "Joint stiffness"],
            "Internal Medicine": ["Annual physical", "Flu symptoms", "General checkup", "Fatigue evaluation"],
            "Neurology": ["Headache consultation", "Migraine follow-up", "Numbness evaluation", "Sleep issues"],
            "Gastroenterology": ["Stomach pain", "Digestive issues", "GERD follow-up", "Colonoscopy prep"],
            "Ophthalmology": ["Eye exam", "Vision check", "Glasses prescription", "Eye strain"],
            "Pulmonology": ["Breathing difficulty", "Asthma follow-up", "Cough evaluation", "Sleep apnea check"],
            "Endocrinology": ["Diabetes management", "Thyroid follow-up", "Hormone evaluation", "Weight management"],
            "Laboratory": ["Blood work", "Annual lab tests", "Lipid panel", "CBC test"],
        }
        
        # Create appointments for each patient
        for patient in patients:
            # Main demo patient (patient@gmail.com) gets more appointments
            is_main_patient = patient.email == "patient@gmail.com"
            num_past = random.randint(5, 8) if is_main_patient else random.randint(1, 4)
            num_upcoming = random.randint(2, 4) if is_main_patient else random.randint(0, 2)
            
            # Past appointments (completed, cancelled, no_show)
            for i in range(num_past):
                days_ago = random.randint(7, 180)
                dept = random.choice(list(providers_by_dept.keys()))
                provider = random.choice(providers_by_dept[dept])
                
                start_time = now - timedelta(days=days_ago, hours=random.randint(-4, 4))
                start_time = start_time.replace(hour=random.choice([9, 10, 11, 14, 15, 16]), minute=random.choice([0, 30]), second=0, microsecond=0)
                
                status_weights = [AppointmentStatus.COMPLETED] * 8 + [AppointmentStatus.CANCELLED] * 1 + [AppointmentStatus.NO_SHOW] * 1
                status = random.choice(status_weights)
                
                reason_list = reasons.get(dept, ["General consultation"])
                
                appointments.append(Appointment(
                    user_id=patient.id,
                    provider_id=provider.id,
                    time_start=start_time,
                    time_end=start_time + timedelta(minutes=30),
                    status=status,
                    channel=random.choice([AppointmentChannel.WEB, AppointmentChannel.AGENT, AppointmentChannel.PHONE]),
                    reason=random.choice(reason_list),
                    confirmation_code=generate_confirmation_code(),
                    created_at=start_time - timedelta(days=random.randint(1, 14)),
                ))
            
            # Upcoming appointments (confirmed, pending)
            for i in range(num_upcoming):
                days_ahead = random.randint(1, 30)
                dept = random.choice(list(providers_by_dept.keys()))
                provider = random.choice(providers_by_dept[dept])
                
                start_time = now + timedelta(days=days_ahead)
                start_time = start_time.replace(hour=random.choice([9, 10, 11, 14, 15, 16]), minute=random.choice([0, 30]), second=0, microsecond=0)
                
                status = random.choice([AppointmentStatus.CONFIRMED, AppointmentStatus.PENDING])
                reason_list = reasons.get(dept, ["General consultation"])
                
                appointments.append(Appointment(
                    user_id=patient.id,
                    provider_id=provider.id,
                    time_start=start_time,
                    time_end=start_time + timedelta(minutes=30),
                    status=status,
                    channel=random.choice([AppointmentChannel.WEB, AppointmentChannel.AGENT]),
                    reason=random.choice(reason_list),
                    confirmation_code=generate_confirmation_code(),
                    created_at=now - timedelta(days=random.randint(0, 7)),
                ))
        
        session.add_all(appointments)
        await session.commit()
        print(f"✓ Seeded {len(appointments)} appointments across {len(patients)} patients")


async def seed_incidents():
    """Seed realistic handover incidents."""
    print("Seeding handover incidents...")
    
    async with async_session_maker() as session:
        # Get patients (excluding main demo patient)
        result = await session.execute(
            select(User).where(User.role == UserRole.PATIENT, User.email != "patient@gmail.com")
        )
        patients = result.scalars().all()
        
        if not patients:
            print("⚠ No patients found for incidents")
            return
        
        now = datetime.now(timezone.utc)
        
        # Realistic incident scenarios
        incident_scenarios = [
            {
                "subject": "Emergency symptoms reported - chest pain",
                "chat_summary": "Patient reported severe chest pain during booking conversation. Agent correctly identified emergency and directed to 911. Logging for records.",
                "conversation": [
                    {"role": "user", "content": "I need to see a doctor urgently, I have really bad chest pain"},
                    {"role": "assistant", "content": "This sounds like a medical emergency. Please call 911 or go to the nearest emergency room immediately."},
                    {"role": "user", "content": "OK I will go now"},
                ],
                "priority": IncidentPriority.URGENT,
                "status": IncidentStatus.RESOLVED,
                "resolution": "Patient was directed to ER. Follow-up confirmed patient received care at AUBMC ER.",
            },
            {
                "subject": "Patient frustrated with appointment availability",
                "chat_summary": "Patient expressed frustration that no cardiology appointments were available for 2 weeks. Requested human assistance to find earlier slot.",
                "conversation": [
                    {"role": "user", "content": "I need to see a cardiologist this week, it's urgent"},
                    {"role": "assistant", "content": "I checked availability and the earliest cardiology appointment is in 2 weeks on December 10th. Would you like me to book that?"},
                    {"role": "user", "content": "That's too late! I need to speak to someone who can help me get an earlier appointment"},
                    {"role": "assistant", "content": "I understand your concern. Let me connect you with our patient services team who may be able to help with urgent scheduling."},
                ],
                "priority": IncidentPriority.HIGH,
                "status": IncidentStatus.RESOLVED,
                "resolution": "Patient services contacted. Found cancellation slot for December 2nd. Patient confirmed and satisfied.",
            },
            {
                "subject": "Billing inquiry - outside agent scope",
                "chat_summary": "Patient asked about insurance coverage and billing for upcoming procedure. Agent correctly identified this as outside scope and flagged for billing department.",
                "conversation": [
                    {"role": "user", "content": "How much will my MRI cost with my insurance?"},
                    {"role": "assistant", "content": "I can help with scheduling appointments, but for billing and insurance questions, I'll need to connect you with our billing department."},
                    {"role": "user", "content": "Can you transfer me to billing?"},
                ],
                "priority": IncidentPriority.LOW,
                "status": IncidentStatus.CLOSED,
                "resolution": "Transferred to billing department. Patient received cost estimate via email.",
            },
            {
                "subject": "Medication refill request - needs physician review",
                "chat_summary": "Patient requested medication refill through chat. Agent correctly declined and advised scheduling follow-up with prescribing physician.",
                "conversation": [
                    {"role": "user", "content": "I need a refill on my blood pressure medication"},
                    {"role": "assistant", "content": "I cannot process medication refills. Please contact your physician's office directly or schedule a follow-up appointment."},
                    {"role": "user", "content": "But I'm running out, can someone call in a refill?"},
                ],
                "priority": IncidentPriority.MEDIUM,
                "status": IncidentStatus.RESOLVED,
                "resolution": "Dr. Rodriguez's office contacted. Emergency 30-day refill approved. Follow-up scheduled.",
            },
            {
                "subject": "Technical issue - appointment not showing",
                "chat_summary": "Patient claims they booked an appointment but it's not showing in system. Needs investigation.",
                "conversation": [
                    {"role": "user", "content": "I booked an appointment last week but I don't see it anywhere"},
                    {"role": "assistant", "content": "I can see your upcoming appointments. You have an appointment on December 5th with Dr. Chen in Cardiology."},
                    {"role": "user", "content": "No that's wrong, I booked with a dermatologist for tomorrow"},
                    {"role": "assistant", "content": "I don't see a dermatology appointment in your records. Let me flag this for our support team to investigate."},
                ],
                "priority": IncidentPriority.MEDIUM,
                "status": IncidentStatus.IN_PROGRESS,
                "admin_notes": "Checking system logs for booking attempt. May have been a session timeout issue.",
            },
            {
                "subject": "Accessibility accommodation request",
                "chat_summary": "Patient needs wheelchair assistance and sign language interpreter for upcoming appointment. Requires coordination with facilities.",
                "conversation": [
                    {"role": "user", "content": "I need special accommodations for my appointment"},
                    {"role": "assistant", "content": "I'd be happy to note any special accommodations. What do you need?"},
                    {"role": "user", "content": "I use a wheelchair and I also need a sign language interpreter"},
                    {"role": "assistant", "content": "I'll flag this for our patient services team to coordinate these accommodations for you."},
                ],
                "priority": IncidentPriority.MEDIUM,
                "status": IncidentStatus.RESOLVED,
                "resolution": "Wheelchair assistance confirmed. ASL interpreter booked for Dec 8th appointment.",
            },
            {
                "subject": "Complaint about wait time at previous visit",
                "chat_summary": "Patient complained about 45-minute wait at last appointment. Wants to file formal complaint.",
                "conversation": [
                    {"role": "user", "content": "I want to file a complaint about my last visit"},
                    {"role": "assistant", "content": "I'm sorry to hear about your experience. What happened during your visit?"},
                    {"role": "user", "content": "I waited 45 minutes past my appointment time. This is unacceptable."},
                    {"role": "assistant", "content": "I apologize for the long wait. I'll escalate this to our patient relations team who can address your complaint formally."},
                ],
                "priority": IncidentPriority.LOW,
                "status": IncidentStatus.PENDING,
            },
            {
                "subject": "Breathing difficulty reported - monitored",
                "chat_summary": "Patient mentioned shortness of breath but clarified it was mild and ongoing for weeks. Not emergency but flagged for awareness.",
                "conversation": [
                    {"role": "user", "content": "I've been having some trouble breathing lately"},
                    {"role": "assistant", "content": "I want to make sure you're safe. Is this severe or sudden? Are you having chest pain?"},
                    {"role": "user", "content": "No no, it's mild. Been happening for a few weeks when I exercise"},
                    {"role": "assistant", "content": "Thank you for clarifying. I'd recommend scheduling with a pulmonologist to evaluate this. Would you like me to find available appointments?"},
                ],
                "priority": IncidentPriority.MEDIUM,
                "status": IncidentStatus.CLOSED,
                "resolution": "Patient booked with pulmonology. Not an emergency case.",
            },
        ]
        
        incidents = []
        for i, scenario in enumerate(incident_scenarios):
            patient = patients[i % len(patients)]
            days_ago = random.randint(1, 60)
            
            incident = HandoverIncident(
                user_id=patient.id,
                patient_name=patient.name,
                patient_email=patient.email,
                patient_phone=f"{patient.country_code}{patient.phone}" if patient.phone else None,
                subject=scenario["subject"],
                chat_summary=scenario["chat_summary"],
                full_conversation=json.dumps(scenario["conversation"]),
                priority=scenario["priority"],
                status=scenario["status"],
                admin_notes=scenario.get("admin_notes"),
                resolution=scenario.get("resolution"),
                created_at=now - timedelta(days=days_ago),
                resolved_at=(now - timedelta(days=days_ago - random.randint(1, 3))) if scenario["status"] in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED] else None,
            )
            incidents.append(incident)
        
        session.add_all(incidents)
        await session.commit()
        print(f"✓ Seeded {len(incidents)} handover incidents")


async def main():
    """Run all seed functions."""
    print("🌱 Starting database seeding...")
    print()

    # Initialize database
    await init_db()
    print("✓ Database initialized")

    # Clear existing data first
    await clear_database()

    # Seed data
    await seed_users()
    await seed_providers()
    await seed_lab_tests()
    await seed_appointments()  # Add appointment history
    await seed_incidents()  # Add handover incidents
    await seed_patient_test_results()  # Add patient test results
    await seed_documents()
    await seed_doctor_documents()
    await seed_lab_test_documents()  # Add lab test documents

    print()
    print("✅ Database seeding completed successfully!")
    print()
    print("Demo credentials:")
    print("  Patient: patient@gmail.com / password123")
    print("  Admin:   admin@aub.com / Admin@123")


if __name__ == "__main__":
    asyncio.run(main())
