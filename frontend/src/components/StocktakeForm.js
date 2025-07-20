// frontend/src/components/StocktakeForm.js

import React, { useState, useEffect } from 'react';
import { organizationsService } from '../services/organizationsService';
import { useAuth } from '../AuthContext';

const StocktakeForm = ({ stocktake = null, onSubmit, onCancel }) => {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    warehouse_id: '',
    scheduled_date: '',
    notes: ''
  });
  const [warehouses, setWarehouses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchWarehouses();

    if (stocktake) {
      setFormData({
        warehouse_id: stocktake.warehouse_id || '',
        scheduled_date: stocktake.scheduled_date ?
          new Date(stocktake.scheduled_date).toISOString().slice(0, 16) : '',
        notes: stocktake.notes || ''
      });
    } else {
      // Set default scheduled date to tomorrow at 9 AM
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      tomorrow.setHours(9, 0, 0, 0);
      setFormData(prev => ({
        ...prev,
        scheduled_date: tomorrow.toISOString().slice(0, 16)
      }));
    }
  }, [stocktake]);

  const fetchWarehouses = async () => {
    try {
      // Get warehouses based on user's organization
      const organizationId = user?.role === 'super_admin' ? null : user?.organization_id;
      const data = await organizationsService.getWarehouses(organizationId);
      setWarehouses(data);
    } catch (err) {
      setError('Failed to fetch warehouses');
      console.error('Failed to fetch warehouses:', err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Convert scheduled_date to ISO string
      const submitData = {
        ...formData,
        scheduled_date: new Date(formData.scheduled_date).toISOString()
      };

      await onSubmit(submitData);
    } catch (err) {
      setError(err.message || 'Failed to save stocktake');
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
        <label htmlFor="scheduled_date" className="block text-sm font-medium text-gray-700 mb-1">
          Scheduled Date & Time *
        </label>
        <input
          type="datetime-local"
          id="scheduled_date"
          name="scheduled_date"
          value={formData.scheduled_date}
          onChange={handleChange}
          required
          min={new Date().toISOString().slice(0, 16)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
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
          placeholder="Optional notes about this stocktake..."
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
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
        >
          {loading ? 'Saving...' : (stocktake ? 'Update Stocktake' : 'Create Stocktake')}
        </button>
      </div>
    </form>
  );
};

export default StocktakeForm;