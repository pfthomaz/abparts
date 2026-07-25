#!/bin/bash

# Production Configuration Verification Script

echo "🔍 Verifying Production Configuration..."
echo ""

# Check .env file
if [ -f .env ]; then
    echo "✓ .env file exists"
    echo ""
    echo "Database Configuration:"
    grep "DATABASE" .env | grep -v "PASSWORD" || echo "⚠️  No DATABASE variables found"
    echo ""
    
    # Check if using production database
    if grep -q "abparts_prod" .env; then
        echo "✓ Using production database (abparts_prod)"
    else
        echo "⚠️  WARNING: Not using abparts_prod database!"
        echo "   Current database:"
        grep "POSTGRES_DB" .env || echo "   POSTGRES_DB not set"
    fi
else
    echo "❌ .env file not found!"
fi

echo ""
echo "---"
echo ""

# Check docker-compose.prod.yml
if [ -f docker-compose.prod.yml ]; then
    echo "✓ docker-compose.prod.yml exists"
else
    echo "⚠️  docker-compose.prod.yml not found"
fi

echo ""
echo "---"
echo ""

# Check if containers are running
echo "Current Docker Containers:"
docker compose ps

echo ""
echo "---"
echo ""

# Check database migrations status
echo "Checking if database migrations are needed..."
echo "(This will show pending migrations if any)"
echo ""

# Try to check migration status
if docker compose ps | grep -q "api.*Up"; then
    echo "API container is running, checking migrations..."
    docker compose exec api alembic current 2>/dev/null || echo "⚠️  Could not check migration status (API may not be running)"
else
    echo "⚠️  API container not running - cannot check migrations"
fi

echo ""
echo "---"
echo ""
echo "Summary:"
echo "1. Verify .env uses POSTGRES_DB=abparts_prod"
echo "2. Check if any migrations need to be run"
echo "3. Backup database before restarting if needed"
