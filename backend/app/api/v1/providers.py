"""Provider endpoints."""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.logging import get_logger
from app.models import Provider
from app.schemas.provider import ProviderResponse, ProviderTimeslots
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
    query = select(Provider)

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
    result = await db.execute(select(Provider).where(Provider.id == provider_id))
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

    # Get provider
    result = await db.execute(select(Provider).where(Provider.id == provider_id))
    provider = result.scalar_one_or_none()

    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    # Get timeslots
    scheduling_client = MockSchedulingClient()
    slots = await scheduling_client.get_timeslots(provider_id, target_date)

    return ProviderTimeslots(
        provider_id=provider.id,
        provider_name=provider.name,
        date=date,
        slots=slots,
    )
