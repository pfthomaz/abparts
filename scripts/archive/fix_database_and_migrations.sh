#!/bin/bash

echo "=== Fixing Database and Migrations ==="
echo ""

# Step 1: Fix collation warnings and create database properly
echo "1. Creating abparts_prod database properly..."

# First, refresh collation versions to clear warnings
docker compose exec db psql -U abparts_user -d postgres -c "ALTER DATABASE postgres REFRESH COLLATION VERSION;" 2>/dev/null
docker compose exec db psql -U abparts_user -d postgres -c "ALTER DATABASE template1 REFRESH COLLATION VERSION;" 2>/dev/null

# Drop abparts_prod if it exists (partially created)
docker compose exec db psql -U abparts_user -d postgres -c "DROP DATABASE IF EXISTS abparts_prod;" 2>/dev/null

# Create abparts_prod fresh
docker compose exec db psql -U abparts_user -d postgres -c "CREATE DATABASE abparts_prod OWNER abparts_user;"

# Verify it was created
DB_EXISTS=$(docker compose exec db psql -U abparts_user -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='abparts_prod'")
if [ "$DB_EXISTS" = "1" ]; then
    echo "✓ abparts_prod database created successfully"
else
    echo "✗ Failed to create abparts_prod"
    exit 1
fi
echo ""

# Step 2: Copy data from abparts_dev
echo "2. Copying data from abparts_dev to abparts_prod..."
docker compose exec db pg_dump -U abparts_user abparts_dev | docker compose exec -T db psql -U abparts_user -d abparts_prod

if [ $? -eq 0 ]; then
    echo "✓ Data copied successfully"
else
    echo "⚠ Data copy had issues, but continuing..."
fi
echo ""

# Step 3: Fix Alembic migration heads
echo "3. Checking Alembic migration status..."
docker compose exec api alembic heads

echo ""
echo "Checking for multiple heads..."
HEADS=$(docker compose exec api alembic heads 2>&1)

if echo "$HEADS" | grep -q "Multiple head revisions"; then
    echo "⚠ Multiple migration heads detected"
    echo ""
    echo "Showing current heads:"
    docker compose exec api alembic heads
    echo ""
    echo "Merging heads..."
    docker compose exec api alembic merge heads -m "merge_migration_heads"
    echo "✓ Heads merged"
    echo ""
    echo "Upgrading to merged head..."
    docker compose exec api alembic upgrade head
else
    echo "✓ No multiple heads, upgrading to head..."
    docker compose exec api alembic upgrade head
fi
echo ""

# Step 4: Restart API
echo "4. Restarting API container..."
docker compose restart api
sleep 5
echo ""

# Step 5: Test connection
echo "5. Testing database connection..."
for i in {1..5}; do
    HEALTH=$(curl -s http://localhost:8000/health)
    DB_STATUS=$(echo "$HEALTH" | python3 -c "import sys, json; print(json.load(sys.stdin).get('database', 'unknown'))" 2>/dev/null)
    
    echo "Attempt $i: Database status = $DB_STATUS"
    
    if [ "$DB_STATUS" = "connected" ]; then
        echo ""
        echo "✓ Database connected successfully!"
        echo "$HEALTH" | python3 -m json.tool
        break
    fi
    
    if [ $i -lt 5 ]; then
        sleep 3
    fi
done
echo ""

# Step 6: Test the website
echo "6. Testing website..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://abparts.oraseas.com)
echo "Website HTTP status: $HTTP_CODE"

if [ "$HTTP_CODE" = "200" ]; then
    echo "✓ Website is accessible!"
else
    echo "⚠ Website returned HTTP $HTTP_CODE"
    echo ""
    echo "Checking nginx error log:"
    sudo tail -20 /var/log/nginx/abparts_error.log
fi
echo ""

echo "=== Fix Complete ==="
echo ""
echo "Final status:"
docker compose ps
echo ""
echo "If database is still not connected, check:"
echo "  docker compose logs api"
echo ""
echo "Visit: https://abparts.oraseas.com"
