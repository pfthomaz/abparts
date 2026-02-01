# Frontend Session Persistence Fix - CRITICAL

## Root Cause Identified ✅

The clarification handling **backend code is correct**, but the **frontend is creating new sessions** instead of maintaining the existing troubleshooting session.

### Evidence
```
Session d1ed4d43... (troubleshooting session):
- 10:04:27 - User: "Machine won't start"
- 10:04:42 - Assistant: "Check power connections" (diagnostic_step)

Session 837f7632... (NEW session created for clarification):
- 10:06:27 - User: "boss does not have power cord..."
- 10:06:32 - Assistant: [LIST OF STEPS] (text)
```

The clarification went to a **different session**, so the backend never detected active troubleshooting.

---

## The Problem

### What's Happening
1. User starts troubleshooting → Session A created
2. User clicks "Didn't work" → Uses Session A (works!)
3. User types clarification → **NEW Session B created** (breaks!)
4. Backend checks Session B for active troubleshooting → None found
5. Backend treats it as new conversation → Returns list

### Why It's Happening
The frontend ChatWidget likely:
- Stores session_id in component state
- Resets or loses session_id when user types (vs clicks button)
- Feedback buttons maintain session_id (they work)
- Regular messages don't include session_id (they break)

---

## The Fix

### File: `frontend/src/components/ChatWidget.js`

Need to ensure session_id persists across ALL message types.

### Current Behavior (Broken)
```javascript
// Feedback button click - WORKS
const handleStepFeedback = async (stepId, feedback) => {
  // Uses existing sessionId from state
  await fetch('/api/ai/chat/step-feedback', {
    body: JSON.stringify({
      session_id: sessionId,  // ✅ Maintains session
      step_id: stepId,
      feedback: feedback
    })
  });
};

// Regular message send - BREAKS
const handleSendMessage = async (message) => {
  // Might not include sessionId or creates new one
  await fetch('/api/ai/chat', {
    body: JSON.stringify({
      message: message,
      session_id: sessionId,  // ❌ Might be undefined or reset
      conversation_history: messages
    })
  });
};
```

### Required Fix
```javascript
// In ChatWidget component

// 1. Store session_id in state that persists
const [sessionId, setSessionId] = useState(null);
const [isInTroubleshooting, setIsInTroubleshooting] = useState(false);

// 2. When receiving diagnostic_step, mark as in troubleshooting
useEffect(() => {
  const lastMessage = messages[messages.length - 1];
  if (lastMessage && lastMessage.message_type === 'diagnostic_step') {
    setIsInTroubleshooting(true);
  }
}, [messages]);

// 3. ALWAYS include session_id in regular messages
const handleSendMessage = async (message) => {
  const response = await fetch('/api/ai/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: message,
      session_id: sessionId,  // ✅ MUST be included
      user_id: currentUser?.id,
      machine_id: selectedMachine?.id,
      conversation_history: messages,
      language: currentUser?.preferred_language
    })
  });
  
  const data = await response.json();
  
  // 4. Update session_id if new one returned
  if (data.session_id && !sessionId) {
    setSessionId(data.session_id);
  }
  
  // 5. Check if response is diagnostic_step
  if (data.message_type === 'diagnostic_step') {
    setIsInTroubleshooting(true);
  }
};

// 6. Feedback handler maintains session
const handleStepFeedback = async (stepId, feedback) => {
  const response = await fetch('/api/ai/chat/step-feedback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,  // ✅ Uses same session
      step_id: stepId,
      feedback: feedback,
      language: currentUser?.preferred_language,
      user_id: currentUser?.id
    })
  });
  
  const data = await response.json();
  
  // Handle next step or completion
  if (data.next_step) {
    // Add next step to messages
    setMessages(prev => [...prev, {
      role: 'assistant',
      content: data.next_step.response,
      message_type: data.next_step.message_type,
      step_data: data.next_step.step_data,
      timestamp: Date.now()
    }]);
  } else {
    // Workflow completed
    setIsInTroubleshooting(false);
    if (data.completion_message) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.completion_message,
        message_type: 'text',
        timestamp: Date.now()
      }]);
    }
  }
};

// 7. Add "New Session" button
const handleNewSession = () => {
  setSessionId(null);
  setIsInTroubleshooting(false);
  setMessages([]);
  setSelectedMachine(null);
};
```

---

## Quick Diagnostic

### Check Current Implementation
```bash
# See if session_id is being sent
docker-compose logs web | grep -A 5 "session_id"

# Check ChatWidget for session management
grep -n "sessionId" frontend/src/components/ChatWidget.js
grep -n "session_id" frontend/src/components/ChatWidget.js
```

### Test Session Persistence
1. Open browser dev tools → Network tab
2. Start troubleshooting
3. Click "Didn't work" → Check request payload for `session_id`
4. Type clarification → Check request payload for `session_id`
5. **They should be THE SAME**

---

## Expected Behavior After Fix

### Correct Flow
```
POST /api/ai/chat
{
  "message": "Machine won't start",
  "session_id": null,  // First message
  "machine_id": "abc123"
}
→ Response: { "session_id": "d1ed4d43...", "message_type": "diagnostic_step" }

POST /api/ai/chat/step-feedback
{
  "session_id": "d1ed4d43...",  // ✅ Same session
  "step_id": "step1",
  "feedback": "didnt_work"
}
→ Response: { "next_step": {...} }

POST /api/ai/chat
{
  "message": "no power cord... diesel engine",
  "session_id": "d1ed4d43...",  // ✅ SAME SESSION
  "machine_id": "abc123"
}
→ Backend detects active troubleshooting
→ Response: { "message_type": "diagnostic_step", "step_data": {...} }
```

---

## Priority: CRITICAL

This is blocking the clarification feature completely. The backend is ready, but the frontend isn't maintaining session state.

### Immediate Action Required
1. Locate session_id management in ChatWidget.js
2. Ensure it persists across all message sends
3. Test with browser dev tools
4. Verify same session_id used throughout conversation

---

## Alternative Quick Fix

If ChatWidget refactor is complex, add this to backend as temporary workaround:

**File**: `ai_assistant/app/routers/chat.py`

```python
# Before checking workflow state, try to find active session by user_id + machine_id
if not request.session_id and request.user_id and request.machine_id:
    # Try to find active troubleshooting session for this user/machine
    with get_db_session() as db:
        query = text("""
            SELECT s.id
            FROM ai_sessions s
            WHERE s.user_id = :user_id 
              AND s.machine_id = :machine_id
              AND s.status = 'active'
              AND EXISTS (
                SELECT 1 FROM troubleshooting_steps ts 
                WHERE ts.session_id = s.id AND ts.completed = false
              )
            ORDER BY s.created_at DESC
            LIMIT 1
        """)
        result = db.execute(query, {
            'user_id': request.user_id,
            'machine_id': request.machine_id
        }).fetchone()
        
        if result:
            request.session_id = str(result[0])
            logger.info(f"Found active troubleshooting session: {request.session_id}")
```

This makes the backend "find" the active session even if frontend doesn't send it.

---

**Status**: Root cause identified - frontend session management issue
**Impact**: Blocks clarification feature completely
**Fix Location**: `frontend/src/components/ChatWidget.js`
**Alternative**: Backend workaround to find active sessions
