# Clarification Handling & Learning System - Complete Fix

## Issues Identified

### Issue 1: Clarification Still Breaking Step-by-Step ❌
When user provides clarification, system returns LIST instead of continuing step-by-step.

**Root Cause**: The `get_workflow_state()` check is failing because:
1. It's checking `workflow_status == 'active'`
2. But `workflow_status` is set to session.status (which is 'active')
3. However, the check needs to verify there are UNCOMPLETED steps

### Issue 2: Frontend Template Variables Not Replaced ❌
Shows `{number}`, `{minutes}`, `{rate}` instead of actual values.

**Root Cause**: Frontend is not replacing template variables in step data.

### Issue 3: No Learning System ❌
Clarifications and session outcomes are not being learned from.

---

## Fix 1: Correct Workflow State Detection

### Problem
```python
# Current check in chat.py
if workflow_state and workflow_state.workflow_status == 'active':
```

This checks session status, not whether troubleshooting is actually active.

### Solution
Check if there's a current_step (uncompleted step):

```python
# Better check
if workflow_state and workflow_state.current_step is not None:
```

### Implementation

**File**: `ai_assistant/app/routers/chat.py` (line ~240)

Change:
```python
if workflow_state and workflow_state.workflow_status == 'active':
```

To:
```python
if workflow_state and workflow_state.current_step is not None:
```

---

## Fix 2: Frontend Template Variable Replacement

### Problem
Frontend receives step_data but doesn't replace `{number}`, `{minutes}`, `{rate}`.

### Solution
Update ChatWidget to replace template variables.

**File**: `frontend/src/components/ChatWidget.js`

Find the section that renders diagnostic steps (around line 800-900) and add:

```javascript
// Replace template variables in step instruction
const formatStepInstruction = (instruction, stepData) => {
  if (!stepData) return instruction;
  
  let formatted = instruction;
  
  // Replace {number} with step number
  if (stepData.step_number) {
    formatted = formatted.replace(/{number}/g, stepData.step_number);
  }
  
  // Replace {minutes} with estimated duration
  if (stepData.estimated_duration) {
    formatted = formatted.replace(/{minutes}/g, stepData.estimated_duration);
  }
  
  // Replace {rate} with confidence score as percentage
  if (stepData.confidence_score) {
    const rate = Math.round(stepData.confidence_score * 100);
    formatted = formatted.replace(/{rate}/g, rate);
  }
  
  return formatted;
};

// Use it when rendering:
{msg.message_type === 'diagnostic_step' && (
  <div className="diagnostic-step-card">
    <div className="step-instruction">
      {formatStepInstruction(msg.content, msg.step_data)}
    </div>
    {/* ... feedback buttons ... */}
  </div>
)}
```

---

## Fix 3: Learning System Implementation

### Database Tables Needed

Check if these exist:
```sql
-- Session outcomes for learning
CREATE TABLE IF NOT EXISTS session_outcomes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES ai_sessions(id),
    outcome_type VARCHAR(50), -- 'resolved', 'escalated', 'abandoned'
    resolution_time_minutes INTEGER,
    steps_taken INTEGER,
    user_satisfaction INTEGER, -- 1-5 rating
    key_learnings JSONB, -- Extracted facts
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Learned facts about machines
CREATE TABLE IF NOT EXISTS machine_facts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    machine_model VARCHAR(50),
    fact_type VARCHAR(50), -- 'power_source', 'component', 'procedure'
    fact_key VARCHAR(100),
    fact_value TEXT,
    confidence_score FLOAT DEFAULT 0.5,
    source_sessions UUID[], -- Array of session IDs that contributed
    times_confirmed INTEGER DEFAULT 1,
    times_contradicted INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(machine_model, fact_type, fact_key)
);

-- Solution effectiveness tracking
CREATE TABLE IF NOT EXISTS solution_effectiveness (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    problem_category VARCHAR(100),
    solution_description TEXT,
    machine_model VARCHAR(50),
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    avg_resolution_time_minutes FLOAT,
    last_used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Service: Session Completion Handler

**File**: `ai_assistant/app/services/session_completion_service.py` (NEW)

```python
"""
Service for handling session completion and learning extraction.
"""

import logging
import uuid
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy import text

from ..database import get_db_session
from ..llm_client import LLMClient, ConversationMessage

logger = logging.getLogger(__name__)


