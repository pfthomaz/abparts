// frontend/src/components/InventoryTransferHistory.js

import React, { useState, useEffect } from 'react';
import { inventoryService } from '../services/inventoryService';
import { warehouseService } from '../services/warehouseService';
import { partsService } from '../services/partsService';
import { useAuth } from '../AuthContext';
import { safeFilter } from '../utils/inventoryValidation';

const InventoryTransferHistory = ({ warehouseId, warehouse }) => {
  const { user } = useAuth();
  const [transfers, setTransfers] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [parts, setParts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0],
    direction: 'all', // 'all', 'in', 'out'
    part_id: '',
    status: 'all'
  });
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchData();
  }, [warehouseId, filters]);

  const fetchData = async () => {
    setLoading(true);
    setError('');
    try {
      const transferFilters = {
        ...filters,
        warehouse_id: warehouseId
      };

      const [transfersData, warehousesData, partsData] = await Promise.all([
        inventoryService.getInventoryTransfers(transferFilters),
        warehouseService.getWarehouses(),
        partsService.getParts({ limit: 200 })
      ]);

      setTransfers(transfersData);
      setWarehouses(warehousesData);
      setParts(partsData);
    } catch (err) {
      setError('Failed to fetch transfer history');
      console.error('Failed to fetch transfer history:', err);
    } finally {
      setLoading(false);
    }
  };

  const getWarehouseName = (warehouseId) => {
    const warehouse = warehouses.find(w => w.id === warehouseId);
    return warehouse ? warehouse.name : 'Unknown Warehouse';
  };

  const getPartDetails = (partId) => {
    return parts.find(p => p.id === partId) || {};
  };

  const filteredTransfers = safeFilter(transfers, (transfer) => {
    if (!transfer) return false;

    try {
      const part = getPartDetails(transfer.part_id);
      const matchesSearch = !searchTerm ||
        part.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        part.part_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        transfer.notes?.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesDirection = filters.direction === 'all' ||
        (filters.direction === 'in' && transfer.to_warehouse_id === warehouseId) ||
        (filters.direction === 'out' && transfer.from_warehouse_id === warehouseId);

      const matchesPart = !filters.part_id || transfer.part_id === filters.part_id;

      const transferDate = new Date(transfer.created_at);
      const startDate = new Date(filters.start_date);
      const endDate = new Date(filters.end_date);
      const matchesDate = transferDate >= startDate && transferDate <= endDate;

      return matchesSearch && matchesDirection && matchesPart && matchesDate;
    } catch (error) {
      console.error('Error filtering transfer:', error, transfer);
      return false;
    }
  }, []);

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const getTransferDirection = (transfer) => {
    if (transfer.from_warehouse_id === warehouseId) {
      return { direction: 'out', label: 'Outbound', color: 'text-red-600 bg-red-100' };
    } else if (transfer.to_warehouse_id === warehouseId) {
      return { direction: 'in', label: 'Inbound', color: 'text-green-600 bg-green-100' };
    }
    return { direction: 'unknown', label: 'Unknown', color: 'text-gray-600 bg-gray-100' };
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

  const exportTransfers = () => {
    if (filteredTransfers.length === 0) return;

    const csvContent = generateCSVContent();
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `inventory_transfers_${warehouse?.name || 'warehouse'}_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const generateCSVContent = () => {
    const headers = ['Date', 'Direction', 'Part Number', 'Part Name', 'Quantity', 'Unit', 'From Warehouse', 'To Warehouse', 'Notes'];
    const rows = filteredTransfers.map(transfer => {
      const part = getPartDetails(transfer.part_id);
      const direction = getTransferDirection(transfer);
      return [
        formatDate(transfer.transaction_date),
        direction.label,
        part.part_number || '',
        part.name || '',
        transfer.quantity,
        transfer.unit_of_measure,
        getWarehouseName(transfer.from_warehouse_id),
        getWarehouseName(transfer.to_warehouse_id),
        transfer.notes || ''
      ];
    });

    return [headers, ...rows].map(row => row.join(',')).join('\n');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-gray-500">Loading transfer history...</div>
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
          Transfer History
          {warehouse && (
            <span className="text-sm font-normal text-gray-500 ml-2">
              - {warehouse.name}
            </span>
          )}
        </h3>
        <button
          onClick={exportTransfers}
          disabled={filteredTransfers.length === 0}
          className="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50"
        >
          Export CSV
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg border border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
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
              Direction
            </label>
            <select
              value={filters.direction}
              onChange={(e) => handleFilterChange('direction', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Transfers</option>
              <option value="in">Inbound Only</option>
              <option value="out">Outbound Only</option>
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

      {/* Transfer Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm font-medium text-gray-500">Total Transfers</div>
          <div className="text-2xl font-bold text-gray-900">
            {formatNumber(filteredTransfers.length)}
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm font-medium text-gray-500">Inbound Transfers</div>
          <div className="text-2xl font-bold text-green-600">
            {formatNumber(safeFilter(filteredTransfers, t => t && t.to_warehouse_id === warehouseId, []).length)}
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm font-medium text-gray-500">Outbound Transfers</div>
          <div className="text-2xl font-bold text-red-600">
            {formatNumber(safeFilter(filteredTransfers, t => t && t.from_warehouse_id === warehouseId, []).length)}
          </div>
        </div>
      </div>

      {/* Transfer Table */}
      {filteredTransfers.length === 0 ? (
        <div className="bg-gray-50 p-8 rounded-lg text-center">
          <div className="text-gray-500">
            {transfers.length === 0
              ? 'No transfers found for this warehouse.'
              : 'No transfers match your current filters.'}
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
                  Direction
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Part
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Quantity
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  From/To
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Notes
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredTransfers.map((transfer) => {
                const part = getPartDetails(transfer.part_id);
                const direction = getTransferDirection(transfer);

                return (
                  <tr key={transfer.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatDate(transfer.transaction_date)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${direction.color}`}>
                        {direction.label}
                      </span>
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
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatNumber(transfer.quantity)} {transfer.unit_of_measure}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {direction.direction === 'in' ? (
                          <>
                            <span className="text-gray-500">From:</span> {getWarehouseName(transfer.from_warehouse_id)}
                          </>
                        ) : (
                          <>
                            <span className="text-gray-500">To:</span> {getWarehouseName(transfer.to_warehouse_id)}
                          </>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      <div className="max-w-xs truncate" title={transfer.notes}>
                        {transfer.notes || '-'}
                      </div>
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

export default InventoryTransferHistory;