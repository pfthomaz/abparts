#!/bin/bash

echo "🔧 Fixing AI Assistant Knowledge Base Routes"
echo "=" * 45

# Restart AI Assistant service to apply the router prefix fix
echo "Restarting AI Assistant service..."
docker compose -f docker-compose.prod.yml restart ai_assistant

if [ $? -eq 0 ]; then
    echo "✅ AI Assistant service restarted successfully"
else
    echo "❌ Error restarting AI Assistant service"
    exit 1
fi

# Wait for service to start
echo "Waiting for service to start..."
sleep 10

# Test the knowledge base endpoints
echo ""
echo "🧪 Testing knowledge base endpoints..."

# Test stats endpoint
echo "Testing /ai/knowledge/stats..."
curl -s https://abparts.oraseas.com/ai/knowledge/stats | jq '.' 2>/dev/null || curl -s https://abparts.oraseas.com/ai/knowledge/stats

echo ""
echo "Testing /ai/knowledge/documents..."
curl -s https://abparts.oraseas.com/ai/knowledge/documents | jq '.' 2>/dev/null || curl -s https://abparts.oraseas.com/ai/knowledge/documents

echo ""
echo "✅ Knowledge base routes fix complete!"
echo ""
echo "📝 Next steps:"
echo "1. Go to https://abparts.oraseas.com/ai/admin"
echo "2. Upload knowledge base documents"
echo "3. Test the AI Assistant with specific AutoBoss questions"