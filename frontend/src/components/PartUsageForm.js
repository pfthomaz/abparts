// frontend/src/components/PartUsageForm.js

import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';

function PartUsageForm({ organizations = [], parts = [], users = [], initialData = {}, onSubmit, onClose }) {
  const { token, user } = useAuth(); // Current logged-in user
  const [formData, setFormData] = useState({
    customer_organization_id: '',
    part_id: '',
    usage_date: new Date().toISOString().split('T')[0], // Default to today's date
    quantity_used: 1,
    machine_id: '',
    recorded_by_user_id: '',
    notes: '',
    ...initialData,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const resetData = {
      customer_organization_id: '',
      part_id: '',
      usage_date: new Date().toISOString().split('T')[0],
      quantity_used: 1,
      machine_id: '',
      recorded_by_user_id: '',
      notes: '',
    };

    // Pre-fill customer_organization_id and recorded_by_user_id for Customer roles
    if (user && (user.role === 'Customer Admin' || user.role === 'Customer User')) {
      resetData.customer_organization_id = user.organization_id || '';
      resetData.recorded_by_user_id = user.id || '';
    }

    setFormData({ ...resetData, ...initialData });
  }, [initialData, user]);

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: type === 'number' ? parseInt(value, 10) : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Ensure numerical fields are parsed correctly, or set to null if empty string for optional fields
      const dataToSend = {
        ...formData,
        usage_date: formData.usage_date ? new Date(formData.usage_date).toISOString() : null,
        quantity_used: parseInt(formData.quantity_used, 10),
        machine_id: formData.machine_id || null, // Convert empty string to null for optional field
        recorded_by_user_id: formData.recorded_by_user_id || null, // Convert empty string to null for optional field
        notes: formData.notes || null, // Convert empty string to null for optional field
      };

      await onSubmit(dataToSend);
      onClose(); // Close modal on successful submission
    } catch (err) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  // Filter organizations: only 'Customer' type can be selected as customer_organization_id
  const customerOrganizations = organizations.filter(org => org.type === 'Customer');

  // Filter users based on the selected customer_organization_id
  const filteredUsers = users.filter(usr => usr.organization_id === formData.customer_organization_id);

  // Determine if the organization dropdown should be disabled
  const disableOrgSelection = loading || (user && (user.role === 'Customer Admin' || user.role === 'Customer User'));
  // Determine if the user dropdown should be disabled
  const disableUserSelection = loading || (user && (user.role === 'Customer Admin' || user.role === 'Customer User'));


  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Error:</strong>
          <span className="block sm:inline ml-2">{error}</span>
        </div>
      )}

      {/* Customer Organization Dropdown */}
      <div>
        <label htmlFor="customer_organization_id" className="block text-sm font-medium text-gray-700 mb-1">
          Customer Organization
        </label>
        <select
          id="customer_organization_id"
          name="customer_organization_id"
          className={`w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 ${disableOrgSelection ? 'bg-gray-100 cursor-not-allowed' : ''}`}
          value={formData.customer_organization_id}
          onChange={handleChange}
          required
          disabled={disableOrgSelection}
        >
          <option value="">Select Customer Organization</option>
          {customerOrganizations.map(org => (
            <option key={org.id} value={org.id}>{org.name}</option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="part_id" className="block text-sm font-medium text-gray-700 mb-1">
          Part
        </label>
        <select
          id="part_id"
          name="part_id"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.part_id}
          onChange={handleChange}
          required
          disabled={loading}
        >
          <option value="">Select a Part</option>
          {parts.map((part) => (
            <option key={part.id} value={part.id}>{part.name} ({part.part_number})</option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="usage_date" className="block text-sm font-medium text-gray-700 mb-1">
          Usage Date
        </label>
        <input
          type="date"
          id="usage_date"
          name="usage_date"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.usage_date}
          onChange={handleChange}
          required
          disabled={loading}
        />
      </div>

      <div>
        <label htmlFor="quantity_used" className="block text-sm font-medium text-gray-700 mb-1">
          Quantity Used
        </label>
        <input
          type="number"
          id="quantity_used"
          name="quantity_used"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.quantity_used}
          onChange={handleChange}
          min="1"
          required
          disabled={loading}
        />
      </div>

      <div>
        <label htmlFor="machine_id" className="block text-sm font-medium text-gray-700 mb-1">
          Machine ID (Optional)
        </label>
        <input
          type="text"
          id="machine_id"
          name="machine_id"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.machine_id || ''}
          onChange={handleChange}
          disabled={loading}
        />
      </div>

      {/* Recorded By User Dropdown */}
      <div>
        <label htmlFor="recorded_by_user_id" className="block text-sm font-medium text-gray-700 mb-1">
          Recorded By User (Optional)
        </label>
        <select
          id="recorded_by_user_id"
          name="recorded_by_user_id"
          className={`w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 ${disableUserSelection ? 'bg-gray-100 cursor-not-allowed' : ''}`}
          value={formData.recorded_by_user_id || ''}
          onChange={handleChange}
          disabled={disableUserSelection}
        >
          <option value="">Select User (Optional)</option>
          {filteredUsers.map(u => (
            <option key={u.id} value={u.id}>{u.name || u.username}</option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-1">
          Notes
        </label>
        <textarea
          id="notes"
          name="notes"
          rows="3"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.notes || ''}
          onChange={handleChange}
          disabled={loading}
        ></textarea>
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
          {loading ? 'Submitting...' : (initialData.id ? 'Update Usage' : 'Record Usage')}
        </button>
      </div>
    </form>
  );
}

export default PartUsageForm;
