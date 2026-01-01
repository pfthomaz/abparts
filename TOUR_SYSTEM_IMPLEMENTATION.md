# Tour System Implementation Guide

## Overview
Interactive step-by-step guided tours to help users learn ABParts workflows using React Joyride.

## Installation

```bash
cd frontend
npm install react-joyride
```

## Integration Steps

### 1. Update App.js
Add the TourProvider wrapper:

```javascript
import { TourProvider } from './contexts/TourContext';
import GuidedTour from './components/GuidedTour';

function App() {
  return (
    <TourProvider>
      <LocalizationProvider>
        <AuthProvider>
          {/* existing app content */}
          <GuidedTour />
        </AuthProvider>
      </LocalizationProvider>
    </TourProvider>
  );
}
```

### 2. Update Layout.js
Add the TourButton component:

```javascript
import TourButton from './TourButton';

const Layout = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* existing layout content */}
      <TourButton />
    </div>
  );
};
```

### 3. Add Data Tour Attributes

Add `data-tour` attributes to key UI elements:

**Navigation (Layout.js):**
```javascript
<Link to="/orders" data-tour="nav-orders">Orders</Link>
<Link to="/machines" data-tour="nav-machines">Machines</Link>
<Link to="/daily-operations" data-tour="nav-daily-ops">Daily Operations</Link>
<Link to="/maintenance" data-tour="nav-maintenance">Maintenance</Link>
```

**Orders Page:**
```javascript
<button data-tour="new-order-button">New Order</button>
<select data-tour="order-type-select">...</select>
<input data-tour="part-search" placeholder="Search parts..." />
<input data-tour="quantity-input" type="number" />
<div data-tour="delivery-details">...</div>
<button data-tour="submit-order">Submit Order</button>
<div data-tour="order-status">...</div>
```

**Machines Page:**
```javascript
<select data-tour="machine-select">...</select>
<button data-tour="record-usage-button">Record Usage</button>
<input data-tour="part-usage-search" />
<input data-tour="usage-quantity" type="number" />
<select data-tour="maintenance-context">...</select>
<button data-tour="submit-usage">Submit</button>
```

**Daily Operations:**
```javascript
<input data-tour="date-selector" type="date" />
<select data-tour="machine-selector">...</select>
<div data-tour="operational-metrics">...</div>
<div data-tour="daily-checklist">...</div>
<textarea data-tour="issues-notes">...</textarea>
<button data-tour="submit-daily-report">Submit Report</button>
```

**Maintenance Executions:**
```javascript
<select data-tour="protocol-selector">...</select>
<div data-tour="machine-technician">...</div>
<div data-tour="checklist-items">...</div>
<div data-tour="parts-used">...</div>
<div data-tour="photos-notes">...</div>
<button data-tour="complete-maintenance">Complete</button>
```

## Features

### ✅ Implemented
- Tour context and state management
- Floating help button with tour menu
- 4 predefined workflows
- Full localization support (6 languages)
- Responsive design with Tailwind CSS
- Progress indicators and navigation controls

### 🔄 Next Steps
1. Install React Joyride dependency
2. Add TourProvider to App.js
3. Add TourButton to Layout.js
4. Add data-tour attributes to UI elements
5. Test tours in development
6. Customize styling if needed

## Tour Workflows

1. **Parts Ordering** - Complete order lifecycle
2. **Parts Usage** - Recording consumption
3. **Daily Operations** - Daily reporting
4. **Scheduled Maintenance** - Protocol execution

## Customization

### Styling
Tours use Tailwind-compatible styling. Modify `joyrideStyles` in `GuidedTour.js` to match your brand.

### Adding New Tours
1. Add steps to `tourSteps.js`
2. Add tour definition to `TourButton.js`
3. Add translation keys to locale files
4. Add data-tour attributes to target elements

### Analytics
Consider adding tour completion tracking:

```javascript
const handleJoyrideCallback = (data) => {
  const { status, type, index } = data;
  
  if (status === STATUS.FINISHED) {
    // Track tour completion
    analytics.track('tour_completed', {
      tourId: activeTour,
      stepsCompleted: index + 1
    });
  }
};
```

## Benefits

- **Reduced Support Tickets** - Self-service learning
- **Faster Onboarding** - Interactive guidance
- **Better Feature Adoption** - Discover functionality
- **Improved UX** - Contextual help
- **Multilingual Support** - All 6 languages supported

## Testing

Test each tour workflow:
1. Click help button
2. Select tour from menu
3. Follow all steps
4. Verify proper navigation
5. Test in different languages
6. Test on mobile devices

The tour system is now ready for integration!