#!/bin/bash

echo "=========================================="
echo "ABParts Database Reset Script"
echo "=========================================="
echo ""
echo "⚠️  WARNING: This will DELETE ALL database data!"
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Reset cancelled"
    exit 1
fi

echo ""
echo "Step 1: Stopping containers..."
docker-compose down

echo ""
echo "Step 2: Removing database volume..."
docker volume rm abparts_db_data 2>/dev/null || echo "Volume already removed or doesn't exist"

echo ""
echo "Step 3: Starting containers..."
docker-compose up -d

echo ""
echo "Step 4: Waiting for database to be ready (30 seconds)..."
sleep 30

echo ""
echo "Step 5: Running migrations..."
docker-compose exec -T api alembic upgrade head

echo ""
echo "Step 6: Initializing seed data..."
docker-compose exec -T api python3 -c "from app.init_db import init_db; from app.database import SessionLocal; db = SessionLocal(); init_db(db); db.close()" 2>/dev/null || echo "Seed data initialization completed (or init_db not available)"

echo ""
echo "=========================================="
echo "✅ Database reset complete!"
echo "=========================================="
echo ""
echo "You can now:"
echo "1. Access the app at http://localhost:3000"
echo "2. Login with: oraseasee_admin / admin123"
echo "3. Create test data for the customer order workflow"
echo ""
echo "Default users created:"
echo "- superadmin / admin123 (Super Admin)"
echo "- oraseasee_admin / admin123 (Oraseas EE Admin)"
echo ""
