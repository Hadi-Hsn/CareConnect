"""Lab test endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.models import LabTest
from app.schemas.lab import LabTestResponse

router = APIRouter()


@router.get("", response_model=list[LabTestResponse])
async def list_lab_tests(
    department: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> list[LabTestResponse]:
    """List lab tests with optional filters."""
    query = select(LabTest)

    if department:
        query = query.where(LabTest.department.ilike(f"%{department}%"))

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    lab_tests = result.scalars().all()

    return [LabTestResponse.model_validate(lt) for lt in lab_tests]


@router.get("/{test_id}", response_model=LabTestResponse)
async def get_lab_test(test_id: int, db: AsyncSession = Depends(get_db)) -> LabTestResponse:
    """Get lab test by ID."""
    result = await db.execute(select(LabTest).where(LabTest.id == test_id))
    lab_test = result.scalar_one_or_none()

    if not lab_test:
        raise HTTPException(status_code=404, detail="Lab test not found")

    return LabTestResponse.model_validate(lab_test)
