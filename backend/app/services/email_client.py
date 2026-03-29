"""Email client for sending notifications via SendGrid."""

from typing import Any

import httpx

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class SendGridEmailClient:
    """SendGrid email client."""

    def __init__(self) -> None:
        """Initialize SendGrid client."""
        self.api_key = settings.sendgrid_api_key
        self.api_url = "https://api.sendgrid.com/v3/mail/send"

    async def send_email(
        self, to_email: str, subject: str, html_content: str, text_content: str | None = None
    ) -> bool:
        """Send email via SendGrid API."""
        try:
            payload = {
                "personalizations": [{"to": [{"email": to_email}], "subject": subject}],
                "from": {"email": settings.email_from, "name": settings.email_from_name},
                "content": [],
            }

            if text_content:
                payload["content"].append({"type": "text/plain", "value": text_content})

            payload["content"].append({"type": "text/html", "value": html_content})

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url, json=payload, headers=headers, timeout=30.0
                )

                if response.status_code in (200, 202):
                    logger.info("email_sent", to=to_email, subject=subject, provider="sendgrid")
                    return True
                else:
                    logger.error(
                        "email_send_failed",
                        to=to_email,
                        status_code=response.status_code,
                        response=response.text,
                        provider="sendgrid",
                    )
                    return False

        except Exception as e:
            logger.error("email_send_failed", to=to_email, error=str(e), provider="sendgrid")
            return False


class MockEmailClient:
    """Mock email client for testing without SendGrid."""

    async def send_email(
        self, to_email: str, subject: str, html_content: str, text_content: str | None = None
    ) -> bool:
        """Mock send email - logs instead of actually sending."""
        logger.info(
            "mock_email_sent",
            to=to_email,
            subject=subject,
            provider="mock",
            html_length=len(html_content),
            text_length=len(text_content) if text_content else 0,
        )
        # Log the text content so you can see what would have been sent
        logger.info(
            "email_content", to=to_email, content=text_content[:500] if text_content else ""
        )
        return True


