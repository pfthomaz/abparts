#!/bin/bash
# debug_auth_error.sh
# Debug authentication 500 error

echo "=== Debugging Authentication Error ==="
echo ""

# Check if backend is running
echo "1. Checking if backend API is running..."
if curl -s http://localhost:8000/docs > /dev/null; then
    echo "✅ Backend API is running at http://localhost:8000"
else
    echo "❌ Backend API is not responding at http://localhost:8000"
    echo "   Try: docker-compose up api"
    exit 1
fi

# Check API logs for errors
echo ""
echo "2. Checking recent API logs..."
echo "Recent API container logs:"
docker-compose logs --tail=20 api

echo ""
echo "3. Testing token endpoint directly..."
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test&password=test" \
  -v

echo ""
echo ""
echo "4. Checking database connection..."
docker-compose exec api python -c "
from app.database import engine
try:
    with engine.connect() as conn:
        result = conn.execute('SELECT 1')
        print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"

echo ""
echo "5. Common fixes:"
echo "   - Restart API: docker-compose restart api"
echo "   - Check database: docker-compose logs db"
echo "   - Reset database: docker-compose down && docker-compose up"