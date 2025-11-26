"""Provider schemas."""
from datetime import datetime, time

from pydantic import BaseModel, Field

from app.models.provider import ProviderType
from app.models.provider_availability import DayOfWeek


class ProviderBase(BaseModel):
    """Base provider schema."""

    name: str = Field(..., min_length=1, max_length=255)
    department: str = Field(..., min_length=1, max_length=255)
    type: ProviderType
    specialty: str | None = Field(None, max_length=255)
    bio: str | None = None


class AvailabilitySlot(BaseModel):
    """Weekly availability slot schema."""

    day_of_week: DayOfWeek
    start_time: time
    end_time: time

    model_config = {"from_attributes": True}


class ProviderCreate(ProviderBase):
    """Provider creation schema."""

    availability_calendar_id: str | None = None
    availability_schedule: list[AvailabilitySlot] = Field(default_factory=list)


class ProviderUpdate(BaseModel):
    """Provider update schema."""

    name: str | None = Field(None, min_length=1, max_length=255)
    department: str | None = None
    specialty: str | None = None
    bio: str | None = None
    availability_calendar_id: str | None = None
    availability_schedule: list[AvailabilitySlot] | None = None


class ProviderResponse(ProviderBase):
    """Provider response schema."""

    id: int
    availability_calendar_id: str | None
    created_at: datetime
    availability_schedule: list[AvailabilitySlot] = Field(default_factory=list)

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
