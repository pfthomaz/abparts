# Order Calendar View - Feature Specification

## Overview
Add a calendar/timeline view to the Orders page showing orders as horizontal bars spanning from order date to delivery date.

## User Interface

### Tab Structure
```
┌─────────────────────────────────────────────────────────┐
│  Orders                                                  │
│  ┌──────────┬──────────────┐                           │
│  │ List View│ Calendar View│                           │
│  └──────────┴──────────────┘                           │
│                                                          │
│  [Current list view OR Calendar view based on tab]      │
└─────────────────────────────────────────────────────────┘
```

### Calendar View Layout

**Time Range:** 30 days (15 days before today, today, 14 days after today)

```
┌────────────────────────────────────────────────────────────────┐
│  Calendar View - Orders Timeline                               │
│  ◄ Previous 30 Days    [Today: Nov 24, 2024]    Next 30 Days ►│
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Nov 10  Nov 15  Nov 20  Nov 24  Nov 30  Dec 5   Dec 10       │
│    │       │       │       │       │       │       │           │
│    ├───────────────────────────────┤                           │ Order #1234
│              ├───────────────────────────────────┤             │ Order #1235
│                      ├───────────────┤                         │ Order #1236
│                              ├───────────────────────────►      │ Order #1237 (In Progress)
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### Order Bar Details

**Bar Colors by Status:**
- 🟦 **Pending** - Blue
- 🟨 **Shipped** - Yellow/Orange
- 🟩 **Delivered/Received** - Green
- 🟥 **Cancelled** - Red (grayed out)

**Bar Span:**
- **Start:** Order date
- **End:** 
  - If delivered: Actual delivery date
  - If shipped: Expected delivery date (dashed line)
  - If pending: Expected delivery date (dashed line)
  - If no expected date: Extends to end of visible calendar

**Bar Content:**
- Order number (e.g., "#1234")
- Customer organization name (if super admin)
- Hover tooltip shows full details

### Interactive Features

1. **Click on bar** → Opens order details modal
2. **Hover on bar** → Shows tooltip with:
   - Order ID
   - Customer organization
   - Status
   - Order date
   - Expected/Actual delivery date
   - Number of items
3. **Navigation buttons** → Move calendar forward/backward by 30 days
4. **Today button** → Jump back to current date
5. **Filter controls** → Same as list view (status, organization, etc.)

## Technical Implementation

### Component Structure

```
Orders.js (existing)
├── Tab Navigation (new)
│   ├── List View Tab
│   └── Calendar View Tab
├── OrderListView (existing content)
└── OrderCalendarView (new component)
    ├── CalendarHeader (date range, navigation)
    ├── CalendarGrid (date axis)
    └── OrderTimeline (order bars)
```

### New Components

#### 1. OrderCalendarView.js
Main calendar view component

```javascript
const OrderCalendarView = ({ orders, onOrderClick }) => {
  const [centerDate, setCenterDate] = useState(new Date());
  const dateRange = useMemo(() => calculateDateRange(centerDate), [centerDate]);
  
  return (
    <div>
      <CalendarHeader 
        centerDate={centerDate}
        onNavigate={setCenterDate}
      />
      <CalendarGrid dateRange={dateRange} />
      <OrderTimeline 
        orders={orders}
        dateRange={dateRange}
        onOrderClick={onOrderClick}
      />
    </div>
  );
};
```

#### 2. CalendarHeader.js
Navigation and date display

```javascript
const CalendarHeader = ({ centerDate, onNavigate }) => {
  const goBack = () => onNavigate(subDays(centerDate, 30));
  const goForward = () => onNavigate(addDays(centerDate, 30));
  const goToday = () => onNavigate(new Date());
  
  return (
    <div className="flex justify-between items-center mb-4">
      <button onClick={goBack}>◄ Previous 30 Days</button>
      <div>
        <button onClick={goToday}>Today: {format(new Date(), 'MMM dd, yyyy')}</button>
      </div>
      <button onClick={goForward}>Next 30 Days ►</button>
    </div>
  );
};
```

#### 3. CalendarGrid.js
Date axis with day markers

```javascript
const CalendarGrid = ({ dateRange }) => {
  const days = eachDayOfInterval(dateRange);
  
  return (
    <div className="relative h-12 border-b-2 border-gray-300">
      {days.map((day, index) => (
        <div 
          key={index}
          className="absolute text-xs"
          style={{ left: `${(index / days.length) * 100}%` }}
        >
          {format(day, 'MMM dd')}
        </div>
      ))}
    </div>
  );
};
```

#### 4. OrderTimeline.js
Renders order bars

```javascript
const OrderTimeline = ({ orders, dateRange, onOrderClick }) => {
  return (
    <div className="relative" style={{ minHeight: '400px' }}>
      {orders.map((order, index) => (
        <OrderBar
          key={order.id}
          order={order}
          dateRange={dateRange}
          yPosition={index * 40}
          onClick={() => onOrderClick(order)}
        />
      ))}
    </div>
  );
};
```

#### 5. OrderBar.js
Individual order bar

```javascript
const OrderBar = ({ order, dateRange, yPosition, onClick }) => {
  const { left, width } = calculateBarPosition(order, dateRange);
  const color = getStatusColor(order.status);
  
  return (
    <div
      className={`absolute h-8 rounded cursor-pointer ${color}`}
      style={{
        left: `${left}%`,
        width: `${width}%`,
        top: `${yPosition}px`
      }}
      onClick={onClick}
      title={`Order #${order.id} - ${order.status}`}
    >
      <span className="text-xs px-2">#{order.id.slice(0, 8)}</span>
    </div>
  );
};
```

### Helper Functions

```javascript
// Calculate date range (15 days before, today, 14 days after)
const calculateDateRange = (centerDate) => ({
  start: subDays(centerDate, 15),
  end: addDays(centerDate, 14)
});

