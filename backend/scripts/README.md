# CareConnect Database Population Scripts

## Overview

This directory contains scripts for populating the CareConnect database with demo data for testing and demonstration purposes.

## Scripts

### `populate_demo_database.py`

Comprehensive database population script that creates a full demo environment.

**What it does:**
- Ensures admin user exists with credentials: `admin@aub.com` / `Admin@123`
- Clears existing demo data (preserves admin account)
- Creates 30 patient accounts with realistic names, emails, and phone numbers
- Creates 3+ providers (doctors) per department across all specialties
- Creates 22 comprehensive lab tests across multiple departments
- Generates diverse appointments:
  - Past, present, and future dates
  - Various statuses (completed, confirmed, pending, cancelled)
  - Different channels (web, phone, agent)
  - Realistic appointment reasons per department
- Indexes facility documents and doctor profiles for RAG/AI search

**Usage:**

Run directly from command line:
```bash
cd backend
python scripts/populate_demo_database.py
```

Or trigger via Admin Portal:
1. Log in as admin (admin@aub.com / Admin@123)
2. Navigate to Admin Dashboard
3. Click "Populate Database" button
4. Confirm the action

**Sample Data Created:**

**Patients (30):**
- Emma Johnson (emma.johnson@patient.com)
- Liam Smith (liam.smith@patient.com)
- Olivia Brown (olivia.brown@patient.com)
- ... and 27 more
- All patients have password: `patient123`

**Providers (90+):**
- 3+ doctors per department including:
  - Cardiology
  - Dermatology
  - Emergency Medicine
  - Endocrinology
  - Gastroenterology
  - Internal Medicine
  - Neurology
  - Oncology
  - Orthopedics
  - Pediatrics
  - Psychiatry
  - And many more...

**Lab Tests (22):**
- Complete Blood Count (CBC)
- Lipid Panel
- Thyroid Function Test
- Hemoglobin A1C
- Comprehensive Metabolic Panel
- Liver Function Test
- X-Ray
- MRI Scan
- CT Scan
- And more...

**Appointments:**
- 2-5 appointments per patient
- Distributed across 60 days in the past to 30 days in the future
- Realistic appointment reasons based on department
- Various statuses reflecting appointment lifecycle

## Admin Credentials

After running any population script, you can always log in as admin:
- **Email:** admin@aub.com
- **Password:** Admin@123

## Notes

⚠️ **WARNING**: The `populate_demo_database.py` script will delete all existing patients, providers, appointments, and lab tests. The admin account is preserved.

💡 **TIP**: Use this script when:
- Setting up a new demo environment
- Testing the system with realistic data
- Resetting the database to a known state
- Preparing for a product demonstration

## Development

To modify the demo data:
1. Edit `populate_demo_database.py`
2. Update the data constants (PATIENT_NAMES, APPOINTMENT_REASONS, etc.)
3. Modify the seed functions to adjust data generation logic
4. Test by running the script locally

## Dependencies

The script uses the existing app models and services:
- `app.models.*` - Database models
- `app.core.security` - Password hashing
- `app.services.rag_service` - Document indexing
- `app.core.db` - Database session management

No additional dependencies required beyond the main application.
