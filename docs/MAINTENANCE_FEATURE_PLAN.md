# Machine Maintenance Feature - Implementation Plan

## Overview

A comprehensive maintenance management system for AutoBoss machines with scheduled services, daily/weekly checklists, and proactive reminders.

---

## Stage 1: Basic Maintenance Recording (Current + Enhancements)

### What We Have Now
- Basic maintenance record creation
- Machine hour recording
- Simple maintenance history

### Stage 1 Enhancements

#### 1.1 Enhanced Maintenance Recording
**Goal**: Link maintenance records with machine hours automatically

**Changes Needed:**
- When recording maintenance, automatically capture current machine hours
- Make machine hours mandatory for maintenance records
- Show last recorded hours as reference

**Database Changes:**
```sql
-- Add to maintenance table (if not exists)
ALTER TABLE maintenance ADD COLUMN machine_hours_at_service DECIMAL(10,2);
ALTER TABLE maintenance ADD COLUMN next_service_due_hours DECIMAL(10,2);
```

**UI Changes:**
- Maintenance form shows current machine hours (read-only)
- User confirms or adjusts hours if needed
- System suggests next service interval based on service type

#### 1.2 Service Type Definitions
**Goal**: Standardize maintenance service types

**Service Types:**
- **Daily Maintenance**: Daily checks (start/end of day)
- **Weekly Maintenance**: Weekly procedures
- **50h Service**: First scheduled service
- **250h Service**: Regular service
- **500h Service**: Major service
- **1000h Service**: Major service
- **Custom/Unscheduled**: Ad-hoc repairs

**Implementation:**
- Add service_type enum to maintenance table
- Add service_interval field (hours until next service)
- Pre-populate common service types

---

## Stage 2: Maintenance Protocols & Checklists

### 2.1 Database Schema

