#!/bin/bash
echo "Rebuilding frontend with organization logos on cards..."
docker-compose build web && docker-compose up -d web
echo "Waiting for frontend to start..."
sleep 3
echo ""
echo "✓ Done! Organization cards now show:"
echo "  - Logo image if uploaded (12x12 rounded square)"
echo "  - 'No Logo' placeholder if not uploaded"
echo "  - Logo appears next to organization name"
