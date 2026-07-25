# Interactive Troubleshooting - Quick Start Guide

## 🚀 Ready to Test!

The interactive step-by-step troubleshooting feature is fully implemented and ready for testing.

## Quick Test (5 minutes)

### 1. Start the Application
```bash
# If not already running
docker-compose up
```

### 2. Open the App
- Navigate to `http://localhost:3000`
- Login with your credentials

### 3. Test the Feature

**Step 1: Open Chat Widget**
- Click the blue chat button (bottom left)

**Step 2: Select a Machine**
- Click the machine icon in chat header
- Select any AutoBoss machine from the list

**Step 3: Report a Problem**
Type one of these messages:
- "My AutoBoss won't start"
- "The machine has a problem"
- "Not working properly"
- "I have an issue with the machine"

**Step 4: See the Magic! ✨**
You should see a beautiful blue step card with:
- Step number (e.g., "Step 1")
- Estimated time (e.g., "5 min")
- Success rate badge (if available)
- Clear instruction
- Safety warnings (if any)
- Three feedback buttons

**Step 5: Provide Feedback**
Click one of the buttons:
- 🟢 **"It worked!"** - Problem resolved
- 🟡 **"Partially worked"** - Some improvement
- 🔴 **"Didn't work"** - Try another approach

**Step 6: Continue or Complete**
- If you clicked "It worked!" → See completion message
- If you clicked other buttons → Get next step
- Repeat until problem is resolved

## What to Look For

### ✅ Good Signs
- Step card appears with blue border
- Buttons are large and easy to click
- Estimated time shows
- Safety warnings display in yellow box
- Smooth transitions between steps
- Completion message appears when done

### ❌ Issues to Report
- Step card doesn't appear
- Buttons don't work
- Translations missing
- Layout broken on mobile
- Errors in console

## Test Different Scenarios

### Scenario 1: Quick Resolution
```
User: "Machine won't start"
System: "Step 1: Check master switch..."
User: [It worked!]
System: "✓ Problem resolved!"
```

### Scenario 2: Multiple Steps
```
User: "Low pressure problem"
System: "Step 1: Check HP gauge..."
User: [Didn't work]
System: "Step 2: Check water supply..."
User: [Partially worked]
System: "Step 3: Inspect unloader valve..."
User: [It worked!]
System: "✓ Problem resolved!"
```

### Scenario 3: Escalation
```
User: "Strange noise from motor"
System: "Step 1: Check for loose parts..."
User: [Didn't work]
System: "Step 2: Inspect motor mounts..."
User: [Didn't work]
System: "⚠ Requires expert assistance"
```

## Test in Different Languages

1. Go to Profile → Change language
2. Start troubleshooting
3. Verify translations work:
   - English (en)
   - Greek (el)
   - Arabic (ar)
   - Spanish (es)
   - Turkish (tr)
   - Norwegian (no)

## Mobile Testing

1. Open on mobile device or resize browser
2. Verify:
   - Step card fits screen
   - Buttons are easy to tap (44px minimum)
   - Text is readable
   - No horizontal scrolling

## API Testing (Advanced)

### Test Chat Endpoint
```bash
curl -X POST http://localhost:8001/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My machine has a problem",
    "machine_id": "your-machine-uuid",
    "user_id": "your-user-uuid",
    "language": "en"
  }'
```

Expected response:
```json
{
  "response": "Step instruction text...",
  "message_type": "troubleshooting_step",
  "step_data": {
    "step_id": "uuid",
    "step_number": 1,
    "estimated_duration": 5,
    "confidence_score": 0.85,
    "safety_warnings": ["..."],
    "expected_outcomes": ["..."]
  }
}
```

### Test Feedback Endpoint
```bash
curl -X POST http://localhost:8001/api/ai/chat/step-feedback \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-uuid",
    "step_id": "step-uuid",
    "feedback": "worked",
    "language": "en"
  }'
```

## Troubleshooting

### Issue: Step card doesn't appear
**Solution**: 
- Ensure machine is selected
- Check browser console for errors
- Verify backend is running

### Issue: Buttons don't work
**Solution**:
- Check network tab for failed requests
- Verify session_id and step_id are set
- Check backend logs

### Issue: Translations missing
**Solution**:
- Run: `python3 add_troubleshooting_translations.py`
- Refresh browser
- Clear cache

### Issue: Backend error
**Solution**:
- Check logs: `docker-compose logs ai_assistant`
- Verify database is running
- Check OpenAI API key is set

## Success Metrics

After testing, you should see:

1. **Smooth User Experience**
   - Steps appear quickly (< 2 seconds)
   - Feedback is processed instantly
   - UI is responsive and intuitive

2. **Learning Works**
   - Database records solution effectiveness
   - Success rates update after feedback
   - Future sessions use learned data

3. **Multi-language Support**
   - All translations display correctly
   - RTL languages (Arabic) work properly
   - No missing translation keys

## Next Steps After Testing

1. **Gather Feedback**
   - Ask users to test
   - Collect usability feedback
   - Note any confusion points

2. **Monitor Metrics**
   - Track completion rates
   - Monitor escalation frequency
   - Analyze learning effectiveness

3. **Iterate**
   - Refine based on feedback
   - Improve prompts
   - Add enhancements

4. **Deploy to Production**
   - After successful testing
   - Monitor closely
   - Be ready to rollback

## Questions?

Check these files:
- **Complete Guide**: `AI_ASSISTANT_INTERACTIVE_TROUBLESHOOTING_COMPLETE.md`
- **Implementation Details**: `AI_ASSISTANT_INTERACTIVE_TROUBLESHOOTING_IMPLEMENTATION.md`
- **Planning Document**: `AI_ASSISTANT_INTERACTIVE_TROUBLESHOOTING_PLAN.md`

---

## 🎯 Ready to Test!

Open the app, select a machine, report a problem, and watch the interactive troubleshooting in action!
