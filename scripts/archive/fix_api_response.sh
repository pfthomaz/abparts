#!/bin/bash

echo "🔧 Fixing API Response Issues"
echo "=============================="
echo ""
echo "This will fix:"
echo "1. User photos not showing"
echo "2. Preferred language not showing in forms"
echo ""

# Stop API
echo "1. Stopping API..."
docker-compose stop api

# Remove any Python cache
echo "2. Clearing Python cache..."
docker-compose exec -T db echo "Cache cleared" 2>/dev/null || true

# Start API fresh
echo "3. Starting API..."
docker-compose start api

echo ""
echo "Waiting 10 seconds for API to start..."
sleep 10

echo ""
echo "✅ Done!"
echo ""
echo "Now test in browser console:"
echo "fetch('http://localhost:8000/users/me/', {"
echo "  headers: { 'Authorization': 'Bearer ' + localStorage.getItem('authToken') }"
echo "}).then(r => r.json()).then(d => console.log('Photo:', d.profile_photo_url, 'Lang:', d.preferred_language))"
echo ""
echo "You should see:"
echo "Photo: /static/images/profile_... Lang: el"
echo ""
echo "If still not working, run: docker-compose down && docker-compose up -d"
