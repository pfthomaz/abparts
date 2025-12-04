# Maintenance Feature - Phase 1 Implementation Guide

## Database Migration

### Running the Migration

```bash
# Development
docker compose exec api alembic upgrade head

# Production
docker compose exec api alembic upgrade head
```

### Verification
```bash
# Check migration status
docker compose exec api alembic current

# Verify tables created
docker compose exec db psql -U abparts_user -d abparts_prod -c "\dt maintenance*"
docker compose exec db psql -U abparts_user -d abparts_prod -c "\dt protocol*"
```

---

## Super Admin Interface: Service Protocol Management

### Navigation Structure

```
Super Admin Menu
├── Organizations
├── Users  
├── Parts
├── Warehouses
└── Maintenance Protocols ⭐ NEW
    ├── Service Protocols List
    ├── Create Protocol
    ├── Edit Protocol
    └── Protocol Checklist Items
```

### Service Protocol Management Interface

#### 1. Protocol List View

```
┌────────────────────────────────────────────────────────────────┐
│ Maintenance Service Protocols                    [+ New Protocol]│
├────────────────────────────────────────────────────────────────┤
│ Filter: [All Models ▼] [All Types ▼]  Search: [________] 🔍    │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌─────────────────────────────────────────────────────────┐   │
│ │ 50h Service - V3.1B                          [Edit] [❌] │   │
│ │ Type: Scheduled | Interval: 50 hours | 12 checklist items│   │
│ │ Status: ✅ Active                                         │   │
│ └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────┐   │
│ │ 250h Service - V3.1B                         [Edit] [❌] │   │
│ │ Type: Scheduled | Interval: 250 hours | 18 checklist items│  │
│ │ Status: ✅ Active                                         │   │
│ └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────┐   │
│ │ Daily Maintenance - All Models               [Edit] [❌] │   │
│ │ Type: Daily | 10 checklist items                         │   │
│ │ Status: ✅ Active                                         │   │
│ └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────┐   │
│ │ 500h Service - V4.0                          [Edit] [❌] │   │
│ │ Type: Scheduled | Interval: 500 hours | 25 checklist items│  │
│ │ Status: ✅ Active                                         │   │
│ └─────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────┘
```

#### 2. Create/Edit Protocol Form

```
┌────────────────────────────────────────────────────────────────┐
│ Create Maintenance Protocol                                     │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Protocol Name: *                                                │
│ [50h Service_____________________________]                      │
│                                                                 │
│ Protocol Type: *                                                │
│ ○ Daily Maintenance                                             │
│ ○ Weekly Maintenance                                            │
│ ● Scheduled Service (hours-based)                              │
│                                                                 │
│ Service Interval (hours): *                                     │
│ [50____] hours                                                  │
│                                                                 │
│ Machine Model: *                                                │
│ ○ All Models                                                    │
│ ● V3.1B                                                         │
│ ○ V4.0                                                          │
│                                                                 │
│ Description:                                                    │
│ [First scheduled service for V3.1B machines_____________]       │
│ [_____________________________________________________]         │
│                                                                 │
│ Status:                                                         │
│ ☑ Active (visible to users)                                    │
│                                                                 │
│ Display Order: [1___]                                           │
│                                                                 │
│ [Cancel]                                    [Save & Add Items]  │
└────────────────────────────────────────────────────────────────┘
```

#### 3. Checklist Items Management

```
┌────────────────────────────────────────────────────────────────┐
│ 50h Service - V3.1B: Checklist Items              [+ Add Item]  │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ┌─────────────────────────────────────────────────────────┐   │
│ │ 1. ☰ Change engine oil                    [Edit] [Delete]│   │
│ │    Type: Part Replacement | Critical: ✅                 │   │
│ │    Part: Engine Oil 5W-30 (2L) | Qty: 2.0 liters        │   │
│ │    Est. Time: 15 min                                     │   │
│ └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────┐   │
│ │ 2. ☰ Replace oil filter                   [Edit] [Delete]│   │
│ │    Type: Part Replacement | Critical: ✅                 │   │
│ │    Part: Oil Filter OF-123 | Qty: 1 piece               │   │
│ │    Est. Time: 10 min                                     │   │
│ └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────┐   │
│ │ 3. ☰ Inspect fuel system                  [Edit] [Delete]│   │
│ │    Type: Check/Inspection | Critical: ⬜                 │   │
│ │    Category: Inspection                                  │   │
│ │    Est. Time: 5 min                                      │   │
│ └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────┐   │
│ │ 4. ☰ Grease rotary unions                 [Edit] [Delete]│   │
│ │    Type: Service/Lubrication | Critical: ✅              │   │
│ │    Part: Marine Grease | Qty: 0.1 kg                    │   │
│ │    Category: Lubrication                                 │   │
│ │    Est. Time: 10 min                                     │   │
│ └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│ [Drag items to reorder]                                         │
│                                                                 │
│ Total Items: 4 | Est. Total Time: 40 minutes                   │
│                                                                 │
│ [Back to Protocols]                          [Save Changes]     │
└────────────────────────────────────────────────────────────────┘
```

