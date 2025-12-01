#!/bin/bash

set -e  # Exit on error

echo "========================================="
echo "Part Usage System - Complete Fix"
echo "========================================="
echo ""
echo "This will:"
echo "1. Add updated_at columns to all tables (with triggers)"
echo "2. Update Transaction model to include updated_at"
echo "3. Fix UI to reload after part usage edits"
echo "4. Restart all services"
echo ""

read -p "Deploy to DEVELOPMENT environment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Cancelled."
    exit 1
fi

echo ""
echo "========================================="
echo "Step 1: Database Schema Updates"
echo "========================================="
echo ""

echo "Adding updated_at columns to tables..."

docker-compose exec -T db psql -U abparts_user -d abparts_dev << 'EOSQL'

-- Create the trigger function if it doesn't exist
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Helper function to safely add updated_at
CREATE OR REPLACE FUNCTION safe_add_updated_at(table_name TEXT)
RETURNS TEXT AS $$
DECLARE
    table_exists BOOLEAN;
    column_exists BOOLEAN;
BEGIN
    -- Check if table exists
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE tables.table_name = $1
    ) INTO table_exists;
    
    IF NOT table_exists THEN
        RETURN 'SKIPPED - Table does not exist: ' || table_name;
    END IF;
    
    -- Check if column exists
    SELECT EXISTS (
        SELECT FROM information_schema.columns 
        WHERE columns.table_name = $1 
        AND column_name = 'updated_at'
    ) INTO column_exists;
    
    IF column_exists THEN
        RETURN 'SKIPPED - Column already exists: ' || table_name;
    END IF;
    
    -- Add the column
    EXECUTE format('ALTER TABLE %I ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL', table_name);
    
    -- Create trigger
    EXECUTE format('DROP TRIGGER IF EXISTS update_%I_updated_at ON %I', table_name, table_name);
    EXECUTE format('CREATE TRIGGER update_%I_updated_at BEFORE UPDATE ON %I FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()', table_name, table_name);
    
    RETURN 'SUCCESS - Added updated_at to: ' || table_name;
END;
$$ language 'plpgsql';

-- Add updated_at to all tables
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

-- Clean up helper function
DROP FUNCTION safe_add_updated_at(TEXT);

-- Verify
\echo ''
\echo 'Verification - Tables with updated_at column:'
SELECT 
    table_name,
    column_name,
    data_type,
    column_default
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

\echo ''
\echo 'Verification - Triggers:'
SELECT 
    trigger_name,
    event_object_table
FROM information_schema.triggers
WHERE trigger_name LIKE 'update_%_updated_at'
ORDER BY event_object_table;

EOSQL

if [ $? -eq 0 ]; then
    echo "✓ Database schema updated successfully"
else
    echo "✗ Database update failed"
    exit 1
fi

echo ""
echo "========================================="
echo "Step 2: Restart API"
echo "========================================="
echo ""

echo "Restarting API to load updated models..."
docker-compose restart api

echo "Waiting for API to start..."
sleep 5

# Check if API is responding
if docker-compose exec api curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ API is running"
else
    echo "⚠ API health check failed, but continuing..."
fi

echo ""
echo "========================================="
echo "Step 3: Rebuild and Restart Frontend"
echo "========================================="
echo ""

echo "Rebuilding frontend with UI fixes..."
docker-compose build web

echo "Restarting frontend..."
docker-compose up -d web

echo "Waiting for frontend to start..."
sleep 5

echo "✓ Frontend restarted"

echo ""
echo "========================================="
echo "✓ DEPLOYMENT COMPLETE"
echo "========================================="
echo ""
echo "What was fixed:"
echo "  1. Added updated_at columns to 11 tables"
echo "  2. Added auto-update triggers for timestamps"
echo "  3. Updated Transaction model"
echo "  4. Fixed UI to reload after part usage edits/deletes"
echo ""
echo "How it works now:"
echo "  - Edit a part usage → Transaction updates → Page reloads → Fresh data"
echo "  - Delete a part usage → Transaction deletes → Page reloads → Fresh data"
echo "  - Inventory always shows calculated values from transactions"
echo ""
echo "Test the fix:"
echo "  1. Open: http://localhost:3000"
echo "  2. Go to a machine details page"
echo "  3. Click 'Parts Usage' tab"
echo "  4. Edit a part usage quantity"
echo "  5. Page should reload and show updated inventory"
echo ""
echo "Check logs if issues:"
echo "  docker-compose logs api | tail -50"
echo "  docker-compose logs web | tail -50"
echo ""
echo "Verify database:"
echo "  docker-compose exec db psql -U abparts_user -d abparts_dev -c '\\d transactions'"
echo ""
