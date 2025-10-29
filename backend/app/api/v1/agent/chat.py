"""Agent chat endpoint."""
import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.router import AgentRouter
from app.core.db import get_db
from app.core.logging import get_logger
from app.schemas.agent import ChatRequest, ChatResponse, FeedbackRequest, FeedbackResponse

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
    """
    if not chat_request.messages:
        raise HTTPException(status_code=400, detail="Messages list cannot be empty")

    start_time = time.perf_counter()

    try:
        agent = AgentRouter(db)
        message, tool_calls, tool_results, usage = await agent.chat_turn(
            chat_request.messages, chat_request.user_id
        )

        # Set tool_call_id for results
        for i, result in enumerate(tool_results):
            if i < len(tool_calls):
                result.tool_call_id = tool_calls[i].id

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return ChatResponse(
            message=message,
            tool_calls=tool_calls,
            tool_results=tool_results,
            finish_reason="stop",
            usage=usage,
            latency_ms=elapsed_ms,
        )

    except Exception as e:
        logger.error("chat_error", error=str(e))
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
