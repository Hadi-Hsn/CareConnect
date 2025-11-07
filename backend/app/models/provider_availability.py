"""Provider availability model."""
from datetime import datetime, time, timezone
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class DayOfWeek(str, Enum):
    """Days of the week."""

    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class ProviderAvailability(Base):
    """Provider weekly availability schedule."""

    __tablename__ = "provider_availability"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    provider_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("providers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    day_of_week: Mapped[DayOfWeek] = mapped_column(String(20), nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
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
    provider: Mapped["Provider"] = relationship("Provider", back_populates="availability_schedule")

    def __repr__(self) -> str:
        return f"<ProviderAvailability(provider_id={self.provider_id}, day={self.day_of_week}, {self.start_time}-{self.end_time})>"
