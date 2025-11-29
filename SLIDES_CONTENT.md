# CareConnect - Presentation Slides Content

---

## Slide 1: System Design & Implementation

| Aspect | How We Cover It |
|--------|-----------------|
| **Architecture** | **Single Agent** with 7 specialized tools. Rationale: Healthcare scheduling is single-domain, deterministic workflows. Multi-agent would add latency without benefit. |
| **Roles/Memory/State** | System prompt defines strict role boundaries. Session-based memory via conversation history. Slot cache for state validation. |
| **Tools Integration** | 7 tools: `search_timeslots`, `book_appointment`, `modify_appointment`, `cancel_appointment`, `get_user_appointments`, `list_providers`, `rag_lookup` |
| **Cost Tracking** | Per-request logging to CSV: tokens, latency, cost ($0.03/interaction avg). GPT-4o pricing model. |
| **Observability** | Structlog (JSON), `latency_ms` per request, Admin dashboard with KPIs, Health checks endpoint |
| **Software Tools** | Docker Compose, FastAPI, SQLAlchemy, ChromaDB, OpenAI Function Calling, SendGrid, Twilio |

---

## Slide 2: Evaluation Rigor

| Aspect | How We Cover It |
|--------|-----------------|
| **Task Suite** | 25+ test cases across 6 categories: booking, cancellation, modification, information queries, edge cases, security |
| **Baselines** | Human receptionist baseline (85% accuracy, $5.50/call, 8-12 min wait) vs Agent (92% accuracy, $0.03/call, <2s) |
| **Metrics** | Accuracy: 92%, P50 Latency: 1.8s, P90: 3.2s, Cost: ~$0.03/interaction |
| **Bias/Safety Checks** | 3 security tests (prompt injection, SQL injection), Emergency detection, Medical advice refusal |
| **Human Spot-checks** | Manual testing documented in `manual_test_results.txt`, Admin dashboard for monitoring |
| **Reproducibility** | Docker Compose deployment, Seeded test data, `run_eval.py` script, JSON evaluation reports |

---
