#!/bin/bash

echo "=== Deploying AI Assistant Admin Interface Fix ==="

# Pull latest changes
echo "1. Pulling latest changes..."
git pull origin main

# Rebuild AI Assistant container to get updated admin.html
echo "2. Rebuilding AI Assistant container..."
docker compose -f docker-compose.prod.yml build ai_assistant

# Restart AI Assistant service
echo "3. Restarting AI Assistant service..."
docker compose -f docker-compose.prod.yml restart ai_assistant

# Wait for service to be ready
echo "4. Waiting for AI Assistant to be ready..."
sleep 10

# Check service health
echo "5. Checking AI Assistant health..."
curl -f http://localhost:8001/health || echo "❌ Health check failed"

echo "✅ AI Assistant admin interface fix deployed!"
echo "📝 Admin interface should now work at: https://abparts.oraseas.com/ai/admin"
echo "🔧 API calls will now use /ai/knowledge instead of /api/ai/knowledge"