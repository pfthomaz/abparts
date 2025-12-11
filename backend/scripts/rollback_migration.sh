#!/bin/bash

# Safe migration rollback script
# Usage: ./rollback_migration.sh [steps_back]

set -e

STEPS_BACK=${1:-1}

echo "=== ABParts Migration Rollback Script ==="
echo "This will rollback $STEPS_BACK migration(s)."
echo ""

# Safety check
read -p "Are you sure you want to rollback migrations? (type 'yes' to continue): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Rollback cancelled."
    exit 1
fi

echo ""
echo "Step 1: Creating backup before rollback..."
./scripts/backup_db.sh ${ENVIRONMENT:-development}

echo ""
echo "Step 2: Checking current migration status..."
docker-compose exec api alembic current

echo ""
echo "Step 3: Showing rollback SQL (dry run)..."
docker-compose exec api alembic downgrade -$STEPS_BACK --sql

echo ""
read -p "Do you want to proceed with the rollback? (type 'yes' to continue): " confirm2
if [ "$confirm2" != "yes" ]; then
    echo "Rollback cancelled."
    exit 1
fi

echo ""
echo "Step 4: Performing rollback..."
docker-compose exec api alembic downgrade -$STEPS_BACK

echo ""
echo "Step 5: Verifying new migration status..."
docker-compose exec api alembic current

echo ""
echo "Step 6: Running basic API health check..."
curl -f http://localhost:8000/health || echo "Warning: Health check failed"

echo ""
echo "=== Rollback completed successfully! ==="
echo "Please test your application thoroughly."