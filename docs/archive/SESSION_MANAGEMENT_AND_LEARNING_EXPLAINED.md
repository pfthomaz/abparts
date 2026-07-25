# Session Management and Learning System - Complete Explanation

## Overview

The AI Assistant uses a sophisticated session management system that tracks each troubleshooting interaction from start to finish, learns from outcomes, and ensures each new issue starts fresh while building on historical knowledge.

## How Sessions Work

### 1. Session Creation (New Issue)

When you start a new troubleshooting interaction:

```
User: "My AutoBoss won't start" + selects machine
    ↓
System detects: problem keywords + machine selected + early conversation
    ↓
Creates NEW SESSION with unique ID
    ↓
Stores in database: ai_sessions table
    - session_id: unique UUID
    - user_id: your user ID
    - machine_id: selected machine
    - status: 'active'
    - problem_description: "My AutoBoss won't start"
    - language: your preferred language
    - created_at: timestamp
```

**Key Point**: Each new problem gets a **completely new session**. The system doesn't confuse different issues.

### 2. Session Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│ SESSION STATES                                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. ACTIVE                                             │
│     - Troubleshooting in progress                      │
│     - User working through steps                       │
│     - Providing feedback on each step                  │
│                                                         │
│  2. COMPLETED (Problem Solved)                         │
│     - User feedback: "It worked!"                      │
│     - Resolution summary stored                        │
│     - Learning triggered                               │
│     - Session closed                                   │
│                                                         │
│  3. ESCALATED (Needs Expert)                           │
│     - Multiple steps didn't work                       │
│     - User feedback: "Still broken"                    │
│     - Escalation reason stored                         │
│     - Learning triggered                               │
│     - Session closed                                   │
│                                                         │
│  4. ABANDONED (User Left)                              │
│     - No activity for extended period                  │
│     - Partial learning triggered                       │
│     - Session closed                                   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 3. What Gets Stored Per Session

**In `ai_sessions` table:**
- Session ID (unique identifier)
- User ID and Machine ID
- Problem description
- Status (active/completed/escalated)
- Resolution summary (how it was solved)
- Language preference
- Session metadata (diagnostic assessment, machine context)
- Timestamps (created, updated)

**In `troubleshooting_steps` table:**
- Each step you go through
- Step number (1, 2, 3...)
- Instruction given
- Your feedback on each step
- Whether step was completed
- Whether step was successful
- Timestamps

**In `ai_messages` table:**
- Every message exchanged
- User messages and AI responses
- Message type (text, troubleshooting_step, completion)
- Language used
- Timestamps

## How Learning Works

### 1. During the Session

As you provide feedback on each step:

```
Step 1: "Check power connections"
Your feedback: "It worked!" ✓
    ↓
System records:
- This solution worked for "startup" problems
- On this machine model (V4.0)
- Success rate increases
- Confidence score increases
```

### 2. At Session Completion

When session ends (solved, escalated, or abandoned):

```python
# Learning Service is triggered
learn_from_session_outcome(
    session_id=session_id,
    outcome="resolved",  # or "escalated" or "abandoned"
    solutions_used=["Check power connections", "Verify switch position"],
    user_feedback={"satisfaction": 5, "time_taken": 10}
)
```

**What happens:**

1. **Solution Effectiveness Tracking**
   - Each solution used gets rated
   - Success rate calculated: (times_successful / times_suggested) × 100
   - Stored in `solution_effectiveness` table

2. **Priority Score Calculation**
   ```
   Priority Score = (success_rate / 100) × recency_factor × expert_bonus × usage_factor
   
   Where:
   - success_rate: 0-100% (how often it works)
   - recency_factor: 0.5-1.0 (recent solutions weighted higher)
   - expert_bonus: 1.2 if verified by expert, 1.0 otherwise
   - usage_factor: min(times_used / 10, 1.0) (more tested = more reliable)
   ```

3. **Pattern Recognition**
   - Identifies trending problems
   - Detects underperforming solutions
   - Finds knowledge gaps
   - Analyzes success patterns

### 3. For Next Session (New Issue)

When you start a NEW troubleshooting session:

```
New Problem: "Machine making strange noise"
    ↓
System creates NEW SESSION (fresh start)
    ↓
But queries learning database:
    ↓
"What solutions worked for 'mechanical' problems on V4.0 machines?"
    ↓
Retrieves prioritized solutions:
1. "Inspect drive belt" (95% success, used 20 times)
2. "Check motor bearings" (87% success, used 15 times)
3. "Verify alignment" (75% success, used 10 times)
    ↓
Presents BEST solution first (learned from history)
```

**Key Point**: New session = fresh conversation, but **informed by all previous sessions**.

## Session Isolation vs. Learning

