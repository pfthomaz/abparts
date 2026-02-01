# Production Deployment Guide - AI Assistant Features

## Overview
This guide covers deploying the AI Assistant troubleshooting features and UI improvements to production.

## Database Changes Required

### New Tables for AI Assistant

The following tables need to be created in the production database:

#### 1. Core AI Tables
- `ai_sessions` - Stores chat sessions
- `ai_messages` - Stores individual messages
- `knowledge_documents` - Stores knowledge base documents
- `document_embeddings` - Stores vector embeddings for semantic search

#### 2. Learning System Tables
- `session_outcomes` - Tracks troubleshooting session results
- `machine_facts` - Stores learned facts about machines
- `solution_effectiveness` - Tracks which solutions work best

#### 3. Enum Types
- `ai_session_status` - ('active', 'completed', 'escalated', 'abandoned')
- `ai_message_sender` - ('user', 'assistant', 'system')
- `ai_message_type` - ('text', 'voice', 'image', 'diagnostic_step', 'escalation')
- `ai_document_type` - ('manual', 'procedure', 'faq', 'expert_input', 'troubleshooting_guide')

### Frontend Changes (No Database Impact)
- Translation placeholder fixes (double curly braces)
- AutoBoss machine icon replacement
- Icon size increase (50% larger)

## Pre-Deployment Checklist

### 1. Environment Variables
Ensure these are set in production `.env`:
```bash
# AI Assistant
OPENAI_API_KEY=your_production_key
AI_ASSISTANT_URL=https://your-domain.com/ai

# Email for escalations (if configured)
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=your_email@domain.com
SMTP_PASSWORD=your_password
SMTP_FROM_EMAIL=your_email@domain.com
```

### 2. Backup Production Database
```bash
# Run this BEFORE any changes
docker-compose exec db pg_dump -U abparts_user abparts_prod > backup_before_ai_$(date +%Y%m%d_%H%M%S).sql
```

### 3. Test Files to Remove
These files should NOT be deployed to production:
- `.hypothesis/` directories
- `__pycache__/` directories
- `.pytest_cache/` directories
- All `test_*.py` files
- All `*_test.py` files
- `debug_*.py` files
- `*.test.js` files

## Deployment Steps

### Step 1: Clean Test Files (Development Server)
```bash
# Remove hypothesis test data
rm -rf .hypothesis
rm -rf ai_assistant/.hypothesis
rm -rf backend/.pytest_cache
rm -rf ai_assistant/.pytest_cache

# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete

# Remove test files (optional - can keep for reference)
# find . -type f \( -name "test_*.py" -o -name "*_test.py" \) -delete
```

### Step 2: Create Database Migration Script

Save this as `ai_assistant_migration.sql`:

