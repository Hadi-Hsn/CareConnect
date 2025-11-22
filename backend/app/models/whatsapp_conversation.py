"""WhatsApp conversation history model."""
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class WhatsAppMessage(Base):
    """WhatsApp message history."""

    __tablename__ = "whatsapp_messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    phone_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # 'user' or 'assistant'
    content: Mapped[str] = mapped_column(Text, nullable=False)
    message_sid: Mapped[str | None] = mapped_column(String(100), nullable=True)  # Twilio message ID
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="whatsapp_messages")

    def __repr__(self) -> str:
        return f"<WhatsAppMessage(id={self.id}, user_id={self.user_id}, role={self.role})>"
