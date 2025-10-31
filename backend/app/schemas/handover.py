"""Handover schemas."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.handover import IncidentPriority, IncidentStatus


class HandoverRequest(BaseModel):
    """Handover request from patient."""

    messages: list[dict[str, Any]] = Field(..., description="Full conversation history")
    subject: str = Field(..., max_length=500, description="Brief subject/reason for handover")
    patient_phone: str | None = Field(None, max_length=50, description="Patient phone number")
    priority: IncidentPriority = Field(
        default=IncidentPriority.MEDIUM,
        description="Urgency level"
    )


class HandoverResponse(BaseModel):
    """Handover response."""

    incident_id: int
    status: IncidentStatus
    message: str
    confirmation_code: str
    estimated_response_time: str = "within 24 hours"


class IncidentDetail(BaseModel):
    """Detailed incident information for admin."""

    id: int
    user_id: int
    patient_name: str
    patient_email: str
    patient_phone: str | None
    subject: str
    chat_summary: str
    full_conversation: str
    priority: IncidentPriority
    status: IncidentStatus
    assigned_to: int | None
    assigned_admin_name: str | None = None
    admin_notes: str | None
    resolution: str | None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None

    class Config:
        from_attributes = True


class IncidentListItem(BaseModel):
    """Incident list item for admin dashboard."""

    id: int
    patient_name: str
    patient_email: str
    subject: str
    priority: IncidentPriority
    status: IncidentStatus
    created_at: datetime
    assigned_to: int | None
    assigned_admin_name: str | None = None

    class Config:
        from_attributes = True


class IncidentUpdate(BaseModel):
    """Update incident."""

    status: IncidentStatus | None = None
    priority: IncidentPriority | None = None
    assigned_to: int | None = None
    admin_notes: str | None = None
    resolution: str | None = None


class IncidentStats(BaseModel):
    """Incident statistics for admin dashboard."""

    total_incidents: int
    pending_count: int
    in_progress_count: int
    resolved_count: int
    avg_resolution_time_hours: float | None
    high_priority_count: int
    urgent_count: int
