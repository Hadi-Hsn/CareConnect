# CareConnect - AI Healthcare Assistant

**A production-grade AI-powered healthcare logistics assistant built with React, FastAPI, and OpenAI.**

CareConnect is a full-stack application that uses OpenAI's function calling (Responses API) and RAG (Retrieval-Augmented Generation) to help patients book appointments, find providers, and get facility information through natural conversation.

## 🎥 Demo Video

Watch a demonstration of CareConnect in action: [Demo Video](https://drive.google.com/file/d/1bJLHlo8Nqm0OtvOP7vh37QuxUUHi4FGF/view?usp=sharing)

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites

Before you begin, ensure you have:
- ✅ **Docker Desktop** installed and running ([Download here](https://www.docker.com/products/docker-desktop))
- ✅ **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))
- ✅ **Git** (optional, for cloning)

### Step 1: Get the Code

```bash
# Option A: Clone the repository
git clone <repository-url>
cd CareConnect

# Option B: If you already have the code, navigate to the folder
cd CareConnect
```

### Step 2: Create Environment File

Create a `.env` file in the root directory:

```bash
# On Windows (PowerShell)
Copy-Item .env.example .env

# On macOS/Linux
cp .env.example .env
```

Or manually create a file named `.env` in the `CareConnect` folder.

### Step 3: Add Your OpenAI API Key

Open the `.env` file and add your credentials:

```env
# Required: Your OpenAI API Key
OPENAI_API_KEY=sk-proj-your-actual-key-here

# Required: Secret for JWT tokens (any random string)
JWT_SECRET=your-random-secret-key-change-this-in-production
# Here is a newly generated JWT Key, replace 'your-random-secret-key-change-this-in-production' with 'a8bfce6ec2a2a158ee26a54d915596da'

# Optional: Email settings (for appointment confirmations)
SENDGRID_API_KEY=your-sendgrid-key-here
SENDGRID_FROM_EMAIL=noreply@careconnect.com
# Replace 'your-sendgrid-key-here' with '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' 

# Optional: Environment
ENVIRONMENT=development
```

**⚠️ Important:** Replace `sk-proj-your-actual-key-here` with your actual OpenAI API key!

### Step 4: Start the Application

```bash
# Start all services with Docker Compose
docker-compose up -d
```

**What happens during startup:**
1. 🗄️ **ChromaDB** starts (vector database for RAG)
2. 💾 **SQLite** database initializes (main database)
3. 🔧 **Backend** starts (FastAPI server)
4. 🎨 **Frontend** starts (React UI)
5. ⚙️ **Database migrations** run automatically
6. 🌱 **Demo data is seeded** (optional, see Step 5)

**Wait ~30 seconds** for all services to start. Check status:

```bash
# Check if all containers are running
docker-compose ps

# Should show all services as "Up" or "healthy"
```

### Step 5: Seed Demo Data (Recommended)

Populate the database with sample doctors, appointments, and lab test information:

```bash
docker-compose exec backend python scripts/seed_demo_data.py
```

**This will create:**
- ✅ 90+ doctors across 25+ medical departments
- ✅ 2 demo users (patient and admin accounts)
- ✅ Lab test preparation documents (CBC, X-Ray, etc.)
- ✅ Facility information (parking, hours, directions)
- ✅ RAG vector store with searchable documents

**Output should show:**
```
🌱 Starting database seeding...
✓ Database initialized
✓ Seeded 2 users
✓ Seeded 90 providers across all departments
✓ Seeded 8 lab tests
✓ Indexed 5 facility documents (XX chunks)
✓ Indexed 90 doctor profiles (XXX chunks)
✓ Indexed 12 lab test documents (XX chunks)
✅ Database seeding completed successfully!
```

### Step 6: Access the Application

Open your browser and visit:

- **🎨 Frontend UI:** http://localhost:5173
- **📚 API Documentation:** http://localhost:8000/docs
- **❤️ Health Check:** http://localhost:8000/healthz
- **📊 Metrics:** http://localhost:8000/metrics

### Step 7: Login

Use the demo credentials:

| Role | Email | Password |
|------|-------|----------|
| **Patient** | hadihacan@gmail.com | password123 |
| **Admin** | admin@aub.com | Admin@123 |

---

## ✅ Verify Everything Works

### Test the Chat Assistant

1. Go to http://localhost:5173
2. Login as patient (`hadihacan@gmail.com` / `password123`)
3. Click on **Chat** in the sidebar
4. Try these example queries:
   - "I need to book an appointment with a cardiologist"
   - "What are the requirements for a CBC blood test?"
   - "Show me my appointments"
   - "Where is the parking?"
   - "Show me my lab test results"
   - Switch to **Voice Mode** using the microphone button for voice interactions

### Test the Admin Panel

1. Logout and login as admin (`admin@aub.com` / `Admin@123`)
2. Go to **Admin** → **Doctors** to manage providers
3. Go to **Admin** → **Appointments** to manage bookings
4. Go to **Admin** → **Statistics** to view metrics

---

## 🛑 Stop the Application

```bash
# Stop all services (keeps data)
docker-compose down

# Stop and remove all data (complete reset)
docker-compose down -v
```

---

## 🔄 Common Operations

### Restart Services

```bash
# Restart all services
docker-compose restart

# Restart only the backend
docker-compose restart backend

# Restart only the frontend
docker-compose restart frontend
```

### View Logs

```bash
# View all logs
docker-compose logs -f

# View backend logs only
docker-compose logs -f backend

# View last 100 lines
docker-compose logs --tail=100 backend
```

### Reset and Start Fresh

```bash
# Stop everything and remove data
docker-compose down -v

# Rebuild and start
docker-compose up -d --build

# Re-seed the database
docker-compose exec backend python scripts/seed_demo_data.py
```

### Update OpenAI API Key

1. Edit `.env` file
2. Update `OPENAI_API_KEY=sk-your-new-key`
3. Restart backend:
   ```bash
   docker-compose restart backend
   ```

---

## 🏗️ Architecture

### Stack
- **Frontend**: React 18 + TypeScript + Material UI + Vite
- **Backend**: FastAPI + Python 3.11 + SQLAlchemy
- **AI**: OpenAI GPT-4 (Responses API) + Embeddings (text-embedding-3-large)
- **Vector DB**: ChromaDB (Docker container, no credentials needed)
- **Database**: SQLite (file-based, no credentials needed, persistent in Docker volumes)
- **Email**: SendGrid / SMTP (configurable)
- **WhatsApp**: Twilio WhatsApp Business API (optional)
- **Voice**: OpenAI Whisper (STT) + OpenAI TTS (text-to-speech)
- **Observability**: Prometheus + structured logging (structlog)

### Key Features

✅ **Conversational AI Agent** using OpenAI function calling  
✅ **RAG-powered information retrieval** for facility docs  
✅ **Multi-channel support**: Web chat, WhatsApp, and Voice interfaces  
✅ **WhatsApp Integration**: Full AI assistant access via WhatsApp using Twilio  
✅ **Voice Chat**: Speech-to-text and text-to-speech with OpenAI Whisper and TTS  
✅ **Lab Test Results**: View and manage patient lab test results with PDF support  
✅ **Human Handover**: Escalate conversations to human support with incident tracking  
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

### Backend Development

```bash
# Access backend container shell
docker-compose exec backend bash

# Run database migrations
docker-compose exec backend alembic upgrade head

# Create a new migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Run tests
docker-compose exec backend pytest -v

# Check code formatting
docker-compose exec backend black . --check
docker-compose exec backend isort . --check-only

# Format code
docker-compose exec backend black .
docker-compose exec backend isort .

# Type checking
docker-compose exec backend mypy app
```

### Frontend Development

```bash
# Access frontend container shell
docker-compose exec frontend sh

# Install new dependency
docker-compose exec frontend npm install <package-name>

# Run linter
docker-compose exec frontend npm run lint

# Format code
docker-compose exec frontend npm run format

# Build for production
docker-compose exec frontend npm run build
```

### Database Operations

```bash
# Access SQLite database
docker-compose exec backend sqlite3 /app/data/careconnect.db

# Backup database
docker-compose exec backend cp /app/data/careconnect.db /app/data/careconnect.db.backup

# Restore database
docker-compose exec backend cp /app/data/careconnect.db.backup /app/data/careconnect.db
```

### ChromaDB (Vector Store)

```bash
# View ChromaDB logs
docker-compose logs -f chromadb

# Reset vector store (removes all indexed documents)
docker-compose exec backend python -c "from app.services.rag_service import RAGService; import asyncio; asyncio.run(RAGService().clear())"

# Re-index documents
docker-compose exec backend python scripts/seed_demo_data.py
```

---

## 🧪 Testing

### Manual Testing with the API

Visit http://localhost:8000/docs to access the interactive API documentation (Swagger UI).

**Example: Test the chat endpoint**
1. Go to `POST /api/v1/agent/chat`
2. Click "Try it out"
3. Use this request body:
   ```json
   {
     "messages": [
       {
         "role": "user",
         "content": "I need to book an appointment with a cardiologist next week"
       }
     ],
     "user_id": 1
   }
   ```
4. Click "Execute"

### Automated Tests

```bash
# Run backend unit tests
docker-compose exec backend pytest tests/ -v

# Run with coverage
docker-compose exec backend pytest tests/ --cov=app --cov-report=html

# Run specific test file
docker-compose exec backend pytest tests/test_agent.py -v

# Run evaluation suite
docker-compose exec backend python tests/evaluation/run_eval.py
```

---

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

**Voice** 🆕
- `POST /api/v1/voice/speech-to-text` - Convert audio to text
- `POST /api/v1/voice/text-to-speech` - Convert text to audio

**Lab Test Results** 🆕
- `GET /api/v1/test-results` - List patient test results
- `GET /api/v1/test-results/{id}` - Get test result details
- `GET /api/v1/test-results/{id}/pdf` - Download test result PDF

**Handover** 🆕
- `POST /api/v1/handover/request` - Request handover to human support
- `GET /api/v1/handover/incidents` - List handover incidents (admin)
- `PUT /api/v1/handover/incidents/{id}` - Update incident status (admin)

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
- [WhatsApp Integration Guide](WHATSAPP_INTEGRATION_GUIDE.md) 🆕
- [Setup Documentation](setup/README.md) 🆕

---

## 🤝 Contributing

### Code Style

- **Backend:** Follow PEP 8, use Black and isort for formatting
- **Frontend:** Follow Airbnb style guide, use Prettier
- **Commits:** Use conventional commits (feat:, fix:, docs:, etc.)

### Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linters
5. Commit your changes (`git commit -m 'feat: add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🆘 Support

- **Issues:** [GitHub Issues](https://github.com/your-repo/issues)
- **Email:** support@careconnect.com
- **Documentation:** Check the `/docs` folder

---

**Built with ❤️ for healthcare accessibility**

**Stack:** React 18 • FastAPI • OpenAI GPT-4 • ChromaDB • PostgreSQL • Docker
