#!/bin/bash

echo "=== Fixing Production Environment Configuration ==="
echo ""

echo "Connecting to production server..."
ssh root@46.62.153.166 << 'ENDSSH'

cd /root/abparts

echo "1. Backing up current .env..."
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

echo ""
echo "2. Checking if REACT_APP_API_BASE_URL exists..."
if grep -q "^REACT_APP_API_BASE_URL=" .env; then
    echo "   Found - updating it..."
    sed -i 's|^REACT_APP_API_BASE_URL=.*|REACT_APP_API_BASE_URL=/api|' .env
else
    echo "   Not found - adding it..."
    echo "" >> .env
    echo "# Frontend API Configuration" >> .env
    echo "REACT_APP_API_BASE_URL=/api" >> .env
fi

echo ""
echo "3. Updating BASE_URL to HTTPS..."
sed -i 's|^BASE_URL=.*|BASE_URL=https://abparts.oraseas.com|' .env

echo ""
echo "4. Current configuration:"
grep -E "^(BASE_URL|REACT_APP_API_BASE_URL)=" .env

echo ""
echo "5. Stopping web container..."
docker compose -f docker-compose.prod.yml stop web

echo ""
echo "6. Removing old container and image..."
docker rm abparts_web_prod 2>/dev/null || true
docker rmi abparts-web 2>/dev/null || true

echo ""
echo "7. Building with --no-cache to ensure clean build..."
docker compose -f docker-compose.prod.yml build --no-cache web

echo ""
echo "8. Starting web container..."
docker compose -f docker-compose.prod.yml up -d web

echo ""
echo "9. Waiting for container to start..."
sleep 5

echo ""
echo "10. Verifying the build..."
if docker exec abparts_web_prod sh -c "grep -r 'localhost:8000' /usr/share/nginx/html/static/js/ 2>/dev/null | head -1"; then
    echo "   ❌ ERROR: Still contains localhost:8000"
    echo ""
    echo "   Checking what REACT_APP_API_BASE_URL was during build..."
    docker compose -f docker-compose.prod.yml config | grep -A 2 REACT_APP_API_BASE_URL
else
    echo "   ✅ SUCCESS: No localhost:8000 found!"
    echo "   Frontend is using /api for API calls"
fi

echo ""
echo "=== Done ==="
echo "Test at: https://abparts.oraseas.com"

ENDSSH
