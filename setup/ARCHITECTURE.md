# CareConnect Setup Architecture

## Service Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Docker Compose Startup                       │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │    PostgreSQL DB      │
                    │  (health check wait)  │
                    └───────────┬───────────┘
                                │
                                │ DB Ready ✓
                                │
                                ▼
                    ┌───────────────────────┐
                    │    Setup Container    │
                    │                       │
                    │  1. Run Migrations    │
                    │  2. Seed Demo Data    │
                    │  3. Generate PDFs     │
                    │  4. Index to RAG      │
                    │                       │
                    │  Exits on Success ✓   │
                    └───────────┬───────────┘
                                │
                                │ Setup Complete ✓
                                │
                                ▼
                    ┌───────────────────────┐
                    │  Backend Container    │
                    │                       │
                    │  FastAPI + SQLAlchemy │
                    │  RAG Service          │
                    │  Agent System         │
                    │                       │
                    │  Port: 8000           │
                    └───────────┬───────────┘
                                │
                                │ Backend Ready ✓
                                │
                                ▼
                    ┌───────────────────────┐
                    │  Frontend Container   │
                    │                       │
                    │  React + TypeScript   │
                    │  Material UI          │
                    │                       │
                    │  Port: 5173           │
                    └───────────────────────┘
```

## Setup Container Details

```
┌──────────────────────────────────────────────────────────────┐
│                     Setup Container                           │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  📂 /app/setup/                                              │
│     ├── run_setup.sh         ← Master orchestrator          │
│     └── scripts/                                             │
│         ├── seed_demo_data.py    ← Database seeding         │
│         ├── generate_doctor_pdfs.py  ← PDF generation       │
│         └── index_pdfs.py        ← RAG indexing             │
│                                                               │
│  📂 /app/backend/                                            │
│     ├── app/                  ← Backend code (for imports)  │
│     ├── alembic/              ← Migrations                   │
│     └── alembic.ini           ← Alembic config              │
│                                                               │
│  📂 /app/data/                                               │
│     ├── doctor_pdfs/          ← Generated PDFs (shared)     │
│     └── vectorstore/          ← FAISS index (shared)        │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

## Data Flow

```
                    Setup Container
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  PostgreSQL  │  │   PDF Files  │  │ Vector Store │
│   Database   │  │              │  │    (FAISS)   │
│              │  │ /data/       │  │ /data/       │
│ - Users      │  │ doctor_pdfs/ │  │ vectorstore/ │
│ - Providers  │  │              │  │              │
│ - Lab Tests  │  │ 5 PDFs       │  │ Embeddings   │
│ - Facility   │  │              │  │ + Metadata   │
│   Docs       │  │              │  │              │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       │                 │                 │
       └─────────────────┴─────────────────┘
                         │
                         ▼
                 Backend Container
                 (Shared Volumes)
```

## Shared Volumes

```
Docker Volumes:
  vector_data  →  /data/vectorstore  (Setup + Backend)
  pdf_data     →  /data/doctor_pdfs  (Setup + Backend)
  postgres_data → /var/lib/postgresql/data (DB only)

Setup writes to:
  - /data/vectorstore/      ← FAISS index files
  - /data/doctor_pdfs/      ← Generated PDFs
  - PostgreSQL database     ← Demo records

Backend reads from:
  - /data/vectorstore/      ← RAG queries
  - /data/doctor_pdfs/      ← PDF serving
  - PostgreSQL database     ← All queries
```

## Execution Timeline

```
Time  │ Setup Container                    │ Backend Container
──────┼────────────────────────────────────┼──────────────────
0s    │ Container starts                   │ Waiting...
      │ Wait for DB (netcat check)         │
──────┼────────────────────────────────────┼──────────────────
5s    │ DB ready ✓                         │ Waiting...
      │ Run alembic migrations             │
──────┼────────────────────────────────────┼──────────────────
10s   │ Seed demo data                     │ Waiting...
      │ - 2 users created                  │
      │ - 5 providers created              │
      │ - 5 lab tests created              │
      │ - 5 facility docs indexed          │
──────┼────────────────────────────────────┼──────────────────
15s   │ Generate doctor PDFs               │ Waiting...
      │ - 5 PDFs created                   │
      │ - Saved to shared volume           │
──────┼────────────────────────────────────┼──────────────────
20s   │ Index PDFs into RAG                │ Waiting...
      │ - Parse 5 PDFs                     │
      │ - Create embeddings                │
      │ - Store in FAISS                   │
──────┼────────────────────────────────────┼──────────────────
25s   │ Setup complete! ✓                  │ Container starts
      │ Container exits (success)          │ Load app
──────┼────────────────────────────────────┼──────────────────
30s   │ (stopped)                          │ FastAPI running ✓
      │                                    │ Port 8000 open
```

