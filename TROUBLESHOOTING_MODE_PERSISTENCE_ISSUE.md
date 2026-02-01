# Troubleshooting Mode Persistence Issue

## Problem Identified

The interactive troubleshooting works great for 6+ steps when using feedback buttons, BUT when the user sends a clarifying message (instead of clicking a button), the system:

1. ❌ Exits troubleshooting mode
2. ❌ Returns to regular chat
3. ❌ Gives a LIST of steps instead of continuing step-by-step

## Example from Testing

**What Worked** (6 steps):
```
Step 1: Check power connections → "Didn't work"
Step 2: Check power switch → "Didn't work"  
Step 3: Examine power cord → "Didn't work"
Step 4: Check outlet → "Didn't work"
Step 5: Ensure cord not damaged → "Didn't work"
Step 6: Check outlet working → "Didn't work"
```

**What Broke** (user clarification):
```
User: "there is no power cord in the AutoBoss... it has a diesel engine and a battery..."

System Response: [LIST OF 4 STEPS] ❌
1. Check diesel fuel level
2. Check battery connections
3. Check starter motor
4. Check fuses
```

**Should Have Been** (continue step-by-step):
```
System Response: [SINGLE STEP] ✅
Step 7: Check the diesel fuel level in the tank. Is the tank at least 1/4 full?

[It worked!] [Partially worked] [Didn't work]
```

---

## Root Cause

The system has TWO paths for handling messages:

### Path 1: Feedback Button Click ✅
- Endpoint: `/api/ai/chat/step-feedback`
- Stays in troubleshooting mode
- Returns next step with feedback buttons
- Works perfectly!

### Path 2: Regular Message ❌
- Endpoint: `/api/ai/chat`
- Checks if troubleshooting should START
- Doesn't check if troubleshooting is ALREADY ACTIVE
- Falls back to regular chat

---

## The Fix

The `/api/ai/chat` endpoint needs to:

1. **Check if session is in active troubleshooting mode**
2. **If yes, treat message as clarification and continue step-by-step**
3. **If no, check if troubleshooting should start**

### Current Logic (Broken)
```python
# In ai_assistant/app/routers/chat.py

# Detect if this is a troubleshooting scenario
is_troubleshooting = _detect_troubleshooting_intent(message_to_process)

# Check if we should start interactive troubleshooting workflow
user_messages = [msg for msg in request.conversation_history if msg.role == 'user']

if is_troubleshooting and request.machine_id and len(user_messages) <= 1:
    # Start troubleshooting
```

**Problem**: Only checks if troubleshooting should START, not if it's already ACTIVE

### Fixed Logic (Needed)
```python
# In ai_assistant/app/routers/chat.py

# FIRST: Check if session is already in troubleshooting mode
if request.session_id:
    workflow_state = await troubleshooting_service.get_workflow_state(request.session_id)
    
    if workflow_state and workflow_state.workflow_status == 'active':
        # Session is in active troubleshooting - treat message as clarification
        # Generate next step incorporating the new information
        next_step = await troubleshooting_service.process_clarification(
            session_id=request.session_id,
            clarification=message_to_process,
            language=language
        )
        
        return ChatResponse(
            response=next_step.instruction,
            session_id=request.session_id,
            model_used="troubleshooting-engine",
            tokens_used=0,
            response_time=time.time() - start_time,
            success=True,
            message_type="diagnostic_step",
            step_data={...}
        )

# THEN: Check if troubleshooting should start
is_troubleshooting = _detect_troubleshooting_intent(message_to_process)
user_messages = [msg for msg in request.conversation_history if msg.role == 'user']

if is_troubleshooting and request.machine_id and len(user_messages) <= 1:
    # Start new troubleshooting workflow
```

---

## Implementation Steps

### Step 1: Add Clarification Handler to TroubleshootingService

**File**: `ai_assistant/app/services/troubleshooting_service.py`

Add new method:
```python
async def process_clarification(
    self,
    session_id: str,
    clarification: str,
    language: str = "en"
) -> Optional[TroubleshootingStepData]:
    """
    Process user clarification during active troubleshooting.
    
    This handles cases where the user provides additional information
    instead of clicking a feedback button.
    """
    # Get current workflow state
    workflow_state = await self.get_workflow_state(session_id)
    if not workflow_state:
        return None
    
    # Get session and assessment
    session = await self._get_session(session_id)
    if not session:
        return None
    
    # Update problem description with clarification
    updated_description = f"{session.problem_description}\n\nAdditional info: {clarification}"
    
    # Generate next step incorporating the clarification
    next_step_number = workflow_state.current_step.step_number + 1
    
    # Use LLM to generate next step with updated context
    context = {
        "problem_description": updated_description,
        "clarification": clarification,
        "previous_steps": [step.instruction for step in workflow_state.completed_steps],
        "current_step": workflow_state.current_step.instruction,
        "machine_context": await self._get_machine_context(session.machine_id) if session.machine_id else None
    }
    
    instruction = await self._generate_step_with_llm(context, language)
    
    # Create next step
    next_step = TroubleshootingStepData(
        step_id=str(uuid.uuid4()),
        step_number=next_step_number,
        instruction=instruction,
        expected_outcomes=[],
        user_feedback=None,
        status=StepStatus.pending,
        confidence_score=0.7,
        next_steps={},
        requires_feedback=True,
        estimated_duration=15,
        safety_warnings=[],
        created_at=datetime.utcnow(),
        completed_at=None
    )
    
    # Store the step and get database ID
    db_step_id = await self._store_troubleshooting_step(session_id, next_step)
    if db_step_id:
        next_step.step_id = db_step_id
    
    return next_step
```

