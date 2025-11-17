# Machine Hours Reminder System - Implementation Plan

## 🎯 Feature Requirements
- Users record machine hours regularly (PLC display values)
- Automated reminders on specific days (1,2,3 and 15,16,17 of each month)
- Modal popup on login if machines haven't been updated in 2 weeks
- User can dismiss modal without entering data

## ✅ Already Implemented
1. **MachineHours model** - Complete with user tracking and validation
2. **API endpoints** - POST/GET machine hours for individual machines
3. **CRUD operations** - Create and retrieve machine hours records

## 🔧 Backend Components to Add

### 1. New API Endpoints
```python
# In backend/app/routers/machines.py or new file
@router.get("/reminder-check", response_model=MachineHoursReminderResponse)
async def check_machine_hours_reminders(current_user: TokenData = Depends(get_current_user))
    """Check if user should see machine hours reminder modal"""

@router.post("/bulk-hours", response_model=List[MachineHoursResponse])
async def record_bulk_machine_hours(hours_data: List[BulkMachineHoursCreate])
    """Record hours for multiple machines at once from reminder modal"""
```

### 2. New Schemas
```python
# In backend/app/schemas.py
class MachineHoursReminderCheck(BaseModel):
    machine_id: uuid.UUID
    machine_name: str
    last_recorded_date: Optional[datetime]
    days_since_last_record: int

class MachineHoursReminderResponse(BaseModel):
    should_show_reminder: bool
    reminder_machines: List[MachineHoursReminderCheck]
    reminder_reason: str  # "monthly_check" or "overdue_machines"

class BulkMachineHoursCreate(BaseModel):
    machine_id: uuid.UUID
    hours_value: Decimal
    notes: Optional[str] = None
```

### 3. Business Logic Functions
```python
# In backend/app/crud/machines.py
def should_show_reminder_today() -> bool:
    """Check if today is a reminder day (1,2,3 or 15,16,17)"""

def get_machines_needing_hours_update(db: Session, organization_id: uuid.UUID) -> List[Machine]:
    """Get machines that haven't had hours recorded in 2+ weeks"""

def get_last_hours_record_date(db: Session, machine_id: uuid.UUID) -> Optional[datetime]:
    """Get the date of the last hours record for a machine"""
```

## 🎨 Frontend Components to Add

### 1. Machine Hours Reminder Modal
```jsx
// In frontend/src/components/MachineHoursReminderModal.js
- Modal that shows on login
- List of machines needing updates
- Input fields for each machine
- "Skip" and "Save" buttons
- Validation for positive numbers
```

### 2. Login Integration
```jsx
// In frontend/src/AuthContext.js or App.js
- Check reminder API after successful login
- Show modal if needed
- Handle modal dismiss/save actions
```

### 3. Machine Hours Management Page
```jsx
// In frontend/src/components/MachineHoursManagement.js
- View all machines and their latest hours
- Quick update interface
- History view per machine
```

## 📅 Reminder Logic Details

### Reminder Days
- Days 1, 2, 3 of each month
- Days 15, 16, 17 of each month
- Only show once per day per user

### Overdue Detection
- Check machines in user's organization
- Find machines with no hours recorded in last 14 days
- OR machines with no hours records at all

### Modal Behavior
- Show on login only on reminder days
- List all overdue machines
- Allow partial updates (some machines, not all)
- Remember dismissed state for the day

## 🗄️ Database Considerations

### Existing Tables (Already Good)
- `machine_hours` - Complete with user_id, machine_id, recorded_date
- `machines` - Has organization_id for filtering
- `users` - Has organization_id for scoping

### Optional Enhancement
```sql
-- Track reminder dismissals to avoid showing multiple times per day
CREATE TABLE machine_hours_reminder_dismissals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    dismissed_date DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, dismissed_date)
);
```

## 🚀 Implementation Priority

### Phase 1 (Core Functionality)
1. Backend reminder check API
2. Frontend reminder modal
3. Login integration

### Phase 2 (Enhancements)
1. Bulk hours recording
2. Reminder dismissal tracking
3. Machine hours management page

### Phase 3 (Advanced Features)
1. Email reminders
2. Manager notifications
3. Hours recording analytics