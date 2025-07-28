// frontend/src/components/InventoryTransferForm.js

import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import { warehouseService } from '../services/warehouseService';
import { partsService } from '../services/partsService';
import { inventoryService } from '../services/inventoryService';
import WarehouseSelector from './WarehouseSelector';
import { safeFilter } from '../utils/inventoryValidation';

const InventoryTransferForm = ({ onSubmit, onCancel, initialData = {} }) => {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    from_warehouse_id: '',
    to_warehouse_id: '',
    part_id: '',
    quantity: '',
    notes: '',
    ...initialData
  });
  const [parts, setParts] = useState([]);
  const [fromWarehouseInventory, setFromWarehouseInventory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchParts();
  }, []);

  useEffect(() => {
    if (formData.from_warehouse_id) {
      fetchWarehouseInventory(formData.from_warehouse_id);
    } else {
      setFromWarehouseInventory([]);
    }
  }, [formData.from_warehouse_id]);

  const fetchParts = async () => {
    try {
      const data = await partsService.getParts({ limit: 200 });
      setParts(data);
    } catch (err) {
      setError('Failed to fetch parts');
      console.error('Failed to fetch parts:', err);
    }
  };

  const fetchWarehouseInventory = async (warehouseId) => {
    try {
      const data = await inventoryService.getWarehouseInventory(warehouseId);
      setFromWarehouseInventory(data);
    } catch (err) {
      console.error('Failed to fetch warehouse inventory:', err);
      setFromWarehouseInventory([]);
    }
  };

  const validateQuantity = (value, availableStock) => {
    const quantity = parseFloat(value);
    if (isNaN(quantity) || quantity <= 0) {
      return { valid: false, error: 'Quantity must be a positive number' };
    }

    // Check decimal precision (max 3 decimal places)
    const decimalPlaces = (value.toString().split('.')[1] || '').length;
    if (decimalPlaces > 3) {
      return { valid: false, error: 'Quantity precision cannot exceed 3 decimal places' };
    }

    if (quantity > availableStock) {
      return { valid: false, error: `Insufficient stock. Available: ${availableStock}` };
    }
    return { valid: true };
  };

  const handleTransferError = (error) => {
    // Handle different types of errors
    if (error.response?.data?.detail) {
      return error.response.data.detail;
    }
    if (error.response?.data?.message) {
      return error.response.data.message;
    }
    if (error.message) {
      return error.message;
    }
    return 'Failed to transfer inventory. Please try again.';
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Enhanced validation
    if (formData.from_warehouse_id === formData.to_warehouse_id) {
      setError('Source and destination warehouses must be different');
      setLoading(false);
      return;
    }

    if (!formData.from_warehouse_id || !formData.to_warehouse_id || !formData.part_id) {
      setError('Please select all required fields');
      setLoading(false);
      return;
    }

    // Get available stock for validation
    const inventoryItem = fromWarehouseInventory.find(item => item.part_id === formData.part_id);
    const availableStock = inventoryItem ? parseFloat(inventoryItem.current_stock) : 0;

    // Validate quantity with enhanced checks
    const quantityValidation = validateQuantity(formData.quantity, availableStock);
    if (!quantityValidation.valid) {
      setError(quantityValidation.error);
      setLoading(false);
      return;
    }

    const quantity = parseFloat(formData.quantity);

    try {
      const submitData = {
        ...formData,
        quantity: quantity
      };

      await onSubmit(submitData);
    } catch (err) {
      const errorMessage = handleTransferError(err);
      setError(errorMessage);
      console.error('Transfer error:', err);
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

  const handleFromWarehouseChange = (warehouseId) => {
    setFormData(prev => ({
      ...prev,
      from_warehouse_id: warehouseId,
      part_id: '' // Reset part selection when warehouse changes
    }));
  };

  const handleToWarehouseChange = (warehouseId) => {
    setFormData(prev => ({
      ...prev,
      to_warehouse_id: warehouseId
    }));
  };

  const getAvailableStock = (partId) => {
    const inventoryItem = fromWarehouseInventory.find(item => item.part_id === partId);
    return inventoryItem ? parseFloat(inventoryItem.current_stock) : 0;
  };

  const getPartDetails = (partId) => {
    return parts.find(p => p.id === partId);
  };

  const filteredParts = safeFilter(parts, part => {
    try {
      return part &&
        (part.part_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
          part.name?.toLowerCase().includes(searchTerm.toLowerCase()));
    } catch (error) {
      console.error('Error filtering parts:', error, part);
      return false;
    }
  }, []);

  // Only show parts that have inventory in the selected from warehouse
  const availableParts = safeFilter(filteredParts, part => {
    try {
      if (!part) return false;
      const stock = getAvailableStock(part.id);
      return stock > 0;
    } catch (error) {
      console.error('Error checking available parts:', error, part);
      return false;
    }
  }, []);

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded" role="alert">
          <span>{error}</span>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            From Warehouse *
          </label>
          <WarehouseSelector
            selectedWarehouseId={formData.from_warehouse_id}
            onWarehouseChange={handleFromWarehouseChange}
            placeholder="Select source warehouse"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            To Warehouse *
          </label>
          <WarehouseSelector
            selectedWarehouseId={formData.to_warehouse_id}
            onWarehouseChange={handleToWarehouseChange}
            placeholder="Select destination warehouse"
          />
        </div>
      </div>

      {formData.from_warehouse_id && (
        <>
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
              size={Math.min(availableParts.length + 1, 8)}
            >
              <option value="">Select a part</option>
              {availableParts.map((part) => {
                const stock = getAvailableStock(part.id);
                return (
                  <option key={part.id} value={part.id}>
                    {part.part_number} - {part.name} (Available: {stock} {part.unit_of_measure})
                  </option>
                );
              })}
            </select>
            {availableParts.length === 0 && formData.from_warehouse_id && (
              <p className="text-sm text-gray-500 mt-1">
                No parts with available stock in selected warehouse
              </p>
            )}
          </div>

          {formData.part_id && (
            <div>
              <label htmlFor="quantity" className="block text-sm font-medium text-gray-700 mb-1">
                Quantity *
              </label>
              <input
                type="number"
                step="0.001"
                id="quantity"
                name="quantity"
                value={formData.quantity}
                onChange={handleChange}
                required
                max={getAvailableStock(formData.part_id)}
                placeholder={`Max: ${getAvailableStock(formData.part_id)}`}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="text-xs text-gray-500 mt-1">
                Available stock: {getAvailableStock(formData.part_id)} {getPartDetails(formData.part_id)?.unit_of_measure}
              </p>
            </div>
          )}
        </>
      )}

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
          placeholder="Optional notes about this transfer..."
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
          disabled={loading || !formData.from_warehouse_id || !formData.to_warehouse_id || !formData.part_id}
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
        >
          {loading ? 'Creating Transfer...' : 'Create Transfer'}
        </button>
      </div>
    </form>
  );
};

export default InventoryTransferForm;