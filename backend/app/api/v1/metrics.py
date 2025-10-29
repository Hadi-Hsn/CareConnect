"""Evaluation and metrics endpoints."""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.logging import get_logger
from app.schemas.metrics import EvaluationReport, KPIResponse

router = APIRouter()
logger = get_logger(__name__)


@router.post("/report")
async def submit_evaluation(
    report: EvaluationReport, db: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    """Submit an evaluation report from human adjudication."""
    # In production, store this in database
    logger.info(
        "evaluation_reported",
        task_type=report.task_type,
        success=report.success,
        satisfaction=report.satisfaction_score,
        ambiguity_resolved=report.ambiguity_resolved,
    )

    return {"message": "Evaluation report received", "status": "recorded"}


@router.get("/kpis", response_model=KPIResponse)
async def get_kpis(
    days: int = 7, db: AsyncSession = Depends(get_db)
) -> KPIResponse:
    """Get KPI metrics for evaluation."""
    # In production, calculate from database
    # For now, return mock data

    period_end = datetime.now(timezone.utc)
    period_start = period_end - timedelta(days=days)

    # Mock KPIs - in production, query from stored metrics
    return KPIResponse(
        task_completion_rate=0.92,  # 92% success rate
        avg_response_time_p50=1.8,  # 1.8s at p50
        avg_response_time_p90=3.2,  # 3.2s at p90
        avg_response_time_p99=5.5,  # 5.5s at p99
        ambiguity_success_rate=0.88,  # 88% ambiguous queries resolved
        avg_satisfaction_score=4.3,  # 4.3/5 average satisfaction
        total_conversations=156,
        period_start=period_start,
        period_end=period_end,
    )
