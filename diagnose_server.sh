#!/bin/bash

echo "=== ABParts Server Diagnostics ==="
echo ""

# Check .env file
echo "1. Checking .env file..."
if [ -f .env ]; then
    echo "✓ .env file exists"
    echo "CORS settings:"
    grep -E "CORS|ENVIRONMENT" .env || echo "⚠ No CORS/ENVIRONMENT variables found"
else
    echo "✗ .env file not found!"
fi
echo ""

# Check container status
echo "2. Container status..."
docker compose ps
echo ""

# Check API container logs (last 20 lines)
echo "3. API container logs (last 20 lines)..."
docker compose logs --tail=20 api
echo ""

# Check web container logs
echo "4. Web container logs (last 20 lines)..."
docker compose logs --tail=20 web
echo ""

# Check if API is responding
echo "5. Testing API health endpoint..."
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:8000/health || echo "✗ API not responding"
echo ""

# Check if frontend is responding
echo "6. Testing frontend..."
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:3000/ || echo "✗ Frontend not responding"
echo ""

# Check nginx config in web container
echo "7. Checking nginx config in web container..."
docker compose exec web cat /etc/nginx/conf.d/default.conf 2>/dev/null || echo "⚠ Cannot read nginx config"
echo ""

# Check what process is running in web container
echo "8. Web container processes..."
docker compose exec web ps aux 2>/dev/null || echo "⚠ Web container not responding"
echo ""

# Check docker compose file
echo "9. Docker compose configuration..."
grep -A 5 "web:" docker-compose.yml
echo ""

echo "=== Diagnostics Complete ==="
