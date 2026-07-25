#!/bin/bash
echo "🔧 Fixing Production AI Assistant Schema Mismatch"
echo "================================================="

echo "The issue: AI models use 'id' as primary key, but escalation service expects 'session_id'"
echo "Solution: Add session_id column as alias to id, or fix the service to use 'id'"
echo ""

echo "1. Checking current ai_sessions table structure..."
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "\d ai_sessions"

echo -e "\n2. The problem is column name mismatch:"
echo "   - SQLAlchemy model uses 'id' as primary key"
echo "   - Escalation service queries for 'session_id'"
echo "   - Need to fix the escalation service to use 'id' instead"

echo -e "\n3. First, let's verify the current table structure..."
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'ai_sessions' 
ORDER BY ordinal_position;
"

echo -e "\n4. Testing session creation with correct column name (id)..."
docker compose -f docker-compose.prod.yml exec ai_assistant python -c "
import sys
sys.path.append('/app')
from app.database import get_db_session
from sqlalchemy import text
import uuid
from datetime import datetime

session_id = str(uuid.uuid4())
user_id = '45e2bc8a-b780-4886-bc0b-b0ba1655ff93'  # Maria Sefteli

print(f'Testing session creation with id column...')
print(f'Session ID: {session_id}')
print(f'User ID: {user_id}')

try:
    with get_db_session() as db:
        # Use 'id' column (correct according to SQLAlchemy model)
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
        
        print('✅ Session created successfully with id column!')
        
        # Verify it was created
        result = db.execute(text('''
            SELECT id, user_id, status, created_at 
            FROM ai_sessions 
            WHERE id = :id
        '''), {'id': session_id}).fetchone()
        
        if result:
            print(f'✅ Session verified:')
            print(f'   ID: {result.id}')
            print(f'   User: {result.user_id}')
            print(f'   Status: {result.status}')
            print(f'   Created: {result.created_at}')
        else:
            print('❌ Session not found after creation')
            
except Exception as e:
    print(f'❌ Error creating session: {e}')
"

echo -e "\n5. The fix is to update the escalation service to use 'id' instead of 'session_id'"
echo "   This requires updating the Python code, not the database schema."

echo -e "\n6. Checking if escalation service needs to be updated..."
docker compose -f docker-compose.prod.yml exec ai_assistant python -c "
import sys
sys.path.append('/app')
import os

# Check if the escalation service file exists and contains session_id references
escalation_file = '/app/app/services/escalation_service.py'
if os.path.exists(escalation_file):
    with open(escalation_file, 'r') as f:
        content = f.read()
        session_id_count = content.count('session_id')
        print(f'Found {session_id_count} references to session_id in escalation service')
        
        # Check for specific problematic queries
        if 'SELECT session_id' in content:
            print('❌ Found SELECT session_id queries - these need to be changed to SELECT id')
        if 'WHERE session_id =' in content:
            print('❌ Found WHERE session_id queries - these need to be changed to WHERE id =')
        if 'INSERT INTO ai_sessions (session_id' in content:
            print('❌ Found INSERT with session_id - this needs to be changed to id')
            
        print('The escalation service code needs to be updated to use id instead of session_id')
else:
    print('Escalation service file not found')
"

echo -e "\n7. Testing escalation endpoint with current schema..."
docker compose -f docker-compose.prod.yml exec ai_assistant python -c "
import sys
sys.path.append('/app')
from app.database import get_db_session
from sqlalchemy import text
import uuid

# Create a test session using the correct column name
session_id = str(uuid.uuid4())
user_id = '45e2bc8a-b780-4886-bc0b-b0ba1655ff93'

try:
    with get_db_session() as db:
        # Create session with 'id' column
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
        
        print(f'✅ Test session created: {session_id}')
        
        # Now test if we can query it using session_id (this should fail)
        try:
            result = db.execute(text('''
                SELECT session_id, user_id FROM ai_sessions WHERE session_id = :session_id
            '''), {'session_id': session_id}).fetchone()
            print('❌ This should not work - session_id column does not exist')
        except Exception as e:
            print(f'✅ Expected error querying session_id: {e}')
            
        # Test querying with correct column name
        try:
            result = db.execute(text('''
                SELECT id, user_id FROM ai_sessions WHERE id = :id
            '''), {'id': session_id}).fetchone()
            print(f'✅ Correct query works: Found session {result.id}')
        except Exception as e:
            print(f'❌ Unexpected error with id query: {e}')
            
except Exception as e:
    print(f'❌ Error in test: {e}')
"

echo -e "\n✅ Schema analysis complete!"
echo ""
echo "SUMMARY:"
echo "========"
echo "- The database schema is correct (uses 'id' as primary key)"
echo "- The escalation service code is incorrect (expects 'session_id')"
echo "- Fix needed: Update escalation service to use 'id' instead of 'session_id'"
echo "- This is a code fix, not a database schema fix"
echo ""
echo "Next step: Update the escalation service Python code to use the correct column names."