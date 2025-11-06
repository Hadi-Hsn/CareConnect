"""Agent router with OpenAI Responses API integration."""
import json
import time
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Any

from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.prompts import SYSTEM_PROMPT
from app.agents.tools import TOOLS
from app.core.config import get_settings
from app.core.logging import get_logger
from app.models import Appointment, Provider, User
from app.schemas.agent import ChatMessage, ToolCall, ToolResult
from app.services.email_client import EmailService
from app.services.intent_classifier import IntentClassifier
from app.services.mock_scheduling_client import MockSchedulingClient
from app.services.rag_service import RAGService
from app.services.scheduling_client import SchedulingClient

logger = get_logger(__name__)
settings = get_settings()

# Lebanon timezone
LEBANON_TZ = ZoneInfo("Asia/Beirut")


class AgentRouter:
    """Agent router using OpenAI function calling."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize agent router."""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.db = db
        self.rag_service = RAGService()
        self.email_service = EmailService()
        self.intent_classifier = IntentClassifier()

        # Use mock scheduling client for development
        if settings.mock_scheduling:
            self.scheduling_client: SchedulingClient = MockSchedulingClient()
        else:
            # Placeholder for real scheduling client
            self.scheduling_client = MockSchedulingClient()

        self.max_iterations = 10  # Prevent infinite loops

    async def chat_turn(
        self, messages: list[ChatMessage], user_id: int | None = None
    ) -> tuple[ChatMessage, list[ToolCall], list[ToolResult], dict[str, int]]:
        """
        Process a chat turn with tool execution loop.

        Args:
            messages: Conversation history
            user_id: Optional user ID for context

        Returns:
            Tuple of (final_message, tool_calls, tool_results, usage)
        """
        start_time = time.perf_counter()

        # Get current date and time for Lebanon timezone
        lebanon_now = datetime.now(LEBANON_TZ)
        current_date = lebanon_now.strftime("%Y-%m-%d")
        current_time = lebanon_now.strftime("%I:%M %p")  # e.g., "08:10 PM"
        
        system_prompt = SYSTEM_PROMPT.format(
            current_date=current_date,
            current_time=current_time,
            user_id=user_id if user_id else "Not authenticated"
        )

        # Build messages for OpenAI
        openai_messages = [{"role": "system", "content": system_prompt}]
        openai_messages.extend([{"role": m.role, "content": m.content} for m in messages])

        # Optional: Pre-retrieve context for information queries
        last_user_message = next((m for m in reversed(messages) if m.role == "user"), None)
        if last_user_message:
            intent = self.intent_classifier.classify(last_user_message.content)
            if intent.value == "information":
                # Pre-fetch RAG context
                try:
                    retrieval = await self.rag_service.retrieve(last_user_message.content, top_k=3)
                    if retrieval.chunks:
                        context = "\n\n".join(
                            f"[{chunk.doc_title}]: {chunk.content}" for chunk in retrieval.chunks
                        )
                        openai_messages.append(
                            {
                                "role": "system",
                                "content": f"Retrieved context:\n{context}",
                            }
                        )
                        logger.info("pre_retrieval_added", num_chunks=len(retrieval.chunks))
                except Exception as e:
                    logger.warning("pre_retrieval_failed", error=str(e))

        all_tool_calls: list[ToolCall] = []
        all_tool_results: list[ToolResult] = []
        total_usage: dict[str, int] = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

        # Tool execution loop
        iteration = 0
        while iteration < self.max_iterations:
            iteration += 1

            try:
                response = await self.client.chat.completions.create(
                    model=settings.openai_model,
                    messages=openai_messages,
                    tools=TOOLS,
                    tool_choice="auto",
                    temperature=settings.openai_temperature,
                    max_tokens=settings.openai_max_tokens,
                )

                # Track usage
                if response.usage:
                    total_usage["prompt_tokens"] += response.usage.prompt_tokens
                    total_usage["completion_tokens"] += response.usage.completion_tokens
                    total_usage["total_tokens"] += response.usage.total_tokens

                message = response.choices[0].message

                # Check if there are tool calls
                if message.tool_calls:
                    logger.info("tool_calls_requested", count=len(message.tool_calls))

                    # Add assistant message to history
                    openai_messages.append(message.model_dump(exclude_unset=True))

                    # Execute each tool call
                    for tool_call in message.tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)

                        logger.info("executing_tool", tool=tool_name, args=tool_args)

                        # Execute tool
                        tool_result = await self._execute_tool(tool_name, tool_args, user_id)

                        # Record tool call and result
                        all_tool_calls.append(
                            ToolCall(
                                id=tool_call.id,
                                name=tool_name,
                                arguments=tool_args,
                            )
                        )
                        all_tool_results.append(tool_result)

                        # Add tool result to conversation
                        openai_messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": tool_name,
                                "content": json.dumps(tool_result.result),
                            }
                        )

                    # Continue loop to get final response
                    continue

                else:
                    # No more tool calls - we have final response
                    final_message = ChatMessage(
                        role="assistant",
                        content=message.content or "",
                    )

                    elapsed_ms = (time.perf_counter() - start_time) * 1000

                    logger.info(
                        "chat_turn_completed",
                        iterations=iteration,
                        tool_calls=len(all_tool_calls),
                        latency_ms=elapsed_ms,
                    )

                    return final_message, all_tool_calls, all_tool_results, total_usage

            except Exception as e:
                logger.error("chat_turn_error", error=str(e), iteration=iteration)
                error_message = ChatMessage(
                    role="assistant",
                    content=f"I encountered an error: {str(e)}. Please try again.",
                )
                return error_message, all_tool_calls, all_tool_results, total_usage

        # Max iterations reached
        logger.warning("max_iterations_reached", iterations=iteration)
        timeout_message = ChatMessage(
            role="assistant",
            content="I'm having trouble processing your request. Could you please try again with more specific details?",
        )
        return timeout_message, all_tool_calls, all_tool_results, total_usage

    async def _execute_tool(
        self, tool_name: str, arguments: dict[str, Any], user_id: int | None
    ) -> ToolResult:
        """Execute a tool function."""
        try:
            if tool_name == "search_timeslots":
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
        # Get appointment details
        result = await self.db.execute(
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
