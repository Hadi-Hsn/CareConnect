# Complete RAG System Testing Guide

This guide will walk you through testing the complete RAG system implementation.

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key
- Internet connection

## Step 1: Environment Setup

Create a `.env` file in the backend directory:

```bash
cd backend
cat > .env << EOF
OPENAI_API_KEY=sk-your-actual-api-key-here
DATABASE_URL=postgresql+psycopg://careconnect:careconnect_dev@db:5432/careconnect
VECTOR_STORE_PATH=/data/faiss_index
OPENAI_MODEL=gpt-4o
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
OPENAI_EMBEDDING_DIMENSIONS=3072
JWT_SECRET=dev_secret_change_in_production
FRONTEND_ORIGIN=http://localhost:5173
LOG_LEVEL=INFO
ENVIRONMENT=development
EOF
```

## Step 2: Start the System

```bash
# From project root
docker-compose up --build
```

**Watch the logs for:**
1. ✅ Database migrations
2. ✅ Demo data seeding
3. ✅ PDF generation (5 doctors)
4. ✅ RAG initialization
5. ✅ API server start

**Expected output:**
```
careconnect-backend | Generating doctor PDFs in: /data/doctor_pdfs
careconnect-backend | Generated: /data/doctor_pdfs/sarah_johnson.pdf
careconnect-backend | Generated: /data/doctor_pdfs/michael_chen.pdf
...
careconnect-backend | Found 5 PDF files to index
careconnect-backend | Processing: sarah_johnson.pdf...
careconnect-backend | ✓ Extracted 2845 characters from 2 pages
...
careconnect-backend | ✓ Indexing completed successfully!
careconnect-backend | INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 3: Verify System Health

### 3.1 Check API Health

```bash
curl http://localhost:8000/healthz
```

**Expected:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-31T..."
}
```

### 3.2 Check RAG Statistics

```bash
curl http://localhost:8000/api/v1/rag/stats
```

**Expected:**
```json
{
  "total_vectors": 125,
  "dimension": 3072,
  "unique_documents": 5,
  "index_path": "/data/faiss_index"
}
```

### 3.3 Verify PDF Files

```bash
docker exec careconnect-backend ls -lh /data/doctor_pdfs/
```

**Expected:**
```
-rw-r--r-- 1 root root 8.2K ... sarah_johnson.pdf
-rw-r--r-- 1 root root 8.5K ... michael_chen.pdf
-rw-r--r-- 1 root root 8.1K ... emily_rodriguez.pdf
-rw-r--r-- 1 root root 8.3K ... james_williams.pdf
-rw-r--r-- 1 root root 8.4K ... lisa_patel.pdf
```

## Step 4: Test RAG Retrieval

### 4.1 Basic Search

```bash
curl -X POST http://localhost:8000/api/v1/rag/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "query": "cardiologist",
    "top_k": 3
  }'
```

**Expected:** Returns Dr. Sarah Johnson's profile as top result.

### 4.2 Specific Specialty Search

```bash
curl -X POST http://localhost:8000/api/v1/rag/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "query": "pediatrician who speaks Spanish",
    "top_k": 2
  }'
```

**Expected:** Returns Dr. Emily Rodriguez's profile.

### 4.3 Condition-based Search

```bash
curl -X POST http://localhost:8000/api/v1/rag/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "query": "doctor for sports injuries and knee replacement",
    "top_k": 3
  }'
```

**Expected:** Returns Dr. Michael Chen's profile.

### 4.4 Filtered Search

```bash
curl -X POST http://localhost:8000/api/v1/rag/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "query": "experienced doctor",
    "top_k": 5,
    "filters": {
      "doc_type": "doctor_profile"
    }
  }'
```

**Expected:** Returns all doctor profiles ranked by relevance.

## Step 5: Test RAG Script

```bash
docker exec careconnect-backend python scripts/test_rag.py
```

**Expected output:**
```
===========================================================
RAG System Test
===========================================================

1. Checking RAG system status...
   ✓ Total vectors: 125
   ✓ Unique documents: 5
   ✓ Dimension: 3072

2. Testing semantic search...
------------------------------------------------------------

   Query 1: 'cardiologist with heart failure experience'
   Retrieving top 3 results...
   ✓ Found 3 results in 45.2ms

   Result 1:
     - Title: Dr. Sarah Johnson
     - Score: 0.8734
     - Preview: Dr. Sarah Johnson is a board-certified cardiologist...

...

===========================================================
✓ All tests completed successfully!
===========================================================
```

## Step 6: Validate Configuration

```bash
docker exec careconnect-backend python scripts/validate_rag.py
```

**Expected output:**
```
============================================================
CareConnect RAG System - Startup Validation
============================================================

🔍 Validating environment configuration...
   ✓ OPENAI_API_KEY: ********************xyz
   ✓ Embedding model: text-embedding-3-large
   ✓ Embedding dimensions: 3072
   ✓ Vector store path: /data/faiss_index

🔍 Validating directories...
   ✓ /data/faiss_index (2 files)
   ✓ /data/doctor_pdfs (5 files)

🔍 Validating PDF files...
   ✓ Found 5 PDF files:
     - sarah_johnson.pdf (8.2 KB)
     - michael_chen.pdf (8.5 KB)
     - emily_rodriguez.pdf (8.1 KB)
     - james_williams.pdf (8.3 KB)
     - lisa_patel.pdf (8.4 KB)

🔍 Validating RAG system...
   ✓ Vector store initialized
   ✓ Total vectors: 125
   ✓ Unique documents: 5
   ✓ Dimension: 3072

============================================================
✅ All validation checks passed!
============================================================
```

## Step 7: Test PDF Upload API

