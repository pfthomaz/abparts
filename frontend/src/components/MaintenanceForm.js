// frontend/src/components/MaintenanceForm.js

import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';

const MaintenanceForm = ({ machineId, initialData = {}, onSubmit, onClose }) => {
  const [formData, setFormData] = useState({
    machine_id: machineId,
    maintenance_date: '',
    maintenance_type: '',
    description: '',
    duration_hours: '',
    cost: '',
    performed_by_user_id: '',
    next_maintenance_date: '',
    parts_used: []
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { user } = useAuth();

  const maintenanceTypes = [
    'routine',
    'preventive',
    'corrective',
    'emergency',
    'inspection',
    'cleaning',
    'calibration',
    'repair',
    'replacement',
    'upgrade',
    'other'
  ];

  useEffect(() => {
    if (initialData.id) {
      setFormData({
        machine_id: machineId,
        maintenance_date: initialData.maintenance_date ?
          new Date(initialData.maintenance_date).toISOString().split('T')[0] : '',
        maintenance_type: initialData.maintenance_type || '',
        description: initialData.description || '',
        duration_hours: initialData.duration_hours || '',
        cost: initialData.cost || '',
        performed_by_user_id: initialData.performed_by_user_id || user?.id || '',
        next_maintenance_date: initialData.next_maintenance_date ?
          new Date(initialData.next_maintenance_date).toISOString().split('T')[0] : '',
        parts_used: initialData.parts_used || []
      });
    } else {
      // Set defaults for new maintenance record
      setFormData(prev => ({
        ...prev,
        machine_id: machineId,
        maintenance_date: new Date().toISOString().split('T')[0],
        performed_by_user_id: user?.id || ''
      }));
    }
  }, [initialData, machineId, user]);

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? (value === '' ? '' : parseFloat(value)) : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Validation
    if (!formData.maintenance_date || !formData.maintenance_type) {
      setError('Maintenance date and type are required.');
      setLoading(false);
      return;
    }

    try {
      // Convert date strings to ISO format for API
      const submitData = {
        ...formData,
        maintenance_date: new Date(formData.maintenance_date).toISOString(),
        next_maintenance_date: formData.next_maintenance_date ?
          new Date(formData.next_maintenance_date).toISOString() : null,
        duration_hours: formData.duration_hours ? parseFloat(formData.duration_hours) : null,
        cost: formData.cost ? parseFloat(formData.cost) : null
      };

      await onSubmit(submitData);
    } catch (err) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded" role="alert">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="maintenance_date" className="block text-sm font-medium text-gray-700">
            Maintenance Date *
          </label>
          <input
            type="date"
            id="maintenance_date"
            name="maintenance_date"
            value={formData.maintenance_date}
            onChange={handleChange}
            className="mt-1 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            required
          />
        </div>

        <div>
          <label htmlFor="maintenance_type" className="block text-sm font-medium text-gray-700">
            Maintenance Type *
          </label>
          <select
            id="maintenance_type"
            name="maintenance_type"
            value={formData.maintenance_type}
            onChange={handleChange}
            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
            required
          >
            <option value="">Select maintenance type</option>
            {maintenanceTypes.map(type => (
              <option key={type} value={type}>
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700">
          Description
        </label>
        <textarea
          id="description"
          name="description"
          rows={3}
          value={formData.description}
          onChange={handleChange}
          placeholder="Describe the maintenance work performed..."
          className="mt-1 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="duration_hours" className="block text-sm font-medium text-gray-700">
            Duration (hours)
          </label>
          <input
            type="number"
            id="duration_hours"
            name="duration_hours"
            step="0.5"
            min="0"
            value={formData.duration_hours}
            onChange={handleChange}
            className="mt-1 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div>
          <label htmlFor="cost" className="block text-sm font-medium text-gray-700">
            Cost ($)
          </label>
          <input
            type="number"
            id="cost"
            name="cost"
            step="0.01"
            min="0"
            value={formData.cost}
            onChange={handleChange}
            className="mt-1 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>

      <div>
        <label htmlFor="next_maintenance_date" className="block text-sm font-medium text-gray-700">
          Next Scheduled Maintenance
        </label>
        <input
          type="date"
          id="next_maintenance_date"
          name="next_maintenance_date"
          value={formData.next_maintenance_date}
          onChange={handleChange}
          className="mt-1 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
        />
      </div>

      <div className="flex justify-end space-x-2 pt-4">
        <button
          type="button"
          onClick={onClose}
          className="bg-gray-200 text-gray-800 py-2 px-4 rounded-md hover:bg-gray-300"
          disabled={loading}
        >
          Cancel
        </button>
        <button
          type="submit"
          className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
          disabled={loading}
        >
          {loading ? 'Saving...' : 'Save Maintenance Record'}
        </button>
      </div>
    </form>
  );
};

export default MaintenanceForm;