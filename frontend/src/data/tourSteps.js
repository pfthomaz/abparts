// Tour step definitions for each workflow
export const tourSteps = {
  partsOrdering: [
    {
      target: 'body',
      content: 'Welcome! Let\'s learn how to order parts step-by-step.',
      title: '📦 Parts Ordering Tutorial',
      placement: 'center',
      disableBeacon: true,
    },
    {
      target: '.hidden.lg\\:flex.items-center.space-x-1',
      content: 'First, hover over the navigation menu to find "Orders".',
      title: 'Step 1: Find Orders',
      placement: 'bottom',
    },
    {
      target: 'body',
      content: 'Click "New Order" button to start creating an order.',
      title: 'Step 2: Create New Order',
      placement: 'center',
    },
    {
      target: 'body',
      content: 'Choose order type: Customer Order (buying parts) or Supplier Order (selling parts).',
      title: 'Step 3: Select Order Type',
      placement: 'center',
    },
    {
      target: 'body',
      content: 'Search for parts by name, number, or description.',
      title: 'Step 4: Search Parts',
      placement: 'center',
    },
    {
      target: 'body',
      content: 'Enter quantities needed and review stock levels.',
      title: 'Step 5: Set Quantities',
      placement: 'center',
    },
    {
      target: 'body',
      content: 'Add delivery details and submit your order. You can then track its status!',
      title: 'Step 6: Submit & Track',
      placement: 'center',
    }
  ],

  partsUsage: [
    {
      target: 'body',
      content: 'Let\'s learn how to record parts consumed during machine operation.',
      title: '🔧 Parts Usage Recording',
      placement: 'center',
      disableBeacon: true,
    },
    {
      target: '.hidden.lg\\:flex.items-center.space-x-1',
      content: 'Navigate to "Machines" in the Operations menu.',
      title: 'Step 1: Go to Machines',
      placement: 'bottom',
    },
    {
      target: 'body',
      content: 'Select the specific machine where parts were used.',
      title: 'Step 2: Select Machine',
      placement: 'center',
    },
    {
      target: 'body',
      content: 'Click "Record Usage" to log consumed parts.',
      title: 'Step 3: Record Usage',
      placement: 'center',
    },
    {
      target: 'body',
      content: 'Search and select the part that was used.',
      title: 'Step 4: Find Part',
      placement: 'center',
    },
    {
      target: 'body',
      content: 'Enter quantity used - inventory updates automatically!',
      title: 'Step 5: Enter Quantity',
      placement: 'center',
    }
  ],

  dailyOperations: [
    {
      target: 'body',
      content: 'Daily reporting helps track machine performance and maintenance.',
      title: '📋 Daily Operations',
      placement: 'center',
      disableBeacon: true,
    },
    {
      target: '.hidden.lg\\:flex.items-center.space-x-1',
      content: 'Find "Daily Operations" in the Operations menu.',
      title: 'Step 1: Navigate Here',
      placement: 'bottom',
    },
    {
      target: 'body',
      content: 'Select the date and machine for your report.',
      title: 'Step 2: Choose Date & Machine',
      placement: 'center',
    },
    {
      target: 'body',
      content: 'Enter operational metrics: hours, cycles, performance data.',
      title: 'Step 3: Enter Metrics',
      placement: 'center',
    },
    {
      target: 'body',
      content: 'Complete daily checklist items and add notes.',
      title: 'Step 4: Complete Checklist',
      placement: 'center',
    },
    {
      target: 'body',
      content: 'Submit report to track machine health trends.',
      title: 'Step 5: Submit Report',
      placement: 'center',
    }
  ],

  scheduledMaintenance: [
    {
      target: 'body',
      content: 'Execute scheduled maintenance protocols systematically.',
      title: '⚙️ Scheduled Maintenance',
      placement: 'center',
      disableBeacon: true,
    },
    {
      target: '.hidden.lg\\:flex.items-center.space-x-1',
      content: 'Go to "Maintenance Executions" in Operations.',
      title: 'Step 1: Find Maintenance',
      placement: 'bottom',
    },
    {
      target: 'body',
      content: 'Select the maintenance protocol to execute.',
      title: 'Step 2: Choose Protocol',
      placement: 'center',
    },
    {
      target: 'body',
      content: 'Assign machine and technician for the maintenance.',
      title: 'Step 3: Assign Resources',
      placement: 'center',
    },
    {
      target: 'body',
      content: 'Work through checklist items systematically.',
      title: 'Step 4: Execute Checklist',
      placement: 'center',
    },
    {
      target: 'body',
      content: 'Record parts used and add photos/notes.',
      title: 'Step 5: Document Work',
      placement: 'center',
    },
    {
      target: 'body',
      content: 'Complete protocol to generate reports and schedule next service.',
      title: 'Step 6: Complete & Schedule',
      placement: 'center',
    }
  ]
};