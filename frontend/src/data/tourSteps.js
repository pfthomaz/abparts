// Tour step definitions for each workflow
// These now use translation keys that will be resolved by the tour components
export const tourSteps = {
  partsOrdering: [
    {
      target: 'body',
      content: 'tour.partsOrdering.steps.welcome',
      title: 'tour.partsOrdering.steps.welcomeTitle',
      placement: 'center',
      disableBeacon: true,
    },
    {
      target: '.hidden.lg\\:flex.items-center.space-x-1',
      content: 'tour.partsOrdering.steps.findOrders',
      title: 'tour.partsOrdering.step1',
      placement: 'bottom',
    },
    {
      target: 'body',
      content: 'tour.partsOrdering.steps.createOrder',
      title: 'tour.partsOrdering.step2',
      placement: 'center',
    },
    {
      target: 'body',
      content: 'tour.partsOrdering.steps.selectType',
      title: 'tour.partsOrdering.step3',
      placement: 'center',
    },
    {
      target: 'body',
      content: 'tour.partsOrdering.steps.searchParts',
      title: 'tour.partsOrdering.step4',
      placement: 'center',
    },
    {
      target: 'body',
      content: 'tour.partsOrdering.steps.setQuantities',
      title: 'tour.partsOrdering.step5',
      placement: 'center',
    },
    {
      target: 'body',
      content: 'tour.partsOrdering.steps.submitTrack',
      title: 'tour.partsOrdering.step6',
      placement: 'center',
    }
  ],

  partsUsage: [
    {
      target: 'body',
      content: 'tour.partsUsage.steps.welcome',
      title: 'tour.partsUsage.steps.welcomeTitle',
      placement: 'center',
      disableBeacon: true,
    },
    {
      target: '.hidden.lg\\:flex.items-center.space-x-1',
      content: 'tour.partsUsage.steps.goToMachines',
      title: 'tour.partsUsage.step1',
      placement: 'bottom',
    },
    {
      target: 'body',
      content: 'tour.partsUsage.steps.selectMachine',
      title: 'tour.partsUsage.step2',
      placement: 'center',
    },
    {
      target: 'body',
      content: 'tour.partsUsage.steps.recordUsage',
      title: 'tour.partsUsage.step3',
      placement: 'center',
    },
    {
      target: 'body',
      content: 'tour.partsUsage.steps.findPart',
      title: 'tour.partsUsage.step4',
      placement: 'center',
    },
    {
      target: 'body',
      content: 'tour.partsUsage.steps.enterQuantity',
      title: 'tour.partsUsage.step5',
      placement: 'center',
    }
  ],

  dailyOperations: [
    {
      target: 'body',
      content: 'tour.dailyOperations.steps.welcome',
      title: 'tour.dailyOperations.steps.welcomeTitle',
      placement: 'center',
      disableBeacon: true,
    },
    {
      target: '.hidden.lg\\:flex.items-center.space-x-1',
      content: 'tour.dailyOperations.steps.navigate',
      title: 'tour.dailyOperations.step1',
      placement: 'bottom',
    },
    {
      target: 'body',
      content: 'tour.dailyOperations.steps.chooseDateMachine',
      title: 'tour.dailyOperations.step2',
      placement: 'center',
    },
    {
      target: 'body',
      content: 'tour.dailyOperations.steps.enterMetrics',
      title: 'tour.dailyOperations.step3',
      placement: 'center',
    },
    {
      target: 'body',
      content: 'tour.dailyOperations.steps.completeChecklist',
      title: 'tour.dailyOperations.step4',
      placement: 'center',
    },
    {
      target: 'body',
      content: 'tour.dailyOperations.steps.submitReport',
      title: 'tour.dailyOperations.step5',
      placement: 'center',
    }
  ],

  scheduledMaintenance: [
    {
      target: 'body',
      content: 'tour.scheduledMaintenance.steps.welcome',
      title: 'tour.scheduledMaintenance.steps.welcomeTitle',
      placement: 'center',
      disableBeacon: true,
    },
    {
      target: '.hidden.lg\\:flex.items-center.space-x-1',
      content: 'tour.scheduledMaintenance.steps.findMaintenance',
      title: 'tour.scheduledMaintenance.step1',
      placement: 'bottom',
    },
    {
      target: 'body',
      content: 'tour.scheduledMaintenance.steps.chooseProtocol',
      title: 'tour.scheduledMaintenance.step2',
      placement: 'center',
    },
    {
      target: 'body',
      content: 'tour.scheduledMaintenance.steps.assignResources',
      title: 'tour.scheduledMaintenance.step3',
      placement: 'center',
    },
    {
      target: 'body',
      content: 'tour.scheduledMaintenance.steps.executeChecklist',
      title: 'tour.scheduledMaintenance.step4',
      placement: 'center',
    },
    {
      target: 'body',
      content: 'tour.scheduledMaintenance.steps.documentWork',
      title: 'tour.scheduledMaintenance.step5',
      placement: 'center',
    },
    {
      target: 'body',
      content: 'tour.scheduledMaintenance.steps.completeSchedule',
      title: 'tour.scheduledMaintenance.step6',
      placement: 'center',
    }
  ]
};