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
  const [filterType, setFilterType] = useState('in_stock'); // 'all_parts', 'in_stock', 'low_stock'
  const [lastUpdated, setLastUpdated] = useState(null);
  const [editingMinStock, setEditingMinStock] = useState(null); // inventory item id being edited
  const [editMinStockValue, setEditMinStockValue] = useState('');
  const [traceabilityData, setTraceabilityData] = useState(null);
  const [traceabilityLoading, setTraceabilityLoading] = useState(false);
  const [showTraceability, setShowTraceability] = useState(false);

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

  // Build the list to display — for 'all_parts' include parts with no inventory record
  const displayItems = React.useMemo(() => {
    if (filterType !== 'all_parts') {
      return inventoryItems; // existing inventory rows only
    }
    // Merge: all parts + existing inventory (keyed by part_id)
    const inventoryByPartId = {};
    inventoryItems.forEach(item => { inventoryByPartId[item.part_id] = item; });

    return parts.map(part => {
      if (inventoryByPartId[part.id]) {
        return inventoryByPartId[part.id]; // real inventory row
      }
      // Virtual row — part exists but has no inventory record in this warehouse
      return {
        id: `virtual_${part.id}`,
        part_id: part.id,
        current_stock: 0,
        minimum_stock_recommendation: 0,
        unit_of_measure: part.unit_of_measure || '',
        _virtual: true, // flag — no real DB row yet
      };
    });
  }, [filterType, inventoryItems, parts]);

  // Safe filtering with validation using utility function
  const filteredInventory = safeFilter(displayItems, item => {
    try {
      if (!item) return false;

      const currentStock = parseFloat(item.current_stock);

      // 'in_stock' mode: exclude zero-stock items (original behaviour)
      if (filterType === 'in_stock' && currentStock === 0) return false;

      const part = getPartDetails(item.part_id);
      const matchesSearch = !searchTerm ||
        part.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        part.part_number?.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesFilter =
        filterType === 'all_parts' ||
        filterType === 'in_stock' ||
        (filterType === 'low_stock' && currentStock <= parseFloat(item.minimum_stock_recommendation));

      return matchesSearch && matchesFilter;
    } catch (error) {
      console.error('Error filtering inventory item:', error, item);
      return false;
    }
  }, []).sort((a, b) => {
    // Sort alphabetically by part_number then by name
    const partA = getPartDetails(a.part_id);
    const partB = getPartDetails(b.part_id);
    const codeA = (partA.part_number || partA.name || '').toLowerCase();
    const codeB = (partB.part_number || partB.name || '').toLowerCase();
    return codeA.localeCompare(codeB);
  });

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

  const handleMinStockClick = (item) => {
    setEditingMinStock(item.id);
    setEditMinStockValue(String(parseFloat(item.minimum_stock_recommendation) || 0));
  };

  const handleMinStockSave = async (itemId) => {
    const newValue = parseFloat(editMinStockValue);
    if (isNaN(newValue) || newValue < 0) {
      setEditingMinStock(null);
      return;
    }
    try {
      // Virtual row — need to create the inventory record first
      if (String(itemId).startsWith('virtual_')) {
        const partId = String(itemId).replace('virtual_', '');
        const part = getPartDetails(partId);
        await inventoryService.createInventoryItem({
          warehouse_id: warehouseId,
          part_id: partId,
          current_stock: 0,
          minimum_stock_recommendation: newValue,
          unit_of_measure: part.unit_of_measure || 'pcs',
          reorder_threshold_set_by: 'user',
        });
        // Refresh to get the real DB row
        await fetchWarehouseInventory();
      } else {
        await inventoryService.updateInventoryItem(itemId, {
          minimum_stock_recommendation: newValue
        });
        setInventoryItems(prev => prev.map(item =>
          item.id === itemId ? { ...item, minimum_stock_recommendation: newValue } : item
        ));
      }
    } catch (err) {
      console.error('Failed to update min stock:', err);
    }
    setEditingMinStock(null);
  };

  const handleMinStockKeyDown = (e, itemId) => {
    if (e.key === 'Enter') {
      handleMinStockSave(itemId);
    } else if (e.key === 'Escape') {
      setEditingMinStock(null);
    }
  };

  const handleShowTraceability = async (partId) => {
    setTraceabilityLoading(true);
    setShowTraceability(true);
    try {
      const data = await inventoryService.getStockTraceability(warehouseId, partId);
      setTraceabilityData(data);
    } catch (err) {
      console.error('Failed to load traceability:', err);
      setTraceabilityData({ error: err.message || 'Failed to load traceability data' });
    } finally {
      setTraceabilityLoading(false);
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
            <option value="in_stock">{t('warehouses.allItemsInStock')}</option>
            <option value="low_stock">{t('warehouses.lowStock')}</option>
            <option value="all_parts">{t('warehouses.allParts') || 'All Parts'}</option>
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
        <div className="bg-white shadow overflow-x-auto sm:rounded-md">
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
                      <div className="text-sm font-medium text-gray-900 flex items-center justify-end gap-1">
                        {parseFloat(item.current_stock).toLocaleString()}
                        <button
                          onClick={() => handleShowTraceability(item.part_id)}
                          className="text-blue-500 hover:text-blue-700 ml-1"
                          title="Stock traceability"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                          </svg>
                        </button>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      {editingMinStock === item.id ? (
                        <input
                          type="number"
                          min="0"
                          step="1"
                          value={editMinStockValue}
                          onChange={(e) => setEditMinStockValue(e.target.value)}
                          onBlur={() => handleMinStockSave(item.id)}
                          onKeyDown={(e) => handleMinStockKeyDown(e, item.id)}
                          autoFocus
                          className="w-20 px-2 py-1 text-sm text-right border border-blue-400 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      ) : (
                        <button
                          onClick={() => handleMinStockClick(item)}
                          className="text-sm text-gray-900 hover:text-blue-600 hover:bg-blue-50 px-2 py-1 rounded cursor-pointer transition-colors"
                          title={t('warehouses.clickToEditMinStock') || 'Click to edit minimum stock'}
                        >
                          {parseFloat(item.minimum_stock_recommendation).toLocaleString()}
                        </button>
                      )}
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

      {/* Traceability Modal */}
      {showTraceability && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex items-center justify-center z-50">
          <div className="relative bg-white p-6 rounded-lg shadow-xl max-w-2xl w-full mx-4 my-10">
            <div className="flex justify-between items-center pb-3 border-b border-gray-200 mb-4">
              <h3 className="text-lg font-bold text-gray-800">
                Stock Traceability
                {traceabilityData && !traceabilityData.error && (
                  <span className="text-sm font-normal text-gray-500 ml-2">
                    {traceabilityData.part_name} ({traceabilityData.part_number})
                  </span>
                )}
              </h3>
              <button
                onClick={() => { setShowTraceability(false); setTraceabilityData(null); }}
                className="text-gray-500 hover:text-gray-700 text-2xl font-light leading-none"
              >
                &times;
              </button>
            </div>
            <div className="max-h-[70vh] overflow-y-auto">
              {traceabilityLoading ? (
                <div className="text-center py-8 text-gray-500">Loading traceability data...</div>
              ) : traceabilityData?.error ? (
                <div className="text-red-600 py-4">{traceabilityData.error}</div>
              ) : traceabilityData ? (
                <div>
                  <div className="mb-4 p-3 bg-blue-50 rounded-lg">
                    <span className="text-sm font-medium text-blue-800">
                      Current Stock: <span className="text-lg font-bold">{traceabilityData.current_stock}</span>
                    </span>
                    <span className="text-sm text-blue-600 ml-4">
                      ({traceabilityData.total_events} events)
                    </span>
                  </div>
                  <div className="space-y-2">
                    {traceabilityData.events.map((event, idx) => (
                      <div key={idx} className={`p-3 rounded-lg border ${
                        event.type === 'stock_adjustment' || event.type === 'initial' 
                          ? 'bg-yellow-50 border-yellow-200' 
                          : event.quantity_change > 0 
                            ? 'bg-green-50 border-green-200' 
                            : 'bg-red-50 border-red-200'
                      }`}>
                        <div className="flex justify-between items-start">
                          <div>
                            <span className="text-sm font-medium text-gray-800">{event.description}</span>
                            {event.notes && (
                              <p className="text-xs text-gray-500 mt-1">{event.notes}</p>
                            )}
                            {event.performed_by && (
                              <p className="text-xs text-gray-400 mt-0.5">By: {event.performed_by}</p>
                            )}
                          </div>
                          <div className="text-right flex-shrink-0 ml-4">
                            {event.quantity_change !== null && (
                              <span className={`text-sm font-bold ${event.quantity_change > 0 ? 'text-green-700' : 'text-red-700'}`}>
                                {event.quantity_change > 0 ? '+' : ''}{event.quantity_change}
                              </span>
                            )}
                            <div className="text-xs text-gray-500">
                              Balance: {event.balance_after}
                            </div>
                          </div>
                        </div>
                        {event.date && (
                          <div className="text-xs text-gray-400 mt-1">
                            {new Date(event.date).toLocaleString()}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ) : null}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WarehouseInventoryView;