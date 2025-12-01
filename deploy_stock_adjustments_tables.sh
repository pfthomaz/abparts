#!/bin/bash

echo "=== PRODUCTION: CREATE STOCK ADJUSTMENTS TABLES ==="
echo ""
echo "This script will:"
echo "1. Create the adjustmenttype enum with all values"
echo "2. Create stock_adjustments table"
echo "3. Create stock_adjustment_items table"
echo "4. Create necessary indexes"
echo ""
echo "⚠️  WARNING: This is a production database operation"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

echo ""
echo "Step 1: Backing up existing data (if any)..."
docker compose -f docker-compose.prod.yml exec -T db psql -U abparts_user -d abparts_prod << 'BACKUP'
-- Create backup tables if the tables exist
DO $$ 
BEGIN
    IF EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'stock_adjustments') THEN
        EXECUTE 'CREATE TABLE stock_adjustments_backup_' || to_char(now(), 'YYYYMMDD_HH24MISS') || ' AS SELECT * FROM stock_adjustments';
        RAISE NOTICE 'Backed up stock_adjustments table';
    END IF;
    
    IF EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'stock_adjustment_items') THEN
        EXECUTE 'CREATE TABLE stock_adjustment_items_backup_' || to_char(now(), 'YYYYMMDD_HH24MISS') || ' AS SELECT * FROM stock_adjustment_items';
        RAISE NOTICE 'Backed up stock_adjustment_items table';
    END IF;
END $$;
BACKUP

echo ""
echo "Step 2: Creating tables and enum..."
docker compose -f docker-compose.prod.yml exec -T db psql -U abparts_user -d abparts_prod < create_stock_adjustments_tables.sql

if [ $? -eq 0 ]; then
    echo ""
    echo "Step 3: Verifying table structure..."
    docker compose -f docker-compose.prod.yml exec -T db psql -U abparts_user -d abparts_prod << 'VERIFY'
-- Check tables exist
SELECT 
    tablename,
    schemaname
FROM pg_tables 
WHERE tablename IN ('stock_adjustments', 'stock_adjustment_items')
ORDER BY tablename;

-- Check enum values
SELECT 
    enumlabel,
    enumsortorder
FROM pg_enum 
WHERE enumtypid = 'adjustmenttype'::regtype 
ORDER BY enumsortorder;

-- Check indexes
SELECT 
    indexname,
    tablename
FROM pg_indexes 
WHERE tablename IN ('stock_adjustments', 'stock_adjustment_items')
ORDER BY tablename, indexname;
VERIFY

    echo ""
    echo "Step 4: Restarting API..."
    docker compose -f docker-compose.prod.yml restart api
    
    echo ""
    echo "=== SUCCESS ==="
    echo "✓ Tables created"
    echo "✓ Enum configured with all values"
    echo "✓ Indexes created"
    echo "✓ API restarted"
    echo ""
    echo "Stock adjustments feature is now ready to use!"
else
    echo ""
    echo "❌ ERROR: Failed to create tables"
    echo "Check the error messages above"
    exit 1
fi