### What's Isolated (Per Session)
- ✅ Conversation history (doesn't mix with other issues)
- ✅ Current troubleshooting steps
- ✅ Session status and outcome
- ✅ Problem description
- ✅ Resolution summary

### What's Shared (Across All Sessions)
- ✅ Solution effectiveness data
- ✅ Success rates per problem category
- ✅ Machine-specific patterns
- ✅ Expert-verified solutions
- ✅ Knowledge base content

## Example: Two Separate Issues

### Issue 1: Won't Start
```
Session A (Created: 10:00 AM)
├─ Problem: "Won't start"
├─ Machine: KEF-1 (V4.0)
├─ Step 1: Check power → "Worked!" ✓
├─ Status: COMPLETED
└─ Learning: "Check power" +1 success for "startup" problems

[Session A is now CLOSED]
```

### Issue 2: Poor Cleaning (Later Same Day)
```
Session B (Created: 2:00 PM)  ← NEW SESSION
├─ Problem: "Not cleaning well"
├─ Machine: KEF-1 (V4.0)  ← Same machine, different problem
├─ Step 1: Check nozzles → "Partially worked"
├─ Step 2: Replace filter → "Worked!" ✓
├─ Status: COMPLETED
└─ Learning: "Replace filter" +1 success for "cleaning_performance"

[Session B is now CLOSED]
```

**Important**: These are **completely separate sessions**. The system doesn't confuse them. But when you report a "startup" problem in the future, it will prioritize "Check power" because it learned from Session A.

## How to View Your Sessions

You can retrieve your session history:

```
GET /api/ai/sessions/user/{user_id}
```

Returns:
```json
{
  "sessions": [
    {
      "session_id": "abc-123",
      "problem_description": "Won't start",
      "status": "completed",
      "resolution_summary": "Problem resolved through troubleshooting",
      "created_at": "2026-02-01T10:00:00",
      "steps_count": 1
    },
    {
      "session_id": "def-456",
      "problem_description": "Not cleaning well",
      "status": "completed",
      "resolution_summary": "Problem resolved through troubleshooting",
      "created_at": "2026-02-01T14:00:00",
      "steps_count": 2
    }
  ]
}
```

## Learning Metrics Tracked

### Per Solution
- **Times suggested**: How many times this solution was recommended
- **Times successful**: How many times it actually worked
- **Success rate**: Percentage (times_successful / times_suggested × 100)
- **Problem category**: What type of problem it solves
- **Machine model**: Which models it works best on
- **Expert verified**: Whether an expert confirmed it
- **Last used**: When it was last suggested
- **Average effectiveness**: User ratings (1-4 scale)

### Per Session
- **Resolution time**: How long to solve
- **Steps to resolution**: How many steps needed
- **User satisfaction**: Rating (1-5)
- **Outcome**: Resolved, escalated, or abandoned
- **Problem category**: Type of issue
- **Machine context**: Which machine, hours, maintenance history

### System-Wide
- **Trending problems**: What issues are increasing
- **Knowledge gaps**: Where escalations happen most
- **Success patterns**: What makes troubleshooting successful
- **Underperforming solutions**: What's not working anymore

## Session Cleanup

### Automatic Cleanup
- **Redis cache**: 24-hour TTL (time-to-live)
- **Active sessions**: Marked abandoned after 1 hour of inactivity
- **Database**: Sessions kept indefinitely for learning

### Manual Session End
You can explicitly end a session:
```
POST /api/ai/sessions/{session_id}/complete
{
  "outcome": "resolved",
  "satisfaction": 5,
  "feedback": "Great help!"
}
```

## Privacy and Data

### What's Stored
- ✅ Problem descriptions (encrypted)
- ✅ Solutions tried
- ✅ Feedback provided
- ✅ Machine context
- ✅ Timestamps

### What's NOT Stored
- ❌ Personal information (filtered out)
- ❌ Sensitive data (redacted automatically)
- ❌ Unrelated conversation

### Data Retention
- **Active sessions**: Until completed/escalated/abandoned
- **Historical sessions**: Kept for learning (anonymized after 90 days)
- **Learning data**: Kept indefinitely (aggregated, no personal info)

## Testing the System

### Test Scenario 1: Complete Resolution
```
1. Start chat, select machine
2. Type: "My machine won't start"
3. Get Step 1 card
4. Click "It worked!"
5. Session completes
6. Learning records success

→ Next time someone has startup issue, this solution is prioritized
```

### Test Scenario 2: Escalation
```
1. Start chat, select machine
2. Type: "Strange error code E47"
3. Get Step 1 card
4. Click "Didn't work"
5. Get Step 2 card
6. Click "Didn't work"
7. Get Step 3 card
8. Click "Didn't work"
9. System suggests escalation
10. Session escalates
11. Learning records: "E47" needs expert help

→ Next time someone reports E47, system escalates faster
```

### Test Scenario 3: Multiple Issues Same Day
```
Morning:
- Issue: "Won't start" → Session A → Resolved

Afternoon:
- Issue: "Leaking water" → Session B (NEW) → Resolved

Evening:
- Issue: "Remote not working" → Session C (NEW) → Escalated

→ Three separate sessions, each tracked independently
→ All contribute to learning database
```

## Summary

**Session Management:**
- ✅ Each issue = new session
- ✅ Sessions are isolated (no confusion)
- ✅ Sessions track complete interaction
- ✅ Sessions close when resolved/escalated/abandoned

**Learning System:**
- ✅ Learns from every session outcome
- ✅ Tracks solution effectiveness
- ✅ Prioritizes successful solutions
- ✅ Identifies patterns and gaps
- ✅ Improves recommendations over time

**Key Benefit:**
Every troubleshooting session makes the AI smarter, but each new issue starts with a clean slate while benefiting from all historical knowledge.

---

**For Testing:**
1. Try solving an issue completely
2. Start a new issue (verify it's a new session)
3. Check that solutions improve over time
4. Verify sessions don't interfere with each other

**Questions to Verify:**
- ✅ Does each new issue get a new session ID?
- ✅ Are previous conversations kept separate?
- ✅ Does the system learn from outcomes?
- ✅ Do solutions get better with more data?
- ✅ Can you see your session history?
