"""Appointment endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.logging import get_logger
from app.models import Appointment, AppointmentStatus, Provider, User
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentUpdate,
    AppointmentWithDetails,
)

router = APIRouter()
logger = get_logger(__name__)


@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment_data: AppointmentCreate, db: AsyncSession = Depends(get_db)
) -> AppointmentResponse:
    """Create a new appointment."""
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
    )

    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)

    logger.info("appointment_created", appointment_id=appointment.id)

    return AppointmentResponse.model_validate(appointment)


@router.get("", response_model=list[AppointmentWithDetails])
async def list_appointments(
    user_id: int | None = Query(None),
    provider_id: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> list[AppointmentWithDetails]:
    """List appointments with filters."""
    query = select(Appointment, User, Provider).join(User).join(Provider)

    if user_id:
        query = query.where(Appointment.user_id == user_id)
    if provider_id:
        query = query.where(Appointment.provider_id == provider_id)

    query = query.offset(skip).limit(limit)

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


@router.get("/{appointment_id}", response_model=AppointmentWithDetails)
async def get_appointment(
    appointment_id: int, db: AsyncSession = Depends(get_db)
) -> AppointmentWithDetails:
    """Get appointment by ID."""
    result = await db.execute(
        select(Appointment, User, Provider)
        .join(User)
        .join(Provider)
        .where(Appointment.id == appointment_id)
    )
    row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appt, user, provider = row
    appt_dict = AppointmentResponse.model_validate(appt).model_dump()
    appt_dict.update(
        {
            "user_name": user.name,
            "user_email": user.email,
            "provider_name": provider.name,
            "provider_department": provider.department,
        }
    )

    return AppointmentWithDetails(**appt_dict)


@router.patch("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    db: AsyncSession = Depends(get_db),
) -> AppointmentResponse:
    """Update an appointment."""
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

    logger.info("appointment_updated", appointment_id=appointment_id)

    return AppointmentResponse.model_validate(appointment)


@router.delete("/clear-cancelled", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cancelled_appointments(
    user_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete cancelled appointments. Patients can clear their own, admins can specify user_id.
    
    SAFETY: This endpoint ONLY deletes appointments with status='cancelled'.
    The WHERE clause explicitly filters for AppointmentStatus.CANCELLED, ensuring
    confirmed, pending, completed, and no_show appointments are NEVER deleted.
    """
    try:
        # Build delete query with explicit status filter for safety
        # CRITICAL: Only delete appointments with status='cancelled'
        delete_query = delete(Appointment).where(Appointment.status == AppointmentStatus.CANCELLED)
        if user_id is not None:
            delete_query = delete_query.where(Appointment.user_id == user_id)
        
        # Execute the delete
        result = await db.execute(delete_query)
        count = result.rowcount
        
        await db.commit()
        logger.info(
            "cancelled_appointments_cleared",
            count=count,
            user_id=user_id,
            status_filter="cancelled_only",
        )
    except Exception as e:
        logger.error("error_clearing_cancelled_appointments", error=str(e), user_id=user_id, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cancelled appointments: {str(e)}",
        )


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appointment(appointment_id: int, db: AsyncSession = Depends(get_db)) -> None:
    """Delete an appointment."""
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
    appointment = result.scalar_one_or_none()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    await db.delete(appointment)
    await db.commit()

    logger.info("appointment_deleted", appointment_id=appointment_id)
