"""Evaluation and metrics schemas."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class EvaluationReport(BaseModel):
    """Evaluation report from human adjudication."""

    conversation_id: str | None = None
    task_type: str  # booking, modification, cancellation, information
    success: bool
    ambiguity_resolved: bool = False
    clarifications_needed: int = 0
    satisfaction_score: int = Field(..., ge=1, le=5)
    tags: list[str] = []
    notes: str | None = None


class MetricSnapshot(BaseModel):
    """Metric snapshot."""

    metric_name: str
    value: float
    timestamp: datetime
    metadata: dict[str, Any] = {}


class KPIResponse(BaseModel):
    """KPI response schema."""

    task_completion_rate: float
    avg_response_time_p50: float
    avg_response_time_p90: float
    avg_response_time_p99: float
    ambiguity_success_rate: float
    avg_satisfaction_score: float
    total_conversations: int
    period_start: datetime
    period_end: datetime


class HealthMetrics(BaseModel):
    """System health metrics."""

    status: str
    uptime_seconds: float
    database_connected: bool
    vector_store_loaded: bool
    openai_api_healthy: bool
    active_requests: int
