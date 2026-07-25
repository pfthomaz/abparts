#!/bin/bash

echo "🔄 Updating Maintenance Protocols Migration..."
echo ""

# Step 1: Downgrade the old migration
echo "⬇️  Downgrading old migration..."
docker-compose exec -T api alembic downgrade 01_add_updated_at

# Step 2: Delete old migration from alembic_version if it exists
echo "🗑️  Cleaning up old migration record..."
docker-compose exec -T db psql -U abparts_user -d abparts_dev -c "DELETE FROM alembic_version WHERE version_num = 'add_maintenance_protocols';"

# Step 3: Run new migration
echo "⬆️  Running new migration with is_recurring field..."
docker-compose exec -T api alembic upgrade head

# Step 4: Verify
echo ""
echo "✅ Checking new schema..."
docker-compose exec -T db psql -U abparts_user -d abparts_dev -c "\d maintenance_protocols" | grep is_recurring

echo ""
echo "🎉 Migration updated successfully!"
echo ""
echo "Note: You'll need to recreate your sample protocols with the new field."
