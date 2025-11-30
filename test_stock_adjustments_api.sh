#!/bin/bash
set -e

echo "=== Testing Stock Adjustments API ==="
echo ""

# Get auth token
echo "Step 1: Getting auth token..."
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
echo "Step 2: Testing GET /stock-adjustments endpoint..."
RESPONSE=$(curl -s -X GET "http://localhost:8000/stock-adjustments" \
  -H "Authorization: Bearer $TOKEN")

echo "Response:"
echo "$RESPONSE" | jq '.'
echo ""

# Check if response is valid JSON array
if echo "$RESPONSE" | jq -e '. | type == "array"' > /dev/null 2>&1; then
  echo "✅ API endpoint working correctly"
  COUNT=$(echo "$RESPONSE" | jq 'length')
  echo "   Found $COUNT stock adjustments"
else
  echo "❌ API endpoint returned invalid response"
  exit 1
fi

echo ""
echo "=== All Tests Passed ==="
