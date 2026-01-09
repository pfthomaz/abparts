#!/bin/bash

# Fix AI Assistant OpenAI Configuration
# This script helps fix common OpenAI API configuration issues

echo "🔧 Fixing AI Assistant OpenAI Configuration..."
echo "=============================================="

# Step 1: Check current .env file for OpenAI configuration
echo "1. Checking current .env configuration..."
if [ -f .env ]; then
    if grep -q "OPENAI_API_KEY" .env; then
        echo "✅ OPENAI_API_KEY found in .env"
        # Check if it looks like a valid key (starts with sk-)
        if grep "OPENAI_API_KEY" .env | grep -q "sk-"; then
            echo "✅ API key format looks correct"
        else
            echo "❌ API key format looks incorrect (should start with sk-)"
        fi
    else
        echo "❌ OPENAI_API_KEY not found in .env"
        echo "Adding OpenAI configuration to .env..."
        
        # Add OpenAI configuration
        cat >> .env << 'EOF'

# AI Assistant Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
OPENAI_FALLBACK_MODEL=gpt-3.5-turbo
EOF
        echo "✅ Added OpenAI configuration template to .env"
        echo "⚠️  Please update OPENAI_API_KEY with your actual API key"
    fi
else
    echo "❌ .env file not found"
    exit 1
fi

# Step 2: Check if the API key is properly formatted
echo ""
echo "2. Validating API key format..."
API_KEY=$(grep "OPENAI_API_KEY" .env | cut -d'=' -f2)
if [[ $API_KEY == sk-* ]]; then
    echo "✅ API key format is correct"
    
    # Test the API key (basic format check)
    if [ ${#API_KEY} -gt 50 ]; then
        echo "✅ API key length looks reasonable"
    else
        echo "⚠️  API key seems too short, please verify"
    fi
else
    echo "❌ API key format is incorrect"
    echo "OpenAI API keys should start with 'sk-' and be about 51 characters long"
    echo "Example: sk-proj-abcd1234..."
fi

# Step 3: Restart AI Assistant service with new configuration
echo ""
echo "3. Restarting AI Assistant service..."
docker compose -f docker-compose.prod.yml restart ai_assistant

# Wait for service to start
echo "Waiting for AI Assistant to start..."
sleep 10

# Step 4: Test the configuration
echo ""
echo "4. Testing AI Assistant with new configuration..."
curl -s http://localhost:8001/health/ | jq '.' 2>/dev/null || curl -s http://localhost:8001/health/

# Step 5: Test a simple chat request
echo ""
echo "5. Testing chat functionality..."
CHAT_RESPONSE=$(curl -s -X POST http://localhost:8001/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, can you help me?",
    "language": "en"
  }')

if echo "$CHAT_RESPONSE" | grep -q "technical difficulties"; then
    echo "❌ Still getting technical difficulties error"
    echo "Response: $CHAT_RESPONSE"
    echo ""
    echo "🔍 Troubleshooting steps:"
    echo "1. Verify your OpenAI API key is correct and active"
    echo "2. Check if your OpenAI account has available credits"
    echo "3. Check OpenAI service status at https://status.openai.com/"
    echo "4. Run debug script: ./debug_ai_assistant_production.sh"
elif echo "$CHAT_RESPONSE" | grep -q "response"; then
    echo "✅ Chat functionality is working!"
    echo "AI Assistant is now responding correctly"
else
    echo "⚠️  Unexpected response format:"
    echo "$CHAT_RESPONSE"
fi

echo ""
echo "🎉 Configuration update complete!"
echo ""
echo "📝 Important notes:"
echo "- Make sure your OpenAI API key is valid and has credits"
echo "- The API key should start with 'sk-proj-' or 'sk-'"
echo "- Check https://platform.openai.com/account/billing for credit balance"
echo "- If issues persist, run: ./debug_ai_assistant_production.sh"