// frontend/src/components/InventoryForm.js

import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';

function InventoryForm({ organizations = [], parts = [], initialData = {}, onSubmit, onClose }) {
  const { token, user } = useAuth();
  const [formData, setFormData] = useState({
    organization_id: '',
    part_id: '',
    current_stock: 0,
    minimum_stock_recommendation: 0,
    reorder_threshold_set_by: 'user', // Default value
    ...initialData,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Reset form data when initialData changes (e.g., opening for new vs. edit)
    const resetData = {
      organization_id: '',
      part_id: '',
      current_stock: 0,
      minimum_stock_recommendation: 0,
      reorder_threshold_set_by: 'user',
    };

    setFormData({ ...resetData, ...initialData });

    // For Customer Admin/User roles, pre-fill their organization_id
    if (user && (user.role === 'Customer Admin' || user.role === 'Customer User')) {
      setFormData(prevData => ({
        ...prevData,
        organization_id: user.organization_id || '',
      }));
    }
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
      // Ensure numerical fields are numbers, even if optional
      const dataToSend = {
        ...formData,
        current_stock: parseInt(formData.current_stock, 10),
        minimum_stock_recommendation: parseInt(formData.minimum_stock_recommendation, 10),
      };

      await onSubmit(dataToSend);
      onClose(); // Close modal on successful submission
    } catch (err) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  // Filter organizations based on user role
  const getFilteredOrganizations = () => {
    if (!user) return [];
    if (user.role === "Oraseas Admin" || user.role === "Oraseas Inventory Manager") {
      // Oraseas roles can select any organization for inventory, but mainly Oraseas EE
      return organizations.filter(org => org.type === 'Warehouse'); // Only Oraseas Warehouse can create inventory records
    } else if (user.role === "Customer Admin" || user.role === "Customer User") {
      // Customers can only see and manage inventory for their own organization
      return organizations.filter(org => org.id === user.organization_id);
    }
    return [];
  };

  const filteredOrganizations = getFilteredOrganizations();


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
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.organization_id}
          onChange={handleChange}
          required
          disabled={loading || (user && (user.role === 'Customer Admin' || user.role === 'Customer User'))} // Disable for customers
        >
          <option value="">Select an Organization</option>
          {filteredOrganizations.map((org) => (
            <option key={org.id} value={org.id}>{org.name} ({org.type})</option>
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
        <label htmlFor="current_stock" className="block text-sm font-medium text-gray-700 mb-1">
          Current Stock
        </label>
        <input
          type="number"
          id="current_stock"
          name="current_stock"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.current_stock}
          onChange={handleChange}
          min="0"
          required
          disabled={loading}
        />
      </div>
      <div>
        <label htmlFor="minimum_stock_recommendation" className="block text-sm font-medium text-gray-700 mb-1">
          Minimum Stock Recommendation
        </label>
        <input
          type="number"
          id="minimum_stock_recommendation"
          name="minimum_stock_recommendation"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.minimum_stock_recommendation}
          onChange={handleChange}
          min="0"
          required
          disabled={loading}
        />
      </div>
      <div>
        <label htmlFor="reorder_threshold_set_by" className="block text-sm font-medium text-gray-700 mb-1">
          Reorder Threshold Set By
        </label>
        <select
          id="reorder_threshold_set_by"
          name="reorder_threshold_set_by"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          value={formData.reorder_threshold_set_by}
          onChange={handleChange}
          required
          disabled={loading}
        >
          <option value="user">User</option>
          <option value="system">System</option>
        </select>
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
          {loading ? 'Submitting...' : (initialData.id ? 'Update Inventory' : 'Create Inventory')}
        </button>
      </div>
    </form>
  );
}

export default InventoryForm;
