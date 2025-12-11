import React, { useState, useEffect } from 'react';
import { createChecklistItem, updateChecklistItem } from '../services/maintenanceProtocolsService';

const ChecklistItemForm = ({ protocolId, item, existingItems, onSave, onCancel }) => {
  const [formData, setFormData] = useState({
    item_description: '',
    item_type: 'check',
    item_category: '',
    part_id: null,
    estimated_quantity: '',
    is_critical: false,
    estimated_duration_minutes: '',
    notes: ''
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (item) {
      setFormData({
        item_description: item.item_description || '',
        item_type: item.item_type || 'check',
        item_category: item.item_category || '',
        part_id: item.part_id || null,
        estimated_quantity: item.estimated_quantity || '',
        is_critical: item.is_critical ?? false,
        estimated_duration_minutes: item.estimated_duration_minutes || '',
        notes: item.notes || ''
      });
    }
  }, [item]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.item_description.trim()) {
      alert('Description is required');
      return;
    }

    setLoading(true);
    try {
      const submitData = {
        ...formData,
        estimated_quantity: formData.estimated_quantity ? parseFloat(formData.estimated_quantity) : null,
        estimated_duration_minutes: formData.estimated_duration_minutes ? parseInt(formData.estimated_duration_minutes) : null,
        item_category: formData.item_category || null,
        part_id: formData.part_id || null
      };

      if (item) {
        // Update existing item
        await updateChecklistItem(protocolId, item.id, submitData);
      } else {
        // Create new item - calculate next order
        const nextOrder = existingItems.length > 0 
          ? Math.max(...existingItems.map(i => i.item_order)) + 1 
          : 1;
        submitData.item_order = nextOrder;
        await createChecklistItem(protocolId, submitData);
      }

      onSave();
    } catch (err) {
      alert(`Failed to save checklist item: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        {item ? 'Edit Checklist Item' : 'Add Checklist Item'}
      </h3>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description *
          </label>
          <textarea
            name="item_description"
            value={formData.item_description}
            onChange={handleChange}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., Check oil level and top up if needed"
            required
            disabled={loading}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Item Type *
            </label>
            <select
              name="item_type"
              value={formData.item_type}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
              disabled={loading}
            >
              <option value="check">Check</option>
              <option value="service">Service</option>
              <option value="replacement">Replacement</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Category
            </label>
            <input
              type="text"
              name="item_category"
              value={formData.item_category}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., Electrical, Mechanical"
              disabled={loading}
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Estimated Duration (minutes)
            </label>
            <input
              type="number"
              name="estimated_duration_minutes"
              value={formData.estimated_duration_minutes}
              onChange={handleChange}
              min="0"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., 15"
              disabled={loading}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Estimated Quantity
            </label>
            <input
              type="number"
              name="estimated_quantity"
              value={formData.estimated_quantity}
              onChange={handleChange}
              step="0.001"
              min="0"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., 2.5"
              disabled={loading}
            />
          </div>
        </div>

        <div className="flex items-center">
          <input
            type="checkbox"
            id="is_critical"
            name="is_critical"
            checked={formData.is_critical}
            onChange={handleChange}
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            disabled={loading}
          />
          <label htmlFor="is_critical" className="ml-2 text-sm text-gray-700">
            Mark as Critical (must be completed)
          </label>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Notes
          </label>
          <textarea
            name="notes"
            value={formData.notes}
            onChange={handleChange}
            rows={2}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Additional instructions or information"
            disabled={loading}
          />
        </div>

        <div className="flex justify-end space-x-3 pt-4 border-t">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            disabled={loading}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:bg-gray-400"
            disabled={loading}
          >
            {loading ? 'Saving...' : (item ? 'Update Item' : 'Add Item')}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChecklistItemForm;
