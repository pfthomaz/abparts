#!/bin/bash

echo "🔄 Running Alembic migration for Maintenance Protocols..."
echo ""

# Check if containers are running
if ! docker compose ps | grep -q "api.*Up"; then
    echo "❌ Error: API container is not running"
    echo "Please start the containers with: docker compose up -d"
    exit 1
fi

# Show current migration status
echo "📊 Current migration status:"
docker compose exec -T api alembic current
echo ""

# Run the migration
echo "⬆️  Running upgrade..."
docker compose exec -T api alembic upgrade head

# Check if migration was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migration completed successfully!"
    echo ""
    echo "📋 Verifying new tables..."
    docker compose exec -T db psql -U abparts_user -d abparts_dev -c "\dt maintenance*"
    echo ""
    echo "🎉 Maintenance Protocols tables created!"
else
    echo ""
    echo "❌ Migration failed. Please check the error messages above."
    exit 1
fi
