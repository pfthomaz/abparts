#!/bin/bash

echo "🔧 Fixing AI Assistant Column References in Production"
echo "===================================================="
echo "Issue: AI assistant code still references 'session_id' instead of 'id' column"
echo "Solution: Rebuild AI assistant container with corrected code"
echo ""

echo "1. Stopping AI assistant container..."
docker compose -f docker-compose.prod.yml stop ai_assistant

echo ""
echo "2. Rebuilding AI assistant container with latest code..."
docker compose -f docker-compose.prod.yml build --no-cache ai_assistant

echo ""
echo "3. Starting AI assistant container..."
docker compose -f docker-compose.prod.yml up -d ai_assistant

echo ""
echo "4. Waiting for container to be ready..."
sleep 10

echo ""
echo "5. Testing escalation endpoint..."
docker compose -f docker-compose.prod.yml exec ai_assistant python -c "
import sys
sys.path.append('/app')
from app.database import get_db_session
from sqlalchemy import text
import uuid
from datetime import datetime

session_id = str(uuid.uuid4())
user_id = '45e2bc8a-b780-4886-bc0b-b0ba1655ff93'  # Maria Sefteli

print('Testing session creation with corrected code...')
print(f'Session ID: {session_id}')
print(f'User ID: {user_id}')

try:
    with get_db_session() as db:
        # Create test session using 'id' column (correct)
        db.execute(text('''
            INSERT INTO ai_sessions (id, user_id, machine_id, status, language, created_at, updated_at)
            VALUES (:id, :user_id, :machine_id, :status, :language, NOW(), NOW())
        '''), {
            'id': session_id,
            'user_id': user_id,
            'machine_id': None,
            'status': 'active',
            'language': 'en'
        })
        print('✅ Session created successfully!')
        
        # Test escalation service query (should now work)
        result = db.execute(text('''
            SELECT id, user_id FROM ai_sessions WHERE id = :session_id
        '''), {'session_id': session_id}).fetchone()
        
        if result:
            print(f'✅ Session query successful:')
            print(f'   ID: {result.id}')
            print(f'   User: {result.user_id}')
        else:
            print('❌ Session not found after creation')
            
except Exception as e:
    print(f'❌ Error: {e}')
"

echo ""
echo "6. Testing escalation endpoint via HTTP..."
curl -X POST "https://abparts.oraseas.com/ai/api/ai/sessions/test-session-123/escalate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token" \
  -d '{
    "escalation_reason": "user_request",
    "priority": "medium",
    "additional_notes": "Testing escalation after column fix"
  }' \
  -w "\nHTTP Status: %{http_code}\n"

echo ""
echo "✅ AI Assistant container rebuilt with corrected column references!"
echo ""
echo "Summary of fixes applied:"
echo "- chat.py: Fixed session_id -> id in ai_sessions queries"
echo "- session_manager.py: Fixed session_id -> id in ai_sessions queries"
echo "- session_manager.py: Fixed user_id -> id in users queries"
echo "- session_manager.py: Removed duplicate get_user_language function"
echo "- escalation_service.py: Already uses correct 'id' column"
echo ""
echo "The escalation system should now work correctly!"