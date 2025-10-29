# CareConnect Architecture

This document provides detailed architectural information about the CareConnect healthcare assistant system.

## System Overview

CareConnect is a multi-tier application with the following layers:

```
┌─────────────────────────────────────────────────────┐
│               Frontend (React)                      │
│  - Material UI Components                           │
│  - TanStack Query for state management              │
│  - Axios API client with auth interceptor           │
└─────────────────┬───────────────────────────────────┘
                  │ REST API (HTTP/JSON)
┌─────────────────┴───────────────────────────────────┐
│             API Layer (FastAPI)                     │
│  - Rate limiting (60/min)                           │
│  - Auth middleware (JWT)                            │
│  - Request ID tracking                              │
│  - Exception handling                               │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────┴───────────────────────────────────┐
│           Service Layer                             │
│  - AgentRouter (OpenAI orchestration)               │
│  - RAGService (document retrieval)                  │
│  - EmailClient (SMTP)                               │
│  - SchedulingClient (mock → real EHR)               │
│  - IntentClassifier                                 │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────┴──────────────┬────────────────────┐
│         Data Layer             │   External APIs    │
│  - SQLAlchemy async models     │  - OpenAI API      │
│  - FAISS vector store          │  - SMTP Server     │
│  - PostgreSQL database         │                    │
└────────────────────────────────┴────────────────────┘
```

## Core Components

### 1. Agent Router (`app/agents/router.py`)

The `AgentRouter` orchestrates conversations using OpenAI's function calling:

**Flow:**
1. Receives user message and conversation history
2. Classifies intent (informational vs action)
3. Pre-retrieves RAG context if informational
4. Calls OpenAI Responses API with available tools
5. Executes tool calls (up to 10 iterations)
6. Returns final assistant response

**Tool Execution Loop:**
```python
while response has tool_calls and iterations < max:
    for tool_call in response.tool_calls:
        result = execute_tool(tool_call)
        append result to messages
    response = call_openai(messages, tools)
return response.content
```

**Available Tools:**
- `search_timeslots` - Query available appointments
- `book_appointment` - Create booking with confirmation code
- `modify_appointment` - Change appointment time
- `cancel_appointment` - Cancel booking
- `send_email_confirmation` - Send notification
- `rag_lookup` - Retrieve facility information

### 2. RAG Service (`app/services/rag_service.py`)

Manages document indexing and retrieval:

**Indexing Pipeline:**
```
Document → Text Extraction
         ↓
    Chunking (1000 chars, 200 overlap)
         ↓
    OpenAI Embeddings (text-embedding-3-large)
         ↓
    FAISS Index (L2 normalized for cosine)
         ↓
    Metadata Storage (pickle)
```

**Retrieval:**
- Accepts query text
- Generates query embedding
- Performs similarity search (default top_k=3)
- Filters by metadata (optional)
- Returns ranked chunks with metadata

### 3. Vector Store (`app/core/vectorstore/`)

**Abstract Interface:**
```python
class VectorStore(ABC):
    @abstractmethod
    async def upsert(docs, metadatas) -> List[str]
    
    @abstractmethod
    async def similarity_search(query, top_k, filter) -> List[Document]
    
    @abstractmethod
    async def delete(ids) -> None
```

**FAISS Implementation:**
- Uses IndexFlatL2 with L2-normalized vectors (cosine similarity)
- Batches embeddings (100 per request)
- Persists index to disk with pickle metadata
- Thread-safe with asyncio locks

**Swappable Alternatives:**
- pgvector: Postgres extension for vector similarity
- Weaviate: Cloud-native vector database
- Pinecone: Managed vector database
- Qdrant: High-performance vector search

### 4. Database Models (`app/models/`)

**Entity Relationships:**
```
User ──────< Appointment >────── Provider
  │
  └──────< BookingEvent
               │
               └─ audit_log (JSON)

LabTest (independent)
```

**Key Models:**
- `User`: Authentication, roles (patient/staff/admin)
- `Provider`: Healthcare providers with departments/specializations
- `Appointment`: Bookings with status tracking (confirmed/cancelled/completed)
- `LabTest`: Lab tests with preparation instructions
- `BookingEvent`: Audit trail for all booking actions

**Database Support:**
- Production: PostgreSQL with psycopg3 (async)
- Development: SQLite with aiosqlite
- Migrations: Alembic

### 5. Email Service (`app/services/email_client.py`)

**SMTP Implementation:**
```python
async def send_email(to_email, subject, html_content):
    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_user,
        password=settings.smtp_password,
        use_tls=True
    )
```

