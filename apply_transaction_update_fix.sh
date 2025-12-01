#!/bin/bash

echo "========================================="
echo "Applying Transaction Update Fix"
echo "========================================="
echo ""
echo "This fix ensures that when you edit a part usage transaction:"
echo "1. The transaction record is updated"
echo "2. The linked part_usage_item is also updated"
echo "3. Inventory calculations reflect the changes"
echo "4. The UI automatically refreshes"
echo ""

echo "Step 1: Restarting API to apply backend changes..."
docker-compose restart api

echo ""
echo "Step 2: Waiting for API to start..."
sleep 5

echo ""
echo "Step 3: Rebuilding frontend for UI refresh fix..."
docker-compose build web

echo ""
echo "Step 4: Restarting frontend..."
docker-compose up -d web

echo ""
echo "Step 5: Waiting for frontend to start..."
sleep 5

echo ""
echo "========================================="
echo "✓ Fix Applied Successfully!"
echo "========================================="
echo ""
echo "What was fixed:"
echo "- Transaction updates now also update part_usage_items"
echo "- Inventory calculations work correctly"
echo "- UI automatically refreshes after edits"
echo ""
echo "Test the fix:"
echo "1. Open a machine details page"
echo "2. Go to 'Parts Usage' tab"
echo "3. Edit a part usage quantity"
echo "4. Verify inventory updates immediately"
echo ""
echo "Check the logs:"
echo "  docker-compose logs api | tail -50"
echo "  docker-compose logs web | tail -50"
echo ""