```sql
-- AI Assistant Production Migration
-- Run this on production database

BEGIN;

-- Create enum types
DO $$ BEGIN
    CREATE TYPE ai_session_status AS ENUM ('active', 'completed', 'escalated', 'abandoned');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE ai_message_sender AS ENUM ('user', 'assistant', 'system');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE ai_message_type AS ENUM ('text', 'voice', 'image', 'diagnostic_step', 'escalation');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE ai_document_type AS ENUM ('manual', 'procedure', 'faq', 'expert_input', 'troubleshooting_guide');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create AI sessions table
CREATE TABLE IF NOT EXISTS ai_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    machine_id UUID REFERENCES machines(id) ON DELETE SET NULL,
    status ai_session_status NOT NULL DEFAULT 'active',
    problem_description TEXT,
    resolution_summary TEXT,
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    session_metadata TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create AI messages table
CREATE TABLE IF NOT EXISTS ai_messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES ai_sessions(session_id) ON DELETE CASCADE,
    sender ai_message_sender NOT NULL,
    content TEXT NOT NULL,
    message_type ai_message_type NOT NULL DEFAULT 'text',
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    message_metadata TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create knowledge documents table
CREATE TABLE IF NOT EXISTS knowledge_documents (
    document_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    document_type ai_document_type NOT NULL,
    machine_models TEXT[],
    tags TEXT[],
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    version VARCHAR(20) NOT NULL DEFAULT '1.0',
    file_path TEXT,
    document_metadata TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create document embeddings table
CREATE TABLE IF NOT EXISTS document_embeddings (
    embedding_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES knowledge_documents(document_id) ON DELETE CASCADE,
    content_chunk TEXT NOT NULL,
    embedding_vector REAL[],
    chunk_index INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create learning system tables
CREATE TABLE IF NOT EXISTS session_outcomes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES ai_sessions(session_id) ON DELETE CASCADE,
    outcome_type VARCHAR(50) NOT NULL,
    resolution_time_minutes INTEGER,
    steps_taken INTEGER,
    user_satisfaction INTEGER,
    key_learnings JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_outcome_type CHECK (outcome_type IN ('resolved', 'escalated', 'abandoned')),
    CONSTRAINT valid_satisfaction CHECK (user_satisfaction IS NULL OR (user_satisfaction >= 1 AND user_satisfaction <= 5))
);

CREATE TABLE IF NOT EXISTS machine_facts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    machine_model VARCHAR(50) NOT NULL,
    fact_type VARCHAR(50) NOT NULL,
    fact_key VARCHAR(100) NOT NULL,
    fact_value TEXT NOT NULL,
    confidence_score FLOAT DEFAULT 0.5,
    source_sessions UUID[] DEFAULT ARRAY[]::UUID[],
    times_confirmed INTEGER DEFAULT 1,
    times_contradicted INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_confidence CHECK (confidence_score >= 0 AND confidence_score <= 1),
    UNIQUE(machine_model, fact_type, fact_key)
);

CREATE TABLE IF NOT EXISTS solution_effectiveness (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    problem_category VARCHAR(100) NOT NULL,
    solution_description TEXT NOT NULL,
    machine_model VARCHAR(50),
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    avg_resolution_time_minutes FLOAT,
    last_used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_counts CHECK (success_count >= 0 AND failure_count >= 0)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_ai_sessions_user_id ON ai_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_sessions_machine_id ON ai_sessions(machine_id);
CREATE INDEX IF NOT EXISTS idx_ai_sessions_status ON ai_sessions(status);
CREATE INDEX IF NOT EXISTS idx_ai_sessions_created_at ON ai_sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_ai_sessions_updated_at ON ai_sessions(updated_at);

CREATE INDEX IF NOT EXISTS idx_ai_messages_session_id ON ai_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_ai_messages_sender ON ai_messages(sender);
CREATE INDEX IF NOT EXISTS idx_ai_messages_created_at ON ai_messages(created_at);

CREATE INDEX IF NOT EXISTS idx_knowledge_documents_type ON knowledge_documents(document_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_documents_language ON knowledge_documents(language);
CREATE INDEX IF NOT EXISTS idx_knowledge_documents_machine_models ON knowledge_documents USING GIN(machine_models);
CREATE INDEX IF NOT EXISTS idx_knowledge_documents_tags ON knowledge_documents USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_knowledge_documents_created_at ON knowledge_documents(created_at);
CREATE INDEX IF NOT EXISTS idx_knowledge_documents_updated_at ON knowledge_documents(updated_at);

CREATE INDEX IF NOT EXISTS idx_document_embeddings_document_id ON document_embeddings(document_id);
CREATE INDEX IF NOT EXISTS idx_document_embeddings_chunk_index ON document_embeddings(chunk_index);

CREATE INDEX IF NOT EXISTS idx_session_outcomes_session_id ON session_outcomes(session_id);
CREATE INDEX IF NOT EXISTS idx_session_outcomes_outcome_type ON session_outcomes(outcome_type);
CREATE INDEX IF NOT EXISTS idx_machine_facts_model ON machine_facts(machine_model);
CREATE INDEX IF NOT EXISTS idx_machine_facts_type ON machine_facts(fact_type);
CREATE INDEX IF NOT EXISTS idx_solution_effectiveness_category ON solution_effectiveness(problem_category);
CREATE INDEX IF NOT EXISTS idx_solution_effectiveness_model ON solution_effectiveness(machine_model);

-- Create triggers
CREATE OR REPLACE FUNCTION update_ai_session_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_ai_session_updated_at ON ai_sessions;
CREATE TRIGGER trigger_update_ai_session_updated_at
    BEFORE UPDATE ON ai_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_ai_session_updated_at();

CREATE OR REPLACE FUNCTION update_knowledge_document_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_knowledge_document_updated_at ON knowledge_documents;
CREATE TRIGGER trigger_update_knowledge_document_updated_at
    BEFORE UPDATE ON knowledge_documents
    FOR EACH ROW
    EXECUTE FUNCTION update_knowledge_document_updated_at();

COMMIT;

-- Verify tables were created
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public' 
    AND table_name IN (
        'ai_sessions', 
        'ai_messages', 
        'knowledge_documents', 
        'document_embeddings',
        'session_outcomes',
        'machine_facts',
        'solution_effectiveness'
    )
ORDER BY table_name;
```

