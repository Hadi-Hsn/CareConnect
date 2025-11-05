"""Test script for admin API functionality."""
import asyncio
from datetime import datetime, timedelta

import httpx


BASE_URL = "http://localhost:8000/api/v1"


async def test_admin_api():
    """Test admin API endpoints."""
    print("=" * 60)
    print("Admin API Test Suite")
    print("=" * 60)
    print()

    async with httpx.AsyncClient() as client:
        # 1. Login as admin
        print("1. Authenticating as admin...")
        login_response = await client.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": "hadi.wmail@gmail.com",
                "password": "admin123"
            }
        )
        
        if login_response.status_code != 200:
            print(f"   ✗ Login failed: {login_response.text}")
            return
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("   ✓ Admin authenticated")
        print()

        # 2. Get system stats
        print("2. Fetching system statistics...")
        stats_response = await client.get(
            f"{BASE_URL}/admin/stats/overview",
            headers=headers
        )
        
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"   ✓ Total doctors: {stats['total_doctors']}")
            print(f"   ✓ Total appointments: {stats['total_appointments']}")
            print(f"   ✓ Total users: {stats['total_users']}")
            print(f"   ✓ Upcoming appointments: {stats['upcoming_appointments']}")
        else:
            print(f"   ✗ Failed: {stats_response.text}")
        print()

        # 3. Create a new doctor
        print("3. Creating a new doctor...")
        doctor_data = {
            "name": "Dr. Test Doctor",
            "department": "General Medicine",
            "type": "physician",
            "specialty": "Family Medicine",
            "bio": "Test doctor for automated testing"
        }
        
        create_response = await client.post(
            f"{BASE_URL}/admin/doctors",
            headers=headers,
            json=doctor_data
        )
        
        if create_response.status_code == 201:
            doctor = create_response.json()
            doctor_id = doctor["id"]
            print(f"   ✓ Doctor created with ID: {doctor_id}")
            print(f"   ✓ Name: {doctor['name']}")
        else:
            print(f"   ✗ Failed: {create_response.text}")
            return
        print()

        # 4. Update doctor
        print("4. Updating doctor information...")
        update_response = await client.put(
            f"{BASE_URL}/admin/doctors/{doctor_id}",
            headers=headers,
            json={
                "specialty": "Family Medicine & Preventive Care",
                "bio": "Updated bio for testing"
            }
        )
        
        if update_response.status_code == 200:
            updated = update_response.json()
            print(f"   ✓ Doctor updated")
            print(f"   ✓ New specialty: {updated['specialty']}")
        else:
            print(f"   ✗ Failed: {update_response.text}")
        print()

        # 5. List all doctors
        print("5. Listing all doctors...")
        list_response = await client.get(
            f"{BASE_URL}/admin/doctors",
            headers=headers
        )
        
        if list_response.status_code == 200:
            doctors = list_response.json()
            print(f"   ✓ Found {len(doctors)} doctors")
            for doc in doctors[:3]:  # Show first 3
                print(f"     - {doc['name']} ({doc['department']})")
        else:
            print(f"   ✗ Failed: {list_response.text}")
        print()

        # 6. Get doctor schedule
        print("6. Fetching doctor schedule...")
        today = datetime.now().date()
        next_week = today + timedelta(days=7)
        
        schedule_response = await client.get(
            f"{BASE_URL}/admin/doctors/{doctor_id}/schedule",
            headers=headers,
            params={
                "date_from": today.isoformat(),
                "date_to": next_week.isoformat()
            }
        )
        
        if schedule_response.status_code == 200:
            schedule = schedule_response.json()
            print(f"   ✓ Schedule retrieved")
            print(f"   ✓ Total appointments: {schedule['total_appointments']}")
        else:
            print(f"   ✗ Failed: {schedule_response.text}")
        print()

        # 7. Block doctor time
        print("7. Blocking doctor time...")
        tomorrow = datetime.now() + timedelta(days=1)
        block_start = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
        block_end = block_start + timedelta(hours=2)
        
        block_response = await client.post(
            f"{BASE_URL}/admin/doctors/{doctor_id}/block-time",
            headers=headers,
            json={
                "time_start": block_start.isoformat(),
                "time_end": block_end.isoformat(),
                "reason": "Test block for automated testing"
            }
        )
        
        if block_response.status_code == 200:
            block = block_response.json()
            print(f"   ✓ Time blocked")
            print(f"   ✓ From: {block['time_start']}")
            print(f"   ✓ To: {block['time_end']}")
        else:
            print(f"   ✗ Failed: {block_response.text}")
        print()

        # 8. List appointments
        print("8. Listing appointments...")
        appts_response = await client.get(
            f"{BASE_URL}/admin/appointments",
            headers=headers,
            params={"limit": 10}
        )
        
        if appts_response.status_code == 200:
            appointments = appts_response.json()
            print(f"   ✓ Found {len(appointments)} recent appointments")
            for appt in appointments[:3]:  # Show first 3
                print(f"     - {appt['user_name']} with {appt['provider_name']}")
                print(f"       Status: {appt['status']}, Time: {appt['time_start']}")
        else:
            print(f"   ✗ Failed: {appts_response.text}")
        print()

        # 9. Test non-admin access (should fail)
        print("9. Testing non-admin access (should fail)...")
        patient_login = await client.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": "hadihacan@gmail.com",
                "password": "password123"
            }
        )
        
        if patient_login.status_code == 200:
            patient_token = patient_login.json()["access_token"]
            patient_headers = {"Authorization": f"Bearer {patient_token}"}
            
            forbidden_response = await client.get(
                f"{BASE_URL}/admin/stats/overview",
                headers=patient_headers
            )
            
            if forbidden_response.status_code == 403:
                print("   ✓ Non-admin access correctly denied (403)")
            else:
                print(f"   ✗ Unexpected response: {forbidden_response.status_code}")
        print()

        # 10. Delete test doctor
        print("10. Cleaning up - deleting test doctor...")
        delete_response = await client.delete(
            f"{BASE_URL}/admin/doctors/{doctor_id}",
            headers=headers
        )
        
        if delete_response.status_code == 204:
            print("   ✓ Test doctor deleted")
        else:
            print(f"   ✗ Failed: {delete_response.text}")
        print()

        print("=" * 60)
        print("✓ Admin API Test Suite Completed!")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_admin_api())
