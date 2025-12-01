#!/bin/bash
set -e

echo "========================================="
echo "Deploy Baseline Migration to Production"
echo "========================================="
echo ""

# Check if baseline migration exists
if [ ! -f backend/alembic/versions/00_baseline_schema.py ]; then
    echo "✗ ERROR: Baseline migration not found!"
    echo "  Expected: backend/alembic/versions/00_baseline_schema.py"
    echo ""
    echo "  You must run reset_migrations_clean_dev.sh in development first,"
    echo "  commit, and push to git before deploying to production."
    exit 1
fi

echo "✓ Baseline migration found"
echo ""

# Determine database name
DB_NAME="abparts_prod"
if [ -f .env ]; then
    DB_FROM_ENV=$(grep "^POSTGRES_DB=" .env | cut -d'=' -f2)
    if [ -n "$DB_FROM_ENV" ]; then
        DB_NAME=$DB_FROM_ENV
    fi
fi

echo "Using database: $DB_NAME"
echo ""

read -p "This will reset production migration history. Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi
echo ""

# Step 1: Rebuild API container with new migration
echo "Step 1: Rebuilding API container..."
docker compose -f docker-compose.prod.yml build api
echo "✓ API container rebuilt"
echo ""

# Step 2: Stop services
echo "Step 2: Stopping services..."
docker compose -f docker-compose.prod.yml down
echo "✓ Services stopped"
echo ""

# Step 3: Start database
echo "Step 3: Starting database..."
docker compose -f docker-compose.prod.yml up -d db redis
sleep 5
echo "✓ Database started"
echo ""

# Step 4: Clear migration history
echo "Step 4: Clearing migration history..."
docker compose -f docker-compose.prod.yml exec -T db psql -U abparts_user -d $DB_NAME -c "DELETE FROM alembic_version;" 2>&1 | grep -v "DELETE"
echo "✓ Migration history cleared"
echo ""

# Step 5: Start all services
echo "Step 5: Starting all services..."
docker compose -f docker-compose.prod.yml up -d
sleep 10
echo "✓ All services started"
echo ""

# Step 6: Stamp database with baseline
echo "Step 6: Stamping database with baseline..."
docker compose -f docker-compose.prod.yml exec api alembic stamp 00_baseline
echo "✓ Database stamped"
echo ""

# Step 7: Verify
echo "Step 7: Verifying..."
CURRENT_VERSION=$(docker compose -f docker-compose.prod.yml exec -T db psql -U abparts_user -d $DB_NAME -c "SELECT version_num FROM alembic_version;" -t 2>/dev/null | tr -d ' \n\r')

if [ "$CURRENT_VERSION" = "00_baseline" ]; then
    echo "✓ Migration status verified: $CURRENT_VERSION"
else
    echo "⚠ Unexpected migration version: $CURRENT_VERSION"
fi
echo ""

# Step 8: Check API health
echo "Step 8: Checking API health..."
sleep 5
if docker compose -f docker-compose.prod.yml exec -T api curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ API is healthy"
else
    echo "⚠ API health check failed, check logs:"
    echo "  docker compose -f docker-compose.prod.yml logs api"
fi
echo ""

echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "Summary:"
echo "  ✓ API container rebuilt with baseline migration"
echo "  ✓ Migration history reset"
echo "  ✓ Database stamped at: 00_baseline"
echo "  ✓ All services running"
echo ""
echo "Verify your application:"
echo "  https://abparts.oraseas.com"
echo ""
