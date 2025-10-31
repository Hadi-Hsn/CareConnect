# CareConnect Setup - Quick Start

## What is this?

The `setup/` directory contains all the scripts and configuration needed to initialize your CareConnect database with demo data, generate sample PDFs, and set up the RAG system.

## First Time Setup

Just run:

```bash
docker-compose up --build
```

That's it! The setup will automatically:
1. ✅ Create the database schema
2. ✅ Add demo users and providers
3. ✅ Generate doctor profile PDFs
4. ✅ Index everything into RAG
5. ✅ Start the application

## What You Get

### Demo Accounts
- **Patient**: `patient@careconnect.health` / `password123`
- **Admin**: `admin@careconnect.health` / `admin123`

### Sample Data
- 5 doctors/providers
- 5 lab tests
- 5 facility information documents
- 5 detailed doctor profile PDFs

### RAG System
All documents are automatically embedded and indexed for AI-powered retrieval.

## Resetting Everything

Want to start fresh?

```bash
# Stop and remove all data
docker-compose down -v

# Start fresh (setup runs automatically)
docker-compose up --build
```

## Re-running Setup Only

```bash
# Stop services
docker-compose down

# Run just setup
docker-compose up setup

# Start the rest
docker-compose up -d backend frontend
```

## Troubleshooting

### Setup fails with "Database connection error"
**Solution**: Wait a few seconds and try again. The database might still be starting.

### Setup fails with "OpenAI API error"
**Solution**: Make sure `OPENAI_API_KEY` is set in your `backend/.env` file.

### I don't see any PDFs
**Solution**: Check the setup logs: `docker-compose logs setup`

### Backend won't start
**Solution**: Make sure setup completed successfully. Check: `docker-compose ps setup`

## Manual Commands

If you need to run individual steps:

```bash
# Seed demo data only
docker-compose exec backend python -c "
import sys
sys.path.append('/app/backend')
from setup.scripts.seed_demo_data import main
import asyncio
asyncio.run(main())
"

# Generate PDFs only
docker-compose run --rm setup python scripts/generate_doctor_pdfs.py

# Index PDFs only
docker-compose run --rm setup python scripts/index_pdfs.py
```

## For Developers

See the full [Setup README](README.md) for:
- Detailed architecture
- Adding custom demo data
- Modifying PDF generation
- Customizing RAG indexing
- Production deployment

## Need Help?

1. Check logs: `docker-compose logs setup`
2. Verify environment: `docker-compose config`
3. See full docs: [Setup README](README.md)

---

**Happy developing! 🚀**
