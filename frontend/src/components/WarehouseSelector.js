// frontend/src/components/WarehouseSelector.js

import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import { warehouseService } from '../services/warehouseService';

const WarehouseSelector = ({
  selectedWarehouseId,
  onWarehouseChange,
  organizationId = null,
  includeInactive = false,
  className = '',
  placeholder = 'Select a warehouse'
}) => {
  const { user } = useAuth();
  const [warehouses, setWarehouses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchWarehouses();
  }, [organizationId, includeInactive, user]);

  const fetchWarehouses = async () => {
    setLoading(true);
    setError('');
    try {
      const filters = {
        include_inactive: includeInactive
      };

      // If organizationId is provided, use it; otherwise use user's organization for non-super_admin
      if (organizationId) {
        filters.organization_id = organizationId;
      } else if (user?.role !== 'super_admin' && user?.organization_id) {
        filters.organization_id = user.organization_id;
      }

      const data = await warehouseService.getWarehouses(filters);
      setWarehouses(data);
    } catch (err) {
      setError('Failed to fetch warehouses');
      console.error('Failed to fetch warehouses:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const warehouseId = e.target.value;
    const selectedWarehouse = warehouses.find(w => w.id === warehouseId);
    onWarehouseChange(warehouseId, selectedWarehouse);
  };

  if (error) {
    return (
      <div className="text-red-600 text-sm">
        {error}
      </div>
    );
  }

  return (
    <div className={className}>
      <select
        value={selectedWarehouseId || ''}
        onChange={handleChange}
        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        disabled={loading}
      >
        <option value="">{loading ? 'Loading...' : placeholder}</option>
        {warehouses.map(warehouse => (
          <option key={warehouse.id} value={warehouse.id}>
            {warehouse.name}
            {warehouse.location && ` - ${warehouse.location}`}
            {!warehouse.is_active && ' (Inactive)'}
          </option>
        ))}
      </select>

      {warehouses.length === 0 && !loading && (
        <p className="text-sm text-gray-500 mt-1">
          No warehouses available
        </p>
      )}
    </div>
  );
};

export default WarehouseSelector;