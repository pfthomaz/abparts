# Learning System - Quick Reference

## What It Does

The AI Assistant now **automatically learns** from every completed troubleshooting session and stores knowledge in the database.

---

## How to See It Working

### 1. Complete a Troubleshooting Session
- Login and select a machine
- Start troubleshooting: "Machine does not start"
- Provide clarification: "AutoBoss uses diesel engine, not power cord"
- Click "It worked!" when resolved

### 2. Check What Was Learned
```sql
-- View recent session outcomes
SELECT 
    outcome_type, 
    resolution_time_minutes, 
    steps_taken,
    created_at
FROM session_outcomes 
ORDER BY created_at DESC 
LIMIT 5;

-- View learned facts
SELECT 
    machine_model,
    fact_type,
    fact_key,
    fact_value,
    times_confirmed,
    confidence_score
FROM machine_facts 
ORDER BY times_confirmed DESC;
```

---

## Database Tables

### session_outcomes
Stores completion metrics for each session:
- Outcome type (resolved/escalated/abandoned)
- Resolution time in minutes
- Number of steps taken
- Extracted learnings (JSON)

### machine_facts
Stores learned facts about machines:
- Machine model (V3.1B, V4.0, etc.)
- Fact type (power_source, component, procedure, specification)
- Fact key and value
- Confidence score (0.0 - 1.0)
- Times confirmed
- Source sessions (array of session IDs)

### solution_effectiveness
Tracks which solutions work best:
- Problem category
- Solution description
- Machine model
- Success/failure counts
- Average resolution time

---

## Key Features

✅ **Automatic** - Learns without manual intervention
✅ **Smart** - Uses AI to extract meaningful facts
✅ **Cumulative** - Knowledge builds over time
✅ **Confident** - Facts gain confidence with confirmations

---

## What Gets Learned

1. **Machine Facts**: "AutoBoss uses diesel engine, not power cord"
2. **Successful Steps**: Which troubleshooting steps work
3. **Failed Approaches**: What doesn't work
4. **Key Insights**: Common misconceptions

---

## Files to Know

- `ai_assistant/app/services/session_completion_service.py` - Learning logic
- `ai_assistant/app/services/troubleshooting_service.py` - Integration point
- `ai_assistant/create_learning_tables.sql` - Database schema

---

## Quick Commands

```bash
# Check AI assistant is running
docker-compose ps ai_assistant

# View AI assistant logs
docker-compose logs ai_assistant --tail 50

# Check learning tables exist
docker-compose exec -T db psql -U abparts_user -d abparts_dev -c \
  "SELECT tablename FROM pg_tables WHERE tablename LIKE '%outcomes%' OR tablename LIKE '%facts%';"

# View recent learnings
docker-compose exec -T db psql -U abparts_user -d abparts_dev -c \
  "SELECT COUNT(*) as total_facts, 
          SUM(times_confirmed) as total_confirmations 
   FROM machine_facts;"
```

---

## Status: ACTIVE ✅

The learning system is running and will automatically learn from all completed troubleshooting sessions.

**Test it now**: Complete a troubleshooting session and watch the knowledge grow!
