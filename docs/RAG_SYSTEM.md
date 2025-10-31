# RAG System Documentation

## Overview

The CareConnect RAG (Retrieval-Augmented Generation) system enables intelligent document retrieval and semantic search. It's designed to index and search through doctor profiles, medical documents, FAQs, and other healthcare-related content.

## Architecture

### Components

1. **Vector Store**: FAISS-based vector database for efficient similarity search
2. **Embeddings**: OpenAI's text-embedding-3-large model (3072 dimensions)
3. **PDF Parser**: Extracts text from PDF documents
4. **Document Chunking**: Splits large documents into manageable chunks with overlap
5. **RAG Service**: Orchestrates indexing and retrieval operations

### Data Flow

```
PDF Files → PDF Parser → Document Chunking → OpenAI Embeddings → FAISS Index
                                                                        ↓
User Query → OpenAI Embeddings → Similarity Search → Ranked Results → Agent/User
```

## Features

### 1. Automatic PDF Indexing

On container startup, the system:
- Generates dummy doctor profile PDFs (5 sample doctors)
- Automatically indexes all PDFs into the vector store
- Persists the index in a Docker volume

### 2. Document Types Supported

- **Doctor Profiles**: Comprehensive physician information including specialties, experience, education
- **Medical Documents**: General healthcare documents
- **Custom PDFs**: Upload via API endpoint

### 3. Smart Chunking

Documents are split into overlapping chunks:
- **Chunk Size**: 1000 characters
- **Overlap**: 200 characters
- **Smart Boundaries**: Attempts to break at sentence boundaries

### 4. Semantic Search

- Uses cosine similarity for relevance ranking
- Supports metadata filtering
- Configurable top-k results (1-20)

## Docker Integration

### Volumes

```yaml
volumes:
  vector_data: /data/faiss_index  # Persists vector store
  pdf_data: /data/doctor_pdfs     # Stores PDF documents
```

### Initialization Flow

The backend container runs these steps in order:

1. `alembic upgrade head` - Database migrations
2. `python scripts/seed_demo_data.py` - Seed demo data
3. `python scripts/generate_doctor_pdfs.py` - Generate doctor PDFs
4. `python scripts/init_rag.py` - Index PDFs into RAG system
5. `uvicorn app.main:app` - Start API server

## API Endpoints

### 1. Index Documents

```http
POST /api/v1/rag/index
```

**Request Body:**
```json
{
  "documents": [
    {
      "title": "Dr. John Doe",
      "content": "Full document text...",
      "metadata": {
        "specialty": "Cardiology",
        "doc_type": "doctor_profile"
      },
      "doc_type": "pdf"
    }
  ],
  "replace": false
}
```

**Response:**
```json
{
  "indexed_count": 1,
  "total_chunks": 5,
  "message": "Successfully indexed 1 documents (5 chunks)"
}
```

### 2. Retrieve Documents

```http
POST /api/v1/rag/retrieve
```

**Request Body:**
```json
{
  "query": "cardiologist with experience in heart failure",
  "top_k": 5,
  "filters": {
    "doc_type": "doctor_profile"
  }
}
```

**Response:**
```json
{
  "query": "cardiologist with experience in heart failure",
  "chunks": [
    {
      "chunk_id": "uuid",
      "doc_title": "Dr. Sarah Johnson",
      "content": "Chunk text...",
      "metadata": {
        "doc_type": "doctor_profile",
        "source": "sarah_johnson.pdf"
      },
      "score": 0.87
    }
  ],
  "retrieval_time_ms": 45.2
}
```

### 3. Get Statistics

```http
GET /api/v1/rag/stats
```

**Response:**
```json
{
  "total_vectors": 125,
  "dimension": 3072,
  "unique_documents": 5,
  "index_path": "/data/faiss_index"
}
```

### 4. Upload PDF

```http
POST /api/v1/files/upload-pdf
```

**Request:**
- Content-Type: `multipart/form-data`
- Form field: `file` (PDF file)
- Query parameter: `doc_type` (optional, default: "document")

