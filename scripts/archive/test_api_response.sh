#!/bin/bash

echo "🔍 Testing API Response"
echo "======================"
echo ""

read -p "Enter your username: " USERNAME
read -sp "Enter your password: " PASSWORD
echo ""
echo ""

# Login and get token
echo "1. Logging in..."
TOKEN_RESPONSE=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$USERNAME&password=$PASSWORD")

TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ Login failed!"
    echo "Response: $TOKEN_RESPONSE"
    exit 1
fi

echo "✅ Login successful!"
echo ""

# Get user info
echo "2. Fetching /users/me/ ..."
curl -s "http://localhost:8000/users/me/" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo ""
echo ""
echo "Check if 'preferred_language' is in the response above!"
