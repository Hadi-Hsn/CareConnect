#!/bin/bash
# Seed all demo data locally
# Run this script from the backend directory

echo "🌱 Seeding CareConnect Database..."
echo ""

# Run in Docker container
docker exec careconnect-backend python scripts/seed_providers.py
echo "✅ Providers seeded"

docker exec careconnect-backend python scripts/populate_lab_tests.py
echo "✅ Lab tests seeded"

docker exec careconnect-backend python scripts/seed_demo_data.py
echo "✅ Demo data seeded"

docker exec careconnect-backend python scripts/validate_rag.py
echo "✅ RAG validated"

docker exec careconnect-backend python scripts/check_data.py
echo "✅ Data checked"

echo ""
echo "🎉 All done! Database is ready."
