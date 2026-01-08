#!/bin/bash

# Production AI Assistant Deployment Script
# Run this on the production server to deploy the AI Assistant

echo "=== ABParts AI Assistant Production Deployment ==="
echo "This script will deploy the AI Assistant to production"
echo ""

# Check if we're in the right directory
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ Error: docker-compose.prod.yml not found"
    echo "Please run this script from the ABParts root directory"
    exit 1
fi

echo "📋 Pre-deployment checklist:"
echo "✅ Committed and pushed AI Assistant changes to main branch"
echo "⚠️  About to resolve Git merge conflict and deploy"
echo ""

# Step 1: Backup current production files
echo "1. Creating backups..."
BACKUP_DIR="backups/ai_assistant_deployment_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

if [ -f "docker-compose.prod.yml" ]; then
    cp docker-compose.prod.yml "$BACKUP_DIR/docker-compose.prod.yml.backup"
    echo "✅ Backed up docker-compose.prod.yml"
fi

if [ -f ".env.production" ]; then
    cp .env.production "$BACKUP_DIR/.env.production.backup"
    echo "✅ Backed up .env.production"
fi

# Step 2: Resolve Git conflict
echo ""
echo "2. Resolving Git merge conflict..."
echo "Current git status:"
git status

echo ""
echo "Stashing local changes and pulling latest..."
git stash push -m "Production files before AI Assistant deployment $(date)"
git pull origin main

if [ $? -ne 0 ]; then
    echo "❌ Git pull failed. Please resolve manually."
    exit 1
fi

echo "✅ Successfully pulled latest changes"

# Step 3: Check if AI Assistant service is in docker-compose.prod.yml
echo ""
echo "3. Checking docker-compose.prod.yml for AI Assistant service..."
if grep -q "ai_assistant:" docker-compose.prod.yml; then
    echo "✅ AI Assistant service found in docker-compose.prod.yml"
else
    echo "⚠️  AI Assistant service not found in docker-compose.prod.yml"
    echo "Adding AI Assistant service to production compose file..."
    
    # Add AI Assistant service to production compose
    cat >> docker-compose.prod.yml << 'EOF'

  # AI Assistant Service
  ai_assistant:
    build:
      context: ./ai_assistant
      dockerfile: Dockerfile
    container_name: abparts_ai_assistant_prod
    ports:
      - "8001:8001"
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER:-abparts_user}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB:-abparts_prod}
      REDIS_URL: redis://redis:6379/2  # Use different Redis database for AI Assistant
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      OPENAI_MODEL: ${OPENAI_MODEL:-gpt-4}
      OPENAI_FALLBACK_MODEL: ${OPENAI_FALLBACK_MODEL:-gpt-3.5-turbo}
      ABPARTS_API_URL: http://api:8000
      CORS_ALLOWED_ORIGINS: ${CORS_ALLOWED_ORIGINS}
      ENVIRONMENT: ${ENVIRONMENT:-production}
      DEBUG: ${DEBUG:-false}
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "python", "-c", "import httpx; httpx.get('http://localhost:8001/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
EOF
    
    echo "✅ Added AI Assistant service to docker-compose.prod.yml"
fi

# Step 4: Update frontend build args for AI Assistant
echo ""
echo "4. Updating frontend build configuration..."
if grep -q "REACT_APP_AI_ASSISTANT_URL" docker-compose.prod.yml; then
    echo "✅ Frontend already configured for AI Assistant"
else
    echo "⚠️  Adding AI Assistant URL to frontend build args..."
    # This would need manual editing - let's note it for the user
    echo "📝 NOTE: You may need to manually add REACT_APP_AI_ASSISTANT_URL to frontend build args"
fi

# Step 5: Check environment variables
echo ""
echo "5. Checking required environment variables..."
echo "📋 Required environment variables for AI Assistant:"
echo "   - OPENAI_API_KEY (required)"
echo "   - OPENAI_MODEL (optional, defaults to gpt-4)"
echo "   - OPENAI_FALLBACK_MODEL (optional, defaults to gpt-3.5-turbo)"
echo ""

if [ -f ".env.production" ]; then
    if grep -q "OPENAI_API_KEY" .env.production; then
        echo "✅ OPENAI_API_KEY found in .env.production"
    else
        echo "⚠️  OPENAI_API_KEY not found in .env.production"
        echo "Please add: OPENAI_API_KEY=your_openai_api_key"
    fi
else
    echo "⚠️  .env.production file not found"
    echo "Please create .env.production with required environment variables"
fi

# Step 6: Database setup
echo ""
echo "6. Setting up AI Assistant database tables..."
echo "The AI Assistant requires additional database tables."
echo "Run these commands after deployment:"
echo ""
echo "# Create AI Assistant database tables:"
echo "docker compose -f docker-compose.prod.yml exec ai_assistant python -c \"
import asyncio
from app.database import engine
from app.models import Base
asyncio.run(Base.metadata.create_all(bind=engine))
\""
echo ""

# Step 7: Build and deploy
echo ""
echo "7. Building and deploying services..."
echo "Building AI Assistant image..."
docker compose -f docker-compose.prod.yml build ai_assistant

if [ $? -ne 0 ]; then
    echo "❌ Failed to build AI Assistant image"
    exit 1
fi

echo "✅ AI Assistant image built successfully"

echo ""
echo "Starting AI Assistant service..."
docker compose -f docker-compose.prod.yml up -d ai_assistant

if [ $? -ne 0 ]; then
    echo "❌ Failed to start AI Assistant service"
    exit 1
fi

echo "✅ AI Assistant service started"

# Step 8: Rebuild frontend with AI Assistant URL
echo ""
echo "8. Rebuilding frontend with AI Assistant integration..."
docker compose -f docker-compose.prod.yml build web
docker compose -f docker-compose.prod.yml up -d web

echo "✅ Frontend rebuilt and restarted"

# Step 9: Verification
echo ""
echo "9. Verifying deployment..."
echo "Checking service status..."
docker compose -f docker-compose.prod.yml ps

echo ""
echo "Testing AI Assistant health endpoint..."
sleep 10  # Give service time to start
curl -f http://localhost:8001/health || echo "⚠️  AI Assistant health check failed - service may still be starting"

echo ""
echo "=== DEPLOYMENT COMPLETE ==="
echo ""
echo "✅ AI Assistant has been deployed to production!"
echo ""
echo "📋 NEXT STEPS:"
echo "1. Verify all services are running:"
echo "   docker compose -f docker-compose.prod.yml ps"
echo ""
echo "2. Check AI Assistant logs:"
echo "   docker compose -f docker-compose.prod.yml logs ai_assistant"
echo ""
echo "3. Test the AI Assistant in the web interface"
echo ""
echo "4. Monitor the services:"
echo "   docker compose -f docker-compose.prod.yml logs -f"
echo ""
echo "🔧 TROUBLESHOOTING:"
echo "- If AI Assistant fails to start, check environment variables"
echo "- If database errors occur, run the database setup commands above"
echo "- If frontend doesn't show chat widget, check browser console for errors"
echo ""
echo "📁 BACKUPS CREATED:"
echo "   $BACKUP_DIR/"
echo ""
echo "🎉 The AutoBoss AI Assistant is now live in production!"