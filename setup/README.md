# CareConnect Setup

This directory contains all the initialization scripts and configuration needed to populate the CareConnect database with demo data, generate sample PDFs, and initialize the RAG system.

## Overview

The setup process is separated from the core application to:
- Keep the backend container startup fast and clean
- Allow independent execution of data population
- Enable easy database reset and re-initialization
- Separate one-time setup from runtime concerns

## Structure

```
setup/
├── Dockerfile              # Setup container configuration
├── run_setup.sh           # Master setup orchestration script
├── scripts/
│   ├── seed_demo_data.py  # Seed users, providers, lab tests, and facility docs
│   ├── generate_doctor_pdfs.py  # Generate 5 doctor profile PDFs
│   └── index_pdfs.py      # Parse and index PDFs into RAG system
└── README.md              # This file
```

## What Gets Created

### 1. Database Records
- **Users** (2):
  - Patient: `hadihacan@gmail.com` / `password123`
  - Admin: `hadi.wmail@gmail.com` / `admin123`

- **Providers** (5):
  - Dr. Sara Haddad (Cardiology)
  - Dr. Omar Nassar (Radiology)
  - Dr. Maria Rodriguez (Primary Care)
  - Dr. James Chen (Orthopedics)
  - Sarah Johnson (Nurse Practitioner)

- **Lab Tests** (5):
  - Complete Blood Count (CBC)
  - Lipid Panel
  - Thyroid Function Test
  - Hemoglobin A1C
  - Comprehensive Metabolic Panel

### 2. RAG Documents (Facility Information)
- Parking Guide
- Department Hours
- Lab Test Preparation
- Facility Directions
- Patient Check-in FAQs

### 3. Doctor Profile PDFs (5)
Detailed professional profiles generated as PDFs:
- Dr. Sarah Johnson (Cardiology)
- Dr. Michael Chen (Orthopedic Surgery)
- Dr. Emily Rodriguez (Pediatrics)
- Dr. James Williams (Internal Medicine)
- Dr. Lisa Patel (Dermatology)

Each PDF includes:
- Credentials and experience
- Education and training
- Specialty areas
- Office hours and insurance
- Awards and recognition

### 4. RAG Vector Store
All facility documents and doctor PDFs are parsed, chunked, embedded, and indexed into the FAISS vector store for retrieval-augmented generation.

## How It Works

### Docker Compose Integration

The setup runs as a separate service in `docker-compose.yml`:

```yaml
setup:
  build:
    context: .
    dockerfile: setup/Dockerfile
  depends_on:
    db:
      condition: service_healthy
```

The backend depends on setup completion:

```yaml
backend:
  depends_on:
    setup:
      condition: service_completed_successfully
```

### Execution Flow

1. **Wait for Database**: Ensures PostgreSQL is ready
2. **Run Migrations**: Applies all Alembic migrations
3. **Seed Demo Data**: Creates users, providers, lab tests, and facility documents
4. **Generate PDFs**: Creates doctor profile PDFs
5. **Index PDFs**: Parses and indexes all PDFs into RAG system

## Usage

### Full System Startup (Recommended)

Start everything including setup:

```bash
docker-compose up --build
```

The setup container will:
- Run once during initial startup
- Populate all data
- Exit with success
- Allow backend to start

### Run Setup Only

To re-run just the setup (e.g., to reset data):

```bash
# Stop all services
docker-compose down

# Remove volumes to clear data (optional)
docker-compose down -v

# Start just the database
docker-compose up -d db

# Run setup
docker-compose up setup

# Start remaining services
docker-compose up -d backend frontend
```

### Skip Setup (Use Existing Data)

If data is already populated, just start backend and frontend:

```bash
docker-compose up backend frontend
```

## Manual Execution

You can run individual setup scripts manually:

### 1. Seed Demo Data

```bash
docker-compose exec backend python scripts/seed_demo_data.py
```

### 2. Generate Doctor PDFs

```bash
docker-compose exec backend python scripts/generate_doctor_pdfs.py
```

### 3. Index PDFs

```bash
docker-compose exec backend python scripts/index_pdfs.py
```

## Environment Variables

Setup uses the following environment variables (configured in `docker-compose.yml`):

- `DATABASE_URL`: PostgreSQL connection string
- `VECTOR_STORE_PATH`: Path to FAISS index directory
- `OPENAI_API_KEY`: OpenAI API key for embeddings
- `OPENAI_EMBEDDING_MODEL`: Model for embeddings (default: text-embedding-3-large)
- `OPENAI_EMBEDDING_DIMENSIONS`: Embedding dimensions (default: 3072)

## Shared Volumes

Setup shares volumes with backend:

- `vector_data`: FAISS vector store index
- `pdf_data`: Generated doctor PDFs

## Troubleshooting

### Setup Fails with "Database not found"

Ensure the database service is healthy:

```bash
docker-compose ps db
```

If unhealthy, check logs:

```bash
docker-compose logs db
```

### Setup Fails with "OpenAI API Error"

Ensure `OPENAI_API_KEY` is set in your `.env` file or environment.

### PDFs Not Generated

Check if the output directory exists and has proper permissions:

```bash
docker-compose exec setup ls -la /app/data/doctor_pdfs/
```

### RAG Indexing Fails

Check backend logs for detailed error messages:

```bash
docker-compose logs backend
```

Verify vector store directory:

```bash
docker-compose exec backend ls -la /data/faiss_index/
```

## Resetting Data

To completely reset and re-initialize:

```bash
# Stop and remove all containers and volumes
docker-compose down -v

# Rebuild and start fresh
docker-compose up --build
```

This will:
- Delete all database data
- Clear vector store
- Remove generated PDFs
- Re-run complete setup

## Development

### Adding New Demo Data

1. Edit `scripts/seed_demo_data.py`
2. Add new seed functions
3. Call them from `main()`
4. Rebuild setup: `docker-compose build setup`

### Adding New Doctor PDFs

1. Edit `scripts/generate_doctor_pdfs.py`
2. Add entries to `DOCTORS_DATA`
3. Rebuild setup: `docker-compose build setup`

### Modifying Indexing

1. Edit `scripts/index_pdfs.py`
2. Adjust chunking, parsing, or indexing logic
3. Rebuild setup: `docker-compose build setup`

## Production Considerations

For production deployments:

1. **Don't Auto-Run Setup**: Remove setup dependency from backend
2. **Use Init Containers**: In Kubernetes, use init containers
3. **Manual Execution**: Run setup as a one-time job
4. **Persistent Volumes**: Ensure vector store and PDFs persist
5. **Real Data**: Replace demo data with production data sources

## Architecture Benefits

Separating setup provides:

✅ **Clean Separation**: Runtime vs initialization concerns  
✅ **Fast Startup**: Backend starts immediately after migrations  
✅ **Independent Control**: Run setup on-demand  
✅ **Easy Testing**: Reset and re-populate data easily  
✅ **Clear Dependencies**: Explicit service dependencies  
✅ **Better Debugging**: Isolated logs for setup issues

## Related Documentation

- [API Contract](../docs/API_CONTRACT.md) - API endpoints and schemas
- [Admin Guide](../docs/ADMIN_GUIDE.md) - Admin functionality
- [RAG Documentation](../docs/ARCHITECTURE.md) - RAG system architecture
- [Main README](../README.md) - Project overview

## Support

For issues or questions:
1. Check logs: `docker-compose logs setup`
2. Verify environment variables
3. Ensure database is healthy
4. Check volume mounts and permissions
