#!/bin/bash

# Fix Production Translation Keys Issue
# This script rebuilds the frontend to load the correct translation files

set -e

echo "========================================="
echo "Fixing Production Translation Keys"
echo "========================================="
echo ""

# Step 1: Verify translation files exist
echo "Step 1: Verifying translation files..."
if docker compose exec web ls /app/src/locales/en.json >/dev/null 2>&1; then
    echo "✓ Translation files found"
else
    echo "✗ Translation files not found"
    exit 1
fi

echo ""

# Step 2: Check if translation key exists in file
echo "Step 2: Checking machineSelected key in en.json..."
if docker compose exec web grep -q "machineSelected" /app/src/locales/en.json; then
    echo "✓ machineSelected key exists in translation file"
    docker compose exec web grep "machineSelected" /app/src/locales/en.json | head -2
else
    echo "✗ machineSelected key not found"
    exit 1
fi

echo ""

# Step 3: Rebuild frontend
echo "Step 3: Rebuilding frontend..."
echo "This will take 2-3 minutes..."
docker compose exec web npm run build

if [ $? -eq 0 ]; then
    echo "✓ Frontend rebuilt successfully"
else
    echo "✗ Frontend build failed"
    exit 1
fi

echo ""

# Step 4: Restart web container
echo "Step 4: Restarting web container..."
docker compose restart web

if [ $? -eq 0 ]; then
    echo "✓ Web container restarted"
else
    echo "✗ Container restart failed"
    exit 1
fi

echo ""

# Step 5: Wait for container to be ready
echo "Step 5: Waiting for web container to be ready..."
sleep 5

WEB_STATUS=$(docker compose ps web | grep -c "Up" || echo "0")
if [ "$WEB_STATUS" -gt 0 ]; then
    echo "✓ Web container is running"
else
    echo "✗ Web container is not running"
    docker compose logs web --tail=20
    exit 1
fi

echo ""
echo "========================================="
echo "Translation Fix Complete!"
echo "========================================="
echo ""
echo "Please test:"
echo "1. Open AI Assistant chat"
echo "2. Select a machine"
echo "3. Verify you see: 'Selected machine: [name] ([model])'"
echo "4. NOT: 'aiAssistant.messages.machineSelected'"
echo ""
echo "If still showing keys, try hard refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)"
echo ""
