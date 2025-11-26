"""Check Lisa appointment timezone handling."""
import asyncio
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.models.appointment import Appointment
from app.models.provider import Provider
from app.models.user import User
from app.core.config import get_settings

# Lebanon timezone
LEBANON_TZ = ZoneInfo("Asia/Beirut")

async def check_appointment_by_code(code: str):
    """Check appointment by confirmation code and verify timezone handling."""
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
            print(f"❌ Appointment with confirmation code '{code}' not found in database")
            return
        
        appt, user, provider = appointment_data
        
        print("=" * 70)
        print(f"📅 APPOINTMENT FOUND")
        print("=" * 70)
        print(f"Appointment ID: {appt.id}")
        print(f"Confirmation Code: {appt.confirmation_code}")
        print(f"👤 Patient: {user.name} ({user.email})")
        print(f"👨‍⚕️ Provider: {provider.name} ({provider.specialty})")
        print(f"📋 Status: {appt.status}")
        print(f"📝 Reason: {appt.reason}")
        print()
        
        # Get the stored UTC time
        utc_time = appt.time_start
        print(f"🕐 STORED IN DATABASE (UTC):")
        print(f"   Raw datetime: {utc_time}")
        print(f"   Formatted: {utc_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"   ISO Format: {utc_time.isoformat()}")
        print()
        
        # Convert to Lebanon time
        lebanon_time = utc_time.astimezone(LEBANON_TZ)
        print(f"🌍 CONVERTED TO LEBANON TIME (Asia/Beirut):")
        print(f"   Full datetime: {lebanon_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"   Display format: {lebanon_time.strftime('%B %d, %Y at %I:%M %p')}")
        print(f"   Time only: {lebanon_time.strftime('%I:%M %p')}")
        print()
        
        # Calculate offset
        offset = lebanon_time.utcoffset()
        print(f"⏰ TIMEZONE INFO:")
        print(f"   UTC Offset: {offset}")
        print(f"   Timezone: {lebanon_time.tzname()}")
        print()
        
        # Show what different timezones would display
        print(f"🌎 TIME COMPARISON:")
        print(f"   UTC:        {utc_time.strftime('%I:%M %p')}")
        print(f"   Lebanon:    {lebanon_time.strftime('%I:%M %p')}")
        print()
        
        # Diagnosis
        print(f"🔍 DIAGNOSIS:")
        if lebanon_time.hour == 13:  # 1 PM
            print(f"   ✅ Lebanon time shows 1:00 PM - MATCHES appointment list")
            print(f"   ⚠️  If agent said 3:00 PM, there's a BUG in agent response")
        elif lebanon_time.hour == 15:  # 3 PM
            print(f"   ✅ Lebanon time shows 3:00 PM - MATCHES agent message")
            print(f"   ⚠️  If appointment list shows 1:00 PM, there's a BUG in frontend")
        else:
            print(f"   ℹ️  Time is {lebanon_time.strftime('%I:%M %p')} Lebanon time")
        
        print("=" * 70)
    
    await engine.dispose()

if __name__ == "__main__":
    APPOINTMENT_CODE = "424E667B75B8A26E"
    print(f"🔍 Checking appointment {APPOINTMENT_CODE}...\n")
    asyncio.run(check_appointment_by_code(APPOINTMENT_CODE))
