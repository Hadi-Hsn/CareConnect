"""Schemas package."""
from app.schemas.agent import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    FeedbackRequest,
    FeedbackResponse,
    ToolCall,
    ToolResult,
)
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentUpdate,
    AppointmentWithDetails,
    BookingConfirmation,
)
from app.schemas.lab import LabTestCreate, LabTestResponse, LabTestUpdate
from app.schemas.metrics import EvaluationReport, HealthMetrics, KPIResponse, MetricSnapshot
from app.schemas.provider import (
    ProviderCreate,
    ProviderResponse,
    ProviderTimeslots,
    ProviderUpdate,
    TimeSlot,
)
from app.schemas.rag import (
    Document,
    DocumentChunk,
    IndexRequest,
    IndexResponse,
    RetrievalRequest,
    RetrievalResponse,
)
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserResponse, UserUpdate

__all__ = [
    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserLogin",
    "TokenResponse",
    # Provider
    "ProviderCreate",
    "ProviderUpdate",
    "ProviderResponse",
    "TimeSlot",
    "ProviderTimeslots",
    # Appointment
    "AppointmentCreate",
    "AppointmentUpdate",
    "AppointmentResponse",
    "AppointmentWithDetails",
    "BookingConfirmation",
    # Lab
    "LabTestCreate",
    "LabTestUpdate",
    "LabTestResponse",
    # Agent
    "ChatMessage",
    "ChatRequest",
    "ChatResponse",
    "ToolCall",
    "ToolResult",
    "FeedbackRequest",
    "FeedbackResponse",
    # RAG
    "Document",
    "DocumentChunk",
    "IndexRequest",
    "IndexResponse",
    "RetrievalRequest",
    "RetrievalResponse",
    # Metrics
    "EvaluationReport",
    "MetricSnapshot",
    "KPIResponse",
    "HealthMetrics",
]
