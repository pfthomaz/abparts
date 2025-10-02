// frontend/src/components/WarehouseStockAdjustmentForm.js

import React, { useState, useEffect } from 'react';
import { partsService } from '../services/partsService';
import { inventoryService } from '../services/inventoryService';

const WarehouseStockAdjustmentForm = ({ warehouseId, warehouse, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    part_id: '',
    quantity_change: '',
    reason: '',
    notes: ''
  });
  const [parts, setParts] = useState([]);
  const [warehouseInventory, setWarehouseInventory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    if (warehouseId) {
      fetchParts();
      fetchWarehouseInventory();
    }
  }, [warehouseId]);

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

  const fetchWarehouseInventory = async () => {
    try {
      const data = await inventoryService.getWarehouseInventory(warehouseId);
      setWarehouseInventory(data);
    } catch (err) {
      console.error('Failed to fetch warehouse inventory:', err);
      setWarehouseInventory([]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const quantityChange = parseFloat(formData.quantity_change);
    if (isNaN(quantityChange)) {
      setError('Quantity change must be a valid number');
      setLoading(false);
      return;
    }

    // Check if negative adjustment would result in negative stock
    if (quantityChange < 0) {
      const currentStock = getCurrentStock(formData.part_id);
      if (Math.abs(quantityChange) > currentStock) {
        setError(`Cannot reduce stock by ${Math.abs(quantityChange)}. Current stock: ${currentStock}`);
        setLoading(false);
        return;
      }
    }

    try {
      const submitData = {
        ...formData,
        quantity_change: quantityChange
      };

      await onSubmit(submitData);

      // Immediately update local state to reflect the change
      setWarehouseInventory(prevInventory =>
        prevInventory.map(item =>
          item.part_id === formData.part_id
            ? { ...item, current_stock: (parseFloat(item.current_stock) + quantityChange).toString() }
            : item
        )
      );

      // Also refresh from server to ensure consistency
      setTimeout(async () => {
        await fetchWarehouseInventory();
      }, 500);

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

  const getCurrentStock = (partId) => {
    const inventoryItem = warehouseInventory.find(item => item.part_id === partId);
    return inventoryItem ? parseFloat(inventoryItem.current_stock) : 0;
  };

  const getPartDetails = (partId) => {
    if (!Array.isArray(parts)) {
      return null;
    }
    return parts.find(p => p.id === partId);
  };

  const filteredParts = Array.isArray(parts) ? parts.filter(part =>
    part.part_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
    part.name.toLowerCase().includes(searchTerm.toLowerCase())
  ) : [];

  const reasonOptions = [
    'Stocktake adjustment',
    'Damaged goods',
    'Expired items',
    'Found items',
    'Lost items',
    'Transfer correction',
    'System error correction',
    'Initial stock entry',
    'Return to vendor',
    'Customer return - resalable',
    'Customer return - damaged',
    'Other'
  ];

  return (
    <div className="space-y-4">
      <div className="bg-blue-50 p-4 rounded-lg">
        <h3 className="text-lg font-medium text-blue-900">
          Stock Adjustment
        </h3>
        <p className="text-sm text-blue-700 mt-1">
          Warehouse: {warehouse?.name || 'Unknown Warehouse'}
          {warehouse?.location && ` - ${warehouse.location}`}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded" role="alert">
            <span>{error}</span>
          </div>
        )}

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
            {filteredParts.map((part) => {
              const currentStock = getCurrentStock(part.id);
              return (
                <option key={part.id} value={part.id}>
                  {part.part_number} - {part.name} (Current: {currentStock} {part.unit_of_measure})
                </option>
              );
            })}
          </select>
        </div>

        {formData.part_id && (
          <div className="bg-gray-50 p-3 rounded-md">
            <p className="text-sm text-gray-700">
              <span className="font-medium">Current Stock:</span> {getCurrentStock(formData.part_id)} {getPartDetails(formData.part_id)?.unit_of_measure}
            </p>
          </div>
        )}

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
          {formData.part_id && formData.quantity_change && (
            <p className="text-xs text-blue-600 mt-1">
              New stock level will be: {getCurrentStock(formData.part_id) + parseFloat(formData.quantity_change || 0)} {getPartDetails(formData.part_id)?.unit_of_measure}
            </p>
          )}
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
            {loading ? 'Creating Adjustment...' : 'Create Adjustment'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default WarehouseStockAdjustmentForm;