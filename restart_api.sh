#!/bin/bash
echo "Restarting API to pick up route changes..."
docker-compose restart api
echo "Waiting for API to be ready..."
sleep 5
echo "Testing stock adjustments endpoint..."
curl -s http://localhost:8000/stock-adjustments | head -20
echo ""
echo "API restarted!"