### 7.1 Create a Test PDF

```bash
# Create a simple test file
docker exec careconnect-backend python -c "
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate('/tmp/test_doctor.pdf', pagesize=letter)
styles = getSampleStyleSheet()
story = [Paragraph('Dr. Test Doctor', styles['Heading1']),
         Paragraph('Specialty: General Medicine', styles['Normal'])]
doc.build(story)
print('Test PDF created')
"
```

### 7.2 Upload via API

```bash
docker exec careconnect-backend curl -X POST \
  http://localhost:8000/api/v1/files/upload-pdf \
  -F "file=@/tmp/test_doctor.pdf" \
  -F "doc_type=doctor_profile"
```

**Expected:**
```json
{
  "indexed_count": 1,
  "total_chunks": 1,
  "message": "Successfully indexed 1 documents (1 chunks)"
}
```

### 7.3 Verify Upload

```bash
curl http://localhost:8000/api/v1/rag/stats
```

**Expected:** `total_vectors` increased by 1.

## Step 8: Test with Interactive API Docs

1. Open browser: http://localhost:8000/docs
2. Expand `/api/v1/rag/retrieve`
3. Click "Try it out"
4. Enter query: `"cardiologist with 15 years experience"`
5. Set `top_k`: `3`
6. Click "Execute"
7. Review results

**Expected:** See Dr. Sarah Johnson in top results.

## Step 9: Test RAG Integration with Chat Agent

### 9.1 Get Access Token

```bash
# Login as patient
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "hadihacan@gmail.com",
    "password": "password123"
  }'
```

Save the `access_token` from response.

### 9.2 Chat with Agent

```bash
curl -X POST http://localhost:8000/api/v1/agent/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "message": "I need to see a cardiologist",
    "session_id": "test-session-1"
  }'
```

**Expected:** Agent responds with information about Dr. Sarah Johnson retrieved from RAG.

## Step 10: Performance Testing

### 10.1 Measure Retrieval Speed

```bash
docker exec careconnect-backend python -c "
import asyncio
import time
from app.services.rag_service import RAGService

async def test():
    rag = RAGService()
    times = []
    for i in range(10):
        start = time.perf_counter()
        await rag.retrieve('cardiologist', top_k=5)
        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)
        print(f'Query {i+1}: {elapsed:.1f}ms')
    
    print(f'\nAverage: {sum(times)/len(times):.1f}ms')
    print(f'Min: {min(times):.1f}ms')
    print(f'Max: {max(times):.1f}ms')

asyncio.run(test())
"
```

**Expected:**
```
Query 1: 82.3ms
Query 2: 45.1ms
Query 3: 43.8ms
...
Average: 47.2ms
Min: 42.1ms
Max: 82.3ms
```

### 10.2 Test Different Query Types

```bash
docker exec careconnect-backend python -c "
import asyncio
from app.services.rag_service import RAGService

async def test():
    rag = RAGService()
    queries = [
        'cardiologist',
        'pediatrician spanish',
        'orthopedic knee surgery',
        'dermatologist skin cancer',
        'internal medicine diabetes'
    ]
    
    for query in queries:
        result = await rag.retrieve(query, top_k=1)
        if result.chunks:
            print(f'{query:30} -> {result.chunks[0].doc_title}')

asyncio.run(test())
"
```

## Step 11: Test Error Handling

### 11.1 Upload Invalid File

```bash
echo "Not a PDF" > /tmp/test.txt
docker exec careconnect-backend curl -X POST \
  http://localhost:8000/api/v1/files/upload-pdf \
  -F "file=@/tmp/test.txt"
```

**Expected:** HTTP 400 error about file type.

### 11.2 Query Empty Index

```bash
# Delete index
docker exec careconnect-backend rm -rf /data/faiss_index/*

# Try to query
curl -X POST http://localhost:8000/api/v1/rag/retrieve \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "top_k": 3}'
```

**Expected:** Returns empty results gracefully.

### 11.3 Restore Index

```bash
docker exec careconnect-backend python scripts/index_pdfs.py --replace
```

## Step 12: Load Testing (Optional)

```bash
# Install Apache Bench
# Then run:
ab -n 100 -c 10 -p query.json -T application/json \
  http://localhost:8000/api/v1/rag/retrieve
```

Where `query.json` contains:
```json
{"query": "cardiologist", "top_k": 5}
```

## Troubleshooting

### Issue: No PDFs generated

```bash
docker exec careconnect-backend python scripts/generate_doctor_pdfs.py
docker exec careconnect-backend ls /data/doctor_pdfs/
```

### Issue: RAG not initialized

```bash
docker exec careconnect-backend python scripts/init_rag.py
```

### Issue: Slow queries

Check OpenAI API status and rate limits:
```bash
docker logs careconnect-backend | grep -i "rate limit"
```

### Issue: Empty results

Verify documents are indexed:
```bash
curl http://localhost:8000/api/v1/rag/stats
```

## Success Criteria

✅ All 5 doctor PDFs generated  
✅ PDFs successfully indexed  
✅ RAG stats show 120+ vectors  
✅ Retrieval returns relevant results  
✅ Query latency < 100ms  
✅ Upload API works  
✅ Validation script passes  
✅ Test script completes  
✅ Agent can use RAG for recommendations  

## Next Steps

- Test in production environment
- Add more doctor profiles
- Monitor performance metrics
- Optimize chunk size/overlap
- Implement caching if needed
- Add more document types

---

**All tests passing?** 🎉 Your RAG system is fully operational!

For more information, see:
- [RAG System Documentation](./RAG_SYSTEM.md)
- [RAG Quick Start Guide](./RAG_QUICKSTART.md)
