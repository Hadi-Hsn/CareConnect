"""Utilities to make sure critical provider records exist."""
from datetime import datetime, timezone

from sqlalchemy import select

from app.core.db import async_session_maker
from app.core.logging import get_logger
from app.models import Provider, ProviderType

logger = get_logger(__name__)

LAB_PROVIDERS = [
    {
        "name": "Lab Services Team A",
        "department": "Laboratory",
        "type": ProviderType.SPECIALIST,
        "specialty": "Diagnostic Lab Testing",
        "bio": "Core laboratory team handling specimen collection and diagnostic testing",
    },
    {
        "name": "Lab Services Team B",
        "department": "Laboratory",
        "type": ProviderType.SPECIALIST,
        "specialty": "Diagnostic Lab Testing",
        "bio": "Experienced technologists ensuring timely turnaround for comprehensive panels",
    },
    {
        "name": "Lab Services Team C",
        "department": "Laboratory",
        "type": ProviderType.SPECIALIST,
        "specialty": "Diagnostic Lab Testing",
        "bio": "Dedicated lab technicians supporting high-volume test scheduling",
    },
]


async def ensure_lab_providers() -> None:
    """Ensure there are providers to handle laboratory appointments."""
    try:
        async with async_session_maker() as session:
            # Check if providers table exists by trying to query it
            try:
                result = await session.execute(
                    select(Provider.name).where(Provider.department == "Laboratory")
                )
                existing_names = {row[0] for row in result.all()}
            except Exception as e:
                # Table doesn't exist yet or database not initialized
                logger.warning(
                    "providers_table_not_ready",
                    error=str(e),
                    message="Providers table not available yet, skipping lab provider initialization",
                )
                return

            missing = [
                Provider(
                    **provider,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
                for provider in LAB_PROVIDERS
                if provider["name"] not in existing_names
            ]

            if not missing:
                logger.debug("lab_providers_already_exist", count=len(LAB_PROVIDERS))
                return

            session.add_all(missing)
            await session.commit()

            logger.info("lab_providers_initialized", count=len(missing))
    except Exception as e:
        # Don't crash the application if provider initialization fails
        logger.error(
            "failed_to_initialize_lab_providers",
            error=str(e),
            message="Failed to initialize lab providers, but continuing startup",
            exc_info=True,
        )

