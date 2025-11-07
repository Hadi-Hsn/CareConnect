"""Database configuration and session management."""
from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy import MetaData, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Naming convention for constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)


class Base(DeclarativeBase):
    """Base class for all models."""

    metadata = metadata


# Create async engine with SQLite-specific settings
engine_args = {
    "echo": settings.log_level == "DEBUG",
    "future": True,
}

# Add SQLite-specific connection arguments if using SQLite
if settings.database_url.startswith("sqlite"):
    engine_args["connect_args"] = {"check_same_thread": False}
else:
    engine_args["pool_pre_ping"] = True

engine = create_async_engine(
    settings.database_url,
    **engine_args,
)

# Create sessionmaker
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("database_initialized")
    except Exception as e:
        # Log but don't fail if tables already exist
        if "already exists" in str(e):
            logger.info("database_tables_already_exist")
        else:
            raise


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()
    logger.info("database_closed")
