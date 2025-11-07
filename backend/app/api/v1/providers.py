"""Provider endpoints."""
from datetime import datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db import get_db
from app.core.logging import get_logger
from app.core.security import require_admin
from app.models import Provider, ProviderAvailability
from app.schemas.provider import ProviderCreate, ProviderResponse, ProviderTimeslots, ProviderUpdate
from app.services.mock_scheduling_client import MockSchedulingClient

router = APIRouter()
logger = get_logger(__name__)


@router.get("", response_model=list[ProviderResponse])
async def list_providers(
    department: str | None = Query(None),
    provider_type: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> list[ProviderResponse]:
    """List providers with optional filters."""
    query = select(Provider).options(selectinload(Provider.availability_schedule))

    if department:
        query = query.where(Provider.department.ilike(f"%{department}%"))
    if provider_type:
        query = query.where(Provider.type == provider_type)

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    providers = result.scalars().all()

    return [ProviderResponse.model_validate(p) for p in providers]


@router.get("/{provider_id}", response_model=ProviderResponse)
async def get_provider(provider_id: int, db: AsyncSession = Depends(get_db)) -> ProviderResponse:
    """Get provider by ID."""
    result = await db.execute(
        select(Provider)
        .options(selectinload(Provider.availability_schedule))
        .where(Provider.id == provider_id)
    )
    provider = result.scalar_one_or_none()

    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    return ProviderResponse.model_validate(provider)


@router.get("/{provider_id}/timeslots", response_model=ProviderTimeslots)
async def get_timeslots(
    provider_id: int,
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    db: AsyncSession = Depends(get_db),
) -> ProviderTimeslots:
    """Get available timeslots for a provider on a specific date."""
    # Validate date format
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    # Get provider with availability schedule
    result = await db.execute(
        select(Provider)
        .options(selectinload(Provider.availability_schedule))
        .where(Provider.id == provider_id)
    )
    provider = result.scalar_one_or_none()

    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    # Get day of week (0=Monday, 6=Sunday)
    day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    day_of_week = day_names[target_date.weekday()]
    
    # Find availability for this day
    day_availability = [
        slot for slot in provider.availability_schedule
        if slot.day_of_week.value == day_of_week
    ]
    
    slots = []
    
    if day_availability:
        # Generate 30-minute slots based on provider availability
        for avail in day_availability:
            current_time = datetime.combine(target_date, avail.start_time)
            end_datetime = datetime.combine(target_date, avail.end_time)
            
            while current_time < end_datetime:
                slot_end = current_time + timedelta(minutes=30)
                if slot_end <= end_datetime:
                    # Check if slot is already booked
                    from app.models import Appointment
                    booking_result = await db.execute(
                        select(Appointment).where(
                            Appointment.provider_id == provider_id,
                            Appointment.time_start == current_time,
                        )
                    )
                    is_booked = booking_result.scalar_one_or_none() is not None
                    
                    from app.schemas.provider import TimeSlot
                    slots.append(
                        TimeSlot(
                            slot_id=f"{provider_id}_{current_time.isoformat()}",
                            start=current_time,
                            end=slot_end,
                            available=not is_booked,
                        )
                    )
                
                current_time = slot_end

    return ProviderTimeslots(
        provider_id=provider.id,
        provider_name=provider.name,
        date=date,
        slots=slots,
    )


@router.post("", response_model=ProviderResponse, status_code=201)
async def create_provider(
    provider_data: ProviderCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin),
) -> ProviderResponse:
    """Create a new provider (admin only)."""
    provider = Provider(
        name=provider_data.name,
        department=provider_data.department,
        type=provider_data.type,
        specialty=provider_data.specialty,
        bio=provider_data.bio,
        availability_calendar_id=provider_data.availability_calendar_id,
    )
    
    db.add(provider)
    await db.flush()  # Get provider ID before adding availability
    
    # Add availability schedule
    for slot in provider_data.availability_schedule:
        availability = ProviderAvailability(
            provider_id=provider.id,
            day_of_week=slot.day_of_week,
            start_time=slot.start_time,
            end_time=slot.end_time,
        )
        db.add(availability)
    
    await db.commit()
    await db.refresh(provider)
    
    # Reload with availability
    result = await db.execute(
        select(Provider)
        .options(selectinload(Provider.availability_schedule))
        .where(Provider.id == provider.id)
    )
    provider = result.scalar_one()
    
    logger.info("provider_created", provider_id=provider.id, name=provider.name)
    
    return ProviderResponse.model_validate(provider)


@router.patch("/{provider_id}", response_model=ProviderResponse)
async def update_provider(
    provider_id: int,
    updates: ProviderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin),
) -> ProviderResponse:
    """Update a provider (admin only)."""
    result = await db.execute(
        select(Provider)
        .options(selectinload(Provider.availability_schedule))
        .where(Provider.id == provider_id)
    )
    provider = result.scalar_one_or_none()
    
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    # Update fields
    if updates.name is not None:
        provider.name = updates.name
    if updates.department is not None:
        provider.department = updates.department
    if updates.specialty is not None:
        provider.specialty = updates.specialty
    if updates.bio is not None:
        provider.bio = updates.bio
    if updates.availability_calendar_id is not None:
        provider.availability_calendar_id = updates.availability_calendar_id
    
    # Update availability schedule if provided
    if updates.availability_schedule is not None:
        # Delete existing schedule
        await db.execute(
            select(ProviderAvailability)
            .where(ProviderAvailability.provider_id == provider_id)
        )
        for existing in provider.availability_schedule:
            await db.delete(existing)
        
        # Add new schedule
        for slot in updates.availability_schedule:
            availability = ProviderAvailability(
                provider_id=provider.id,
                day_of_week=slot.day_of_week,
                start_time=slot.start_time,
                end_time=slot.end_time,
            )
            db.add(availability)
    
    await db.commit()
    await db.refresh(provider)
    
    # Reload with availability
    result = await db.execute(
        select(Provider)
        .options(selectinload(Provider.availability_schedule))
        .where(Provider.id == provider_id)
    )
    provider = result.scalar_one()
    
    logger.info("provider_updated", provider_id=provider.id, name=provider.name)
    
    return ProviderResponse.model_validate(provider)


@router.delete("/{provider_id}", status_code=204)
async def delete_provider(
    provider_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin),
) -> None:
    """Delete a provider (admin only)."""
    result = await db.execute(select(Provider).where(Provider.id == provider_id))
    provider = result.scalar_one_or_none()
    
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    await db.delete(provider)
    await db.commit()
    
    logger.info("provider_deleted", provider_id=provider_id)
