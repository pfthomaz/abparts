#!/bin/bash
echo "=== Applying all image fixes ==="
echo ""
echo "1. Restarting API (for logo_url in responses)..."
docker-compose restart api
echo ""
echo "2. Rebuilding frontend (for refreshUser calls)..."
docker-compose build web
echo ""
echo "3. Restarting frontend..."
docker-compose up -d web
echo ""
echo "Waiting for services to start..."
sleep 5
echo ""
echo "✓ Done! Changes applied:"
echo "  - Organization responses now include logo_url with cache-busting"
echo "  - Profile photo/logo uploads now refresh user context automatically"
echo "  - Header will update immediately after photo/logo changes"
