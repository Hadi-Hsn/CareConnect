#!/bin/bash
# Exit on error for critical steps, but we'll handle some non-critical steps explicitly
set -e

echo "=================================================="
echo "  CareConnect Setup - Database Initialization"
echo "=================================================="
echo ""

# Wait for database to be ready
echo "⏳ Waiting for database..."
while ! nc -z db 5432; do
  sleep 1
done
echo "✅ Database is ready!"
echo ""

# Run database migrations
echo "🔄 Running database migrations..."
cd /app/backend
alembic upgrade head
echo "✅ Migrations completed!"
echo ""

# Seed demo data
echo "🌱 Seeding demo data..."
cd /app/setup
python scripts/seed_demo_data.py || echo "⚠️  Seed script failed (non-fatal). Continuing setup."
echo ""

# Generate doctor PDFs
echo "📄 Generating doctor PDFs..."
python scripts/generate_doctor_pdfs.py || echo "⚠️  PDF generation failed (non-fatal). Continuing setup."
echo ""

# Index PDFs into RAG
echo "🔍 Indexing PDFs into RAG system..."
python scripts/index_pdfs.py || echo "⚠️  PDF indexing failed (non-fatal). Continuing setup."
echo ""

echo "=================================================="
echo "  ✅ Setup completed successfully!"
echo "=================================================="
echo ""
echo "Demo credentials:"
echo "  Patient: hadihacan@gmail.com / password123"
echo "  Admin:   hadi.wmail@gmail.com / admin123"
echo ""
