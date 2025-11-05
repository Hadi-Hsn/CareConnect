# Admin API Documentation

## Overview

The Admin API provides comprehensive management capabilities for doctors, appointments, schedules, and system administration. All endpoints require admin authentication.

## Authentication

All admin endpoints require:
1. Valid JWT token in Authorization header
2. User must have `admin` role

```bash
# Login as admin
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "hadi.wmail@gmail.com",
    "password": "admin123"
  }'

# Use the access_token in subsequent requests
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  http://localhost:8000/api/v1/admin/stats/overview
```

## API Endpoints

### Doctor Management

#### Create Doctor

```http
POST /api/v1/admin/doctors
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Dr. Jane Smith",
  "department": "Cardiology",
  "type": "physician",
  "specialty": "Interventional Cardiology",
  "bio": "Board-certified cardiologist with 10 years of experience...",
  "availability_calendar_id": "cal_12345"
}
```

**Response:**
```json
{
  "id": 10,
  "name": "Dr. Jane Smith",
  "department": "Cardiology",
  "type": "physician",
  "specialty": "Interventional Cardiology",
  "bio": "Board-certified cardiologist...",
  "availability_calendar_id": "cal_12345",
  "created_at": "2025-10-31T10:30:00Z"
}
```

#### List All Doctors

```http
GET /api/v1/admin/doctors?skip=0&limit=100&department=Cardiology
Authorization: Bearer {token}
```

**Query Parameters:**
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Max records to return (default: 100, max: 500)
- `department` (string): Filter by department
- `specialty` (string): Filter by specialty

#### Get Doctor Details

```http
GET /api/v1/admin/doctors/{doctor_id}
Authorization: Bearer {token}
```

#### Update Doctor

```http
PUT /api/v1/admin/doctors/{doctor_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Dr. Jane Smith-Johnson",
  "specialty": "Interventional & Preventive Cardiology",
  "bio": "Updated bio..."
}
```

**Note:** All fields are optional. Only provided fields will be updated.

#### Delete Doctor

```http
DELETE /api/v1/admin/doctors/{doctor_id}
Authorization: Bearer {token}
```

⚠️ **Warning:** This will also cancel all future appointments for this doctor.

#### Upload Doctor Profile PDF

```http
POST /api/v1/admin/doctors/{doctor_id}/upload-profile
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: [PDF file]
```

**What it does:**
1. Validates the PDF file
2. Extracts text content
3. Creates embeddings using OpenAI
4. Indexes into RAG system
5. Makes the profile searchable

**Response:**
```json
{
  "indexed_count": 1,
  "total_chunks": 8,
  "message": "Successfully indexed 1 documents (8 chunks)"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/v1/admin/doctors/5/upload-profile \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@dr_jane_smith_profile.pdf"
```

---

### Appointment Management

#### List All Appointments

```http
GET /api/v1/admin/appointments
Authorization: Bearer {token}
```

**Query Parameters:**
- `user_id` (int): Filter by patient
- `provider_id` (int): Filter by doctor
- `status` (string): Filter by status (pending, confirmed, cancelled, completed, no_show)
- `date_from` (date): Start date filter (YYYY-MM-DD)
- `date_to` (date): End date filter (YYYY-MM-DD)
- `skip` (int): Pagination offset
- `limit` (int): Max records (default: 100, max: 500)

**Example:**
```bash
# Get all confirmed appointments for next week
curl -X GET "http://localhost:8000/api/v1/admin/appointments?status=confirmed&date_from=2025-11-01&date_to=2025-11-07" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
[
  {
    "id": 45,
    "user_id": 12,
    "provider_id": 5,
    "time_start": "2025-11-03T10:00:00Z",
    "time_end": "2025-11-03T10:30:00Z",
    "status": "confirmed",
    "channel": "agent",
    "reason": "Annual checkup",
    "notes": null,
    "user_name": "John Doe",
    "user_email": "john@example.com",
    "provider_name": "Dr. Jane Smith",
    "provider_department": "Cardiology",
    "created_at": "2025-10-28T14:20:00Z",
    "updated_at": "2025-10-28T14:20:00Z"
  }
]
```

