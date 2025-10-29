"""Lab test schemas."""
from datetime import datetime

from pydantic import BaseModel, Field


class LabTestBase(BaseModel):
    """Base lab test schema."""

    name: str = Field(..., min_length=1, max_length=255)
    code: str = Field(..., min_length=1, max_length=50)
    department: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    prep_instructions: str | None = None
    fasting_hours: int | None = Field(None, ge=0)
    estimated_duration_minutes: int = Field(30, ge=1)


class LabTestCreate(LabTestBase):
    """Lab test creation schema."""

    pass


class LabTestUpdate(BaseModel):
    """Lab test update schema."""

    name: str | None = None
    description: str | None = None
    prep_instructions: str | None = None
    fasting_hours: int | None = Field(None, ge=0)
    estimated_duration_minutes: int | None = Field(None, ge=1)


class LabTestResponse(LabTestBase):
    """Lab test response schema."""

    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
