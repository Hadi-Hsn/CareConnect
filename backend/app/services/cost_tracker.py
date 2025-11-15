"""Cost tracking service for monitoring API usage and costs."""
import csv
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Pricing (as of Nov 2024)
GPT4O_INPUT_COST_PER_1K = 0.0025  # $0.0025 per 1K input tokens
GPT4O_OUTPUT_COST_PER_1K = 0.010  # $0.01 per 1K output tokens
EMBEDDING_COST_PER_1K = 0.00013  # text-embedding-3-large

COST_LOG_PATH = Path("/app/data/cost_log.csv")


class CostTracker:
    """Track and log API costs per request."""

    def __init__(self):
        """Initialize cost tracker."""
        self.ensure_log_file()

    def ensure_log_file(self):
        """Create cost log file with headers if it doesn't exist."""
        if not COST_LOG_PATH.exists():
            COST_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(COST_LOG_PATH, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "task_id",
                    "task_type",
                    "timestamp",
                    "input_tokens",
                    "output_tokens",
                    "total_tokens",
                    "api_cost_usd",
                    "success",
                    "latency_ms",
                    "model",
                    "user_id"
                ])

    def log_completion(
        self,
        task_id: str,
        task_type: str,
        input_tokens: int,
        output_tokens: int,
        success: bool,
        latency_ms: float,
        model: str = "gpt-4o",
        user_id: int | None = None
    ) -> dict[str, Any]:
        """
        Log a completion cost.
        
        Args:
            task_id: Unique identifier for the task
            task_type: Type of task (chat, booking, info_query, etc.)
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens generated
            success: Whether the task completed successfully
            latency_ms: Response time in milliseconds
            model: Model used (default: gpt-4o)
            user_id: Optional user ID
        
        Returns:
            dict with cost breakdown
        """
        # Calculate costs
        input_cost = (input_tokens / 1000) * GPT4O_INPUT_COST_PER_1K
        output_cost = (output_tokens / 1000) * GPT4O_OUTPUT_COST_PER_1K
        total_cost = input_cost + output_cost
        total_tokens = input_tokens + output_tokens

        # Log to file
        try:
            with open(COST_LOG_PATH, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    task_id,
                    task_type,
                    datetime.now(timezone.utc).isoformat(),
                    input_tokens,
                    output_tokens,
                    total_tokens,
                    f"{total_cost:.6f}",
                    success,
                    f"{latency_ms:.2f}",
                    model,
                    user_id or ""
                ])
        except Exception as e:
            logger.error("cost_log_write_failed", error=str(e))

        # Log to structured logger
        logger.info(
            "api_cost_tracked",
            task_id=task_id,
            task_type=task_type,
            total_tokens=total_tokens,
            cost_usd=total_cost,
            success=success,
            latency_ms=latency_ms
        )

        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "input_cost_usd": input_cost,
            "output_cost_usd": output_cost,
            "total_cost_usd": total_cost,
            "success": success,
            "latency_ms": latency_ms
        }

    def log_embedding(
        self,
        task_id: str,
        tokens: int,
        success: bool,
        latency_ms: float,
        user_id: int | None = None
    ) -> dict[str, Any]:
        """Log embedding API cost."""
        cost = (tokens / 1000) * EMBEDDING_COST_PER_1K

        try:
            with open(COST_LOG_PATH, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    task_id,
                    "embedding",
                    datetime.now(timezone.utc).isoformat(),
                    tokens,
                    0,
                    tokens,
                    f"{cost:.6f}",
                    success,
                    f"{latency_ms:.2f}",
                    "text-embedding-3-large",
                    user_id or ""
                ])
        except Exception as e:
            logger.error("cost_log_write_failed", error=str(e))

        return {
            "tokens": tokens,
            "cost_usd": cost,
            "success": success,
            "latency_ms": latency_ms
        }

    def get_summary_stats(self) -> dict[str, Any]:
        """Get summary statistics from cost log."""
        if not COST_LOG_PATH.exists():
            return {
                "total_tasks": 0,
                "total_cost_usd": 0,
                "avg_cost_per_task": 0,
                "total_tokens": 0,
                "success_rate": 0
            }

        total_cost = 0
        total_tasks = 0
        successful_tasks = 0
        total_tokens = 0

        with open(COST_LOG_PATH, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                total_tasks += 1
                total_cost += float(row["api_cost_usd"])
                total_tokens += int(row["total_tokens"])
                if row["success"].lower() == "true":
                    successful_tasks += 1

        return {
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "total_cost_usd": round(total_cost, 4),
            "avg_cost_per_task": round(total_cost / total_tasks, 4) if total_tasks > 0 else 0,
            "cost_per_successful_task": round(total_cost / successful_tasks, 4) if successful_tasks > 0 else 0,
            "total_tokens": total_tokens,
            "success_rate": round(successful_tasks / total_tasks, 3) if total_tasks > 0 else 0
        }


# Global instance
cost_tracker = CostTracker()