#### 4. Add/Edit Checklist Item Modal

```
┌────────────────────────────────────────────────────────────────┐
│ Add Checklist Item                                         [×]  │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Item Description: *                                             │
│ [Change engine oil_________________________________]            │
│                                                                 │
│ Item Type: *                                                    │
│ ○ Check/Inspection                                              │
│ ○ Service/Maintenance                                           │
│ ● Part Replacement                                              │
│                                                                 │
│ Category:                                                       │
│ [Lubrication ▼]                                                 │
│ Options: Inspection, Cleaning, Lubrication, Adjustment,        │
│          Replacement, Electrical, Hydraulic                     │
│                                                                 │
│ ☑ Critical Item (must be completed)                            │
│                                                                 │
│ ┌─────────────────────────────────────────────────────────┐   │
│ │ Part Selection (for replacements/services)              │   │
│ │                                                         │   │
│ │ Select Part: *                                          │   │
│ │ [Search parts..._______________] 🔍                     │   │
│ │                                                         │   │
│ │ Selected: Engine Oil 5W-30 (2L)                        │   │
│ │ Current Stock: 45.5 liters                             │   │
│ │                                                         │   │
│ │ Expected Quantity: *                                    │   │
│ │ [2.0___] liters                                        │   │
│ └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│ Estimated Duration:                                             │
│ [15___] minutes                                                 │
│                                                                 │
│ Notes/Instructions:                                             │
│ [Drain old oil completely before adding new oil_______]         │
│ [_____________________________________________________]         │
│                                                                 │
│ [Cancel]                                          [Add Item]    │
└────────────────────────────────────────────────────────────────┘
```

---

## Pre-defined Service Protocols

### Daily Maintenance Protocol (All Models)

**Start of Day:**
1. ✓ Lift power pack (Check)
2. ✓ Check for oil leaks in pontoon (Check - Critical)
3. ✓ Inspect belts for wear/tension (Check - Critical)
4. ✓ Check water level (Check)
5. ✓ Verify all safety features (Check - Critical)

**End of Day:**
6. ✓ Grease rotary unions (Service - Part: Marine Grease, 0.05kg)
7. ✓ Grease propellers (Service - Part: Marine Grease, 0.05kg)
8. ✓ Clean filters (Service)
9. ✓ Check for unusual noises/vibrations (Check)
10. ✓ Record machine hours (Check - Critical)

### Weekly Maintenance Protocol (All Models)

1. ✓ Deep clean machine exterior (Service)
2. ✓ Inspect all hoses and connections (Check)
3. ✓ Check chemical levels (Check)
4. ✓ Test all safety switches (Check - Critical)
5. ✓ Lubricate all moving parts (Service - Part: Marine Grease, 0.2kg)
6. ✓ Check tire pressure if applicable (Check)
7. ✓ Inspect electrical connections (Check)

### 50h Service - V3.1B

1. ✓ Change engine oil (Replacement - Part: Engine Oil 5W-30, 2L - Critical)
2. ✓ Replace oil filter (Replacement - Part: Oil Filter, 1pc - Critical)
3. ✓ Inspect fuel system (Check)
4. ✓ Check hydraulic fluid level (Check)
5. ✓ Grease all fittings (Service - Part: Marine Grease, 0.3kg)
6. ✓ Inspect belts and adjust tension (Service)
7. ✓ Check battery connections (Check)
8. ✓ Inspect propellers for damage (Check)
9. ✓ Test all safety systems (Check - Critical)
10. ✓ Clean/inspect air filter (Service)
11. ✓ Check coolant level (Check)
12. ✓ Record all findings (Check - Critical)

### 250h Service - V3.1B

(Includes all 50h items plus:)
13. ✓ Replace air filter (Replacement - Part: Air Filter, 1pc)
14. ✓ Change hydraulic fluid (Replacement - Part: Hydraulic Oil, 3L)
15. ✓ Replace hydraulic filter (Replacement - Part: Hydraulic Filter, 1pc)
16. ✓ Inspect and clean fuel injectors (Service)
17. ✓ Check valve clearances (Service)
18. ✓ Inspect cooling system (Check)

