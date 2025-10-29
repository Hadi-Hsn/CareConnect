# API Contract & Tool Schemas

This document describes the REST API endpoints and OpenAI tool schemas used in CareConnect.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.careconnect.health`

All endpoints are prefixed with `/api/v1` unless otherwise noted.

## Authentication

Most endpoints require authentication via JWT bearer token.

### Login

**POST** `/auth/login`

Request:
```json
{
  "email": "patient@example.com",
  "password": "securepassword"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "patient@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890",
    "date_of_birth": "1990-01-15",
    "role": "patient"
  }
}
```

### Register

**POST** `/auth/register`

Request:
```json
{
  "email": "newpatient@example.com",
  "password": "securepassword",
  "first_name": "Jane",
  "last_name": "Smith",
  "phone_number": "+1234567891",
  "date_of_birth": "1985-03-20"
}
```

Response: Same as login

### Using Tokens

Include in all authenticated requests:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Agent Endpoints

### Chat

**POST** `/agent/chat`

Send a message to the AI agent.

**Rate Limit**: 60 requests per minute

Request:
```json
{
  "message": "I need to book an appointment with a cardiologist",
  "conversation_history": [
    {
      "role": "user",
      "content": "Hello"
    },
    {
      "role": "assistant",
      "content": "Hi! How can I help you today?"
    }
  ]
}
```

Response:
```json
{
  "response": "I'd be happy to help you book a cardiology appointment. We have several cardiologists available. Could you tell me your preferred date?",
  "tool_calls": [
    {
      "tool": "search_timeslots",
      "arguments": {
        "department": "Cardiology"
      },
      "result": {
        "providers": [
          {"id": 1, "name": "Dr. Sarah Johnson"}
        ]
      }
    }
  ]
}
```

### Submit Feedback

**POST** `/agent/feedback`

Submit user satisfaction feedback.

Request:
```json
{
  "conversation_id": "conv_123",
  "rating": 5,
  "feedback_text": "Very helpful!"
}
```

Response:
```json
{
  "message": "Thank you for your feedback"
}
```

## RAG Endpoints

### Index Documents

**POST** `/rag/index` (Admin only)

Add documents to the vector store.

Request:
```json
{
  "documents": [
    {
      "id": "doc_parking",
      "content": "We have 3 parking garages available...",
      "metadata": {
        "category": "facilities",
        "title": "Parking Information"
      }
    }
  ]
}
```

Response:
```json
{
  "indexed_count": 1,
  "document_ids": ["doc_parking"]
}
```

### Retrieve Documents

**POST** `/rag/retrieve`

Retrieve relevant documents for a query.

Request:
```json
{
  "query": "parking options",
  "top_k": 3,
  "filter": {
    "category": "facilities"
  }
}
```

Response:
```json
{
  "results": [
    {
      "content": "We have 3 parking garages available on levels 1-3...",
      "metadata": {
        "category": "facilities",
        "title": "Parking Information",
        "doc_id": "doc_parking"
      },
      "score": 0.89
    }
  ]
}
```

### Vector Store Stats

**GET** `/rag/stats`

Get statistics about indexed documents.

Response:
```json
{
  "total_documents": 127,
  "total_chunks": 453,
  "index_size_mb": 2.3,
  "last_updated": "2025-01-15T10:30:00Z"
}
```

## Provider Endpoints

### List Providers

**GET** `/providers`

Query parameters:
- `department` (optional): Filter by department
- `skip` (optional, default 0): Pagination offset
- `limit` (optional, default 100): Page size

Response:
```json
{
  "providers": [
    {
      "id": 1,
      "first_name": "Sarah",
      "last_name": "Johnson",
      "department": "Cardiology",
      "specialization": "Interventional Cardiology",
      "is_accepting_patients": true
    }
  ],
  "total": 12
}
```

### Get Provider Timeslots

**GET** `/providers/{provider_id}/timeslots`

Query parameters:
- `date`: Date in YYYY-MM-DD format
- `duration_minutes` (optional, default 30): Appointment duration

Response:
```json
{
  "provider": {
    "id": 1,
    "name": "Dr. Sarah Johnson"
  },
  "date": "2025-02-01",
  "slots": [
    {
      "slot_id": "2025-02-01_09:00",
      "start_time": "09:00",
      "end_time": "09:30",
      "is_available": true
    },
    {
      "slot_id": "2025-02-01_09:30",
      "start_time": "09:30",
      "end_time": "10:00",
      "is_available": false
    }
  ]
}
```

## Appointment Endpoints

### List Appointments

**GET** `/appointments`

Query parameters:
- `status` (optional): Filter by status (confirmed/cancelled/completed)
- `skip` (optional): Pagination
- `limit` (optional): Page size

Response:
```json
{
  "appointments": [
    {
      "id": 1,
      "patient_id": 1,
      "provider_id": 1,
      "appointment_time": "2025-02-01T09:00:00",
      "duration_minutes": 30,
      "reason": "Annual checkup",
      "status": "confirmed",
      "confirmation_code": "ABC123XY",
      "provider": {
        "name": "Dr. Sarah Johnson"
      }
    }
  ]
}
```

### Create Appointment

**POST** `/appointments`

Request:
```json
{
  "provider_id": 1,
  "appointment_time": "2025-02-01T09:00:00",
  "duration_minutes": 30,
  "reason": "Follow-up visit"
}
```

Response:
```json
{
  "id": 2,
  "confirmation_code": "DEF456GH",
  "status": "confirmed",
  "appointment_time": "2025-02-01T09:00:00"
}
```

### Update Appointment

**PATCH** `/appointments/{appointment_id}`

Request:
```json
{
  "appointment_time": "2025-02-01T10:00:00",
  "reason": "Updated: Follow-up visit with additional concerns"
}
```

Response: Updated appointment object

### Cancel Appointment

**DELETE** `/appointments/{appointment_id}`

Query parameters:
- `reason` (optional): Cancellation reason

Response:
```json
{
  "message": "Appointment cancelled successfully",
  "confirmation_code": "DEF456GH"
}
```

## Lab Test Endpoints

### List Lab Tests

**GET** `/labs`

Query parameters:
- `search` (optional): Search by name
- `skip` (optional): Pagination
- `limit` (optional): Page size

Response:
```json
{
  "lab_tests": [
    {
      "id": 1,
      "name": "Complete Blood Count (CBC)",
      "description": "Measures different components of blood",
      "preparation_instructions": "Fasting for 8-12 hours recommended",
      "estimated_time_minutes": 15,
      "is_fasting_required": true
    }
  ]
}
```

## Email Endpoints

### Send Test Email

**POST** `/email/test` (Admin only)

Request:
```json
{
  "recipient": "test@example.com",
  "subject": "Test Email",
  "body": "This is a test"
}
```

Response:
```json
{
  "success": true,
  "provider": "smtp"
}
```

## Metrics Endpoints

### Get KPIs

**GET** `/eval/kpis`

Query parameters:
- `start_date` (optional): Start of date range
- `end_date` (optional): End of date range

Response:
```json
{
  "task_completion_rate": 0.92,
  "avg_response_time_seconds": 1.8,
  "p50_latency_seconds": 1.5,
  "p90_latency_seconds": 3.2,
  "total_conversations": 1523,
  "successful_bookings": 1401,
  "avg_satisfaction_score": 4.6
}
```

## Health Check

**GET** `/health`

No authentication required.

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "dependencies": {
    "database": "connected",
    "openai": "available",
    "vectorstore": "loaded"
  }
}
```

