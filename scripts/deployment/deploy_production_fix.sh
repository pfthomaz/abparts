#!/bin/bash
# Production Deployment Fix Script

set -e

echo "=== ABParts Production Deployment Fix ==="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Please create .env file with required variables"
    exit 1
fi

# Update or add REACT_APP_API_BASE_URL in .env
echo "Step 1: Updating .env file..."
if grep -q "^REACT_APP_API_BASE_URL=" .env; then
    sed -i.bak 's|^REACT_APP_API_BASE_URL=.*|REACT_APP_API_BASE_URL=/api|' .env
    echo "✓ Updated REACT_APP_API_BASE_URL in .env"
else
    echo "REACT_APP_API_BASE_URL=/api" >> .env
    echo "✓ Added REACT_APP_API_BASE_URL to .env"
fi

echo ""
echo "Step 2: Stopping services..."
sudo docker compose -f docker-compose.prod.yml down

echo ""
echo "Step 3: Rebuilding frontend with new configuration..."
sudo docker compose -f docker-compose.prod.yml build web --no-cache

echo ""
echo "Step 4: Starting all services..."
sudo docker compose -f docker-compose.prod.yml up -d

echo ""
echo "Step 5: Waiting for services to start..."
sleep 10

echo ""
echo "Step 6: Checking service status..."
sudo docker ps | grep abparts

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Testing endpoints:"
echo "  Frontend: http://46.62.153.166/"
echo "  API (via proxy): http://46.62.153.166/api/"
echo "  API docs: http://46.62.153.166/docs"
echo ""
echo "Check logs with:"
echo "  sudo docker logs abparts_web_prod"
echo "  sudo docker logs abparts_api_prod"
echo ""
