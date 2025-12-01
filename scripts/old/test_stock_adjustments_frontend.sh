#!/bin/bash
set -e

echo "=== Stock Adjustments Feature - Frontend Test ==="
echo ""

echo "Step 1: Checking if API is running..."
if curl -s http://localhost:8000/docs > /dev/null; then
  echo "✅ API is running"
else
  echo "❌ API is not running. Start with: docker-compose up -d"
  exit 1
fi
echo ""

echo "Step 2: Checking if frontend is running..."
if curl -s http://localhost:3000 > /dev/null; then
  echo "✅ Frontend is running"
else
  echo "⚠️  Frontend might not be running. Start with: cd frontend && npm start"
fi
echo ""

echo "Step 3: Testing API endpoints..."
echo ""

# Get token
echo "Getting auth token..."
TOKEN=$(curl -s -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@oraseas.com&password=admin123" | jq -r '.access_token')

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
  echo "❌ Failed to get auth token"
  exit 1
fi
echo "✅ Got auth token"
echo ""

# Test list endpoint
echo "Testing GET /stock-adjustments..."
RESPONSE=$(curl -s -X GET "http://localhost:8000/stock-adjustments" \
  -H "Authorization: Bearer $TOKEN")

if echo "$RESPONSE" | jq -e '. | type == "array"' > /dev/null 2>&1; then
  COUNT=$(echo "$RESPONSE" | jq 'length')
  echo "✅ List endpoint working - Found $COUNT adjustments"
else
  echo "❌ List endpoint failed"
  echo "$RESPONSE"
  exit 1
fi
echo ""

echo "=== All Tests Passed ==="
echo ""
echo "Next steps:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Login as admin@oraseas.com / admin123"
echo "3. Navigate to Stock Adjustments from the Inventory menu"
echo "4. Try creating a new adjustment"
echo ""
