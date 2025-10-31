"""Generate dummy PDF documents for doctor profiles."""
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# Doctor profiles data
DOCTORS_DATA = [
    {
        "name": "Dr. Sarah Johnson",
        "specialty": "Cardiology",
        "credentials": "MD, FACC",
        "experience": "15 years",
        "education": "Harvard Medical School (2008), Residency at Johns Hopkins Hospital",
        "about": """Dr. Sarah Johnson is a board-certified cardiologist with over 15 years of 
        experience in treating cardiovascular diseases. She specializes in preventive cardiology, 
        heart failure management, and advanced cardiac imaging. Dr. Johnson is known for her 
        patient-centered approach and has published numerous research papers on heart disease 
        prevention.""",
        "areas_of_expertise": [
            "Preventive Cardiology",
            "Heart Failure Management",
            "Cardiac Imaging (Echo, CT, MRI)",
            "Hypertension Management",
            "Coronary Artery Disease",
            "Arrhythmia Treatment"
        ],
        "languages": ["English", "Spanish"],
        "office_hours": "Monday-Friday: 8:00 AM - 5:00 PM",
        "insurance": "Accepts most major insurance plans including Blue Cross, Aetna, UnitedHealthcare",
        "awards": [
            "Top Cardiologist Award - City Medical Society (2022)",
            "Excellence in Patient Care - Healthcare Alliance (2021)",
            "Best Doctor Recognition - Medical Magazine (2020)"
        ]
    },
    {
        "name": "Dr. Michael Chen",
        "specialty": "Orthopedic Surgery",
        "credentials": "MD, FAAOS",
        "experience": "20 years",
        "education": "Stanford University School of Medicine (2003), Fellowship in Sports Medicine",
        "about": """Dr. Michael Chen is a distinguished orthopedic surgeon specializing in sports 
        medicine and joint reconstruction. With two decades of experience, he has performed over 
        5,000 successful surgeries. Dr. Chen is the team physician for several professional sports 
        teams and is renowned for his minimally invasive surgical techniques.""",
        "areas_of_expertise": [
            "Sports Medicine",
            "Knee Replacement Surgery",
            "Hip Replacement Surgery",
            "Arthroscopic Surgery",
            "Shoulder Reconstruction",
            "ACL Repair",
            "Fracture Care"
        ],
        "languages": ["English", "Mandarin"],
        "office_hours": "Tuesday-Saturday: 9:00 AM - 6:00 PM",
        "insurance": "Accepts all major insurance plans",
        "awards": [
            "Surgeon of Excellence Award (2023)",
            "Outstanding Physician Award - State Medical Board (2022)",
            "Innovation in Orthopedic Surgery Award (2019)"
        ]
    },
    {
        "name": "Dr. Emily Rodriguez",
        "specialty": "Pediatrics",
        "credentials": "MD, FAAP",
        "experience": "12 years",
        "education": "Yale School of Medicine (2011), Pediatric Residency at Children's Hospital Boston",
        "about": """Dr. Emily Rodriguez is a compassionate pediatrician dedicated to providing 
        comprehensive care for children from infancy through adolescence. She has a special 
        interest in childhood development, preventive care, and managing chronic conditions 
        like asthma and diabetes. Dr. Rodriguez is fluent in Spanish and is committed to 
        serving diverse communities.""",
        "areas_of_expertise": [
            "Well-Child Visits",
            "Childhood Vaccinations",
            "Developmental Assessments",
            "Asthma Management",
            "Pediatric Diabetes Care",
            "Behavioral Health",
            "Adolescent Medicine"
        ],
        "languages": ["English", "Spanish", "Portuguese"],
        "office_hours": "Monday-Friday: 7:00 AM - 4:00 PM, Saturday: 8:00 AM - 12:00 PM",
        "insurance": "Accepts Medicaid and most major insurance plans",
        "awards": [
            "Pediatrician of the Year (2023)",
            "Community Health Champion Award (2022)",
            "Excellence in Child Care (2020)"
        ]
    },
    {
        "name": "Dr. James Williams",
        "specialty": "Internal Medicine",
        "credentials": "MD, FACP",
        "experience": "18 years",
        "education": "University of Pennsylvania School of Medicine (2005), Internal Medicine Residency at Mayo Clinic",
        "about": """Dr. James Williams is an experienced internist providing comprehensive primary 
        care for adults. He specializes in managing complex chronic conditions including diabetes, 
        hypertension, and metabolic disorders. Dr. Williams emphasizes preventive medicine and 
        works closely with patients to develop personalized treatment plans.""",
        "areas_of_expertise": [
            "Diabetes Management",
            "Hypertension Treatment",
            "Preventive Medicine",
            "Cholesterol Management",
            "Thyroid Disorders",
            "Chronic Disease Management",
            "Executive Health Screenings"
        ],
        "languages": ["English"],
        "office_hours": "Monday-Thursday: 8:00 AM - 6:00 PM, Friday: 8:00 AM - 3:00 PM",
        "insurance": "Accepts Medicare and most major insurance plans",
        "awards": [
            "Excellence in Internal Medicine Award (2022)",
            "Top Doc Recognition (2021, 2023)",
            "Patient's Choice Award (2020-2023)"
        ]
    },
    {
        "name": "Dr. Lisa Patel",
        "specialty": "Dermatology",
        "credentials": "MD, FAAD",
        "experience": "10 years",
        "education": "Columbia University College of Physicians and Surgeons (2013), Dermatology Residency at NYU",
        "about": """Dr. Lisa Patel is a board-certified dermatologist with expertise in both 
        medical and cosmetic dermatology. She treats a wide range of skin conditions and is 
        particularly skilled in skin cancer detection and treatment. Dr. Patel stays at the 
        forefront of dermatological advances and offers the latest evidence-based treatments.""",
        "areas_of_expertise": [
            "Skin Cancer Screening",
            "Acne Treatment",
            "Psoriasis Management",
            "Eczema Care",
            "Cosmetic Dermatology",
            "Botox and Fillers",
            "Laser Treatments",
            "Mole Removal"
        ],
        "languages": ["English", "Hindi", "Gujarati"],
        "office_hours": "Monday-Friday: 9:00 AM - 5:00 PM",
        "insurance": "Accepts most major insurance plans",
        "awards": [
            "Rising Star in Dermatology (2023)",
            "Best Cosmetic Dermatologist - Local Magazine (2022)",
            "Excellence in Skin Cancer Detection (2021)"
        ]
    }
]


