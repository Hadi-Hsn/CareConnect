"""Email client for sending notifications via SMTP."""
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

import aiosmtplib

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class SMTPEmailClient:
    """SMTP email client."""

    async def send_email(
        self, to_email: str, subject: str, html_content: str, text_content: str | None = None
    ) -> bool:
        """Send email via SMTP."""
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = settings.email_from
            message["To"] = to_email

            if text_content:
                part1 = MIMEText(text_content, "plain")
                message.attach(part1)

            part2 = MIMEText(html_content, "html")
            message.attach(part2)

            await aiosmtplib.send(
                message,
                hostname=settings.smtp_host,
                port=settings.smtp_port,
                username=settings.smtp_user,
                password=settings.smtp_password,
                use_tls=True,
            )

            logger.info("email_sent", to=to_email, subject=subject, provider="smtp")
            return True

        except Exception as e:
            logger.error("email_send_failed", to=to_email, error=str(e), provider="smtp")
            return False


class EmailService:
    """Email service using SMTP."""

    def __init__(self) -> None:
        """Initialize email service."""
        self.client = SMTPEmailClient()
        logger.info("email_service_initialized", provider="smtp")

    async def send_confirmation(self, user_email: str, details: dict[str, Any]) -> bool:
        """Send appointment confirmation email."""
        subject = f"Appointment Confirmation - {details.get('confirmation_code', 'N/A')}"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2>Appointment Confirmed</h2>
            <p>Your appointment has been successfully scheduled.</p>
            
            <div style="background-color: #f4f4f4; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p><strong>Confirmation Code:</strong> {details.get('confirmation_code', 'N/A')}</p>
                <p><strong>Provider:</strong> {details.get('provider_name', 'N/A')}</p>
                <p><strong>Department:</strong> {details.get('department', 'N/A')}</p>
                <p><strong>Date & Time:</strong> {details.get('datetime', 'N/A')}</p>
                {f"<p><strong>Reason:</strong> {details.get('reason')}</p>" if details.get('reason') else ""}
            </div>
            
            <p>If you need to modify or cancel this appointment, please contact us or use the CareConnect portal.</p>
            
            <p style="color: #666; font-size: 12px; margin-top: 30px;">
                This is an automated message from CareConnect. Please do not reply to this email.
            </p>
        </body>
        </html>
        """

        text_content = f"""
        Appointment Confirmed
        
        Your appointment has been successfully scheduled.
        
        Confirmation Code: {details.get('confirmation_code', 'N/A')}
        Provider: {details.get('provider_name', 'N/A')}
        Department: {details.get('department', 'N/A')}
        Date & Time: {details.get('datetime', 'N/A')}
        {f"Reason: {details.get('reason')}" if details.get('reason') else ""}
        
        If you need to modify or cancel this appointment, please contact us or use the CareConnect portal.
        """

        return await self.client.send_email(user_email, subject, html_content, text_content)

    async def send_reminder(self, user_email: str, details: dict[str, Any]) -> bool:
        """Send appointment reminder email."""
        subject = "Appointment Reminder - CareConnect"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2>Appointment Reminder</h2>
            <p>This is a reminder about your upcoming appointment.</p>
            
            <div style="background-color: #f4f4f4; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p><strong>Provider:</strong> {details.get('provider_name', 'N/A')}</p>
                <p><strong>Department:</strong> {details.get('department', 'N/A')}</p>
                <p><strong>Date & Time:</strong> {details.get('datetime', 'N/A')}</p>
            </div>
            
            <p>Please arrive 15 minutes early for check-in.</p>
        </body>
        </html>
        """

        text_content = f"""
        Appointment Reminder
        
        This is a reminder about your upcoming appointment.
        
        Provider: {details.get('provider_name', 'N/A')}
        Department: {details.get('department', 'N/A')}
        Date & Time: {details.get('datetime', 'N/A')}
        
        Please arrive 15 minutes early for check-in.
        """

        return await self.client.send_email(user_email, subject, html_content, text_content)
