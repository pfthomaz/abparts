#!/bin/bash

echo "=== Setting up Production Database ==="
echo ""

# Kill process on port 8000
echo "1. Clearing port 8000..."
sudo kill -9 $(sudo lsof -t -i:8000) 2>/dev/null || echo "Port already clear"
sleep 2
echo ""

# Check if abparts_prod exists
echo "2. Checking if abparts_prod database exists..."
DB_EXISTS=$(docker compose exec db psql -U abparts_user -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='abparts_prod'")

if [ "$DB_EXISTS" = "1" ]; then
    echo "✓ abparts_prod database already exists"
    echo ""
    read -p "Do you want to drop and recreate it? (y/n): " recreate
    if [ "$recreate" = "y" ] || [ "$recreate" = "Y" ]; then
        echo "Dropping abparts_prod..."
        docker compose exec db psql -U abparts_user -d postgres -c "DROP DATABASE abparts_prod;"
        echo "Creating fresh abparts_prod..."
        docker compose exec db psql -U abparts_user -d postgres -c "CREATE DATABASE abparts_prod OWNER abparts_user;"
    fi
else
    echo "Creating abparts_prod database..."
    docker compose exec db psql -U abparts_user -d postgres -c "CREATE DATABASE abparts_prod OWNER abparts_user;"
    echo "✓ Database created"
fi
echo ""

# Check if we should copy data from abparts_dev
echo "3. Checking abparts_dev database..."
DEV_EXISTS=$(docker compose exec db psql -U abparts_user -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='abparts_dev'")

if [ "$DEV_EXISTS" = "1" ]; then
    echo "✓ abparts_dev exists"
    echo ""
    read -p "Copy data from abparts_dev to abparts_prod? (y/n): " copy_data
    
    if [ "$copy_data" = "y" ] || [ "$copy_data" = "Y" ]; then
        echo "Dumping abparts_dev..."
        docker compose exec db pg_dump -U abparts_user abparts_dev > /tmp/abparts_dev_dump.sql
        
        echo "Restoring to abparts_prod..."
        docker compose exec -T db psql -U abparts_user -d abparts_prod < /tmp/abparts_dev_dump.sql
        
        echo "✓ Data copied"
        rm /tmp/abparts_dev_dump.sql
    else
        echo "Skipping data copy. Will run migrations on empty database."
    fi
else
    echo "abparts_dev doesn't exist. Will run migrations on empty database."
fi
echo ""

# Start API container
echo "4. Starting API container..."
docker compose up -d api
sleep 5
echo ""

# Run migrations
echo "5. Running database migrations..."
docker compose exec api alembic upgrade head
echo ""

# Check API health
echo "6. Checking API health..."
sleep 3
for i in {1..5}; do
    HEALTH=$(curl -s http://localhost:8000/health)
    echo "Attempt $i: $HEALTH"
    
    if echo "$HEALTH" | grep -q '"database": "connected"'; then
        echo ""
        echo "✓ API is healthy and connected to database!"
        break
    fi
    
    if [ $i -lt 5 ]; then
        echo "Waiting..."
        sleep 3
    fi
done
echo ""

# Show final status
echo "7. Final status..."
docker compose ps
echo ""

echo "API logs (last 15 lines):"
docker compose logs --tail=15 api
echo ""

echo "=== Setup Complete ==="
echo ""
echo "Test the API:"
echo "  curl http://localhost:8000/health | python3 -m json.tool"
echo ""
echo "Test the website:"
echo "  curl -I https://abparts.oraseas.com"
echo ""
echo "View logs:"
echo "  docker compose logs -f api"
