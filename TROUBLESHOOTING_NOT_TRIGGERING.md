# Interactive Troubleshooting - Fix Applied ✅

## Status: READY FOR TESTING

The bug preventing interactive troubleshooting from triggering has been **FIXED** and the container has been **RESTARTED**.

---

## What Was Fixed

### The Bug
The conversation history check was counting **ALL messages** (including system messages like "Selected machine: KEF-5"), so by the time you sent your first problem message, the history was already at 3+ messages and the condition failed.

### The Fix
Changed the condition to count **only user messages**:

```python
# OLD (broken):
if is_troubleshooting and request.machine_id and len(request.conversation_history) < 3:

# NEW (fixed):
user_messages = [msg for msg in request.conversation_history if msg.role == 'user']
if is_troubleshooting and request.machine_id and len(user_messages) <= 1:
```

**File**: `ai_assistant/app/routers/chat.py` (line ~696)
**Container**: Restarted at 09:18 UTC

---

## How to Test

### Test 1: Basic Troubleshooting Trigger

1. **Login**: Use credentials `dthomaz/amFT1999!`
2. **Open AI Assistant**: Click the chat icon
3. **Select Machine**: Choose "KEF-5 (V3.1B)" from dropdown
4. **Type Problem**: "This machine wont start"
5. **Send Message**

**Expected Result**:
- ✅ Blue step card appears
- ✅ Shows ONE instruction (not all steps)
- ✅ Three feedback buttons at bottom: "It worked!" / "Partially worked" / "Didn't work"
- ✅ Backend logs show: `[DEBUG] TRIGGERING TROUBLESHOOTING WORKFLOW`

**If it fails**:
- Check backend logs: `docker-compose logs ai_assistant | grep DEBUG`
- Look for: `is_troubleshooting=True`, `machine_id=<uuid>`, `user_messages` count

---

### Test 2: Step-by-Step Workflow

1. Complete Test 1 to get first step
2. **Click "Didn't work"** button
3. **Expected**: Second step appears with new instruction
4. **Click "Partially worked"** button
5. **Expected**: Third step or follow-up question
6. **Click "It worked!"** button
7. **Expected**: Completion message or next diagnostic step

**What to verify**:
- ✅ Only ONE step shows at a time
- ✅ Feedback buttons disappear after clicking
- ✅ Next step appears automatically
- ✅ Each step has clear instructions
- ✅ Safety warnings show if applicable

---

### Test 3: Different Problem Types

Try these problem descriptions (with machine selected):

1. **"Machine won't start"** → Should trigger power/electrical checks
2. **"Poor cleaning quality"** → Should trigger cleaning system checks
3. **"Strange noise"** → Should trigger mechanical checks
4. **"Error message on screen"** → Should ask for error code
5. **"Leaking water"** → Should trigger seal/connection checks

**Expected**: Each should start interactive troubleshooting with relevant first step

---

### Test 4: Without Machine Selected

1. Open chat
2. **Don't select a machine**
3. Type: "My machine won't start"
4. Send

**Expected**: Regular chat response (all steps at once) - this is correct behavior since no machine is selected

---

### Test 5: Mid-Conversation Troubleshooting

1. Open chat
2. Send: "Hello"
3. Get response
4. **Now select a machine**
5. Send: "This machine has a problem"

**Expected**: Should still trigger interactive troubleshooting (the fix allows this)

---

## Backend Debug Logs

To see what's happening behind the scenes:

```bash
# Watch logs in real-time
docker-compose logs -f ai_assistant | grep -E "DEBUG|troubleshooting"

# Check recent troubleshooting attempts
docker-compose logs --tail=100 ai_assistant | grep "TRIGGERING TROUBLESHOOTING"
```

**Look for these log lines**:
```
[DEBUG] Troubleshooting detection: is_troubleshooting=True, machine_id=<uuid>, history_len=3
[DEBUG] Message: This machine wont start
[DEBUG] TRIGGERING TROUBLESHOOTING WORKFLOW for session <session_id>
[DEBUG] Starting interactive troubleshooting workflow for session <session_id>
[DEBUG] Workflow state retrieved: <state>
[DEBUG] Returning troubleshooting step
```