**Response:**
```json
{
  "indexed_count": 1,
  "total_chunks": 8,
  "message": "Successfully indexed 1 documents (8 chunks)"
}
```

## CLI Scripts

### Generate Doctor PDFs

```bash
# Inside container
python scripts/generate_doctor_pdfs.py

# Output: data/doctor_pdfs/*.pdf
```

### Index PDFs

```bash
# Index all PDFs in default directory
python scripts/index_pdfs.py

# Custom directory
python scripts/index_pdfs.py --pdf-dir /path/to/pdfs

# Replace existing index
python scripts/index_pdfs.py --replace
```

### Initialize RAG

```bash
# Check and initialize if needed
python scripts/init_rag.py
```

## Sample Doctor Profiles

The system includes 5 pre-generated doctor profiles:

1. **Dr. Sarah Johnson** - Cardiology (MD, FACC)
   - 15 years experience
   - Specialties: Preventive Cardiology, Heart Failure, Cardiac Imaging

2. **Dr. Michael Chen** - Orthopedic Surgery (MD, FAAOS)
   - 20 years experience
   - Specialties: Sports Medicine, Joint Reconstruction

3. **Dr. Emily Rodriguez** - Pediatrics (MD, FAAP)
   - 12 years experience
   - Specialties: Child Development, Preventive Care

4. **Dr. James Williams** - Internal Medicine (MD, FACP)
   - 18 years experience
   - Specialties: Diabetes, Hypertension, Chronic Disease

5. **Dr. Lisa Patel** - Dermatology (MD, FAAD)
   - 10 years experience
   - Specialties: Skin Cancer, Cosmetic Dermatology

## Configuration

Environment variables in `docker-compose.yml`:

```yaml
OPENAI_API_KEY: ${OPENAI_API_KEY}
OPENAI_EMBEDDING_MODEL: text-embedding-3-large
OPENAI_EMBEDDING_DIMENSIONS: "3072"
VECTOR_STORE_PATH: /data/faiss_index
```

## Integration with Agent

The RAG system integrates with the chat agent to:

1. Retrieve relevant doctor information based on user queries
2. Provide context for appointment recommendations
3. Answer questions about physician specialties and availability

Example agent flow:
```
User: "I need a cardiologist"
  ↓
Agent queries RAG: "cardiologist"
  ↓
RAG returns: Dr. Sarah Johnson's profile
  ↓
Agent: "I recommend Dr. Sarah Johnson, a board-certified cardiologist..."
```

## Performance

- **Indexing Speed**: ~100-200 documents/second
- **Query Latency**: 40-80ms for top-5 results
- **Storage**: ~4KB per document chunk (including embeddings)

## Monitoring

Check RAG health:
```bash
curl http://localhost:8000/api/v1/rag/stats
```

View logs:
```bash
docker logs careconnect-backend | grep rag
```

## Troubleshooting

### Issue: No PDFs found

```bash
# Check PDF directory
docker exec careconnect-backend ls -la /data/doctor_pdfs

# Regenerate PDFs
docker exec careconnect-backend python scripts/generate_doctor_pdfs.py
```

### Issue: Vector store empty

```bash
# Re-index PDFs
docker exec careconnect-backend python scripts/index_pdfs.py --replace
```

### Issue: OpenAI API errors

- Verify `OPENAI_API_KEY` is set in `.env` file
- Check API quota and rate limits
- Review logs for specific error messages

## Future Enhancements

- [ ] Support for more document formats (DOCX, TXT, HTML)
- [ ] Hybrid search (keyword + semantic)
- [ ] Document version control
- [ ] Advanced filtering and faceted search
- [ ] Multi-tenancy support
- [ ] Real-time indexing via webhooks

## References

- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [OpenAI Embeddings API](https://platform.openai.com/docs/guides/embeddings)
- [RAG Pattern Best Practices](https://python.langchain.com/docs/use_cases/question_answering/)
