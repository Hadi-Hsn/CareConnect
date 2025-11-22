#!/bin/bash
set -e

echo "🚀 Starting CareConnect Backend..."

# Wait for ChromaDB to be ready
echo "⏳ Waiting for ChromaDB..."
until curl -f http://chromadb:8000/api/v1/heartbeat > /dev/null 2>&1; do
    echo "   ChromaDB is unavailable - sleeping"
    sleep 2
done
echo "✅ ChromaDB is ready!"

# Run database migrations
echo "🔄 Running database migrations..."
alembic upgrade head

# Check if database is empty (no users)
echo "🔍 Checking if database needs seeding..."
USER_COUNT=$(python -c "
import sqlite3
conn = sqlite3.connect('/app/data/careconnect.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM users')
count = cursor.fetchone()[0]
conn.close()
print(count)
")

if [ "$USER_COUNT" -eq "0" ]; then
    echo "📊 Database is empty, seeding demo data..."
    
    # Seed providers
    echo "   👨‍⚕️ Seeding providers..."
    python scripts/seed_providers.py
    
    # Seed lab tests
    echo "   🧪 Seeding lab tests..."
    python scripts/populate_lab_tests.py
    
    # Seed demo data (users, appointments, etc.)
    echo "   🎭 Seeding demo data..."
    python scripts/seed_demo_data.py
    
    # Validate RAG
    echo "   🔍 Validating RAG system..."
    python scripts/validate_rag.py || echo "⚠️  RAG validation failed, but continuing..."
    
    # Check data
    echo "   ✔️  Checking seeded data..."
    python scripts/check_data.py
    
    echo "✅ Database seeding complete!"
else
    echo "ℹ️  Database already has $USER_COUNT users, skipping seed"
fi

# Start the application
echo "🎉 Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
