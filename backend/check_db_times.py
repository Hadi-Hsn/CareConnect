import asyncio
from sqlalchemy import select, text
from app.core.db import async_session_maker
from app.models.appointment import Appointment
from zoneinfo import ZoneInfo

LEBANON_TZ = ZoneInfo('Asia/Beirut')

async def check_appointments():
    async with async_session_maker() as session:
        result = await session.execute(
            select(Appointment).limit(5)
        )
        appointments = result.scalars().all()
        
        print("=== Appointment Times in Database ===")
        for appt in appointments:
            print(f"\nAppointment ID: {appt.id}")
            print(f"  Raw time_start: {appt.time_start}")
            print(f"  tzinfo: {appt.time_start.tzinfo}")
            print(f"  time_start.astimezone(LEBANON_TZ): {appt.time_start.astimezone(LEBANON_TZ)}")
            print(f"  Formatted: {appt.time_start.astimezone(LEBANON_TZ).strftime('%I:%M %p')}")
            
            # Check if time has UTC offset info
            if appt.time_start.utcoffset():
                print(f"  UTC offset: {appt.time_start.utcoffset()}")
            else:
                print(f"  UTC offset: None (naive datetime)")
                
        # Also raw SQL check
        print("\n=== Raw SQL Query ===")
        raw_result = await session.execute(
            text("SELECT id, time_start, time_start AT TIME ZONE 'Asia/Beirut' as lebanon_time FROM appointment LIMIT 5")
        )
        for row in raw_result:
            print(f"ID: {row[0]}, Raw: {row[1]}, Lebanon: {row[2]}")

asyncio.run(check_appointments())
