# Backend Scripts

This directory contains utility scripts for managing the CareConnect backend.

## Available Scripts

### 📊 Database & Data Management

#### `seed_demo_data.py`
Seeds the database with demo data for development and testing.

```bash
python scripts/seed_demo_data.py
```

**Creates:**
- Demo users (patient, admin)
- Sample providers
- Demo appointments
- Lab results

---

### 📄 RAG System Scripts

#### `generate_doctor_pdfs.py`
Generates sample doctor profile PDFs.

```bash
python scripts/generate_doctor_pdfs.py
```

**Output:** `data/doctor_pdfs/*.pdf` (5 sample doctors)

**Doctors Generated:**
- Dr. Sarah Johnson (Cardiology)
- Dr. Michael Chen (Orthopedic Surgery)
- Dr. Emily Rodriguez (Pediatrics)
- Dr. James Williams (Internal Medicine)
- Dr. Lisa Patel (Dermatology)

---

#### `index_pdfs.py`
Indexes PDF documents into the RAG vector store.

```bash
# Index PDFs from default directory
python scripts/index_pdfs.py

# Index from custom directory
python scripts/index_pdfs.py --pdf-dir /path/to/pdfs

# Replace existing index
python scripts/index_pdfs.py --replace
```

**What it does:**
1. Finds all PDF files in directory
2. Extracts text using pypdf
3. Creates document chunks
4. Generates embeddings
5. Stores in FAISS index

---

#### `init_rag.py`
Initializes RAG system on startup (auto-run by Docker).

```bash
python scripts/init_rag.py
```

**Behavior:**
- Checks if RAG already initialized
- Auto-indexes PDFs if found
- Graceful error handling
- Doesn't block service startup

---

#### `test_rag.py`
Tests RAG system with sample queries.

```bash
python scripts/test_rag.py
```

**Tests:**
- Vector store connectivity
- Semantic search quality
- Response times
- Result relevance

**Example Output:**
```
Testing RAG System
==================
✓ Total vectors: 125
✓ Unique documents: 5

Query: "cardiologist with heart failure experience"
✓ Found 3 results in 45.2ms
  1. Dr. Sarah Johnson (score: 0.87)
  2. Dr. James Williams (score: 0.65)
  ...
```

---

#### `validate_rag.py`
Validates RAG system configuration and health.

```bash
python scripts/validate_rag.py
```

**Checks:**
- Environment variables (OPENAI_API_KEY)
- Directory structure
- PDF files existence
- Vector store status
- RAG system operational

**Exit codes:**
- `0` - All checks passed
- `1` - Validation failed

---

### 📧 Email Testing

#### `test_sendgrid.py`
Tests SendGrid email integration.

```bash
python scripts/test_sendgrid.py
```

**Requirements:**
- `SENDGRID_API_KEY` in environment
- Valid sender email configured

---

## Common Workflows

### First Time Setup

```bash
# 1. Run migrations
alembic upgrade head

# 2. Seed demo data
python scripts/seed_demo_data.py

# 3. Generate doctor PDFs
python scripts/generate_doctor_pdfs.py

# 4. Index PDFs into RAG
python scripts/index_pdfs.py

# 5. Validate everything
python scripts/validate_rag.py
```

### Docker Automatic Setup

When using `docker-compose up`, these scripts run automatically:

```bash
# Startup sequence in docker-compose.yml
alembic upgrade head &&
python scripts/seed_demo_data.py &&
python scripts/generate_doctor_pdfs.py &&
python scripts/init_rag.py &&
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Reset RAG System

```bash
# 1. Delete existing index
rm -rf /data/faiss_index/*

# 2. Regenerate PDFs (optional)
python scripts/generate_doctor_pdfs.py

# 3. Re-index
python scripts/index_pdfs.py --replace
```

### Add New Doctor

```bash
# Option 1: Edit generate_doctor_pdfs.py
# Add to DOCTORS_DATA list, then:
python scripts/generate_doctor_pdfs.py
python scripts/index_pdfs.py

# Option 2: Use API
curl -X POST http://localhost:8000/api/v1/files/upload-pdf \
  -F "file=@new_doctor.pdf"
```

---

## Script Dependencies

All scripts require:
- Python 3.11+
- Installed dependencies: `pip install -e ".[dev]"`
- Proper environment variables (`.env` file)

### Required Environment Variables

```bash
# For RAG scripts
OPENAI_API_KEY=sk-...
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
OPENAI_EMBEDDING_DIMENSIONS=3072
VECTOR_STORE_PATH=./data/faiss_index

# For email script
SENDGRID_API_KEY=SG...
EMAIL_FROM=your-email@domain.com
```

---

## Troubleshooting

### "Module not found" error

```bash
# Make sure you're in the backend directory
cd backend

# Install dependencies
pip install -e ".[dev]"
```

### "OpenAI API key not found"

```bash
# Check .env file exists
cat .env | grep OPENAI_API_KEY

# Or set manually
export OPENAI_API_KEY=sk-your-key-here
```

### "Permission denied" error

```bash
# Ensure data directories exist and are writable
mkdir -p data/doctor_pdfs data/faiss_index
chmod -R 755 data/
```

### RAG indexing fails

```bash
# Check PDFs exist
ls -lh data/doctor_pdfs/

# Validate environment
python scripts/validate_rag.py

# Check logs
python scripts/index_pdfs.py 2>&1 | tee index.log
```

---

## Development Tips

### Running in Development Mode

```bash
# Use uvicorn directly for hot reload
uvicorn app.main:app --reload

# In another terminal, run scripts as needed
python scripts/seed_demo_data.py
python scripts/test_rag.py
```

### Testing Script Changes

```bash
# Test individual script
python scripts/your_script.py

# Test with verbose output
LOG_LEVEL=DEBUG python scripts/your_script.py
```

### Adding New Scripts

1. Create script in `scripts/` directory
2. Add shebang and imports:
   ```python
   #!/usr/bin/env python3
   import sys
   from pathlib import Path
   sys.path.insert(0, str(Path(__file__).parent.parent))
   ```
3. Use async if needed: `asyncio.run(main())`
4. Add proper error handling
5. Document in this README

---

## Related Documentation

- [RAG System Documentation](../../docs/RAG_SYSTEM.md)
- [RAG Quick Start Guide](../../docs/RAG_QUICKSTART.md)
- [Main README](../../README.md)

---

**Need help?** Check the logs or run validation scripts to diagnose issues.
