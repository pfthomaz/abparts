// frontend/src/components/CustomerOrderForm.js

import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';

function CustomerOrderForm({ organizations = [], users = [], initialData = {}, onSubmit, onClose }) {
  const { token, user } = useAuth(); // Current logged-in user
  const [formData, setFormData] = useState({
    customer_organization_id: '',
    oraseas_organization_id: '', // Should default to Oraseas EE's ID
    order_date: new Date().toISOString().split('T')[0], // Default to today's date
    expected_delivery_date: '',
    actual_delivery_date: '',
    status: 'Pending', // Default status
    ordered_by_user_id: '',
    notes: '',
    ...initialData,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Find Oraseas EE organization
  const oraseasOrg = organizations.find(org => org.name === 'Oraseas EE' && org.type === 'Warehouse');

  useEffect(() => {
    const resetData = {
      customer_organization_id: '',
      oraseas_organization_id: oraseasOrg ? oraseasOrg.id : '', // Set Oraseas EE ID
      order_date: new Date().toISOString().split('T')[0],
      expected_delivery_date: '',
      actual_delivery_date: '',
      status: 'Pending',
      ordered_by_user_id: '',
      notes: '',
    };

    // Pre-fill customer_organization_id and ordered_by_user_id for Customer roles
    if (user && (user.role === 'Customer Admin' || user.role === 'Customer User')) {
      resetData.customer_organization_id = user.organization_id || '';
      resetData.ordered_by_user_id = user.id || '';
    }

    setFormData({ ...resetData, ...initialData });
  }, [initialData, user, oraseasOrg]);

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
      // Convert date strings to ISO 8601 format or set to null if empty
      const dataToSend = {
        ...formData,
        order_date: formData.order_date ? new Date(formData.order_date).toISOString() : null,
        expected_delivery_date: formData.expected_delivery_date ? new Date(formData.expected_delivery_date).toISOString() : null,
        actual_delivery_date: formData.actual_delivery_date ? new Date(formData.actual_delivery_date).toISOString() : null,
        // Ensure ordered_by_user_id is null if empty string
        ordered_by_user_id: formData.ordered_by_user_id || null,
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

      {/* Oraseas Organization (pre-filled and disabled) */}
      <div>
        <label htmlFor="oraseas_organization_id" className="block text-sm font-medium text-gray-700 mb-1">
          Oraseas Organization (Receiving Order)
        </label>
        <select
          id="oraseas_organization_id"
          name="oraseas_organization_id"
          className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100 cursor-not-allowed"
          value={formData.oraseas_organization_id}
          disabled={true} // Always disabled as it's pre-filled
        >
          {oraseasOrg && <option value={oraseasOrg.id}>{oraseasOrg.name}</option>}
          {!oraseasOrg && <option value="">Loading Oraseas EE...</option>}
        </select>
        {(!oraseasOrg && !loading) && (
            <p className="text-red-500 text-xs mt-1">Oraseas EE organization not found. Please ensure it exists.</p>
        )}
      </div>

      <div>
        <label htmlFor="order_date" className="block text-sm font-medium text-gray-700 mb-1">
          Order Date
        </label>
        <input
          type="date"
          id="order_date"
          name="order_date"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.order_date}
          onChange={handleChange}
          required
          disabled={loading}
        />
      </div>

      <div>
        <label htmlFor="expected_delivery_date" className="block text-sm font-medium text-gray-700 mb-1">
          Expected Delivery Date
        </label>
        <input
          type="date"
          id="expected_delivery_date"
          name="expected_delivery_date"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.expected_delivery_date || ''}
          onChange={handleChange}
          disabled={loading}
        />
      </div>

      <div>
        <label htmlFor="actual_delivery_date" className="block text-sm font-medium text-gray-700 mb-1">
          Actual Delivery Date
        </label>
        <input
          type="date"
          id="actual_delivery_date"
          name="actual_delivery_date"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.actual_delivery_date || ''}
          onChange={handleChange}
          disabled={loading}
        />
      </div>

      <div>
        <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">
          Status
        </label>
        <select
          id="status"
          name="status"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.status}
          onChange={handleChange}
          required
          disabled={loading}
        >
          <option value="Pending">Pending</option>
          <option value="Shipped">Shipped</option>
          <option value="Delivered">Delivered</option>
          <option value="Cancelled">Cancelled</option>
        </select>
      </div>

      {/* Ordered By User Dropdown */}
      <div>
        <label htmlFor="ordered_by_user_id" className="block text-sm font-medium text-gray-700 mb-1">
          Ordered By User (Optional)
        </label>
        <select
          id="ordered_by_user_id"
          name="ordered_by_user_id"
          className={`w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 ${disableUserSelection ? 'bg-gray-100 cursor-not-allowed' : ''}`}
          value={formData.ordered_by_user_id || ''}
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
          {loading ? 'Submitting...' : (initialData.id ? 'Update Order' : 'Create Order')}
        </button>
      </div>
    </form>
  );
}

export default CustomerOrderForm;
