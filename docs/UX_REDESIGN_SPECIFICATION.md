# ABParts UX Redesign Specification

## Executive Summary

Complete redesign of ABParts UI to be action-oriented, mobile-first, and role-appropriate. Focus on daily operational tasks for field workers while maintaining comprehensive management capabilities for admins.

## Design Principles

1. **Action-First**: Primary workflows front and center
2. **Role-Appropriate**: Different UX for users vs admins vs super_admins
3. **Mobile-Optimized**: Touch-friendly, offline-capable, minimal scrolling
4. **Progressive Disclosure**: Show only what's needed, hide complexity
5. **Consistent Patterns**: Reusable components, predictable interactions

## User Personas

### Persona 1: Field Worker (Regular User)
- **Primary Tasks**: Record net cleanings, perform daily maintenance
- **Secondary Tasks**: View assigned machines, check inventory
- **Rarely Needs**: Setup, configuration, reports
- **Device**: Mobile phone, often in field with poor connectivity

### Persona 2: Site Manager (Admin)
- **Primary Tasks**: Monitor operations, manage team, review reports
- **Secondary Tasks**: Setup farms/nets/machines, manage inventory
- **Regularly Needs**: Analytics, team performance, inventory management
- **Device**: Tablet or desktop

### Persona 3: System Administrator (Super Admin)
- **Primary Tasks**: Manage organizations, system configuration
- **Secondary Tasks**: Monitor all operations, generate reports
- **Regularly Needs**: Full system access, analytics, user management
- **Device**: Desktop

## Navigation Structure

### Current (Flat)
```
- Dashboard
- Organizations
- Users
- Parts
- Warehouses
- Machines
- Orders
- Stock Adjustments
- Transactions
- Farm Sites
- Nets
- Net Cleaning Records
- Daily Operations
- Maintenance Protocols
- Maintenance Executions
```

### Proposed (Grouped & Role-Based)

#### For Regular Users
```
🏠 Home (Field Operations Dashboard)
📋 Quick Actions (FAB)
  - 🌊 Record Net Cleaning
  - 🔧 Daily Service
  - 📦 Order Parts
📊 My Activity
  - Today's Work
  - Recent Cleanings
  - Recent Services
📱 More
  - Farms & Nets (view only)
  - Machines (view only)
  - Help
  - Profile
```

#### For Admins
```
🏠 Home (Operations Dashboard)
📋 Operations
  - 🌊 Net Cleaning Records
  - 🔧 Maintenance Executions
  - 📦 Orders
  - 📊 Daily Operations
⚙️ Setup
  - Farms & Nets
  - Machines
  - Users
  - Parts & Inventory
  - Warehouses
📈 Reports
  - Net Cleaning Analytics
  - Maintenance Reports
  - Inventory Reports
  - Team Performance
👤 Profile
```

#### For Super Admins
```
🏠 Home (System Dashboard)
🏢 Organizations
👥 Users (All)
📋 Operations (All Orgs)
⚙️ System Setup
📈 Analytics
👤 Profile
```

## Page Designs

### 1. Field Operations Dashboard (Regular Users)

**Layout**: Mobile-first, single column

```
┌─────────────────────────────────┐
│ 👋 Good Morning, João!          │
│ Today: 3 nets cleaned, 2 services│
├─────────────────────────────────┤
│                                 │
│  ┌───────────────────────────┐ │
│  │   🌊 WASH NETS            │ │
│  │   Record net cleaning     │ │
│  └───────────────────────────┘ │
│                                 │
│  ┌───────────────────────────┐ │
│  │   🔧 DAILY SERVICE        │ │
│  │   Perform maintenance     │ │
│  └───────────────────────────┘ │
│                                 │
│  ┌───────────────────────────┐ │
│  │   📦 ORDER PARTS          │ │
│  │   Request supplies        │ │
│  └───────────────────────────┘ │
│                                 │
├─────────────────────────────────┤
│ 📊 Today's Activity             │
│                                 │
│ ✓ Net A1 - Cleaned 09:30       │
│ ✓ Net A2 - Cleaned 11:15       │
│ ✓ Machine M1 - Service 14:00   │
│                                 │
│ [View All Activity →]           │
└─────────────────────────────────┘
```

**Key Features**:
- Large touch targets (min 48px)
- High contrast colors
- Minimal text, icon-driven
- Offline indicator
- Quick stats at top

### 2. Operations Dashboard (Admins)

**Layout**: Responsive grid

```
┌─────────────────────────────────────────────────────┐
│ Operations Overview - Farm Site Alpha               │
├──────────────┬──────────────┬──────────────────────┤
│ Today        │ This Week    │ Alerts               │
│ 12 Cleanings │ 45 Cleanings │ 3 Low Stock Items    │
│ 8 Services   │ 32 Services  │ 2 Overdue Services   │
├──────────────┴──────────────┴──────────────────────┤
│                                                     │
│ Quick Actions                                       │
│ [🌊 Record Cleaning] [🔧 Service] [📦 Order]       │
│                                                     │
├─────────────────────────────────────────────────────┤
│ Recent Activity                  │ Team Performance │
│                                  │                  │
│ João - Net A1 (09:30)           │ João: 5 tasks    │
│ Maria - Machine M1 (10:15)      │ Maria: 3 tasks   │
│ Pedro - Net B2 (11:00)          │ Pedro: 4 tasks   │
│                                  │                  │
└─────────────────────────────────┴──────────────────┘
```

**Key Features**:
- Metrics at a glance
- Quick actions always visible
- Team activity monitoring
- Alert notifications
- Drill-down capabilities

### 3. Streamlined Net Cleaning Workflow

