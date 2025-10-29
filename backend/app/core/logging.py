"""Structured logging configuration."""
import logging
import sys
from typing import Any

import structlog
from structlog.typing import EventDict, Processor

from app.core.config import get_settings

settings = get_settings()


def add_privacy_masking(
    logger: logging.Logger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Mask PHI in logs when privacy mode is enabled."""
    if not settings.enable_privacy_mode:
        return event_dict

    # Fields to mask
    sensitive_fields = ["email", "phone", "ssn", "date_of_birth", "patient_id", "user_id"]

    for field in sensitive_fields:
        if field in event_dict:
            value = str(event_dict[field])
            if len(value) > 4:
                event_dict[field] = f"{value[:2]}***{value[-2:]}"
            else:
                event_dict[field] = "***"

    return event_dict


def add_request_id(
    logger: logging.Logger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Add request ID to log entries."""
    # Will be set by middleware
    return event_dict


def setup_logging() -> None:
    """Configure structured logging."""
    log_level = getattr(logging, settings.log_level.upper())

    # Configure structlog
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        add_privacy_masking,
        add_request_id,
    ]

    if settings.is_production:
        # JSON formatting for production
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Pretty console output for development
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )


def get_logger(name: str) -> Any:
    """Get a structured logger."""
    return structlog.get_logger(name)
