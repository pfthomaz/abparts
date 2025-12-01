#!/bin/bash

set -e  # Exit on error

echo "========================================="
echo "Part Usage Fix - PRODUCTION Deployment"
echo "========================================="
echo ""
echo "⚠️  WARNING: This will modify the PRODUCTION database!"
echo ""
echo "This will:"
echo "1. Add updated_at columns to 11 tables"
echo "2. Add auto-update triggers"
echo "3. Update backend code"
echo "4. Rebuild and restart services"
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

BACKUP_FILE="backup_before_updated_at_$(date +%Y%m%d_%H%M%S).sql"
echo "Creating backup: $BACKUP_FILE"

docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U abparts_user abparts_prod > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "✓ Backup created: $BACKUP_FILE"
else
    echo "✗ Backup failed!"
    exit 1
fi

echo ""
echo "========================================="
echo "Step 2: Apply Database Migration"
echo "========================================="
echo ""

docker-compose -f docker-compose.prod.yml exec -T db psql -U abparts_user -d abparts_prod << 'EOSQL'

-- Create the trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Helper function
CREATE OR REPLACE FUNCTION safe_add_updated_at(table_name TEXT)
RETURNS TEXT AS $$
DECLARE
    table_exists BOOLEAN;
    column_exists BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE tables.table_name = $1
    ) INTO table_exists;
    
    IF NOT table_exists THEN
        RETURN 'SKIPPED - Table does not exist: ' || table_name;
    END IF;
    
    SELECT EXISTS (
        SELECT FROM information_schema.columns 
        WHERE columns.table_name = $1 
        AND column_name = 'updated_at'
    ) INTO column_exists;
    
    IF column_exists THEN
        RETURN 'SKIPPED - Column already exists: ' || table_name;
    END IF;
    
    EXECUTE format('ALTER TABLE %I ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL', table_name);
    EXECUTE format('DROP TRIGGER IF EXISTS update_%I_updated_at ON %I', table_name, table_name);
    EXECUTE format('CREATE TRIGGER update_%I_updated_at BEFORE UPDATE ON %I FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()', table_name, table_name);
    
    RETURN 'SUCCESS - Added updated_at to: ' || table_name;
END;
$$ language 'plpgsql';

-- Apply to all tables
SELECT safe_add_updated_at('transactions');
SELECT safe_add_updated_at('customer_orders');
SELECT safe_add_updated_at('customer_order_items');
SELECT safe_add_updated_at('supplier_orders');
SELECT safe_add_updated_at('supplier_order_items');
SELECT safe_add_updated_at('part_usage');
SELECT safe_add_updated_at('part_usage_records');
SELECT safe_add_updated_at('part_usage_items');
SELECT safe_add_updated_at('machine_sales');
SELECT safe_add_updated_at('part_order_requests');
SELECT safe_add_updated_at('part_order_items');

DROP FUNCTION safe_add_updated_at(TEXT);

-- Verify
\echo 'Tables with updated_at:'
SELECT table_name FROM information_schema.columns
WHERE column_name = 'updated_at'
AND table_name IN (
    'transactions', 'customer_orders', 'customer_order_items',
    'supplier_orders', 'supplier_order_items', 'part_usage',
    'part_usage_records', 'part_usage_items', 'machine_sales',
    'part_order_requests', 'part_order_items'
)
ORDER BY table_name;

EOSQL

if [ $? -eq 0 ]; then
    echo "✓ Database migration successful"
else
    echo "✗ Migration failed!"
    echo "Restore from backup: $BACKUP_FILE"
    exit 1
fi

echo ""
echo "========================================="
echo "Step 3: Rebuild Services"
echo "========================================="
echo ""

echo "Rebuilding API..."
docker-compose -f docker-compose.prod.yml build api

echo "Rebuilding Frontend..."
docker-compose -f docker-compose.prod.yml build web

echo ""
echo "========================================="
echo "Step 4: Restart Services"
echo "========================================="
echo ""

echo "Restarting services..."
docker-compose -f docker-compose.prod.yml up -d

echo "Waiting for services to start..."
sleep 10

echo ""
echo "========================================="
echo "Step 5: Verify Deployment"
echo "========================================="
echo ""

# Check API
if docker-compose -f docker-compose.prod.yml exec api curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ API is running"
else
    echo "⚠ API health check failed"
fi

# Check database
echo ""
echo "Verifying database changes..."
docker-compose -f docker-compose.prod.yml exec -T db psql -U abparts_user -d abparts_prod -c "SELECT COUNT(*) as tables_with_updated_at FROM information_schema.columns WHERE column_name = 'updated_at' AND table_name IN ('transactions', 'customer_orders', 'part_usage_records');"

echo ""
echo "========================================="
echo "✓ PRODUCTION DEPLOYMENT COMPLETE"
echo "========================================="
echo ""
echo "Backup saved: $BACKUP_FILE"
echo ""
echo "What was deployed:"
echo "  - Added updated_at columns to 11 tables"
echo "  - Added auto-update triggers"
echo "  - Updated UI to reload after edits"
echo ""
echo "Monitor logs:"
echo "  docker-compose -f docker-compose.prod.yml logs -f api"
echo "  docker-compose -f docker-compose.prod.yml logs -f web"
echo ""
echo "If issues occur, restore from backup:"
echo "  docker-compose -f docker-compose.prod.yml exec -T db psql -U abparts_user -d abparts_prod < $BACKUP_FILE"
echo ""
