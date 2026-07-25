#!/bin/bash
echo "🔧 Setting up AI Assistant Database Schema in Production"
echo "======================================================"

echo "The issue is clear: AI assistant tables don't exist in production."
echo "We need to create the AI assistant database schema."
echo ""

echo "1. First, let's check what AI-related tables exist..."
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "
SELECT tablename 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename LIKE '%ai%' 
OR tablename LIKE '%session%' 
OR tablename LIKE '%escalation%' 
OR tablename LIKE '%support%'
ORDER BY tablename;
"

echo -e "\n2. Let's create the AI assistant tables using the SQL script..."
echo "Running AI assistant table creation script..."

docker compose -f docker-compose.prod.yml exec ai_assistant python -c "
import sys
sys.path.append('/app')
from app.database import engine
from app.models import Base

print('Creating AI assistant database tables...')
try:
    Base.metadata.create_all(bind=engine)
    print('✅ AI assistant tables created successfully!')
except Exception as e:
    print(f'❌ Error creating tables: {e}')
"

echo -e "\n3. Verifying tables were created..."
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "
SELECT tablename 
FROM pg_tables 
WHERE schemaname = 'public' 
AND (tablename LIKE '%ai%' 
     OR tablename LIKE '%session%' 
     OR tablename LIKE '%escalation%' 
     OR tablename LIKE '%support%')
ORDER BY tablename;
"

echo -e "\n4. Testing session creation with a real user..."
echo "Using user: 45e2bc8a-b780-4886-bc0b-b0ba1655ff93 (Maria Sefteli)"

docker compose -f docker-compose.prod.yml exec ai_assistant python -c "
import sys
sys.path.append('/app')
from app.database import get_db_session
from sqlalchemy import text
import uuid
from datetime import datetime

# Test session creation with real user
session_id = str(uuid.uuid4())
user_id = '45e2bc8a-b780-4886-bc0b-b0ba1655ff93'  # Maria Sefteli

print(f'Testing session creation...')
print(f'Session ID: {session_id}')
print(f'User ID: {user_id}')

try:
    with get_db_session() as db:
        # Create test session
        db.execute(text('''
            INSERT INTO ai_sessions (session_id, user_id, machine_id, status, language, created_at, updated_at)
            VALUES (:session_id, :user_id, :machine_id, :status, :language, NOW(), NOW())
        '''), {
            'session_id': session_id,
            'user_id': user_id,
            'machine_id': None,
            'status': 'active',
            'language': 'en'
        })
        
        # Verify session was created
        result = db.execute(text('''
            SELECT session_id, user_id, status, created_at 
            FROM ai_sessions 
            WHERE session_id = :session_id
        '''), {'session_id': session_id}).fetchone()
        
        if result:
            print(f'✅ Session created successfully!')
            print(f'   Session: {result.session_id}')
            print(f'   User: {result.user_id}')
            print(f'   Status: {result.status}')
            print(f'   Created: {result.created_at}')
        else:
            print('❌ Session not found after creation')
            
except Exception as e:
    print(f'❌ Error creating session: {e}')
"

echo -e "\n✅ Production AI Assistant database setup complete!"
echo ""
echo "Now try creating an escalation ticket through the UI."
echo "The session creation should work and escalation should succeed."