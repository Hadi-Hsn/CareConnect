"""Patient test result model."""
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class PatientTestResult(Base):
    """Patient lab test result model."""

    __tablename__ = "patient_test_results"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    lab_test_id: Mapped[int | None] = mapped_column(ForeignKey("lab_tests.id"), nullable=True)
    ordered_by_provider_id: Mapped[int | None] = mapped_column(ForeignKey("providers.id"), nullable=True)
    
    # Test details
    test_name: Mapped[str] = mapped_column(String(255), nullable=False)  # Display name for the test
    test_category: Mapped[str] = mapped_column(String(100), default="General", nullable=False)  # Category like Blood, Imaging, etc.
    test_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    result_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    result_unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    reference_range: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)  # pending, completed, reviewed
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # PDF storage
    pdf_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pdf_data: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)  # Store PDF binary data
    
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
    user: Mapped["User"] = relationship("User", back_populates="test_results")
    lab_test: Mapped["LabTest"] = relationship("LabTest")
    ordered_by: Mapped["Provider | None"] = relationship("Provider")

    def __repr__(self) -> str:
        return f"<PatientTestResult(id={self.id}, user_id={self.user_id}, test_date={self.test_date})>"
