#!/bin/bash

# AI Assistant Production Deployment Script
# This script deploys translation fixes, new icon, and troubleshooting features

set -e  # Exit on error

echo "========================================="
echo "AI Assistant Production Deployment"
echo "========================================="
echo ""

# Step 1: Fix troubleshooting_steps table schema
echo "Step 1: Fixing troubleshooting_steps table schema..."
cat fix_troubleshooting_steps_production.sql | docker compose exec -T db psql -U abparts_user -d abparts_prod

if [ $? -eq 0 ]; then
    echo "✓ Database schema fixed successfully"
else
    echo "✗ Database schema fix failed"
    exit 1
fi

echo ""

# Step 2: Pull latest code
echo "Step 2: Pulling latest code from repository..."
git pull origin main

if [ $? -eq 0 ]; then
    echo "✓ Code updated successfully"
else
    echo "✗ Git pull failed"
    exit 1
fi

echo ""

# Step 3: Rebuild frontend
echo "Step 3: Rebuilding frontend with new changes..."
docker compose exec web npm run build

if [ $? -eq 0 ]; then
    echo "✓ Frontend rebuilt successfully"
else
    echo "✗ Frontend build failed"
    exit 1
fi

echo ""

# Step 4: Restart containers
echo "Step 4: Restarting containers..."
docker compose restart web ai_assistant

if [ $? -eq 0 ]; then
    echo "✓ Containers restarted successfully"
else
    echo "✗ Container restart failed"
    exit 1
fi

echo ""

# Step 5: Verify services are running
echo "Step 5: Verifying services..."
sleep 5  # Give services time to start

# Check web service
WEB_STATUS=$(docker compose ps web | grep -c "Up" || echo "0")
if [ "$WEB_STATUS" -gt 0 ]; then
    echo "✓ Web service is running"
else
    echo "✗ Web service is not running"
fi

# Check AI assistant service
AI_STATUS=$(docker compose ps ai_assistant | grep -c "Up" || echo "0")
if [ "$AI_STATUS" -gt 0 ]; then
    echo "✓ AI Assistant service is running"
else
    echo "✗ AI Assistant service is not running"
fi

echo ""
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "Next Steps:"
echo "1. Test AI Assistant chat widget"
echo "2. Verify AutoBoss icon appears (larger size)"
echo "3. Test step-by-step troubleshooting"
echo "4. Check translation placeholders display correctly"
echo ""
echo "Test with: dthomaz/amFT1999!"
echo ""
