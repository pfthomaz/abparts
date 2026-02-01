#!/bin/bash

# Rebuild Frontend for Production
# This script rebuilds the frontend container with the latest translation files

set -e

echo "========================================="
echo "Rebuilding Frontend for Production"
echo "========================================="
echo ""

# Step 1: Verify translation files exist in source
echo "Step 1: Verifying translation files..."
if [ -f "frontend/src/locales/en.json" ]; then
    echo "✓ Translation files found"
    if grep -q "machineSelected" frontend/src/locales/en.json; then
        echo "✓ machineSelected key exists"
    fi
else
    echo "✗ Translation files not found"
    exit 1
fi

echo ""

# Step 2: Stop web container
echo "Step 2: Stopping web container..."
docker compose stop web
echo "✓ Web container stopped"

echo ""

# Step 3: Rebuild web container with latest code
echo "Step 3: Rebuilding web container..."
echo "This will take 3-5 minutes..."
docker compose build --no-cache web

if [ $? -eq 0 ]; then
    echo "✓ Web container rebuilt successfully"
else
    echo "✗ Web container build failed"
    exit 1
fi

echo ""

# Step 4: Start web container
echo "Step 4: Starting web container..."
docker compose up -d web

if [ $? -eq 0 ]; then
    echo "✓ Web container started"
else
    echo "✗ Web container start failed"
    exit 1
fi

echo ""

# Step 5: Wait for container to be ready
echo "Step 5: Waiting for web container to be ready..."
sleep 10

WEB_STATUS=$(docker compose ps web | grep -c "Up" || echo "0")
if [ "$WEB_STATUS" -gt 0 ]; then
    echo "✓ Web container is running"
else
    echo "✗ Web container is not running"
    docker compose logs web --tail=20
    exit 1
fi

echo ""

# Step 6: Check nginx is serving files
echo "Step 6: Checking nginx is serving files..."
if docker compose exec web ls /usr/share/nginx/html/index.html >/dev/null 2>&1; then
    echo "✓ Frontend build is being served"
else
    echo "⚠ Could not verify frontend files"
fi

echo ""
echo "========================================="
echo "Frontend Rebuild Complete!"
echo "========================================="
echo ""
echo "Please test:"
echo "1. Open your browser and hard refresh: Ctrl+Shift+R (or Cmd+Shift+R)"
echo "2. Open AI Assistant chat"
echo "3. Select a machine"
echo "4. Verify you see: 'Selected machine: [name] ([model])'"
echo "5. NOT: 'aiAssistant.messages.machineSelected'"
echo ""
echo "Note: You MUST do a hard refresh to clear browser cache!"
echo ""
