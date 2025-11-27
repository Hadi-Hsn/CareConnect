"""Patient test result schemas."""
from datetime import datetime

from pydantic import BaseModel, Field


class TestResultBase(BaseModel):
    """Base test result schema."""

    test_name: str = Field(..., min_length=1, max_length=255)
    test_category: str = Field("General", max_length=100)
    test_date: datetime
    result_value: str | None = None
    result_unit: str | None = None
    reference_range: str | None = None
    status: str = Field("completed", pattern="^(pending|completed|reviewed)$")
    notes: str | None = None


class TestResultCreate(TestResultBase):
    """Test result creation schema."""

    user_id: int
    lab_test_id: int | None = None
    ordered_by_provider_id: int | None = None


class TestResultUpdate(BaseModel):
    """Test result update schema."""

    test_name: str | None = None
    test_category: str | None = None
    result_value: str | None = None
    result_unit: str | None = None
    reference_range: str | None = None
    status: str | None = None
    notes: str | None = None


class TestResultResponse(TestResultBase):
    """Test result response schema."""

    id: int
    user_id: int
    lab_test_id: int | None = None
    ordered_by_provider_id: int | None = None
    has_pdf: bool = False
    pdf_filename: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TestResultListResponse(BaseModel):
    """Test result list response with summary info."""

    id: int
    test_name: str
    test_category: str
    test_date: datetime
    status: str
    has_pdf: bool
    provider_name: str | None = None

    model_config = {"from_attributes": True}


class TestResultWithProvider(TestResultResponse):
    """Test result with provider details."""

    provider_name: str | None = None
    provider_specialty: str | None = None

    model_config = {"from_attributes": True}
