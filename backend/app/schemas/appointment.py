"""Appointment schemas."""
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.appointment import AppointmentChannel, AppointmentStatus


class AppointmentBase(BaseModel):
    """Base appointment schema."""

    provider_id: int
    time_start: datetime
    time_end: datetime
    reason: str | None = None


class AppointmentCreate(AppointmentBase):
    """Appointment creation schema."""

    user_id: int
    channel: AppointmentChannel = AppointmentChannel.WEB


class AppointmentUpdate(BaseModel):
    """Appointment update schema."""

    time_start: datetime | None = None
    time_end: datetime | None = None
    status: AppointmentStatus | None = None
    reason: str | None = None
    notes: str | None = None


class AppointmentResponse(AppointmentBase):
    """Appointment response schema."""

    id: int
    user_id: int
    status: AppointmentStatus
    channel: AppointmentChannel
    notes: str | None
    confirmation_code: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AppointmentWithDetails(AppointmentResponse):
    """Appointment with user and provider details."""

    user_name: str
    user_email: str
    provider_name: str
    provider_department: str


class BookingConfirmation(BaseModel):
    """Booking confirmation schema."""

    appointment: AppointmentResponse
    confirmation_code: str
    message: str
