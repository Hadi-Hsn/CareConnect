"""Admin endpoints for managing doctors, appointments, and schedules."""
import asyncio
import json
import sys
from datetime import date, datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.logging import get_logger
from app.core.security import require_admin
from app.models import Appointment, PatientTestResult, Provider, User
from app.models.appointment import AppointmentStatus
from app.models.provider import ProviderType
from app.models.user import UserRole
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentUpdate,
    AppointmentWithDetails,
)
from app.schemas.provider import ProviderCreate, ProviderResponse, ProviderUpdate, TimeSlot
from app.schemas.rag import Document, IndexResponse
from app.services.pdf_parser import PDFParser
from app.services.rag_service import RAGService

# Import PDF generator
from scripts.generate_provider_pdfs import generate_provider_pdf

router = APIRouter()
logger = get_logger(__name__)

# Lebanon timezone
LEBANON_TZ = ZoneInfo("Asia/Beirut")


# ============================================================================
# DOCTOR (PROVIDER) MANAGEMENT
# ============================================================================


@router.post("/doctors", response_model=ProviderResponse, status_code=status.HTTP_201_CREATED)
async def create_doctor(
    doctor_data: ProviderCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> ProviderResponse:
    """
    Create a new doctor/provider.
    
    **Admin only.**
    """
    doctor = Provider(
        name=doctor_data.name,
        department=doctor_data.department,
        type=doctor_data.type,
        specialty=doctor_data.specialty,
        bio=doctor_data.bio,
        availability_calendar_id=doctor_data.availability_calendar_id,
    )

    db.add(doctor)
    await db.commit()
    await db.refresh(doctor)

    logger.info(
        "doctor_created",
        doctor_id=doctor.id,
        name=doctor.name,
        admin_id=admin.id,
    )

    return ProviderResponse.model_validate(doctor)


@router.get("/doctors", response_model=list[ProviderResponse])
async def list_all_doctors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    department: str | None = Query(None),
    specialty: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> list[ProviderResponse]:
    """
    List all doctors with optional filters.
    
    **Admin only.**
    """
    query = select(Provider)

    if department:
        query = query.where(Provider.department.ilike(f"%{department}%"))
    if specialty:
        query = query.where(Provider.specialty.ilike(f"%{specialty}%"))

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    doctors = result.scalars().all()

    return [ProviderResponse.model_validate(d) for d in doctors]


@router.get("/doctors/{doctor_id}", response_model=ProviderResponse)
async def get_doctor(
    doctor_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> ProviderResponse:
    """
    Get doctor details by ID.
    
    **Admin only.**
    """
    result = await db.execute(select(Provider).where(Provider.id == doctor_id))
    doctor = result.scalar_one_or_none()

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    return ProviderResponse.model_validate(doctor)


@router.put("/doctors/{doctor_id}", response_model=ProviderResponse)
async def update_doctor(
    doctor_id: int,
    doctor_data: ProviderUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> ProviderResponse:
    """
    Update doctor information.
    
    **Admin only.**
    """
    result = await db.execute(select(Provider).where(Provider.id == doctor_id))
    doctor = result.scalar_one_or_none()

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Update fields
    if doctor_data.name is not None:
        doctor.name = doctor_data.name
    if doctor_data.department is not None:
        doctor.department = doctor_data.department
    if doctor_data.specialty is not None:
        doctor.specialty = doctor_data.specialty
    if doctor_data.bio is not None:
        doctor.bio = doctor_data.bio
    if doctor_data.availability_calendar_id is not None:
        doctor.availability_calendar_id = doctor_data.availability_calendar_id

    await db.commit()
    await db.refresh(doctor)

    logger.info(
        "doctor_updated",
        doctor_id=doctor_id,
        admin_id=admin.id,
    )

    return ProviderResponse.model_validate(doctor)


@router.delete("/doctors/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_doctor(
    doctor_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> None:
    """
    Delete a doctor.
    
    **Admin only.** This will also cancel all associated appointments.
    """
    result = await db.execute(select(Provider).where(Provider.id == doctor_id))
    doctor = result.scalar_one_or_none()

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Cancel all future appointments
    await db.execute(
        delete(Appointment).where(
            Appointment.provider_id == doctor_id,
            Appointment.time_start > datetime.now(LEBANON_TZ),
        )
    )

    await db.delete(doctor)
    await db.commit()

    logger.info(
        "doctor_deleted",
        doctor_id=doctor_id,
        admin_id=admin.id,
    )


@router.post("/doctors/{doctor_id}/upload-profile", response_model=IndexResponse)
async def upload_doctor_profile(
    doctor_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> IndexResponse:
    """
    Upload and index a PDF profile for a doctor.
    
    **Admin only.** The PDF will be parsed, embedded, and made searchable via RAG.
    """
    # Verify doctor exists
    result = await db.execute(select(Provider).where(Provider.id == doctor_id))
    doctor = result.scalar_one_or_none()

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Validate file type
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )

    try:
        # Read file content
        content = await file.read()
        
        # Parse PDF
        pdf_parser = PDFParser()
        text = pdf_parser.extract_text_from_bytes(content)
        
        if not text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PDF appears to be empty or could not be parsed"
            )
        
        # Create document with doctor metadata
        document = Document(
            title=f"Dr. {doctor.name}",
            content=text,
            metadata={
                "doctor_id": str(doctor_id),
                "doctor_name": doctor.name,
                "department": doctor.department,
                "specialty": doctor.specialty or "",
                "doc_type": "doctor_profile",
                "source": file.filename,
                "upload_type": "admin",
            },
            doc_type="pdf"
        )
        
        # Index document
        rag_service = RAGService()
        response = await rag_service.index_documents([document], replace=False)
        
        logger.info(
            "doctor_profile_uploaded",
            doctor_id=doctor_id,
            filename=file.filename,
            admin_id=admin.id,
            chunks=response.total_chunks
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("doctor_profile_upload_failed", doctor_id=doctor_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process PDF: {str(e)}"
        )


@router.get("/doctors/{doctor_id}/download-profile")
async def download_doctor_profile(
    doctor_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> Response:
    """
    Download the generated PDF profile for a doctor.
    
    **Admin only.** Generates a professional 2-page PDF profile on-the-fly.
    """
    # Verify doctor exists
    result = await db.execute(select(Provider).where(Provider.id == doctor_id))
    doctor = result.scalar_one_or_none()

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    try:
        # Generate PDF
        pdf_bytes = generate_provider_pdf(doctor)
        
        # Sanitize doctor name for filename
        safe_name = doctor.name.replace(" ", "_").replace(".", "")
        filename = f"{safe_name}_Profile.pdf"
        
        logger.info(
            "doctor_profile_downloaded",
            doctor_id=doctor_id,
            admin_id=admin.id,
        )
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
        
    except Exception as e:
        logger.error("doctor_profile_download_failed", doctor_id=doctor_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF: {str(e)}"
        )


# ============================================================================
# APPOINTMENT MANAGEMENT
# ============================================================================


@router.get("/appointments", response_model=list[AppointmentWithDetails])
async def list_all_appointments(
    user_id: int | None = Query(None),
    provider_id: int | None = Query(None),
    status: AppointmentStatus | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> list[AppointmentWithDetails]:
    """
    List all appointments with filters.
    
    **Admin only.** Can filter by user, provider, status, and date range.
    """
    query = select(Appointment, User, Provider).join(User).join(Provider)

    if user_id:
        query = query.where(Appointment.user_id == user_id)
    if provider_id:
        query = query.where(Appointment.provider_id == provider_id)
    if status:
        query = query.where(Appointment.status == status)
    if date_from:
        query = query.where(Appointment.time_start >= datetime.combine(date_from, time.min))
    if date_to:
        query = query.where(Appointment.time_start <= datetime.combine(date_to, time.max))

    query = query.offset(skip).limit(limit).order_by(Appointment.time_start.desc())

    result = await db.execute(query)
    rows = result.all()

    appointments = []
    for appt, user, provider in rows:
        appt_dict = AppointmentResponse.model_validate(appt).model_dump()
        appt_dict.update(
            {
                "user_name": user.name,
                "user_email": user.email,
                "provider_name": provider.name,
                "provider_department": provider.department,
            }
        )
        appointments.append(AppointmentWithDetails(**appt_dict))

    return appointments


@router.post("/appointments", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment_admin(
    appointment_data: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> AppointmentResponse:
    """
    Create an appointment on behalf of a user.
    
    **Admin only.**
    """
    # Verify user exists
    result = await db.execute(select(User).where(User.id == appointment_data.user_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="User not found")

    # Verify provider exists
    result = await db.execute(select(Provider).where(Provider.id == appointment_data.provider_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Provider not found")

    # Create appointment
    appointment = Appointment(
        user_id=appointment_data.user_id,
        provider_id=appointment_data.provider_id,
        time_start=appointment_data.time_start,
        time_end=appointment_data.time_end,
        reason=appointment_data.reason,
        channel=appointment_data.channel,
        status=AppointmentStatus.CONFIRMED,  # Auto-confirm admin-created appointments
    )

    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)

    logger.info(
        "appointment_created_by_admin",
        appointment_id=appointment.id,
        admin_id=admin.id,
    )

    return AppointmentResponse.model_validate(appointment)


@router.put("/appointments/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment_admin(
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> AppointmentResponse:
    """
    Update any appointment.
    
    **Admin only.**
    """
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
    appointment = result.scalar_one_or_none()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # Update fields
    if appointment_data.time_start is not None:
        appointment.time_start = appointment_data.time_start
    if appointment_data.time_end is not None:
        appointment.time_end = appointment_data.time_end
    if appointment_data.status is not None:
        appointment.status = appointment_data.status
    if appointment_data.reason is not None:
        appointment.reason = appointment_data.reason
    if appointment_data.notes is not None:
        appointment.notes = appointment_data.notes

    await db.commit()
    await db.refresh(appointment)

    logger.info(
        "appointment_updated_by_admin",
        appointment_id=appointment_id,
        admin_id=admin.id,
    )

    return AppointmentResponse.model_validate(appointment)


@router.delete("/appointments/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appointment_admin(
    appointment_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> None:
    """
    Delete any appointment.
    
    **Admin only.**
    """
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
    appointment = result.scalar_one_or_none()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    await db.delete(appointment)
    await db.commit()

    logger.info(
        "appointment_deleted_by_admin",
        appointment_id=appointment_id,
        admin_id=admin.id,
    )


@router.patch("/appointments/{appointment_id}/status", response_model=AppointmentResponse)
async def update_appointment_status(
    appointment_id: int,
    status: AppointmentStatus,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> AppointmentResponse:
    """
    Update appointment status.
    
    **Admin only.** Quick endpoint for changing appointment status.
    """
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
    appointment = result.scalar_one_or_none()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appointment.status = status

    await db.commit()
    await db.refresh(appointment)

    logger.info(
        "appointment_status_updated",
        appointment_id=appointment_id,
        new_status=status,
        admin_id=admin.id,
    )

    return AppointmentResponse.model_validate(appointment)


# ============================================================================
# SCHEDULE MANAGEMENT
# ============================================================================


@router.get("/doctors/{doctor_id}/schedule")
async def get_doctor_schedule(
    doctor_id: int,
    date_from: date = Query(..., description="Start date (YYYY-MM-DD)"),
    date_to: date = Query(..., description="End date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> dict:
    """
    Get doctor's schedule for a date range.
    
    **Admin only.** Shows all appointments and available slots.
    """
    # Verify doctor exists
    result = await db.execute(select(Provider).where(Provider.id == doctor_id))
    doctor = result.scalar_one_or_none()

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Get appointments in date range
    query = (
        select(Appointment, User)
        .join(User)
        .where(
            Appointment.provider_id == doctor_id,
            Appointment.time_start >= datetime.combine(date_from, time.min),
            Appointment.time_start <= datetime.combine(date_to, time.max),
        )
        .order_by(Appointment.time_start)
    )

    result = await db.execute(query)
    appointments = []
    
    for appt, user in result.all():
        appointments.append({
            "id": appt.id,
            "user_name": user.name,
            "user_email": user.email,
            "time_start": appt.time_start,
            "time_end": appt.time_end,
            "status": appt.status,
            "reason": appt.reason,
        })

    return {
        "doctor_id": doctor_id,
        "doctor_name": doctor.name,
        "date_from": date_from.isoformat(),
        "date_to": date_to.isoformat(),
        "appointments": appointments,
        "total_appointments": len(appointments),
    }


@router.put("/doctors/{doctor_id}/availability")
async def update_doctor_availability(
    doctor_id: int,
    availability_calendar_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> ProviderResponse:
    """
    Update doctor's availability calendar ID.
    
    **Admin only.** Used to link doctor with external scheduling system.
    """
    result = await db.execute(select(Provider).where(Provider.id == doctor_id))
    doctor = result.scalar_one_or_none()

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    doctor.availability_calendar_id = availability_calendar_id

    await db.commit()
    await db.refresh(doctor)

    logger.info(
        "doctor_availability_updated",
        doctor_id=doctor_id,
        admin_id=admin.id,
    )

    return ProviderResponse.model_validate(doctor)


@router.post("/doctors/{doctor_id}/block-time", response_model=AppointmentResponse)
async def block_doctor_time(
    doctor_id: int,
    time_start: datetime,
    time_end: datetime,
    reason: str = "Blocked by admin",
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> AppointmentResponse:
    """
    Block a time slot for a doctor.
    
    **Admin only.** Creates a special "blocked" appointment.
    """
    # Verify doctor exists
    result = await db.execute(select(Provider).where(Provider.id == doctor_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Create blocked appointment (using admin as user)
    appointment = Appointment(
        user_id=admin.id,
        provider_id=doctor_id,
        time_start=time_start,
        time_end=time_end,
        reason=reason,
        channel="web",
        status=AppointmentStatus.CONFIRMED,
        notes="Admin blocked time",
    )

    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)

    logger.info(
        "doctor_time_blocked",
        doctor_id=doctor_id,
        admin_id=admin.id,
        time_start=time_start,
        time_end=time_end,
    )

    return AppointmentResponse.model_validate(appointment)


# ============================================================================
# PATIENT MANAGEMENT
# ============================================================================


@router.get("/patients", response_model=list[dict])
async def list_all_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: str | None = Query(None, description="Search by name or email"),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> list[dict]:
    """
    List all patients with optional search.
    
    **Admin only.**
    """
    query = select(User).where(User.role == UserRole.PATIENT)

    if search:
        search_term = f"%{search}%"
        query = query.where(
            (User.name.ilike(search_term)) | (User.email.ilike(search_term))
        )

    query = query.offset(skip).limit(limit).order_by(User.name)

    result = await db.execute(query)
    patients = result.scalars().all()

    # Get appointment counts for each patient
    patient_list = []
    now_lebanon = datetime.now(LEBANON_TZ)
    
    for patient in patients:
        appt_result = await db.execute(
            select(Appointment).where(Appointment.user_id == patient.id)
        )
        appointments = appt_result.scalars().all()
        
        # Count upcoming appointments (check time_start exists and compare with aware datetime)
        upcoming_count = 0
        for appt in appointments:
            if appt.time_start:
                # Make sure time_start is timezone-aware
                appt_time = appt.time_start if appt.time_start.tzinfo else appt.time_start.replace(tzinfo=LEBANON_TZ)
                if appt_time > now_lebanon:
                    upcoming_count += 1
        
        # Get test result counts
        test_result = await db.execute(
            select(PatientTestResult).where(PatientTestResult.user_id == patient.id)
        )
        test_results = test_result.scalars().all()
        
        patient_list.append({
            "id": patient.id,
            "name": patient.name,
            "email": patient.email,
            "phone": patient.phone,
            "created_at": patient.created_at,
            "total_appointments": len(appointments),
            "upcoming_appointments": upcoming_count,
            "total_test_results": len(test_results),
        })

    return patient_list


@router.get("/patients/{patient_id}")
async def get_patient_details(
    patient_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> dict:
    """
    Get detailed patient information including appointments and test results.
    
    **Admin only.**
    """
    # Get patient
    result = await db.execute(
        select(User).where(User.id == patient_id, User.role == UserRole.PATIENT)
    )
    patient = result.scalar_one_or_none()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Get appointments with provider details
    appt_query = (
        select(Appointment, Provider)
        .join(Provider)
        .where(Appointment.user_id == patient_id)
        .order_by(Appointment.time_start.desc())
    )
    appt_result = await db.execute(appt_query)
    
    appointments = []
    for appt, provider in appt_result.all():
        appointments.append({
            "id": appt.id,
            "provider_name": provider.name,
            "provider_department": provider.department,
            "time_start": appt.time_start,
            "time_end": appt.time_end,
            "status": appt.status,
            "reason": appt.reason,
            "notes": appt.notes,
            "confirmation_code": appt.confirmation_code,
        })

    # Get test results
    from app.models.lab import LabTest
    
    test_query = (
        select(PatientTestResult, LabTest, Provider)
        .join(LabTest, PatientTestResult.lab_test_id == LabTest.id)
        .outerjoin(Provider, PatientTestResult.ordered_by_provider_id == Provider.id)
        .where(PatientTestResult.user_id == patient_id)
        .order_by(PatientTestResult.test_date.desc())
    )
    test_result = await db.execute(test_query)
    
    test_results = []
    for test, lab_test, provider in test_result.all():
        test_results.append({
            "id": test.id,
            "test_name": lab_test.name,
            "test_code": lab_test.code,
            "test_date": test.test_date,
            "result_value": test.result_value,
            "result_unit": test.result_unit,
            "reference_range": test.reference_range,
            "status": test.status,
            "notes": test.notes,
            "ordered_by": provider.name if provider else None,
        })

    return {
        "id": patient.id,
        "name": patient.name,
        "email": patient.email,
        "phone": patient.phone,
        "created_at": patient.created_at,
        "appointments": appointments,
        "test_results": test_results,
    }


# ============================================================================
# STATISTICS & REPORTING
# ============================================================================


@router.get("/stats/overview")
async def get_admin_stats(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> dict:
    """
    Get overall system statistics.
    
    **Admin only.**
    """
    # Count doctors
    doctor_result = await db.execute(select(Provider))
    total_doctors = len(doctor_result.scalars().all())

    # Count appointments
    appt_result = await db.execute(select(Appointment))
    appointments = appt_result.scalars().all()
    total_appointments = len(appointments)

    # Count by status
    status_counts = {}
    for status in AppointmentStatus:
        status_counts[status.value] = sum(1 for a in appointments if a.status == status)

    # Count users
    user_result = await db.execute(select(User))
    total_users = len(user_result.scalars().all())

    # Count upcoming appointments
    upcoming = sum(1 for a in appointments if a.time_start > datetime.now(LEBANON_TZ))

    return {
        "total_doctors": total_doctors,
        "total_appointments": total_appointments,
        "total_users": total_users,
        "upcoming_appointments": upcoming,
        "appointments_by_status": status_counts,
    }


# ============================================================================
# DATABASE POPULATION
# ============================================================================


@router.post("/populate-database", status_code=status.HTTP_200_OK)
async def populate_database(
    admin: User = Depends(require_admin),
) -> dict:
    """
    Populate database with comprehensive demo data.
    
    **Admin only.** This will:
    - Ensure admin@aub.com exists with password Admin@123
    - Clear existing demo data (except admin)
    - Create 30 patient accounts
    - Create 3+ providers per department
    - Create 22 lab tests
    - Create diverse appointments
    - Index all documents for RAG
    
    WARNING: This will delete existing data!
    """
    try:
        logger.info("database_population_started", admin_id=admin.id)
        
        # Import and run the population script
        # We'll use subprocess to run the script to avoid module conflicts
        import subprocess
        
        script_path = Path(__file__).parent.parent.parent.parent / "scripts" / "populate_demo_database.py"
        
        # Run the script
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            str(script_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_msg = stderr.decode() if stderr else "Unknown error"
            logger.error("database_population_failed", error=error_msg, admin_id=admin.id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database population failed: {error_msg}"
            )
        
        output = stdout.decode() if stdout else ""
        
        logger.info("database_population_completed", admin_id=admin.id)
        
        return {
            "success": True,
            "message": "Database populated successfully with demo data",
            "details": {
                "admin_email": "admin@aub.com",
                "admin_password": "Admin@123",
                "patients_created": 30,
                "providers_created": "3+ per department",
                "lab_tests_created": 22,
                "appointments_created": "Varied across time periods",
            },
            "output": output,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("database_population_error", error=str(e), admin_id=admin.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to populate database: {str(e)}"
        )


@router.post("/run-evaluation", status_code=status.HTTP_200_OK)
async def run_evaluation(
    admin: User = Depends(require_admin),
) -> dict:
    """
    Run the automated evaluation test suite.
    
    **Admin only.** Executes 25+ test cases and returns comprehensive report.
    """
    try:
        logger.info("evaluation_started", admin_id=admin.id)
        
        import subprocess
        
        script_path = Path(__file__).parent.parent.parent.parent / "tests" / "evaluation" / "run_eval.py"
        
        # Run the evaluation script
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            str(script_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_msg = stderr.decode() if stderr else "Unknown error"
            logger.error("evaluation_failed", error=error_msg, admin_id=admin.id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Evaluation failed: {error_msg}"
            )
        
        output = stdout.decode() if stdout else ""
        
        # Try to load the evaluation report
        report_path = Path("/app/data/evaluation_report.json")
        if report_path.exists():
            with open(report_path, "r") as f:
                report = json.load(f)
        else:
            report = {"error": "Report file not found"}
        
        logger.info("evaluation_completed", admin_id=admin.id)
        
        return {
            "success": True,
            "message": "Evaluation completed successfully",
            "report": report,
            "output": output
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("evaluation_error", error=str(e), admin_id=admin.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run evaluation: {str(e)}"
        )
