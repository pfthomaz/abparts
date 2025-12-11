// frontend/src/components/WarehouseStockAdjustmentHistory.js

import React, { useState, useEffect } from 'react';
import { inventoryService } from '../services/inventoryService';
import { partsService } from '../services/partsService';
import { stockAdjustmentsService } from '../services/stockAdjustmentsService';
import { useTranslation } from '../hooks/useTranslation';
import StockAdjustmentDetailsModal from './StockAdjustmentDetailsModal';

const WarehouseStockAdjustmentHistory = ({ warehouseId, warehouse }) => {
  const { t } = useTranslation();
  const [adjustments, setAdjustments] = useState([]);
  const [parts, setParts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedAdjustment, setSelectedAdjustment] = useState(null);
  const [filters, setFilters] = useState({
    start_date: '',  // No default date filter - show all
    end_date: '',    // No default date filter - show all
    reason: 'all',
    adjustment_type: 'all' // 'all', 'increase', 'decrease'
  });
  const [searchTerm, setSearchTerm] = useState('');

  const fetchData = async () => {
    setLoading(true);
    setError('');
    try {
      // Fetch parts data first (this should work)
      const partsResponse = await partsService.getPartsWithInventory({ limit: 1000 });
      const partsData = partsResponse?.items || partsResponse || [];
      setParts(Array.isArray(partsData) ? partsData : []);

      // Try to fetch adjustments data, but handle 404 gracefully
      try {
        const adjustmentsData = await inventoryService.getWarehouseStockAdjustments(warehouseId, filters);
        setAdjustments(adjustmentsData);
      } catch (adjustmentError) {
        // If it's a 404, the API endpoint doesn't exist yet - show empty state without error
        if (adjustmentError.response?.status === 404) {
          console.warn('Stock adjustments API endpoint not implemented yet');
          setAdjustments([]);
        } else {
          // For other errors, show the error message
          throw adjustmentError;
        }
      }
    } catch (err) {
      setError('Failed to fetch adjustment history');
      console.error('Failed to fetch adjustment history:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (warehouseId) {
      fetchData();
    }
  }, [warehouseId, filters]);

  // Auto-refresh every 15 minutes (reduced frequency for non-existent API endpoint)
  useEffect(() => {
    if (!warehouseId) return;

    const interval = setInterval(() => {
      fetchData();
    }, 15 * 60 * 1000);

    return () => clearInterval(interval);
  }, [warehouseId]);

  const getPartDetails = (partId) => {
    if (!Array.isArray(parts)) {
      return {};
    }
    return parts.find(p => p.id === partId) || {};
  };

  // New API returns adjustment headers, not individual items
  // Filter adjustments based on search and type
  const filteredAdjustments = adjustments.filter(adjustment => {
    const matchesSearch = !searchTerm ||
      adjustment.reason?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      adjustment.username?.toLowerCase().includes(searchTerm.toLowerCase());

    // For the new format, we just show all adjustments
    return matchesSearch;
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

  const handleViewDetails = async (adjustmentId) => {
    try {
      const details = await stockAdjustmentsService.getById(adjustmentId);
      setSelectedAdjustment(details);
    } catch (err) {
      console.error('Failed to fetch adjustment details:', err);
      setError('Failed to load adjustment details');
    }
  };

  const getAdjustmentType = (quantityChange) => {
    const change = parseFloat(quantityChange);
    if (change > 0) {
      return { type: 'increase', label: t('warehouses.increase'), color: 'text-green-600 bg-green-100' };
    } else if (change < 0) {
      return { type: 'decrease', label: t('warehouses.decrease'), color: 'text-red-600 bg-red-100' };
    }
    return { type: 'neutral', label: t('warehouses.noChange'), color: 'text-gray-600 bg-gray-100' };
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
        <div className="text-gray-500">{t('warehouses.loadingAdjustments')}</div>
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
          {t('warehouses.stockAdjustmentHistory')}
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
          {t('warehouses.exportCSV')}
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg border border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
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
              {t('warehouses.adjustmentType')}
            </label>
            <select
              value={filters.adjustment_type}
              onChange={(e) => handleFilterChange('adjustment_type', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">{t('warehouses.allAdjustments')}</option>
              <option value="increase">{t('warehouses.increasesOnly')}</option>
              <option value="decrease">{t('warehouses.decreasesOnly')}</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('warehouses.reason')}
            </label>
            <select
              value={filters.reason}
              onChange={(e) => handleFilterChange('reason', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">{t('warehouses.allReasons')}</option>
              {reasonOptions.map((reason) => (
                <option key={reason} value={reason}>
                  {reason}
                </option>
              ))}
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

      {/* Adjustment Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm font-medium text-gray-500">{t('warehouses.totalAdjustments')}</div>
          <div className="text-2xl font-bold text-gray-900">
            {formatNumber(filteredAdjustments.length)}
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm font-medium text-gray-500">{t('warehouses.stockIncreases')}</div>
          <div className="text-2xl font-bold text-green-600">
            {formatNumber(filteredAdjustments.filter(a => parseFloat(a.quantity_change) > 0).length)}
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm font-medium text-gray-500">{t('warehouses.stockDecreases')}</div>
          <div className="text-2xl font-bold text-red-600">
            {formatNumber(filteredAdjustments.filter(a => parseFloat(a.quantity_change) < 0).length)}
          </div>
        </div>
      </div>

      {/* Adjustments Table */}
      {filteredAdjustments.length === 0 ? (
        <div className="bg-gray-50 p-8 rounded-lg text-center">
          <div className="text-gray-500">
            {error ? (
              <div>
                <div className="mb-2">{t('warehouses.adjustmentHistoryUnavailable')}</div>
                <div className="text-sm">{t('warehouses.backendDevelopment')}</div>
              </div>
            ) : adjustments.length === 0 ? (
              t('warehouses.noAdjustmentsFound')
            ) : (
              t('warehouses.noAdjustmentsMatch')
            )}
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
                  {t('warehouses.part')}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t('warehouses.change')}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t('warehouses.type')}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t('warehouses.reason')}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t('warehouses.notes')}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t('warehouses.performedBy')}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t('warehouses.actions')}
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredAdjustments.map((adjustment) => {
                // New API format: adjustment headers with total_items_adjusted
                const adjustmentTypeLabel = adjustment.adjustment_type?.replace('_', ' ').toUpperCase() || 'UNKNOWN';

                return (
                  <tr key={adjustment.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatDate(adjustment.adjustment_date || adjustment.created_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {adjustment.total_items_adjusted} {adjustment.total_items_adjusted === 1 ? t('warehouses.partAdjusted') : t('warehouses.partsAdjusted')}
                        </div>
                        <div className="text-sm text-gray-500">
                          {adjustmentTypeLabel}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => handleViewDetails(adjustment.id)}
                        className="text-blue-600 hover:text-blue-800 underline cursor-pointer"
                      >
                        {adjustment.total_items_adjusted} {t('warehouses.items')}
                      </button>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                        {adjustmentTypeLabel}
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
                      {adjustment.username || 'Unknown'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <button
                        onClick={() => handleViewDetails(adjustment.id)}
                        className="text-blue-600 hover:text-blue-800 font-medium"
                      >
                        {t('warehouses.viewDetails')}
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Details Modal */}
      {selectedAdjustment && (
        <StockAdjustmentDetailsModal
          adjustment={selectedAdjustment}
          onClose={() => setSelectedAdjustment(null)}
        />
      )}
    </div>
  );
};

export default WarehouseStockAdjustmentHistory;