"""Quick check of database population."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import select, func
from app.core.db import async_session_maker
from app.models import Provider, User, PatientTestResult, Appointment


async def check_data():
    async with async_session_maker() as session:
        providers_count = await session.execute(select(func.count(Provider.id)))
        users_count = await session.execute(select(func.count(User.id)))
        tests_count = await session.execute(select(func.count(PatientTestResult.id)))
        appointments_count = await session.execute(select(func.count(Appointment.id)))
        
        print("=" * 50)
        print("DATABASE POPULATION CHECK")
        print("=" * 50)
        print(f"Providers: {providers_count.scalar()}")
        print(f"Users: {users_count.scalar()}")
        print(f"Appointments: {appointments_count.scalar()}")
        print(f"Test Results: {tests_count.scalar()}")
        print("=" * 50)


if __name__ == "__main__":
    asyncio.run(check_data())
