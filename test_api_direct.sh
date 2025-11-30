#!/bin/bash

# Get the warehouse ID from the database
WAREHOUSE_ID=$(docker-compose exec -T db psql -U abparts_user -d abparts_dev -t -c "SELECT id FROM warehouses WHERE name = 'Kefalonia Fisheries SA' LIMIT 1;" | tr -d ' ')

echo "Testing API with warehouse_id: $WAREHOUSE_ID"
echo ""

# Test the API endpoint directly
echo "Calling: GET /stock-adjustments?warehouse_id=$WAREHOUSE_ID"
curl -s "http://localhost:8000/stock-adjustments?warehouse_id=$WAREHOUSE_ID" \
  -H "Authorization: Bearer $(curl -s -X POST http://localhost:8000/token -d 'username=admin@oraseas.com&password=admin123' | jq -r '.access_token')" \
  | jq '.'
