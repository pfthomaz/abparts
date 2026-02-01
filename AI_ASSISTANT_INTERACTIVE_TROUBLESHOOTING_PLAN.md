# AI Assistant Interactive Step-by-Step Troubleshooting Implementation Plan

## Overview
Transform the AI Assistant from providing all troubleshooting steps at once to an interactive, step-by-step workflow that learns from user interactions and prioritizes proven solutions.

## Current State Analysis

### Existing Infrastructure (Already Implemented)
1. **Troubleshooting Service** (`ai_assistant/app/services/troubleshooting_service.py`)
   - ✅ Step-by-step workflow infrastructure exists
   - ✅ `start_troubleshooting_workflow()` - initiates diagnostic assessment
   - ✅ `process_user_feedback()` - handles feedback and generates next steps
   - ✅ Database storage for steps and feedback
   - ✅ Multi-language support

2. **Learning Service** (`ai_assistant/app/services/learning_service.py`)
   - ✅ Solution prioritization based on historical success
   - ✅ `prioritize_solutions()` - ranks solutions by effectiveness
   - ✅ `learn_from_session_outcome()` - updates solution effectiveness
   - ✅ Success rate tracking and recency factors
   - ✅ Expert verification support

3. **Database Models** (`ai_assistant/app/models.py`)
   - ✅ `TroubleshootingStep` model
   - ✅ `solution_effectiveness` table
   - ✅ Session tracking with metadata

### What Needs to be Modified

1. **Chat Router** (`ai_assistant/app/routers/chat.py`)
   - ❌ Currently provides all steps at once
   - ❌ No detection of troubleshooting mode
   - ❌ No integration with troubleshooting service

2. **LLM Client** (`ai_assistant/app/llm_client.py`)
   - ❌ Generates multiple steps in one response
   - ❌ No single-step mode

3. **Frontend ChatWidget** (`frontend/src/components/ChatWidget.js`)
   - ❌ No step feedback UI
   - ❌ No visual indication of troubleshooting mode
   - ❌ No buttons for "worked", "didn't work", "partially worked"

## Implementation Plan

### Phase 1: Backend - Enable Interactive Mode

#### 1.1 Modify Chat Router
**File**: `ai_assistant/app/routers/chat.py`

Add troubleshooting mode detection:
```python
# Detect if user is describing a problem (keywords: problem, issue, not working, broken, etc.)
# If detected, start interactive troubleshooting workflow
# Return first step with special format indicating interactive mode
```

Add new endpoint for step feedback:
```python
@router.post("/chat/step-feedback")
async def submit_step_feedback(
    session_id: str,
    step_id: str,
    feedback: str,  # "worked", "didnt_work", "partially_worked", or free text
    language: str = "en"
) -> StepResponse
```

#### 1.2 Integrate Learning Service
**File**: `ai_assistant/app/services/troubleshooting_service.py`

Modify `_generate_first_step()` to use learning service:
```python
# Get prioritized solutions from learning service
prioritized_solutions = await learning_service.prioritize_solutions(
    db, problem_category, machine_model
)

# Use top solution as first step
# Include success rate in response for user confidence
```

Modify `_generate_next_step()` to use learning:
```python
# After each step, update solution effectiveness
# Generate next step based on feedback and historical data
```

#### 1.3 Update LLM Prompts
**File**: `ai_assistant/app/llm_client.py`

Add single-step generation mode:
```python
def _build_single_step_prompt(self, context, language):
    """Generate ONE actionable step, not a list"""
    # Emphasize: "Provide ONLY the next single step"
    # "Do not provide multiple steps or a complete solution"
```

### Phase 2: Frontend - Interactive UI

#### 2.1 Add Step Feedback UI
**File**: `frontend/src/components/ChatWidget.js`

Add state for troubleshooting mode:
```javascript
const [troubleshootingMode, setTroubleshootingMode] = useState(false);
const [currentStepId, setCurrentStepId] = useState(null);
const [awaitingFeedback, setAwaitingFeedback] = useState(false);
```

Add feedback buttons component:
```javascript
const StepFeedbackButtons = ({ onFeedback }) => (
  <div className="flex gap-2 mt-2">
    <button onClick={() => onFeedback('worked')} className="bg-green-500...">
      ✓ {t('aiAssistant.feedback.worked')}
    </button>
    <button onClick={() => onFeedback('partially_worked')} className="bg-yellow-500...">
      ~ {t('aiAssistant.feedback.partiallyWorked')}
    </button>
    <button onClick={() => onFeedback('didnt_work')} className="bg-red-500...">
      ✗ {t('aiAssistant.feedback.didntWork')}
    </button>
  </div>
);
```

