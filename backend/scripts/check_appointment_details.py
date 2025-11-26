"""Check specific appointment details."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.models.appointment import Appointment
from app.models.provider import Provider
from app.models.user import User
from app.core.config import get_settings

async def check_appointment_by_code(code: str):
    """Check appointment by confirmation code."""
    settings = get_settings()
    
    # Create engine
    engine_args = {
        "echo": False,
        "future": True,
    }
    if settings.database_url.startswith("sqlite"):
        engine_args["connect_args"] = {"check_same_thread": False}
    
    engine = create_async_engine(settings.database_url, **engine_args)
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session_maker() as session:
        # Find appointment by confirmation_code
        stmt = (
            select(Appointment, User, Provider)
            .join(User, Appointment.user_id == User.id)
            .join(Provider, Appointment.provider_id == Provider.id)
            .where(Appointment.confirmation_code == code)
        )
        result = await session.execute(stmt)
        appointment_data = result.first()
        
        if not appointment_data:
            print(f"Appointment with code '{code}' not found")
            return
        
        appt, user, provider = appointment_data
        
        unknown = "Unknown"
        patient_name = user.name if user else unknown
        provider_name = provider.name if provider else unknown
        provider_dept = provider.department if provider else unknown
        
        print("=" * 70)
        print("APPOINTMENT DETAILS")
        print("=" * 70)
        print(f"Confirmation Code: {appt.confirmation_code}")
        print(f"Patient ID: {appt.user_id}")
        print(f"Patient Name: {patient_name}")
        print(f"Provider ID: {appt.provider_id}")
        print(f"Provider Name: {provider_name}")
        print(f"Department: {provider_dept}")
        print(f"Appointment Time: {appt.time_start}")
        print(f"Reason: {appt.reason}")
        print(f"Status: {appt.status}")
        print("=" * 70)
    
    await engine.dispose()

if __name__ == "__main__":
    APPOINTMENT_CODE = "62A040B1EA36C8CB"
    print(f"Checking appointment {APPOINTMENT_CODE}...\n")
    asyncio.run(check_appointment_by_code(APPOINTMENT_CODE))
