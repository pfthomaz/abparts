#!/bin/bash

# Fix for production deployment - handles untracked file conflicts
echo "=== Production Deployment Fix ==="
echo "Resolving untracked file conflicts and deploying AI Assistant"
echo ""

# Step 1: Remove conflicting local files
echo "1. Removing conflicting local files..."
if [ -f "production_git_pull_fix.sh" ]; then
    rm production_git_pull_fix.sh
    echo "✅ Removed local production_git_pull_fix.sh"
fi

if [ -f "deploy_ai_assistant_production.sh" ]; then
    rm deploy_ai_assistant_production.sh
    echo "✅ Removed local deploy_ai_assistant_production.sh"
fi

# Step 2: Backup current production docker-compose.yml
echo ""
echo "2. Creating backup of production configuration..."
if [ -f "docker-compose.yml" ]; then
    cp docker-compose.yml docker-compose.yml.production.backup.$(date +%Y%m%d_%H%M%S)
    echo "✅ Backup created"
fi

# Step 3: Stash any other local changes and pull
echo ""
echo "3. Stashing local changes and pulling latest code..."
git stash push -m "Production files before AI Assistant deployment $(date)"
git pull origin main

if [ $? -ne 0 ]; then
    echo "❌ Git pull failed. Please check for remaining conflicts."
    exit 1
fi

echo "✅ Successfully pulled latest changes with AI Assistant"

# Step 4: Make deployment script executable
echo ""
echo "4. Setting up deployment script..."
if [ -f "deploy_ai_assistant_production.sh" ]; then
    chmod +x deploy_ai_assistant_production.sh
    echo "✅ Made deployment script executable"
else
    echo "⚠️  deploy_ai_assistant_production.sh not found in pulled code"
fi

# Step 5: Check if AI Assistant service is in docker-compose.yml
echo ""
echo "5. Checking for AI Assistant service in docker-compose.yml..."
if grep -q "ai_assistant:" docker-compose.yml; then
    echo "✅ AI Assistant service found in docker-compose.yml"
    
    # Step 6: Deploy AI Assistant
    echo ""
    echo "6. Deploying AI Assistant..."
    echo "Building AI Assistant image..."
    docker compose build ai_assistant
    
    if [ $? -eq 0 ]; then
        echo "✅ AI Assistant image built successfully"
        
        echo "Starting AI Assistant service..."
        docker compose up -d ai_assistant
        
        if [ $? -eq 0 ]; then
            echo "✅ AI Assistant service started"
            
            echo "Rebuilding and restarting frontend..."
            docker compose build web
            docker compose up -d web
            
            echo "✅ Frontend rebuilt and restarted"
        else
            echo "❌ Failed to start AI Assistant service"
            exit 1
        fi
    else
        echo "❌ Failed to build AI Assistant image"
        exit 1
    fi
    
else
    echo "⚠️  AI Assistant service not found in docker-compose.yml"
    echo "This might be using docker-compose.prod.yml for production"
    
    if [ -f "docker-compose.prod.yml" ]; then
        echo "Found docker-compose.prod.yml - checking for AI Assistant..."
        if grep -q "ai_assistant:" docker-compose.prod.yml; then
            echo "✅ AI Assistant found in docker-compose.prod.yml"
            
            echo "Building and deploying with production compose file..."
            docker compose -f docker-compose.prod.yml build ai_assistant
            docker compose -f docker-compose.prod.yml up -d ai_assistant
            docker compose -f docker-compose.prod.yml build web
            docker compose -f docker-compose.prod.yml up -d web
            
            echo "✅ AI Assistant deployed using production configuration"
        else
            echo "❌ AI Assistant service not found in docker-compose.prod.yml either"
            echo "Please run the deployment script manually: ./deploy_ai_assistant_production.sh"
        fi
    fi
fi

# Step 7: Verification
echo ""
echo "7. Verifying deployment..."
echo "Checking service status..."
if [ -f "docker-compose.prod.yml" ]; then
    docker compose -f docker-compose.prod.yml ps
else
    docker compose ps
fi

echo ""
echo "Testing AI Assistant health endpoint..."
sleep 5
curl -f http://localhost:8001/health && echo "" || echo "⚠️  AI Assistant health check failed - service may still be starting"

echo ""
echo "=== DEPLOYMENT COMPLETE ==="
echo ""
echo "✅ AI Assistant deployment process completed!"
echo ""
echo "📋 NEXT STEPS:"
echo "1. Verify all services are running above"
echo "2. Check AI Assistant logs if needed:"
if [ -f "docker-compose.prod.yml" ]; then
    echo "   docker compose -f docker-compose.prod.yml logs ai_assistant"
else
    echo "   docker compose logs ai_assistant"
fi
echo "3. Test the AI Assistant in your web interface"
echo ""
echo "🎉 The AutoBoss AI Assistant should now be live in production!"