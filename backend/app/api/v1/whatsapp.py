"""WhatsApp webhook endpoint for Twilio integration."""
from typing import Any
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Request, Response, HTTPException, status
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.router import AgentRouter
from app.core.db import get_db
from app.core.logging import get_logger
from app.models import User, WhatsAppMessage
from app.schemas.agent import ChatMessage
from app.services.whatsapp_service import get_whatsapp_service

router = APIRouter()
logger = get_logger(__name__)

# Keep conversation history for 24 hours
CONVERSATION_HISTORY_HOURS = 24
# Maximum number of messages to include in context
MAX_HISTORY_MESSAGES = 10


@router.post("/webhook", response_class=PlainTextResponse)
async def whatsapp_webhook(request: Request, db: AsyncSession = Depends(get_db)) -> str:
    """
    Handle incoming WhatsApp messages from Twilio.
    
    Twilio sends messages in application/x-www-form-urlencoded format.
    """
    try:
        # Parse form data from Twilio
        form_data = await request.form()
        
        # Extract message details
        from_number = form_data.get("From", "")  # Format: whatsapp:+1234567890
        to_number = form_data.get("To", "")
        body = form_data.get("Body", "")
        message_sid = form_data.get("MessageSid", "")
        
        # Clean phone number (remove whatsapp: prefix)
        if from_number.startswith("whatsapp:"):
            from_number = from_number[9:]
        
        logger.info(
            "whatsapp_message_received",
            from_number=from_number,
            message_sid=message_sid,
            body_preview=body[:50] if body else ""
        )
        
        # Validate message
        if not body or not from_number:
            logger.warning("invalid_whatsapp_message", from_number=from_number, body=body)
            return ""
        
        # Find user by phone number
        user = await find_user_by_phone(db, from_number)
        
        if not user:
            # User not found - send friendly signup message
            logger.info("unregistered_whatsapp_user", phone=from_number)
            whatsapp_service = get_whatsapp_service()
            
            # Send a friendly message asking them to sign up first
            signup_message = (
                "👋 Welcome to *CareConnect*!\n\n"
                "To use our AI health assistant via WhatsApp, you need to sign up first.\n\n"
                "📱 *Please register at our portal:*\n"
                "https://carecon.online/login\n\n"
                "Make sure to use this phone number (*{phone}*) when signing up so we can connect your account!\n\n"
                "Once registered, come back here and I'll be ready to help you! 🏥"
            ).format(phone=from_number)
            
            await whatsapp_service.send_message(from_number, signup_message)
            return ""
        
        # User found - store their message in history
        user_message = WhatsAppMessage(
            user_id=user.id,
            phone_number=from_number,
            role="user",
            content=body,
            message_sid=message_sid
        )
        db.add(user_message)
        await db.commit()
        
        logger.info("processing_whatsapp_message", user_id=user.id, phone=from_number)
        
        # Retrieve recent conversation history (last 24 hours, max 10 messages)
        history_cutoff = datetime.now(timezone.utc) - timedelta(hours=CONVERSATION_HISTORY_HOURS)
        result = await db.execute(
            select(WhatsAppMessage)
            .where(
                WhatsAppMessage.user_id == user.id,
                WhatsAppMessage.created_at >= history_cutoff
            )
            .order_by(WhatsAppMessage.created_at.desc())
            .limit(MAX_HISTORY_MESSAGES)
        )
        history_messages = result.scalars().all()
        
        # Reverse to get chronological order (oldest first)
        history_messages = list(reversed(history_messages))
        
        # Build conversation with history
        messages = [
            ChatMessage(role=msg.role, content=msg.content)
            for msg in history_messages
        ]
        
        logger.info(
            "conversation_history_loaded",
            user_id=user.id,
            history_count=len(messages),
            total_messages=len(history_messages)
        )
        
        # Create agent router with voice mode for concise responses
        agent = AgentRouter(db=db, voice_mode=True)
        
        # Process through agent with full conversation history
        response, tool_calls, tool_results, usage = await agent.chat_turn(
            messages=messages,
            user_id=user.id
        )
        
        # Store assistant's response in history
        assistant_message = WhatsAppMessage(
            user_id=user.id,
            phone_number=from_number,
            role="assistant",
            content=response.content
        )
        db.add(assistant_message)
        await db.commit()
        
        # Send response back via WhatsApp
        whatsapp_service = get_whatsapp_service()
        result = await whatsapp_service.send_message(from_number, response.content)
        
        if result.get("success"):
            # Update assistant message with Twilio message SID
            assistant_message.message_sid = result.get("message_sid")
            await db.commit()
            
            logger.info(
                "whatsapp_response_sent",
                user_id=user.id,
                message_sid=result.get("message_sid"),
                tool_calls_count=len(tool_calls)
            )
        else:
            logger.error(
                "whatsapp_response_failed",
                user_id=user.id,
                error=result.get("error")
            )
        
        # Return empty response (Twilio doesn't need response body)
        return ""
        
    except Exception as e:
        logger.error("whatsapp_webhook_error", error=str(e), exc_info=True)
        # Don't return error to Twilio - just log it
        return ""


@router.get("/webhook", response_class=PlainTextResponse)
async def whatsapp_webhook_verify(request: Request) -> str:
    """
    Verify webhook endpoint (for initial Twilio setup).
    """
    logger.info("whatsapp_webhook_verification")
    return "WhatsApp webhook endpoint is active"


async def find_user_by_phone(db: AsyncSession, full_phone: str) -> User | None:
    """
    Find user by phone number.
    
    Args:
        db: Database session
        full_phone: Full international phone number (e.g., +9611234567)
        
    Returns:
        User object if found, None otherwise
    """
    # Try to parse country code from full phone number
    # Common country codes: +1 (1-4 digits)
    possible_country_codes = []
    
    # Try extracting country codes of different lengths
    if full_phone.startswith("+"):
        # Try 1-4 digit country codes
        for length in range(1, 5):
            if len(full_phone) > length:
                country_code = full_phone[:length + 1]  # +1 for the + sign
                phone_number = full_phone[length + 1:]
                possible_country_codes.append((country_code, phone_number))
    
    # Try each possible combination
    for country_code, phone_number in possible_country_codes:
        result = await db.execute(
            select(User).where(
                User.country_code == country_code,
                User.phone == phone_number
            )
        )
        user = result.scalar_one_or_none()
        if user:
            logger.info(
                "user_found_by_phone",
                user_id=user.id,
                country_code=country_code,
                phone=phone_number
            )
            return user
    
    # Also try without country code parsing (in case it's stored differently)
    result = await db.execute(
        select(User).where(User.phone.like(f"%{full_phone[-10:]}%"))
    )
    user = result.scalar_one_or_none()
    
    if user:
        logger.info("user_found_by_phone_partial", user_id=user.id)
    else:
        logger.warning("user_not_found_by_phone", phone=full_phone)
    
    return user
