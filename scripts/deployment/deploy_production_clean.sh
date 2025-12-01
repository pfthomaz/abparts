#!/bin/bash
set -e

echo "========================================="
echo "ABParts Production Deployment"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}ERROR: .env file not found${NC}"
    echo "Please create .env from .env.production.example"
    echo "  cp .env.production.example .env"
    echo "  nano .env  # Edit with your values"
    exit 1
fi

# Verify critical environment variables
echo "Checking environment configuration..."
if ! grep -q "CORS_ALLOWED_ORIGINS=https://" .env; then
    echo -e "${YELLOW}WARNING: CORS_ALLOWED_ORIGINS not set to HTTPS${NC}"
    echo "Please update .env with: CORS_ALLOWED_ORIGINS=https://abparts.oraseas.com"
fi

if ! grep -q "ENVIRONMENT=production" .env; then
    echo -e "${YELLOW}WARNING: ENVIRONMENT not set to production${NC}"
fi

echo -e "${GREEN}✓${NC} Environment configuration found"
echo ""

# Step 1: Stop existing containers
echo "Step 1: Stopping existing containers..."
docker compose -f docker-compose.prod.yml down
echo -e "${GREEN}✓${NC} Containers stopped"
echo ""

# Step 2: Build images
echo "Step 2: Building Docker images..."
docker compose -f docker-compose.prod.yml build --no-cache
echo -e "${GREEN}✓${NC} Images built"
echo ""

# Step 3: Start database and redis first
echo "Step 3: Starting database and redis..."
docker compose -f docker-compose.prod.yml up -d db redis
echo "Waiting for database to be ready..."
sleep 10
echo -e "${GREEN}✓${NC} Database and Redis started"
echo ""

# Step 4: Run migrations (if needed)
echo "Step 4: Checking migrations..."
if [ -f "reset_migrations_clean.sh" ]; then
    read -p "Do you want to reset migrations to clean baseline? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        chmod +x reset_migrations_clean.sh
        ./reset_migrations_clean.sh
    fi
else
    echo "Running existing migrations..."
    docker compose -f docker-compose.prod.yml run --rm api alembic upgrade head
fi
echo -e "${GREEN}✓${NC} Migrations complete"
echo ""

# Step 5: Start all services
echo "Step 5: Starting all services..."
docker compose -f docker-compose.prod.yml up -d
echo -e "${GREEN}✓${NC} All services started"
echo ""

# Step 6: Wait for services to be ready
echo "Step 6: Waiting for services to be ready..."
sleep 5

# Check API health
echo "Checking API health..."
for i in {1..30}; do
    if docker compose -f docker-compose.prod.yml exec -T api curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} API is healthy"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}ERROR: API failed to start${NC}"
        echo "Check logs with: docker compose -f docker-compose.prod.yml logs api"
        exit 1
    fi
    echo "Waiting for API... ($i/30)"
    sleep 2
done
echo ""

# Step 7: Display status
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "Services Status:"
docker compose -f docker-compose.prod.yml ps
echo ""
echo "Access Points:"
echo "  - Frontend: https://abparts.oraseas.com"
echo "  - API: https://abparts.oraseas.com/api"
echo "  - API Docs: https://abparts.oraseas.com/api/docs"
echo ""
echo "Useful Commands:"
echo "  - View logs: docker compose -f docker-compose.prod.yml logs -f"
echo "  - Restart service: docker compose -f docker-compose.prod.yml restart <service>"
echo "  - Stop all: docker compose -f docker-compose.prod.yml down"
echo ""
echo "CORS Configuration:"
docker compose -f docker-compose.prod.yml exec -T api python -c "from app.cors_config import get_cors_origins; print('  Allowed origins:', get_cors_origins())" 2>/dev/null || echo "  (Could not retrieve CORS config)"
echo ""
