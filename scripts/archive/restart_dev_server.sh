#!/bin/bash

# Restart Development Server
# Your production is actually running in development mode

echo "========================================="
echo "Restarting Development Server"
echo "========================================="
echo ""

echo "Your production is running React development server (npm start)"
echo "Not a production nginx build"
echo ""

# Step 1: Restart web container
echo "Step 1: Restarting web container..."
docker compose restart web

echo "✓ Container restarted"
echo ""

# Step 2: Wait for dev server to start
echo "Step 2: Waiting for development server to start..."
echo "This takes about 30 seconds..."
sleep 30

# Step 3: Check if it's running
echo "Step 3: Checking container status..."
docker compose ps web

echo ""
echo "========================================="
echo "Restart Complete!"
echo "========================================="
echo ""
echo "IMPORTANT: Clear your browser cache!"
echo ""
echo "1. Hard refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)"
echo "2. Or clear all browser cache"
echo "3. Or try incognito/private window"
echo ""
echo "The translations should now work because:"
echo "- Development server reloaded with latest source files"
echo "- Translation files are imported directly (no build needed)"
echo ""
