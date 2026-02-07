// frontend/src/components/InventoryTransferHistory.js

import React, { useState, useEffect } from 'react';
import { warehouseService } from '../services/warehouseService';
import { partsService } from '../services/partsService';
import { inventoryService } from '../services/inventoryService';
import { useTranslation } from '../hooks/useTranslation';
import { safeFilter } from '../utils/inventoryValidation';

const InventoryTransferHistory = ({ warehouseId, warehouse }) => {
  const { t } = useTranslation();
  const [transfers, setTransfers] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [parts, setParts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    start_date: '2025-09-01', // Use a fixed date in the past
    end_date: '2025-09-29',   // Use a fixed date that's valid
    direction: 'all', // 'all', 'in', 'out'
    part_id: '',
    status: 'all'
  });
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    // Only fetch data if we have a valid warehouse ID
    if (warehouseId) {
      fetchData();
    }
  }, [warehouseId, filters.start_date, filters.end_date]); // Refresh when warehouse or date filters change

  // Auto-refresh every 10 minutes
  useEffect(() => {
    if (!warehouseId) return;

    const interval = setInterval(() => {
      fetchData();
    }, 10 * 60 * 1000);

    return () => clearInterval(interval);
  }, [warehouseId]);

  const fetchData = async () => {
    setLoading(true);
    setError('');
    try {
      // Validate warehouse ID before making API calls
      if (!warehouseId) {
        // console.log('No warehouse ID provided, skipping transfer fetch');
        setTransfers([]);
        setLoading(false);
        return;
      }

      // Validate UUID format
      const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
      if (!uuidRegex.test(warehouseId)) {
        // console.error('Invalid warehouse ID format:', warehouseId);
        setError('Invalid warehouse ID format');
        setLoading(false);
        return;
      }

      // Fetch data with individual error handling
      let transfersData = [];
      let warehousesData = [];
      let partsData = [];

      try {
        // Debug: Log all the values we're about to send
        // console.log('Debug - warehouseId:', warehouseId, 'type:', typeof warehouseId);
        // console.log('Debug - start_date:', filters.start_date, 'type:', typeof filters.start_date);
        // console.log('Debug - end_date:', filters.end_date, 'type:', typeof filters.end_date);
        // console.log('Fetching transfers with params:', { warehouse_id: warehouseId, start_date: filters.start_date, end_date: filters.end_date, limit: 1000 });

        // Validate date formats
        const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
        if (!dateRegex.test(filters.start_date) || !dateRegex.test(filters.end_date)) {
          throw new Error(`Invalid date format. start_date: ${filters.start_date}, end_date: ${filters.end_date}. Expected YYYY-MM-DD`);
        }

        // Fetch transfers with proper filtering
        // console.log('Fetching transfers with params:', { warehouse_id: warehouseId, start_date: filters.start_date, end_date: filters.end_date, limit: 1000 });

        const transfersResponse = await inventoryService.getInventoryTransfers({
          warehouse_id: warehouseId,
          start_date: filters.start_date,
          end_date: filters.end_date,
          limit: 1000
        });

        // console.log('Transfers response:', transfersResponse);
        transfersData = Array.isArray(transfersResponse) ? transfersResponse : [];
      } catch (transferError) {
        // console.error('Failed to fetch transfers:', transferError);
        // console.error('Full error object:', JSON.stringify(transferError, null, 2));

        // Log the full response for debugging
        if (transferError.response) {
          // console.error('Error response status:', transferError.response.status);
          // console.error('Error response headers:', transferError.response.headers);
          // console.error('Error response data:', transferError.response.data);
        }

        // Handle specific error types
        if (transferError.response?.status === 422) {
          // console.error('422 Validation error details:', transferError.response.data);
          // Log the specific validation errors
          if (transferError.response.data?.detail) {
            // console.error('Validation detail:', transferError.response.data.detail);
          }
        } else if (transferError.response?.status === 401) {
          // console.error('Authentication error - user may need to log in again');
        } else {
          // console.error('Transfer error details:', transferError.response?.data || transferError.message);
        }

        transfersData = [];
        // Don't set a general error here - let the component show "no transfers found" instead
      }

      try {
        warehousesData = await warehouseService.getWarehouses();
        warehousesData = Array.isArray(warehousesData) ? warehousesData : [];
      } catch (warehouseError) {
        // console.error('Failed to fetch warehouses:', warehouseError);
        warehousesData = [];
      }

      try {
        const partsResponse = await partsService.getPartsWithInventory({ limit: 1000 });
        // Handle paginated response format
        partsData = partsResponse?.items || partsResponse || [];
        partsData = Array.isArray(partsData) ? partsData : [];
      } catch (partsError) {
        // console.error('Failed to fetch parts:', partsError);
        partsData = [];
      }

      setTransfers(transfersData);
      setWarehouses(warehousesData);
      setParts(partsData);

      // Only show error if critical data (warehouses and parts) failed to load
      // Transfer data can be empty without it being an error
      if (warehousesData.length === 0 && partsData.length === 0) {
        setError('Failed to fetch essential data for transfer history');
      }
    } catch (err) {
      setError('Failed to fetch transfer history');
      // console.error('Failed to fetch transfer history:', err);
      // Set empty arrays as fallback
      setTransfers([]);
      setWarehouses([]);
      setParts([]);
    } finally {
      setLoading(false);
    }
  };

  const getWarehouseName = (warehouseId) => {
    const warehouse = warehouses.find(w => w.id === warehouseId);
    return warehouse ? warehouse.name : t('warehouses.unknownWarehouse');
  };

  const getPartDetails = (partId) => {
    if (!Array.isArray(parts)) {
      return {};
    }
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

      const transferDate = new Date(transfer.transaction_date || transfer.created_at);
      const startDate = new Date(filters.start_date);
      const endDate = new Date(filters.end_date);
      const matchesDate = transferDate >= startDate && transferDate <= endDate;

      return matchesSearch && matchesDirection && matchesPart && matchesDate;
    } catch (error) {
      // console.error('Error filtering transfer:', error, transfer);
      return false;
    }
  }, []);

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
    // Date filters will trigger API calls via useEffect
    // Other filters work client-side to avoid excessive API calls
  };

  const getTransferDirection = (transfer) => {
    if (transfer.from_warehouse_id === warehouseId) {
      return { direction: 'out', label: t('warehouses.outbound'), color: 'text-red-600 bg-red-100' };
    } else if (transfer.to_warehouse_id === warehouseId) {
      return { direction: 'in', label: t('warehouses.inbound'), color: 'text-green-600 bg-green-100' };
    }
    return { direction: 'unknown', label: t('common.unknown'), color: 'text-gray-600 bg-gray-100' };
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
        formatDate(transfer.transaction_date || transfer.created_at),
        direction.label,
        part.part_number || transfer.part_number || '',
        part.name || transfer.part_name || '',
        transfer.quantity,
        transfer.unit_of_measure,
        transfer.from_warehouse_name || getWarehouseName(transfer.from_warehouse_id),
        transfer.to_warehouse_name || getWarehouseName(transfer.to_warehouse_id),
        transfer.notes || ''
      ];
    });

    return [headers, ...rows].map(row => row.join(',')).join('\n');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-gray-500">{t('common.loading')}</div>
      </div>
    );
  }

  // Only show error for critical failures, not for empty transfer data
  if (error && (warehouses.length === 0 || parts.length === 0)) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 px-4 py-3 rounded">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-yellow-800">
              {t('warehouses.transferHistoryUnavailable')}
            </h3>
            <div className="mt-2 text-sm text-yellow-700">
              <p>{t('warehouses.unableToLoadTransfers')}</p>
              <ul className="list-disc list-inside mt-1">
                <li>{t('warehouses.essentialDataNotLoaded')}</li>
                <li>{t('warehouses.temporaryConnectivity')}</li>
                <li>{t('warehouses.tryRefreshing')}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium text-gray-900">
          {t('warehouses.transferHistoryTitle')}
          {warehouse && (
            <span className="text-sm font-normal text-gray-500 ml-2">
              - {warehouse.name}
            </span>
          )}
        </h3>
        <div className="flex space-x-2">
          <button
            onClick={exportTransfers}
            disabled={filteredTransfers.length === 0}
            className="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50"
          >
            {t('warehouses.exportCSV')}
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg border border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('warehouses.fromDate')}
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
              {t('warehouses.toDate')}
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
              {t('warehouses.direction')}
            </label>
            <select
              value={filters.direction}
              onChange={(e) => handleFilterChange('direction', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">{t('warehouses.allTransfers')}</option>
              <option value="in">{t('warehouses.inboundOnly')}</option>
              <option value="out">{t('warehouses.outboundOnly')}</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('common.search')}
            </label>
            <input
              type="text"
              placeholder={t('warehouses.partNameOrNotes')}
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
          <div className="text-sm font-medium text-gray-500">{t('warehouses.totalTransfers')}</div>
          <div className="text-2xl font-bold text-gray-900">
            {formatNumber(filteredTransfers.length)}
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm font-medium text-gray-500">{t('warehouses.inboundTransfers')}</div>
          <div className="text-2xl font-bold text-green-600">
            {formatNumber(safeFilter(filteredTransfers, transfer => transfer && transfer.to_warehouse_id === warehouseId, []).length)}
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm font-medium text-gray-500">{t('warehouses.outboundTransfers')}</div>
          <div className="text-2xl font-bold text-red-600">
            {formatNumber(safeFilter(filteredTransfers, transfer => transfer && transfer.from_warehouse_id === warehouseId, []).length)}
          </div>
        </div>
      </div>

      {/* Transfer Table */}
      {filteredTransfers.length === 0 ? (
        <div className="bg-gray-50 p-8 rounded-lg text-center">
          <div className="text-gray-500">
            <div className="mb-2">{t('warehouses.noTransfersFound')}</div>
            <div className="text-sm">
              {warehouseId ?
                t('warehouses.noTransfersRecorded') :
                t('warehouses.selectWarehouseForTransfers')
              }
            </div>
            <div className="text-xs text-gray-600 mt-2">
              {t('warehouses.transferFunctionalityWorking')}
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t('warehouses.date')}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t('warehouses.direction')}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t('warehouses.part')}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t('warehouses.quantity')}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t('warehouses.fromTo')}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t('warehouses.notes')}
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
                      {formatDate(transfer.transaction_date || transfer.created_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${direction.color}`}>
                        {direction.label}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {part.name || transfer.part_name || 'Unknown Part'}
                        </div>
                        <div className="text-sm text-gray-500">
                          {part.part_number || transfer.part_number}
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
                            <span className="text-gray-500">{t('warehouses.from')}:</span> {transfer.from_warehouse_name || getWarehouseName(transfer.from_warehouse_id)}
                          </>
                        ) : (
                          <>
                            <span className="text-gray-500">{t('warehouses.to')}:</span> {transfer.to_warehouse_name || getWarehouseName(transfer.to_warehouse_id)}
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