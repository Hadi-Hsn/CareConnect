"""Generate lab test preparation PDF documents for RAG system."""
import io
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

# Lab test preparation information
LAB_TESTS = {
    "Complete Blood Count (CBC)": {
        "category": "Blood Test",
        "preparation": [
            "No fasting required",
            "No special preparation needed",
            "Wear comfortable clothing with sleeves that can be easily rolled up",
            "Stay well hydrated before the test",
            "Inform your doctor of any medications you're taking",
        ],
        "what_it_tests": [
            "Red blood cell count",
            "White blood cell count",
            "Hemoglobin levels",
            "Hematocrit",
            "Platelet count",
        ],
        "duration": "5-10 minutes",
        "results_time": "1-2 days",
    },
    "Basic Metabolic Panel (BMP)": {
        "category": "Blood Test",
        "preparation": [
            "Fasting for 8-12 hours required",
            "Water is allowed during fasting period",
            "No food, juice, coffee, or tea before the test",
            "Take regular medications unless instructed otherwise",
            "Schedule appointment in the morning if possible",
        ],
        "what_it_tests": [
            "Glucose levels",
            "Calcium levels",
            "Electrolyte balance (sodium, potassium, chloride, bicarbonate)",
            "Kidney function (BUN, creatinine)",
        ],
        "duration": "5-10 minutes",
        "results_time": "1-2 days",
    },
    "Lipid Panel": {
        "category": "Blood Test",
        "preparation": [
            "Fasting for 9-12 hours required",
            "Only water allowed during fasting period",
            "Avoid alcohol for 24 hours before test",
            "Take regular medications unless instructed otherwise",
            "Schedule appointment in the morning",
        ],
        "what_it_tests": [
            "Total cholesterol",
            "LDL (bad) cholesterol",
            "HDL (good) cholesterol",
            "Triglycerides",
        ],
        "duration": "5-10 minutes",
        "results_time": "1-3 days",
    },
    "Thyroid Function Tests": {
        "category": "Blood Test",
        "preparation": [
            "No fasting required",
            "Best to test in the morning for consistent results",
            "Inform doctor if taking thyroid medications",
            "Some medications may affect results - consult your doctor",
        ],
        "what_it_tests": [
            "TSH (Thyroid Stimulating Hormone)",
            "T3 and T4 levels",
            "Thyroid antibodies (if ordered)",
        ],
        "duration": "5-10 minutes",
        "results_time": "1-3 days",
    },
    "Hemoglobin A1C": {
        "category": "Blood Test",
        "preparation": [
            "No fasting required",
            "No special preparation needed",
            "Test can be done at any time of day",
            "Results reflect average blood sugar over 2-3 months",
        ],
        "what_it_tests": [
            "Average blood glucose levels over past 2-3 months",
            "Used to diagnose and monitor diabetes",
        ],
        "duration": "5-10 minutes",
        "results_time": "1-2 days",
    },
    "Urinalysis": {
        "category": "Urine Test",
        "preparation": [
            "No fasting required",
            "First morning urine sample is preferred",
            "Clean-catch midstream collection required",
            "Follow provided instructions for clean collection",
            "Avoid contamination of sample",
        ],
        "what_it_tests": [
            "Urinary tract infections",
            "Kidney disease",
            "Diabetes",
            "Liver problems",
            "Blood in urine",
        ],
        "duration": "5 minutes",
        "results_time": "1-2 days",
    },
    "X-Ray": {
        "category": "Imaging",
        "preparation": [
            "No fasting required",
            "Remove jewelry and metal objects",
            "Notify the radiologist if you have any previous surgery that involves metal implants",
            "Wear comfortable clothing without metal fasteners",
        ],
        "what_it_tests": [
            "Imaging of requested body part",
            "Bone fractures",
            "Joint conditions",
            "Soft tissue abnormalities",
        ],
        "duration": "10-15 minutes",
        "results_time": "1-2 days",
    },
    "Abdominal Ultrasound": {
        "category": "Imaging",
        "preparation": [
            "Fasting for 8-12 hours required",
            "Water may be restricted 2 hours before test",
            "Take regular medications with small sips of water",
            "Wear comfortable, loose-fitting clothing",
            "Full bladder may be required (for some exams)",
        ],
        "what_it_tests": [
            "Liver, gallbladder, pancreas, spleen",
            "Kidneys and bladder",
            "Abdominal aorta",
            "Presence of tumors or cysts",
        ],
        "duration": "30-45 minutes",
        "results_time": "2-3 days",
    },
    "Mammogram": {
        "category": "Imaging",
        "preparation": [
            "Schedule 1 week after your period if possible",
            "Don't use deodorant, perfume, or powder on test day",
            "Wear two-piece clothing for easy undressing",
            "Inform technician of any breast symptoms",
            "Bring previous mammogram images if available",
        ],
        "what_it_tests": [
            "Breast cancer screening",
            "Breast lumps or masses",
            "Calcifications",
            "Breast tissue changes",
        ],
        "duration": "20-30 minutes",
        "results_time": "1-2 weeks",
    },
    "Colonoscopy": {
        "category": "Procedure",
        "preparation": [
            "Clear liquid diet 1 day before procedure",
            "Bowel preparation (laxatives) required",
            "Fasting for 8 hours before procedure",
            "Arrange for someone to drive you home",
            "Stop certain medications as instructed",
        ],
        "what_it_tests": [
            "Colon cancer screening",
            "Polyps",
            "Inflammatory bowel disease",
            "Causes of bleeding or abdominal pain",
        ],
        "duration": "30-60 minutes",
        "results_time": "Preliminary results same day, biopsy results 1-2 weeks",
    },
    "EKG (Electrocardiogram)": {
        "category": "Diagnostic Test",
        "preparation": [
            "No fasting required",
            "Wear comfortable clothing",
            "Avoid oily or greasy skin lotions on test day",
            "Inform technician of pacemaker or other devices",
            "Relax and breathe normally during test",
        ],
        "what_it_tests": [
            "Heart rhythm",
            "Heart rate",
            "Heart attack damage",
            "Enlarged heart",
            "Abnormal heart rhythms",
        ],
        "duration": "5-10 minutes",
        "results_time": "Immediate (read by doctor)",
    },
    "Stress Test": {
        "category": "Diagnostic Test",
        "preparation": [
            "Fasting for 3-4 hours before test",
            "Wear comfortable shoes and clothing for exercise",
            "Avoid caffeine for 24 hours before test",
            "Take regular medications unless instructed otherwise",
            "Inform doctor of any chest pain or symptoms",
        ],
        "what_it_tests": [
            "Heart function during physical stress",
            "Blood flow to heart",
            "Exercise capacity",
            "Abnormal heart rhythms during exercise",
        ],
        "duration": "60-90 minutes",
        "results_time": "Same day (preliminary), full report 1-2 days",
    },
}


