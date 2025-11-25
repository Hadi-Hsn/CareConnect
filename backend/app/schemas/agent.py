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
    
    extracted_entities: dict[str, Any] = Field(
        default_factory=dict,
        description="Raw entities extracted from the message (dates, times, names, etc.)"
    )
    
    requires_clarification: bool = Field(
        description="Whether the intent is unclear and needs clarification"
    )
    
    clarification_questions: list[str] = Field(
        default_factory=list,
        description="Specific questions to ask the user for clarification"
    )
    
    user_message_summary: str = Field(
        description="A brief summary of what the user is asking for"
    )


class BookingParameters(BaseModel):
    """Layer 2: Validated and structured booking parameters."""
    
    action: Literal["book", "modify", "cancel", "query"] = Field(
        description="The specific booking action to perform"
    )
    
    # Booking/Search parameters
    date: str | None = Field(
        None, 
        description="Target date in YYYY-MM-DD format",
        pattern=r"^\d{4}-\d{2}-\d{2}$"
    )
    
    time_hour: int | None = Field(
        None,
        ge=0,
        le=23,
        description="Preferred hour in 24h format (0-23)"
    )
    
    time_minute: int | None = Field(
        None,
        ge=0,
        le=59,
        description="Preferred minute (0-59)"
    )
    
    provider_name: str | None = Field(
        None,
        description="Requested doctor/provider name"
    )
    
    provider_id: int | None = Field(
        None,
        description="Specific provider ID if known"
    )
    
    department: str | None = Field(
        None,
        description="Medical department (e.g., Cardiology, Pediatrics)"
    )
    
    reason: str | None = Field(
        None,
        description="Reason for appointment"
    )
    
    # Modification/Cancellation parameters
    appointment_id: int | None = Field(
        None,
        description="Appointment ID to modify or cancel"
    )
    
    confirmation_code: str | None = Field(
        None,
        description="Appointment confirmation code"
    )
    
    # Query parameters
    query_filter: Literal["upcoming", "past", "all"] | None = Field(
        None,
        description="Filter for appointment queries"
    )
    
    # Validation flags
    has_all_required_info: bool = Field(
        description="Whether all required information for the action is present"
    )
    
    missing_fields: list[str] = Field(
        default_factory=list,
        description="List of required fields that are missing"
    )
    
    ambiguities: list[str] = Field(
        default_factory=list,
        description="List of ambiguous or unclear parameters"
    )
    
    validation_notes: str = Field(
        default="",
        description="Additional validation notes or warnings"
    )


class ExecutionPlan(BaseModel):
    """Layer 3: Validated execution plan before taking action."""
    
    action_description: str = Field(
        description="Human-readable description of what will be executed"
    )
    
    parameters: BookingParameters = Field(
        description="The validated parameters to use"
    )
    
    tools_to_call: list[str] = Field(
        description="Ordered list of tools that will be called"
    )
    
    tool_arguments: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Arguments for each tool call"
    )
    
    execution_confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence that this execution plan is correct"
    )
    
    requires_user_confirmation: bool = Field(
        description="Whether to ask user confirmation before executing"
    )
    
    confirmation_message: str | None = Field(
        None,
        description="Message to show user for confirmation"
    )
    
    warning_messages: list[str] = Field(
        default_factory=list,
        description="Warnings or important notes about this execution"
    )
    
    can_execute: bool = Field(
        description="Whether this plan is safe and ready to execute"
    )
    
    blocking_issues: list[str] = Field(
        default_factory=list,
        description="Issues preventing execution (if can_execute is False)"
    )
