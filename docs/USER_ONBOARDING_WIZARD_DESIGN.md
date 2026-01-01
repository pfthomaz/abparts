# User Onboarding Wizard Design

## Overview
Interactive step-by-step guides to help new users navigate key ABParts workflows using React Joyride.

## Target Workflows

### 1. Parts Ordering Workflow
**"How to Order Parts"**
- Navigate to Orders page
- Click "New Order" 
- Select supplier/customer type
- Search and select parts
- Set quantities and delivery details
- Submit order
- Track order status
- Receive parts notification
- Move parts to warehouse inventory

### 2. Parts Usage Recording
**"How to Record Part Usage"**
- Navigate to Machines page
- Select specific machine
- Click "Record Usage"
- Search for used part
- Enter quantity used
- Select maintenance context (daily/scheduled)
- Submit usage record
- View updated inventory levels

### 3. Daily Operations Recording
**"How to Record Daily Services"**
- Navigate to Daily Operations
- Select machine and date
- Fill operational metrics (hours, cycles, etc.)
- Record any issues or notes
- Mark daily checklist items
- Submit daily report
- View operation history

### 4. Scheduled Maintenance Recording
**"How to Record Scheduled Services"**
- Navigate to Maintenance Executions
- Select maintenance protocol
- Choose machine and technician
- Work through checklist items
- Record parts used during service
- Add photos and notes
- Mark protocol as completed
- Generate maintenance report

## Technical Implementation

### Dependencies
```bash
npm install react-joyride
```

### Core Components
- `TourProvider` - Context for managing tour state
- `GuidedTour` - Main tour component
- `TourButton` - Help button to trigger tours
- `TourSteps` - Step definitions for each workflow

### Integration Points
- Help button in main navigation
- Context-sensitive tour triggers
- Progress tracking and analytics
- Localization support for all 6 languages

### UI Design
- Floating help button (bottom-right corner)
- Overlay with highlighted elements
- Progress indicators
- Skip/Previous/Next controls
- Completion celebrations

## User Experience Flow

1. **Discovery**: Help button always visible
2. **Selection**: Choose from available tours
3. **Guidance**: Step-by-step overlay instructions
4. **Practice**: Real interactions with guided assistance
5. **Completion**: Success message and next steps
6. **Reference**: Ability to replay tours anytime

## Benefits
- Reduced support tickets
- Faster user onboarding
- Improved feature adoption
- Better user satisfaction
- Self-service learning