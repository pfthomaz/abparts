#!/bin/bash

echo "=== Checking Login Error ==="
echo ""

# Check API logs for errors
echo "1. Recent API logs (last 30 lines):"
docker compose logs --tail=30 api
echo ""

# Test the token endpoint directly
echo "2. Testing /api/token endpoint directly..."
curl -X POST https://abparts.oraseas.com/api/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test&password=test" \
  -v 2>&1 | grep -E "HTTP|error|Error"
echo ""

# Check if there are any users in the database
echo "3. Checking if users exist in database..."
docker compose exec db psql -U abparts_user -d abparts_prod -c "SELECT id, username, email, role FROM users LIMIT 5;"
echo ""

# Check database connection from API
echo "4. Checking API database connection..."
curl -s http://localhost:8000/health | python3 -m json.tool
echo ""

# Check if alembic migrations are up to date
echo "5. Checking migration status..."
docker compose exec api alembic current
echo ""

echo "=== Diagnostics Complete ==="
echo ""
echo "Check the logs above for the specific error."
echo "Common issues:"
echo "  - No users in database (need to create initial user)"
echo "  - Missing database tables (need to run migrations)"
echo "  - SECRET_KEY not set in environment"
