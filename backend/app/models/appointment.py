"""Appointment model."""
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class AppointmentStatus(str, Enum):
    """Appointment status."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"


class AppointmentChannel(str, Enum):
    """Channel through which appointment was created."""

    WEB = "web"
    PHONE = "phone"
    AGENT = "agent"


class Appointment(Base):
    """Appointment model."""

    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    provider_id: Mapped[int] = mapped_column(
        ForeignKey("providers.id"), nullable=False, index=True
    )
    time_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    time_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[AppointmentStatus] = mapped_column(
        String(50), default=AppointmentStatus.PENDING, nullable=False
    )
    channel: Mapped[AppointmentChannel] = mapped_column(String(50), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    confirmation_code: Mapped[str | None] = mapped_column(String(50), nullable=True, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="appointments")
    provider: Mapped["Provider"] = relationship("Provider", back_populates="appointments")
    events: Mapped[list["BookingEvent"]] = relationship(
        "BookingEvent", back_populates="appointment", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<Appointment(id={self.id}, user_id={self.user_id}, "
            f"provider_id={self.provider_id}, status={self.status})>"
        )
