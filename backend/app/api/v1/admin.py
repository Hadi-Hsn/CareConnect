"""Admin endpoints for managing doctors, appointments, and schedules."""
from datetime import date, datetime, time

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.logging import get_logger
from app.core.security import require_admin
from app.models import Appointment, Provider, User
from app.models.appointment import AppointmentStatus
from app.models.provider import ProviderType
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

router = APIRouter()
logger = get_logger(__name__)


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
            Appointment.time_start > datetime.now(),
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
    upcoming = sum(1 for a in appointments if a.time_start > datetime.now())

    return {
        "total_doctors": total_doctors,
        "total_appointments": total_appointments,
        "total_users": total_users,
        "upcoming_appointments": upcoming,
        "appointments_by_status": status_counts,
    }