### Step 2: Update Chat Router

**File**: `ai_assistant/app/routers/chat.py`

In the `chat()` function, add check BEFORE the troubleshooting detection:

```python
# Around line 250, BEFORE "Detect if this is a troubleshooting scenario"

# Check if session is already in active troubleshooting mode
if request.session_id:
    try:
        from ..session_manager import session_manager
        troubleshooting_service = TroubleshootingService(llm_client, session_manager)
        workflow_state = await troubleshooting_service.get_workflow_state(request.session_id)
        
        if workflow_state and workflow_state.workflow_status == 'active':
            logger.info(f"Session {request.session_id} is in active troubleshooting - processing clarification")
            
            # Process as clarification
            next_step = await troubleshooting_service.process_clarification(
                session_id=request.session_id,
                clarification=message_to_process,
                language=language
            )
            
            if next_step:
                # Store user message
                if request.user_id:
                    try:
                        with get_db_session() as db:
                            db.execute(text("""
                                INSERT INTO ai_messages (id, session_id, sender, content, message_type, language, timestamp)
                                VALUES (:id, :session_id, :sender, :content, :message_type, :language, NOW())
                            """), {
                                'id': str(uuid.uuid4()),
                                'session_id': request.session_id,
                                'sender': 'user',
                                'content': message_to_process,
                                'message_type': 'text',
                                'language': language
                            })
                            
                            # Store assistant response
                            db.execute(text("""
                                INSERT INTO ai_messages (id, session_id, sender, content, message_type, language, timestamp)
                                VALUES (:id, :session_id, :sender, :content, :message_type, :language, NOW())
                            """), {
                                'id': str(uuid.uuid4()),
                                'session_id': request.session_id,
                                'sender': 'assistant',
                                'content': next_step.instruction,
                                'message_type': 'diagnostic_step',
                                'language': language
                            })
                    except Exception as e:
                        logger.warning(f"Failed to store messages: {e}")
                
                return ChatResponse(
                    response=next_step.instruction,
                    session_id=request.session_id,
                    model_used="troubleshooting-engine",
                    tokens_used=0,
                    response_time=time.time() - start_time,
                    success=True,
                    message_type="diagnostic_step",
                    step_data={
                        "step_id": next_step.step_id,
                        "step_number": next_step.step_number,
                        "estimated_duration": next_step.estimated_duration,
                        "confidence_score": next_step.confidence_score,
                        "requires_feedback": next_step.requires_feedback,
                        "safety_warnings": next_step.safety_warnings,
                        "expected_outcomes": next_step.expected_outcomes
                    }
                )
    except Exception as e:
        logger.warning(f"Failed to check troubleshooting state: {e}")
        # Continue to regular chat handling

# NOW continue with existing troubleshooting detection logic...
```

---

## Benefits After Fix

### User Experience
- ✅ Can provide clarifications without breaking workflow
- ✅ System adapts to new information
- ✅ Maintains step-by-step format throughout
- ✅ No confusing mode switches

### Example Fixed Flow
```
Step 6: Check outlet working → "Didn't work"

User: "there is no power cord... it has a diesel engine and battery"

Step 7: Check the diesel fuel level in the tank. Is it at least 1/4 full?
[It worked!] [Partially worked] [Didn't work]

User: "Didn't work"

Step 8: Check the battery connections for loose wires or corrosion...
[It worked!] [Partially worked] [Didn't work]
```

---

## Testing After Fix

### Test 1: Clarification Mid-Workflow
1. Start troubleshooting: "Machine won't start"
2. Click "Didn't work" 2-3 times
3. Type clarification: "The machine has a diesel engine"
4. ✅ Should get next step (not a list)
5. ✅ Should still have feedback buttons

### Test 2: Multiple Clarifications
1. Start troubleshooting
2. Provide clarification
3. Click "Didn't work"
4. Provide another clarification
5. ✅ Should stay in step-by-step mode throughout

### Test 3: Question During Troubleshooting
1. Start troubleshooting
2. Ask question: "Where is the fuel tank?"
3. ✅ Should answer question AND provide next step
4. ✅ Should maintain troubleshooting format

---

## Priority

**HIGH** - This is critical for user experience

Users need to be able to:
- Clarify information
- Correct assumptions
- Ask questions
- Provide context

Without breaking the step-by-step flow that makes troubleshooting accessible to "simple, step by step people" (as you correctly noted).

---

## Current Status

- ✅ Troubleshooting triggers correctly
- ✅ Step-by-step works with feedback buttons
- ✅ Multiple steps work (tested 6+ steps)
- ✅ Database persistence works
- ❌ **Clarifications break the workflow** ← THIS NEEDS FIXING

---

## Estimated Implementation Time

- Add `process_clarification` method: 30 minutes
- Update chat router logic: 30 minutes
- Test and debug: 30 minutes
- **Total**: ~1.5 hours

---

**Last Updated**: 2026-02-01 11:45 UTC
**Status**: Issue identified, solution designed, ready to implement
**Priority**: HIGH - Critical UX issue
