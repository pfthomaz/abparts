#!/bin/bash

echo "=== Checking Environment Configuration ==="
echo ""

echo "1. Current .env file on server:"
ssh root@46.62.153.166 "cat /root/abparts/.env | grep -E 'REACT_APP|BASE_URL'"

echo ""
echo "2. Checking if REACT_APP_API_BASE_URL is in .env:"
ssh root@46.62.153.166 "grep REACT_APP_API_BASE_URL /root/abparts/.env || echo '❌ NOT FOUND'"

echo ""
echo "3. Checking docker-compose.prod.yml build args:"
ssh root@46.62.153.166 "grep -A 5 'REACT_APP_API_BASE_URL' /root/abparts/docker-compose.prod.yml"

echo ""
echo "4. Checking what's baked into the current build:"
ssh root@46.62.153.166 "docker exec abparts_web_prod sh -c 'grep -o \"localhost:8000\" /usr/share/nginx/html/static/js/*.js | head -5' 2>/dev/null || echo 'Container not running'"

echo ""
echo "=== Fix Instructions ==="
echo ""
echo "The issue is that REACT_APP_API_BASE_URL must be:"
echo "  1. Set in .env file"
echo "  2. Passed as build arg in docker-compose"
echo "  3. Available during 'npm run build'"
echo ""
echo "Run this to fix:"
echo "  ssh root@46.62.153.166"
echo "  cd /root/abparts"
echo "  echo 'REACT_APP_API_BASE_URL=/api' >> .env"
echo "  docker compose -f docker-compose.prod.yml build --no-cache web"
echo "  docker compose -f docker-compose.prod.yml up -d web"