## OpenAI Tool Schemas

These are the tool definitions passed to OpenAI for function calling.

### search_timeslots

**Description**: Find available appointment slots for a provider or department.

**Parameters**:
```json
{
  "type": "object",
  "properties": {
    "provider_id": {
      "type": "integer",
      "description": "ID of specific provider (optional if department provided)"
    },
    "department": {
      "type": "string",
      "description": "Department name (e.g., 'Cardiology', 'Primary Care')"
    },
    "date": {
      "type": "string",
      "description": "Date in YYYY-MM-DD format"
    },
    "duration_minutes": {
      "type": "integer",
      "description": "Appointment duration (default 30)",
      "default": 30
    }
  },
  "required": ["date"]
}
```

**Returns**:
```json
{
  "provider": {
    "id": 1,
    "name": "Dr. Sarah Johnson"
  },
  "available_slots": [
    {
      "slot_id": "2025-02-01_09:00",
      "start_time": "09:00",
      "end_time": "09:30"
    }
  ]
}
```

### book_appointment

**Description**: Book an appointment at a specific timeslot.

**Parameters**:
```json
{
  "type": "object",
  "properties": {
    "provider_id": {
      "type": "integer",
      "description": "Provider ID from search_timeslots result"
    },
    "slot_id": {
      "type": "string",
      "description": "Slot ID from search_timeslots (format: YYYY-MM-DD_HH:MM)"
    },
    "reason": {
      "type": "string",
      "description": "Reason for visit"
    },
    "duration_minutes": {
      "type": "integer",
      "description": "Appointment duration",
      "default": 30
    }
  },
  "required": ["provider_id", "slot_id", "reason"]
}
```

