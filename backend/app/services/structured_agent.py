"""Structured Agent Service - Three-Layer Architecture for Intent Parsing."""
import json
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models import Appointment, Provider
from app.schemas.agent import ParsedIntent, BookingParameters, ExecutionPlan

logger = get_logger(__name__)
settings = get_settings()

LEBANON_TZ = ZoneInfo("Asia/Beirut")


class StructuredAgentService:
    """
    Three-layer structured agent service using OpenAI structured outputs.
    
    Layer 1: Intent Parser - Extracts structured intent from user message
    Layer 2: Parameter Extractor - Validates and structures booking parameters
    Layer 3: Execution Validator - Creates safe execution plan
    """
    
    def __init__(self, db: AsyncSession) -> None:
        """Initialize structured agent service."""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.db = db
        self.model = "gpt-4o"  # Use GPT-4o for structured outputs
        
    async def parse_intent(
        self, 
        user_message: str,
        conversation_history: list[dict[str, str]] | None = None,
        user_id: int | None = None
    ) -> ParsedIntent:
        """
        Layer 1: Parse user intent with structured output.
        
        Args:
            user_message: The user's message
            conversation_history: Previous messages for context
            user_id: Optional user ID for personalization
            
        Returns:
            ParsedIntent with structured intent information
        """
        lebanon_now = datetime.now(LEBANON_TZ)
        current_date = lebanon_now.strftime("%Y-%m-%d")
        current_time = lebanon_now.strftime("%I:%M %p")
        
        system_prompt = f"""You are an intent parser for a medical appointment booking system.

Current date: {current_date} (November 25, 2025)
Current time: {current_time}
User ID: {user_id or "Not authenticated"}

Your task is to extract the user's intent and entities from their message.

Intent Categories:
- book_appointment: User wants to book a new appointment OR search for available appointment slots
- modify_appointment: User wants to change an existing appointment
- cancel_appointment: User wants to cancel an appointment
- query_appointments: User wants to see their booked appointments
- query_information: User asking for facility information (directions, hours, departments, etc.)
- emergency: Medical emergency requiring immediate attention
- general_conversation: Greetings, thanks, or other non-actionable messages

Extract entities like:
- Dates: Convert relative dates to YYYY-MM-DD format based on current date {current_date}
  - "tomorrow" = 2025-11-26
  - "26th" or "26" = 2025-11-26
  - "27th" or "27" = 2025-11-27
  - "next week" = any day in early December 2025
- Times: Extract hour and minute (e.g., "10am" = 10:00, "3pm" = 15:00)
- Provider names: doctor names (e.g., "Dr. Smith", "Lisa Chen")
- Department names: "cardiologist" or "cardiology" = Cardiology department
- Appointment codes or IDs
- Reason for visit

CRITICAL CLARIFICATION RULES:
- Set requires_clarification=FALSE if the user provides enough info to take an action
- If user asks to "see available appointments" or "show me slots" or "give me a list", set requires_clarification=FALSE
  → We can search for available slots and show them to the user
- If user provides a department (e.g., "cardiologist", "cardiology"), that's enough to search - set requires_clarification=FALSE
- If user provides dates (e.g., "26th", "tomorrow"), that's clear - set requires_clarification=FALSE
- Missing specific time or provider name is OK - we can show all available slots
- Only set requires_clarification=TRUE if:
  → The message is truly unintelligible or ambiguous
  → You genuinely don't understand what action they want
  → The action requires critical missing information (e.g., cancelling without any appointment identifier)

Examples:
- "Book with cardiologist" → requires_clarification=FALSE (we can search cardiology slots)
- "Show me available appointments on 26th" → requires_clarification=FALSE (we can search slots for that date)
- "I want to see slots for cardiology tomorrow" → requires_clarification=FALSE (we have department and date)
- "Cancel appointment" with NO context → requires_clarification=TRUE (need to know which appointment)
"""

        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history for context
        if conversation_history:
            messages.extend(conversation_history[-5:])  # Last 5 messages for context
            
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = await self.client.beta.chat.completions.parse(
                model=self.model,
                messages=messages,
                response_format=ParsedIntent,
            )
            
            intent = response.choices[0].message.parsed
            
            logger.info(
                "intent_parsed",
                action=intent.action,
                confidence=intent.confidence,
                requires_clarification=intent.requires_clarification,
            )
            
            return intent
            
        except Exception as e:
            logger.error("intent_parsing_failed", error=str(e))
            # Return a safe fallback
            return ParsedIntent(
                action="general_conversation",
                confidence=0.0,
                requires_clarification=True,
                clarification_questions=["I'm having trouble understanding. Could you please rephrase your request?"],
                user_message_summary="Unable to parse message",
            )
    
    async def extract_parameters(
        self,
        intent: ParsedIntent,
        user_message: str,
        conversation_history: list[dict[str, str]] | None = None,
        user_id: int | None = None,
    ) -> BookingParameters:
        """
        Layer 2: Extract and validate booking parameters from intent.
        
        Args:
            intent: The parsed intent from Layer 1
            user_message: Original user message
            conversation_history: Previous messages for context
            user_id: Optional user ID
            
        Returns:
            BookingParameters with validated parameters
        """
        lebanon_now = datetime.now(LEBANON_TZ)
        current_date = lebanon_now.strftime("%Y-%m-%d")
        
        system_prompt = f"""You are a parameter extractor for medical appointment booking.

Current date: {current_date}

Based on the detected intent and user message, extract and validate booking parameters.

User Intent: {intent.action}
User Message Summary: {intent.user_message_summary}
Extracted Entities: {json.dumps(intent.extracted_entities)}

IMPORTANT - Understanding User Intent:
- If user asks to "see available appointments", "give me a list", "show me options" → They want to SEARCH for slots, not book yet
- If user says "tomorrow or 27th" or provides multiple dates → They want to see options for BOTH dates
- If user says "book me for tomorrow at 2pm" → They want to BOOK a specific slot

Validation Rules:
1. For SEARCHING/BROWSING slots (user wants to see options):
   - Need: department OR provider_name
   - Date is OPTIONAL - if provided, use it; if multiple dates mentioned, pick the first one
   - Set action="book" (we'll search first, then book later)
   - Set has_all_required_info=TRUE if we have department/provider
   
2. For BOOKING a specific slot (user commits to a time):
   - Need: date, time (hour/minute), and either (provider_id/provider_name) OR department
   - Set has_all_required_info=TRUE only if ALL booking details are present
   
3. For MODIFICATION: 
   - Need: appointment_id OR confirmation_code, AND new date/time
   
4. For CANCELLATION: 
   - Need: appointment_id OR confirmation_code
   
5. For QUERY: 
   - Optional query_filter (upcoming/past/all)

KEY POINT: When user says "show me appointments on 26th" or "give me options for tomorrow or 27th":
- Extract the FIRST date mentioned (e.g., "26th" or "tomorrow" = 2025-11-26)
- DO NOT mark multiple dates as an ambiguity
- Set has_all_required_info=TRUE if we have department
- The system will search and show results to the user

Convert times to 24h format (time_hour: 0-23, time_minute: 0-59) only when user specifies a time.
"""

        messages = [{"role": "system", "content": system_prompt}]
        
        if conversation_history:
            messages.extend(conversation_history[-3:])
            
        messages.append({
            "role": "user", 
            "content": f"Original message: {user_message}\n\nIntent: {intent.model_dump_json()}"
        })
        
        try:
            response = await self.client.beta.chat.completions.parse(
                model=self.model,
                messages=messages,
                response_format=BookingParameters,
            )
            
            params = response.choices[0].message.parsed
            
            # Additional validation against database
            params = await self._validate_parameters_against_db(params)
            
            logger.info(
                "parameters_extracted",
                action=params.action,
                has_all_info=params.has_all_required_info,
                missing_fields=params.missing_fields,
            )
            
            return params
            
        except Exception as e:
            logger.error("parameter_extraction_failed", error=str(e))
            # Return safe fallback
            return BookingParameters(
                action="query",
                has_all_required_info=False,
                missing_fields=["all"],
                validation_notes=f"Failed to extract parameters: {str(e)}",
            )
    
    async def create_execution_plan(
        self,
        parameters: BookingParameters,
        user_message: str,
        user_id: int | None = None,
    ) -> ExecutionPlan:
        """
        Layer 3: Create validated execution plan.
        
        Args:
            parameters: The validated parameters from Layer 2
            user_message: Original user message
            user_id: Optional user ID
            
        Returns:
            ExecutionPlan with tool calls and validation
        """
        system_prompt = f"""You are an execution planner for medical appointment booking.

Based on the validated parameters, create a safe execution plan.

Parameters: {parameters.model_dump_json()}

Your task:
1. List the tools to call in order (search_timeslots, book_appointment, modify_appointment, etc.)
2. Prepare arguments for each tool call
3. Determine if user confirmation is needed
4. Check for any warnings or blocking issues

Set can_execute=true ONLY if:
- All required parameters are present
- No ambiguities exist
- The action is safe to execute

Require user confirmation for:
- Modifications/cancellations (unless very clear)
- Bookings with multiple provider options
- Any ambiguous situations

Available tools:
- search_timeslots(date, provider_id?, department?)
- book_appointment(provider_id, slot_id, user_id, reason?)
- modify_appointment(appointment_id, new_slot_id)
- cancel_appointment(appointment_id)
- get_user_appointments(user_id, status?, limit?)
- rag_lookup(query) - for information queries
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Create execution plan for: {user_message}"},
        ]
        
        try:
            response = await self.client.beta.chat.completions.parse(
                model=self.model,
                messages=messages,
                response_format=ExecutionPlan,
            )
            
            plan = response.choices[0].message.parsed
            
            logger.info(
                "execution_plan_created",
                can_execute=plan.can_execute,
                tools=plan.tools_to_call,
                requires_confirmation=plan.requires_user_confirmation,
            )
            
            return plan
            
        except Exception as e:
            logger.error("execution_plan_failed", error=str(e))
            return ExecutionPlan(
                action_description="Unable to create execution plan",
                parameters=parameters,
                tools_to_call=[],
                tool_arguments=[],
                execution_confidence=0.0,
                requires_user_confirmation=True,
                can_execute=False,
                blocking_issues=[f"Planning failed: {str(e)}"],
            )
    
    async def _validate_parameters_against_db(
        self, 
        params: BookingParameters
    ) -> BookingParameters:
        """Validate parameters against database constraints."""
        
        # Initialize list fields if they are None
        if params.ambiguities is None:
            params.ambiguities = []
        if params.missing_fields is None:
            params.missing_fields = []
        
        try:
            # Validate provider if specified
            if params.provider_id:
                result = await self.db.execute(
                    select(Provider).where(Provider.id == params.provider_id)
                )
                provider = result.scalar_one_or_none()
                if not provider:
                    params.ambiguities.append(f"Provider ID {params.provider_id} not found")
                    params.validation_notes += f" Provider {params.provider_id} does not exist."
                    
            # Validate provider name if specified
            if params.provider_name and not params.provider_id:
                result = await self.db.execute(
                    select(Provider).where(Provider.name.ilike(f"%{params.provider_name}%"))
                )
                providers = result.scalars().all()
                if len(providers) == 0:
                    params.ambiguities.append(f"No provider found matching '{params.provider_name}'")
                elif len(providers) > 1:
                    params.ambiguities.append(
                        f"Multiple providers match '{params.provider_name}': "
                        f"{[p.name for p in providers]}"
                    )
                else:
                    # Exactly one match - set provider_id
                    params.provider_id = providers[0].id
                    params.validation_notes += f" Matched provider: {providers[0].name}."
                    
            # Validate appointment if specified (for modifications/cancellations)
            if params.appointment_id:
                result = await self.db.execute(
                    select(Appointment).where(Appointment.id == params.appointment_id)
                )
                appointment = result.scalar_one_or_none()
                if not appointment:
                    params.ambiguities.append(f"Appointment ID {params.appointment_id} not found")
                    
            # Validate confirmation code if specified
            if params.confirmation_code and not params.appointment_id:
                result = await self.db.execute(
                    select(Appointment).where(
                        Appointment.confirmation_code == params.confirmation_code
                    )
                )
                appointment = result.scalar_one_or_none()
                if appointment:
                    params.appointment_id = appointment.id
                    params.validation_notes += f" Matched appointment {appointment.id}."
                else:
                    params.ambiguities.append(
                        f"No appointment found with code '{params.confirmation_code}'"
                    )
            
            # NEW: For cancellation/modification, try to find appointment by provider name, date, and time
            if params.action in ["cancel", "modify"] and not params.appointment_id:
                if params.provider_name or params.date or params.time_hour is not None:
                    # Try to find the appointment based on the provided details
                    query = select(Appointment, Provider).join(Provider, Appointment.provider_id == Provider.id)
                    
                    # Filter by provider name if provided
                    if params.provider_name:
                        query = query.where(Provider.name.ilike(f"%{params.provider_name}%"))
                    
                    # Filter by date if provided
                    if params.date:
                        from datetime import datetime
                        target_date = datetime.strptime(params.date, "%Y-%m-%d").date()
                        # Convert to Lebanon timezone for comparison
                        from zoneinfo import ZoneInfo
                        lebanon_tz = ZoneInfo("Asia/Beirut")
                        start_of_day = datetime.combine(target_date, datetime.min.time(), tzinfo=lebanon_tz)
                        end_of_day = datetime.combine(target_date, datetime.max.time(), tzinfo=lebanon_tz)
                        query = query.where(
                            Appointment.time_start >= start_of_day,
                            Appointment.time_start <= end_of_day
                        )
                    
                    # Filter by time if provided
                    if params.time_hour is not None:
                        # This is trickier - we need to check the hour in Lebanon timezone
                        # We'll validate this after fetching candidates
                        pass
                    
                    result = await self.db.execute(query)
                    candidates = result.all()
                    
                    # Filter by time if hour was specified
                    if params.time_hour is not None and candidates:
                        from zoneinfo import ZoneInfo
                        lebanon_tz = ZoneInfo("Asia/Beirut")
                        filtered_candidates = []
                        for apt, prov in candidates:
                            lebanon_time = apt.time_start.astimezone(lebanon_tz)
                            if lebanon_time.hour == params.time_hour:
                                # Check minute too if specified
                                if params.time_minute is not None:
                                    if lebanon_time.minute == params.time_minute:
                                        filtered_candidates.append((apt, prov))
                                else:
                                    filtered_candidates.append((apt, prov))
                        candidates = filtered_candidates
                    
                    if len(candidates) == 1:
                        # Found exactly one matching appointment
                        apt, prov = candidates[0]
                        params.appointment_id = apt.id
                        params.confirmation_code = apt.confirmation_code
                        # Also set provider info if not already set
                        if not params.provider_id:
                            params.provider_id = prov.id
                        if not params.provider_name:
                            params.provider_name = prov.name
                        params.validation_notes += f" Matched appointment {apt.id} (Code: {apt.confirmation_code}) with {prov.name}."
                    elif len(candidates) > 1:
                        # Multiple matches - need clarification
                        from zoneinfo import ZoneInfo
                        lebanon_tz = ZoneInfo("Asia/Beirut")
                        apt_details = [
                            f"{prov.name} on {apt.time_start.astimezone(lebanon_tz).strftime('%B %d at %I:%M %p')}"
                            for apt, prov in candidates
                        ]
                        params.ambiguities.append(
                            f"Found {len(candidates)} appointments matching your description: {', '.join(apt_details)}"
                        )
                    # If no candidates found, the ambiguity about missing appointment ID will be caught below
                    
            # Update has_all_required_info based on validation
            if params.ambiguities:
                params.has_all_required_info = False
                
        except Exception as e:
            logger.error("db_validation_failed", error=str(e))
            params.validation_notes += f" Database validation failed: {str(e)}"
            
        return params