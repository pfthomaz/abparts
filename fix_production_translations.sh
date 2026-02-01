#!/bin/bash

# Fix Production Translation Keys Issue
# This script rebuilds the frontend to load the correct translation files

set -e

echo "========================================="
echo "Fixing Production Translation Keys"
echo "========================================="
echo ""

# Step 1: Check if web container is running
echo "Step 1: Checking web container status..."
if ! docker compose ps web | grep -q "Up"; then
    echo "✗ Web container is not running"
    echo "Starting web container..."
    docker compose up -d web
    sleep 5
fi
echo "✓ Web container is running"

echo ""

# Step 2: Verify translation files exist in source
echo "Step 2: Verifying translation files in source..."
if [ -f "frontend/src/locales/en.json" ]; then
    echo "✓ Translation files found in source"
    # Check for the key
    if grep -q "machineSelected" frontend/src/locales/en.json; then
        echo "✓ machineSelected key exists in translation file"
    else
        echo "⚠ machineSelected key not found, but continuing..."
    fi
else
    echo "✗ Translation files not found in source"
    exit 1
fi

echo ""

# Step 3: Rebuild frontend inside container
echo "Step 3: Rebuilding frontend..."
echo "This will take 2-3 minutes..."

# Run npm build inside the container
docker compose exec -T web npm run build

if [ $? -eq 0 ]; then
    echo "✓ Frontend rebuilt successfully"
else
    echo "✗ Frontend build failed"
    echo "Checking logs..."
    docker compose logs web --tail=50
    exit 1
fi

echo ""

# Step 4: Restart web container to serve new build
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