**Returns**:
```json
{
  "appointment_id": 123,
  "confirmation_code": "ABC123XY",
  "appointment_time": "2025-02-01T09:00:00",
  "provider_name": "Dr. Sarah Johnson"
}
```

### modify_appointment

**Description**: Change an existing appointment to a new time.

**Parameters**:
```json
{
  "type": "object",
  "properties": {
    "appointment_id": {
      "type": "integer",
      "description": "ID of appointment to modify"
    },
    "new_slot_id": {
      "type": "string",
      "description": "New slot ID from search_timeslots"
    }
  },
  "required": ["appointment_id", "new_slot_id"]
}
```

**Returns**:
```json
{
  "appointment_id": 123,
  "new_time": "2025-02-01T10:00:00",
  "confirmation_code": "ABC123XY"
}
```

### cancel_appointment

**Description**: Cancel an existing appointment.

**Parameters**:
```json
{
  "type": "object",
  "properties": {
    "appointment_id": {
      "type": "integer",
      "description": "ID of appointment to cancel"
    },
    "reason": {
      "type": "string",
      "description": "Reason for cancellation (optional)"
    }
  },
  "required": ["appointment_id"]
}
```

**Returns**:
```json
{
  "success": true,
  "message": "Appointment ABC123XY cancelled successfully"
}
```

### send_email_confirmation

**Description**: Send appointment confirmation email to patient.

**Parameters**:
```json
{
  "type": "object",
  "properties": {
    "appointment_id": {
      "type": "integer",
      "description": "Appointment to send confirmation for"
    },
    "email_type": {
      "type": "string",
      "enum": ["confirmation", "reminder", "cancellation"],
      "description": "Type of email to send"
    }
  },
  "required": ["appointment_id", "email_type"]
}
```

**Returns**:
```json
{
  "success": true,
  "message": "Confirmation email sent to patient@example.com"
}
```

### rag_lookup

**Description**: Search facility documentation for information.

**Parameters**:
```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "User's question or search query"
    },
    "top_k": {
      "type": "integer",
      "description": "Number of results to return (default 3)",
      "default": 3
    }
  },
  "required": ["query"]
}
```

**Returns**:
```json
{
  "results": [
    {
      "content": "Relevant document chunk...",
      "metadata": {
        "title": "Parking Information",
        "category": "facilities"
      }
    }
  ]
}
```

## Error Responses

All endpoints may return these error formats:

### 400 Bad Request
```json
{
  "detail": "Invalid date format. Use YYYY-MM-DD"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Admin access required"
}
```

### 404 Not Found
```json
{
  "detail": "Appointment not found"
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded. Try again in 60 seconds"
}
```

### 500 Internal Server Error
```json
{
  "detail": "An unexpected error occurred",
  "request_id": "req_abc123"
}
```

## Rate Limits

- **Chat endpoint**: 60 requests per minute per IP
- **All other endpoints**: 300 requests per minute per IP

## Versioning

API version is in the URL: `/api/v1/...`

Breaking changes will increment the version: `/api/v2/...`

---

**Last Updated:** 2025
**API Version:** 1.0