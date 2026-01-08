#!/bin/bash

# Simple production Git pull fix for AI Assistant deployment
# Run this on the production server

echo "=== Production Git Pull Fix ==="
echo "Resolving docker-compose.yml conflict for AI Assistant deployment"
echo ""

# Backup current production docker-compose.yml
echo "1. Creating backup..."
cp docker-compose.yml docker-compose.yml.production.backup.$(date +%Y%m%d_%H%M%S)
echo "✅ Backup created"

# Stash local changes and pull
echo ""
echo "2. Stashing local changes and pulling from main..."
git stash push -m "Production docker-compose.yml before AI Assistant merge"
git pull origin main

if [ $? -eq 0 ]; then
    echo "✅ Successfully pulled latest changes with AI Assistant"
    echo ""
    echo "📋 NEXT STEPS:"
    echo "1. Run the AI Assistant deployment script:"
    echo "   ./deploy_ai_assistant_production.sh"
    echo ""
    echo "2. Or manually deploy with:"
    echo "   docker compose -f docker-compose.prod.yml build ai_assistant"
    echo "   docker compose -f docker-compose.prod.yml up -d ai_assistant"
    echo "   docker compose -f docker-compose.prod.yml build web"
    echo "   docker compose -f docker-compose.prod.yml up -d web"
else
    echo "❌ Git pull failed. Manual resolution needed."
    echo "Check git status and resolve conflicts manually."
fi