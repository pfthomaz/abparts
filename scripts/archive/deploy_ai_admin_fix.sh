#!/bin/bash

echo "=== Deploying AI Assistant Admin Interface Fix ==="

# Check if we're in the right directory
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ Error: docker-compose.prod.yml not found. Are you in the abparts directory?"
    exit 1
fi

# Resolve any Git conflicts first
echo "1. Resolving Git conflicts..."
if [ -f "resolve_production_git_conflicts.sh" ]; then
    ./resolve_production_git_conflicts.sh
else
    echo "Pulling latest changes..."
    git pull origin main || {
        echo "❌ Git pull failed. Please resolve conflicts manually."
        echo "Run: git stash && git pull origin main"
        exit 1
    }
fi

# Rebuild AI Assistant container to get updated admin.html
echo "2. Rebuilding AI Assistant container..."
docker compose -f docker-compose.prod.yml build ai_assistant || {
    echo "❌ Failed to build AI Assistant container"
    exit 1
}

# Restart AI Assistant service
echo "3. Restarting AI Assistant service..."
docker compose -f docker-compose.prod.yml restart ai_assistant || {
    echo "❌ Failed to restart AI Assistant service"
    exit 1
}

# Wait for service to be ready
echo "4. Waiting for AI Assistant to be ready..."
sleep 15

# Check service health
echo "5. Checking AI Assistant health..."
if curl -f http://localhost:8001/health >/dev/null 2>&1; then
    echo "✅ AI Assistant is healthy"
else
    echo "⚠️  Health check failed, checking logs..."
    docker compose -f docker-compose.prod.yml logs --tail=20 ai_assistant
fi

# Test admin interface
echo "6. Testing admin interface..."
if curl -f https://abparts.oraseas.com/ai/admin >/dev/null 2>&1; then
    echo "✅ Admin interface is accessible"
else
    echo "⚠️  Admin interface test failed"
fi

echo ""
echo "✅ AI Assistant admin interface fix deployed!"
echo "📝 Admin interface: https://abparts.oraseas.com/ai/admin"
echo "🔧 API calls now use /ai/knowledge (fixed from /api/ai/knowledge)"
echo "📋 You can now upload knowledge documents without authentication errors"