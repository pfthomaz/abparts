#!/bin/bash
echo "Restarting API..."
docker-compose restart api
echo "Waiting for API to start..."
sleep 3
echo ""
echo "API is ready. Try updating the organization again."
echo "If it fails, check logs with: docker-compose logs --tail=50 api"
