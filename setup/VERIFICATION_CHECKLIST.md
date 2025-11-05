# CareConnect Setup - Verification Checklist

Use this checklist to verify the setup was successful.

## Pre-Flight Checks

- [ ] Docker and Docker Compose installed
- [ ] OpenAI API key configured in `backend/.env`
- [ ] Sufficient disk space (at least 2GB free)
- [ ] Port 5432 (PostgreSQL), 8000 (Backend), 5173 (Frontend) available

## Build and Start

```bash
cd CareConnect
docker-compose up --build
```

## Verification Steps

### 1. Setup Container

**Check logs:**
```bash
docker-compose logs setup
```

**Expected output should include:**
- [ ] ✅ Database is ready!
- [ ] ✅ Migrations completed!
- [ ] ✅ Seeded 2 users
- [ ] ✅ Seeded 5 providers
- [ ] ✅ Seeded 5 lab tests
- [ ] ✅ Indexed 5 documents (facility info)
- [ ] ✅ Successfully generated 5 doctor PDFs!
- [ ] ✅ PDF indexing completed!
- [ ] ✅ Setup completed successfully!

**Check container status:**
```bash
docker-compose ps setup
```

- [ ] Status should be "Exit 0" (success)

### 2. Database

**Connect to database:**
```bash
docker-compose exec db psql -U careconnect -d careconnect
```

**Verify tables:**
```sql
\dt
```

- [ ] Tables exist: users, providers, lab_tests, appointments, booking_events

**Verify data:**
```sql
SELECT email FROM users;
SELECT name FROM providers;
SELECT name FROM lab_tests;
\q
```

- [ ] 2 users: hadihacan@gmail.com, hadi.wmail@gmail.com
- [ ] 5 providers listed
- [ ] 5 lab tests listed

### 3. Generated PDFs

**Check PDFs exist:**
```bash
docker-compose exec backend ls -la /data/doctor_pdfs/
```

**Expected files:**
- [ ] sarah_johnson.pdf
- [ ] michael_chen.pdf
- [ ] emily_rodriguez.pdf
- [ ] james_williams.pdf
- [ ] lisa_patel.pdf

**Verify file sizes:**
```bash
docker-compose exec backend du -h /data/doctor_pdfs/*.pdf
```

- [ ] Each PDF should be 10-50KB (reasonable size)

### 4. Vector Store

**Check FAISS index:**
```bash
docker-compose exec backend ls -la /data/faiss_index/
```

**Expected files:**
- [ ] index.faiss (binary index file)
- [ ] index.pkl (metadata pickle file)

**Check file sizes:**
```bash
docker-compose exec backend du -h /data/faiss_index/*
```

- [ ] Files should have non-zero size

### 5. Backend Container

**Check backend is running:**
```bash
docker-compose ps backend
```

- [ ] Status: "Up"
- [ ] Ports: 0.0.0.0:8000->8000/tcp

**Check backend logs:**
```bash
docker-compose logs backend | tail -20
```

- [ ] No error messages
- [ ] "Application startup complete" visible

**Test health endpoint:**
```bash
curl http://localhost:8000/api/v1/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "environment": "development",
  ...
}
```

- [ ] Status 200 OK
- [ ] Response includes database and vector store status

### 6. Frontend Container

**Check frontend is running:**
```bash
docker-compose ps frontend
```

- [ ] Status: "Up"
- [ ] Ports: 0.0.0.0:5173->5173/tcp

**Open browser:**
```
http://localhost:5173
```

- [ ] Login page loads
- [ ] No console errors
- [ ] UI renders correctly

### 7. Authentication

**Test patient login:**
#### Test Login (Patient)
- Email: `hadihacan@gmail.com`
- Password: `password123`

- [ ] Login successful
- [ ] Redirects to chat page
- [ ] Chat interface loads

**Test admin login:**
- Email: `hadi.wmail@gmail.com`
- Password: `admin123`

- [ ] Login successful
- [ ] Admin menu visible
- [ ] Can access admin panel

### 8. RAG System

**Test RAG query in chat:**

