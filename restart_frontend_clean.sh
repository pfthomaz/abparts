#!/bin/bash

echo "🛑 Stopping all Node/React processes..."

# Kill any running npm/node processes
pkill -f "react-scripts" || true
pkill -f "node.*frontend" || true
pkill -f "npm start" || true

# Wait a moment
sleep 2

echo "🧹 Cleaning build cache..."
cd frontend

# Remove build cache
rm -rf node_modules/.cache
rm -rf build
rm -rf .cache

echo "✅ Cleanup complete!"
echo ""
echo "🚀 Now start fresh with:"
echo "   cd frontend"
echo "   npm start"