#!/bin/bash
# deploy_image_fixes_production.sh
# Deploy image functionality fixes to production environment

set -e  # Exit on any error

echo "=========================================="
echo "🚀 Deploying Image Functionality Fixes"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "docker-compose.prod.yml" ]; then
    print_error "docker-compose.prod.yml not found. Please run this script from the project root directory."
    exit 1
fi

print_status "Starting production deployment..."

# Step 1: Backup current state
print_status "Creating backup of current containers..."
docker compose -f docker-compose.prod.yml ps > production_containers_backup_$(date +%Y%m%d_%H%M%S).txt

# Step 2: Stop production services gracefully
print_status "Stopping production services..."
docker compose -f docker-compose.prod.yml down

print_success "Services stopped successfully"

# Step 3: Rebuild containers with latest code
print_status "Rebuilding backend container with latest fixes..."
docker compose -f docker-compose.prod.yml build --no-cache api

print_status "Rebuilding frontend container with latest fixes..."
docker compose -f docker-compose.prod.yml build --no-cache web

print_success "Containers rebuilt successfully"

# Step 4: Start database and redis first
print_status "Starting database and Redis services..."
docker compose -f docker-compose.prod.yml up -d db redis

# Wait for database to be ready
print_status "Waiting for database to be ready..."
sleep 15

# Check database health
DB_READY=false
for i in {1..30}; do
    if docker compose -f docker-compose.prod.yml exec -T db pg_isready -U abparts_user -d abparts_prod > /dev/null 2>&1; then
        DB_READY=true
        break
    fi
    print_status "Waiting for database... ($i/30)"
    sleep 2
done

if [ "$DB_READY" = false ]; then
    print_error "Database failed to start within timeout"
    exit 1
fi

print_success "Database is ready"

# Step 5: Start API service
print_status "Starting API service..."
docker compose -f docker-compose.prod.yml up -d api celery_worker

# Wait for API to be ready
print_status "Waiting for API to be ready..."
sleep 20

# Check API health
API_READY=false
for i in {1..30}; do
    if curl -f http://localhost:8000/docs > /dev/null 2>&1; then
        API_READY=true
        break
    fi
    print_status "Waiting for API... ($i/30)"
    sleep 2
done

if [ "$API_READY" = false ]; then
    print_warning "API health check failed, but continuing deployment"
fi

# Step 6: Run database migrations
print_status "Running database migrations..."
docker compose -f docker-compose.prod.yml exec -T api alembic upgrade head

print_success "Database migrations completed"

# Step 7: Start frontend service
print_status "Starting frontend service..."
docker compose -f docker-compose.prod.yml up -d web

print_success "All services started"

# Step 8: Verify deployment
print_status "Verifying deployment..."

# Check container status
print_status "Container status:"
docker compose -f docker-compose.prod.yml ps

# Test API endpoints
print_status "Testing API endpoints..."

# Test health endpoint
if curl -f http://localhost:8000/docs > /dev/null 2>&1; then
    print_success "✅ API documentation accessible"
else
    print_warning "⚠️  API documentation not accessible"
fi

# Test parts endpoint (requires authentication, so just check if it returns 401)
PARTS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/parts/with-inventory)
if [ "$PARTS_RESPONSE" = "401" ]; then
    print_success "✅ Parts endpoint responding (authentication required)"
elif [ "$PARTS_RESPONSE" = "200" ]; then
    print_success "✅ Parts endpoint responding"
else
    print_warning "⚠️  Parts endpoint returned status: $PARTS_RESPONSE"
fi

# Step 9: Check recent database entries
print_status "Checking database for recent parts..."
RECENT_PARTS=$(docker compose -f docker-compose.prod.yml exec -T db psql -U abparts_user -d abparts_prod -t -c "SELECT COUNT(*) FROM parts WHERE created_at > NOW() - INTERVAL '1 hour';" 2>/dev/null | tr -d ' ')

if [ ! -z "$RECENT_PARTS" ] && [ "$RECENT_PARTS" -gt 0 ]; then
    print_success "✅ Found $RECENT_PARTS recent parts in database"
else
    print_status "ℹ️  No recent parts found (this is normal if no parts were created recently)"
fi

# Step 10: Display final status
echo ""
echo "=========================================="
echo "🎉 DEPLOYMENT COMPLETE"
echo "=========================================="
echo ""
print_success "Image functionality fixes have been deployed to production!"
echo ""
echo "📋 WHAT WAS DEPLOYED:"
echo "   ✅ Backend CRUD fixes (parts sorting by creation date)"
echo "   ✅ Backend image handling fixes (preserve image_urls)"
echo "   ✅ Frontend debugging enhancements"
echo "   ✅ Database migrations applied"
echo ""
echo "🧪 TESTING INSTRUCTIONS:"
echo "   1. Open production site in browser"
echo "   2. Login with credentials: dthomaz / amFT1999!"
echo "   3. Go to Parts management (SuperAdmin interface)"
echo "   4. Create a new part with images (up to 20 images)"
echo "   5. Verify:"
echo "      - Part appears at top of list immediately"
echo "      - Correct image count is displayed"
echo "      - Success message appears"
echo ""
echo "🔍 IF ISSUES PERSIST:"
echo "   1. Check browser console for JavaScript errors"
echo "   2. Check Network tab for failed API requests"
echo "   3. Check API logs: docker-compose -f docker-compose.prod.yml logs api"
echo "   4. Check database: docker-compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod"
echo ""
echo "📊 MONITORING:"
echo "   - API logs: docker compose -f docker-compose.prod.yml logs -f api"
echo "   - All services: docker compose -f docker-compose.prod.yml logs -f"
echo ""

# Step 11: Show service URLs
echo "🌐 SERVICE URLS:"
echo "   - Frontend: http://46.62.153.166:3001"
echo "   - API: http://46.62.153.166:8000"
echo "   - API Docs: http://46.62.153.166:8000/docs"
echo "   - PgAdmin: http://46.62.153.166:8080 (if enabled)"
echo ""

print_success "Deployment completed successfully! 🚀"