## Environment Variables Flow

```
.env file (local)
      │
      ├─── OPENAI_API_KEY ────────┬─→ Setup Container
      │                           └─→ Backend Container
      │
      └─── JWT_SECRET ────────────────→ Backend Container

docker-compose.yml
      │
      ├─── DATABASE_URL ──────────┬─→ Setup Container
      │                           └─→ Backend Container
      │
      ├─── VECTOR_STORE_PATH ─────┬─→ Setup Container
      │                           └─→ Backend Container
      │
      └─── Other configs ─────────────→ Backend Container
```

## Dependency Graph

```
              db (PostgreSQL)
                 │
                 │ health check: service_healthy
                 │
                 ▼
              setup
                 │
                 │ condition: service_completed_successfully
                 │
                 ▼
              backend ──────────┐
                                │
                                │ network connection
                                │
                                ▼
                            frontend
```

## File System Layout

```
CareConnect/
│
├── setup/                          ← Setup directory
│   ├── Dockerfile                  ← Setup container
│   ├── run_setup.sh                ← Orchestrator
│   ├── scripts/                    ← Python scripts
│   │   ├── seed_demo_data.py
│   │   ├── generate_doctor_pdfs.py
│   │   └── index_pdfs.py
│   ├── README.md                   ← Full documentation
│   ├── QUICKSTART.md               ← Quick guide
│   ├── MIGRATION_SUMMARY.md        ← Migration notes
│   └── ARCHITECTURE.md             ← This file
│
├── backend/                        ← Backend application
│   ├── app/                        ← Application code
│   ├── alembic/                    ← Migrations
│   └── Dockerfile                  ← Backend container
│
├── frontend/                       ← Frontend application
│   ├── src/                        ← React code
│   └── Dockerfile                  ← Frontend container
│
└── docker-compose.yml              ← Multi-container config
```

## Why This Architecture?

### Benefits

✅ **Separation of Concerns**
- Setup runs once, backend runs continuously
- Clear boundary between initialization and runtime

✅ **Fast Backend Startup**
- No initialization delays
- Backend starts immediately after setup

✅ **Easy Data Reset**
- `docker-compose down -v && docker-compose up`
- Clean slate in seconds

✅ **Independent Execution**
- Run setup without restarting backend
- Useful for data refresh or testing

✅ **Better Debugging**
- Isolated logs for setup vs runtime
- Clear success/failure signals

✅ **Production Ready**
- Can be run as Kubernetes init container
- Can be run as CI/CD job
- No setup code in production runtime

### Comparison

**Before** (Inline Initialization):
```
docker-compose up
  → Backend starts
  → Run migrations
  → Seed data
  → Generate PDFs
  → Index RAG
  → Start FastAPI server
  → Ready to serve (30+ seconds)
```

**After** (Separate Setup):
```
docker-compose up
  → Setup container runs (25 seconds)
    ├─ Migrations
    ├─ Seed data
    ├─ Generate PDFs
    └─ Index RAG
  → Setup exits ✓
  → Backend starts (5 seconds)
  → Ready to serve immediately
```

## Production Deployment

### Option 1: One-Time Job
```bash
# Run setup as separate job
docker run --rm careconnect-setup

# Then start backend
docker run careconnect-backend
```

### Option 2: Init Container (Kubernetes)
```yaml
initContainers:
  - name: setup
    image: careconnect-setup:latest
    env:
      - name: DATABASE_URL
        valueFrom:
          secretKeyRef:
            name: db-credentials
            key: url
```

### Option 3: Manual Execution
```bash
# SSH into server
ssh production-server

# Run setup
docker-compose -f docker-compose.prod.yml run --rm setup

# Start services
docker-compose -f docker-compose.prod.yml up -d
```

---

**This architecture provides a clean, maintainable, and production-ready initialization system.**