#### Create Appointment (Admin)

```http
POST /api/v1/admin/appointments
Authorization: Bearer {token}
Content-Type: application/json

{
  "user_id": 12,
  "provider_id": 5,
  "time_start": "2025-11-03T10:00:00Z",
  "time_end": "2025-11-03T10:30:00Z",
  "reason": "Annual checkup",
  "channel": "web"
}
```

**Note:** Admin-created appointments are automatically confirmed.

#### Update Appointment

```http
PUT /api/v1/admin/appointments/{appointment_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "time_start": "2025-11-03T14:00:00Z",
  "time_end": "2025-11-03T14:30:00Z",
  "status": "confirmed",
  "notes": "Patient requested time change"
}
```

#### Delete Appointment

```http
DELETE /api/v1/admin/appointments/{appointment_id}
Authorization: Bearer {token}
```

#### Update Appointment Status

```http
PATCH /api/v1/admin/appointments/{appointment_id}/status?status=confirmed
Authorization: Bearer {token}
```

**Status options:**
- `pending`
- `confirmed`
- `cancelled`
- `completed`
- `no_show`

---

### Schedule Management

#### Get Doctor Schedule

```http
GET /api/v1/admin/doctors/{doctor_id}/schedule?date_from=2025-11-01&date_to=2025-11-07
Authorization: Bearer {token}
```

**Response:**
```json
{
  "doctor_id": 5,
  "doctor_name": "Dr. Jane Smith",
  "date_from": "2025-11-01",
  "date_to": "2025-11-07",
  "appointments": [
    {
      "id": 45,
      "user_name": "John Doe",
      "user_email": "john@example.com",
      "time_start": "2025-11-03T10:00:00Z",
      "time_end": "2025-11-03T10:30:00Z",
      "status": "confirmed",
      "reason": "Annual checkup"
    }
  ],
  "total_appointments": 1
}
```

#### Update Doctor Availability

```http
PUT /api/v1/admin/doctors/{doctor_id}/availability
Authorization: Bearer {token}
Content-Type: application/json

{
  "availability_calendar_id": "cal_new_calendar_id"
}
```

**Use case:** Link doctor with external scheduling system (Epic, Cerner, etc.)

#### Block Doctor Time

```http
POST /api/v1/admin/doctors/{doctor_id}/block-time
Authorization: Bearer {token}
Content-Type: application/json

{
  "time_start": "2025-11-05T09:00:00Z",
  "time_end": "2025-11-05T17:00:00Z",
  "reason": "Medical conference"
}
```

**What it does:** Creates a special "blocked" appointment to prevent patient bookings during specified time.

---

### Statistics & Reporting

#### Get System Overview

```http
GET /api/v1/admin/stats/overview
Authorization: Bearer {token}
```

**Response:**
```json
{
  "total_doctors": 25,
  "total_appointments": 450,
  "total_users": 180,
  "upcoming_appointments": 45,
  "appointments_by_status": {
    "pending": 12,
    "confirmed": 28,
    "cancelled": 5,
    "completed": 400,
    "no_show": 5
  }
}
```

---

## Common Workflows

### Onboard New Doctor

```bash
# 1. Create doctor
DOCTOR_RESPONSE=$(curl -X POST http://localhost:8000/api/v1/admin/doctors \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr. Robert Johnson",
    "department": "Orthopedics",
    "type": "physician",
    "specialty": "Sports Medicine",
    "bio": "Experienced orthopedic surgeon..."
  }')

DOCTOR_ID=$(echo $DOCTOR_RESPONSE | jq -r '.id')

# 2. Upload profile PDF
curl -X POST http://localhost:8000/api/v1/admin/doctors/$DOCTOR_ID/upload-profile \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@dr_robert_johnson.pdf"

# 3. Set availability calendar
curl -X PUT http://localhost:8000/api/v1/admin/doctors/$DOCTOR_ID/availability \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"availability_calendar_id": "cal_ortho_123"}'
```

### Schedule Patient Appointment

