"""WhatsApp service using Twilio API."""

import os
from typing import Any

import httpx
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class WhatsAppService:
    """WhatsApp messaging service using Twilio."""

    def __init__(self) -> None:
        """Initialize WhatsApp service."""
        self.account_sid = settings.twilio_account_sid
        self.auth_token = settings.twilio_auth_token
        self.whatsapp_number = settings.twilio_whatsapp_number
        self.enabled = bool(self.account_sid and self.auth_token and self.whatsapp_number)

        if self.enabled:
            self.client = Client(self.account_sid, self.auth_token)
            logger.info("whatsapp_service_initialized", whatsapp_number=self.whatsapp_number)
        else:
            logger.warning("whatsapp_service_disabled", reason="Missing Twilio credentials")

    async def send_message(self, to_phone: str, message: str) -> dict[str, Any]:
        """
        Send a WhatsApp message to a phone number.

        Args:
            to_phone: Full international phone number (e.g., +9611234567)
            message: Message content to send

        Returns:
            Dict with status and message SID or error
        """
        if not self.enabled:
            logger.warning("whatsapp_send_skipped", reason="Service not enabled")
            return {"success": False, "error": "WhatsApp service not configured"}

        try:
            # Ensure phone number has whatsapp: prefix for Twilio
            if not to_phone.startswith("whatsapp:"):
                to_phone = f"whatsapp:{to_phone}"

            from_number = f"whatsapp:{self.whatsapp_number}"

            # Add CareConnect branding header to all messages
            branded_message = f"🏥 *CareConnect Medical Center*\n\n{message}"

            message_obj = self.client.messages.create(
                body=branded_message, from_=from_number, to=to_phone
            )

            logger.info(
                "whatsapp_message_sent",
                to=to_phone,
                message_sid=message_obj.sid,
                status=message_obj.status,
            )

            return {"success": True, "message_sid": message_obj.sid, "status": message_obj.status}

        except TwilioRestException as e:
            logger.error("whatsapp_send_failed", error=str(e), error_code=e.code, to_phone=to_phone)
            return {"success": False, "error": str(e), "error_code": e.code}
        except Exception as e:
            logger.error("whatsapp_send_error", error=str(e), to_phone=to_phone)
            return {"success": False, "error": str(e)}

    async def send_appointment_confirmation(
        self, to_phone: str, appointment_details: dict[str, Any]
    ) -> dict[str, Any]:
        """Send appointment confirmation via WhatsApp."""
        message = (
            f"🏥 *CareConnect Appointment Confirmation*\n\n"
            f"✅ Confirmation Code: *{appointment_details.get('confirmation_code')}*\n"
            f"👨‍⚕️ Provider: {appointment_details.get('provider_name')}\n"
            f"🏢 Department: {appointment_details.get('department')}\n"
            f"📅 Date & Time: {appointment_details.get('datetime')}\n"
        )

        if appointment_details.get("reason"):
            message += f"📋 Reason: {appointment_details.get('reason')}\n"

        message += "\nNeed to reschedule? Just reply to this message!"

        return await self.send_message(to_phone, message)

    async def send_appointment_reminder(
        self, to_phone: str, appointment_details: dict[str, Any]
    ) -> dict[str, Any]:
        """Send appointment reminder via WhatsApp."""
        message = (
            f"⏰ *CareConnect Appointment Reminder*\n\n"
            f"Your appointment is coming up:\n"
            f"👨‍⚕️ Provider: {appointment_details.get('provider_name')}\n"
            f"📅 Date & Time: {appointment_details.get('datetime')}\n"
            f"🏢 Location: {appointment_details.get('department')}\n\n"
            f"Confirmation Code: *{appointment_details.get('confirmation_code')}*\n\n"
            f"Reply 'CONFIRM' to confirm or 'RESCHEDULE' to change your appointment."
        )

        return await self.send_message(to_phone, message)

    async def send_welcome_message(self, to_phone: str, user_name: str) -> dict[str, Any]:
        """Send welcome message to new WhatsApp user."""
        message = (
            f"👋 Welcome to *CareConnect*, {user_name}!\n\n"
            f"I'm your AI health assistant. I can help you:\n"
            f"📅 Book appointments\n"
            f"🔍 Check appointment status\n"
            f"💬 Answer health questions\n"
            f"🏥 Find doctors and departments\n\n"
            f"Just send me a message anytime!"
        )

        return await self.send_message(to_phone, message)

    async def send_portal_link(self, to_phone: str) -> dict[str, Any]:
        """Send portal registration link for unregistered phone numbers."""
        portal_url = settings.frontend_origin
        message = (
            f"👋 Welcome to *CareConnect*!\n\n"
            f"I noticed you don't have an account yet.\n\n"
            f"📱 Please register at: {portal_url}\n\n"
            f"Once you sign up with this phone number ({to_phone}), "
            f"you'll be able to chat with me here on WhatsApp!\n\n"
            f"Looking forward to helping you manage your healthcare! 🏥"
        )

        return await self.send_message(to_phone, message)


# Singleton instance
_whatsapp_service: WhatsAppService | None = None


def get_whatsapp_service() -> WhatsAppService:
    """Get WhatsApp service singleton."""
    global _whatsapp_service
    if _whatsapp_service is None:
        _whatsapp_service = WhatsAppService()
    return _whatsapp_service