// Calculate bar position and width
const calculateBarPosition = (order, dateRange) => {
  const totalDays = differenceInDays(dateRange.end, dateRange.start);
  const startOffset = differenceInDays(order.order_date, dateRange.start);
  const endDate = order.actual_delivery_date || order.expected_delivery_date || dateRange.end;
  const endOffset = differenceInDays(endDate, dateRange.start);
  
  return {
    left: (startOffset / totalDays) * 100,
    width: ((endOffset - startOffset) / totalDays) * 100
  };
};

// Get color based on status
const getStatusColor = (status) => {
  switch (status) {
    case 'Pending': return 'bg-blue-500';
    case 'Shipped': return 'bg-yellow-500';
    case 'Delivered':
    case 'Received': return 'bg-green-500';
    case 'Cancelled': return 'bg-red-300 opacity-50';
    default: return 'bg-gray-500';
  }
};
```

### Dependencies

```json
{
  "date-fns": "^2.30.0"  // For date manipulation
}
```

## Data Requirements

### Existing Data (Already Available)
- ✅ order_date
- ✅ expected_delivery_date
- ✅ actual_delivery_date
- ✅ status
- ✅ customer_organization_name
- ✅ order ID

### No Backend Changes Needed
All required data is already in the API response.

## User Stories

### Story 1: View Order Timeline
**As a** warehouse manager  
**I want to** see all orders on a timeline  
**So that** I can visualize order flow and identify bottlenecks

### Story 2: Identify Overdue Orders
**As a** operations manager  
**I want to** see which orders are past their expected delivery date  
**So that** I can follow up with suppliers/customers

### Story 3: Plan Capacity
**As a** logistics coordinator  
**I want to** see upcoming deliveries  
**So that** I can plan warehouse capacity and staffing

## Implementation Phases

### Phase 1: Basic Calendar View (2-3 hours)
- [ ] Add tab navigation to Orders page
- [ ] Create OrderCalendarView component
- [ ] Implement date range calculation
- [ ] Render basic order bars
- [ ] Add navigation (prev/next/today)

### Phase 2: Visual Enhancements (1-2 hours)
- [ ] Add status colors
- [ ] Implement hover tooltips
- [ ] Add date axis with labels
- [ ] Style improvements

### Phase 3: Interactivity (1 hour)
- [ ] Click to view order details
- [ ] Filter integration
- [ ] Responsive design

### Total Estimated Time: 4-6 hours

## Future Enhancements

- **Zoom levels**: Week view, Month view, Quarter view
- **Drag & drop**: Reschedule orders by dragging bars
- **Milestones**: Show key dates (ordered, shipped, delivered) as markers
- **Grouping**: Group by customer organization
- **Export**: Export calendar view as image/PDF
- **Notifications**: Highlight overdue orders in red
- **Multi-select**: Select multiple orders for batch operations

## Design Mockup

```
┌──────────────────────────────────────────────────────────────────┐
│  Orders                                                           │
│  ┌──────────┬──────────────┐  [+ Add Order] [Filters ▼]        │
│  │ List View│ Calendar View│                                     │
│  └──────────┴──────────────┘                                     │
│                                                                   │
│  ◄ Previous    Today: Nov 24, 2024    Next ►                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Nov 10    Nov 15    Nov 20    Nov 24    Nov 30    Dec 5   │ │
│  │   │         │         │         │         │         │      │ │
│  │   ├─────────────────────────────┤                          │ │ #1234 (Delivered)
│  │             ├─────────────────────────────────┤            │ │ #1235 (Shipped)
│  │                     ├─────────────┤                        │ │ #1236 (Delivered)
│  │                             ├───────────────────────►      │ │ #1237 (Pending)
│  │                                                            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  Legend: 🟦 Pending  🟨 Shipped  🟩 Delivered  🟥 Cancelled     │
└──────────────────────────────────────────────────────────────────┘
```

## Benefits

1. **Visual clarity** - See order timelines at a glance
2. **Better planning** - Identify busy periods and gaps
3. **Quick identification** - Spot overdue or delayed orders
4. **Professional appearance** - Modern, intuitive interface
5. **Complementary view** - Works alongside existing list view

## Notes

- Calendar view is read-only (no editing in calendar)
- Clicking an order opens the same detail modal as list view
- Filters apply to both list and calendar views
- Calendar view is responsive (may need horizontal scroll on mobile)
- Orders without dates are shown at the bottom with a note

---

This feature will significantly improve order visibility and management!
