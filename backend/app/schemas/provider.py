"""Provider schemas."""
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.provider import ProviderType


class ProviderBase(BaseModel):
    """Base provider schema."""

    name: str = Field(..., min_length=1, max_length=255)
    department: str = Field(..., min_length=1, max_length=255)
    type: ProviderType
    specialty: str | None = Field(None, max_length=255)
    bio: str | None = None


class ProviderCreate(ProviderBase):
    """Provider creation schema."""

    availability_calendar_id: str | None = None


class ProviderUpdate(BaseModel):
    """Provider update schema."""

    name: str | None = Field(None, min_length=1, max_length=255)
    department: str | None = None
    specialty: str | None = None
    bio: str | None = None
    availability_calendar_id: str | None = None


class ProviderResponse(ProviderBase):
    """Provider response schema."""

    id: int
    availability_calendar_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TimeSlot(BaseModel):
    """Time slot schema."""

    slot_id: str
    start: datetime
    end: datetime
    available: bool


class ProviderTimeslots(BaseModel):
    """Provider timeslots response."""

    provider_id: int
    provider_name: str
    date: str
    slots: list[TimeSlot]
