// frontend/src/components/InventoryForm.js

import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import { processError } from '../utils/errorHandling';

function InventoryForm({ organizations = [], parts = [], warehouses = [], initialData = {}, onSubmit, onClose, isEditMode = false }) {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    warehouse_id: '',
    part_id: '',
    current_stock: 0,
    minimum_stock_recommendation: 0,
    unit_of_measure: '',
    reorder_threshold_set_by: 'user', // Default value
    // No spread of initialData here, handled by useEffect
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const defaultData = {
      warehouse_id: '',
      part_id: '',
      current_stock: 0,
      minimum_stock_recommendation: 0,
      unit_of_measure: '',
      reorder_threshold_set_by: 'user',
    };

    let effectiveInitialData = { ...defaultData, ...initialData };

    setFormData(effectiveInitialData);

  }, [initialData, user, organizations, isEditMode]);

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    let newValue = type === 'number' ? parseFloat(value) || 0 : value;

    setFormData((prevData) => {
      const newData = {
        ...prevData,
        [name]: newValue,
      };

      // Auto-populate unit_of_measure when part is selected
      if (name === 'part_id' && value) {
        const selectedPart = parts.find(part => part.id === value);
        if (selectedPart && selectedPart.unit_of_measure) {
          newData.unit_of_measure = selectedPart.unit_of_measure;
        }
      }

      return newData;
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Ensure numerical fields are numbers, even if optional
      const dataToSend = {
        ...formData,
        current_stock: parseFloat(formData.current_stock),
        minimum_stock_recommendation: parseFloat(formData.minimum_stock_recommendation),
      };

      await onSubmit(dataToSend);
      onClose(); // Close modal on successful submission
    } catch (err) {
      const errorMessage = processError(err);
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Filter warehouses based on user role
  const getFilteredWarehouses = () => {
    if (!user || !Array.isArray(warehouses)) return [];

    // Super Admin can see all warehouses
    if (user.role === "super_admin") {
      return warehouses;
    }

    // Filter warehouses by user's organization
    return warehouses.filter(warehouse => warehouse.organization_id === user.organization_id);
  };

  const filteredWarehouses = getFilteredWarehouses();


  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Error:</strong>
          <span className="block sm:inline ml-2">{error}</span>
        </div>
      )}
      <div>
        <label htmlFor="warehouse_id" className="block text-sm font-medium text-gray-700 mb-1">
          Warehouse
        </label>
        <select
          id="warehouse_id"
          name="warehouse_id"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 bg-gray-50"
          value={formData.warehouse_id}
          onChange={handleChange}
          required
          disabled={loading || isEditMode}
        >
          <option value="">Select a Warehouse</option>
          {filteredWarehouses.map((warehouse) => (
            <option key={warehouse.id} value={warehouse.id}>
              {warehouse.name}
            </option>
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
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 bg-gray-50"
          value={formData.part_id}
          onChange={handleChange}
          required
          disabled={loading || isEditMode}
        >
          <option value="">Select a Part</option>
          {Array.isArray(parts) && parts.map((part) => (
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
          step="0.001"
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
          step="0.001"
          required
          disabled={loading}
        />
      </div>
      <div>
        <label htmlFor="unit_of_measure" className="block text-sm font-medium text-gray-700 mb-1">
          Unit of Measure
        </label>
        <input
          type="text"
          id="unit_of_measure"
          name="unit_of_measure"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 bg-gray-100"
          value={formData.unit_of_measure}
          onChange={handleChange}
          required
          disabled={loading || !formData.part_id}
          placeholder="Select a part to auto-fill"
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
