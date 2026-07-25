#!/bin/bash
# Fix Alembic migration detection issue

echo "=== Fixing Migration Detection ==="

# Step 1: Clear Python cache in migrations directory
echo "1. Clearing Python cache..."
docker compose exec api rm -rf /app/alembic/versions/__pycache__

# Step 2: Restart API container to reload modules
echo "2. Restarting API container..."
docker compose restart api

# Wait for API to be ready
echo "3. Waiting for API to start..."
sleep 5

# Step 3: Check what Alembic sees
echo "4. Checking Alembic history..."
docker compose exec api alembic history

echo ""
echo "5. Checking current migration..."
docker compose exec api alembic current

echo ""
echo "6. Checking available heads..."
docker compose exec api alembic heads

echo ""
echo "=== Ready to run migration ==="
echo "Run: docker compose exec api alembic upgrade head"