class EmailService:
    """Email service using SendGrid or mock for testing."""

    def __init__(self) -> None:
        """Initialize email service."""
        settings = get_settings()

        if not settings.sendgrid_api_key or settings.sendgrid_api_key == "":
            self.client = MockEmailClient()
            logger.info(
                "email_service_initialized", provider="mock", note="SendGrid API key not configured"
            )
        else:
            self.client = SendGridEmailClient()
            logger.info("email_service_initialized", provider="sendgrid")

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

    async def send_handover_notification(
        self, admin_emails: list[str], incident_details: dict[str, Any]
    ) -> bool:
        """Send handover notification to admin team."""
        subject = f"🚨 Patient Handover Request - {incident_details.get('subject', 'N/A')}"

        priority_emoji = {"low": "🟢", "medium": "🟡", "high": "🟠", "urgent": "🔴"}
        priority = incident_details.get("priority", "medium")
        priority_display = f"{priority_emoji.get(priority, '🟡')} {priority.upper()}"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="background-color: #fff3cd; border-left: 5px solid #ffc107; padding: 20px; margin-bottom: 20px;">
                <h2 style="margin: 0; color: #856404;">🚨 Patient Handover Request</h2>
                <p style="margin: 10px 0 0 0; color: #856404;">Priority: {priority_display}</p>
            </div>
            
            <h3>Patient Information</h3>
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <p><strong>Name:</strong> {incident_details.get('patient_name', 'N/A')}</p>
                <p><strong>Email:</strong> {incident_details.get('patient_email', 'N/A')}</p>
                <p><strong>Phone:</strong> {incident_details.get('patient_phone', 'Not provided')}</p>
                <p><strong>Incident ID:</strong> #{incident_details.get('incident_id', 'N/A')}</p>
            </div>
            
            <h3>Subject</h3>
            <p style="background-color: #e9ecef; padding: 15px; border-radius: 5px; margin: 15px 0;">
                {incident_details.get('subject', 'N/A')}
            </p>
            
            <h3>Conversation Summary</h3>
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; white-space: pre-wrap;">
                {incident_details.get('chat_summary', 'No summary available')}
            </div>
            
            <h3>Action Required</h3>
            <p>Please review this handover request and contact the patient as soon as possible.</p>
            
            <div style="margin: 30px 0;">
                <a href="{incident_details.get('admin_portal_url', 'http://localhost:5173')}/admin/incidents/{incident_details.get('incident_id', '')}" 
                   style="display: inline-block; background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                    View in Admin Portal
                </a>
            </div>
            
            <p style="color: #666; font-size: 12px; margin-top: 40px; border-top: 1px solid #ddd; padding-top: 20px;">
                This is an automated notification from CareConnect. Patient requested human assistance.
                <br>Confirmation Code: {incident_details.get('confirmation_code', 'N/A')}
            </p>
        </body>
        </html>
        """

        text_content = f"""
        🚨 PATIENT HANDOVER REQUEST
        Priority: {priority.upper()}
        
        PATIENT INFORMATION
        Name: {incident_details.get('patient_name', 'N/A')}
        Email: {incident_details.get('patient_email', 'N/A')}
        Phone: {incident_details.get('patient_phone', 'Not provided')}
        Incident ID: #{incident_details.get('incident_id', 'N/A')}
        
        SUBJECT
        {incident_details.get('subject', 'N/A')}
        
        CONVERSATION SUMMARY
        {incident_details.get('chat_summary', 'No summary available')}
        
        ACTION REQUIRED
        Please review this handover request and contact the patient as soon as possible.
        
        Confirmation Code: {incident_details.get('confirmation_code', 'N/A')}
        """

        # Send to all admin emails
        success_count = 0
        for admin_email in admin_emails:
            if await self.client.send_email(admin_email, subject, html_content, text_content):
                success_count += 1

        return success_count > 0

    async def send_handover_confirmation_to_patient(
        self, patient_email: str, incident_details: dict[str, Any]
    ) -> bool:
        """Send confirmation to patient that handover was received."""
        subject = "Your Request for Human Assistance - CareConnect"

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #007bff;">Request Received</h2>
            <p>Thank you for reaching out. We've received your request for human assistance.</p>
            
            <div style="background-color: #e3f2fd; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 0;"><strong>Confirmation Code:</strong> {incident_details.get('confirmation_code', 'N/A')}</p>
                <p style="margin: 10px 0 0 0;"><strong>Incident ID:</strong> #{incident_details.get('incident_id', 'N/A')}</p>
            </div>
            
            <h3>What happens next?</h3>
            <ol style="line-height: 2;">
                <li>Our care team has been notified</li>
                <li>A staff member will review your conversation</li>
                <li>We'll contact you within {incident_details.get('estimated_response_time', '24 hours')}</li>
            </ol>
            
            <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 0;"><strong>⚠️ For medical emergencies:</strong></p>
                <p style="margin: 10px 0 0 0;">Please call 911 or go to your nearest emergency room immediately. Do not wait for a response from our team.</p>
            </div>
            
            <h3>Your Information</h3>
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px;">
                <p><strong>Subject:</strong> {incident_details.get('subject', 'N/A')}</p>
                <p><strong>Contact Email:</strong> {patient_email}</p>
                <p><strong>Contact Phone:</strong> {incident_details.get('patient_phone', 'Not provided')}</p>
            </div>
            
            <p style="margin-top: 30px;">We appreciate your patience and look forward to assisting you.</p>
            
            <p style="color: #666; font-size: 12px; margin-top: 40px;">
                This is an automated confirmation from CareConnect.
            </p>
        </body>
        </html>
        """

        text_content = f"""
        Request Received
        
        Thank you for reaching out. We've received your request for human assistance.
        
        Confirmation Code: {incident_details.get('confirmation_code', 'N/A')}
        Incident ID: #{incident_details.get('incident_id', 'N/A')}
        
        WHAT HAPPENS NEXT?
        1. Our care team has been notified
        2. A staff member will review your conversation
        3. We'll contact you within {incident_details.get('estimated_response_time', '24 hours')}
        
        ⚠️ FOR MEDICAL EMERGENCIES:
        Please call 911 or go to your nearest emergency room immediately. Do not wait for a response from our team.
        
        YOUR INFORMATION
        Subject: {incident_details.get('subject', 'N/A')}
        Contact Email: {patient_email}
        Contact Phone: {incident_details.get('patient_phone', 'Not provided')}
        
        We appreciate your patience and look forward to assisting you.
        """

        return await self.client.send_email(patient_email, subject, html_content, text_content)
