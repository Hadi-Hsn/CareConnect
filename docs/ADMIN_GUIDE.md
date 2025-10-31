# Admin User Guide

## Getting Started

### Access the System

1. **Login Credentials**
   - Email: `admin@careconnect.health`
   - Password: `admin123` (change in production!)

2. **API Documentation**
   - Interactive docs: http://localhost:8000/docs
   - Admin endpoints: All under `/api/v1/admin/*`

### Quick Test

```bash
# Test admin access
docker exec careconnect-backend python scripts/test_admin_api.py
```

---

## Managing Doctors

### Add a New Doctor

**Via API:**
```bash
curl -X POST http://localhost:8000/api/v1/admin/doctors \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr. Sarah Williams",
    "department": "Neurology",
    "type": "physician",
    "specialty": "Pediatric Neurology",
    "bio": "Board-certified neurologist specializing in pediatric care..."
  }'
```

**What you'll get:**
- Doctor ID (use this for further operations)
- Confirmation of creation
- Full doctor profile

### Upload Doctor Profile PDF

After creating a doctor, upload their detailed profile:

```bash
curl -X POST http://localhost:8000/api/v1/admin/doctors/10/upload-profile \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@dr_sarah_williams_profile.pdf"
```

**What happens:**
1. PDF is parsed and text extracted
2. Content is embedded using AI
3. Profile becomes searchable via RAG system
4. Patients and chat agent can find this doctor

### Update Doctor Information

```bash
curl -X PUT http://localhost:8000/api/v1/admin/doctors/10 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "specialty": "Pediatric & Adult Neurology",
    "bio": "Updated bio with new certifications..."
  }'
```

### View All Doctors

```bash
curl http://localhost:8000/api/v1/admin/doctors \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Filter by department:**
```bash
curl "http://localhost:8000/api/v1/admin/doctors?department=Cardiology" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Remove a Doctor

⚠️ **Warning:** This cancels all future appointments!

```bash
curl -X DELETE http://localhost:8000/api/v1/admin/doctors/10 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Best practice:** Before deleting:
1. Check their schedule
2. Reschedule existing appointments
3. Notify affected patients

---

## Managing Appointments

### View All Appointments

```bash
# All appointments
curl http://localhost:8000/api/v1/admin/appointments \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filter by date range
curl "http://localhost:8000/api/v1/admin/appointments?date_from=2025-11-01&date_to=2025-11-30" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filter by status
curl "http://localhost:8000/api/v1/admin/appointments?status=pending" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Create Appointment for Patient

```bash
curl -X POST http://localhost:8000/api/v1/admin/appointments \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 25,
    "provider_id": 10,
    "time_start": "2025-11-05T10:00:00Z",
    "time_end": "2025-11-05T10:30:00Z",
    "reason": "Follow-up consultation",
    "channel": "phone"
  }'
```

**Note:** Admin-created appointments are auto-confirmed.

### Reschedule Appointment

```bash
curl -X PUT http://localhost:8000/api/v1/admin/appointments/123 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "time_start": "2025-11-05T14:00:00Z",
    "time_end": "2025-11-05T14:30:00Z",
    "notes": "Rescheduled at patient request"
  }'
```

### Update Appointment Status

```bash
# Confirm appointment
curl -X PATCH "http://localhost:8000/api/v1/admin/appointments/123/status?status=confirmed" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Mark as completed
curl -X PATCH "http://localhost:8000/api/v1/admin/appointments/123/status?status=completed" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Mark as no-show
curl -X PATCH "http://localhost:8000/api/v1/admin/appointments/123/status?status=no_show" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Cancel Appointment

```bash
curl -X DELETE http://localhost:8000/api/v1/admin/appointments/123 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Managing Doctor Schedules

### View Doctor's Schedule

