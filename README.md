# CareConnect

**An AI-Driven Healthcare Logistics Assistant**

CareConnect is a production-grade, full-stack healthcare logistics assistant that enables patients to interact with healthcare systems through natural language. The system combines large language models with deterministic tool execution and retrieval-augmented generation (RAG) to support appointment scheduling, provider discovery, and facility information retrieval.

The platform is scoped to healthcare logistics and informational support. It does **not** provide medical advice.

---

## Key Capabilities

* Conversational AI with structured and auditable tool orchestration
* Appointment booking, modification, and cancellation
* Provider discovery by specialty and availability
* Retrieval-augmented generation for facility and laboratory preparation information
* Multi-modal interaction (text and voice)
* Human handover with incident tracking
* Privacy-conscious logging and operational metrics
* Production-oriented, modular architecture

---

## System Architecture (Summary)

* **Frontend:** React 18, TypeScript, Material UI
* **Backend:** FastAPI, Python 3.11
* **LLM Integration:** OpenAI Responses API with function calling
* **Retrieval:** ChromaDB with OpenAI embeddings
* **Database:** SQLite (containerized, persistent volumes)
* **Voice:** OpenAI Whisper (speech-to-text) and OpenAI TTS
* **Observability:** Prometheus metrics and structured logging

---

## Running CareConnect Locally

### Prerequisites

Ensure the following are installed and running:

* Docker Desktop
* Docker Compose
* An OpenAI API key

---

### 1. Clone the Repository

```bash
git clone <repository-url>
cd careconnect
```

---

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit the file and set at minimum:

```env
OPENAI_API_KEY=sk-your-api-key-here
JWT_SECRET=your-random-secret
ENVIRONMENT=development
```

---

### 3. Start the Application

```bash
docker-compose up -d
```

This starts the backend API, frontend UI, vector database, and the persistent application database. Allow approximately 30 seconds for initialization.

Check container status:

```bash
docker-compose ps
```

---

### 4. (Recommended) Seed Demo Data

Populate the system with sample providers, appointments, and RAG documents:

```bash
docker-compose exec backend python scripts/seed_demo_data.py
```

---

### 5. Access Local Services

* **Frontend UI:** [http://localhost:5173](http://localhost:5173)
* **API Documentation (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
* **Health Check:** [http://localhost:8000/healthz](http://localhost:8000/healthz)

---

### 6. Stop the Application

```bash
docker-compose down
```

To fully reset data:

```bash
docker-compose down -v
```

---

## Project Structure (High-Level)

```
careconnect/
├── backend/        # FastAPI backend and agent logic
├── frontend/       # React frontend
├── docs/           # Architecture and evaluation documentation
└── docker-compose.yml
```

---

## Intended Use

CareConnect is designed as a research-grade and production-oriented reference implementation for agentic AI systems applied to healthcare logistics, emphasizing safety, determinism, and extensibility.