### 500h Service - V3.1B

(Includes all 250h items plus:)
19. ✓ Replace fuel filter (Replacement - Part: Fuel Filter, 1pc - Critical)
20. ✓ Inspect/replace spark plugs (Replacement - Part: Spark Plug, 4pc)
21. ✓ Check engine compression (Service)
22. ✓ Inspect exhaust system (Check)
23. ✓ Replace coolant (Replacement - Part: Coolant, 5L)
24. ✓ Inspect/adjust brakes (Service)
25. ✓ Full electrical system check (Check)

---

## Backend Implementation

### File Structure
```
backend/app/
├── models.py (add new models)
├── schemas.py (add new schemas)
├── routers/
│   └── maintenance_protocols.py (NEW)
├── crud/
│   └── maintenance_protocols.py (NEW)
```

### Key Features

1. **Protocol CRUD Operations**
   - Create, Read, Update, Delete protocols
   - Duplicate protocol (for creating variants)
   - Activate/Deactivate protocols

2. **Checklist Item Management**
   - Add/Remove/Reorder items
   - Link parts to items
   - Set criticality flags

3. **Model-Specific Protocols**
   - Filter protocols by machine model
   - Support "All Models" option
   - Validate model compatibility

4. **Part Integration**
   - Search and link parts to checklist items
   - Track expected quantities
   - Auto-suggest parts based on service type

---

## Frontend Implementation

### New Components

1. **MaintenanceProtocolsList** - List all protocols
2. **ProtocolForm** - Create/Edit protocol
3. **ChecklistItemManager** - Manage checklist items
4. **ChecklistItemForm** - Add/Edit individual items
5. **PartSelector** - Search and select parts for items

### Navigation Addition

Add to super admin menu:
```javascript
{
  path: '/maintenance-protocols',
  label: 'Maintenance Protocols',
  icon: '🔧',
  permission: 'super_admin'
}
```

---

## User-Facing Features (Phase 1)

### For Regular Users

1. **View Available Protocols**
   - See protocols applicable to their machines
   - View checklist items for each protocol
   - See estimated time and parts needed

2. **Execute Maintenance**
   - Select protocol to execute
   - Check off items as completed
   - Record parts used (auto-populated from protocol)
   - Record machine hours (mandatory)
   - Add notes

3. **Maintenance History**
   - View past maintenance executions
   - See what was completed
   - Track parts usage per service

---

## Testing Checklist

### Migration Testing
- [ ] Migration runs successfully in development
- [ ] Migration runs successfully in production
- [ ] All tables created with correct structure
- [ ] Indexes created properly
- [ ] Foreign keys working correctly
- [ ] Rollback works if needed

### Super Admin Interface Testing
- [ ] Can create new protocol
- [ ] Can edit existing protocol
- [ ] Can delete protocol (with confirmation)
- [ ] Can add checklist items
- [ ] Can reorder checklist items
- [ ] Can link parts to items
- [ ] Can set item criticality
- [ ] Can filter by model
- [ ] Can activate/deactivate protocols

### User Interface Testing
- [ ] Users can view protocols for their machines
- [ ] Users can execute maintenance
- [ ] Checklist items display correctly
- [ ] Parts auto-populate when selected
- [ ] Machine hours recorded correctly
- [ ] Part usage tracked correctly

---

## Deployment Steps

### 1. Backup Database
```bash
docker compose exec db pg_dump -U abparts_user abparts_prod > backup_before_maintenance_$(date +%Y%m%d).sql
```

### 2. Deploy Code
```bash
git pull origin main
docker compose build api
```

### 3. Run Migration
```bash
docker compose exec api alembic upgrade head
```

### 4. Verify Migration
```bash
docker compose exec api alembic current
docker compose exec db psql -U abparts_user -d abparts_prod -c "SELECT COUNT(*) FROM maintenance_protocols;"
```

### 5. Seed Initial Data (Optional)
```bash
docker compose exec api python -m app.scripts.seed_maintenance_protocols
```

### 6. Test Super Admin Interface
- Login as super admin
- Navigate to Maintenance Protocols
- Create a test protocol
- Verify it appears in the list

---

## Next Steps After Phase 1

1. **User Execution Interface** - Allow users to execute protocols
2. **Reminder System** - Automated reminders based on hours
3. **Mobile Optimization** - PWA for mobile access
4. **Dashboard Widgets** - Show pending maintenance
5. **Reporting** - Maintenance compliance reports