Type in chat:
```
What are the parking options at the facility?
```

**Expected response should mention:**
- [ ] North Lot (24/7, $5/day)
- [ ] South Lot (Free, 6 AM - 10 PM)
- [ ] Valet Service ($10/day)

**Test doctor profile query:**

Type in chat:
```
Tell me about Dr. Sarah Johnson
```

**Expected response should mention:**
- [ ] Cardiologist
- [ ] Harvard Medical School
- [ ] 15+ years experience
- [ ] Specialties (should list some)

### 9. API Documentation

**Open API docs:**
```
http://localhost:8000/docs
```

- [ ] Swagger UI loads
- [ ] All endpoints visible
- [ ] Can expand and view schemas

**Test an endpoint:**
1. Navigate to GET `/api/v1/providers`
2. Click "Try it out"
3. Click "Execute"

- [ ] 200 response
- [ ] Returns list of 5 providers

### 10. Admin Functions

**In Admin Panel, verify:**

**Providers:**
- [ ] Can view list of providers
- [ ] 5 providers displayed
- [ ] Each has name, specialty, department

**Appointments:**
- [ ] Can view appointments list
- [ ] Can filter and search

**Lab Tests:**
- [ ] Can view lab tests
- [ ] 5 tests displayed

**Statistics:**
- [ ] Overview shows counts
- [ ] Metrics displayed

### 11. Appointment Booking

**Test booking flow in chat:**

Type:
```
I need to book an appointment with a cardiologist
```

**Follow the conversation:**

- [ ] Agent asks for date preference
- [ ] Provides available time slots
- [ ] Can complete booking
- [ ] Confirmation shown

### 12. Volume Persistence

**Test data persistence:**

1. Stop containers:
```bash
docker-compose stop
```

2. Start again:
```bash
docker-compose start backend frontend
```

3. Verify:
- [ ] Can login (data persists)
- [ ] Providers still exist
- [ ] PDFs still accessible
- [ ] RAG queries still work

### 13. Reset Test

**Test complete reset:**

1. Stop and remove volumes:
```bash
docker-compose down -v
```

2. Start fresh:
```bash
docker-compose up --build
```

- [ ] Setup runs again
- [ ] All data recreated
- [ ] System functional

## Troubleshooting

### Setup fails

**Check:**
1. Docker daemon running: `docker ps`
2. Sufficient disk space: `df -h`
3. Network connectivity: `docker-compose logs db`
4. Environment variables: `docker-compose config`

### Backend fails to start

**Check:**
1. Setup completed: `docker-compose ps setup` (Exit 0)
2. Database healthy: `docker-compose ps db`
3. Volumes mounted: `docker volume ls`
4. Backend logs: `docker-compose logs backend`

### RAG not working

**Check:**
1. OPENAI_API_KEY set: `docker-compose config | grep OPENAI_API_KEY`
2. Vector store exists: `docker-compose exec backend ls /data/faiss_index/`
3. PDFs exist: `docker-compose exec backend ls /data/doctor_pdfs/`
4. Backend logs for errors

### Login fails

**Check:**
1. Database has users: `docker-compose exec db psql -U careconnect -d careconnect -c "SELECT email FROM users;"`
2. Backend logs for auth errors
3. JWT_SECRET configured
4. CORS settings correct

## Success Criteria

All checkboxes above should be checked ✅

**If all checks pass:**
- 🎉 Setup is successful!
- 🚀 CareConnect is ready to use
- 📚 Share feedback or start developing

**If any checks fail:**
- 📋 Review troubleshooting section
- 📝 Check logs for specific errors
- 🔍 Consult README.md or ARCHITECTURE.md
- 💬 Open an issue with details

## Quick Reference

**Useful commands:**
```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f setup
docker-compose logs -f backend

# Restart a service
docker-compose restart backend

# Rebuild everything
docker-compose up --build --force-recreate

# Clean slate
docker-compose down -v && docker-compose up --build
```

---

**Verification Date:** _______________  
**Verified By:** _______________  
**Result:** ☐ Pass  ☐ Fail  
**Notes:** _______________________________________________
