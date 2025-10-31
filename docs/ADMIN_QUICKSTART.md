# Quick Start: Admin Features

## 🚀 Get Started in 5 Minutes

### Step 1: Start the System

```bash
cd CareConnect
docker-compose up -d
```

Wait for initialization (~30 seconds)

### Step 2: Get Admin Token

```bash
# Login as admin
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@careconnect.health",
    "password": "admin123"
  }' | jq -r '.access_token'
```

Save the token as `TOKEN` variable:
```bash
export TOKEN="eyJhbGc..."
```

### Step 3: Test Admin Features

#### View System Stats
```bash
curl http://localhost:8000/api/v1/admin/stats/overview \
  -H "Authorization: Bearer $TOKEN" | jq
```

#### List All Doctors
```bash
curl http://localhost:8000/api/v1/admin/doctors \
  -H "Authorization: Bearer $TOKEN" | jq
```

#### Create a New Doctor
```bash
curl -X POST http://localhost:8000/api/v1/admin/doctors \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr. Test Doctor",
    "department": "Cardiology",
    "type": "physician",
    "specialty": "Interventional Cardiology",
    "bio": "Expert cardiologist"
  }' | jq
```

Save the doctor ID:
```bash
DOCTOR_ID=$(curl -s ... | jq -r '.id')
```

#### Upload Doctor Profile PDF
```bash
# Use one of the existing doctor PDFs
curl -X POST http://localhost:8000/api/v1/admin/doctors/$DOCTOR_ID/upload-profile \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@backend/data/doctor_pdfs/sarah_johnson.pdf" | jq
```

#### View Appointments
```bash
curl http://localhost:8000/api/v1/admin/appointments \
  -H "Authorization: Bearer $TOKEN" | jq
```

#### View Doctor Schedule
```bash
curl "http://localhost:8000/api/v1/admin/doctors/$DOCTOR_ID/schedule?date_from=2025-11-01&date_to=2025-11-30" \
  -H "Authorization: Bearer $TOKEN" | jq
```

### Step 4: Run Automated Tests

```bash
docker exec careconnect-backend python scripts/test_admin_api.py
```

Expected output:
```
============================================================
Admin API Test Suite
============================================================

1. Authenticating as admin...
   ✓ Admin authenticated

2. Fetching system statistics...
   ✓ Total doctors: 5
   ✓ Total appointments: 10
   ...

============================================================
✓ Admin API Test Suite Completed!
============================================================
```

### Step 5: Explore Interactive Docs

1. Open browser: http://localhost:8000/docs
2. Click "Authorize" button
3. Enter: `Bearer YOUR_TOKEN`
4. Navigate to "Admin" section
5. Try any endpoint!

## 🎯 Common Tasks

### Create & Upload Doctor Profile

```bash
# 1. Create doctor
DOCTOR=$(curl -s -X POST http://localhost:8000/api/v1/admin/doctors \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr. Jane Smith",
    "department": "Neurology",
    "type": "physician",
    "specialty": "Pediatric Neurology"
  }')

DOCTOR_ID=$(echo $DOCTOR | jq -r '.id')
echo "Created doctor with ID: $DOCTOR_ID"

# 2. Upload profile
curl -X POST http://localhost:8000/api/v1/admin/doctors/$DOCTOR_ID/upload-profile \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@path/to/profile.pdf"

# 3. Verify it's searchable
curl -X POST http://localhost:8000/api/v1/rag/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "query": "pediatric neurologist",
    "top_k": 5
  }' | jq
```

### Manage Appointments

```bash
# Get all pending appointments
curl "http://localhost:8000/api/v1/admin/appointments?status=pending" \
  -H "Authorization: Bearer $TOKEN" | jq

# Confirm an appointment
curl -X PATCH "http://localhost:8000/api/v1/admin/appointments/123/status?status=confirmed" \
  -H "Authorization: Bearer $TOKEN" | jq

# Filter by date range
TODAY=$(date +%Y-%m-%d)
NEXT_WEEK=$(date -d "+7 days" +%Y-%m-%d)

curl "http://localhost:8000/api/v1/admin/appointments?date_from=$TODAY&date_to=$NEXT_WEEK" \
  -H "Authorization: Bearer $TOKEN" | jq
```

### Block Doctor Time

```bash
# Block next week for vacation
curl -X POST http://localhost:8000/api/v1/admin/doctors/5/block-time \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "time_start": "2025-11-10T00:00:00Z",
    "time_end": "2025-11-17T23:59:59Z",
    "reason": "Vacation"
  }' | jq
```

## 📚 Documentation

- **API Reference:** [ADMIN_API.md](./ADMIN_API.md)
- **User Guide:** [ADMIN_GUIDE.md](./ADMIN_GUIDE.md)
- **Implementation:** [ADMIN_IMPLEMENTATION.md](./ADMIN_IMPLEMENTATION.md)
- **Interactive Docs:** http://localhost:8000/docs

## 🐛 Troubleshooting

### "Could not validate credentials"

```bash
# Re-login to get fresh token
export TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@careconnect.health", "password": "admin123"}' \
  | jq -r '.access_token')
```

### "Admin access required"

Make sure you're using admin credentials:
- Email: `admin@careconnect.health`
- Password: `admin123`

### Docker not running

```bash
docker-compose up -d
docker ps  # Verify containers are running
```

## ✅ Verification Checklist

- [ ] System is running (`docker ps`)
- [ ] Can login as admin
- [ ] Can view statistics
- [ ] Can create doctor
- [ ] Can upload PDF
- [ ] Can view appointments
- [ ] Can view schedule
- [ ] Test suite passes

## 🎉 Success!

You now have full admin capabilities including:
- ✅ Doctor management (CRUD)
- ✅ Appointment management
- ✅ Schedule management
- ✅ PDF upload with RAG integration
- ✅ Statistics and reporting

**Next Steps:**
1. Explore the interactive docs
2. Test with real data
3. Integrate with frontend
4. Review security settings for production
