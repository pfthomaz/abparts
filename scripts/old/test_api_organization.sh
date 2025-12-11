#!/bin/bash

echo "Testing /users/me/ endpoint..."
echo ""

# Login first
echo "1. Logging in..."
TOKEN_RESPONSE=$(curl -s -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jamie&password=your_password_here")

TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ Login failed!"
  echo "Response: $TOKEN_RESPONSE"
  exit 1
fi

echo "✅ Login successful!"
echo ""

# Get user info
echo "2. Getting user info from /users/me/..."
USER_RESPONSE=$(curl -s -X GET "http://localhost:8000/users/me/" \
  -H "Authorization: Bearer $TOKEN")

echo "$USER_RESPONSE" | python3 -m json.tool

echo ""
echo "3. Checking for organization field..."
if echo "$USER_RESPONSE" | grep -q '"organization"'; then
  echo "✅ Organization field found!"
else
  echo "❌ Organization field NOT found!"
fi
