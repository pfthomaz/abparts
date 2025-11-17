// frontend/src/components/MachineHoursReminderModal.js

import React, { useState } from 'react';
import { machinesService } from '../services/machinesService';

const MachineHoursReminderModal = ({ machines, onClose, onHoursSaved }) => {
  const [hoursData, setHoursData] = useState({});
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [successCount, setSuccessCount] = useState(0);

  const handleHoursChange = (machineId, value) => {
    setHoursData(prev => ({
      ...prev,
      [machineId]: value
    }));
  };

  const handleSaveAll = async () => {
    setSaving(true);
    setError(null);
    let saved = 0;

    try {
      // Save hours for each machine that has a value entered
      for (const [machineId, hours] of Object.entries(hoursData)) {
        if (hours && parseFloat(hours) > 0) {
          await machinesService.recordMachineHours(machineId, {
            hours_value: parseFloat(hours),
            notes: 'Recorded via reminder'
          });
          saved++;
        }
      }

      setSuccessCount(saved);
      
      if (saved > 0) {
        setTimeout(() => {
          if (onHoursSaved) onHoursSaved();
          onClose();
        }, 1500);
      }
    } catch (err) {
      setError(err.message || 'Failed to save machine hours');
    } finally {
      setSaving(false);
    }
  };

  const hasAnyHours = Object.values(hoursData).some(v => v && parseFloat(v) > 0);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-[90vh] overflow-hidden" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="bg-yellow-500 text-white px-6 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-xl font-bold">⏰ Machine Hours Reminder</h2>
              <p className="text-yellow-100 text-sm mt-1">
                The following machines haven't had hours recorded in the last 2 weeks
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-white hover:text-gray-200 text-2xl"
              disabled={saving}
            >
              ×
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          {successCount > 0 && (
            <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded mb-4">
              ✅ Successfully saved hours for {successCount} machine{successCount > 1 ? 's' : ''}!
            </div>
          )}

          <div className="space-y-4">
            {machines.map((machine) => (
              <div key={machine.id} className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">{machine.name}</h3>
                    <p className="text-sm text-gray-600">
                      Model: {machine.model_type} | Serial: {machine.serial_number}
                    </p>
                    {machine.last_hours_date && (
                      <p className="text-xs text-gray-500 mt-1">
                        Last recorded: {new Date(machine.last_hours_date).toLocaleDateString()} 
                        {' '}({machine.last_hours_value?.toLocaleString()} hrs)
                      </p>
                    )}
                    {!machine.last_hours_date && (
                      <p className="text-xs text-orange-600 mt-1">
                        ⚠️ No hours ever recorded
                      </p>
                    )}
                  </div>
                  
                  <div className="w-40">
                    <label className="block text-xs font-medium text-gray-700 mb-1">
                      Current Hours
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      placeholder="Enter hours..."
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      value={hoursData[machine.id] || ''}
                      onChange={(e) => handleHoursChange(machine.id, e.target.value)}
                      disabled={saving}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>

          {machines.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <p className="text-lg">✅ All machines are up to date!</p>
              <p className="text-sm mt-2">All machines have hours recorded within the last 2 weeks.</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="bg-gray-50 px-6 py-4 flex justify-between items-center border-t">
          <p className="text-sm text-gray-600">
            {machines.length} machine{machines.length !== 1 ? 's' : ''} need{machines.length === 1 ? 's' : ''} updating
          </p>
          <div className="flex space-x-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
              disabled={saving}
            >
              Skip for Now
            </button>
            {hasAnyHours && (
              <button
                onClick={handleSaveAll}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                disabled={saving}
              >
                {saving ? 'Saving...' : 'Save Hours'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MachineHoursReminderModal;
