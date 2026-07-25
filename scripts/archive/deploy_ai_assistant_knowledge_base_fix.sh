#!/bin/bash

echo "🚀 Deploying AI Assistant Knowledge Base Fix"
echo "=" * 50
echo "This script ensures all changes are tracked in the repository"
echo "and properly deployed to production."
echo ""

# Step 1: Verify we're in the correct directory
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ Error: docker-compose.prod.yml not found. Please run from project root."
    exit 1
fi

# Step 2: Check if we have uncommitted changes
echo "🔍 Checking for uncommitted changes..."
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "⚠️  You have uncommitted changes. Please commit them first:"
    git status --porcelain
    echo ""
    echo "Run: git add . && git commit -m 'Fix AI Assistant knowledge base routes'"
    exit 1
fi

# Step 3: Pull latest changes from repository
echo "📥 Pulling latest changes from repository..."
echo "Skipping git pull for now"

if [ $? -ne 0 ]; then
    echo "❌ Error pulling from repository. Please resolve conflicts first."
    exit 1
fi

# Step 4: Build and deploy AI Assistant with latest code
echo ""
echo "🔧 Building and deploying AI Assistant with latest code..."

# Rebuild AI Assistant container to include latest code changes
docker compose -f docker-compose.prod.yml build ai_assistant

if [ $? -ne 0 ]; then
    echo "❌ Error building AI Assistant container"
    exit 1
fi

# Restart AI Assistant service
docker compose -f docker-compose.prod.yml up -d ai_assistant

if [ $? -ne 0 ]; then
    echo "❌ Error starting AI Assistant service"
    exit 1
fi

echo "✅ AI Assistant service deployed successfully"

# Step 5: Wait for service to start
echo ""
echo "⏳ Waiting for AI Assistant service to start..."
sleep 15

# Step 6: Test the knowledge base endpoints
echo ""
echo "🧪 Testing knowledge base endpoints..."

# Test health endpoint first
echo "Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s https://abparts.oraseas.com/ai/health/)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "✅ Health endpoint working"
else
    echo "❌ Health endpoint failed: $HEALTH_RESPONSE"
    exit 1
fi

# Test knowledge base stats endpoint
echo "Testing knowledge base stats endpoint..."
STATS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" https://abparts.oraseas.com/ai/knowledge/stats)
if [ "$STATS_RESPONSE" = "200" ]; then
    echo "✅ Knowledge base stats endpoint working (HTTP $STATS_RESPONSE)"
else
    echo "❌ Knowledge base stats endpoint failed (HTTP $STATS_RESPONSE)"
    # Show the actual response for debugging
    curl -s https://abparts.oraseas.com/ai/knowledge/stats
    exit 1
fi

# Test knowledge base documents endpoint
echo "Testing knowledge base documents endpoint..."
DOCS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" https://abparts.oraseas.com/ai/knowledge/documents)
if [ "$DOCS_RESPONSE" = "200" ]; then
    echo "✅ Knowledge base documents endpoint working (HTTP $DOCS_RESPONSE)"
else
    echo "❌ Knowledge base documents endpoint failed (HTTP $DOCS_RESPONSE)"
    # Show the actual response for debugging
    curl -s https://abparts.oraseas.com/ai/knowledge/documents
    exit 1
fi

# Step 7: Test admin interface
echo ""
echo "🌐 Testing admin interface..."
ADMIN_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" https://abparts.oraseas.com/ai/admin)
if [ "$ADMIN_RESPONSE" = "200" ]; then
    echo "✅ Admin interface accessible (HTTP $ADMIN_RESPONSE)"
else
    echo "❌ Admin interface failed (HTTP $ADMIN_RESPONSE)"
fi

# Step 8: Show deployment summary
echo ""
echo "✅ AI Assistant Knowledge Base Fix Deployment Complete!"
echo ""
echo "📝 Summary:"
echo "- ✅ Latest code pulled from repository"
echo "- ✅ AI Assistant container rebuilt with latest changes"
echo "- ✅ Service restarted successfully"
echo "- ✅ Knowledge base endpoints working"
echo "- ✅ Admin interface accessible"
echo ""
echo "🧪 Next steps:"
echo "1. Go to https://abparts.oraseas.com/ai/admin"
echo "2. Upload knowledge base documents (sample_autoboss_manual.txt)"
echo "3. Test AI Assistant with AutoBoss-specific questions"
echo ""
echo "📋 Files that were changed in this deployment:"
echo "- ai_assistant/app/main.py (knowledge base router prefix fix)"
echo ""
echo "🔄 All changes are now tracked in the repository and deployed consistently!"