"""Agent router with structured output architecture."""
import asyncio
import json
import re
import time
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Any

from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.prompts import VOICE_MODE_INSTRUCTION
from app.core.config import get_settings
from app.core.logging import get_logger
from app.models import Appointment, Provider, User
from app.schemas.agent import ChatMessage, ToolCall, ToolResult
from app.services.email_client import EmailService
from app.services.mock_scheduling_client import MockSchedulingClient
from app.services.rag_service import RAGService
from app.services.scheduling_client import SchedulingClient
from app.services.structured_agent import StructuredAgentService

logger = get_logger(__name__)
settings = get_settings()

# Lebanon timezone
LEBANON_TZ = ZoneInfo("Asia/Beirut")


class AgentRouter:
    """Agent router using structured output architecture."""

    def __init__(self, db: AsyncSession, voice_mode: bool = False) -> None:
        """Initialize agent router."""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.db = db
        self.voice_mode = voice_mode
        self.rag_service = RAGService()
        self.email_service = EmailService()
        self.structured_agent = StructuredAgentService(db)

        # Use mock scheduling client for development
        if settings.mock_scheduling:
            self.scheduling_client: SchedulingClient = MockSchedulingClient()
        else:
            self.scheduling_client = MockSchedulingClient()

    async def chat_turn(
        self, messages: list[ChatMessage], user_id: int | None = None
    ) -> tuple[ChatMessage, list[ToolCall], list[ToolResult], dict[str, int]]:
        """
        Process a chat turn using structured output architecture.

        Args:
            messages: Conversation history
            user_id: Optional user ID for context

        Returns:
            Tuple of (final_message, tool_calls, tool_results, usage)
        """
        start_time = time.perf_counter()
        total_usage: dict[str, int] = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

        # Get last user message
        last_user_message = next((m for m in reversed(messages) if m.role == "user"), None)
        if not last_user_message:
            return ChatMessage(role="assistant", content="How can I help you?"), [], [], total_usage

        user_message = last_user_message.content

        # === LAYER 1: PARSE INTENT ===
        logger.info("layer_1_parsing_intent", message_preview=user_message[:50])
        
        conversation_history = [{"role": m.role, "content": m.content} for m in messages[:-1]]
        intent = await self.structured_agent.parse_intent(
            user_message=user_message,
            conversation_history=conversation_history,
            user_id=user_id
        )

        # Handle emergency intent immediately
        if intent.action == "emergency":
            return ChatMessage(
                role="assistant",
                content="This sounds like a medical emergency. Please call 911 or go to the nearest emergency room immediately.",
            ), [], [], total_usage

        # Handle medical advice refusal
        text_lower = user_message.lower()
        if re.search(r"\b(what (medicine|medication)|what should i take|which medicine|take for my)\b", text_lower):
            return ChatMessage(
                role="assistant",
                content="I cannot provide medical advice. Please consult with a healthcare provider for medical concerns.",
            ), [], [], total_usage

        # Handle diagnosis requests
        if re.search(r"\b(do i have|could i have|am i (sick|infected))\b", text_lower):
            return ChatMessage(
                role="assistant",
                content="I cannot diagnose medical conditions. Please schedule an appointment with a healthcare provider who can properly evaluate your symptoms.",
            ), [], [], total_usage

        # Handle general conversation
        if intent.action == "general_conversation":
            response_content = await self._handle_general_conversation(user_message, intent)
            return ChatMessage(role="assistant", content=response_content), [], [], total_usage

        # Handle clarification needed - but ONLY if there are actual clarification questions
        if intent.requires_clarification and intent.clarification_questions:
            clarification = "\n".join(intent.clarification_questions)
            return ChatMessage(role="assistant", content=clarification), [], [], total_usage

        # Handle information queries with RAG
        if intent.action == "query_information":
            return await self._handle_information_query(user_message, intent)

        # === LAYER 2: EXTRACT PARAMETERS ===
        logger.info("layer_2_extracting_parameters", action=intent.action)
        
        parameters = await self.structured_agent.extract_parameters(
            intent=intent,
            user_message=user_message,
            conversation_history=conversation_history,
            user_id=user_id
        )

        # Check if we have all required information
        if not parameters.has_all_required_info:
            # Handle None values for missing_fields
            missing_fields = parameters.missing_fields or []
            ambiguities = parameters.ambiguities or []
            
            missing_info = ", ".join(missing_fields) if missing_fields else "some information"
            response = f"I need some more information to help you: {missing_info}"
            if ambiguities:
                response += f"\n\nAlso, I need clarification on: {', '.join(ambiguities)}"
            return ChatMessage(role="assistant", content=response), [], [], total_usage

        # === LAYER 3: CREATE EXECUTION PLAN ===
        logger.info("layer_3_creating_execution_plan", action=parameters.action)
        
        execution_plan = await self.structured_agent.create_execution_plan(
            parameters=parameters,
            user_message=user_message,
            user_id=user_id
        )

        # Check if execution is blocked
        if not execution_plan.can_execute:
            blocking_reasons = "\n".join(execution_plan.blocking_issues)
            return ChatMessage(
                role="assistant",
                content=f"I can't complete this request:\n{blocking_reasons}"
            ), [], [], total_usage

        # Check if user confirmation is required
        if execution_plan.requires_user_confirmation:
            confirmation = execution_plan.confirmation_message or execution_plan.action_description
            warnings = ""
            if execution_plan.warning_messages:
                warnings = "\n\n⚠️ " + "\n⚠️ ".join(execution_plan.warning_messages)
            return ChatMessage(
                role="assistant",
                content=f"{confirmation}{warnings}\n\nWould you like me to proceed?"
            ), [], [], total_usage

        # === EXECUTE THE PLAN ===
        logger.info("executing_plan", tools=execution_plan.tools_to_call)
        
        all_tool_calls: list[ToolCall] = []
        all_tool_results: list[ToolResult] = []

        try:
            for i, tool_name in enumerate(execution_plan.tools_to_call):
                tool_args = execution_plan.tool_arguments[i] if i < len(execution_plan.tool_arguments) else {}
                
                # Add user_id to tool arguments if needed
                if tool_name in ["book_appointment", "get_user_appointments"] and user_id:
                    tool_args["user_id"] = user_id

                logger.info("executing_tool", tool=tool_name, args=tool_args)
                
                tool_result = await self._execute_tool(tool_name, tool_args, user_id)
                
                tool_call_id = f"call_{i}_{tool_name}"
                all_tool_calls.append(ToolCall(id=tool_call_id, name=tool_name, arguments=tool_args))
                all_tool_results.append(tool_result)

                # Check for errors
                if not tool_result.success or tool_result.result.get("error"):
                    error_msg = tool_result.error or tool_result.result.get("error", "Unknown error")
                    return ChatMessage(
                        role="assistant",
                        content=f"I encountered an error: {error_msg}"
                    ), all_tool_calls, all_tool_results, total_usage

            # Generate final response based on execution results
            final_response = await self._generate_final_response(
                execution_plan=execution_plan,
                tool_results=all_tool_results,
                parameters=parameters,
                user_message=user_message
            )

            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "structured_chat_completed",
                action=intent.action,
                tools_executed=len(all_tool_calls),
                latency_ms=elapsed_ms
            )

            return ChatMessage(role="assistant", content=final_response), all_tool_calls, all_tool_results, total_usage

        except Exception as e:
            logger.error("execution_failed", error=str(e))
            return ChatMessage(
                role="assistant",
                content="I encountered an error while processing your request. Please try again."
            ), all_tool_calls, all_tool_results, total_usage

    async def _handle_general_conversation(self, user_message: str, intent: Any) -> str:
        """Handle general conversation (greetings, thanks, etc.)."""
        user_lower = user_message.lower()
        
        if any(word in user_lower for word in ["hello", "hi", "hey"]):
            return "Hello! I'm your CareConnect assistant. I can help you book appointments, answer questions about our services, or check your existing appointments. How can I help you today?"
        
        if any(word in user_lower for word in ["thank", "thanks"]):
            return "You're welcome! Let me know if you need anything else."
        
        if any(word in user_lower for word in ["bye", "goodbye"]):
            return "Goodbye! Take care and feel free to reach out if you need any assistance."
        
        return "I'm here to help with appointment booking and medical facility information. What can I assist you with?"

    async def _handle_information_query(
        self, user_message: str, intent: Any
    ) -> tuple[ChatMessage, list[ToolCall], list[ToolResult], dict[str, int]]:
        """Handle information queries using RAG."""
        try:
            retrieval = await self.rag_service.retrieve(user_message, top_k=3)
            
            if not retrieval.chunks:
                return (
                    ChatMessage(
                        role="assistant",
                        content="I don't have specific information about that. Could you rephrase or ask something else?"
                    ),
                    [],
                    [],
                    {}
                )

            # Format context from RAG
            context = "\n\n".join(
                f"**{chunk.doc_title}**\n{chunk.content}" for chunk in retrieval.chunks
            )

            # Use GPT to generate response based on context
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a helpful medical facility assistant. Use the following information to answer the user's question:\n\n{context}"
                    },
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=500
            )

            content = response.choices[0].message.content or "I couldn't generate a response."
            
            return (
                ChatMessage(role="assistant", content=content),
                [],
                [],
                {}
            )

        except Exception as e:
            logger.error("rag_query_failed", error=str(e))
            return (
                ChatMessage(
                    role="assistant",
                    content="I'm having trouble finding that information right now. Please try again."
                ),
                [],
                [],
                {}
            )

    async def _generate_final_response(
        self,
        execution_plan: Any,
        tool_results: list[ToolResult],
        parameters: Any,
        user_message: str
    ) -> str:
        """Generate final human-friendly response based on execution results."""
        
        # Extract results from tools
        results_summary = []
        for tool_result in tool_results:
            if tool_result.name == "book_appointment" and tool_result.success:
                result_data = tool_result.result
                time_start = result_data.get("time_start", "")
                provider_name = result_data.get("provider_name", "the doctor")
                confirmation = result_data.get("confirmation_code", "")
                
                return (
                    f"✅ Your appointment has been booked!\n\n"
                    f"📅 **When:** {time_start}\n"
                    f"👨‍⚕️ **Doctor:** {provider_name}\n"
                    f"🔖 **Confirmation Code:** {confirmation}\n\n"
                    f"An email confirmation has been sent to you."
                )

            elif tool_result.name == "modify_appointment" and tool_result.success:
                result_data = tool_result.result
                new_time = result_data.get("new_time_start", "")
                
                return (
                    f"✅ Your appointment has been rescheduled!\n\n"
                    f"📅 **New Time:** {new_time}\n\n"
                    f"A confirmation email has been sent."
                )

            elif tool_result.name == "cancel_appointment" and tool_result.success:
                return "✅ Your appointment has been cancelled successfully."

            elif tool_result.name == "get_user_appointments" and tool_result.success:
                appointments = tool_result.result.get("appointments", [])
                if not appointments:
                    return "You don't have any appointments scheduled."
                
                response = f"**Your Appointments** ({len(appointments)} total):\n\n"
                for apt in appointments[:5]:  # Show first 5
                    response += (
                        f"📅 {apt['datetime_display']}\n"
                        f"👨‍⚕️ {apt['provider_name']} ({apt['department']})\n"
                        f"🔖 {apt['confirmation_code']} • Status: {apt['status']}\n\n"
                    )
                
                if len(appointments) > 5:
                    response += f"... and {len(appointments) - 5} more."
                
                return response

            elif tool_result.name == "search_timeslots" and tool_result.success:
                result_data = tool_result.result
                providers = result_data.get("providers", [])
                
                if not providers:
                    return "I couldn't find any available appointment slots for that date and provider/department."
                
                response = "**Available Appointments:**\n\n"
                for provider in providers[:2]:  # Show first 2 providers
                    response += f"👨‍⚕️ **{provider['provider_name']}** ({provider['department']})\n"
                    slots = provider.get('slots', [])[:3]  # Show first 3 slots
                    for slot in slots:
                        start_time = datetime.fromisoformat(slot['start'].replace('Z', '+00:00'))
                        lebanon_time = start_time.astimezone(LEBANON_TZ)
                        response += f"  • {lebanon_time.strftime('%I:%M %p')}\n"
                    response += "\n"
                
                response += "Would you like to book one of these slots?"
                return response

        # Fallback response
        return execution_plan.action_description

    # Keep all existing tool execution methods
    async def _execute_tool(
        self, tool_name: str, arguments: dict[str, Any], user_id: int | None
    ) -> ToolResult:
        """Execute a tool function."""
        try:
            if tool_name == "get_user_appointments":
                result = await self._get_user_appointments(user_id=user_id, **arguments)
            elif tool_name == "search_timeslots":
                result = await self._search_timeslots(**arguments)
            elif tool_name == "book_appointment":
                # Remove user_id from arguments if present (we'll use the authenticated user_id)
                book_args = {k: v for k, v in arguments.items() if k != 'user_id'}
                result = await self._book_appointment(**book_args, user_id=user_id)
            elif tool_name == "modify_appointment":
                result = await self._modify_appointment(**arguments)
            elif tool_name == "cancel_appointment":
                result = await self._cancel_appointment(**arguments)
            elif tool_name == "send_email_confirmation":
                result = await self._send_email_confirmation(**arguments)
            elif tool_name == "rag_lookup":
                result = await self._rag_lookup(**arguments)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")

            return ToolResult(
                tool_call_id="",  # Will be set by caller
                name=tool_name,
                result=result,
                success=True,
            )

        except Exception as e:
            logger.error("tool_execution_failed", tool=tool_name, error=str(e))
            return ToolResult(
                tool_call_id="",
                name=tool_name,
                result={"error": str(e)},
                success=False,
                error=str(e),
            )

    async def _search_timeslots(
        self, date: str, provider_id: int | None = None, department: str | None = None
    ) -> dict[str, Any]:
        """Search for available timeslots."""
        from datetime import datetime

        target_date = datetime.strptime(date, "%Y-%m-%d").date()

        # If provider_id is given, search for that provider
        if provider_id:
            slots = await self.scheduling_client.get_timeslots(provider_id, target_date)
            result = await self.db.execute(select(Provider).where(Provider.id == provider_id))
            provider = result.scalar_one_or_none()

            return {
                "provider_id": provider_id,
                "provider_name": provider.name if provider else "Unknown",
                "department": provider.department if provider else "",
                "date": date,
                "slots": [
                    {
                        "slot_id": s.slot_id,
                        "start": s.start.isoformat(),
                        "end": s.end.isoformat(),
                        "available": s.available,
                    }
                    for s in slots
                ],
            }

        # If department is given, find providers in that department
        elif department:
            providers = await self.scheduling_client.search_providers(department=department)
            if not providers:
                return {"error": f"No providers found in department: {department}"}

            # Return all providers with their slots
            providers_with_slots = []
            for provider in providers[:3]:  # Limit to first 3 providers for performance
                slots = await self.scheduling_client.get_timeslots(provider["id"], target_date)
                # Only include providers with available slots
                available_slots = [s for s in slots if s.available]
                if available_slots:
                    providers_with_slots.append({
                        "provider_id": provider["id"],
                        "provider_name": provider["name"],
                        "department": provider.get("department", ""),
                        "specialty": provider.get("specialty", ""),
                        "slots": [
                            {
                                "slot_id": s.slot_id,
                                "start": s.start.isoformat(),
                                "end": s.end.isoformat(),
                            }
                            for s in available_slots[:10]  # Limit to first 10 slots
                        ],
                    })
            
            if not providers_with_slots:
                return {
                    "department": department,
                    "date": date,
                    "message": f"No available appointments found in {department} for {date}",
                }

            return {
                "department": department,
                "date": date,
                "providers": providers_with_slots,
                "message": f"Found {len(providers_with_slots)} provider(s) with availability",
            }

        return {"error": "Either provider_id or department must be specified"}

    async def _book_appointment(
        self,
        provider_id: int,
        slot_id: str,
        user_id: int | None = None,
        reason: str | None = None,
    ) -> dict[str, Any]:
        """Book an appointment."""
        if not user_id:
            return {"error": "user_id is required to book an appointment"}

        result = await self.scheduling_client.book_appointment(
            user_id=user_id,
            provider_id=provider_id,
            slot_id=slot_id,
            reason=reason,
        )

        # Automatically send email confirmation after successful booking
        if "appointment_id" in result and "error" not in result:
            try:
                appointment_id = result["appointment_id"]
                email_result = await self._send_email_confirmation(appointment_id)
                result["email_sent"] = email_result.get("email_sent", False)
                logger.info(
                    "auto_email_sent",
                    appointment_id=appointment_id,
                    email_sent=email_result.get("email_sent", False),
                )
            except Exception as e:
                logger.error("auto_email_failed", error=str(e), appointment_id=result.get("appointment_id"))
                # Don't fail the booking if email fails
                result["email_sent"] = False
                result["email_error"] = str(e)

        return result

    async def _modify_appointment(
        self, appointment_id: int, new_slot_id: str
    ) -> dict[str, Any]:
        """Modify an appointment."""
        result = await self.scheduling_client.modify_appointment(appointment_id, new_slot_id)
        return result

    async def _cancel_appointment(self, appointment_id: int) -> dict[str, Any]:
        """Cancel an appointment."""
        result = await self.scheduling_client.cancel_appointment(appointment_id)
        return result

    async def _send_email_confirmation(self, appointment_id: int) -> dict[str, Any]:
        """Send email confirmation for an appointment."""
        # Import here to avoid circular dependency
        from app.core.db import async_session_maker
        
        # Use a fresh session to ensure we get the latest data
        # This prevents stale reads when the appointment was created in a different session
        async with async_session_maker() as session:
            result = await session.execute(
                select(Appointment, User, Provider)
                .join(User, Appointment.user_id == User.id)
                .join(Provider, Appointment.provider_id == Provider.id)
                .where(Appointment.id == appointment_id)
            )
            row = result.first()

            if not row:
                return {"error": "Appointment not found"}

            appointment, user, provider = row

            # Convert to Lebanon timezone for display
            lebanon_time = appointment.time_start.astimezone(LEBANON_TZ)

            details = {
                "confirmation_code": appointment.confirmation_code,
                "provider_name": provider.name,
                "department": provider.department,
                "datetime": lebanon_time.strftime("%B %d, %Y at %I:%M %p"),
                "reason": appointment.reason,
            }

            success = await self.email_service.send_confirmation(user.email, details)

            return {
                "email_sent": success,
                "recipient": user.email,
                "confirmation_code": appointment.confirmation_code,
            }

    async def _rag_lookup(self, query: str) -> dict[str, Any]:
        """Look up information using RAG."""
        retrieval = await self.rag_service.retrieve(query, top_k=5)

        return {
            "query": query,
            "results": [
                {
                    "doc_title": chunk.doc_title,
                    "content": chunk.content,
                    "score": chunk.score,
                }
                for chunk in retrieval.chunks
            ],
        }

    async def _get_user_appointments(
        self, user_id: int | None = None, status: str = "all", limit: int = 100
    ) -> dict[str, Any]:
        """Get user's appointments.
        
        Default behavior matches the Appointments page: shows ALL appointments
        ordered by time (newest first), regardless of status.
        """
        if not user_id:
            return {"error": "user_id is required to retrieve appointments"}

        from datetime import datetime
        from sqlalchemy import desc, or_

        # Get current time in Lebanon timezone
        lebanon_now = datetime.now(LEBANON_TZ)

        # Build base query - matches Appointments page API
        query = (
            select(Appointment, Provider)
            .join(Provider, Appointment.provider_id == Provider.id)
            .where(Appointment.user_id == user_id)
        )

        # Apply status filter only if explicitly requested
        if status == "upcoming":
            query = query.where(
                Appointment.time_start >= lebanon_now,
                Appointment.status.in_(["scheduled", "confirmed"])
            ).order_by(Appointment.time_start)
        elif status == "past":
            query = query.where(
                or_(
                    Appointment.time_start < lebanon_now,
                    Appointment.status.in_(["completed", "cancelled"])
                )
            ).order_by(desc(Appointment.time_start))
        else:  # "all" - default behavior matching Appointments page
            # Show ALL appointments regardless of status, newest first
            query = query.order_by(desc(Appointment.time_start))

        # Apply limit
        query = query.limit(limit)

        # Execute query
        result = await self.db.execute(query)
        rows = result.all()

        if not rows:
            return {
                "appointments": [],
                "count": 0,
                "message": f"No {status} appointments found" if status != "all" else "No appointments found"
            }

        # Format appointments - same format as Appointments page
        appointments = []
        for appointment, provider in rows:
            # Convert to Lebanon timezone for display
            lebanon_time = appointment.time_start.astimezone(LEBANON_TZ)
            
            appointments.append({
                "appointment_id": appointment.id,
                "confirmation_code": appointment.confirmation_code,
                "provider_name": provider.name,
                "provider_id": provider.id,
                "department": provider.department,
                "specialty": provider.specialty,
                "date": lebanon_time.strftime("%Y-%m-%d"),
                "time": lebanon_time.strftime("%I:%M %p"),
                "datetime_display": lebanon_time.strftime("%B %d, %Y at %I:%M %p"),
                "status": appointment.status,
                "reason": appointment.reason,
            })

        return {
            "appointments": appointments,
            "count": len(appointments),
            "status_filter": status,
        }
