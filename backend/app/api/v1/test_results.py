"""Patient test results endpoints."""
from datetime import datetime
from io import BytesIO

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.db import get_db
from app.core.logging import get_logger
from app.core.security import get_current_user, require_admin
from app.models import PatientTestResult, Provider, User
from app.schemas.test_result import (
    TestResultCreate,
    TestResultResponse,
    TestResultUpdate,
    TestResultWithProvider,
)

router = APIRouter()
logger = get_logger(__name__)


# ============================================================================
# PATIENT ENDPOINTS - View own results
# ============================================================================


@router.get("/my-results", response_model=list[TestResultWithProvider])
async def get_my_test_results(
    status_filter: str | None = Query(None, description="Filter by status"),
    category: str | None = Query(None, description="Filter by category"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TestResultWithProvider]:
    """
    Get current user's test results.
    
    Returns test results for the authenticated user with optional filters.
    """
    query = select(PatientTestResult).where(PatientTestResult.user_id == current_user.id)
    
    if status_filter:
        query = query.where(PatientTestResult.status == status_filter)
    if category:
        query = query.where(PatientTestResult.test_category.ilike(f"%{category}%"))
    
    query = query.order_by(PatientTestResult.test_date.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    test_results = result.scalars().all()
    
    # Build response with provider info
    response = []
    for tr in test_results:
        provider_name = None
        provider_specialty = None
        
        if tr.ordered_by_provider_id:
            provider_result = await db.execute(
                select(Provider).where(Provider.id == tr.ordered_by_provider_id)
            )
            provider = provider_result.scalar_one_or_none()
            if provider:
                provider_name = provider.name
                provider_specialty = provider.specialty
        
        response.append(TestResultWithProvider(
            id=tr.id,
            user_id=tr.user_id,
            lab_test_id=tr.lab_test_id,
            ordered_by_provider_id=tr.ordered_by_provider_id,
            test_name=tr.test_name,
            test_category=tr.test_category,
            test_date=tr.test_date,
            result_value=tr.result_value,
            result_unit=tr.result_unit,
            reference_range=tr.reference_range,
            status=tr.status,
            notes=tr.notes,
            has_pdf=tr.pdf_data is not None,
            pdf_filename=tr.pdf_filename,
            created_at=tr.created_at,
            updated_at=tr.updated_at,
            provider_name=provider_name,
            provider_specialty=provider_specialty,
        ))
    
    return response


@router.get("/my-results/{result_id}", response_model=TestResultWithProvider)
async def get_my_test_result(
    result_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TestResultWithProvider:
    """Get a specific test result for the current user."""
    result = await db.execute(
        select(PatientTestResult).where(
            PatientTestResult.id == result_id,
            PatientTestResult.user_id == current_user.id,
        )
    )
    test_result = result.scalar_one_or_none()
    
    if not test_result:
        raise HTTPException(status_code=404, detail="Test result not found")
    
    provider_name = None
    provider_specialty = None
    
    if test_result.ordered_by_provider_id:
        provider_result = await db.execute(
            select(Provider).where(Provider.id == test_result.ordered_by_provider_id)
        )
        provider = provider_result.scalar_one_or_none()
        if provider:
            provider_name = provider.name
            provider_specialty = provider.specialty
    
    return TestResultWithProvider(
        id=test_result.id,
        user_id=test_result.user_id,
        lab_test_id=test_result.lab_test_id,
        ordered_by_provider_id=test_result.ordered_by_provider_id,
        test_name=test_result.test_name,
        test_category=test_result.test_category,
        test_date=test_result.test_date,
        result_value=test_result.result_value,
        result_unit=test_result.result_unit,
        reference_range=test_result.reference_range,
        status=test_result.status,
        notes=test_result.notes,
        has_pdf=test_result.pdf_data is not None,
        pdf_filename=test_result.pdf_filename,
        created_at=test_result.created_at,
        updated_at=test_result.updated_at,
        provider_name=provider_name,
        provider_specialty=provider_specialty,
    )


@router.get("/my-results/{result_id}/pdf")
async def download_my_test_result_pdf(
    result_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download PDF for a specific test result."""
    result = await db.execute(
        select(PatientTestResult).where(
            PatientTestResult.id == result_id,
            PatientTestResult.user_id == current_user.id,
        )
    )
    test_result = result.scalar_one_or_none()
    
    if not test_result:
        raise HTTPException(status_code=404, detail="Test result not found")
    
    if not test_result.pdf_data:
        raise HTTPException(status_code=404, detail="No PDF available for this test result")
    
    filename = test_result.pdf_filename or f"test_result_{result_id}.pdf"
    
    return StreamingResponse(
        BytesIO(test_result.pdf_data),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/my-results/categories/list")
async def get_my_result_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[str]:
    """Get list of unique test categories for current user."""
    result = await db.execute(
        select(PatientTestResult.test_category)
        .where(PatientTestResult.user_id == current_user.id)
        .distinct()
    )
    categories = result.scalars().all()
    return list(categories)


# ============================================================================
# ADMIN ENDPOINTS - Manage all results
# ============================================================================


@router.get("/admin/results", response_model=list[TestResultResponse])
async def list_all_test_results(
    user_id: int | None = Query(None),
    status_filter: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> list[TestResultResponse]:
    """
    List all test results (admin only).
    """
    query = select(PatientTestResult)
    
    if user_id:
        query = query.where(PatientTestResult.user_id == user_id)
    if status_filter:
        query = query.where(PatientTestResult.status == status_filter)
    
    query = query.order_by(PatientTestResult.test_date.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    test_results = result.scalars().all()
    
    return [
        TestResultResponse(
            id=tr.id,
            user_id=tr.user_id,
            lab_test_id=tr.lab_test_id,
            ordered_by_provider_id=tr.ordered_by_provider_id,
            test_name=tr.test_name,
            test_category=tr.test_category,
            test_date=tr.test_date,
            result_value=tr.result_value,
            result_unit=tr.result_unit,
            reference_range=tr.reference_range,
            status=tr.status,
            notes=tr.notes,
            has_pdf=tr.pdf_data is not None,
            pdf_filename=tr.pdf_filename,
            created_at=tr.created_at,
            updated_at=tr.updated_at,
        )
        for tr in test_results
    ]


@router.post("/admin/results", response_model=TestResultResponse, status_code=status.HTTP_201_CREATED)
async def create_test_result(
    result_data: TestResultCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> TestResultResponse:
    """
    Create a new test result (admin only).
    """
    # Verify user exists
    user_result = await db.execute(select(User).where(User.id == result_data.user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    test_result = PatientTestResult(
        user_id=result_data.user_id,
        lab_test_id=result_data.lab_test_id,
        ordered_by_provider_id=result_data.ordered_by_provider_id,
        test_name=result_data.test_name,
        test_category=result_data.test_category,
        test_date=result_data.test_date,
        result_value=result_data.result_value,
        result_unit=result_data.result_unit,
        reference_range=result_data.reference_range,
        status=result_data.status,
        notes=result_data.notes,
    )
    
    db.add(test_result)
    await db.commit()
    await db.refresh(test_result)
    
    logger.info(
        "test_result_created",
        result_id=test_result.id,
        user_id=test_result.user_id,
        admin_id=admin.id,
    )
    
    return TestResultResponse(
        id=test_result.id,
        user_id=test_result.user_id,
        lab_test_id=test_result.lab_test_id,
        ordered_by_provider_id=test_result.ordered_by_provider_id,
        test_name=test_result.test_name,
        test_category=test_result.test_category,
        test_date=test_result.test_date,
        result_value=test_result.result_value,
        result_unit=test_result.result_unit,
        reference_range=test_result.reference_range,
        status=test_result.status,
        notes=test_result.notes,
        has_pdf=False,
        pdf_filename=None,
        created_at=test_result.created_at,
        updated_at=test_result.updated_at,
    )


@router.post("/admin/results/{result_id}/upload-pdf", response_model=TestResultResponse)
async def upload_test_result_pdf(
    result_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> TestResultResponse:
    """
    Upload PDF for a test result (admin only).
    """
    # Validate file type
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Get test result
    result = await db.execute(
        select(PatientTestResult).where(PatientTestResult.id == result_id)
    )
    test_result = result.scalar_one_or_none()
    
    if not test_result:
        raise HTTPException(status_code=404, detail="Test result not found")
    
    # Read and store PDF
    pdf_content = await file.read()
    test_result.pdf_data = pdf_content
    test_result.pdf_filename = file.filename
    
    await db.commit()
    await db.refresh(test_result)
    
    logger.info(
        "test_result_pdf_uploaded",
        result_id=result_id,
        filename=file.filename,
        admin_id=admin.id,
    )
    
    return TestResultResponse(
        id=test_result.id,
        user_id=test_result.user_id,
        lab_test_id=test_result.lab_test_id,
        ordered_by_provider_id=test_result.ordered_by_provider_id,
        test_name=test_result.test_name,
        test_category=test_result.test_category,
        test_date=test_result.test_date,
        result_value=test_result.result_value,
        result_unit=test_result.result_unit,
        reference_range=test_result.reference_range,
        status=test_result.status,
        notes=test_result.notes,
        has_pdf=True,
        pdf_filename=test_result.pdf_filename,
        created_at=test_result.created_at,
        updated_at=test_result.updated_at,
    )


@router.post("/admin/results/upload-with-pdf", response_model=TestResultResponse, status_code=status.HTTP_201_CREATED)
async def create_test_result_with_pdf(
    user_id: int,
    test_name: str,
    test_date: datetime,
    test_category: str = "General",
    result_value: str | None = None,
    result_unit: str | None = None,
    reference_range: str | None = None,
    notes: str | None = None,
    ordered_by_provider_id: int | None = None,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> TestResultResponse:
    """
    Create a new test result with PDF upload in one step (admin only).
    """
    # Validate file type
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Verify user exists
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Read PDF
    pdf_content = await file.read()
    
    test_result = PatientTestResult(
        user_id=user_id,
        ordered_by_provider_id=ordered_by_provider_id,
        test_name=test_name,
        test_category=test_category,
        test_date=test_date,
        result_value=result_value,
        result_unit=result_unit,
        reference_range=reference_range,
        status="completed",
        notes=notes,
        pdf_data=pdf_content,
        pdf_filename=file.filename,
    )
    
    db.add(test_result)
    await db.commit()
    await db.refresh(test_result)
    
    logger.info(
        "test_result_created_with_pdf",
        result_id=test_result.id,
        user_id=user_id,
        filename=file.filename,
        admin_id=admin.id,
    )
    
    return TestResultResponse(
        id=test_result.id,
        user_id=test_result.user_id,
        lab_test_id=test_result.lab_test_id,
        ordered_by_provider_id=test_result.ordered_by_provider_id,
        test_name=test_result.test_name,
        test_category=test_result.test_category,
        test_date=test_result.test_date,
        result_value=test_result.result_value,
        result_unit=test_result.result_unit,
        reference_range=test_result.reference_range,
        status=test_result.status,
        notes=test_result.notes,
        has_pdf=True,
        pdf_filename=test_result.pdf_filename,
        created_at=test_result.created_at,
        updated_at=test_result.updated_at,
    )


@router.put("/admin/results/{result_id}", response_model=TestResultResponse)
async def update_test_result(
    result_id: int,
    result_data: TestResultUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
) -> TestResultResponse:
    """
    Update a test result (admin only).
    """
    result = await db.execute(
        select(PatientTestResult).where(PatientTestResult.id == result_id)
    )
    test_result = result.scalar_one_or_none()
    
    if not test_result:
        raise HTTPException(status_code=404, detail="Test result not found")
    
    # Update fields
    if result_data.test_name is not None:
        test_result.test_name = result_data.test_name
    if result_data.test_category is not None:
        test_result.test_category = result_data.test_category
    if result_data.result_value is not None:
        test_result.result_value = result_data.result_value
    if result_data.result_unit is not None:
        test_result.result_unit = result_data.result_unit
    if result_data.reference_range is not None:
        test_result.reference_range = result_data.reference_range
    if result_data.status is not None:
        test_result.status = result_data.status
    if result_data.notes is not None:
        test_result.notes = result_data.notes
    
    await db.commit()
    await db.refresh(test_result)
    
    logger.info(
        "test_result_updated",
        result_id=result_id,
        admin_id=admin.id,
    )
    
    return TestResultResponse(
        id=test_result.id,
        user_id=test_result.user_id,
        lab_test_id=test_result.lab_test_id,
        ordered_by_provider_id=test_result.ordered_by_provider_id,
        test_name=test_result.test_name,
        test_category=test_result.test_category,
        test_date=test_result.test_date,
        result_value=test_result.result_value,
        result_unit=test_result.result_unit,
        reference_range=test_result.reference_range,
        status=test_result.status,
        notes=test_result.notes,
        has_pdf=test_result.pdf_data is not None,
        pdf_filename=test_result.pdf_filename,
        created_at=test_result.created_at,
        updated_at=test_result.updated_at,
    )


@router.delete("/admin/results/{result_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_result(
    result_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    Delete a test result (admin only).
    """
    result = await db.execute(
        select(PatientTestResult).where(PatientTestResult.id == result_id)
    )
    test_result = result.scalar_one_or_none()
    
    if not test_result:
        raise HTTPException(status_code=404, detail="Test result not found")
    
    await db.delete(test_result)
    await db.commit()
    
    logger.info(
        "test_result_deleted",
        result_id=result_id,
        admin_id=admin.id,
    )
