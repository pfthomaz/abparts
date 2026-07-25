# Step-by-Step Troubleshooting - Root Cause Found

## Issue

When user provides clarification during troubleshooting, the system returns plain text instead of continuing with step-by-step cards with buttons.

## Root Cause: Frontend Not Sending session_id

Looking at the logs, the clarification detection code is **never running**. The debug logs we added don't appear, which means this check is failing:

```python
if request.session_id:  # <-- This is FALSE!
    # Check for active troubleshooting...
```

**The frontend is not including the session_id in the chat request when you type the clarification message.**

## Evidence from Logs

```
'message_type': 'text'  <-- Regular chat response, not diagnostic_step
```

No debug logs appear:
- No "[DEBUG] Workflow state found"
- No "[DEBUG] Active troubleshooting detected"
- No "[DEBUG] No workflow state found"

This means the `if request.session_id:` check failed, so the code never even tried to detect active troubleshooting.

## Why This Happens

The frontend ChatWidget likely:
1. Starts troubleshooting → Gets session_id → Shows step card
2. User clicks "Didn't work" → Sends feedback with session_id ✓
3. Gets next step → Shows step card
4. User types clarification → **Sends message WITHOUT session_id** ✗

The session_id is probably stored in the step card component but not in the main chat input component.

## The Fix Needed

This is a **FRONTEND** issue, not a backend issue. The frontend needs to:

1. **Store the session_id** when troubleshooting starts
2. **Include the session_id** in ALL subsequent chat messages
3. **Maintain the session_id** even when user types free text (not clicking buttons)

## Where to Fix

**File**: `frontend/src/components/ChatWidget.js`

The chat input needs to:
```javascript
// When sending a message, include the current troubleshooting session_id
const sendMessage = async (message) => {
  const payload = {
    message: message,
    session_id: currentTroubleshootingSessionId,  // <-- ADD THIS
    user_id: user.id,
    machine_id: selectedMachine?.id,
    language: user.preferred_language
  };
  
  // Send to /api/ai/chat
};
```

## Current Workaround in Backend

The backend has a workaround that tries to find recent active sessions:

```python
# WORKAROUND: If no session_id provided, try to find RECENT active troubleshooting session
if not request.session_id and request.user_id and request.machine_id:
    # Query for active session updated in last 5 minutes...
```

But this workaround **doesn't work** because:
1. It only looks for sessions with `completed = false` in troubleshooting_steps
2. After clicking "Didn't work", the step is marked `completed = true`
3. So the query finds no active sessions
4. System treats it as a new chat message

## Proper Solution

### Option 1: Fix Frontend (Recommended)
Update ChatWidget to maintain and send session_id with every message during active troubleshooting.

### Option 2: Improve Backend Workaround
Change the query to look for ANY active session, not just ones with uncompleted steps:

```python
query = text("""
    SELECT s.id, s.updated_at
    FROM ai_sessions s
    WHERE s.user_id = :user_id 
      AND s.machine_id = :machine_id
      AND s.status = 'active'
      AND s.updated_at > NOW() - INTERVAL '5 minutes'
    ORDER BY s.updated_at DESC
    LIMIT 1
""")
```

Remove the `EXISTS (SELECT 1 FROM troubleshooting_steps WHERE completed = false)` condition.

## Recommendation

**Fix the frontend** to properly maintain session_id. This is the correct solution because:
- Session management should be handled by the client
- Backend shouldn't have to guess which session the user means
- Prevents edge cases and race conditions
- Makes the system more reliable

---

## Summary

**Problem**: Frontend doesn't send session_id with clarification messages
**Result**: Backend treats it as new chat, not active troubleshooting
**Fix**: Update ChatWidget to include session_id in all messages during troubleshooting

The backend code is correct - it's ready to handle clarifications. The frontend just needs to tell it which session to use.
