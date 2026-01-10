#!/bin/bash
echo "🔍 Debugging Production Escalation Issue"
echo "========================================"

echo "1. Checking AI Assistant logs for errors..."
docker compose -f docker-compose.prod.yml logs ai_assistant | tail -20

echo -e "\n2. Checking for specific escalation errors..."
docker compose -f docker-compose.prod.yml logs ai_assistant | grep -i "escalation\|error\|failed" | tail -10

echo -e "\n3. Checking session creation..."
docker compose -f docker-compose.prod.yml logs ai_assistant | grep -i "session" | tail -5

echo -e "\n4. Testing database connection..."
docker compose -f docker-compose.prod.yml exec ai_assistant python -c "
from app.database import get_db_session
try:
    with get_db_session() as db:
        result = db.execute('SELECT COUNT(*) FROM ai_sessions').fetchone()
        print(f'✅ Database connection OK - {result[0]} sessions in database')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"

echo -e "\n5. Checking if session exists for the failing session ID..."
SESSION_ID="59d5e2a4-edcb-4336-a7f7-b99331c4a529"
docker compose -f docker-compose.prod.yml exec ai_assistant python -c "
from app.database import get_db_session
from sqlalchemy import text
try:
    with get_db_session() as db:
        result = db.execute(text('SELECT session_id, user_id, status FROM ai_sessions WHERE session_id = :session_id'), {'session_id': '$SESSION_ID'}).fetchone()
        if result:
            print(f'✅ Session found: {result.session_id}, user: {result.user_id}, status: {result.status}')
        else:
            print('❌ Session not found in database')
except Exception as e:
    print(f'❌ Error checking session: {e}')
"