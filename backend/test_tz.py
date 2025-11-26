from datetime import datetime
from zoneinfo import ZoneInfo

LEBANON_TZ = ZoneInfo('Asia/Beirut')

# Test: If we have 10:00 AM Lebanon time stored
lebanon_10am = datetime(2025, 11, 27, 10, 0, 0, tzinfo=LEBANON_TZ)
print(f'Lebanon 10:00 AM = {lebanon_10am}')
print(f'As UTC = {lebanon_10am.astimezone(ZoneInfo("UTC"))}')

# Now simulate what happens when retrieved from DB (as UTC)
utc_time = lebanon_10am.astimezone(ZoneInfo('UTC'))
print(f'UTC stored = {utc_time}')

# Convert back to Lebanon
back_to_lebanon = utc_time.astimezone(LEBANON_TZ)
print(f'Back to Lebanon = {back_to_lebanon}')
print(f'Formatted = {back_to_lebanon.strftime("%I:%M %p")}')

print()
print("--- Docker timezone issue simulation ---")
# If Docker is in a different timezone and the DB stores without proper TZ handling
# Simulating: time is stored as 10:00 (thinking it's UTC but it's actually Lebanon)
naive_10am = datetime(2025, 11, 27, 10, 0, 0)  # No timezone
print(f'Naive 10:00 = {naive_10am}')

# If we treat it as UTC and convert to Lebanon
wrong_conversion = naive_10am.replace(tzinfo=ZoneInfo('UTC')).astimezone(LEBANON_TZ)
print(f'Wrong conversion (treating as UTC) = {wrong_conversion}')
print(f'Wrong formatted = {wrong_conversion.strftime("%I:%M %p")}')

print()
print("--- Current system info ---")
import time
print(f'Local timezone: {time.tzname}')
print(f'Current local time: {datetime.now()}')
print(f'Current UTC time: {datetime.now(ZoneInfo("UTC"))}')
print(f'Current Lebanon time: {datetime.now(LEBANON_TZ)}')
