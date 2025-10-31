# RAG System Quick Start Guide

## Quick Start with Docker

### 1. Start the System

```bash
# Make sure you have OPENAI_API_KEY in your .env file
docker-compose up -d
```

The system will automatically:
- ✓ Generate 5 sample doctor PDFs
- ✓ Index them into the RAG system
- ✓ Start the API server

### 2. Verify RAG is Working

```bash
# Check statistics
curl http://localhost:8000/api/v1/rag/stats

# Expected output:
# {
#   "total_vectors": 125,
#   "unique_documents": 5,
#   "dimension": 3072,
#   "index_path": "/data/faiss_index"
# }
```

### 3. Test Semantic Search

```bash
# Search for a cardiologist
curl -X POST http://localhost:8000/api/v1/rag/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "query": "cardiologist with heart failure experience",
    "top_k": 3
  }'
```

## Common Use Cases

### Search for Doctors by Specialty

```bash
curl -X POST http://localhost:8000/api/v1/rag/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "query": "orthopedic surgeon for knee replacement",
    "top_k": 5,
    "filters": {"doc_type": "doctor_profile"}
  }'
```

### Upload a New Doctor PDF

```bash
curl -X POST http://localhost:8000/api/v1/files/upload-pdf \
  -F "file=@/path/to/doctor.pdf" \
  -F "doc_type=doctor_profile"
```

### Re-index All PDFs

```bash
# Inside the Docker container
docker exec careconnect-backend python scripts/index_pdfs.py --replace
```

## Testing RAG System

### Run Test Suite

```bash
docker exec careconnect-backend python scripts/test_rag.py
```

### Generate More Sample PDFs

Edit `backend/scripts/generate_doctor_pdfs.py` to add more doctors to the `DOCTORS_DATA` list, then:

```bash
docker exec careconnect-backend python scripts/generate_doctor_pdfs.py
docker exec careconnect-backend python scripts/index_pdfs.py
```

## Monitoring

### View Logs

```bash
# All logs
docker logs careconnect-backend

# RAG-specific logs
docker logs careconnect-backend | grep -i rag

# Follow logs
docker logs -f careconnect-backend
```

### Check Vector Store Files

```bash
# List vector store files
docker exec careconnect-backend ls -lh /data/faiss_index/

# List PDF files
docker exec careconnect-backend ls -lh /data/doctor_pdfs/
```

## Troubleshooting

### Problem: No vectors in the system

**Solution:**
```bash
# Check if PDFs exist
docker exec careconnect-backend ls /data/doctor_pdfs/

# If no PDFs, generate them
docker exec careconnect-backend python scripts/generate_doctor_pdfs.py

# Index PDFs
docker exec careconnect-backend python scripts/index_pdfs.py
```

### Problem: "OpenAI API key not found"

**Solution:**
1. Create `.env` file in the project root
2. Add: `OPENAI_API_KEY=sk-your-api-key-here`
3. Restart containers: `docker-compose restart backend`

### Problem: RAG queries are slow

**Possible causes:**
- Large document corpus (normal at scale)
- OpenAI API rate limits
- Network latency

**Check:**
```bash
# View retrieval times in logs
docker logs careconnect-backend | grep retrieval_time
```

## Integration with Chat Agent

The RAG system is automatically used by the chat agent for:

1. **Doctor Recommendations**: When users ask for doctors by specialty
2. **Information Retrieval**: Answering questions about doctor credentials
3. **Contextual Responses**: Providing detailed information in conversations

Example conversation:
```
User: "I need a cardiologist who treats heart failure"

Agent (uses RAG):
1. Queries: "cardiologist heart failure treatment"
2. Retrieves: Dr. Sarah Johnson's profile
3. Responds: "I recommend Dr. Sarah Johnson. She's a board-certified 
   cardiologist with 15 years of experience and specializes in heart 
   failure management..."
```

## Performance Benchmarks

Based on 5 doctor profiles (~125 chunks):

| Operation | Time |
|-----------|------|
| Index 1 PDF | ~2-3 seconds |
| Retrieve top-5 | ~40-80ms |
| Upload & index PDF | ~3-5 seconds |

## Data Persistence

All RAG data is persisted in Docker volumes:

```yaml
volumes:
  vector_data:  # FAISS index files
  pdf_data:     # Original PDF documents
```

To backup:
```bash
docker run --rm -v careconnect_vector_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/vector_store_backup.tar.gz /data
```

To restore:
```bash
docker run --rm -v careconnect_vector_data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/vector_store_backup.tar.gz -C /
```

## Advanced Configuration

### Customize Chunking

Edit `backend/app/core/vectorstore/faiss_store.py`:

```python
def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200):
    # Adjust chunk_size and overlap as needed
```

### Change Embedding Model

Update `docker-compose.yml`:

```yaml
environment:
  OPENAI_EMBEDDING_MODEL: text-embedding-3-small  # Faster, smaller
  OPENAI_EMBEDDING_DIMENSIONS: "1536"
```

Then re-index all documents.

## API Authentication

For production, protect RAG endpoints with authentication:

```python
# Add to rag.py and files.py
from app.core.security import require_admin

@router.post("/index")
async def index_documents(
    request: IndexRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin)  # Add this
):
    ...
```

## Next Steps

1. ✅ System is running
2. ✅ Sample PDFs are indexed
3. ✅ RAG is integrated with the agent
4. 🔄 Test via the chat interface
5. 🔄 Upload real doctor profiles
6. 🔄 Monitor and optimize performance

For detailed documentation, see [RAG_SYSTEM.md](./RAG_SYSTEM.md)