```sql
-- Maintenance Protocol Templates
CREATE TABLE maintenance_protocols (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    protocol_type VARCHAR(50) NOT NULL, -- 'daily', 'weekly', 'scheduled', 'custom'
    service_interval_hours DECIMAL(10,2), -- NULL for daily/weekly
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Protocol Checklist Items
CREATE TABLE protocol_checklist_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    protocol_id UUID REFERENCES maintenance_protocols(id) ON DELETE CASCADE,
    item_order INTEGER NOT NULL,
    item_description TEXT NOT NULL,
    item_category VARCHAR(100), -- 'inspection', 'cleaning', 'lubrication', 'adjustment'
    is_critical BOOLEAN DEFAULT false,
    estimated_duration_minutes INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Maintenance Execution Records
CREATE TABLE maintenance_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    machine_id UUID REFERENCES machines(id) ON DELETE CASCADE,
    protocol_id UUID REFERENCES maintenance_protocols(id),
    performed_by_user_id UUID REFERENCES users(id),
    performed_date TIMESTAMP NOT NULL,
    machine_hours_at_service DECIMAL(10,2) NOT NULL,
    next_service_due_hours DECIMAL(10,2),
    status VARCHAR(50) DEFAULT 'completed', -- 'completed', 'partial', 'skipped'
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Checklist Item Completion
CREATE TABLE maintenance_checklist_completions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id UUID REFERENCES maintenance_executions(id) ON DELETE CASCADE,
    checklist_item_id UUID REFERENCES protocol_checklist_items(id),
    is_completed BOOLEAN DEFAULT false,
    completed_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Maintenance Reminders/Alerts
CREATE TABLE maintenance_reminders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    machine_id UUID REFERENCES machines(id) ON DELETE CASCADE,
    protocol_id UUID REFERENCES maintenance_protocols(id),
    reminder_type VARCHAR(50) NOT NULL, -- 'daily', 'weekly', 'hours_based', 'overdue'
    due_date DATE,
    due_hours DECIMAL(10,2),
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'acknowledged', 'completed', 'dismissed'
    acknowledged_by_user_id UUID REFERENCES users(id),
    acknowledged_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 2.2 Pre-defined Maintenance Protocols

#### Daily Maintenance Protocol
**Start of Day Checklist:**
- [ ] Lift power pack
- [ ] Check for oil leaks in pontoon
- [ ] Inspect belts for wear/tension
- [ ] Check water level
- [ ] Verify all safety features

**End of Day Checklist:**
- [ ] Grease rotary unions
- [ ] Grease propellers
- [ ] Clean filters
- [ ] Check for unusual noises/vibrations
- [ ] Record machine hours

#### Weekly Maintenance Protocol
- [ ] Deep clean machine exterior
- [ ] Inspect all hoses and connections
- [ ] Check chemical levels
- [ ] Test all safety switches
- [ ] Lubricate all moving parts
- [ ] Check tire pressure (if applicable)

#### Scheduled Service Protocols (50h, 250h, 500h, 1000h)
Each with specific checklist items based on manufacturer recommendations.

### 2.3 User Interface Components

#### Dashboard Maintenance Widget
```
┌─────────────────────────────────────┐
│ 🔧 Maintenance Alerts               │
├─────────────────────────────────────┤
│ ⚠️  Machine AB-001                  │
│     Daily checklist pending         │
│     [Complete Now]                  │
│                                     │
│ 🔴 Machine AB-003                   │
│     500h service OVERDUE (523h)     │
│     [Schedule Service]              │
│                                     │
│ 🟡 Machine AB-002                   │
│     250h service due soon (238h)    │
│     [View Details]                  │
└─────────────────────────────────────┘
```

#### Daily Maintenance Quick Entry (Mobile-Optimized)
```
┌─────────────────────────────────────┐
│ Daily Maintenance - Machine AB-001  │
├─────────────────────────────────────┤
│ Start of Day (7:30 AM)              │
│ ☐ Lift power pack                   │
│ ☐ Check oil leaks                   │
│ ☐ Inspect belts                     │
│ ☐ Check water level                 │
│ ☐ Verify safety features            │
│                                     │
│ [Save & Continue]                   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ End of Day (5:00 PM)                │
│ ☐ Grease rotary unions              │
│ ☐ Grease propellers                 │
│ ☐ Clean filters                     │
│ ☐ Check for unusual sounds          │
│                                     │
│ Machine Hours: [___] (required)     │
│ Notes: [________________]           │
│                                     │
│ [Complete Daily Maintenance]        │
└─────────────────────────────────────┘
```

#### Scheduled Service Interface
```
┌─────────────────────────────────────┐
│ 500h Service - Machine AB-001       │
├─────────────────────────────────────┤
│ Current Hours: 498h                 │
│ Service Due: 500h                   │
│ Last Service: 250h (3 months ago)   │
│                                     │
│ Service Checklist (15 items)        │
│ ☐ Change engine oil                 │
│ ☐ Replace oil filter                │
│ ☐ Inspect fuel system               │
│ ☐ Check hydraulic fluid             │
│ ☐ Replace air filter                │
│ ... (show all items)                │
│                                     │
│ Parts Used: [+ Add Part]            │
│ Labor Hours: [___]                  │
│ Performed By: [Current User]        │
│ Notes: [________________]           │
│                                     │
│ [Complete Service]                  │
└─────────────────────────────────────┘
```

### 2.4 Reminder System

#### Login Notifications
When user logs in, show maintenance alerts:
```
┌─────────────────────────────────────┐
│ 🔔 Maintenance Reminders            │
├─────────────────────────────────────┤
│ You have 3 pending maintenance tasks│
│                                     │
│ • Daily checklist for 2 machines    │
│ • 500h service overdue (AB-003)     │
│                                     │
│ [View All] [Dismiss]                │
└─────────────────────────────────────┘
```

#### Proactive Alerts
- **50 hours before service**: "Service due soon" notification
- **At service interval**: "Service due now" alert
- **25 hours overdue**: "Service OVERDUE" warning (red)
- **Daily**: Reminder if daily checklist not completed by 6 PM
- **Weekly**: Reminder on designated day (e.g., every Friday)

### 2.5 Mobile Optimization

#### Progressive Web App (PWA)
**Yes, we can make it mobile-friendly!**

**Implementation Steps:**
1. Add PWA manifest file
2. Implement service worker for offline capability
3. Optimize UI for touch interfaces
4. Add "Add to Home Screen" prompt
5. Enable push notifications for reminders

**Benefits:**
- Works like a native app
- Can be installed on phone home screen
- Works offline (with sync when online)
- Push notifications for reminders
- No app store approval needed

**Mobile-Specific Features:**
- Large touch targets for checkboxes
- Swipe gestures for navigation
- Camera integration for photos (damage/issues)
- GPS location tagging (optional)
- Quick access to most recent machines

---

## Stage 3: Advanced Features (Future)

### 3.1 Predictive Maintenance
- Analyze maintenance history
- Predict failure patterns
- Suggest preventive actions

### 3.2 Parts Integration
- Link maintenance protocols to required parts
- Auto-suggest parts for scheduled services
- Track parts usage per service type
- Generate parts orders based on upcoming services

### 3.3 Technician Management
- Assign services to specific technicians
- Track technician performance
- Certification tracking
- Service time estimation vs actual

### 3.4 Reporting & Analytics
- Maintenance cost per machine
- Service completion rates
- Downtime analysis
- Compliance reporting

---

## Implementation Priority

### Phase 1 (Immediate - 1-2 weeks)
1. ✅ Enhanced maintenance recording with hours
2. ✅ Service type standardization
3. ✅ Basic reminder system on dashboard
4. ✅ Simple daily checklist (start/end of day)

### Phase 2 (Short-term - 2-4 weeks)
1. Full protocol system (database schema)
2. Pre-defined maintenance protocols
3. Checklist completion tracking
4. Login notifications
5. Mobile-optimized interface

### Phase 3 (Medium-term - 1-2 months)
1. PWA implementation
2. Push notifications
3. Offline capability
4. Advanced reminder logic
5. Parts integration

### Phase 4 (Long-term - 3+ months)
1. Predictive maintenance
2. Advanced analytics
3. Technician management
4. Custom protocol builder

---

## Technical Considerations

### Backend (FastAPI)
- New routers: `maintenance_protocols.py`, `maintenance_executions.py`
- CRUD operations for all new tables
- Reminder calculation logic
- Notification system

### Frontend (React)
- New components: `MaintenanceChecklist`, `DailyMaintenanceWidget`, `ServiceScheduler`
- Mobile-responsive design
- PWA configuration
- Push notification handling

### Database (PostgreSQL)
- New tables as defined above
- Indexes on machine_id, due_dates, status fields
- Triggers for automatic reminder creation

### Mobile (PWA)
- Service worker for offline
- Manifest.json for installability
- Push notification API integration
- Responsive CSS for mobile

---

## User Workflow Examples

### Daily Maintenance Workflow
1. User arrives at work, opens app on phone
2. Sees notification: "Daily maintenance pending for 2 machines"
3. Taps notification → Opens daily checklist
4. Completes start-of-day checklist (5 items)
5. At end of day, reminder appears
6. Completes end-of-day checklist
7. Records machine hours (mandatory)
8. Submits → System marks daily maintenance complete

### Scheduled Service Workflow
1. Machine approaches 500h (at 450h)
2. User sees dashboard alert: "500h service due in 50 hours"
3. User clicks "Schedule Service"
4. System shows 500h protocol checklist
5. User performs service, checks off items
6. Records parts used (optional)
7. Records final machine hours
8. Submits → System calculates next service (1000h)
9. System creates reminder for 1000h service

---

## Success Metrics

- **Compliance Rate**: % of daily/weekly maintenance completed on time
- **Service Adherence**: % of scheduled services completed within tolerance
- **Downtime Reduction**: Decrease in unplanned maintenance
- **User Engagement**: Daily active users on mobile
- **Response Time**: Time from reminder to completion

---

## Questions to Consider

1. **Service Tolerance**: How many hours past due before service is "overdue"? (Suggest: 25 hours)
2. **Daily Reminder Time**: What time should daily reminders appear? (Suggest: 6 PM if not completed)
3. **Weekly Schedule**: Which day for weekly maintenance? (Suggest: Configurable per organization)
4. **Photo Attachments**: Should users be able to attach photos to maintenance records?
5. **Signature Requirement**: Should services require digital signature?
6. **Notification Channels**: Email, SMS, or just in-app notifications?

---

**Next Steps**: 
1. Review and approve this plan
2. Prioritize which phase to start with
3. Create detailed technical specifications for Phase 1
4. Begin implementation

