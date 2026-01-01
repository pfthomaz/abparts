import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useTour } from '../contexts/TourContext';

// Enhanced tour steps that can navigate and interact with real elements
export const createInteractiveTourSteps = (navigate) => ({
  partsOrdering: [
    {
      target: 'body',
      content: 'Welcome! Let\'s learn how to order parts. I\'ll guide you through the actual interface.',
      title: '📦 Interactive Parts Ordering',
      placement: 'center',
      disableBeacon: true,
    },
    {
      target: '.hidden.lg\\:flex.items-center.space-x-1',
      content: 'First, let\'s navigate to the Orders page. Hover over the navigation menu above.',
      title: 'Step 1: Find Navigation',
      placement: 'bottom',
      beforeStep: () => {
        // Ensure we're on a page where navigation is visible
        if (window.location.pathname === '/orders') return;
      }
    },
    {
      target: 'body',
      content: 'Perfect! Now I\'ll take you to the Orders page where you can see the actual interface.',
      title: 'Step 2: Navigate to Orders',
      placement: 'center',
      beforeStep: () => {
        navigate('/orders');
      }
    },
    {
      target: '[data-tour="new-order-button"], button:contains("New Order"), button:contains("Create")',
      content: 'Look for the "New Order" or "Create Order" button. This is where you start creating orders.',
      title: 'Step 3: Find New Order Button',
      placement: 'bottom',
    },
    {
      target: 'body',
      content: 'When you click "New Order", you\'ll see a form to:\n• Choose order type\n• Search for parts\n• Set quantities\n• Add delivery details',
      title: 'Step 4: Order Creation Process',
      placement: 'center',
    },
    {
      target: 'body',
      content: 'After submitting, you can track order status and receive notifications when parts arrive!',
      title: 'Step 5: Order Tracking',
      placement: 'center',
    }
  ],

  partsUsage: [
    {
      target: 'body',
      content: 'Let\'s learn how to record part usage. I\'ll show you the actual interface.',
      title: '🔧 Interactive Parts Usage',
      placement: 'center',
      disableBeacon: true,
    },
    {
      target: 'body',
      content: 'I\'ll take you to the Machines page where you can record part usage.',
      title: 'Step 1: Navigate to Machines',
      placement: 'center',
      beforeStep: () => {
        navigate('/machines');
      }
    },
    {
      target: 'body',
      content: 'On this page, you can:\n• Select a specific machine\n• Click "Record Usage"\n• Search for used parts\n• Enter quantities\n• Submit usage records',
      title: 'Step 2: Usage Recording Interface',
      placement: 'center',
    },
    {
      target: 'body',
      content: 'The system automatically updates inventory levels when you record usage!',
      title: 'Step 3: Automatic Updates',
      placement: 'center',
    }
  ],

  dailyOperations: [
    {
      target: 'body',
      content: 'Let\'s explore daily operations reporting with the real interface.',
      title: '📋 Interactive Daily Operations',
      placement: 'center',
      disableBeacon: true,
    },
    {
      target: 'body',
      content: 'I\'ll take you to the Daily Operations page.',
      title: 'Step 1: Navigate to Daily Operations',
      placement: 'center',
      beforeStep: () => {
        navigate('/daily-operations');
      }
    },
    {
      target: 'body',
      content: 'Here you can:\n• Select date and machine\n• Enter operational metrics\n• Complete checklists\n• Add notes and observations\n• Submit daily reports',
      title: 'Step 2: Daily Reporting Interface',
      placement: 'center',
    }
  ],

  scheduledMaintenance: [
    {
      target: 'body',
      content: 'Let\'s explore scheduled maintenance with the actual interface.',
      title: '⚙️ Interactive Maintenance',
      placement: 'center',
      disableBeacon: true,
    },
    {
      target: 'body',
      content: 'I\'ll take you to the Maintenance Executions page.',
      title: 'Step 1: Navigate to Maintenance',
      placement: 'center',
      beforeStep: () => {
        navigate('/maintenance-executions');
      }
    },
    {
      target: 'body',
      content: 'On this page, you can:\n• Select maintenance protocols\n• Assign machines and technicians\n• Execute checklists\n• Record parts used\n• Add photos and notes\n• Complete protocols',
      title: 'Step 2: Maintenance Interface',
      placement: 'center',
    }
  ]
});

// Hook to use interactive tours
export const useInteractiveTour = () => {
  const navigate = useNavigate();
  const { startTour } = useTour();

  const startInteractiveTour = (tourId) => {
    const interactiveSteps = createInteractiveTourSteps(navigate);
    const steps = interactiveSteps[tourId];
    
    if (steps) {
      startTour(tourId, steps);
    }
  };

  return { startInteractiveTour };
};