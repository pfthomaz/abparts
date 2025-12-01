#!/bin/bash

echo "=== Frontend Build Diagnosis ==="
echo ""

# Check if REACT_APP_API_BASE_URL is in the .env file
echo "Step 1: Checking .env file..."
if grep -q "REACT_APP_API_BASE_URL" .env; then
    echo "✅ Found in .env:"
    grep "REACT_APP_API_BASE_URL" .env
else
    echo "❌ REACT_APP_API_BASE_URL NOT in .env file"
    echo ""
    echo "This is the problem! Add it now:"
    echo "echo 'REACT_APP_API_BASE_URL=/api' >> .env"
fi

echo ""
echo "Step 2: Checking docker-compose.prod.yml..."
grep -A 3 "REACT_APP_API_BASE_URL" docker-compose.prod.yml

echo ""
echo "Step 3: The frontend code has these fallbacks:"
echo "   frontend/src/services/api.js: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000'"
echo "   frontend/src/services/authService.js: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000'"
echo "   frontend/src/AuthContext.js: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000'"

echo ""
echo "=== THE FIX ==="
echo ""
echo "The .env file needs REACT_APP_API_BASE_URL=/api"
echo "Then rebuild: docker compose -f docker-compose.prod.yml build --no-cache web"