**Features:**
- HTML templates with appointment details
- Confirmation code embedding
- Structured logging for debugging
- Supports Gmail, custom SMTP servers

### 6. Scheduling Client (`app/services/scheduling_client.py`)

**Abstract Interface:**
```python
class SchedulingClient(ABC):
    @abstractmethod
    async def get_timeslots(provider_id, date, duration) -> List[Timeslot]
    
    @abstractmethod
    async def book_appointment(details) -> Appointment
    
    @abstractmethod
    async def modify_appointment(id, new_time) -> Appointment
    
    @abstractmethod
    async def cancel_appointment(id, reason) -> bool
```

**Mock Implementation:**
- Generates 30-min slots from 9 AM to 5 PM
- Checks database for existing appointments
- Creates confirmation codes (8 random uppercase chars)
- Persists to SQLAlchemy models

**Real Integration:**
To integrate with real EHR systems (Epic, Cerner, etc.):
1. Create new file `app/services/epic_scheduling_client.py`
2. Implement `SchedulingClient` interface
3. Call Epic FHIR API for slots and bookings
4. Update dependency injection in `main.py`

## Data Flow Diagrams

### Appointment Booking Flow

```
User: "Book appointment with Dr. Smith on Monday"
  ↓
Frontend → POST /api/v1/agent/chat
  ↓
AgentRouter.chat_turn()
  ↓
IntentClassifier → "action"
  ↓
OpenAI (with tools) → tool_call: search_timeslots
  ↓
SchedulingClient.get_timeslots(dr_smith, monday)
  ↓  (returns available slots)
OpenAI → "Which time works: 9 AM, 10:30 AM, 2 PM?"
  ↓
User: "2 PM"
  ↓
OpenAI → tool_call: book_appointment
  ↓
SchedulingClient.book_appointment(dr_smith, 2pm)
  ↓
Database: INSERT INTO appointments
  ↓
OpenAI → tool_call: send_email_confirmation
  ↓
EmailClient.send_confirmation(user_email, appt_details)
  ↓  (SMTP)
OpenAI → "Your appointment is confirmed! Confirmation: ABC123XY"
  ↓
Frontend displays response
```

### RAG Retrieval Flow

```
User: "What are your parking options?"
  ↓
Frontend → POST /api/v1/agent/chat
  ↓
AgentRouter.chat_turn()
  ↓
IntentClassifier → "information"
  ↓
RAGService.retrieve("parking options", top_k=3)
  ↓
VectorStore.similarity_search()
  ↓
  - Chunk 1: "We have 3 parking garages..."
  - Chunk 2: "Valet parking available..."
  - Chunk 3: "Visitor parking validation..."
  ↓
AgentRouter adds context to system message
  ↓
OpenAI (without tool calls) → synthesizes answer
  ↓
"We offer three parking options: garage parking on levels 1-3..."
```

## Security Architecture

### Authentication Flow

```
User → POST /api/v1/auth/login {email, password}
  ↓
Security.verify_password(hash_from_db, provided_password)
  ↓
Security.create_access_token(user_id, role)
  ↓
Returns: {access_token: "eyJ...", token_type: "bearer"}
  ↓
Frontend stores in localStorage
  ↓
All subsequent requests include header:
  Authorization: Bearer eyJ...
  ↓
API dependency: get_current_user() validates token
  ↓
Extracts user_id and role from JWT claims
  ↓
Query database for full User object
  ↓
Inject into endpoint as current_user parameter
```

### PHI Protection

**Logging:**
- When `ENABLE_PRIVACY_MODE=true`:
  - Mask SSN, MRN, credit cards in logs
  - Redact email addresses
  - Replace with "[REDACTED]"
  
**Storage:**
- Passwords: bcrypt hashed (12 rounds)
- Tokens: Short-lived JWTs (default 30 min)
- No raw PHI in vector store metadata (only doc IDs)

**Network:**
- CORS restricted to frontend origin
- Rate limiting per IP
- HTTPS enforced in production (FORCE_HTTPS=true)

## Observability

### Structured Logging

All logs include:
- `timestamp` (ISO8601)
- `level` (DEBUG/INFO/WARNING/ERROR)
- `event` (descriptive message)
- `request_id` (UUID for tracing)
- `user_id` (if authenticated)
- `module` (Python module name)

**Format:**
- Development: Colored console output
- Production: JSON lines for log aggregation

### Prometheus Metrics

Exposed at `/metrics`:

**Counters:**
- `http_requests_total{method, endpoint, status}`
- `agent_tool_calls_total{tool_name, success}`

