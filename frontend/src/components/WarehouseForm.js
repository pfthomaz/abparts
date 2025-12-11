// frontend/src/components/WarehouseForm.js

import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import { organizationsService } from '../services/organizationsService';

const WarehouseForm = ({ warehouse, onSubmit, onCancel, loading = false }) => {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    name: '',
    organization_id: '',
    location: '',
    description: '',
    is_active: true
  });
  const [organizations, setOrganizations] = useState([]);
  const [loadingOrganizations, setLoadingOrganizations] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchOrganizations();

    if (warehouse) {
      setFormData({
        name: warehouse.name || '',
        organization_id: warehouse.organization_id || '',
        location: warehouse.location || '',
        description: warehouse.description || '',
        is_active: warehouse.is_active !== undefined ? warehouse.is_active : true
      });
    } else {
      // For new warehouses, default to user's organization if not super_admin
      if (user?.role !== 'super_admin' && user?.organization_id) {
        setFormData(prev => ({
          ...prev,
          organization_id: user.organization_id
        }));
      }
    }
  }, [warehouse, user]);

  const fetchOrganizations = async () => {
    setLoadingOrganizations(true);
    try {
      const data = await organizationsService.getOrganizations();
      setOrganizations(data);
    } catch (err) {
      setError('Failed to fetch organizations');
      console.error('Failed to fetch organizations:', err);
    } finally {
      setLoadingOrganizations(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!formData.name.trim()) {
      setError('Warehouse name is required');
      return;
    }

    if (!formData.organization_id) {
      setError('Organization is required');
      return;
    }

    onSubmit(formData);
  };

  // Filter organizations based on user role
  const availableOrganizations = user?.role === 'super_admin'
    ? organizations
    : organizations.filter(org => org.id === user?.organization_id);

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
          Warehouse Name *
        </label>
        <input
          type="text"
          id="name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter warehouse name"
          required
          disabled={loading}
        />
      </div>

      <div>
        <label htmlFor="organization_id" className="block text-sm font-medium text-gray-700 mb-1">
          Organization *
        </label>
        <select
          id="organization_id"
          name="organization_id"
          value={formData.organization_id}
          onChange={handleChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          required
          disabled={loading || loadingOrganizations || user?.role !== 'super_admin'}
        >
          <option value="">Select an organization</option>
          {availableOrganizations.map(org => (
            <option key={org.id} value={org.id}>
              {org.name} ({org.organization_type})
            </option>
          ))}
        </select>
        {user?.role !== 'super_admin' && (
          <p className="text-sm text-gray-500 mt-1">
            You can only create warehouses in your organization
          </p>
        )}
      </div>

      <div>
        <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-1">
          Location
        </label>
        <input
          type="text"
          id="location"
          name="location"
          value={formData.location}
          onChange={handleChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter warehouse location/address"
          disabled={loading}
        />
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
          Description
        </label>
        <textarea
          id="description"
          name="description"
          value={formData.description}
          onChange={handleChange}
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter warehouse description"
          disabled={loading}
        />
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          id="is_active"
          name="is_active"
          checked={formData.is_active}
          onChange={handleChange}
          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          disabled={loading}
        />
        <label htmlFor="is_active" className="ml-2 block text-sm text-gray-700">
          Active warehouse
        </label>
      </div>

      <div className="flex justify-end space-x-3 pt-4">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          disabled={loading}
        >
          Cancel
        </button>
        <button
          type="submit"
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          disabled={loading}
        >
          {loading ? 'Saving...' : warehouse ? 'Update Warehouse' : 'Create Warehouse'}
        </button>
      </div>
    </form>
  );
};

export default WarehouseForm;