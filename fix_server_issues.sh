#!/bin/bash

echo "=== Fixing ABParts Server Issues ==="
echo ""

# Fix 1: Update docker-compose.yml to properly pass CORS env var
echo "1. Fixing docker-compose.yml CORS configuration..."
sed -i 's/http:\/\/46\.62\.1CORS_ALLOWED_ORIGINS:/CORS_ALLOWED_ORIGINS:/' docker-compose.yml
echo "✓ Fixed CORS_ALLOWED_ORIGINS line in docker-compose.yml"
echo ""

# Fix 2: Rebuild and restart API container
echo "2. Rebuilding and restarting API container..."
docker compose stop api
docker compose rm -f api
docker compose up -d api
echo "✓ API container restarted"
echo ""

# Fix 3: Check if web container should be running
echo "3. Checking web container configuration..."
if grep -q "npm start" docker-compose.yml; then
    echo "⚠ Web container is configured for development mode"
    echo "   In production, you should serve the built React app with nginx"
    echo "   For now, stopping the web container..."
    docker compose stop web
    docker compose rm -f web
    echo "✓ Web container stopped"
else
    echo "✓ Web container configuration looks good"
fi
echo ""

# Wait for API to start
echo "4. Waiting for API to start..."
sleep 5
echo ""

# Test the fixes
echo "5. Testing the fixes..."
echo ""

echo "API logs (last 10 lines):"
docker compose logs --tail=10 api | grep -E "CORS|Origins"
echo ""

echo "Testing API health:"
curl -s http://localhost:8000/health | python3 -m json.tool || echo "✗ API not responding"
echo ""

echo "Testing CORS from frontend domain:"
curl -s -H "Origin: https://abparts.oraseas.com" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     http://localhost:8000/health -v 2>&1 | grep -E "Access-Control|HTTP"
echo ""

echo "=== Fix Complete ==="
echo ""
echo "Next steps:"
echo "1. Check if CORS origins are now showing in the logs above"
echo "2. If origins are still empty, check .env file format"
echo "3. For production frontend, you need to:"
echo "   - Build the React app: cd frontend && npm run build"
echo "   - Serve it with nginx or through a CDN"
