"""Clear all providers from the database to allow re-seeding."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.db import async_session_maker


async def clear_providers():
    """Delete all providers from the database."""
    async with async_session_maker() as session:
        result = await session.execute(text("DELETE FROM providers"))
        await session.commit()
        print(f"✓ Deleted all providers from database")


if __name__ == "__main__":
    asyncio.run(clear_providers())
