"""Booking event model for audit trail."""
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class BookingEventType(str, Enum):
    """Booking event types."""

    CREATED = "created"
    MODIFIED = "modified"
    CANCELLED = "cancelled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    NO_SHOW = "no_show"


class BookingEvent(Base):
    """Booking event for audit trail."""

    __tablename__ = "booking_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    appointment_id: Mapped[int] = mapped_column(
        ForeignKey("appointments.id"), nullable=False, index=True
    )
    type: Mapped[BookingEventType] = mapped_column(String(50), nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    performed_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    appointment: Mapped["Appointment"] = relationship("Appointment", back_populates="events")

    def __repr__(self) -> str:
        return (
            f"<BookingEvent(id={self.id}, appointment_id={self.appointment_id}, type={self.type})>"
        )
