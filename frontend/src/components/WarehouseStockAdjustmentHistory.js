// frontend/src/components/WarehouseStockAdjustmentHistory.js

import React, { useState, useEffect, useCallback } from 'react';
import { inventoryService } from '../services/inventoryService';
import { partsService } from '../services/partsService';

const WarehouseStockAdjustmentHistory = ({ warehouseId, warehouse }) => {
  const [adjustments, setAdjustments] = useState([]);
  const [parts, setParts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0],
    reason: 'all',
    adjustment_type: 'all' // 'all', 'increase', 'decrease'
  });
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    if (warehouseId) {
      fetchData();
    }
  }, [warehouseId, filters, fetchData]);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const [adjustmentsData, partsData] = await Promise.all([
        inventoryService.getWarehouseStockAdjustments(warehouseId, filters),
        partsService.getParts({ limit: 200 })
      ]);

      setAdjustments(adjustmentsData);
      setParts(partsData);
    } catch (err) {
      setError('Failed to fetch adjustment history');
      console.error('Failed to fetch adjustment history:', err);
    } finally {
      setLoading(false);
    }
  }, [warehouseId, filters]);

  const getPartDetails = (partId) => {
    return parts.find(p => p.id === partId) || {};
  };

  const filteredAdjustments = adjustments.filter(adjustment => {
    const part = getPartDetails(adjustment.part_id);
    const matchesSearch = !searchTerm ||
      part.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      part.part_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      adjustment.reason?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      adjustment.notes?.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesType = filters.adjustment_type === 'all' ||
      (filters.adjustment_type === 'increase' && parseFloat(adjustment.quantity_change) > 0) ||
      (filters.adjustment_type === 'decrease' && parseFloat(adjustment.quantity_change) < 0);

    return matchesSearch && matchesType;
  });

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatNumber = (value) => {
    return new Intl.NumberFormat('en-US').format(value || 0);
  };

  const getAdjustmentType = (quantityChange) => {
    const change = parseFloat(quantityChange);
    if (change > 0) {
      return { type: 'increase', label: 'Increase', color: 'text-green-600 bg-green-100' };
    } else if (change < 0) {
      return { type: 'decrease', label: 'Decrease', color: 'text-red-600 bg-red-100' };
    }
    return { type: 'neutral', label: 'No Change', color: 'text-gray-600 bg-gray-100' };
  };

  const exportAdjustments = () => {
    if (filteredAdjustments.length === 0) return;

    const csvContent = generateCSVContent();
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `stock_adjustments_${warehouse?.name || 'warehouse'}_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const generateCSVContent = () => {
    const headers = ['Date', 'Part Number', 'Part Name', 'Quantity Change', 'Unit', 'Reason', 'Notes', 'Performed By'];
    const rows = filteredAdjustments.map(adjustment => {
      const part = getPartDetails(adjustment.part_id);
      return [
        formatDate(adjustment.created_at),
        part.part_number || '',
        part.name || '',
        adjustment.quantity_change,
        adjustment.unit_of_measure,
        adjustment.reason || '',
        adjustment.notes || '',
        adjustment.performed_by_user_name || 'Unknown'
      ];
    });

    return [headers, ...rows].map(row => row.join(',')).join('\n');
  };

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

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-gray-500">Loading adjustment history...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium text-gray-900">
          Stock Adjustment History
          {warehouse && (
            <span className="text-sm font-normal text-gray-500 ml-2">
              - {warehouse.name}
            </span>
          )}
        </h3>
        <button
          onClick={exportAdjustments}
          disabled={filteredAdjustments.length === 0}
          className="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50"
        >
          Export CSV
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg border border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              From Date
            </label>
            <input
              type="date"
              value={filters.start_date}
              onChange={(e) => handleFilterChange('start_date', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              To Date
            </label>
            <input
              type="date"
              value={filters.end_date}
              onChange={(e) => handleFilterChange('end_date', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Adjustment Type
            </label>
            <select
              value={filters.adjustment_type}
              onChange={(e) => handleFilterChange('adjustment_type', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Adjustments</option>
              <option value="increase">Increases Only</option>
              <option value="decrease">Decreases Only</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Reason
            </label>
            <select
              value={filters.reason}
              onChange={(e) => handleFilterChange('reason', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Reasons</option>
              {reasonOptions.map((reason) => (
                <option key={reason} value={reason}>
                  {reason}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Search
            </label>
            <input
              type="text"
              placeholder="Part name or notes..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Adjustment Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm font-medium text-gray-500">Total Adjustments</div>
          <div className="text-2xl font-bold text-gray-900">
            {formatNumber(filteredAdjustments.length)}
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm font-medium text-gray-500">Stock Increases</div>
          <div className="text-2xl font-bold text-green-600">
            {formatNumber(filteredAdjustments.filter(a => parseFloat(a.quantity_change) > 0).length)}
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm font-medium text-gray-500">Stock Decreases</div>
          <div className="text-2xl font-bold text-red-600">
            {formatNumber(filteredAdjustments.filter(a => parseFloat(a.quantity_change) < 0).length)}
          </div>
        </div>
      </div>

      {/* Adjustments Table */}
      {filteredAdjustments.length === 0 ? (
        <div className="bg-gray-50 p-8 rounded-lg text-center">
          <div className="text-gray-500">
            {adjustments.length === 0
              ? 'No stock adjustments found for this warehouse.'
              : 'No adjustments match your current filters.'}
          </div>
        </div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Part
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Change
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Reason
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Notes
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Performed By
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredAdjustments.map((adjustment) => {
                const part = getPartDetails(adjustment.part_id);
                const adjustmentType = getAdjustmentType(adjustment.quantity_change);

                return (
                  <tr key={adjustment.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatDate(adjustment.created_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {part.name || 'Unknown Part'}
                        </div>
                        <div className="text-sm text-gray-500">
                          {part.part_number}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <span className={parseFloat(adjustment.quantity_change) >= 0 ? 'text-green-600' : 'text-red-600'}>
                        {parseFloat(adjustment.quantity_change) >= 0 ? '+' : ''}{adjustment.quantity_change} {adjustment.unit_of_measure}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${adjustmentType.color}`}>
                        {adjustmentType.label}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {adjustment.reason || '-'}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      <div className="max-w-xs truncate" title={adjustment.notes}>
                        {adjustment.notes || '-'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {adjustment.performed_by_user_name || 'Unknown'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default WarehouseStockAdjustmentHistory;