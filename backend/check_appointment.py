"""Check appointment timezone handling."""
import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo
from app.core.db import async_session_maker
from app.models import Appointment, Provider
from sqlalchemy import select


async def check_appointment():
    """Check the appointment with confirmation code 3EE5E12F8CF5E388."""
    async with async_session_maker() as session:
        result = await session.execute(
            select(Appointment, Provider)
            .join(Provider, Appointment.provider_id == Provider.id)
            .where(Appointment.confirmation_code == '3EE5E12F8CF5E388')
        )
        row = result.first()
        
        if not row:
            print("❌ Appointment not found")
            return
        
        apt, prov = row
        lebanon_tz = ZoneInfo("Asia/Beirut")
        
        print("\n" + "="*80)
        print("APPOINTMENT DETAILS")
        print("="*80)
        print(f"Confirmation Code: {apt.confirmation_code}")
        print(f"Provider: {prov.name}")
        print(f"Department: {prov.department}")
        print(f"Status: {apt.status}")
        print(f"\nTime Details:")
        print(f"  Stored in DB (UTC): {apt.time_start}")
        print(f"  UTC timezone aware: {apt.time_start.tzinfo}")
        
        # Convert to Lebanon time
        lebanon_time = apt.time_start.astimezone(lebanon_tz)
        print(f"  Lebanon time: {lebanon_time}")
        print(f"  Lebanon formatted: {lebanon_time.strftime('%B %d, %Y at %I:%M %p')}")
        print(f"  Hour (Lebanon): {lebanon_time.hour}")
        print(f"  Minute (Lebanon): {lebanon_time.minute}")
        
        # Check what the API would return
        print(f"\nAPI Response Format:")
        print(f"  date: {lebanon_time.strftime('%Y-%m-%d')}")
        print(f"  time: {lebanon_time.strftime('%I:%M %p')}")
        print(f"  datetime_display: {lebanon_time.strftime('%B %d, %Y at %I:%M %p')}")
        print("="*80)


if __name__ == "__main__":
    asyncio.run(check_appointment())
