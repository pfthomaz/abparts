#!/bin/bash

# Debug AI Assistant Production Issues
# This script helps diagnose why the AI Assistant is showing "technical difficulties"

echo "🔍 Debugging AI Assistant Production Issues..."
echo "================================================"

# Step 1: Check if AI Assistant service is running
echo "1. Checking AI Assistant service status..."
docker compose -f docker-compose.prod.yml ps ai_assistant

# Step 2: Check AI Assistant logs for errors
echo ""
echo "2. Checking AI Assistant logs (last 50 lines)..."
docker compose -f docker-compose.prod.yml logs --tail=50 ai_assistant

# Step 3: Check if OpenAI API key is configured
echo ""
echo "3. Checking OpenAI API key configuration..."
if docker compose -f docker-compose.prod.yml exec ai_assistant printenv | grep -q "OPENAI_API_KEY=sk-"; then
    echo "✅ OpenAI API key is configured"
else
    echo "❌ OpenAI API key is NOT configured or invalid"
fi

# Step 4: Test AI Assistant health endpoint
echo ""
echo "4. Testing AI Assistant health endpoint..."
curl -s http://localhost:8001/health/ | jq '.' 2>/dev/null || curl -s http://localhost:8001/health/

# Step 5: Test knowledge base endpoints
echo ""
echo "5. Testing knowledge base stats..."
curl -s http://localhost:8001/knowledge/stats | jq '.' 2>/dev/null || curl -s http://localhost:8001/knowledge/stats

# Step 6: Test a simple chat request
echo ""
echo "6. Testing chat endpoint with simple request..."
curl -X POST http://localhost:8001/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello",
    "language": "en"
  }' | jq '.' 2>/dev/null || echo "Chat endpoint test failed"

# Step 7: Check environment variables in container
echo ""
echo "7. Checking AI Assistant environment variables..."
docker compose -f docker-compose.prod.yml exec ai_assistant printenv | grep -E "(OPENAI|DATABASE|REDIS)" | head -10

# Step 8: Check database connectivity
echo ""
echo "8. Testing database connectivity..."
docker compose -f docker-compose.prod.yml exec ai_assistant python -c "
import asyncio
import sys
sys.path.append('/app')
from app.database import get_database_url, test_connection

async def test_db():
    try:
        url = get_database_url()
        print(f'Database URL: {url[:50]}...')
        result = await test_connection()
        print('✅ Database connection successful')
        return True
    except Exception as e:
        print(f'❌ Database connection failed: {e}')
        return False

asyncio.run(test_db())
" 2>/dev/null || echo "Database test failed"

# Step 9: Check OpenAI API connectivity
echo ""
echo "9. Testing OpenAI API connectivity..."
docker compose -f docker-compose.prod.yml exec ai_assistant python -c "
import asyncio
import sys
sys.path.append('/app')
from app.llm_client import LLMClient

async def test_openai():
    try:
        client = LLMClient()
        await client.initialize()
        print('✅ OpenAI client initialized successfully')
        
        # Test a simple request
        from app.llm_client import ConversationMessage
        messages = [ConversationMessage(role='user', content='Hello')]
        response = await client.generate_response(messages)
        
        if response.success:
            print('✅ OpenAI API test successful')
            print(f'Response: {response.content[:100]}...')
        else:
            print(f'❌ OpenAI API test failed: {response.error_message}')
        
        await client.cleanup()
    except Exception as e:
        print(f'❌ OpenAI test failed: {e}')

asyncio.run(test_openai())
" 2>/dev/null || echo "OpenAI test failed"

echo ""
echo "🔍 Debug Summary:"
echo "=================="
echo "If you see 'technical difficulties', the most common causes are:"
echo "1. ❌ OpenAI API key not configured or invalid"
echo "2. ❌ OpenAI API rate limits or service issues"
echo "3. ❌ Database connection problems"
echo "4. ❌ Knowledge base initialization issues"
echo ""
echo "💡 Next steps:"
echo "- Check the logs above for specific error messages"
echo "- Verify OpenAI API key is valid and has credits"
echo "- Ensure all environment variables are properly set"
echo "- Check if OpenAI service is experiencing outages"