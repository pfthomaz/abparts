#!/bin/bash
set -e

echo "========================================="
echo "Fixing Production Issues"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Issue 1: Fix .env CORS settings
echo "1. Fixing .env CORS settings..."
if [ -f .env ]; then
    # Backup current .env
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    
    # Update CORS_ALLOWED_ORIGINS if it exists but is wrong
    if grep -q "^CORS_ALLOWED_ORIGINS=" .env; then
        # Check if it's already HTTPS
        if ! grep -q "^CORS_ALLOWED_ORIGINS=https://" .env; then
            echo "  Updating CORS_ALLOWED_ORIGINS to HTTPS..."
            sed -i.bak 's|^CORS_ALLOWED_ORIGINS=.*|CORS_ALLOWED_ORIGINS=https://abparts.oraseas.com|' .env
        fi
    else
        # Add CORS_ALLOWED_ORIGINS
        echo "  Adding CORS_ALLOWED_ORIGINS..."
        echo "" >> .env
        echo "# CORS Configuration" >> .env
        echo "CORS_ALLOWED_ORIGINS=https://abparts.oraseas.com" >> .env
        echo "CORS_ALLOW_CREDENTIALS=true" >> .env
    fi
    
    # Add ENVIRONMENT if missing
    if ! grep -q "^ENVIRONMENT=" .env; then
        echo "  Adding ENVIRONMENT=production..."
        echo "ENVIRONMENT=production" >> .env
    fi
    
    # Check SECRET_KEY
    if ! grep -q "^SECRET_KEY=.\{20,\}" .env; then
        echo "  Generating SECRET_KEY..."
        SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
        if grep -q "^SECRET_KEY=" .env; then
            sed -i.bak "s|^SECRET_KEY=.*|SECRET_KEY=$SECRET|" .env
        else
            echo "SECRET_KEY=$SECRET" >> .env
        fi
    fi
    
    # Check JWT_SECRET_KEY
    if ! grep -q "^JWT_SECRET_KEY=.\{20,\}" .env; then
        echo "  Generating JWT_SECRET_KEY..."
        JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
        if grep -q "^JWT_SECRET_KEY=" .env; then
            sed -i.bak "s|^JWT_SECRET_KEY=.*|JWT_SECRET_KEY=$JWT_SECRET|" .env
        else
            echo "JWT_SECRET_KEY=$JWT_SECRET" >> .env
        fi
    fi
    
    echo -e "${GREEN}✓${NC} .env file updated"
else
    echo -e "${YELLOW}⚠${NC} .env file not found, creating from template..."
    cp .env.production.example .env
    echo "  Please edit .env and add your actual values"
fi
echo ""

# Issue 2: Fix docker-compose.prod.yml web service restart policy
echo "2. Checking docker-compose.prod.yml..."
if grep -A 10 "web:" docker-compose.prod.yml | grep -q "restart:"; then
    echo -e "${GREEN}✓${NC} Restart policy already exists"
else
    echo "  Adding restart policy to web service..."
    # This is complex to do with sed, so we'll just note it
    echo -e "${YELLOW}⚠${NC} Please manually add 'restart: unless-stopped' to web service in docker-compose.prod.yml"
fi
echo ""

# Issue 3: Start web container
echo "3. Starting web container..."
docker compose -f docker-compose.prod.yml up -d web
echo -e "${GREEN}✓${NC} Web container started"
echo ""

# Issue 4: Check API health
echo "4. Waiting for API to be ready..."
sleep 5
if docker compose exec -T api curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} API is healthy"
else
    echo -e "${YELLOW}⚠${NC} API health check failed, restarting..."
    docker compose restart api
    sleep 5
fi
echo ""

# Issue 5: Fix migration version check
echo "5. Checking database migration..."
MIGRATION=$(docker compose exec -T db psql -U abparts_user -d abparts_prod -c "SELECT version_num FROM alembic_version;" -t 2>/dev/null | tr -d ' \n\r')
if [ -n "$MIGRATION" ]; then
    echo -e "${GREEN}✓${NC} Migration version: $MIGRATION"
else
    echo -e "${YELLOW}⚠${NC} Could not retrieve migration version"
    echo "  This might be normal if alembic_version table doesn't exist yet"
fi
echo ""

echo "========================================="
echo "Fixes Applied"
echo "========================================="
echo ""
echo "Running verification again..."
echo ""
./verify_production_setup.sh
