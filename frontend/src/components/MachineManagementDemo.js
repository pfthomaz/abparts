// frontend/src/components/MachineManagementDemo.js

import React, { useState } from 'react';
import MachineHoursRecorder from './MachineHoursRecorder';
import MachineServiceAlert from './MachineServiceAlert';
import MachineTransferWizard from './MachineTransferWizard';
import MachineModelSelector from './MachineModelSelector';

const MachineManagementDemo = () => {
  const [activeModal, setActiveModal] = useState(null);
  const [selectedMachine, setSelectedMachine] = useState(null);

  // Sample machine data for demonstration
  const sampleMachine = {
    id: 'machine-123',
    name: 'Production Line A',
    serial_number: 'AB-2024-001',
    model: 'V4.0',
    current_hours: 1850.5,
    last_service_hours: 1500.0,
    service_interval_hours: 300.0,
    customer_organization_id: 'org-456'
  };

  const handleOpenModal = (modalType, machine = null) => {
    setSelectedMachine(machine || sampleMachine);
    setActiveModal(modalType);
  };

  const handleCloseModal = () => {
    setActiveModal(null);
    setSelectedMachine(null);
  };

  const handleHoursRecorded = () => {
    // console.log('Machine hours recorded successfully');
    // In a real app, you would refresh the machine data here
  };

  const handleTransferComplete = () => {
    // console.log('Machine transfer completed successfully');
    // In a real app, you would refresh the machine list here
  };

  const handleMachineUpdate = (updatedMachine) => {
    // console.log('Machine updated:', updatedMachine);
    // In a real app, you would update the machine in your state here
  };

  const handleScheduleService = (machine) => {
    // console.log('Scheduling service for machine:', machine.id);
    // In a real app, you would open a service scheduling interface
  };

  const handleDismissAlert = (machineId) => {
    // console.log('Dismissing alert for machine:', machineId);
    // In a real app, you would dismiss the alert in your state
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Machine Management Components Demo</h1>

      {/* Service Alert Demo */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold mb-4">Service Alert</h2>
        <MachineServiceAlert
          machine={sampleMachine}
          onScheduleService={handleScheduleService}
          onDismiss={handleDismissAlert}
        />
      </div>

      {/* Action Buttons */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold mb-4">Machine Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button
            onClick={() => handleOpenModal('hours')}
            className="p-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-center"
          >
            <div className="text-sm font-medium">Record Hours</div>
            <div className="text-xs opacity-90">Update machine hours</div>
          </button>

          <button
            onClick={() => handleOpenModal('transfer')}
            className="p-4 bg-orange-600 text-white rounded-lg hover:bg-orange-700 text-center"
          >
            <div className="text-sm font-medium">Transfer Machine</div>
            <div className="text-xs opacity-90">Change ownership</div>
          </button>

          <button
            onClick={() => handleOpenModal('model')}
            className="p-4 bg-green-600 text-white rounded-lg hover:bg-green-700 text-center"
          >
            <div className="text-sm font-medium">Configure Model</div>
            <div className="text-xs opacity-90">Set model & name</div>
          </button>

          <button
            onClick={() => handleOpenModal('name')}
            className="p-4 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-center"
          >
            <div className="text-sm font-medium">Edit Name</div>
            <div className="text-xs opacity-90">Admin only</div>
          </button>
        </div>
      </div>

      {/* Machine Info Display */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold mb-4">Sample Machine Data</h2>
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Name:</span>
              <div className="font-medium">{sampleMachine.name}</div>
            </div>
            <div>
              <span className="text-gray-600">Serial:</span>
              <div className="font-medium">{sampleMachine.serial_number}</div>
            </div>
            <div>
              <span className="text-gray-600">Model:</span>
              <div className="font-medium">{sampleMachine.model}</div>
            </div>
            <div>
              <span className="text-gray-600">Current Hours:</span>
              <div className="font-medium">{sampleMachine.current_hours}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Modals */}
      {activeModal === 'hours' && selectedMachine && (
        <MachineHoursRecorder
          machine={selectedMachine}
          onHoursRecorded={handleHoursRecorded}
          onClose={handleCloseModal}
        />
      )}

      {activeModal === 'transfer' && selectedMachine && (
        <MachineTransferWizard
          machine={selectedMachine}
          onTransferComplete={handleTransferComplete}
          onClose={handleCloseModal}
        />
      )}

      {activeModal === 'model' && selectedMachine && (
        <MachineModelSelector
          machine={selectedMachine}
          onUpdate={handleMachineUpdate}
          onClose={handleCloseModal}
          isNameEdit={false}
        />
      )}

      {activeModal === 'name' && selectedMachine && (
        <MachineModelSelector
          machine={selectedMachine}
          onUpdate={handleMachineUpdate}
          onClose={handleCloseModal}
          isNameEdit={true}
        />
      )}
    </div>
  );
};

export default MachineManagementDemo;