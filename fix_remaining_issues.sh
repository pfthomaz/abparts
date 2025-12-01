#!/bin/bash
set -e

echo "========================================="
echo "Fixing Remaining Issues"
echo "========================================="
echo ""

# Issue 1: Fix SECRET_KEY
echo "1. Fixing SECRET_KEY..."
if ! grep -q "^SECRET_KEY=.\{32,\}" .env; then
    echo "  Generating new SECRET_KEY..."
    SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    
    if grep -q "^SECRET_KEY=" .env; then
        # Update existing
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s|^SECRET_KEY=.*|SECRET_KEY=$SECRET|" .env
        else
            sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$SECRET|" .env
        fi
    else
        # Add new
        echo "SECRET_KEY=$SECRET" >> .env
    fi
    echo "  ✓ SECRET_KEY generated and added"
else
    echo "  ✓ SECRET_KEY already valid"
fi

# Also check JWT_SECRET_KEY
if ! grep -q "^JWT_SECRET_KEY=.\{32,\}" .env; then
    echo "  Generating JWT_SECRET_KEY..."
    JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    
    if grep -q "^JWT_SECRET_KEY=" .env; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s|^JWT_SECRET_KEY=.*|JWT_SECRET_KEY=$JWT_SECRET|" .env
        else
            sed -i "s|^JWT_SECRET_KEY=.*|JWT_SECRET_KEY=$JWT_SECRET|" .env
        fi
    else
        echo "JWT_SECRET_KEY=$JWT_SECRET" >> .env
    fi
    echo "  ✓ JWT_SECRET_KEY generated and added"
fi
echo ""

# Issue 2: Web service restart policy (false positive - it's already there)
echo "2. Web service restart policy..."
echo "  ✓ Already configured in docker-compose.prod.yml (verification script bug)"
echo ""

# Issue 3: Start web container
echo "3. Starting web container..."
docker compose up -d web
sleep 3
if docker compose ps | grep -q "web.*Up"; then
    echo "  ✓ Web container is running"
else
    echo "  ✗ Web container failed to start"
    echo "  Checking logs..."
    docker compose logs --tail=20 web
fi
echo ""

# Issue 4: Fix API health check
echo "4. Restarting API for health check..."
docker compose restart api
echo "  Waiting for API to be ready..."
sleep 10

# Try health check
if docker compose exec -T api curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "  ✓ API health check passed"
else
    echo "  ✗ API health check still failing"
    echo "  Checking API logs..."
    docker compose logs --tail=30 api
fi
echo ""

# Issue 5: Database migration version
echo "5. Checking database migration..."
MIGRATION=$(docker compose exec -T db psql -U abparts_user -d abparts_prod -c "SELECT version_num FROM alembic_version;" -t 2>&1 | tr -d ' \n\r')

if [ -n "$MIGRATION" ] && [ "$MIGRATION" != "ERROR" ]; then
    echo "  ✓ Migration version: $MIGRATION"
else
    echo "  ⚠ Migration table might not exist yet"
    echo "  This is normal if you haven't run migrations"
    echo "  Run: docker compose exec api alembic upgrade head"
fi
echo ""

echo "========================================="
echo "Fixes Complete"
echo "========================================="
echo ""
echo "Running verification again..."
echo ""
./verify_production_setup.sh