---

## Known Issues (Still Need Fixing)

### 1. No "New Session" Button
**Problem**: Can't clear chat to start fresh session
**Impact**: Medium - users can refresh page as workaround
**Fix**: See `fix_chat_session_ux.md` for implementation

### 2. Feedback Buttons May Not Appear
**Problem**: Strict visibility conditions in frontend
**Impact**: High - blocks workflow progression
**Fix**: See `fix_chat_session_ux.md` for implementation

### 3. Session Persists After Closing Chat
**Problem**: Reopening chat shows old conversation
**Impact**: Medium - confusing for users
**Fix**: See `fix_chat_session_ux.md` for implementation

---

## If Troubleshooting Still Doesn't Trigger

### Check 1: Verify Fix is Applied
```bash
# Check the code has the fix
docker-compose exec ai_assistant grep -A 3 "user_messages = \[msg for msg" /app/app/routers/chat.py
```

Should show:
```python
user_messages = [msg for msg in request.conversation_history if msg.role == 'user']

if is_troubleshooting and request.machine_id and len(user_messages) <= 1:
```

### Check 2: Verify Container Restarted
```bash
# Check container uptime (should be recent)
docker-compose ps ai_assistant
```

### Check 3: Check OpenAI Connection
```bash
# Test OpenAI API
docker-compose exec ai_assistant python -c "
from app.llm_client import LLMClient
from app.config import settings
client = LLMClient(settings.OPENAI_API_KEY, settings.OPENAI_MODEL)
print('OpenAI connected:', client.client is not None)
"
```

### Check 4: Verify Database Tables
```bash
# Check AI tables exist
docker-compose exec db psql -U abparts_user -d abparts_dev -c "
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name LIKE 'ai_%'
ORDER BY table_name;
"
```

Should show:
- ai_messages
- ai_sessions
- troubleshooting_sessions
- troubleshooting_steps

---

## Next Steps

### Immediate (Test Now)
1. ✅ Test basic troubleshooting trigger (Test 1)
2. ✅ Test step-by-step workflow (Test 2)
3. ✅ Test different problem types (Test 3)

### Short-term (Implement Soon)
1. ⏳ Add "New Session" button (see `fix_chat_session_ux.md`)
2. ⏳ Fix feedback button visibility (see `fix_chat_session_ux.md`)
3. ⏳ Add session status indicator (see `fix_chat_session_ux.md`)

### Medium-term (Nice to Have)
1. ⏳ Add session history view
2. ⏳ Add ability to resume previous sessions
3. ⏳ Add session export/sharing

---

## Success Criteria

Interactive troubleshooting is working correctly when:

- ✅ Selecting machine + reporting problem triggers step-by-step mode
- ✅ Only ONE step shows at a time
- ✅ Feedback buttons appear and work
- ✅ Workflow progresses based on feedback
- ✅ Completion or escalation happens appropriately
- ✅ Each session is tracked in database
- ✅ Learning system records outcomes

---

## Test Results

**Date**: _____________
**Tester**: _____________

| Test | Result | Notes |
|------|--------|-------|
| Test 1: Basic Trigger | ⬜ Pass ⬜ Fail | |
| Test 2: Step-by-Step | ⬜ Pass ⬜ Fail | |
| Test 3: Different Problems | ⬜ Pass ⬜ Fail | |
| Test 4: No Machine | ⬜ Pass ⬜ Fail | |
| Test 5: Mid-Conversation | ⬜ Pass ⬜ Fail | |

**Overall Status**: ⬜ Working ⬜ Needs More Fixes

**Additional Notes**:
_____________________________________________
_____________________________________________
_____________________________________________

---

## Quick Reference

**Login**: `dthomaz/amFT1999!`
**Test Machine**: KEF-5 (V3.1B)
**Test Problem**: "This machine wont start"
**Expected**: Blue step card with 3 buttons
**Logs**: `docker-compose logs -f ai_assistant | grep DEBUG`

---

**Last Updated**: 2026-02-01 09:18 UTC
**Status**: Fix applied, container restarted, ready for testing
