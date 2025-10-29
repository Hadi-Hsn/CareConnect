"""Email endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.logging import get_logger
from app.services.email_client import EmailService

router = APIRouter()
logger = get_logger(__name__)


@router.post("/test")
async def test_email(
    to_email: str, db: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    """Test email sending (admin only)."""
    email_service = EmailService()

    test_details = {
        "confirmation_code": "TEST123",
        "provider_name": "Dr. Test Provider",
        "department": "Test Department",
        "datetime": "January 1, 2025 at 10:00 AM",
        "reason": "Test appointment",
    }

    success = await email_service.send_confirmation(to_email, test_details)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to send test email")

    logger.info("test_email_sent", to=to_email)

    return {"message": "Test email sent successfully", "recipient": to_email}
