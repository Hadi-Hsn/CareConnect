FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e ".[dev]"

# Copy application code
COPY . .

# Create data directory for SQLite database and PDFs
RUN mkdir -p /app/data /data/doctor_pdfs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/healthz || exit 1

# Run migrations and start server
# Seeding is optional: set SEED_DATABASE=true to run seed script on startup
CMD ["sh", "-c", "python -c 'import asyncio; from app.core.db import init_db; asyncio.run(init_db())' && alembic upgrade head && if [ \"$SEED_DATABASE\" = \"true\" ]; then python scripts/seed_demo_data.py; fi && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
