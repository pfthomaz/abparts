// frontend/src/components/MachineForm.js

import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';

function MachineForm({ organizations = [], initialData = {}, onSubmit, onClose }) {
  const { user } = useAuth(); // Get current logged-in user
  const [formData, setFormData] = useState({
    organization_id: '',
    name: '',
    model_type: '',
    serial_number: '',
    ...initialData,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const resetData = {
      organization_id: '',
      name: '',
      model_type: '',
      serial_number: '',
    };

    // Pre-fill organization_id if the user is a Customer Admin or Customer User
    // and not an Oraseas Admin (who might be creating for any org)
    if (user && (user.role === 'Customer Admin' || user.role === 'Customer User')) {
      resetData.organization_id = user.organization_id || '';
    }

    setFormData({ ...resetData, ...initialData });
  }, [initialData, user]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await onSubmit(formData); // The parent component (App.js) handles the API call
      onClose(); // Close modal on successful submission
    } catch (err) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  // Filter organizations:
  // Oraseas Admin can select any.
  // Customer Admin/User can only select their own organization.
  const filteredOrganizations = organizations.filter(org => {
    if (!user) return false;
    if (user.role === 'Oraseas Admin' || user.role === 'Oraseas Inventory Manager') { // Oraseas roles can see all for now
      return true;
    }
    return org.id === user.organization_id;
  });

  const disableOrgSelection = loading || (user && (user.role === 'Customer Admin' || user.role === 'Customer User'));


  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Error:</strong>
          <span className="block sm:inline ml-2">{error}</span>
        </div>
      )}

      <div>
        <label htmlFor="organization_id" className="block text-sm font-medium text-gray-700 mb-1">
          Organization
        </label>
        <select
          id="organization_id"
          name="organization_id"
          className={`w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 ${disableOrgSelection ? 'bg-gray-100 cursor-not-allowed' : ''}`}
          value={formData.organization_id}
          onChange={handleChange}
          required
          disabled={disableOrgSelection}
        >
          <option value="">Select Organization</option>
          {filteredOrganizations.map(org => (
            <option key={org.id} value={org.id}>{org.name}</option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
          Machine Name
        </label>
        <input
          type="text"
          id="name"
          name="name"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.name}
          onChange={handleChange}
          required
          disabled={loading}
        />
      </div>

      <div>
        <label htmlFor="model_type" className="block text-sm font-medium text-gray-700 mb-1">
          Model Type
        </label>
        <input
          type="text"
          id="model_type"
          name="model_type"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.model_type}
          onChange={handleChange}
          required
          disabled={loading}
        />
      </div>

      <div>
        <label htmlFor="serial_number" className="block text-sm font-medium text-gray-700 mb-1">
          Serial Number
        </label>
        <input
          type="text"
          id="serial_number"
          name="serial_number"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.serial_number}
          onChange={handleChange}
          required
          disabled={loading}
        />
      </div>

      <div className="flex justify-end space-x-3 mt-6">
        <button
          type="button"
          onClick={onClose}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
          disabled={loading}
        >
          Cancel
        </button>
        <button
          type="submit"
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          disabled={loading}
        >
          {loading ? 'Submitting...' : (initialData.id ? 'Update Machine' : 'Create Machine')}
        </button>
      </div>
    </form>
  );
}

export default MachineForm;
