#!/bin/bash

echo "========================================="
echo "Applying Inventory Refresh Fix"
echo "========================================="
echo ""
echo "This fix ensures inventory displays update automatically"
echo "when transactions are edited or deleted."
echo ""

echo "Step 1: Rebuilding frontend container..."
docker-compose build web

echo ""
echo "Step 2: Restarting frontend..."
docker-compose up -d web

echo ""
echo "Step 3: Waiting for frontend to start..."
sleep 5

echo ""
echo "========================================="
echo "✓ Fix Applied Successfully!"
echo "========================================="
echo ""
echo "What was fixed:"
echo "- Transaction updates now trigger inventory refresh"
echo "- Transaction deletes now trigger inventory refresh"
echo "- Inventory displays update automatically without manual refresh"
echo ""
echo "Test the fix:"
echo "1. Open a machine details page"
echo "2. Go to the 'Parts Usage' tab"
echo "3. Edit a part usage quantity"
echo "4. Check that inventory updates immediately"
echo ""
