// frontend/src/components/CreateStockAdjustmentModal.js

import React, { useState, useEffect } from 'react';
import { partsService } from '../services/partsService';
import PartSearchSelector from './PartSearchSelector';

const CreateStockAdjustmentModal = ({ warehouses, onClose, onSubmit }) => {
  const [formData, setFormData] = useState({
    warehouse_id: '',
    adjustment_type: 'stock_take',
    reason: '',
    notes: '',
    items: []
  });
  const [parts, setParts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadParts();
  }, []);

  const loadParts = async () => {
    try {
      const data = await partsService.list();
      setParts(data);
    } catch (err) {
      setError('Failed to load parts');
    }
  };

  const handleAddItem = (part) => {
    // Check if part already added
    if (formData.items.some(item => item.part_id === part.id)) {
      setError('Part already added to this adjustment');
      return;
    }

    setFormData(prev => ({
      ...prev,
      items: [
        ...prev.items,
        {
          part_id: part.id,
          part_number: part.part_number,
          part_name: part.name,
          quantity_after: 0,
          reason: ''
        }
      ]
    }));
    setError(null);
  };

  const handleRemoveItem = (index) => {
    setFormData(prev => ({
      ...prev,
      items: prev.items.filter((_, i) => i !== index)
    }));
  };

  const handleItemChange = (index, field, value) => {
    setFormData(prev => ({
      ...prev,
      items: prev.items.map((item, i) => 
        i === index ? { ...item, [field]: value } : item
      )
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.warehouse_id) {
      setError('Please select a warehouse');
      return;
    }
    
    if (formData.items.length === 0) {
      setError('Please add at least one item');
      return;
    }

    // Validate all items have quantity_after
    const invalidItems = formData.items.filter(item => !item.quantity_after && item.quantity_after !== 0);
    if (invalidItems.length > 0) {
      setError('Please set quantity for all items');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Format data for API
      const submitData = {
        warehouse_id: formData.warehouse_id,
        adjustment_type: formData.adjustment_type,
        reason: formData.reason || null,
        notes: formData.notes || null,
        items: formData.items.map(item => ({
          part_id: item.part_id,
          quantity_after: parseFloat(item.quantity_after),
          reason: item.reason || null
        }))
      };

      await onSubmit(submitData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold">Create Stock Adjustment</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
          </div>

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            {/* Basic Info */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Warehouse *
                </label>
                <select
                  value={formData.warehouse_id}
                  onChange={(e) => setFormData(prev => ({ ...prev, warehouse_id: e.target.value }))}
                  className="w-full border border-gray-300 rounded px-3 py-2"
                  required
                >
                  <option value="">Select Warehouse</option>
                  {warehouses.map(wh => (
                    <option key={wh.id} value={wh.id}>{wh.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Adjustment Type *
                </label>
                <select
                  value={formData.adjustment_type}
                  onChange={(e) => setFormData(prev => ({ ...prev, adjustment_type: e.target.value }))}
                  className="w-full border border-gray-300 rounded px-3 py-2"
                  required
                >
                  <option value="stock_take">Stock Take</option>
                  <option value="damage">Damage</option>
                  <option value="loss">Loss</option>
                  <option value="found">Found</option>
                  <option value="correction">Correction</option>
                  <option value="return">Return</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Reason
              </label>
              <input
                type="text"
                value={formData.reason}
                onChange={(e) => setFormData(prev => ({ ...prev, reason: e.target.value }))}
                className="w-full border border-gray-300 rounded px-3 py-2"
                placeholder="Overall reason for this adjustment"
              />
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Notes
              </label>
              <textarea
                value={formData.notes}
                onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
                className="w-full border border-gray-300 rounded px-3 py-2"
                rows="3"
                placeholder="Additional notes"
              />
            </div>

            {/* Items Section */}
            <div className="mb-6">
              <div className="flex justify-between items-center mb-3">
                <h3 className="text-lg font-semibold">Items to Adjust *</h3>
              </div>

              {/* Add Part */}
              <div className="mb-4">
                <PartSearchSelector
                  parts={parts}
                  onSelect={handleAddItem}
                  placeholder="Search and add parts..."
                />
              </div>

              {/* Items List */}
              {formData.items.length === 0 ? (
                <div className="text-center py-8 text-gray-500 border-2 border-dashed border-gray-300 rounded">
                  No items added yet. Search and add parts above.
                </div>
              ) : (
                <div className="space-y-3">
                  {formData.items.map((item, index) => (
                    <div key={index} className="border border-gray-300 rounded p-4">
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <div className="font-medium">{item.part_number}</div>
                          <div className="text-sm text-gray-600">{item.part_name}</div>
                        </div>
                        <button
                          type="button"
                          onClick={() => handleRemoveItem(index)}
                          className="text-red-600 hover:text-red-800"
                        >
                          Remove
                        </button>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            New Quantity *
                          </label>
                          <input
                            type="number"
                            step="0.01"
                            value={item.quantity_after}
                            onChange={(e) => handleItemChange(index, 'quantity_after', e.target.value)}
                            className="w-full border border-gray-300 rounded px-3 py-2"
                            required
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Item Reason
                          </label>
                          <input
                            type="text"
                            value={item.reason}
                            onChange={(e) => handleItemChange(index, 'reason', e.target.value)}
                            className="w-full border border-gray-300 rounded px-3 py-2"
                            placeholder="Specific reason for this part"
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50"
                disabled={loading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
                disabled={loading}
              >
                {loading ? 'Creating...' : 'Create Adjustment'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default CreateStockAdjustmentModal;
