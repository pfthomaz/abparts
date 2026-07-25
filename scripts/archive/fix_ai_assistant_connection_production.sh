#!/bin/bash

# Fix AI Assistant Connection in Production
# This script fixes the frontend connection to AI Assistant service

echo "🔧 Fixing AI Assistant connection in production..."

# Step 1: Rebuild the frontend with the fix
echo "📦 Rebuilding frontend with AI Assistant connection fix..."
cd frontend

# Install dependencies (in case there are any updates)
npm install

# Build the production frontend
npm run build

# Step 2: Copy the built files to the production location
echo "📁 Copying built files to production location..."
sudo cp -r build/* /home/abparts/abparts/frontend/build/

# Step 3: Restart nginx to ensure clean state
echo "🔄 Restarting nginx..."
sudo systemctl restart nginx

# Step 4: Test the AI Assistant connection
echo "🧪 Testing AI Assistant connection..."
echo "Testing nginx proxy to AI Assistant..."
curl -s -o /dev/null -w "%{http_code}" https://abparts.oraseas.com/ai/health/

if [ $? -eq 0 ]; then
    echo "✅ AI Assistant proxy is working"
else
    echo "❌ AI Assistant proxy test failed"
fi

# Step 5: Check nginx logs for any errors
echo "📋 Checking nginx logs for errors..."
sudo tail -n 10 /var/log/nginx/abparts_error.log

echo ""
echo "🎉 AI Assistant connection fix deployment complete!"
echo ""
echo "📝 What was fixed:"
echo "- Frontend now uses '/ai/api/ai/chat' in production instead of 'http://localhost:8001/api/ai/chat'"
echo "- This routes through nginx proxy correctly"
echo "- Development environment still uses direct connection"
echo ""
echo "🧪 To test:"
echo "1. Open https://abparts.oraseas.com"
echo "2. Click the AI Assistant chat button"
echo "3. Send a message - it should work without connection errors"
echo ""
echo "🔍 If issues persist, check:"
echo "- AI Assistant service status: docker compose -f docker-compose.prod.yml ps ai_assistant"
echo "- AI Assistant logs: docker compose -f docker-compose.prod.yml logs ai_assistant"
echo "- Nginx error logs: sudo tail -f /var/log/nginx/abparts_error.log"