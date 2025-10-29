# CareConnect - Your Smart Health Assistant

**A production-grade AI-powered healthcare logistics assistant built with React, FastAPI, and OpenAI.**

CareConnect is a full-stack application that uses OpenAI's function calling (Responses API) and RAG (Retrieval-Augmented Generation) to help patients book appointments, find providers, and get facility information through natural conversation.

## 🚀 Quick Start

```bash
# Clone and setup
cd CareConnect

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Add your OpenAI API key to backend/.env
# OPENAI_API_KEY=sk-your-key-here

# Start with Docker
docker-compose up --build

# Or manually:
# Backend: cd backend && pip install -e ".[dev]" && uvicorn app.main:app --reload
# Frontend: cd frontend && npm install && npm run dev
```

Visit:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Metrics: http://localhost:8000/metrics

Demo credentials:
- Patient: `patient@careconnect.health` / `password123`
- Admin: `admin@careconnect.health` / `admin123`

## 🏗️ Architecture

### Stack
- **Frontend**: React 18 + TypeScript + Material UI + Vite
- **Backend**: FastAPI + Python 3.11 + SQLAlchemy
- **AI**: OpenAI GPT-4 (Responses API) + Embeddings (text-embedding-3-large)
- **Vector DB**: FAISS (dev) → swappable to pgvector/Weaviate
- **Database**: PostgreSQL (prod) / SQLite (dev)
- **Email**: SMTP (Gmail/custom SMTP server)
- **Observability**: Prometheus + structured logging (structlog)

### Key Features

✅ **Conversational AI Agent** using OpenAI function calling  
✅ **RAG-powered information retrieval** for facility docs  
✅ **Mock scheduling client** (easy to swap for real EHR APIs)  
✅ **Production-grade patterns**: async, typed, tested, observable  
✅ **HIPAA-conscious design**: PHI masking, audit trails, privacy mode  
✅ **Success metrics tracking**: completion rate, latency, satisfaction  

## 📁 Project Structure

```
careconnect/
├── backend/               # FastAPI application
│   ├── app/
│   │   ├── agents/       # OpenAI agent + tools + prompts
│   │   ├── api/v1/       # REST endpoints
│   │   ├── core/         # Config, DB, security, vector store
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # Business logic (scheduling, RAG, email)
│   ├── alembic/          # Database migrations
│   ├── scripts/          # Seed data
│   └── tests/            # Pytest tests
├── frontend/             # React application
│   ├── src/
│   │   ├── components/   # Reusable UI components
│   │   ├── pages/        # Chat, Appointments, Labs, Admin
│   │   ├── lib/          # API client, theme
│   │   └── types/        # TypeScript types
│   └── public/
├── docs/                 # Architecture docs
└── docker-compose.yml    # Multi-container setup
```

## 🤖 AI Agent Design

### OpenAI Responses API + Function Calling

The agent uses OpenAI's function calling to orchestrate workflows:

1. **Tools defined** (`backend/app/agents/tools.py`):
   - `search_timeslots` - Find available appointments
   - `book_appointment` - Book with confirmation
   - `modify_appointment` - Change time
   - `cancel_appointment` - Cancel booking
   - `send_email_confirmation` - Send notifications
   - `rag_lookup` - Retrieve facility information

2. **Agent router** (`backend/app/agents/router.py`):
   - Loops until task complete or max iterations
   - Executes tool calls and feeds results back
   - Handles clarifications and error recovery

3. **System prompt** (`backend/app/agents/prompts.py`):
   - Clear role definition (logistics, not medical advice)
   - Tool usage policies
   - Safety guardrails (emergency escalation)

### RAG Implementation

- **Embedding**: OpenAI `text-embedding-3-large` (3072 dims)
- **Chunking**: 1000 chars with 200 char overlap
- **Storage**: FAISS index (swappable via `VectorStore` interface)
- **Retrieval**: Pre-fetch context + on-demand `rag_lookup` tool

## 📊 Success Metrics

Tracked via `/api/v1/eval/kpis`:

| Metric | Target | Implementation |
|--------|--------|----------------|
| Task completion | ≥90% | Track booking flows end-to-end |
| Response latency (p50) | <2s | Prometheus histograms |
| Response latency (p90) | <5s | Percentile aggregation |
| Ambiguity resolution | ≥80% | Count clarification → success |
| User satisfaction | ≥4/5 | Thumbs up/down + ratings |

## 🔐 Security & Privacy

- **Auth**: JWT tokens (OAuth2 compatible)
- **Rate limiting**: 60 req/min per IP (configurable)
- **PHI masking**: Automatic in logs when `ENABLE_PRIVACY_MODE=true`
- **Input validation**: Pydantic on all endpoints
- **CORS**: Restricted to configured frontend origin
- **Secrets**: Never logged; loaded from environment

## 📦 Development Commands

```bash
# Start all services
docker-compose up --build

# Seed demo data
docker-compose exec backend python -m scripts.seed_data

# Apply database migrations
docker-compose exec backend alembic upgrade head

# Run backend tests
cd backend && pytest -v --cov=app

# Run frontend tests
cd frontend && npm run test:e2e

# Format code
cd backend && black . && isort .
cd frontend && npm run format

# Lint code
cd backend && flake8 app && mypy app
cd frontend && npm run lint

# Clean up containers
docker-compose down -v
```

## 🧪 Testing

### Backend (pytest)
```bash
cd backend
pytest -v --cov=app
```

### Frontend (Playwright)
```bash
cd frontend
npm run test:e2e
```

## 📚 API Documentation

### Key Endpoints

**Agent**
- `POST /api/v1/agent/chat` - Main chat interface
- `POST /api/v1/agent/feedback` - Submit user feedback

**RAG**
- `POST /api/v1/rag/index` - Index documents (admin)
- `POST /api/v1/rag/retrieve` - Retrieve relevant chunks
- `GET /api/v1/rag/stats` - Vector store stats

**Providers**
- `GET /api/v1/providers` - List providers
- `GET /api/v1/providers/{id}/timeslots` - Get availability

**Appointments**
- `GET /api/v1/appointments` - List appointments
- `POST /api/v1/appointments` - Create appointment
- `PATCH /api/v1/appointments/{id}` - Update appointment

Full OpenAPI spec: http://localhost:8000/docs

## 🔄 Swappable Components

The architecture uses interfaces to enable swapping:

| Component | Current | Swap To | File |
|-----------|---------|---------|------|
| Vector Store | FAISS | pgvector, Weaviate | `core/vectorstore/` |
| Scheduling | Mock | Epic, Cerner | `services/scheduling_client.py` |
| Email | SMTP | AWS SES, Postmark | `services/email_client.py` |
| Auth | JWT | Auth0, Okta | `core/security.py` |

## 📖 Additional Documentation

- [Architecture Details](docs/ARCHITECTURE.md)
- [API Contract & Tool Schemas](docs/API_CONTRACT.md)
- [Evaluation Framework](docs/EVALUATION.md)
- [Threat Model & Security](docs/THREAT_MODEL.md)

---

**Built with ❤️ for healthcare accessibility**
