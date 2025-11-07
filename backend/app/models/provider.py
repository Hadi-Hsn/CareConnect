"""Provider model."""
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class ProviderType(str, Enum):
    """Provider types."""

    PHYSICIAN = "physician"
    NURSE_PRACTITIONER = "nurse_practitioner"
    PHYSICIAN_ASSISTANT = "physician_assistant"
    SPECIALIST = "specialist"
    THERAPIST = "therapist"


class Provider(Base):
    """Provider (doctor, specialist) model."""

    __tablename__ = "providers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    department: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    type: Mapped[ProviderType] = mapped_column(String(50), nullable=False)
    specialty: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    availability_calendar_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
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
    appointments: Mapped[list["Appointment"]] = relationship(
        "Appointment", back_populates="provider"
    )
    availability_schedule: Mapped[list["ProviderAvailability"]] = relationship(
        "ProviderAvailability", back_populates="provider", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Provider(id={self.id}, name={self.name}, dept={self.department})>"