#### 2.2 Handle Step Responses
Modify message rendering to detect troubleshooting steps:
```javascript
// Check if message contains step indicator
if (message.type === 'troubleshooting_step') {
  // Render with feedback buttons
  // Show step number and estimated time
  // Display success rate if available
}
```

#### 2.3 Submit Feedback
Add feedback submission handler:
```javascript
const handleStepFeedback = async (feedback) => {
  // Send feedback to backend
  // Receive next step or completion message
  // Update UI accordingly
};
```

### Phase 3: Response Format Changes

#### 3.1 Step Response Structure
```json
{
  "response": "Step instruction text",
  "session_id": "uuid",
  "type": "troubleshooting_step",
  "step_data": {
    "step_id": "uuid",
    "step_number": 1,
    "estimated_duration": 15,
    "success_rate": 0.85,
    "requires_feedback": true,
    "safety_warnings": ["warning1", "warning2"]
  }
}
```

#### 3.2 Feedback Response Structure
```json
{
  "feedback_received": true,
  "next_step": {
    "response": "Next step instruction",
    "step_data": { ... }
  },
  "workflow_status": "in_progress|completed|escalated"
}
```

### Phase 4: Learning Integration

#### 4.1 Track Solution Effectiveness
After each step feedback:
```python
# Update solution effectiveness in database
await learning_service.update_solution_priority(
    db,
    solution_text=step.instruction,
    problem_category=assessment.problem_category,
    machine_model=machine_model,
    success_feedback=(feedback == "worked"),
    expert_verified=False
)
```

#### 4.2 Prioritize Common Solutions
When starting troubleshooting:
```python
# Get solutions sorted by success rate
solutions = await learning_service.prioritize_solutions(
    db,
    problem_category=assessment.problem_category,
    machine_model=machine_model,
    limit=10
)

# Use top solution as first step
# Fall back to LLM-generated steps if no historical data
```

### Phase 5: Translation Keys

Add new translation keys to all language files:
```json
{
  "aiAssistant": {
    "troubleshooting": {
      "stepNumber": "Step {number}",
      "estimatedTime": "Estimated time: {minutes} minutes",
      "successRate": "Success rate: {rate}%",
      "awaitingFeedback": "Please try this step and let me know the result"
    },
    "feedback": {
      "worked": "It worked!",
      "partiallyWorked": "Partially worked",
      "didntWork": "Didn't work",
      "provideFeedback": "How did this step go?"
    }
  }
}
```

## Implementation Order

1. **Backend First** (Minimize frontend changes until backend is ready)
   - Add step feedback endpoint
   - Integrate learning service into troubleshooting service
   - Modify LLM prompts for single-step mode
   - Test with API calls

2. **Frontend Second**
   - Add troubleshooting mode detection
   - Implement step feedback UI
   - Handle step responses
   - Test end-to-end workflow

3. **Learning Last**
   - Verify solution tracking works
   - Test prioritization logic
   - Monitor effectiveness over time

## Testing Strategy

1. **Unit Tests**
   - Test step generation with learning data
   - Test feedback processing
   - Test solution prioritization

2. **Integration Tests**
   - Test complete troubleshooting workflow
   - Test learning from multiple sessions
   - Test multi-language support

3. **User Acceptance Testing**
   - Test with real problem scenarios
   - Verify step-by-step flow is intuitive
   - Confirm learning improves over time

## Success Metrics

1. **User Experience**
   - Average steps to resolution decreases over time
   - User satisfaction with step-by-step approach
   - Reduced escalation rate

2. **Learning Effectiveness**
   - Solution success rates improve
   - Common problems resolved faster
   - Historical data influences recommendations

3. **Technical Performance**
   - Response time for step generation < 2s
   - Feedback submission < 500ms
   - Learning updates don't block user flow

## Rollout Plan

1. **Phase 1**: Backend implementation (1-2 days)
2. **Phase 2**: Frontend implementation (1-2 days)
3. **Phase 3**: Testing and refinement (1 day)
4. **Phase 4**: Deployment to development (immediate)
5. **Phase 5**: Monitor and collect data (1 week)
6. **Phase 6**: Deploy to production (after validation)

## Notes

- Existing infrastructure is solid - most work is integration
- Learning service is already sophisticated
- Main challenge is UI/UX for step feedback
- Need to balance automation with user control
- Consider adding "skip step" option for experienced users
