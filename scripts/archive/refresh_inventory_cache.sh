#!/bin/bash

echo "Refreshing inventory cache with calculated values..."
echo ""

# Call the API endpoint to refresh cache
curl -X POST "http://localhost:8000/inventory/calculated/refresh-cache" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

echo ""
echo "Done! Inventory cache refreshed."
echo "Reload the page in your browser to see updated values."
