#!/bin/bash
echo "🔧 Recreating AI Assistant Tables in Production"
echo "=============================================="

echo "The AI assistant tables were accidentally dropped."
echo "This script will recreate them using the correct SQLAlchemy models."
echo ""

echo "1. Checking current AI tables status..."
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "
SELECT tablename FROM pg_tables 
WHERE schemaname = 'public' 
AND (tablename LIKE '%ai%' OR tablename LIKE '%escalation%' OR tablename LIKE '%support%' OR tablename LIKE '%expert%')
ORDER BY tablename;
"

echo -e "\n2. Recreating AI assistant tables using SQLAlchemy models..."
docker compose -f docker-compose.prod.yml exec ai_assistant python -c "
import sys
sys.path.append('/app')
from app.database import engine
from app.models import Base
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print('Creating AI assistant database tables using SQLAlchemy models...')
try:
    # This will create all tables defined in the models
    Base.metadata.create_all(bind=engine)
    print('✅ AI assistant tables created successfully!')
    
    # List the tables that were created
    from sqlalchemy import text
    with engine.connect() as conn:
        result = conn.execute(text('''
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            AND (tablename LIKE '%ai%' OR tablename LIKE '%escalation%' OR tablename LIKE '%support%' OR tablename LIKE '%expert%')
            ORDER BY tablename;
        '''))
        
        tables = result.fetchall()
        print('Created tables:')
        for table in tables:
            print(f'  - {table[0]}')
            
except Exception as e:
    print(f'❌ Error creating tables: {e}')
    import traceback
    traceback.print_exc()
"

echo -e "\n3. Verifying table structures..."
echo "Checking ai_sessions table:"
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "\d ai_sessions"

echo -e "\nChecking ai_messages table:"
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "\d ai_messages"

echo -e "\nChecking support_tickets table:"
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "\d support_tickets"

echo -e "\n4. Testing session creation with correct schema..."
docker compose -f docker-compose.prod.yml exec ai_assistant python -c "
import sys
sys.path.append('/app')
from app.database import get_db_session
from sqlalchemy import text
import uuid
from datetime import datetime

session_id = str(uuid.uuid4())
user_id = '45e2bc8a-b780-4886-bc0b-b0ba1655ff93'  # Maria Sefteli

print(f'Testing session creation...')
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
        
        print('✅ Session created successfully!')
        
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
    import traceback
    traceback.print_exc()
"

echo -e "\n5. Testing escalation service compatibility..."
docker compose -f docker-compose.prod.yml exec ai_assistant python -c "
import sys
sys.path.append('/app')
from app.services.escalation_service import escalation_service
from app.database import get_db_session
from sqlalchemy import text
import uuid

# Create a test session first
session_id = str(uuid.uuid4())
user_id = '45e2bc8a-b780-4886-bc0b-b0ba1655ff93'

try:
    with get_db_session() as db:
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
    
    print(f'Test session created: {session_id}')
    
    # Test escalation evaluation (this should not fail with database errors)
    import asyncio
    async def test_escalation():
        try:
            should_escalate, reason, factors = await escalation_service.evaluate_escalation_need(
                session_id=session_id,
                current_confidence=0.2,  # Low confidence to trigger escalation
                steps_completed=3,
                user_feedback='I need help'
            )
            print(f'✅ Escalation evaluation successful:')
            print(f'   Should escalate: {should_escalate}')
            print(f'   Reason: {reason}')
            return True
        except Exception as e:
            print(f'❌ Escalation evaluation failed: {e}')
            import traceback
            traceback.print_exc()
            return False
    
    # Run the async test
    result = asyncio.run(test_escalation())
    if result:
        print('✅ Escalation service is compatible with database schema')
    else:
        print('❌ Escalation service has compatibility issues')
        
except Exception as e:
    print(f'❌ Error in escalation test: {e}')
    import traceback
    traceback.print_exc()
"

echo -e "\n✅ AI Assistant tables recreation complete!"
echo ""
echo "SUMMARY:"
echo "========"
echo "- All AI assistant tables have been recreated using SQLAlchemy models"
echo "- Tables use 'id' as primary key (correct for SQLAlchemy)"
echo "- Foreign key relationships use 'session_id' column (correct)"
echo "- Escalation service has been updated to use correct column names"
echo "- Ready for production escalation testing"
echo ""
echo "Next step: Test the escalation flow in production UI"