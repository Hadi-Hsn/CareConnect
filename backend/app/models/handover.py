"""Handover incident model."""
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class IncidentStatus(str, Enum):
    """Incident status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IncidentPriority(str, Enum):
    """Incident priority."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class HandoverIncident(Base):
    """Handover incident model for human escalation."""

    __tablename__ = "handover_incidents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Patient contact info
    patient_name: Mapped[str] = mapped_column(String(255), nullable=False)
    patient_email: Mapped[str] = mapped_column(String(255), nullable=False)
    patient_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    # Incident details
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    chat_summary: Mapped[str] = mapped_column(Text, nullable=False)
    full_conversation: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string
    priority: Mapped[IncidentPriority] = mapped_column(
        String(50), default=IncidentPriority.MEDIUM, nullable=False
    )
    status: Mapped[IncidentStatus] = mapped_column(
        String(50), default=IncidentStatus.PENDING, nullable=False
    )
    
    # Assignment
    assigned_to: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Notes and resolution
    admin_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolution: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], backref="handover_incidents")
    assigned_admin: Mapped["User"] = relationship(
        "User", foreign_keys=[assigned_to], backref="assigned_incidents"
    )

    def __repr__(self) -> str:
        return f"<HandoverIncident(id={self.id}, user_id={self.user_id}, status={self.status})>"
