#!/bin/bash
# Test the stock adjustments migration

echo "=========================================="
echo "  Testing Stock Adjustments Migration"
echo "=========================================="
echo ""

# Check current migration status
echo "📋 Current migration status:"
docker-compose exec api alembic current
echo ""

# Show pending migrations
echo "📋 Pending migrations:"
docker-compose exec api alembic heads
echo ""

# Run the migration
echo "🔄 Running migration..."
docker-compose exec api alembic upgrade head

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migration completed successfully!"
    echo ""
    
    # Verify new tables exist
    echo "🔍 Verifying new structure..."
    echo ""
    echo "Checking stock_adjustments table:"
    docker-compose exec db psql -U abparts_user -d abparts_dev -c "\d stock_adjustments"
    echo ""
    echo "Checking stock_adjustment_items table:"
    docker-compose exec db psql -U abparts_user -d abparts_dev -c "\d stock_adjustment_items"
    echo ""
    echo "Checking if inventory_adjustments was dropped:"
    docker-compose exec db psql -U abparts_user -d abparts_dev -c "\dt inventory_adjustments" 2>&1 | grep -q "Did not find" && echo "✅ inventory_adjustments table dropped" || echo "⚠️  inventory_adjustments still exists"
    
else
    echo ""
    echo "❌ Migration failed!"
    echo ""
    echo "Check the error above and fix the migration file."
    exit 1
fi

echo ""
echo "=========================================="
echo "  Migration Test Complete"
echo "=========================================="
