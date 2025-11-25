"""Agent and chat schemas."""
from datetime import datetime
from typing import Any, Literal

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
    voice_mode: bool = False  # Enable phone-call style short responses


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


# ============================================================================
# STRUCTURED OUTPUT SCHEMAS - Three-Layer Architecture
# ============================================================================


class ParsedIntent(BaseModel):
    """Layer 1: Structured intent extraction from user message."""
    
    action: Literal[
        "book_appointment",
        "modify_appointment", 
        "cancel_appointment",
        "query_appointments",
        "query_information",
        "emergency",
        "general_conversation"
    ] = Field(description="The primary action the user wants to perform")
    
    confidence: float = Field(
        ge=0.0, 
        le=1.0,
        description="Confidence score for the detected intent (0.0 to 1.0)"
    )
    
    requires_clarification: bool = Field(
        description="Whether the intent is unclear and needs clarification"
    )
    
    user_message_summary: str = Field(
        description="A brief summary of what the user is asking for"
    )
    
    # Optional fields - must come after required fields
    extracted_entities: dict[str, Any] | None = Field(
        default=None,
        description="Raw entities extracted from the message (dates, times, names, etc.)"
    )
    
    clarification_questions: list[str] | None = Field(
        default=None,
        description="Specific questions to ask the user for clarification"
    )


class BookingParameters(BaseModel):
    """Layer 2: Validated and structured booking parameters."""
    
    action: Literal["book", "modify", "cancel", "query"] = Field(
        description="The specific booking action to perform"
    )
    
    has_all_required_info: bool = Field(
        description="Whether all required information for the action is present"
    )
    
    validation_notes: str = Field(
        default="",
        description="Additional validation notes or warnings"
    )
    
    # Optional fields with None defaults
    date: str | None = Field(
        default=None, 
        description="Target date in YYYY-MM-DD format"
    )
    
    time_hour: int | None = Field(
        default=None,
        description="Preferred hour in 24h format (0-23)"
    )
    
    time_minute: int | None = Field(
        default=None,
        description="Preferred minute (0-59)"
    )
    
    provider_name: str | None = Field(
        default=None,
        description="Requested doctor/provider name"
    )
    
    provider_id: int | None = Field(
        default=None,
        description="Specific provider ID if known"
    )
    
    department: str | None = Field(
        default=None,
        description="Medical department (e.g., Cardiology, Pediatrics)"
    )
    
    reason: str | None = Field(
        default=None,
        description="Reason for appointment"
    )
    
    appointment_id: int | None = Field(
        default=None,
        description="Appointment ID to modify or cancel"
    )
    
    confirmation_code: str | None = Field(
        default=None,
        description="Appointment confirmation code"
    )
    
    query_filter: Literal["upcoming", "past", "all"] | None = Field(
        default=None,
        description="Filter for appointment queries"
    )
    
    missing_fields: list[str] | None = Field(
        default=None,
        description="List of required fields that are missing"
    )
    
    ambiguities: list[str] | None = Field(
        default=None,
        description="List of ambiguous or unclear parameters"
    )


class ExecutionPlan(BaseModel):
    """Layer 3: Validated execution plan before taking action."""
    
    action_description: str = Field(
        description="Human-readable description of what will be executed"
    )
    
    parameters: BookingParameters = Field(
        description="The validated parameters to use"
    )
    
    execution_confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence that this execution plan is correct"
    )
    
    requires_user_confirmation: bool = Field(
        description="Whether to ask user confirmation before executing"
    )
    
    can_execute: bool = Field(
        description="Whether this plan is safe and ready to execute"
    )
    
    # Optional fields with None defaults
    confirmation_message: str | None = Field(
        default=None,
        description="Message to show user for confirmation"
    )
    
    tools_to_call: list[str] | None = Field(
        default=None,
        description="Ordered list of tools that will be called"
    )
    
    tool_arguments: list[dict[str, Any]] | None = Field(
        default=None,
        description="Arguments for each tool call"
    )
    
    warning_messages: list[str] | None = Field(
        default=None,
        description="Warnings or important notes about this execution"
    )
    
    blocking_issues: list[str] | None = Field(
        default=None,
        description="Issues preventing execution (if can_execute is False)"
    )
