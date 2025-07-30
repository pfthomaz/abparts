// frontend/src/components/MachineModelSelector.js

import React, { useState } from 'react';
import { machinesService } from '../services/machinesService';
import { useAuth } from '../AuthContext';

const MachineModelSelector = ({ machine, onUpdate, onClose, isNameEdit = false }) => {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    model: machine?.model || '',
    name: machine?.name || ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Available machine models based on requirements
  const availableModels = [
    { value: 'V3.1B', label: 'AutoBoss V3.1B', description: 'Standard model with basic features' },
    { value: 'V4.0', label: 'AutoBoss V4.0', description: 'Advanced model with enhanced capabilities' }
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (isNameEdit) {
      // Only updating machine name (admin only)
      if (!formData.name.trim()) {
        setError('Machine name cannot be empty');
        return;
      }

      setLoading(true);
      try {
        await machinesService.updateMachineName(machine.id, formData.name.trim());

        if (onUpdate) {
          onUpdate({ ...machine, name: formData.name.trim() });
        }
        if (onClose) {
          onClose();
        }
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to update machine name');
      } finally {
        setLoading(false);
      }
    } else {
      // Creating new machine or updating model
      if (!formData.model) {
        setError('Please select a machine model');
        return;
      }

      setLoading(true);
      try {
        const updateData = {
          model: formData.model,
          name: formData.name.trim() || null
        };

        let updatedMachine;
        if (machine?.id) {
          // Update existing machine
          updatedMachine = await machinesService.updateMachine(machine.id, updateData);
        } else {
          // This would be handled by a parent component for machine creation
          if (onUpdate) {
            onUpdate(updateData);
          }
          if (onClose) {
            onClose();
          }
          return;
        }

        if (onUpdate) {
          onUpdate(updatedMachine);
        }
        if (onClose) {
          onClose();
        }
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to update machine');
      } finally {
        setLoading(false);
      }
    }
  };

  const canEditName = user?.role === 'admin' || user?.role === 'super_admin';

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">
            {isNameEdit ? 'Edit Machine Name' : 'Machine Configuration'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
            disabled={loading}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {machine && (
          <div className="mb-4 p-3 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-600">
              <strong>Serial Number:</strong> {machine.serial_number}
            </p>
            {machine.current_hours && (
              <p className="text-sm text-gray-600">
                <strong>Current Hours:</strong> {machine.current_hours.toFixed(1)}
              </p>
            )}
          </div>
        )}

        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {!isNameEdit && (
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Machine Model *
              </label>
              <div className="space-y-2">
                {availableModels.map(model => (
                  <label key={model.value} className="flex items-start p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                    <input
                      type="radio"
                      name="model"
                      value={model.value}
                      checked={formData.model === model.value}
                      onChange={handleInputChange}
                      className="mt-1 mr-3"
                      disabled={loading}
                    />
                    <div>
                      <div className="font-medium">{model.label}</div>
                      <div className="text-sm text-gray-600">{model.description}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          )}

          {(canEditName || !machine) && (
            <div className="mb-6">
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                Machine Name {isNameEdit && '*'}
              </label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter custom machine name (optional)"
                disabled={loading}
                required={isNameEdit}
                maxLength={100}
              />
              <p className="text-xs text-gray-500 mt-1">
                {isNameEdit
                  ? 'Provide a custom name for this machine'
                  : 'Optional: Provide a custom name for easier identification'
                }
              </p>
            </div>
          )}

          {!canEditName && machine && !isNameEdit && (
            <div className="mb-6 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex">
                <svg className="w-5 h-5 text-blue-600 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                <div>
                  <p className="text-sm text-blue-800">
                    <strong>Note:</strong> Only administrators can customize machine names.
                  </p>
                </div>
              </div>
            </div>
          )}

          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 disabled:opacity-50"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              disabled={loading}
            >
              {loading ? 'Saving...' : (isNameEdit ? 'Update Name' : 'Save Configuration')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default MachineModelSelector;