// frontend/src/components/ProtocolForm.js

import React, { useState, useEffect } from 'react';
import { createProtocol, updateProtocol } from '../services/maintenanceProtocolsService';

const ProtocolForm = ({ protocol, onSave, onCancel }) => {
  const [formData, setFormData] = useState({
    name: '',
    protocol_type: 'daily',
    service_interval_hours: '',
    is_recurring: false,
    machine_model: '',
    description: '',
    is_active: true,
    display_order: 0
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (protocol) {
      setFormData({
        name: protocol.name || '',
        protocol_type: protocol.protocol_type || 'daily',
        service_interval_hours: protocol.service_interval_hours || '',
        is_recurring: protocol.is_recurring || false,
        machine_model: protocol.machine_model || '',
        description: protocol.description || '',
        is_active: protocol.is_active !== undefined ? protocol.is_active : true,
        display_order: protocol.display_order || 0
      });
    }
  }, [protocol]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);

    try {
      const data = {
        ...formData,
        service_interval_hours: formData.service_interval_hours ? parseFloat(formData.service_interval_hours) : null,
        machine_model: formData.machine_model || null
      };

      if (protocol) {
        await updateProtocol(protocol.id, data);
      } else {
        await createProtocol(data);
      }

      onSave();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-2xl">
      <h2 className="text-2xl font-bold mb-6">
        {protocol ? 'Edit Protocol' : 'Create New Protocol'}
      </h2>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Protocol Name *
          </label>
          <input
            type="text"
            required
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            className="w-full border border-gray-300 rounded-md px-3 py-2"
            placeholder="e.g., Daily Start of Day"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Protocol Type *
          </label>
          <select
            required
            value={formData.protocol_type}
            onChange={(e) => setFormData({ ...formData, protocol_type: e.target.value })}
            className="w-full border border-gray-300 rounded-md px-3 py-2"
          >
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="scheduled">Scheduled (Hours-based)</option>
            <option value="custom">Custom</option>
          </select>
        </div>

        {formData.protocol_type === 'scheduled' && (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Service Hours *
              </label>
              <input
                type="number"
                step="0.01"
                required={formData.protocol_type === 'scheduled'}
                value={formData.service_interval_hours}
                onChange={(e) => setFormData({ ...formData, service_interval_hours: e.target.value })}
                className="w-full border border-gray-300 rounded-md px-3 py-2"
                placeholder="e.g., 50 or 250"
              />
              <p className="text-xs text-gray-500 mt-1">
                Number of operating hours for this service
              </p>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="is_recurring"
                checked={formData.is_recurring}
                onChange={(e) => setFormData({ ...formData, is_recurring: e.target.checked })}
                className="h-4 w-4 text-blue-600 border-gray-300 rounded"
              />
              <label htmlFor="is_recurring" className="ml-2 text-sm text-gray-700">
                Recurring service (repeat every {formData.service_interval_hours || 'N'} hours)
              </label>
            </div>
            <p className="text-xs text-gray-500 -mt-2">
              Uncheck for one-time services (e.g., 50h initial service). Check for recurring services (e.g., every 250h).
            </p>
          </>
        )}

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Machine Model
          </label>
          <select
            value={formData.machine_model}
            onChange={(e) => setFormData({ ...formData, machine_model: e.target.value })}
            className="w-full border border-gray-300 rounded-md px-3 py-2"
          >
            <option value="">All Models (Universal)</option>
            <option value="V3.1B">V3.1B</option>
            <option value="V4.0">V4.0</option>
          </select>
          <p className="text-xs text-gray-500 mt-1">
            Leave empty to apply to all machine models
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            rows={3}
            className="w-full border border-gray-300 rounded-md px-3 py-2"
            placeholder="Brief description of this protocol..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Display Order
          </label>
          <input
            type="number"
            value={formData.display_order}
            onChange={(e) => setFormData({ ...formData, display_order: parseInt(e.target.value) || 0 })}
            className="w-full border border-gray-300 rounded-md px-3 py-2"
            placeholder="0"
          />
          <p className="text-xs text-gray-500 mt-1">
            Lower numbers appear first
          </p>
        </div>

        <div className="flex items-center">
          <input
            type="checkbox"
            id="is_active"
            checked={formData.is_active}
            onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
            className="h-4 w-4 text-blue-600 border-gray-300 rounded"
          />
          <label htmlFor="is_active" className="ml-2 text-sm text-gray-700">
            Active (protocol is available for use)
          </label>
        </div>

        <div className="flex gap-3 pt-4">
          <button
            type="submit"
            disabled={saving}
            className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:bg-gray-400"
          >
            {saving ? 'Saving...' : (protocol ? 'Update Protocol' : 'Create Protocol')}
          </button>
          <button
            type="button"
            onClick={onCancel}
            className="bg-gray-200 text-gray-700 px-6 py-2 rounded-md hover:bg-gray-300"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};

export default ProtocolForm;