def create_doctor_pdf(doctor_data: dict, output_path: Path) -> None:
    """Create a PDF document for a doctor profile."""
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )

    # Container for the 'Flowable' objects
    elements = []

    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a5490'),
        spaceAfter=30,
        alignment=1,  # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1a5490'),
        spaceAfter=12,
        spaceBefore=12,
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        spaceAfter=12,
    )

    # Title
    elements.append(Paragraph(doctor_data['name'], title_style))
    elements.append(Paragraph(
        f"{doctor_data['specialty']} | {doctor_data['credentials']}",
        ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=12, alignment=1)
    ))
    elements.append(Spacer(1, 0.3 * inch))

    # Basic Info Table
    basic_info = [
        ['Experience:', doctor_data['experience']],
        ['Education:', doctor_data['education']],
        ['Languages:', ', '.join(doctor_data['languages'])],
    ]
    
    info_table = Table(basic_info, colWidths=[1.5 * inch, 4.5 * inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e6f2ff')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.2 * inch))

    # About section
    elements.append(Paragraph('About', heading_style))
    elements.append(Paragraph(doctor_data['about'], body_style))
    elements.append(Spacer(1, 0.1 * inch))

    # Areas of Expertise
    elements.append(Paragraph('Areas of Expertise', heading_style))
    for area in doctor_data['areas_of_expertise']:
        elements.append(Paragraph(f"• {area}", body_style))
    elements.append(Spacer(1, 0.1 * inch))

    # Office Hours
    elements.append(Paragraph('Office Hours', heading_style))
    elements.append(Paragraph(doctor_data['office_hours'], body_style))
    elements.append(Spacer(1, 0.1 * inch))

    # Insurance
    elements.append(Paragraph('Insurance', heading_style))
    elements.append(Paragraph(doctor_data['insurance'], body_style))
    elements.append(Spacer(1, 0.1 * inch))

    # Awards and Recognition
    elements.append(Paragraph('Awards & Recognition', heading_style))
    for award in doctor_data['awards']:
        elements.append(Paragraph(f"• {award}", body_style))

    # Build PDF
    doc.build(elements)
    print(f"  ✓ Generated: {output_path.name}")


def main():
    """Generate all doctor PDFs."""
    # Create output directory - shared volume with backend
    output_dir = Path("/app/data/doctor_pdfs")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("📄 Generating doctor PDFs...")
    print(f"   Output: {output_dir}")
    print()

    # Generate PDFs
    for doctor in DOCTORS_DATA:
        # Create filename from doctor name
        filename = doctor['name'].replace('Dr. ', '').replace(' ', '_').lower() + '.pdf'
        output_path = output_dir / filename
        
        create_doctor_pdf(doctor, output_path)

    print()
    print(f"✅ Successfully generated {len(DOCTORS_DATA)} doctor PDFs!")


if __name__ == "__main__":
    main()