```bash
curl "http://localhost:8000/api/v1/admin/doctors/10/schedule?date_from=2025-11-01&date_to=2025-11-07" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Shows:**
- All appointments in date range
- Patient information
- Appointment status
- Available gaps

### Block Time (Vacation, Meeting, etc.)

```bash
curl -X POST http://localhost:8000/api/v1/admin/doctors/10/block-time \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "time_start": "2025-12-20T00:00:00Z",
    "time_end": "2025-12-31T23:59:59Z",
    "reason": "Winter vacation"
  }'
```

**Use cases:**
- Vacation time
- Conference attendance
- Training sessions
- Administrative work
- Emergency leave

### Update Availability Calendar

Link doctor with external scheduling system:

```bash
curl -X PUT http://localhost:8000/api/v1/admin/doctors/10/availability \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"availability_calendar_id": "epic_calendar_789"}'
```

---

## Common Admin Tasks

### Daily Operations

#### 1. Review Pending Appointments

```bash
# Get all pending
curl "http://localhost:8000/api/v1/admin/appointments?status=pending" \
  -H "Authorization: Bearer YOUR_TOKEN" | jq

# Confirm each one
for id in $(curl -s "..." | jq -r '.[].id'); do
  curl -X PATCH "http://localhost:8000/api/v1/admin/appointments/$id/status?status=confirmed" \
    -H "Authorization: Bearer YOUR_TOKEN"
done
```

#### 2. Check Today's Schedule

```bash
TODAY=$(date +%Y-%m-%d)

curl "http://localhost:8000/api/v1/admin/appointments?date_from=$TODAY&date_to=$TODAY" \
  -H "Authorization: Bearer YOUR_TOKEN" | jq
```

#### 3. View System Health

```bash
curl http://localhost:8000/api/v1/admin/stats/overview \
  -H "Authorization: Bearer YOUR_TOKEN" | jq
```

### Weekly Tasks

#### 1. Onboard New Doctor

```bash
#!/bin/bash

TOKEN="your_admin_token"

# Create doctor
DOCTOR=$(curl -s -X POST http://localhost:8000/api/v1/admin/doctors \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr. New Doctor",
    "department": "Cardiology",
    "type": "physician",
    "specialty": "Interventional Cardiology"
  }')

DOCTOR_ID=$(echo $DOCTOR | jq -r '.id')

# Upload profile
curl -X POST http://localhost:8000/api/v1/admin/doctors/$DOCTOR_ID/upload-profile \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@profile.pdf"

# Set calendar
curl -X PUT http://localhost:8000/api/v1/admin/doctors/$DOCTOR_ID/availability \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"availability_calendar_id": "cal_new_123"}'

echo "Doctor onboarded with ID: $DOCTOR_ID"
```

#### 2. Review No-Shows

```bash
curl "http://localhost:8000/api/v1/admin/appointments?status=no_show&date_from=2025-10-24&date_to=2025-10-31" \
  -H "Authorization: Bearer YOUR_TOKEN" | jq
```

### Monthly Tasks

#### 1. Generate Reports

```bash
# Get stats
STATS=$(curl -s http://localhost:8000/api/v1/admin/stats/overview \
  -H "Authorization: Bearer YOUR_TOKEN")

echo "Monthly Report - $(date +%B\ %Y)"
echo "================================"
echo "Total Doctors: $(echo $STATS | jq -r '.total_doctors')"
echo "Total Appointments: $(echo $STATS | jq -r '.total_appointments')"
echo "Upcoming: $(echo $STATS | jq -r '.upcoming_appointments')"
echo ""
echo "By Status:"
echo $STATS | jq -r '.appointments_by_status | to_entries[] | "  \(.key): \(.value)"'
```

#### 2. Update Doctor Profiles

```bash
# Update all doctors with new policy
curl http://localhost:8000/api/v1/admin/doctors \
  -H "Authorization: Bearer $TOKEN" | jq -r '.[].id' | while read ID; do
  
  curl -X PUT http://localhost:8000/api/v1/admin/doctors/$ID \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"bio": "Updated to include new telemedicine policy..."}'
  
