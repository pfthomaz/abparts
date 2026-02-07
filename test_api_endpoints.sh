#!/bin/bash

# Test API Endpoints for Maintenance Executions Page
# This script tests the three main endpoints needed for the page to load

echo "Testing API endpoints..."
echo ""

# Get auth token (you'll need to replace with actual token)
TOKEN=$(cat <<EOF
# To get your token:
# 1. Open browser DevTools (F12)
# 2. Go to Application > Local Storage
# 3. Copy the value of 'authToken'
# 4. Replace YOUR_TOKEN_HERE below
EOF
)

echo "Testing /machines/ endpoint..."
curl -s -w "\nStatus: %{http_code}\n" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  http://localhost:8000/machines/ | head -20
echo ""
echo "---"
echo ""

echo "Testing /maintenance-protocols/ endpoint..."
curl -s -w "\nStatus: %{http_code}\n" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  http://localhost:8000/maintenance-protocols/ | head -20
echo ""
echo "---"
echo ""

echo "Testing /maintenance-protocols/executions endpoint..."
curl -s -w "\nStatus: %{http_code}\n" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  http://localhost:8000/maintenance-protocols/executions | head -20
echo ""

echo ""
echo "If you see 401 errors, you need to update YOUR_TOKEN_HERE with your actual token"
echo "If you see 408 errors, the API is timing out"
echo "If you see 200 with data, the API is working"
