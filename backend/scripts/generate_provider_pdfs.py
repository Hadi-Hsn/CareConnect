"""Generate professional 2-page PDF profiles for each provider."""
import io
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

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
    PageBreak,
)

from app.models import Provider


def generate_provider_pdf(provider: Provider) -> bytes:
    """
    Generate a professional 2-page PDF profile for a provider.
    
    Args:
        provider: Provider model instance
        
    Returns:
        PDF content as bytes
    """
    # Create a buffer to hold the PDF
    buffer = io.BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
    )
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#0077BE'),
        spaceAfter=12,
        alignment=1,  # Center
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#00A896'),
        spaceAfter=8,
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.HexColor('#0077BE'),
        spaceAfter=6,
        spaceBefore=12,
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        spaceAfter=6,
        leading=14,
    )
    
    # Get provider type display name
    provider_type = provider.type if hasattr(provider.type, 'value') else provider.type
    type_display = provider_type.replace('_', ' ').title()
    
    # ============================================================================
    # PAGE 1: Professional Profile
    # ============================================================================
    
    # Header
    elements.append(Paragraph(provider.name, title_style))
    elements.append(Paragraph(f"{provider.specialty or provider.department}", subtitle_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    # Provider Information Table
    info_data = [
        ['Department:', provider.department],
        ['Type:', type_display],
        ['Specialty:', provider.specialty or 'General'],
        ['Provider ID:', f'#{provider.id}'],
    ]
    
    info_table = Table(info_data, colWidths=[2 * inch, 4 * inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F8FF')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#0077BE')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#F8F8F8')]),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 0.3 * inch))
    
    # About Section
    elements.append(Paragraph("About", heading_style))
    bio_text = provider.bio or f"Experienced {type_display} specializing in {provider.specialty or provider.department}."
    elements.append(Paragraph(bio_text, body_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    # Specialties Section
    elements.append(Paragraph("Areas of Expertise", heading_style))
    
    # Department-specific expertise
    expertise_map = {
        "Cardiology": [
            "Heart disease diagnosis and treatment",
            "Cardiovascular risk assessment",
            "Hypertension management",
            "Heart failure care",
            "Preventive cardiology",
            "Cardiac rehabilitation",
        ],
        "Dermatology": [
            "Skin cancer screening and treatment",
            "Acne and rosacea management",
            "Eczema and psoriasis care",
            "Cosmetic dermatology",
            "Skin infection treatment",
            "Mole removal and biopsies",
        ],
        "Emergency Medicine": [
            "Acute trauma care",
            "Emergency resuscitation",
            "Critical care medicine",
            "Toxicology and overdose management",
            "Rapid diagnostic assessment",
            "Emergency procedures",
        ],
        "Endocrinology": [
            "Diabetes management and education",
            "Thyroid disorder treatment",
            "Hormonal imbalance diagnosis",
            "Metabolic syndrome care",
            "Osteoporosis management",
            "Pituitary and adrenal disorders",
        ],
        "Gastroenterology": [
            "Digestive disorder diagnosis",
            "Endoscopy and colonoscopy",
            "Liver disease management",
            "IBS and IBD treatment",
            "GERD and reflux management",
            "Nutritional counseling",
        ],
        "Internal Medicine": [
            "Comprehensive primary care",
            "Chronic disease management",
            "Preventive medicine",
            "Health screenings",
            "Medication management",
            "Geriatric care",
        ],
        "Neurology": [
            "Stroke care and prevention",
            "Seizure disorder management",
            "Headache and migraine treatment",
            "Movement disorder evaluation",
            "Memory disorder assessment",
            "Neuropathy management",
        ],
        "Oncology": [
            "Cancer screening and diagnosis",
            "Chemotherapy administration",
            "Immunotherapy treatment",
            "Palliative care",
            "Cancer survivorship care",
            "Clinical trial coordination",
        ],
        "Orthopedics": [
            "Joint replacement surgery",
            "Sports injury treatment",
            "Arthritis management",
            "Fracture care",
            "Spine surgery",
            "Arthroscopic procedures",
        ],
        "Pediatrics": [
            "Well-child examinations",
            "Childhood vaccination programs",
            "Growth and development monitoring",
            "Acute illness treatment",
            "Behavioral health support",
            "Chronic condition management",
        ],
        "Psychiatry": [
            "Mental health assessment",
            "Depression and anxiety treatment",
            "Medication management",
            "Psychotherapy",
            "Substance abuse treatment",
            "Crisis intervention",
        ],
    }
    
    expertise_list = expertise_map.get(provider.department, [
        f"{provider.department} diagnosis and treatment",
        "Patient education and counseling",
        "Evidence-based medical care",
        "Collaborative healthcare approach",
    ])
    
    # Create bullet points
    for expertise in expertise_list[:6]:  # Limit to 6 items for page 1
        elements.append(Paragraph(f"• {expertise}", body_style))
    
    elements.append(Spacer(1, 0.2 * inch))
    
    # Appointment Information
    elements.append(Paragraph("Scheduling Information", heading_style))
    appointment_text = f"""
    To book an appointment with {provider.name}, you can:
    <br/>
    • Search for available time slots in the {provider.department} department
    <br/>
    • Request appointment by provider name or specialty
    <br/>
    • Use our AI assistant for natural language booking
    <br/>
    • Call our scheduling line: +961 (XX) XXX-XXXX
    <br/><br/>
    Appointments typically available Monday through Friday, 8:00 AM - 5:00 PM.
    Same-day appointments may be available for urgent concerns.
    """
    elements.append(Paragraph(appointment_text, body_style))
    
    # ============================================================================
    # PAGE 2: Clinical Information & Patient Resources
    # ============================================================================
    
    elements.append(PageBreak())
    
    # Page 2 Header
    elements.append(Paragraph(f"{provider.name} - Clinical Information", title_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    # Common Conditions Treated
    elements.append(Paragraph("Common Conditions Treated", heading_style))
    
    conditions_map = {
        "Cardiology": [
            "Coronary artery disease",
            "Heart failure",
            "Arrhythmias",
            "Hypertension",
            "Valvular heart disease",
            "Cardiomyopathy",
        ],
        "Dermatology": [
            "Acne and acne scars",
            "Eczema and atopic dermatitis",
            "Psoriasis",
            "Skin cancer",
            "Rosacea",
            "Hair loss",
        ],
        "Emergency Medicine": [
            "Chest pain",
            "Shortness of breath",
            "Trauma and injuries",
            "Abdominal pain",
            "Allergic reactions",
            "Poisoning and overdose",
        ],
        "Endocrinology": [
            "Type 1 and Type 2 diabetes",
            "Hypothyroidism and hyperthyroidism",
            "Metabolic syndrome",
            "Polycystic ovary syndrome (PCOS)",
            "Osteoporosis",
            "Adrenal insufficiency",
        ],
        "Gastroenterology": [
            "Irritable bowel syndrome (IBS)",
            "Inflammatory bowel disease (IBD)",
            "GERD and reflux",
            "Peptic ulcers",
            "Liver disease",
            "Pancreatitis",
        ],
        "Internal Medicine": [
            "High blood pressure",
            "Diabetes",
            "High cholesterol",
            "Asthma",
            "Chronic kidney disease",
            "Arthritis",
        ],
        "Neurology": [
            "Stroke",
            "Epilepsy",
            "Parkinson's disease",
            "Multiple sclerosis",
            "Alzheimer's disease",
            "Migraine headaches",
        ],
        "Oncology": [
            "Breast cancer",
            "Lung cancer",
            "Colorectal cancer",
            "Prostate cancer",
            "Lymphoma",
            "Leukemia",
        ],
        "Orthopedics": [
            "Osteoarthritis",
            "Sports injuries",
            "Fractures",
            "Back and neck pain",
            "Tendonitis",
            "Carpal tunnel syndrome",
        ],
        "Pediatrics": [
            "Asthma",
            "Allergies",
            "ADHD",
            "Childhood obesity",
            "Developmental delays",
            "Ear infections",
        ],
        "Psychiatry": [
            "Major depression",
            "Anxiety disorders",
            "Bipolar disorder",
            "PTSD",
            "Schizophrenia",
            "Substance use disorders",
        ],
    }
    
    conditions_list = conditions_map.get(provider.department, [
        f"Various {provider.department.lower()} conditions",
    ])
    
    for condition in conditions_list:
        elements.append(Paragraph(f"• {condition}", body_style))
    
    elements.append(Spacer(1, 0.2 * inch))
    
    # What to Expect
    elements.append(Paragraph("What to Expect at Your Appointment", heading_style))
    expect_text = f"""
    During your appointment with {provider.name}, you can expect:
    <br/><br/>
    <b>Initial Consultation:</b>
    <br/>
    • Comprehensive medical history review
    <br/>
    • Discussion of your symptoms and concerns
    <br/>
    • Physical examination as appropriate
    <br/>
    • Review of current medications and allergies
    <br/><br/>
    <b>Diagnosis and Treatment:</b>
    <br/>
    • Diagnostic testing if needed (labs, imaging, etc.)
    <br/>
    • Clear explanation of findings
    <br/>
    • Personalized treatment plan
    <br/>
    • Prescription medications if necessary
    <br/><br/>
    <b>Follow-up Care:</b>
    <br/>
    • Scheduling of follow-up appointments
    <br/>
    • Instructions for at-home care
    <br/>
    • Contact information for questions
    <br/>
    • Coordination with other healthcare providers as needed
    """
    elements.append(Paragraph(expect_text, body_style))
    
    elements.append(Spacer(1, 0.2 * inch))
    
    # Preparation Instructions
    elements.append(Paragraph("Preparing for Your Visit", heading_style))
    prep_text = """
    To make the most of your appointment:
    <br/><br/>
    • Bring a list of current medications (include dosages)
    <br/>
    • Bring your insurance card and photo ID
    <br/>
    • Arrive 15 minutes early to complete paperwork
    <br/>
    • Write down questions you want to ask
    <br/>
    • Bring a friend or family member if desired
    <br/>
    • Bring relevant medical records from other providers
    """
    elements.append(Paragraph(prep_text, body_style))
    
    elements.append(Spacer(1, 0.2 * inch))
    
    # Footer with contact information
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=1,  # Center
    )
    
    elements.append(Spacer(1, 0.3 * inch))
    footer_text = f"""
    <b>CareConnect Medical Center</b>
    <br/>
    {provider.department} Department | Provider ID: {provider.id}
    <br/>
    For appointments: Call +961 (XX) XXX-XXXX or use our AI scheduling assistant
    <br/>
    Generated: {datetime.now().strftime('%B %d, %Y')}
    """
    elements.append(Paragraph(footer_text, footer_style))
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes


if __name__ == "__main__":
    print("This script should be imported, not run directly.")
    print("Use populate_demo_database.py to generate PDFs during seeding.")
