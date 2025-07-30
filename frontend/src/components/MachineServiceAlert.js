// frontend/src/components/MachineServiceAlert.js

import React from 'react';

const MachineServiceAlert = ({ machine, onScheduleService, onDismiss }) => {
  // Calculate service status based on machine hours
  const getServiceStatus = () => {
    if (!machine.current_hours || !machine.service_interval_hours) {
      return { status: 'unknown', message: 'Service information not available' };
    }

    const hoursSinceService = machine.current_hours - (machine.last_service_hours || 0);
    const serviceInterval = machine.service_interval_hours;

    if (hoursSinceService >= serviceInterval) {
      const overdueHours = hoursSinceService - serviceInterval;
      return {
        status: 'overdue',
        message: `Service overdue by ${overdueHours.toFixed(1)} hours`,
        urgency: 'high'
      };
    } else if (hoursSinceService >= serviceInterval * 0.9) {
      const remainingHours = serviceInterval - hoursSinceService;
      return {
        status: 'due_soon',
        message: `Service due in ${remainingHours.toFixed(1)} hours`,
        urgency: 'medium'
      };
    } else if (hoursSinceService >= serviceInterval * 0.8) {
      const remainingHours = serviceInterval - hoursSinceService;
      return {
        status: 'approaching',
        message: `Service due in ${remainingHours.toFixed(1)} hours`,
        urgency: 'low'
      };
    }

    return { status: 'ok', message: 'Service not due' };
  };

  const serviceStatus = getServiceStatus();

  // Don't render if service is OK
  if (serviceStatus.status === 'ok' || serviceStatus.status === 'unknown') {
    return null;
  }

  const getAlertStyles = () => {
    switch (serviceStatus.urgency) {
      case 'high':
        return 'bg-red-100 border-red-400 text-red-800';
      case 'medium':
        return 'bg-yellow-100 border-yellow-400 text-yellow-800';
      case 'low':
        return 'bg-blue-100 border-blue-400 text-blue-800';
      default:
        return 'bg-gray-100 border-gray-400 text-gray-800';
    }
  };

  const getIconColor = () => {
    switch (serviceStatus.urgency) {
      case 'high':
        return 'text-red-600';
      case 'medium':
        return 'text-yellow-600';
      case 'low':
        return 'text-blue-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className={`border rounded-lg p-4 mb-4 ${getAlertStyles()}`}>
      <div className="flex items-start">
        <div className={`flex-shrink-0 ${getIconColor()}`}>
          {serviceStatus.urgency === 'high' ? (
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          ) : (
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          )}
        </div>

        <div className="ml-3 flex-1">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium">
                {machine.name || machine.serial_number} - Service Alert
              </h3>
              <p className="text-sm mt-1">
                {serviceStatus.message}
              </p>
              <div className="text-xs mt-2 space-y-1">
                <p>Current Hours: {machine.current_hours?.toFixed(1) || 'N/A'}</p>
                <p>Last Service: {machine.last_service_hours?.toFixed(1) || 'N/A'} hours</p>
                <p>Service Interval: {machine.service_interval_hours?.toFixed(1) || 'N/A'} hours</p>
              </div>
            </div>

            <div className="flex items-center space-x-2 ml-4">
              {onScheduleService && (
                <button
                  onClick={() => onScheduleService(machine)}
                  className="text-xs bg-white border border-current rounded px-2 py-1 hover:bg-opacity-10 hover:bg-current"
                >
                  Schedule Service
                </button>
              )}
              {onDismiss && (
                <button
                  onClick={() => onDismiss(machine.id)}
                  className="text-xs text-gray-500 hover:text-gray-700"
                  title="Dismiss alert"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MachineServiceAlert;