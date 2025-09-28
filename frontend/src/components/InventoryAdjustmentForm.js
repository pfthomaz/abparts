// frontend/src/components/InventoryAdjustmentForm.js

import React, { useState, useEffect } from 'react';
import { organizationsService } from '../services/organizationsService';
import { partsService } from '../services/partsService';
import { useAuth } from '../AuthContext';

const InventoryAdjustmentForm = ({ onSubmit, onCancel }) => {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    warehouse_id: '',
    part_id: '',
    quantity_change: '',
    reason: '',
    notes: ''
  });
  const [warehouses, setWarehouses] = useState([]);
  const [parts, setParts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchWarehouses();
    fetchParts();
  }, []);

  const fetchWarehouses = async () => {
    try {
      const organizationId = user?.role === 'super_admin' ? null : user?.organization_id;
      const data = await organizationsService.getWarehouses(organizationId);
      setWarehouses(data);
    } catch (err) {
      setError('Failed to fetch warehouses');
      console.error('Failed to fetch warehouses:', err);
    }
  };

  const fetchParts = async () => {
    try {
      const response = await partsService.getPartsWithInventory({ limit: 1000 });
      // Handle paginated response format
      const partsData = response?.items || response || [];
      setParts(Array.isArray(partsData) ? partsData : []);
    } catch (err) {
      setError('Failed to fetch parts');
      console.error('Failed to fetch parts:', err);
      setParts([]); // Ensure parts is always an array
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const submitData = {
        ...formData,
        quantity_change: parseFloat(formData.quantity_change)
      };

      await onSubmit(submitData);
    } catch (err) {
      setError(err.message || 'Failed to create adjustment');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const filteredParts = Array.isArray(parts) ? parts.filter(part =>
    part.part_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
    part.name.toLowerCase().includes(searchTerm.toLowerCase())
  ) : [];

  const reasonOptions = [
    'Damaged goods',
    'Expired items',
    'Found items',
    'Lost items',
    'Stocktake adjustment',
    'Transfer correction',
    'System error correction',
    'Other'
  ];

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded" role="alert">
          <span>{error}</span>
        </div>
      )}

      <div>
        <label htmlFor="warehouse_id" className="block text-sm font-medium text-gray-700 mb-1">
          Warehouse *
        </label>
        <select
          id="warehouse_id"
          name="warehouse_id"
          value={formData.warehouse_id}
          onChange={handleChange}
          required
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">Select a warehouse</option>
          {warehouses.map((warehouse) => (
            <option key={warehouse.id} value={warehouse.id}>
              {warehouse.name} - {warehouse.location}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="part_search" className="block text-sm font-medium text-gray-700 mb-1">
          Search Parts
        </label>
        <input
          type="text"
          id="part_search"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Search by part number or name..."
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      <div>
        <label htmlFor="part_id" className="block text-sm font-medium text-gray-700 mb-1">
          Part *
        </label>
        <select
          id="part_id"
          name="part_id"
          value={formData.part_id}
          onChange={handleChange}
          required
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          size={Math.min(filteredParts.length + 1, 8)}
        >
          <option value="">Select a part</option>
          {filteredParts.map((part) => (
            <option key={part.id} value={part.id}>
              {part.part_number} - {part.name} ({part.unit_of_measure})
            </option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="quantity_change" className="block text-sm font-medium text-gray-700 mb-1">
          Quantity Change *
        </label>
        <input
          type="number"
          step="0.001"
          id="quantity_change"
          name="quantity_change"
          value={formData.quantity_change}
          onChange={handleChange}
          required
          placeholder="Enter positive for increase, negative for decrease"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <p className="text-xs text-gray-500 mt-1">
          Use positive numbers to increase inventory, negative numbers to decrease
        </p>
      </div>

      <div>
        <label htmlFor="reason" className="block text-sm font-medium text-gray-700 mb-1">
          Reason *
        </label>
        <select
          id="reason"
          name="reason"
          value={formData.reason}
          onChange={handleChange}
          required
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">Select a reason</option>
          {reasonOptions.map((reason) => (
            <option key={reason} value={reason}>
              {reason}
            </option>
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
          value={formData.notes}
          onChange={handleChange}
          rows={3}
          placeholder="Optional additional details about this adjustment..."
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      <div className="flex justify-end space-x-3 pt-4">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50"
        >
          {loading ? 'Creating...' : 'Create Adjustment'}
        </button>
      </div>
    </form>
  );
};

export default InventoryAdjustmentForm;