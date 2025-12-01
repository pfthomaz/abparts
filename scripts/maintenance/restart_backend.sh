#!/bin/bash

echo "🔄 Restarting Backend to Load New Endpoints..."

# Restart the API container
docker-compose restart api

echo "⏳ Waiting for backend to start..."
sleep 5

# Check if backend is responding
echo "🧪 Testing backend connection..."
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ || echo "Backend not responding"

echo "✅ Backend restart complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Hard refresh your browser (Shift+Cmd+R)"
echo "2. Login as zisis"
echo "3. Check browser console for logs"
echo "4. Try entering machine hours"