#!/bin/bash
echo "Rebuilding API container to clear Python cache..."
docker-compose build --no-cache api
echo ""
echo "Starting API..."
docker-compose up -d api
echo ""
echo "Waiting for API to start..."
sleep 10
echo ""
echo "Testing API..."
./test_stock_adjustments_api.sh
