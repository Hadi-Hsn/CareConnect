"""Agent and chat schemas."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Chat message schema."""

    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str


class ToolCall(BaseModel):
    """Tool call schema."""

    id: str
    name: str
    arguments: dict[str, Any]


class ToolResult(BaseModel):
    """Tool execution result."""

    tool_call_id: str
    name: str
    result: dict[str, Any]
    success: bool
    error: str | None = None


class ChatRequest(BaseModel):
    """Chat request schema."""

    messages: list[ChatMessage]
    user_id: int | None = None
    stream: bool = False


class ChatResponse(BaseModel):
    """Chat response schema."""

    message: ChatMessage
    tool_calls: list[ToolCall] = []
    tool_results: list[ToolResult] = []
    finish_reason: str
    usage: dict[str, int] | None = None
    latency_ms: float


class FeedbackRequest(BaseModel):
    """User feedback schema."""

    conversation_id: str | None = None
    rating: int = Field(..., ge=1, le=5)
    thumbs_up: bool
    comment: str | None = None
    tags: list[str] = []


class FeedbackResponse(BaseModel):
    """Feedback response schema."""

    id: int
    received_at: datetime
    message: str = "Thank you for your feedback!"
