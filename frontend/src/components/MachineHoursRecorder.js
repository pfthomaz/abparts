// frontend/src/components/MachineHoursRecorder.js

import React, { useState } from 'react';
import { machinesService } from '../services/machinesService';
import { useAuth } from '../AuthContext';

const MachineHoursRecorder = ({ machine, onSubmit, onClose, onHoursRecorded }) => {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    hours_value: '',
    recorded_date: new Date().toISOString().split('T')[0],
    notes: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

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

    if (!formData.hours_value || parseFloat(formData.hours_value) <= 0) {
      setError('Please enter a valid hours value');
      return;
    }

    setLoading(true);
    try {
      const hoursData = {
        hours_value: parseFloat(formData.hours_value),
        recorded_date: formData.recorded_date,
        notes: formData.notes.trim() || null
      };

      await machinesService.recordMachineHours(machine.id, hoursData);

      if (onHoursRecorded) {
        onHoursRecorded();
      }
      if (onSubmit) {
        onSubmit();
      }
      if (onClose) {
        onClose();
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to record machine hours');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Record Machine Hours</h2>
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

        <div className="mb-4">
          <p className="text-sm text-gray-600">
            <strong>Machine:</strong> {machine.name || machine.serial_number}
          </p>
          <p className="text-sm text-gray-600">
            <strong>Model:</strong> {machine.model}
          </p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="hours_value" className="block text-sm font-medium text-gray-700 mb-2">
              Hours Value *
            </label>
            <input
              type="number"
              id="hours_value"
              name="hours_value"
              value={formData.hours_value}
              onChange={handleInputChange}
              step="0.1"
              min="0.1"
              max="99999.9"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter hours (e.g., 123.5)"
              required
              disabled={loading}
            />
          </div>

          <div className="mb-4">
            <label htmlFor="recorded_date" className="block text-sm font-medium text-gray-700 mb-2">
              Date *
            </label>
            <input
              type="date"
              id="recorded_date"
              name="recorded_date"
              value={formData.recorded_date}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
              disabled={loading}
            />
          </div>

          <div className="mb-6">
            <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-2">
              Notes
            </label>
            <textarea
              id="notes"
              name="notes"
              value={formData.notes}
              onChange={handleInputChange}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Optional notes about this reading..."
              disabled={loading}
            />
          </div>

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
              {loading ? 'Recording...' : 'Record Hours'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default MachineHoursRecorder;