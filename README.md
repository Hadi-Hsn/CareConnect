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

# Start with Docker (includes automatic data population)
docker-compose up --build
```

**What happens on first start:**
1. 🗄️ PostgreSQL database starts
2. 🔧 Setup container runs (one-time):
   - Applies database migrations
   - Seeds demo users, providers, and lab tests
   - Generates 5 doctor profile PDFs
   - Indexes all documents into RAG system
3. 🚀 Backend API starts (after setup completes)
4. 🎨 Frontend starts

Visit:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Metrics: http://localhost:8000/metrics

Demo credentials:
- Patient: `patient@careconnect.health` / `password123`
- Admin: `admin@careconnect.health` / `admin123`

**Admin Features:**
- Full CRUD operations for doctors/providers
- Comprehensive appointment management
- Schedule management and time blocking
- PDF upload and RAG integration for doctor profiles
- System statistics and reporting

### Resetting Data

To reset and re-populate all data:

```bash
# Stop and remove everything
docker-compose down -v

# Restart fresh (will re-run setup)
docker-compose up --build
```

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
│   ├── scripts/          # Development scripts
│   └── tests/            # Pytest tests
├── frontend/             # React application
│   ├── src/
│   │   ├── components/   # Reusable UI components
│   │   ├── pages/        # Chat, Appointments, Labs, Admin
│   │   ├── lib/          # API client, theme
│   │   └── types/        # TypeScript types
│   └── public/
├── setup/                # Database initialization 🆕
│   ├── scripts/          # Seed data, PDF generation, RAG indexing
│   ├── Dockerfile        # Setup container
│   ├── run_setup.sh      # Setup orchestration
│   └── README.md         # Setup documentation
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
- **Content**: Doctor profiles, facility docs, FAQs
- **Auto-indexing**: PDFs indexed automatically on container startup

See [RAG System Documentation](docs/RAG_SYSTEM.md) for details.

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
# Start all services (includes setup on first run)
docker-compose up --build

# Re-run setup only (reset data)
docker-compose up setup

# Apply database migrations manually
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

**Admin** 🆕
- `POST /api/v1/admin/doctors` - Create doctor
- `PUT /api/v1/admin/doctors/{id}` - Update doctor
- `DELETE /api/v1/admin/doctors/{id}` - Delete doctor
- `POST /api/v1/admin/doctors/{id}/upload-profile` - Upload doctor PDF
- `GET /api/v1/admin/appointments` - List all appointments
- `PUT /api/v1/admin/appointments/{id}` - Update appointment
- `GET /api/v1/admin/doctors/{id}/schedule` - View schedule
- `POST /api/v1/admin/doctors/{id}/block-time` - Block time slot
- `GET /api/v1/admin/stats/overview` - System statistics

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
- [RAG System Documentation](docs/RAG_SYSTEM.md)
- [RAG Quick Start Guide](docs/RAG_QUICKSTART.md)
- [Admin API Documentation](docs/ADMIN_API.md)
- [Admin User Guide](docs/ADMIN_GUIDE.md)
- [Setup Documentation](setup/README.md) 🆕

---

**Built with ❤️ for healthcare accessibility**
