#!/bin/bash

# Safe Production Restart Script

set -e

echo "🚀 ABParts Production Restart Script"
echo "===================================="
echo ""

# Step 1: Verify configuration
echo "Step 1: Verifying configuration..."
if [ ! -f .env ]; then
    echo "❌ ERROR: .env file not found!"
    exit 1
fi

if ! grep -q "abparts_prod" .env; then
    echo "⚠️  WARNING: .env may not be configured for production database"
    echo "   Please verify POSTGRES_DB=abparts_prod in .env"
    read -p "Continue anyway? (y/N): " confirm
    if [ "$confirm" != "y" ]; then
        echo "Aborted."
        exit 1
    fi
fi

echo "✓ Configuration verified"
echo ""

# Step 2: Check for pending migrations
echo "Step 2: Checking for database migrations..."
if docker compose ps | grep -q "api.*Up"; then
    CURRENT_MIGRATION=$(docker compose exec -T api alembic current 2>/dev/null | tail -1 || echo "unknown")
    echo "Current migration: $CURRENT_MIGRATION"
    
    # Check if there are pending migrations
    PENDING=$(docker compose exec -T api alembic heads 2>/dev/null | tail -1 || echo "unknown")
    echo "Latest migration: $PENDING"
    
    if [ "$CURRENT_MIGRATION" != "$PENDING" ] && [ "$CURRENT_MIGRATION" != "unknown" ]; then
        echo "⚠️  Pending migrations detected!"
        read -p "Run migrations before restart? (Y/n): " run_migrations
        if [ "$run_migrations" != "n" ]; then
            echo "Running migrations..."
            docker compose exec api alembic upgrade head
            echo "✓ Migrations complete"
        fi
    else
        echo "✓ Database is up to date"
    fi
else
    echo "⚠️  API container not running - will start fresh"
fi

echo ""

# Step 3: Stop containers
echo "Step 3: Stopping containers..."
docker compose down
echo "✓ Containers stopped"
echo ""

# Step 4: Start containers
echo "Step 4: Starting containers..."
docker compose -f docker-compose.prod.yml up -d
echo "✓ Containers started"
echo ""

# Step 5: Wait for services to be ready
echo "Step 5: Waiting for services to start..."
sleep 5

# Step 6: Check container status
echo "Step 6: Checking container status..."
docker compose ps
echo ""

# Step 7: Check API health
echo "Step 7: Checking API health..."
sleep 3
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ API is responding"
else
    echo "⚠️  API may not be ready yet (this is normal, give it a moment)"
fi

echo ""
echo "Step 8: Checking logs for errors..."
docker compose logs --tail=20 api

echo ""
echo "===================================="
echo "✅ Restart complete!"
echo ""
echo "Next steps:"
echo "  - Check logs: docker compose logs -f"
echo "  - Check API: curl http://localhost:8000/health"
echo "  - Access app: http://your-domain.com"
echo ""
echo "If you see errors, check:"
echo "  - docker compose logs api"
echo "  - docker compose logs web"
echo "  - docker compose logs db"