class SessionCompletionService:
    """Service for processing completed sessions and extracting learnings."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
    
    async def complete_session(
        self,
        session_id: str,
        outcome_type: str,  # 'resolved', 'escalated', 'abandoned'
        resolution_summary: Optional[str] = None
    ) -> None:
        """
        Mark session as complete and extract learnings.
        
        Args:
            session_id: ID of the session to complete
            outcome_type: Type of outcome
            resolution_summary: Optional summary of resolution
        """
        logger.info(f"Completing session {session_id} with outcome: {outcome_type}")
        
        # Get session data
        session_data = await self._get_session_data(session_id)
        if not session_data:
            logger.error(f"Session {session_id} not found")
            return
        
        # Calculate metrics
        steps_taken = session_data['step_count']
        resolution_time = self._calculate_resolution_time(session_data)
        
        # Extract learnings from session
        key_learnings = await self._extract_learnings(session_data)
        
        # Store session outcome
        await self._store_session_outcome(
            session_id=session_id,
            outcome_type=outcome_type,
            resolution_time_minutes=resolution_time,
            steps_taken=steps_taken,
            key_learnings=key_learnings
        )
        
        # Update session status
        await self._update_session_status(session_id, outcome_type, resolution_summary)
        
        # Process learnings
        if key_learnings:
            await self._process_learnings(session_data, key_learnings)
        
        logger.info(f"Session {session_id} completed successfully")
    
    async def _get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get complete session data including messages and steps."""
        try:
            with get_db_session() as db:
                # Get session
                session_query = text("""
                    SELECT id, user_id, machine_id, status, problem_description,
                           language, session_metadata, created_at
                    FROM ai_sessions
                    WHERE id = :session_id
                """)
                session = db.execute(session_query, {'session_id': session_id}).fetchone()
                
                if not session:
                    return None
                
                # Get messages
                messages_query = text("""
                    SELECT sender, content, message_type, timestamp
                    FROM ai_messages
                    WHERE session_id = :session_id
                    ORDER BY timestamp ASC
                """)
                messages = db.execute(messages_query, {'session_id': session_id}).fetchall()
                
                # Get steps
                steps_query = text("""
                    SELECT step_number, instruction, user_feedback, completed, success
                    FROM troubleshooting_steps
                    WHERE session_id = :session_id
                    ORDER BY step_number ASC
                """)
                steps = db.execute(steps_query, {'session_id': session_id}).fetchall()
                
                return {
                    'session_id': str(session.id),
                    'user_id': str(session.user_id),
                    'machine_id': str(session.machine_id) if session.machine_id else None,
                    'problem_description': session.problem_description,
                    'language': session.language,
                    'metadata': session.session_metadata if isinstance(session.session_metadata, dict) else {},
                    'created_at': session.created_at,
                    'messages': [dict(m._mapping) for m in messages],
                    'steps': [dict(s._mapping) for s in steps],
                    'step_count': len(steps)
                }
        except Exception as e:
            logger.error(f"Failed to get session data: {e}")
            return None
    
    def _calculate_resolution_time(self, session_data: Dict[str, Any]) -> int:
        """Calculate resolution time in minutes."""
        if not session_data.get('messages'):
            return 0
        
        first_msg = session_data['messages'][0]
        last_msg = session_data['messages'][-1]
        
        time_diff = last_msg['timestamp'] - first_msg['timestamp']
        return int(time_diff.total_seconds() / 60)
    
    async def _extract_learnings(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key learnings from session using LLM."""
        
        # Build conversation summary
        conversation = "\n".join([
            f"{msg['sender']}: {msg['content']}"
            for msg in session_data['messages']
        ])
        
        system_prompt = """You are analyzing a troubleshooting session to extract key learnings.
Focus on:
1. Machine-specific facts mentioned by the user
2. Successful troubleshooting approaches
3. Failed approaches that should be avoided
4. Important clarifications about the machine

Return a JSON object with:
{
    "machine_facts": [{"type": "power_source|component|procedure", "key": "brief_key", "value": "fact_value"}],
    "successful_approaches": ["approach 1", "approach 2"],
    "failed_approaches": ["approach 1", "approach 2"],
    "key_insights": ["insight 1", "insight 2"]
}"""
        
        user_prompt = f"""Analyze this troubleshooting session and extract learnings:

Machine: {session_data.get('machine_id', 'Unknown')}
Problem: {session_data.get('problem_description', 'Unknown')}

Conversation:
{conversation}

Extract key learnings in JSON format."""
        
        try:
            messages = [
                ConversationMessage(role="system", content=system_prompt),
                ConversationMessage(role="user", content=user_prompt)
            ]
            
            response = await self.llm_client.generate_response(messages, language="en")
            
            if response.success:
                # Parse JSON from response
                import json
                content = response.content.strip()
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_content = content[start_idx:end_idx]
                    return json.loads(json_content)
            
            return {}
        except Exception as e:
            logger.error(f"Failed to extract learnings: {e}")
            return {}
    
    async def _store_session_outcome(
        self,
        session_id: str,
        outcome_type: str,
        resolution_time_minutes: int,
        steps_taken: int,
        key_learnings: Dict[str, Any]
    ) -> None:
        """Store session outcome in database."""
        try:
            with get_db_session() as db:
                query = text("""
                    INSERT INTO session_outcomes 
                    (id, session_id, outcome_type, resolution_time_minutes, steps_taken, key_learnings)
                    VALUES (:id, :session_id, :outcome_type, :resolution_time, :steps_taken, :learnings)
                """)
                db.execute(query, {
                    'id': str(uuid.uuid4()),
                    'session_id': session_id,
                    'outcome_type': outcome_type,
                    'resolution_time': resolution_time_minutes,
                    'steps_taken': steps_taken,
                    'learnings': json.dumps(key_learnings) if key_learnings else '{}'
                })
        except Exception as e:
            logger.error(f"Failed to store session outcome: {e}")
    
    async def _update_session_status(
        self,
        session_id: str,
        outcome_type: str,
        resolution_summary: Optional[str]
    ) -> None:
        """Update session status to completed/escalated/abandoned."""
        try:
            with get_db_session() as db:
                query = text("""
                    UPDATE ai_sessions
                    SET status = :status, resolution_summary = :summary, updated_at = NOW()
                    WHERE id = :session_id
                """)
                db.execute(query, {
                    'session_id': session_id,
                    'status': outcome_type,
                    'summary': resolution_summary
                })
        except Exception as e:
            logger.error(f"Failed to update session status: {e}")
    
    async def _process_learnings(
        self,
        session_data: Dict[str, Any],
        key_learnings: Dict[str, Any]
    ) -> None:
        """Process and store extracted learnings."""
        
        # Extract machine model from machine_id
        machine_model = await self._get_machine_model(session_data.get('machine_id'))
        
        # Store machine facts
        if key_learnings.get('machine_facts'):
            for fact in key_learnings['machine_facts']:
                await self._store_or_update_machine_fact(
                    machine_model=machine_model,
                    fact_type=fact.get('type', 'general'),
                    fact_key=fact.get('key', ''),
                    fact_value=fact.get('value', ''),
                    session_id=session_data['session_id']
                )
        
        logger.info(f"Processed {len(key_learnings.get('machine_facts', []))} machine facts")
    
    async def _get_machine_model(self, machine_id: Optional[str]) -> str:
        """Get machine model from machine_id."""
        if not machine_id:
            return "unknown"
        
        try:
            with get_db_session() as db:
                query = text("""
                    SELECT model_type FROM machines WHERE id = :machine_id
                """)
                result = db.execute(query, {'machine_id': machine_id}).fetchone()
                return result[0] if result else "unknown"
        except:
            return "unknown"
    
    async def _store_or_update_machine_fact(
        self,
        machine_model: str,
        fact_type: str,
        fact_key: str,
        fact_value: str,
        session_id: str
    ) -> None:
        """Store or update a machine fact."""
        try:
            with get_db_session() as db:
                # Check if fact exists
                check_query = text("""
                    SELECT id, times_confirmed, source_sessions
                    FROM machine_facts
                    WHERE machine_model = :model AND fact_type = :type AND fact_key = :key
                """)
                existing = db.execute(check_query, {
                    'model': machine_model,
                    'type': fact_type,
                    'key': fact_key
                }).fetchone()
                
                if existing:
                    # Update existing fact
                    update_query = text("""
                        UPDATE machine_facts
                        SET times_confirmed = times_confirmed + 1,
                            source_sessions = array_append(source_sessions, :session_id::UUID),
                            updated_at = NOW()
                        WHERE id = :id
                    """)
                    db.execute(update_query, {
                        'id': existing.id,
                        'session_id': session_id
                    })
                else:
                    # Insert new fact
                    insert_query = text("""
                        INSERT INTO machine_facts
                        (id, machine_model, fact_type, fact_key, fact_value, source_sessions)
                        VALUES (:id, :model, :type, :key, :value, ARRAY[:session_id]::UUID[])
                    """)
                    db.execute(insert_query, {
                        'id': str(uuid.uuid4()),
                        'model': machine_model,
                        'type': fact_type,
                        'key': fact_key,
                        'value': fact_value,
                        'session_id': session_id
                    })
        except Exception as e:
            logger.error(f"Failed to store machine fact: {e}")
```

---

## Implementation Steps

### Step 1: Fix Workflow State Check
```bash
# Edit chat.py
docker-compose exec ai_assistant sed -i 's/workflow_state.workflow_status == .active./workflow_state.current_step is not None/g' /app/app/routers/chat.py
```

### Step 2: Create Database Tables
```bash
# Run SQL to create learning tables
docker-compose exec db psql -U abparts_user -d abparts_dev -f /path/to/create_learning_tables.sql
```

### Step 3: Add Session Completion Service
Create the file above and integrate it.

### Step 4: Update Frontend Template Replacement
Edit ChatWidget.js to replace template variables.

### Step 5: Restart Containers
```bash
docker-compose restart ai_assistant web
```

---

## Testing

### Test 1: Clarification Handling
1. Start troubleshooting
2. Click "Didn't work" once
3. Type clarification
4. ✅ Should get ONE next step with buttons

### Test 2: Session Completion
1. Complete a troubleshooting session
2. Check `session_outcomes` table
3. Check `machine_facts` table
4. ✅ Should see extracted learnings

### Test 3: Learning Application
1. Start new session with same machine model
2. ✅ Should use learned facts in troubleshooting

---

**Priority**: Fix workflow state check FIRST (5 minutes), then implement learning system (2-3 hours).
