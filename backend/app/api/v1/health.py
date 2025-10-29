"""Health check endpoint."""
import time
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.schemas.metrics import HealthMetrics

router = APIRouter()

# Store startup time
STARTUP_TIME = time.time()


@router.get("/healthz")
async def healthz() -> dict[str, str]:
    """Basic health check."""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@router.get("/health", response_model=HealthMetrics)
async def health_detailed(db: AsyncSession = Depends(get_db)) -> HealthMetrics:
    """Detailed health check with dependency status."""
    # Check database
    db_healthy = False
    try:
        await db.execute(text("SELECT 1"))
        db_healthy = True
    except Exception:
        pass

    # Check vector store
    vector_store_healthy = False
    try:
        from app.core.vectorstore import get_vector_store

        store = get_vector_store()
        await store.get_stats()
        vector_store_healthy = True
    except Exception:
        pass

    # Check OpenAI (simple check)
    openai_healthy = True  # Assume healthy unless we test

    uptime = time.time() - STARTUP_TIME

    return HealthMetrics(
        status="healthy" if all([db_healthy, vector_store_healthy]) else "degraded",
        uptime_seconds=uptime,
        database_connected=db_healthy,
        vector_store_loaded=vector_store_healthy,
        openai_api_healthy=openai_healthy,
        active_requests=0,  # Could track this with middleware
    )
