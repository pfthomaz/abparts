#!/bin/bash

echo "🔄 Restarting Frontend with Safe localStorage..."

# Navigate to frontend directory
cd frontend

# Kill any existing npm processes
echo "🛑 Stopping existing frontend processes..."
pkill -f "react-scripts start" || true
sleep 2

# Clear npm cache to avoid build issues
echo "🧹 Clearing npm cache..."
npm cache clean --force

# Start the frontend server
echo "🚀 Starting frontend server..."
npm start

echo "✅ Frontend restart complete!"
echo ""
echo "🎯 Look for this message in the startup logs:"
echo "   'Proxy created: /api -> http://localhost:8000'"
echo ""
echo "🧪 After startup:"
echo "1. Hard refresh browser (Shift+Cmd+R)"
echo "2. Login as zisis"
echo "3. Check console for reminder logs"