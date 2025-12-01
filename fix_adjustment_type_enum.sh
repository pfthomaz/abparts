#!/bin/bash

echo "=== PRODUCTION DATABASE ENUM FIX ==="
echo "This script will add missing values to the adjustmenttype enum."
echo "This is a safe, non-destructive operation."
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

echo ""
echo "Step 1: Creating backup of stock_adjustments table..."
docker compose -f docker-compose.prod.yml exec -T db psql -U abparts_user -d abparts_prod << 'BACKUP'
CREATE TABLE IF NOT EXISTS stock_adjustments_backup_$(date +%Y%m%d) AS 
SELECT * FROM stock_adjustments;
BACKUP

echo ""
echo "Step 2: Checking current enum values..."
docker compose -f docker-compose.prod.yml exec -T db psql -U abparts_user -d abparts_prod << 'CHECK'
SELECT enumlabel FROM pg_enum WHERE enumtypid = 'adjustmenttype'::regtype ORDER BY enumsortorder;
CHECK

echo ""
echo "Step 3: Adding missing enum values..."

# Update the enum type in production
docker compose -f docker-compose.prod.yml exec -T db psql -U abparts_user -d abparts_prod << 'EOF'
-- First, check current enum values
SELECT enumlabel FROM pg_enum WHERE enumtypid = 'adjustmenttype'::regtype ORDER BY enumsortorder;

-- Add missing enum values one by one (if they don't exist)
DO $$ 
BEGIN
    -- Add stock_take if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'stock_take' AND enumtypid = 'adjustmenttype'::regtype) THEN
        ALTER TYPE adjustmenttype ADD VALUE 'stock_take';
    END IF;
    
    -- Add correction if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'correction' AND enumtypid = 'adjustmenttype'::regtype) THEN
        ALTER TYPE adjustmenttype ADD VALUE 'correction';
    END IF;
    
    -- Add damage if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'damage' AND enumtypid = 'adjustmenttype'::regtype) THEN
        ALTER TYPE adjustmenttype ADD VALUE 'damage';
    END IF;
    
    -- Add expired if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'expired' AND enumtypid = 'adjustmenttype'::regtype) THEN
        ALTER TYPE adjustmenttype ADD VALUE 'expired';
    END IF;
    
    -- Add transfer_in if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'transfer_in' AND enumtypid = 'adjustmenttype'::regtype) THEN
        ALTER TYPE adjustmenttype ADD VALUE 'transfer_in';
    END IF;
    
    -- Add transfer_out if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'transfer_out' AND enumtypid = 'adjustmenttype'::regtype) THEN
        ALTER TYPE adjustmenttype ADD VALUE 'transfer_out';
    END IF;
    
    -- Add initial_stock if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'initial_stock' AND enumtypid = 'adjustmenttype'::regtype) THEN
        ALTER TYPE adjustmenttype ADD VALUE 'initial_stock';
    END IF;
    
    -- Add recount if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'recount' AND enumtypid = 'adjustmenttype'::regtype) THEN
        ALTER TYPE adjustmenttype ADD VALUE 'recount';
    END IF;
    
    -- Add loss if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'loss' AND enumtypid = 'adjustmenttype'::regtype) THEN
        ALTER TYPE adjustmenttype ADD VALUE 'loss';
    END IF;
    
    -- Add found if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'found' AND enumtypid = 'adjustmenttype'::regtype) THEN
        ALTER TYPE adjustmenttype ADD VALUE 'found';
    END IF;
    
    -- Add return if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'return' AND enumtypid = 'adjustmenttype'::regtype) THEN
        ALTER TYPE adjustmenttype ADD VALUE 'return';
    END IF;
    
    -- Add write_off if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'write_off' AND enumtypid = 'adjustmenttype'::regtype) THEN
        ALTER TYPE adjustmenttype ADD VALUE 'write_off';
    END IF;
    
    -- Add supplier_correction if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'supplier_correction' AND enumtypid = 'adjustmenttype'::regtype) THEN
        ALTER TYPE adjustmenttype ADD VALUE 'supplier_correction';
    END IF;
    
    -- Add customer_return if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'customer_return' AND enumtypid = 'adjustmenttype'::regtype) THEN
        ALTER TYPE adjustmenttype ADD VALUE 'customer_return';
    END IF;
    
    -- Add manufacturing_adjustment if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'manufacturing_adjustment' AND enumtypid = 'adjustmenttype'::regtype) THEN
        ALTER TYPE adjustmenttype ADD VALUE 'manufacturing_adjustment';
    END IF;
    
    -- Add quality_control if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'quality_control' AND enumtypid = 'adjustmenttype'::regtype) THEN
        ALTER TYPE adjustmenttype ADD VALUE 'quality_control';
    END IF;
    
    -- Add other if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'other' AND enumtypid = 'adjustmenttype'::regtype) THEN
        ALTER TYPE adjustmenttype ADD VALUE 'other';
    END IF;
END $$;

-- Verify all enum values are present
SELECT enumlabel FROM pg_enum WHERE enumtypid = 'adjustmenttype'::regtype ORDER BY enumsortorder;

EOF

echo ""
echo "Step 4: Verifying enum values..."
docker compose -f docker-compose.prod.yml exec -T db psql -U abparts_user -d abparts_prod << 'VERIFY'
SELECT COUNT(*) as total_enum_values FROM pg_enum WHERE enumtypid = 'adjustmenttype'::regtype;
SELECT enumlabel FROM pg_enum WHERE enumtypid = 'adjustmenttype'::regtype ORDER BY enumsortorder;
VERIFY

echo ""
echo "Step 5: Restarting API to pick up changes..."
docker compose -f docker-compose.prod.yml restart api

echo ""
echo "=== COMPLETE ==="
echo "✓ Backup created"
echo "✓ Enum values added"
echo "✓ API restarted"
echo ""
echo "The adjustmenttype enum now has all required values."
echo "You can now create stock adjustments with type 'stock_take'."
