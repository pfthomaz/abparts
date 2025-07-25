#!/bin/bash

# Production migration script with safety checks
# Usage: ./migrate_prod.sh

set -e

echo "=== ABParts Production Migration Script ==="
echo "This script will apply database migrations to production."
echo ""

# Safety check - require explicit confirmation
read -p "Are you sure you want to run migrations on PRODUCTION? (type 'yes' to continue): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Migration cancelled."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "alembic.ini" ]; then
    echo "Error: alembic.ini not found. Please run this script from the backend directory."
    exit 1
fi

# Set production environment
export ENVIRONMENT=production

echo ""
echo "Step 1: Creating database backup..."
./scripts/backup_db.sh production

echo ""
echo "Step 2: Checking current migration status..."
docker-compose exec api alembic current

echo ""
echo "Step 3: Checking pending migrations..."
docker-compose exec api alembic show head

echo ""
echo "Step 4: Showing migration SQL (dry run)..."
docker-compose exec api alembic upgrade head --sql

echo ""
read -p "Do you want to proceed with applying these migrations? (type 'yes' to continue): " confirm2
if [ "$confirm2" != "yes" ]; then
    echo "Migration cancelled."
    exit 1
fi

echo ""
echo "Step 5: Applying migrations..."
docker-compose exec api alembic upgrade head

echo ""
echo "Step 6: Verifying migration status..."
docker-compose exec api alembic current

echo ""
echo "Step 7: Running basic API health check..."
curl -f http://localhost:8000/health || echo "Warning: Health check failed"

echo ""
echo "=== Migration completed successfully! ==="
echo "Please monitor your application logs for any issues."
echo "If you encounter problems, you can rollback using:"
echo "  docker-compose exec api alembic downgrade -1"