// c:/abparts/frontend/src/components/MachineForm.js

import React, { useState, useEffect } from 'react';

const MachineForm = ({ initialData = {}, organizations = [], onSubmit, onClose }) => {
  const [formData, setFormData] = useState({
    organization_id: '',
    model_type: '',
    name: '',
    serial_number: '',
  });
  const [error, setError] = useState('');

  useEffect(() => {
    if (initialData.id) {
      setFormData({
        organization_id: initialData.organization_id || '',
        model_type: initialData.model_type || '',
        name: initialData.name || '',
        serial_number: initialData.serial_number || '',
      });
    } else {
      // Reset for new entry
      setFormData({
        organization_id: '',
        model_type: '',
        name: '',
        serial_number: '',
      });
    }
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!formData.organization_id || !formData.model_type || !formData.name || !formData.serial_number) {
      setError('All fields are required.');
      return;
    }
    try {
      await onSubmit(formData);
    } catch (err) {
      setError(err.message || 'An unexpected error occurred.');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded" role="alert">{error}</div>}
      
      <div>
        <label htmlFor="organization_id" className="block text-sm font-medium text-gray-700">Organization</label>
        <select
          id="organization_id"
          name="organization_id"
          value={formData.organization_id}
          onChange={handleChange}
          className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
          required
        >
          <option value="">Select an Organization</option>
          {organizations.map(org => (
            <option key={org.id} value={org.id}>{org.name}</option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700">Machine Name</label>
        <input type="text" id="name" name="name" value={formData.name} onChange={handleChange} className="mt-1 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md" required />
      </div>

      <div>
        <label htmlFor="model_type" className="block text-sm font-medium text-gray-700">Model Type</label>
        <input type="text" id="model_type" name="model_type" value={formData.model_type} onChange={handleChange} className="mt-1 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md" required />
      </div>

      <div>
        <label htmlFor="serial_number" className="block text-sm font-medium text-gray-700">Serial Number</label>
        <input type="text" id="serial_number" name="serial_number" value={formData.serial_number} onChange={handleChange} className="mt-1 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md" required />
      </div>

      <div className="flex justify-end space-x-2 pt-4">
        <button type="button" onClick={onClose} className="bg-gray-200 text-gray-800 py-2 px-4 rounded-md hover:bg-gray-300">
          Cancel
        </button>
        <button type="submit" className="bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700">
          Save Machine
        </button>
      </div>
    </form>
  );
};

export default MachineForm;