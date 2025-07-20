// frontend/src/components/WarehouseCapacityManagement.js

import React, { useState, useEffect } from 'react';
import { warehouseService } from '../services/warehouseService';

const WarehouseCapacityManagement = ({ warehouse, onUpdate }) => {
  const [capacityData, setCapacityData] = useState({
    max_capacity: warehouse?.max_capacity || '',
    current_utilization: warehouse?.current_utilization || 0,
    capacity_unit: warehouse?.capacity_unit || 'cubic_meters'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    if (warehouse) {
      setCapacityData({
        max_capacity: warehouse.max_capacity || '',
        current_utilization: warehouse.current_utilization || 0,
        capacity_unit: warehouse.capacity_unit || 'cubic_meters'
      });
    }
  }, [warehouse]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setCapacityData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSave = async () => {
    setLoading(true);
    setError('');
    try {
      const updatedWarehouse = await warehouseService.updateWarehouse(warehouse.id, {
        ...warehouse,
        max_capacity: parseFloat(capacityData.max_capacity) || null,
        capacity_unit: capacityData.capacity_unit
      });

      setIsEditing(false);
      if (onUpdate) {
        onUpdate(updatedWarehouse);
      }
    } catch (err) {
      setError('Failed to update warehouse capacity');
      console.error('Failed to update warehouse capacity:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setCapacityData({
      max_capacity: warehouse?.max_capacity || '',
      current_utilization: warehouse?.current_utilization || 0,
      capacity_unit: warehouse?.capacity_unit || 'cubic_meters'
    });
    setIsEditing(false);
    setError('');
  };

  const getUtilizationPercentage = () => {
    if (!capacityData.max_capacity || capacityData.max_capacity === 0) {
      return 0;
    }
    return Math.min((capacityData.current_utilization / capacityData.max_capacity) * 100, 100);
  };

  const getUtilizationColor = (percentage) => {
    if (percentage >= 90) return 'bg-red-500';
    if (percentage >= 75) return 'bg-orange-500';
    if (percentage >= 50) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const utilizationPercentage = getUtilizationPercentage();

  return (
    <div className="bg-white p-6 rounded-lg border border-gray-200">
      <div className="flex justify-between items-center mb-4">
        <h4 className="text-lg font-medium text-gray-900">Warehouse Capacity</h4>
        {!isEditing && (
          <button
            onClick={() => setIsEditing(true)}
            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            Edit Capacity
          </button>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded mb-4 text-sm">
          {error}
        </div>
      )}

      <div className="space-y-4">
        {/* Capacity Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Maximum Capacity
            </label>
            {isEditing ? (
              <div className="flex space-x-2">
                <input
                  type="number"
                  name="max_capacity"
                  value={capacityData.max_capacity}
                  onChange={handleInputChange}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter capacity"
                  min="0"
                  step="0.01"
                />
                <select
                  name="capacity_unit"
                  value={capacityData.capacity_unit}
                  onChange={handleInputChange}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="cubic_meters">m³</option>
                  <option value="square_meters">m²</option>
                  <option value="pallets">Pallets</option>
                  <option value="shelves">Shelves</option>
                  <option value="units">Units</option>
                </select>
              </div>
            ) : (
              <div className="text-lg font-semibold text-gray-900">
                {capacityData.max_capacity ?
                  `${parseFloat(capacityData.max_capacity).toLocaleString()} ${capacityData.capacity_unit}` :
                  'Not specified'
                }
              </div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Current Utilization
            </label>
            <div className="text-lg font-semibold text-gray-900">
              {capacityData.current_utilization.toLocaleString()} {capacityData.capacity_unit}
            </div>
          </div>
        </div>

        {/* Utilization Bar */}
        {capacityData.max_capacity && (
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">Utilization</span>
              <span className="text-sm font-medium text-gray-900">
                {utilizationPercentage.toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className={`h-3 rounded-full transition-all duration-300 ${getUtilizationColor(utilizationPercentage)}`}
                style={{ width: `${utilizationPercentage}%` }}
              ></div>
            </div>
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>0</span>
              <span>{parseFloat(capacityData.max_capacity).toLocaleString()}</span>
            </div>
          </div>
        )}

        {/* Capacity Status */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-sm font-medium text-gray-500">Available Space</div>
            <div className="text-lg font-bold text-green-600">
              {capacityData.max_capacity ?
                (parseFloat(capacityData.max_capacity) - capacityData.current_utilization).toLocaleString() :
                'N/A'
              }
            </div>
          </div>

          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-sm font-medium text-gray-500">Utilization Status</div>
            <div className={`text-lg font-bold ${utilizationPercentage >= 90 ? 'text-red-600' :
                utilizationPercentage >= 75 ? 'text-orange-600' :
                  utilizationPercentage >= 50 ? 'text-yellow-600' :
                    'text-green-600'
              }`}>
              {utilizationPercentage >= 90 ? 'Critical' :
                utilizationPercentage >= 75 ? 'High' :
                  utilizationPercentage >= 50 ? 'Medium' :
                    'Low'}
            </div>
          </div>

          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-sm font-medium text-gray-500">Efficiency</div>
            <div className="text-lg font-bold text-blue-600">
              {utilizationPercentage > 0 ? `${utilizationPercentage.toFixed(0)}%` : 'N/A'}
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        {isEditing && (
          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
            <button
              onClick={handleCancel}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              disabled={loading}
            >
              {loading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default WarehouseCapacityManagement;