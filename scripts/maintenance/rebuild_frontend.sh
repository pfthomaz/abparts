#!/bin/bash
echo "Rebuilding frontend to apply logo fix..."
docker-compose build web
echo ""
echo "Restarting frontend..."
docker-compose up -d web
echo ""
echo "Waiting for frontend to start..."
sleep 3
echo ""
echo "✓ Done! Try updating the organization again."