done
```

---

## Using the Web Interface

While the API is powerful, you can also use the interactive documentation:

1. **Open Browser:** http://localhost:8000/docs
2. **Authorize:**
   - Click "Authorize" button
   - Enter: `Bearer YOUR_TOKEN`
   - Click "Authorize"
3. **Navigate:** Find "Admin" section
4. **Test Endpoints:** Click, fill forms, execute

**Benefits:**
- Visual interface
- Automatic validation
- See request/response formats
- No command-line needed

---

## Troubleshooting

### "Admin access required" Error

**Problem:** Getting 403 Forbidden

**Solutions:**
1. Verify you're logged in as admin:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "admin@careconnect.health", "password": "admin123"}'
   ```

2. Check token is valid:
   ```bash
   # Token should not be expired (24 hour validity)
   ```

3. Ensure proper header format:
   ```bash
   Authorization: Bearer eyJhbGc...
   # Note: "Bearer " prefix is required
   ```

### Doctor Not Found

**Problem:** 404 error when accessing doctor

**Solutions:**
1. List all doctors to find correct ID
2. Check if doctor was deleted
3. Verify database connection

### Cannot Delete Doctor

**Problem:** Error when trying to delete

**Possible causes:**
- Doctor has future appointments
- Database constraint violation

**Solution:**
1. Check doctor's schedule
2. Manually cancel/reschedule appointments first
3. Then delete doctor

### PDF Upload Fails

**Problem:** PDF upload returns error

**Common issues:**
1. **File not PDF:** Only PDF files accepted
2. **Empty PDF:** PDF has no extractable text
3. **File too large:** Check file size limits
4. **OpenAI error:** Check API key and quota

**Debug:**
```bash
# Check PDF locally first
docker exec careconnect-backend python -c "
from app.services.pdf_parser import PDFParser
text = PDFParser.extract_text_from_file('/path/to/file.pdf')
print(f'Extracted {len(text)} characters')
"
```

---

## Security Best Practices

### 1. Change Default Password

```bash
# Create new admin user with strong password
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin-new@careconnect.health",
    "password": "STRONG_SECURE_PASSWORD",
    "name": "Admin User",
    "role": "admin"
  }'
```

### 2. Rotate Tokens Regularly

- Tokens expire after 24 hours
- Re-login daily for security
- Don't share tokens

### 3. Use HTTPS in Production

- All API calls should use HTTPS
- Never send tokens over HTTP
- Configure SSL/TLS properly

### 4. Monitor Admin Actions

```bash
# Check logs for admin activity
docker logs careconnect-backend | grep admin_id
```

### 5. Limit Admin Accounts

- Only create necessary admin accounts
- Use staff role for limited access
- Regular audit of admin users

---

## Quick Reference

### Common Endpoints

```
POST   /api/v1/admin/doctors                    Create doctor
GET    /api/v1/admin/doctors                    List doctors
PUT    /api/v1/admin/doctors/{id}               Update doctor
DELETE /api/v1/admin/doctors/{id}               Delete doctor
POST   /api/v1/admin/doctors/{id}/upload-profile Upload PDF

GET    /api/v1/admin/appointments               List appointments
POST   /api/v1/admin/appointments               Create appointment
PUT    /api/v1/admin/appointments/{id}          Update appointment
DELETE /api/v1/admin/appointments/{id}          Delete appointment
PATCH  /api/v1/admin/appointments/{id}/status   Update status

GET    /api/v1/admin/doctors/{id}/schedule      View schedule
POST   /api/v1/admin/doctors/{id}/block-time    Block time
PUT    /api/v1/admin/doctors/{id}/availability  Update calendar

GET    /api/v1/admin/stats/overview             System stats
```

### Getting Help

- **API Docs:** http://localhost:8000/docs
- **Admin API Guide:** `docs/ADMIN_API.md`
- **Test Script:** `scripts/test_admin_api.py`
- **Logs:** `docker logs careconnect-backend`

---

**Ready to start?** Test the system with:
```bash
docker exec careconnect-backend python scripts/test_admin_api.py
```