**Current Flow**: 5+ steps
1. Navigate to Net Cleaning Records
2. Click "Add Record"
3. Select farm from dropdown
4. Select net from dropdown
5. Fill form
6. Submit

**New Flow**: 3 steps

```
Step 1: Select Farm (Visual Cards)
┌─────────────────────────────────┐
│ Select Farm Site                │
├─────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐      │
│  │ [Photo] │  │ [Photo] │      │
│  │ Farm A  │  │ Farm B  │      │
│  │ 12 nets │  │ 8 nets  │      │
│  └─────────┘  └─────────┘      │
└─────────────────────────────────┘

Step 2: Select Net(s) (Multi-select)
┌─────────────────────────────────┐
│ Farm A - Select Nets            │
├─────────────────────────────────┤
│ ☑ Net A1 (Diameter: 50m)       │
│ ☑ Net A2 (Diameter: 50m)       │
│ ☐ Net A3 (Diameter: 60m)       │
│                                 │
│ [Continue with 2 nets →]        │
└─────────────────────────────────┘

Step 3: Record Details (Simplified)
┌─────────────────────────────────┐
│ Cleaning Details                │
├─────────────────────────────────┤
│ Start Time: [Now] [Custom]      │
│ End Time: [Now] [Custom]        │
│                                 │
│ Operator: [Auto-filled]         │
│                                 │
│ Notes (optional):               │
│ [Text area]                     │
│                                 │
│ [📸 Add Photos]                 │
│                                 │
│ [✓ Complete Cleaning]           │
└─────────────────────────────────┘
```

## Component Library

### 1. Floating Action Button (FAB)

```javascript
// Position: Bottom-right, always visible
// Behavior: Tap to expand, shows 3 primary actions
// Mobile: Bottom-center for thumb reach
```

### 2. Action Card

```javascript
// Large touch target (min 120px height)
// Icon + Title + Subtitle
// Hover/Active states
// Loading state
// Disabled state
```

### 3. Quick Stats Widget

```javascript
// Compact metrics display
// Icon + Number + Label
// Color-coded (green=good, yellow=warning, red=alert)
// Tap to drill down
```

### 4. Activity Feed

```javascript
// Chronological list
// Avatar + Action + Time
// Pull to refresh
// Infinite scroll
// Empty state
```

### 5. Bottom Navigation (Mobile)

```javascript
// 4-5 items max
// Icon + Label
// Active indicator
// Badge support for notifications
```

## Responsive Breakpoints

```css
/* Mobile First */
mobile: 0-640px (default)
tablet: 641px-1024px
desktop: 1025px+

/* Touch targets */
min-height: 48px
min-width: 48px

/* Font sizes */
mobile: base 16px
tablet: base 16px
desktop: base 14px
```

## Color System

### Primary Actions
- Net Cleaning: Cyan/Teal (#14B8A6)
- Maintenance: Orange (#F97316)
- Orders: Blue (#3B82F6)

### Status Colors
- Success: Green (#10B981)
- Warning: Yellow (#F59E0B)
- Error: Red (#EF4444)
- Info: Blue (#3B82F6)

### Neutral
- Background: Gray-50 (#F9FAFB)
- Surface: White (#FFFFFF)
- Border: Gray-200 (#E5E7EB)
- Text Primary: Gray-900 (#111827)
- Text Secondary: Gray-600 (#4B5563)

## Accessibility

- WCAG 2.1 AA compliance
- Minimum contrast ratio 4.5:1
- Keyboard navigation
- Screen reader support
- Focus indicators
- Touch target size (48px min)

## Performance Targets

- First Contentful Paint: < 1.5s
- Time to Interactive: < 3s
- Lighthouse Score: > 90
- Bundle size: < 500KB (gzipped)

## Offline Capabilities

### Phase 1 (MVP)
- Cache static assets
- Show offline indicator
- Queue failed requests

### Phase 2 (Enhanced)
- IndexedDB for data storage
- Background sync
- Conflict resolution
- Offline-first architecture

## Implementation Phases

### Phase 1: Foundation (Days 1-2)
- [ ] Create FieldOperationsDashboard component
- [ ] Implement role-based routing
- [ ] Add FloatingActionButton component
- [ ] Reorganize navigation structure
- [ ] Add bottom navigation for mobile

### Phase 2: Streamlined Workflows (Days 3-4)
- [ ] Redesign net cleaning workflow
- [ ] Simplify maintenance execution
- [ ] Improve order creation flow
- [ ] Add visual farm/net selection

### Phase 3: Enhanced Components (Days 5-6)
- [ ] Activity feed component
- [ ] Quick stats widgets
- [ ] Improved mobile forms
- [ ] Photo capture optimization
- [ ] Pull-to-refresh

### Phase 4: Advanced Features (Days 7-8)
- [ ] Offline mode (basic)
- [ ] Service worker setup
- [ ] Background sync
- [ ] Push notifications
- [ ] PWA manifest

### Phase 5: Polish & Testing (Days 9-10)
- [ ] Performance optimization
- [ ] Accessibility audit
- [ ] Cross-browser testing
- [ ] User acceptance testing
- [ ] Documentation

## Success Metrics

- Reduce clicks to complete net cleaning: 5+ → 3
- Increase mobile usage: Track adoption
- Reduce time to complete tasks: Measure before/after
- User satisfaction: Survey feedback
- Error rate: Monitor form submissions

## Migration Strategy

1. **Parallel Development**: New UI alongside existing
2. **Feature Flag**: Toggle between old/new UI
3. **Gradual Rollout**: Start with pilot users
4. **Feedback Loop**: Iterate based on user input
5. **Full Migration**: After validation period

## Next Steps

1. Review and approve this specification
2. Create detailed wireframes/mockups
3. Begin Phase 1 implementation
4. Set up user testing framework
5. Plan rollout schedule