def generate_lab_test_pdf(test_name: str, test_info: dict) -> bytes:
    """Generate a PDF document for a lab test."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#0077BE'),
        spaceAfter=12,
        alignment=1,
    )
    
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#00A896'),
        spaceAfter=8,
        spaceBefore=12,
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['BodyText'],
        fontSize=11,
        spaceAfter=6,
        leading=14,
    )
    
    # Title
    elements.append(Paragraph(test_name, title_style))
    elements.append(Paragraph(f"Category: {test_info['category']}", body_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Preparation Instructions
    elements.append(Paragraph("Preparation Instructions", heading_style))
    for instruction in test_info['preparation']:
        elements.append(Paragraph(f"• {instruction}", body_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # What It Tests
    elements.append(Paragraph("What This Test Measures", heading_style))
    for item in test_info['what_it_tests']:
        elements.append(Paragraph(f"• {item}", body_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Test Details
    elements.append(Paragraph("Test Details", heading_style))
    elements.append(Paragraph(f"• <b>Duration:</b> {test_info['duration']}", body_style))
    elements.append(Paragraph(f"• <b>Results Available:</b> {test_info['results_time']}", body_style))
    
    doc.build(elements)
    return buffer.getvalue()


async def populate_lab_tests():
    """Generate PDFs and populate vector store with lab test information."""
    from app.schemas.rag import Document
    from app.services.pdf_parser import PDFParser
    from app.services.rag_service import RAGService
    
    print("Generating lab test preparation documents...")
    
    rag_service = RAGService()
    pdf_parser = PDFParser()
    
    # Create documents from lab test PDFs
    documents = []
    
    for test_name, test_info in LAB_TESTS.items():
        print(f"Processing: {test_name}")
        
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


if __name__ == "__main__":
    import asyncio
    asyncio.run(populate_lab_tests())
