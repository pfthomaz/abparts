#!/bin/bash

set -e  # Exit on error

echo "========================================="
echo "Part Usage Fix - PRODUCTION (via Alembic)"
echo "========================================="
echo ""
echo "⚠️  WARNING: This will modify the PRODUCTION database!"
echo ""
echo "This will:"
echo "1. Backup production database"
echo "2. Run Alembic migration to add updated_at columns"
echo "3. Rebuild and restart services"
echo ""

read -p "Are you sure you want to deploy to PRODUCTION? (yes/no) " -r
echo
if [[ ! $REPLY == "yes" ]]
then
    echo "Cancelled. (You must type 'yes' to confirm)"
    exit 1
fi

echo ""
echo "========================================="
echo "Step 1: Backup Production Database"
echo "========================================="
echo ""

BACKUP_FILE="backup_before_alembic_updated_at_$(date +%Y%m%d_%H%M%S).sql"
echo "Creating backup: $BACKUP_FILE"

docker compose -f docker-compose.prod.yml exec -T db pg_dump -U abparts_user abparts_prod > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "✓ Backup created: $BACKUP_FILE"
else
    echo "✗ Backup failed!"
    exit 1
fi

echo ""
echo "========================================="
echo "Step 2: Check Current Migration Status"
echo "========================================="
echo ""

echo "Current Alembic version:"
docker compose -f docker-compose.prod.yml exec api alembic current

echo ""
echo "========================================="
echo "Step 3: Run Alembic Migration"
echo "========================================="
echo ""

echo "Running: alembic upgrade head"
docker compose -f docker-compose.prod.yml exec api alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✓ Migration successful"
else
    echo "✗ Migration failed!"
    echo "Restore from backup: $BACKUP_FILE"
    exit 1
fi

echo ""
echo "New Alembic version:"
docker compose -f docker-compose.prod.yml exec api alembic current

echo ""
echo "========================================="
echo "Step 4: Rebuild Services"
echo "========================================="
echo ""

echo "Rebuilding API..."
docker compose -f docker-compose.prod.yml build api

echo "Rebuilding Frontend..."
docker compose -f docker-compose.prod.yml build web

echo ""
echo "========================================="
echo "Step 5: Restart Services"
echo "========================================="
echo ""

echo "Restarting services..."
docker compose -f docker-compose.prod.yml up -d

echo "Waiting for services to start..."
sleep 10

echo ""
echo "========================================="
echo "Step 6: Verify Deployment"
echo "========================================="
echo ""

# Check API
if docker compose -f docker-compose.prod.yml exec api curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ API is running"
else
    echo "⚠ API health check failed"
fi

# Check database
echo ""
echo "Verifying database changes..."
docker compose -f docker-compose.prod.yml exec -T db psql -U abparts_user -d abparts_prod << 'EOSQL'
SELECT 
    table_name,
    column_name
FROM information_schema.columns
WHERE column_name = 'updated_at'
AND table_name IN (
    'transactions',
    'customer_orders',
    'customer_order_items',
    'supplier_orders',
    'supplier_order_items',
    'part_usage',
    'part_usage_records',
    'part_usage_items',
    'machine_sales',
    'part_order_requests',
    'part_order_items'
)
ORDER BY table_name;
EOSQL

echo ""
echo "Checking triggers:"
docker compose -f docker-compose.prod.yml exec -T db psql -U abparts_user -d abparts_prod << 'EOSQL'
SELECT 
    trigger_name,
    event_object_table
FROM information_schema.triggers
WHERE trigger_name LIKE 'update_%_updated_at'
ORDER BY event_object_table;
EOSQL

echo ""
echo "========================================="
echo "✓ PRODUCTION DEPLOYMENT COMPLETE"
echo "========================================="
echo ""
echo "Backup saved: $BACKUP_FILE"
echo ""
echo "What was deployed:"
echo "  - Alembic migration: 01_add_updated_at"
echo "  - Added updated_at columns to 11 tables"
echo "  - Added auto-update triggers"
echo "  - Updated UI to reload after edits"
echo ""
echo "Monitor logs:"
echo "  docker compose -f docker-compose.prod.yml logs -f api"
echo "  docker compose -f docker-compose.prod.yml logs -f web"
echo ""
echo "If issues occur, restore from backup:"
echo "  docker compose -f docker-compose.prod.yml exec -T db psql -U abparts_user -d abparts_prod < $BACKUP_FILE"
echo ""
echo "Or rollback migration:"
echo "  docker compose -f docker-compose.prod.yml exec api alembic downgrade -1"
echo ""