**Histograms:**
- `http_request_duration_seconds{method, endpoint}`
- `agent_response_duration_seconds`
- `vectorstore_query_duration_seconds`

**Gauges:**
- `active_users_total`
- `vectorstore_documents_total`

**Queries:**
```promql
# P50 latency
histogram_quantile(0.5, 
  rate(http_request_duration_seconds_bucket[5m]))

# P90 latency
histogram_quantile(0.9, 
  rate(http_request_duration_seconds_bucket[5m]))

# Success rate
sum(rate(http_requests_total{status=~"2.."}[5m])) /
sum(rate(http_requests_total[5m]))
```

## Deployment Architecture

### Development (docker-compose)

```yaml
services:
  backend:
    - FastAPI on port 8000
    - Mounts ./backend for hot reload
    - SQLite database
    
  frontend:
    - Vite dev server on port 5173
    - Mounts ./frontend for HMR
    - Proxies API to backend
    
  (no postgres, no nginx in dev)
```

### Production

```
               Internet
                  ↓
             Load Balancer (SSL termination)
                  ↓
        ┌─────────┴─────────┐
        ↓                   ↓
    NGINX (reverse proxy) NGINX
        ↓                   ↓
    Frontend            Backend
    (static files)      (uvicorn workers)
                            ↓
                    PostgreSQL (RDS/managed)
                            ↓
                    FAISS index (EFS/persistent storage)
```

**Scaling:**
- Frontend: CDN for static assets
- Backend: Horizontal scaling (stateless)
  - 4-8 uvicorn workers per container
  - Multiple containers behind load balancer
- Database: Read replicas for reporting
- Vector store: Shared filesystem (EFS) or migrate to managed vector DB

**Environment Variables (Production):**
- `DATABASE_URL=postgresql+asyncpg://...`
- `OPENAI_API_KEY=sk-...` (from secrets manager)
- `SMTP_HOST`, `SMTP_USERNAME`, `SMTP_PASSWORD` (from secrets manager)
- `FRONTEND_URL=https://careconnect.health`
- `ENABLE_PRIVACY_MODE=true`
- `LOG_LEVEL=INFO`
- `FORCE_HTTPS=true`

## Technology Decisions

### Why FastAPI?
- Async/await native (critical for I/O-bound AI workloads)
- Automatic OpenAPI docs
- Pydantic validation built-in
- Strong typing with type hints
- Fast performance (on par with Node.js)

### Why FAISS for vectors?
- Fast similarity search (Facebook AI Research)
- Works in-memory (low latency)
- Easy to swap for managed solution later
- No additional infrastructure in dev

### Why React + Material UI?
- Component reusability
- Strong TypeScript support
- Material Design = professional healthcare UI
- Large ecosystem of libraries

### Why OpenAI Responses API?
- Native function calling (no prompt engineering)
- Reliable tool execution loop
- Easy to define tools with JSON schemas
- High-quality GPT-4 responses

### Why PostgreSQL?
- Strong ACID guarantees (critical for bookings)
- JSON column support (booking_event.audit_log)
- pgvector extension available (future migration)
- Industry standard for healthcare apps

## Performance Considerations

### Current Bottlenecks

1. **OpenAI API latency** (~1-3s per call)
   - Mitigation: Pre-retrieve RAG context, use streaming (future)
   
2. **FAISS similarity search** (linear scan)
   - Mitigation: Migrate to HNSW index or pgvector for large datasets
   
3. **Database round-trips**
   - Mitigation: Connection pooling, eager loading relationships

### Optimization Strategies

**Caching:**
- Provider list (changes infrequently)
- Lab test catalog
- RAG embeddings (cache OpenAI calls)

**Async Execution:**
- Email sending (don't block response)
- Metrics recording
- Audit log writes

**Load Testing:**
- Target: 100 concurrent users
- Tool: Locust or k6
- Metrics: P95 latency < 5s, throughput > 50 req/s

## Future Enhancements

### Short-term
- [ ] Add streaming responses (SSE) for real-time chat
- [ ] Implement conversation memory (Redis cache)
- [ ] Add file upload for lab results
- [ ] Create mobile app (React Native)

### Medium-term
- [ ] Multi-language support (i18n)
- [ ] Voice interface (speech-to-text)
- [ ] Video appointment integration (Zoom/Teams)
- [ ] Insurance verification

### Long-term
- [ ] Multi-tenant support (multiple healthcare providers)
- [ ] FHIR API compliance
- [ ] Clinical decision support (drug interactions, etc.)
- [ ] Predictive analytics (no-show risk, demand forecasting)

---

**Last Updated:** 2025
**Version:** 1.0