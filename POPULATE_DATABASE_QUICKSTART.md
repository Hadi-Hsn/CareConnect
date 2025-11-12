# Quick Start: Database Population

## Admin Credentials
- **Email:** `admin@aub.com`
- **Password:** `Admin@123`

## How to Populate Database

### Option 1: Admin Portal (Recommended)
1. Login at http://localhost:5173/login
2. Use admin credentials above
3. Go to Admin Dashboard
4. Click **"Populate Database"** button (top right)
5. Confirm the action
6. Wait ~10-30 seconds
7. Page reloads automatically ✅

### Option 2: Command Line
```bash
cd backend
python scripts/populate_demo_database.py
```

## What Gets Created

| Data Type | Count | Details |
|-----------|-------|---------|
| **Patients** | 30 | All with password `patient123` |
| **Providers** | 90+ | 3+ doctors per department |
| **Lab Tests** | 22 | Blood tests, imaging, etc. |
| **Appointments** | 150-300+ | Past, present, future |
| **Departments** | 25+ | All medical specialties |

## Sample Patient Login
- Email: `emma.johnson@patient.com`
- Password: `patient123`

## Sample Providers
- Dr. Sara Haddad - Cardiology
- Dr. Jennifer Wong - Dermatology  
- Dr. Maria Rodriguez - Internal Medicine
- Dr. Emily Taylor - Pediatrics
- ... and 86+ more!

## Appointment Distribution
- **Past (60 days ago):** Completed/Cancelled
- **Recent:** Various statuses
- **Future (30 days):** Confirmed/Pending

## ⚠️ Important Notes

1. **Deletes existing data** (except admin account)
2. **Run before demos** to ensure fresh, consistent data
3. **Takes 10-30 seconds** depending on system
4. **Admin account always preserved**
5. **Can be run multiple times** safely

## Troubleshooting

**Script fails?**
- Ensure database is running
- Check backend logs for errors
- Verify admin permissions

**Button not working?**
- Check browser console for errors
- Verify you're logged in as admin
- Check network tab for API errors

**Data not showing?**
- Refresh the page manually
- Clear browser cache
- Check API endpoints are working

## Quick Demo Workflow

1. **Populate** → Click "Populate Database"
2. **Wait** → ~20 seconds
3. **Demo** → Show rich appointments, provider directory
4. **Chat** → AI assistant knows all doctors
5. **Book** → Patients can book with any provider
6. **Repeat** → Can repopulate anytime for fresh demo

---

**Ready to Demo!** 🚀
