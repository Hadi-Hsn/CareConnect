"""FastAPI application entry point."""
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.v1 import admin, appointments, auth, email, files, handover, health, labs, metrics, providers, rag, voice
from app.api.v1.agent import chat as agent_chat
from app.core.config import get_settings
from app.core.db import close_db, init_db
from app.core.logging import get_logger, setup_logging

# Setup logging first
setup_logging()
logger = get_logger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    logger.info("starting_application", environment=settings.environment)
    await init_db()
    yield
    logger.info("shutting_down_application")
    await close_db()


# Rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])

# Create FastAPI app
app = FastAPI(
    title="CareConnect API",
    description="Smart Health Assistant - Backend API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware - ALLOW ALL ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID to each request."""
    request_id = str(uuid.uuid4())
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id)

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=exc,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if not settings.is_production else "An error occurred",
        },
    )


# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(agent_chat.router, prefix="/api/v1/agent", tags=["Agent"])
app.include_router(handover.router, prefix="/api/v1/handover", tags=["Handover"])
app.include_router(voice.router, prefix="/api/v1/voice", tags=["Voice"])
app.include_router(rag.router, prefix="/api/v1/rag", tags=["RAG"])
app.include_router(files.router, prefix="/api/v1/files", tags=["Files"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(providers.router, prefix="/api/v1/providers", tags=["Providers"])
app.include_router(appointments.router, prefix="/api/v1/appointments", tags=["Appointments"])
app.include_router(labs.router, prefix="/api/v1/labs", tags=["Labs"])
app.include_router(email.router, prefix="/api/v1/email", tags=["Email"])
app.include_router(metrics.router, prefix="/api/v1/eval", tags=["Evaluation"])

# Prometheus metrics endpoint
if settings.enable_prometheus:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "environment": settings.environment,
        "docs": "/docs",
    }
