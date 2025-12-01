#!/bin/bash

echo "========================================="
echo "Part Usage System Fix"
echo "========================================="
echo ""
echo "This script will:"
echo "1. Add updated_at columns to all tables"
echo "2. Add triggers to auto-update timestamps"
echo "3. Fix the part usage update logic"
echo "4. Restart services"
echo ""

read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

echo ""
echo "Step 1: Adding updated_at columns to database..."
echo "---------------------------------------------"

docker-compose exec -T db psql -U abparts_user -d abparts_dev << 'EOF'

-- Create the trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to add updated_at to a table
CREATE OR REPLACE FUNCTION add_updated_at_to_table(table_name TEXT)
RETURNS void AS $$
DECLARE
    column_exists BOOLEAN;
BEGIN
    -- Check if column exists
    SELECT EXISTS (
        SELECT FROM information_schema.columns 
        WHERE table_name = $1 
        AND column_name = 'updated_at'
    ) INTO column_exists;
    
    IF NOT column_exists THEN
        -- Add the column
        EXECUTE format('ALTER TABLE %I ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL', table_name);
        
        -- Create trigger
        EXECUTE format('DROP TRIGGER IF EXISTS update_%I_updated_at ON %I', table_name, table_name);
        EXECUTE format('CREATE TRIGGER update_%I_updated_at BEFORE UPDATE ON %I FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()', table_name, table_name);
        
        RAISE NOTICE 'Added updated_at to %', table_name;
    ELSE
        RAISE NOTICE 'Skipped % - updated_at already exists', table_name;
    END IF;
END;
$$ language 'plpgsql';

-- Add updated_at to all tables that need it
SELECT add_updated_at_to_table('transactions');
SELECT add_updated_at_to_table('customer_orders');
SELECT add_updated_at_to_table('customer_order_items');
SELECT add_updated_at_to_table('supplier_orders');
SELECT add_updated_at_to_table('supplier_order_items');
SELECT add_updated_at_to_table('part_usage');
SELECT add_updated_at_to_table('part_usage_records');
SELECT add_updated_at_to_table('part_usage_items');
SELECT add_updated_at_to_table('machine_sales');
SELECT add_updated_at_to_table('part_order_requests');
SELECT add_updated_at_to_table('part_order_items');

-- Clean up
DROP FUNCTION add_updated_at_to_table(TEXT);

-- Verify
SELECT 
    table_name,
    column_name,
    data_type
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

EOF

echo ""
echo "✓ Database updated"
echo ""

echo "Step 2: Restarting API to load new model definitions..."
echo "---------------------------------------------"
docker-compose restart api
sleep 5
echo "✓ API restarted"
echo ""

echo "Step 3: Rebuilding frontend..."
echo "---------------------------------------------"
docker-compose build web
docker-compose up -d web
sleep 5
echo "✓ Frontend rebuilt"
echo ""

echo "========================================="
echo "✓ Fix Complete!"
echo "========================================="
echo ""
echo "What was done:"
echo "- Added updated_at columns to 11 tables"
echo "- Added auto-update triggers"
echo "- Updated Transaction model"
echo "- Restarted services"
echo ""
echo "Verify the fix:"
echo "1. Check database:"
echo "   docker-compose exec db psql -U abparts_user -d abparts_dev -c \"\\d transactions\""
echo ""
echo "2. Test part usage edit:"
echo "   - Open machine details"
echo "   - Edit a part usage quantity"
echo "   - Check that inventory updates"
echo ""
echo "3. Check logs:"
echo "   docker-compose logs api | tail -50"
echo ""
