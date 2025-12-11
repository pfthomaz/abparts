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
docker compose -f docker-compose.prod.yml exec -T db psql -U abparts_user -d abparts_prod << 'CREATETABLES'
-- Create stock adjustments tables in production

BEGIN;

-- Create the adjustmenttype enum with all values
DO $$ 
BEGIN
    -- Drop and recreate the enum if it exists
    DROP TYPE IF EXISTS adjustmenttype CASCADE;
    
    CREATE TYPE adjustmenttype AS ENUM (
        'increase',
        'decrease',
        'stock_take',
        'correction',
        'damage',
        'expired',
        'transfer_in',
        'transfer_out',
        'initial_stock',
        'recount',
        'loss',
        'found',
        'return',
        'write_off',
        'supplier_correction',
        'customer_return',
        'manufacturing_adjustment',
        'quality_control',
        'other'
    );
END $$;

-- Create stock_adjustments table
CREATE TABLE IF NOT EXISTS stock_adjustments (
    id UUID PRIMARY KEY,
    warehouse_id UUID NOT NULL REFERENCES warehouses(id) ON DELETE CASCADE,
    adjustment_type adjustmenttype NOT NULL,
    adjustment_date TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    reason TEXT NOT NULL,
    reason_code VARCHAR(50),
    notes TEXT,
    user_id UUID NOT NULL REFERENCES users(id),
    total_items_adjusted INTEGER DEFAULT 0,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create stock_adjustment_items table
CREATE TABLE IF NOT EXISTS stock_adjustment_items (
    id UUID PRIMARY KEY,
    stock_adjustment_id UUID NOT NULL REFERENCES stock_adjustments(id) ON DELETE CASCADE,
    part_id UUID NOT NULL REFERENCES parts(id) ON DELETE CASCADE,
    quantity_before NUMERIC(10, 3) NOT NULL,
    quantity_after NUMERIC(10, 3) NOT NULL,
    quantity_change NUMERIC(10, 3) NOT NULL,
    reason TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_stock_adjustments_warehouse_id ON stock_adjustments(warehouse_id);
CREATE INDEX IF NOT EXISTS idx_stock_adjustments_user_id ON stock_adjustments(user_id);
CREATE INDEX IF NOT EXISTS idx_stock_adjustments_adjustment_date ON stock_adjustments(adjustment_date);
CREATE INDEX IF NOT EXISTS idx_stock_adjustments_adjustment_type ON stock_adjustments(adjustment_type);

CREATE INDEX IF NOT EXISTS idx_stock_adjustment_items_stock_adjustment_id ON stock_adjustment_items(stock_adjustment_id);
CREATE INDEX IF NOT EXISTS idx_stock_adjustment_items_part_id ON stock_adjustment_items(part_id);

-- Verify tables were created
SELECT 
    'stock_adjustments' as table_name,
    COUNT(*) as row_count
FROM stock_adjustments
UNION ALL
SELECT 
    'stock_adjustment_items' as table_name,
    COUNT(*) as row_count
FROM stock_adjustment_items;

COMMIT;
CREATETABLES

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
    COUNT(*) as total_enum_values
FROM pg_enum 
WHERE enumtypid = 'adjustmenttype'::regtype;

-- Check indexes
SELECT 
    COUNT(*) as total_indexes
FROM pg_indexes 
WHERE tablename IN ('stock_adjustments', 'stock_adjustment_items');
VERIFY

    echo ""
    echo "Step 4: Restarting API..."
    docker compose -f docker-compose.prod.yml restart api
    
    echo ""
    echo "=== SUCCESS ==="
    echo "✓ Tables created"
    echo "✓ Enum configured with all 19 values"
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
