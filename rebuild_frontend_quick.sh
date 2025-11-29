#!/bin/bash
echo "Rebuilding frontend..."
docker-compose build web && docker-compose up -d web
echo "Waiting for frontend to start..."
sleep 3
echo "✓ Done! Organization logos should now persist when reopening the edit modal."
