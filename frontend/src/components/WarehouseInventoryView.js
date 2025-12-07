// frontend/src/components/WarehouseInventoryView.js

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { inventoryService } from '../services/inventoryService';
import { partsService } from '../services/partsService';
import { useTranslation } from '../hooks/useTranslation';
import { validateInventoryData, safeFilter } from '../utils/inventoryValidation';

const WarehouseInventoryView = ({ warehouseId, warehouse, onRefresh }) => {
  const { t } = useTranslation();
  const [inventoryItems, setInventoryItems] = useState([]);
  const [parts, setParts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all'); // 'all', 'low_stock', 'out_of_stock'
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchWarehouseInventory = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await inventoryService.getWarehouseInventory(warehouseId);
      // Use the validation utility to ensure we have a proper array
      const validatedData = validateInventoryData(data);
      setInventoryItems(validatedData);
      setLastUpdated(new Date());
    } catch (err) {
      setError('Failed to fetch warehouse inventory');
      console.error('Failed to fetch warehouse inventory:', err);
      // Set empty array as fallback
      setInventoryItems([]);
    } finally {
      setLoading(false);
    }
  }, [warehouseId]);

  const fetchParts = useCallback(async () => {
    try {
      const response = await partsService.getPartsWithInventory({ limit: 1000 });
      // Handle paginated response format
      const partsData = response?.items || response || [];
      setParts(Array.isArray(partsData) ? partsData : []);
    } catch (err) {
      console.error('Failed to fetch parts:', err);
      setParts([]); // Ensure parts is always an array
    }
  }, []);

  useEffect(() => {
    if (warehouseId) {
      fetchWarehouseInventory();
      fetchParts();
    }
  }, [warehouseId, fetchWarehouseInventory, fetchParts]);

  // Listen for inventory updates and refresh automatically
  useEffect(() => {
    const handleInventoryUpdate = (event) => {
      if (event.detail) {
        // Check if this warehouse is affected (either as source or destination)
        const isSourceWarehouse = event.detail.warehouseId === warehouseId;
        const isDestinationWarehouse = event.detail.toWarehouseId === warehouseId;

        if (isSourceWarehouse || isDestinationWarehouse) {
          fetchWarehouseInventory();
        }
      }
    };

    window.addEventListener('inventoryUpdated', handleInventoryUpdate);
    return () => {
      window.removeEventListener('inventoryUpdated', handleInventoryUpdate);
    };
  }, [warehouseId, fetchWarehouseInventory]);

  // Use ref to store the latest refresh function
  const refreshFunctionRef = useRef(fetchWarehouseInventory);
  refreshFunctionRef.current = fetchWarehouseInventory;

  // Expose refresh function to parent component
  useEffect(() => {
    if (onRefresh && typeof onRefresh === 'function') {
      const refreshWrapper = () => refreshFunctionRef.current();
      onRefresh(refreshWrapper);
    }
  }, [onRefresh]);

  const getPartDetails = (partId) => {
    if (!Array.isArray(parts)) {
      return {};
    }
    return parts.find(p => p.id === partId) || {};
  };

  // Safe filtering with validation using utility function
  const filteredInventory = safeFilter(inventoryItems, item => {
    try {
      if (!item) return false;

      // Always exclude items with zero stock from the main inventory view
      const currentStock = parseFloat(item.current_stock);
      if (currentStock === 0) return false;

      const part = getPartDetails(item.part_id);
      const matchesSearch = !searchTerm ||
        part.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        part.part_number?.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesFilter = filterType === 'all' ||
        (filterType === 'low_stock' && currentStock <= parseFloat(item.minimum_stock_recommendation));

      return matchesSearch && matchesFilter;
    } catch (error) {
      console.error('Error filtering inventory item:', error, item);
      return false;
    }
  }, []);

  const getStockStatus = (currentStock, minStock) => {
    const current = parseFloat(currentStock);
    const minimum = parseFloat(minStock);

    if (current === 0) {
      return { status: 'out_of_stock', color: 'text-red-600', bg: 'bg-red-100' };
    } else if (current <= minimum) {
      return { status: 'low_stock', color: 'text-orange-600', bg: 'bg-orange-100' };
    } else {
      return { status: 'in_stock', color: 'text-green-600', bg: 'bg-green-100' };
    }
  };

  const getStockStatusLabel = (status) => {
    switch (status) {
      case 'out_of_stock': return t('warehouses.outOfStock');
      case 'low_stock': return t('warehouses.lowStock');
      case 'in_stock': return t('warehouses.inStock');
      default: return t('common.unknown');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-gray-500">{t('warehouses.loadingInventory')}</div>
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
          {t('warehouses.inventory')}
          {warehouse && (
            <span className="text-sm font-normal text-gray-500 ml-2">
              - {warehouse.name}
            </span>
          )}
        </h3>

        <div className="text-sm text-gray-500">
          {filteredInventory.length} {t('warehouses.items')}
          {lastUpdated && (
            <div className="text-xs text-gray-400 mt-1">
              {t('warehouses.lastUpdated')}: {lastUpdated.toLocaleTimeString()}
            </div>
          )}
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <input
            type="text"
            placeholder={t('warehouses.searchParts')}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">{t('warehouses.allItemsInStock')}</option>
            <option value="low_stock">{t('warehouses.lowStock')}</option>
          </select>
        </div>
      </div>

      {/* Inventory Table */}
      {filteredInventory.length === 0 ? (
        <div className="bg-gray-50 p-8 rounded-lg text-center">
          <div className="text-gray-500">
            {searchTerm || filterType !== 'all'
              ? t('warehouses.noInventoryMatch')
              : t('warehouses.noInventoryFound')}
          </div>
        </div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t('warehouses.part')}
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t('warehouses.currentStock')}
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t('warehouses.minStock')}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t('warehouses.statusLabel')}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  {t('warehouses.unit')}
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredInventory.map((item) => {
                const part = getPartDetails(item.part_id);
                const stockStatus = getStockStatus(item.current_stock, item.minimum_stock_recommendation);

                return (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {part.name || t('warehouses.unknownPart')}
                        </div>
                        <div className="text-sm text-gray-500">
                          {part.part_number}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <div className="text-sm font-medium text-gray-900">
                        {parseFloat(item.current_stock).toLocaleString()}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <div className="text-sm text-gray-900">
                        {parseFloat(item.minimum_stock_recommendation).toLocaleString()}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${stockStatus.bg} ${stockStatus.color}`}>
                        {getStockStatusLabel(stockStatus.status)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {item.unit_of_measure}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm font-medium text-gray-500">{t('warehouses.totalItems')}</div>
          <div className="text-2xl font-bold text-gray-900">
            {Array.isArray(inventoryItems) ? inventoryItems.filter(item => parseFloat(item.current_stock || 0) > 0).length : 0}
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm font-medium text-gray-500">{t('warehouses.lowStockItems')}</div>
          <div className="text-2xl font-bold text-orange-600">
            {safeFilter(inventoryItems, item => {
              try {
                return item &&
                  parseFloat(item.current_stock) <= parseFloat(item.minimum_stock_recommendation) &&
                  parseFloat(item.current_stock) > 0;
              } catch (error) {
                console.error('Error calculating low stock:', error, item);
                return false;
              }
            }, []).length}
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm font-medium text-gray-500">{t('warehouses.itemsInStock')}</div>
          <div className="text-2xl font-bold text-green-600">
            {safeFilter(inventoryItems, item => {
              try {
                return item && parseFloat(item.current_stock) > 0;
              } catch (error) {
                console.error('Error calculating in stock:', error, item);
                return false;
              }
            }, []).length}
          </div>
        </div>
      </div>
    </div>
  );
};

export default WarehouseInventoryView;