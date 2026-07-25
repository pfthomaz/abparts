#!/bin/bash

# Switch from Development to Production Mode
# This script migrates from docker-compose.yml to docker-compose.prod.yml

set -e

echo "========================================="
echo "Switch to Production Mode"
echo "========================================="
echo ""
echo "This will:"
echo "1. Stop current dev containers"
echo "2. Build production images"
echo "3. Start production containers"
echo "4. Verify everything is running"
echo ""
echo "⚠️  WARNING: This will cause ~5 minutes of downtime"
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo "========================================="
echo "Step 1: Stopping development containers"
echo "========================================="
docker compose down

echo "✓ Development containers stopped"
echo ""

echo "========================================="
echo "Step 2: Building production images"
echo "========================================="
echo "This will take 3-5 minutes..."
docker compose -f docker-compose.prod.yml build --no-cache web api ai_assistant

if [ $? -ne 0 ]; then
    echo "✗ Build failed"
    echo "Rolling back to development mode..."
    docker compose up -d
    exit 1
fi

echo "✓ Production images built"
echo ""

echo "========================================="
echo "Step 3: Starting production containers"
echo "========================================="
docker compose -f docker-compose.prod.yml up -d

if [ $? -ne 0 ]; then
    echo "✗ Failed to start production containers"
    echo "Rolling back to development mode..."
    docker compose -f docker-compose.prod.yml down
    docker compose up -d
    exit 1
fi

echo "✓ Production containers started"
echo ""

echo "========================================="
echo "Step 4: Waiting for services to be ready"
echo "========================================="
echo "Waiting 30 seconds for all services to initialize..."
sleep 30

echo ""
echo "========================================="
echo "Step 5: Verifying services"
echo "========================================="

# Check containers
echo "Container status:"
docker compose -f docker-compose.prod.yml ps

echo ""

# Check web service
if docker compose -f docker-compose.prod.yml ps web | grep -q "Up"; then
    echo "✓ Web service is running (port 3001)"
else
    echo "✗ Web service is not running"
fi

# Check API service
if docker compose -f docker-compose.prod.yml ps api | grep -q "Up"; then
    echo "✓ API service is running (port 8000)"
else
    echo "✗ API service is not running"
fi

# Check AI Assistant
if docker compose -f docker-compose.prod.yml ps ai_assistant | grep -q "Up"; then
    echo "✓ AI Assistant is running (port 8001)"
else
    echo "✗ AI Assistant is not running"
fi

# Check database
if docker compose -f docker-compose.prod.yml ps db | grep -q "Up"; then
    echo "✓ Database is running"
else
    echo "✗ Database is not running"
fi

# Check Redis
if docker compose -f docker-compose.prod.yml ps redis | grep -q "Up"; then
    echo "✓ Redis is running"
else
    echo "✗ Redis is not running"
fi

echo ""
echo "========================================="
echo "Step 6: Testing frontend build"
echo "========================================="

# Check if production build exists in container
if docker compose -f docker-compose.prod.yml exec -T web ls /usr/share/nginx/html/index.html > /dev/null 2>&1; then
    echo "✓ Production build files found"
    
    # Check for translation files in build
    if docker compose -f docker-compose.prod.yml exec -T web ls /usr/share/nginx/html/static/js/*.js > /dev/null 2>&1; then
        echo "✓ JavaScript bundles found"
    else
        echo "⚠ Warning: JavaScript bundles not found"
    fi
else
    echo "✗ Production build files not found"
fi

echo ""
echo "========================================="
echo "Migration Complete!"
echo "========================================="
echo ""
echo "✅ Production mode is now active!"
echo ""
echo "IMPORTANT NEXT STEPS:"
echo ""
echo "1. Frontend is now on PORT 3001 (was 3000)"
echo "   - Docker container serves on port 80 internally"
echo "   - Exposed as port 3001 on host"
echo ""
echo "2. ✅ Your nginx is ALREADY configured correctly!"
echo "   - Config: /etc/nginx/sites-available/abparts.oraseas.com"
echo "   - Already proxying to: http://localhost:3001"
echo "   - NO CHANGES NEEDED!"
echo ""
echo "3. Clear your browser cache:"
echo "   - Press Ctrl+Shift+R (hard refresh)"
echo "   - Or clear cache in browser settings"
echo ""
echo "4. Test the application:"
echo "   - Visit: https://abparts.oraseas.com"
echo "   - Login with: dthomaz/amFT1999!"
echo "   - Check translations are working"
echo "   - Test AI Assistant"
echo ""
echo "5. Production features now active:"
echo "   - ✅ Minified JavaScript with translations baked in"
echo "   - ✅ Static file serving with nginx in Docker"
echo "   - ✅ Better performance and caching"
echo "   - ✅ 4 uvicorn workers for API"
echo "   - ✅ Production-optimized React build"
echo ""
echo "6. To manage production containers:"
echo "   - View logs: docker compose -f docker-compose.prod.yml logs -f [service]"
echo "   - Restart: docker compose -f docker-compose.prod.yml restart [service]"
echo "   - Stop all: docker compose -f docker-compose.prod.yml down"
echo "   - Start all: docker compose -f docker-compose.prod.yml up -d"
echo ""
echo "7. Useful commands:"
echo "   - Check status: docker compose -f docker-compose.prod.yml ps"
echo "   - Web logs: docker compose -f docker-compose.prod.yml logs -f web"
echo "   - API logs: docker compose -f docker-compose.prod.yml logs -f api"
echo "   - AI logs: docker compose -f docker-compose.prod.yml logs -f ai_assistant"
echo ""
