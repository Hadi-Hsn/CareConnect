"""Test script to validate SendGrid email configuration."""
import asyncio
import sys
from pathlib import Path

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.email_client import EmailService
from app.core.logging import get_logger

logger = get_logger(__name__)


async def main():
    """Send a test email to validate SendGrid configuration."""
    email_service = EmailService()
    
    test_email = "hadi.wmail@gmail.com"
    
    logger.info("sending_test_email", to=test_email)
    
    # Send a test email
    success = await email_service.send_confirmation(
        user_email=test_email,
        details={
            "confirmation_code": "TEST-12345",
            "provider_name": "Dr. Sarah Johnson",
            "department": "Cardiology",
            "datetime": "November 5, 2025 at 10:00 AM",
            "reason": "SendGrid Integration Test - This is a test email to validate the SendGrid configuration"
        }
    )
    
    if success:
        logger.info("test_email_sent_successfully", to=test_email)
        print(f"\n✅ SUCCESS: Test email sent successfully to {test_email}")
        print("Please check your inbox (and spam folder) for the confirmation email.")
    else:
        logger.error("test_email_failed", to=test_email)
        print(f"\n❌ FAILED: Unable to send test email to {test_email}")
        print("Please check the logs for more details.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