```bash
# 1. Find available doctor
curl http://localhost:8000/api/v1/admin/doctors?department=Cardiology \
  -H "Authorization: Bearer $TOKEN"

# 2. Check doctor schedule
curl "http://localhost:8000/api/v1/admin/doctors/5/schedule?date_from=2025-11-01&date_to=2025-11-07" \
  -H "Authorization: Bearer $TOKEN"

# 3. Create appointment
curl -X POST http://localhost:8000/api/v1/admin/appointments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 42,
    "provider_id": 5,
    "time_start": "2025-11-03T10:00:00Z",
    "time_end": "2025-11-03T10:30:00Z",
    "reason": "Follow-up appointment",
    "channel": "phone"
  }'
```

### Manage Doctor Schedule

```bash
# Block time for vacation
curl -X POST http://localhost:8000/api/v1/admin/doctors/5/block-time \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "time_start": "2025-12-20T00:00:00Z",
    "time_end": "2025-12-31T23:59:59Z",
    "reason": "Winter vacation"
  }'

# Reschedule conflicting appointments
curl -X PUT http://localhost:8000/api/v1/admin/appointments/123 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "time_start": "2025-11-15T14:00:00Z",
    "time_end": "2025-11-15T14:30:00Z"
  }'
```

### Bulk Operations

```bash
# Get all pending appointments
PENDING=$(curl "http://localhost:8000/api/v1/admin/appointments?status=pending&limit=500" \
  -H "Authorization: Bearer $TOKEN")

# Process each one (example: auto-confirm)
echo $PENDING | jq -r '.[].id' | while read APPT_ID; do
  curl -X PATCH "http://localhost:8000/api/v1/admin/appointments/$APPT_ID/status?status=confirmed" \
    -H "Authorization: Bearer $TOKEN"
done
```

---

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

**Solution:** Ensure valid JWT token is provided.

### 403 Forbidden
```json
{
  "detail": "Admin access required"
}
```

**Solution:** User must have admin role.

### 404 Not Found
```json
{
  "detail": "Doctor not found"
}
```

**Solution:** Verify the resource ID exists.

### 400 Bad Request
```json
{
  "detail": "Only PDF files are allowed"
}
```

**Solution:** Check request data and file types.

---

## Security Considerations

### Authorization
- All endpoints check for valid admin role
- JWT tokens expire after 24 hours
- Failed auth attempts are logged

### Audit Trail
All admin actions are logged with:
- Admin user ID
- Action type
- Timestamp
- Resource affected

### Data Protection
- PHI is masked in logs
- Sensitive data requires HTTPS in production
- Rate limiting applies (60 req/min per IP)

---

## Testing

### Test Admin Access

```bash
# Login as admin
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "hadi.wmail@gmail.com",
    "password": "admin123"
  }' | jq -r '.access_token')

# Test endpoint
curl http://localhost:8000/api/v1/admin/stats/overview \
  -H "Authorization: Bearer $TOKEN"
```

### Test Regular User (Should Fail)

```bash
# Login as patient
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "hadihacan@gmail.com",
    "password": "password123"
  }' | jq -r '.access_token')

# Should return 403 Forbidden
curl http://localhost:8000/api/v1/admin/stats/overview \
  -H "Authorization: Bearer $TOKEN"
```

---

## API Reference Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/admin/doctors` | POST | Create doctor |
| `/admin/doctors` | GET | List all doctors |
| `/admin/doctors/{id}` | GET | Get doctor details |
| `/admin/doctors/{id}` | PUT | Update doctor |
| `/admin/doctors/{id}` | DELETE | Delete doctor |
| `/admin/doctors/{id}/upload-profile` | POST | Upload doctor PDF |
| `/admin/appointments` | GET | List all appointments |
| `/admin/appointments` | POST | Create appointment |
| `/admin/appointments/{id}` | PUT | Update appointment |
| `/admin/appointments/{id}` | DELETE | Delete appointment |
| `/admin/appointments/{id}/status` | PATCH | Update status |
| `/admin/doctors/{id}/schedule` | GET | Get doctor schedule |
| `/admin/doctors/{id}/availability` | PUT | Update availability |
| `/admin/doctors/{id}/block-time` | POST | Block time slot |
| `/admin/stats/overview` | GET | System statistics |

---

For interactive API documentation, visit: http://localhost:8000/docs
