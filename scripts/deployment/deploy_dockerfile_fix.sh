#!/bin/bash

echo "=== Deploying Dockerfile Fix ==="
echo ""

echo "1. Copying updated Dockerfile to server..."
scp frontend/Dockerfile.frontend diogo@46.62.153.166:/tmp/

echo ""
echo "2. Copying .dockerignore to server..."
scp frontend/.dockerignore diogo@46.62.153.166:/tmp/

echo ""
echo "3. Building on server with fix..."
ssh diogo@46.62.153.166 << 'ENDSSH'

# Move files to correct location with sudo
sudo mv /tmp/Dockerfile.frontend /root/abparts/frontend/
sudo mv /tmp/.dockerignore /root/abparts/frontend/

cd /root/abparts

echo "Stopping web container..."
sudo docker compose -f docker-compose.prod.yml stop web

echo ""
echo "Removing old container and image..."
sudo docker rm abparts_web_prod 2>/dev/null || true
sudo docker rmi abparts-web 2>/dev/null || true

echo ""
echo "Building with --no-cache (watch for the echo statement)..."
sudo docker compose -f docker-compose.prod.yml build --no-cache web 2>&1 | grep -E "(Building with REACT_APP|Step|Successfully)"

echo ""
echo "Starting web container..."
sudo docker compose -f docker-compose.prod.yml up -d web

echo ""
echo "Waiting for container to start..."
sleep 5

echo ""
echo "Checking the build..."
if sudo docker exec abparts_web_prod sh -c "grep -r 'localhost:8000' /usr/share/nginx/html/static/js/*.js 2>/dev/null" | head -1; then
    echo "❌ ERROR: Still contains localhost:8000"
    echo ""
    echo "Debugging - checking what's in the built file:"
    sudo docker exec abparts_web_prod sh -c "grep -o 'API_BASE_URL=\"[^\"]*' /usr/share/nginx/html/static/js/main.*.js | head -3"
else
    echo "✅ SUCCESS: No localhost:8000 found!"
    echo ""
    echo "Verifying API_BASE_URL value:"
    sudo docker exec abparts_web_prod sh -c "grep -o 'API_BASE_URL=\"[^\"]*' /usr/share/nginx/html/static/js/main.*.js | head -1"
fi

echo ""
echo "=== Done ==="
echo "Test at: https://abparts.oraseas.com"

ENDSSH
