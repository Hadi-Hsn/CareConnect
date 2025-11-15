"""Agent chat endpoint."""
import time
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.router import AgentRouter
from app.core.db import get_db
from app.core.logging import get_logger
from app.schemas.agent import ChatRequest, ChatResponse, FeedbackRequest, FeedbackResponse
from app.services.cost_tracker import cost_tracker

router = APIRouter()
logger = get_logger(__name__)


@router.post("/chat", response_model=ChatResponse)
async def chat(
    chat_request: ChatRequest,
    db: AsyncSession = Depends(get_db)
) -> ChatResponse:
    """
    Process a chat turn with the agent.

    This endpoint uses OpenAI's function calling to orchestrate booking flows
    and information retrieval.
    
    Supports voice_mode parameter for phone-call-style short responses.
    """
    if not chat_request.messages:
        raise HTTPException(status_code=400, detail="Messages list cannot be empty")

    start_time = time.perf_counter()

    try:
        logger.info("chat_request_received", 
                   user_id=chat_request.user_id, 
                   message_count=len(chat_request.messages),
                   voice_mode=chat_request.voice_mode)
        
        agent = AgentRouter(db, voice_mode=chat_request.voice_mode)
        message, tool_calls, tool_results, usage = await agent.chat_turn(
            chat_request.messages, chat_request.user_id
        )

        # Set tool_call_id for results
        for i, result in enumerate(tool_results):
            if i < len(tool_calls):
                result.tool_call_id = tool_calls[i].id

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        logger.info("chat_response_successful",
                   message_content_length=len(message.content),
                   tool_calls_count=len(tool_calls),
                   latency_ms=elapsed_ms)

        # Track cost
        task_id = str(uuid.uuid4())
        task_type = "chat"
        
        # Determine task type based on tools used
        if tool_calls:
            tool_names = [tc.name for tc in tool_calls]
            if "book_appointment" in tool_names:
                task_type = "booking"
            elif "cancel_appointment" in tool_names:
                task_type = "cancellation"
            elif "modify_appointment" in tool_names:
                task_type = "modification"
            elif "rag_lookup" in tool_names:
                task_type = "information"
        
        cost_tracker.log_completion(
            task_id=task_id,
            task_type=task_type,
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
            success=True,
            latency_ms=elapsed_ms,
            model="gpt-4o",
            user_id=chat_request.user_id
        )

        return ChatResponse(
            message=message,
            tool_calls=tool_calls,
            tool_results=tool_results,
            finish_reason="stop",
            usage=usage,
            latency_ms=elapsed_ms,
        )

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error("chat_error", 
                    error=str(e), 
                    error_type=type(e).__name__,
                    traceback=error_details)
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    feedback: FeedbackRequest, db: AsyncSession = Depends(get_db)
) -> FeedbackResponse:
    """Submit user feedback on chat interaction."""
    # Store feedback (could be in database)
    logger.info(
        "feedback_received",
        rating=feedback.rating,
        thumbs_up=feedback.thumbs_up,
        tags=feedback.tags,
        has_comment=bool(feedback.comment),
    )

    # In a full implementation, store this in database for analysis
    from datetime import datetime, timezone

    return FeedbackResponse(
        id=1,  # Placeholder
        received_at=datetime.now(timezone.utc),
        message="Thank you for your feedback!",
    )
