#!/bin/bash

echo "=== Testing Docker Build Process ==="
echo ""

echo "1. Testing build with explicit ARG..."
ssh root@46.62.153.166 << 'ENDSSH'

cd /root/abparts

echo "Building with explicit build arg..."
docker compose -f docker-compose.prod.yml build \
  --build-arg REACT_APP_API_BASE_URL=/api \
  --no-cache \
  web 2>&1 | grep -E "(REACT_APP|Step|Building)"

echo ""
echo "Checking if build succeeded..."
docker images | grep abparts-web

ENDSSH

echo ""
echo "2. If build succeeded, check the output..."
ssh root@46.62.153.166 << 'ENDSSH'

cd /root/abparts

# Start the container
docker compose -f docker-compose.prod.yml up -d web

# Wait a moment
sleep 3

# Check for localhost:8000 in the built files
echo "Checking for localhost:8000..."
if docker exec abparts_web_prod sh -c "grep -r 'localhost:8000' /usr/share/nginx/html/static/js/*.js 2>/dev/null" | head -1; then
    echo "❌ STILL FOUND localhost:8000"
    
    echo ""
    echo "Let's check what API_BASE_URL is actually set to:"
    docker exec abparts_web_prod sh -c "grep -o 'API_BASE_URL[^,]*' /usr/share/nginx/html/static/js/main.*.js | head -1"
else
    echo "✅ No localhost:8000 found!"
fi

ENDSSH