### Step 3: Deploy to Production

```bash
# On production server

# 1. Pull latest code
git pull origin main

# 2. Run database migration
docker-compose exec db psql -U abparts_user -d abparts_prod -f /path/to/ai_assistant_migration.sql

# 3. Rebuild frontend with new changes
docker-compose exec web npm run build

# 4. Restart containers
docker-compose restart web ai_assistant

# 5. Verify services are running
docker-compose ps
```

### Step 4: Verify Deployment

```bash
# Check AI Assistant is responding
curl http://localhost:8001/health

# Check database tables exist
docker-compose exec db psql -U abparts_user -d abparts_prod -c "\dt ai_*"

# Check frontend is serving new build
curl -I http://localhost:3000
```

## Post-Deployment Verification

### 1. Test AI Assistant Chat
- Log in to the application
- Open the AI Assistant chat widget
- Verify the AutoBoss machine icon appears (larger size)
- Select a machine
- Type a troubleshooting question
- Verify step-by-step responses appear correctly
- Check that step numbers, time estimates, and success rates display (not placeholders)

### 2. Test Troubleshooting Workflow
- Start a troubleshooting session
- Click "Didn't work" to continue
- Click "It worked!" to complete
- Verify session is marked as resolved

### 3. Check Database
```sql
-- Verify sessions are being created
SELECT COUNT(*) FROM ai_sessions;

-- Verify messages are being stored
SELECT COUNT(*) FROM ai_messages;

-- Check learning system is working
SELECT COUNT(*) FROM session_outcomes;
```

## Rollback Plan

If issues occur:

```bash
# 1. Restore database backup
docker-compose exec db psql -U abparts_user -d abparts_prod < backup_before_ai_YYYYMMDD_HHMMSS.sql

# 2. Revert code
git revert HEAD
docker-compose restart web ai_assistant

# 3. Rebuild frontend
docker-compose exec web npm run build
```

## Summary of Changes

### Code Changes
1. **Frontend**:
   - Fixed translation placeholders (single `{param}` → double `{{param}}`)
   - Replaced machine icon with custom AutoBoss SVG
   - Increased icon size by 50% (w-4 h-4 → w-6 h-6)

2. **Backend** (AI Assistant):
   - Step-by-step troubleshooting service
   - Learning system for knowledge extraction
   - Session management and persistence
   - Troubleshooting detection improvements

3. **Database**:
   - 7 new tables
   - 4 new enum types
   - 16 new indexes
   - 2 new triggers

### Files Modified
- `frontend/src/components/ChatWidget.js` - Icon and translation fixes
- `frontend/src/locales/*.json` - All 6 language files updated
- `ai_assistant/app/routers/chat.py` - Detection improvements
- `ai_assistant/app/services/troubleshooting_service.py` - Feedback handling
- `ai_assistant/app/services/session_completion_service.py` - Learning system

### No Changes Required
- Existing ABParts tables (users, machines, parts, etc.)
- Authentication system
- Existing API endpoints
- Docker configuration (already set up)

## Support

If you encounter issues:
1. Check logs: `docker-compose logs ai_assistant`
2. Check database: `docker-compose exec db psql -U abparts_user -d abparts_prod`
3. Verify environment variables are set correctly
4. Ensure OpenAI API key is valid and has credits

## Next Steps After Deployment

1. Upload AutoBoss manual to knowledge base
2. Monitor AI Assistant usage and learning
3. Review session outcomes for improvements
4. Add more troubleshooting guides as needed
