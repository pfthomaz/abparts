// frontend/src/components/WarehouseInventoryReporting.js

import React, { useState, useEffect, useCallback } from 'react';
import { inventoryService } from '../services/inventoryService';
import { warehouseService } from '../services/warehouseService';

// Helper functions moved outside component to avoid dependency issues
const getStockStatus = (currentStock) => {
  if (!currentStock || currentStock <= 0) return 'out_of_stock';
  if (currentStock <= 5) return 'low_stock'; // Arbitrary threshold
  return 'in_stock';
};

const transformValuationData = (rawData) => {
  const items = rawData.map(item => ({
    warehouse_id: item.warehouse_id,  // Include warehouse_id for filtering
    warehouse_name: item.warehouse_name,
    part_number: item.part_number,
    part_name: item.part_name,
    current_stock: item.current_stock,
    unit_of_measure: item.unit_of_measure,
    minimum_stock_recommendation: 0, // Not available in valuation data
    stock_status: getStockStatus(item.current_stock),
    estimated_value: item.total_value || 0
  }));

  // Calculate summary
  const totalItems = items.length;
  const totalValue = items.reduce((sum, item) => sum + (item.estimated_value || 0), 0);
  const lowStockItems = items.filter(item => item.stock_status === 'low_stock').length;
  const outOfStockItems = items.filter(item => item.stock_status === 'out_of_stock').length;

  // Group by warehouse for breakdown
  const warehouseGroups = {};
  items.forEach(item => {
    if (!warehouseGroups[item.warehouse_id]) {
      warehouseGroups[item.warehouse_id] = {
        warehouse_id: item.warehouse_id,  // Include warehouse_id
        warehouse_name: item.warehouse_name,
        total_items: 0,
        total_value: 0,
        low_stock_items: 0,
        out_of_stock_items: 0
      };
    }
    const group = warehouseGroups[item.warehouse_id];
    group.total_items++;
    group.total_value += item.estimated_value || 0;
    if (item.stock_status === 'low_stock') group.low_stock_items++;
    if (item.stock_status === 'out_of_stock') group.out_of_stock_items++;
  });

  return {
    items,
    summary: {
      total_items: totalItems,
      total_value: totalValue,
      low_stock_items: lowStockItems,
      out_of_stock_items: outOfStockItems
    },
    warehouse_breakdown: Object.values(warehouseGroups)
  };
};

const transformMovementData = (rawData) => {
  const items = rawData.map(item => ({
    warehouse_name: 'Multiple', // Movement data is aggregated
    part_number: item.part_number,
    part_name: item.part_name,
    current_stock: item.current_inventory,
    unit_of_measure: item.unit_of_measure,
    minimum_stock_recommendation: 0,
    stock_status: getStockStatus(item.current_inventory),
    estimated_value: 0, // Not available in movement data
    beginning_balance: item.beginning_balance,
    received: item.received,
    issued: item.issued,
    adjusted: item.adjusted,
    ending_balance: item.ending_balance
  }));

  return {
    items,
    summary: {
      total_items: items.length,
      total_value: 0,
      low_stock_items: items.filter(item => item.stock_status === 'low_stock').length,
      out_of_stock_items: items.filter(item => item.stock_status === 'out_of_stock').length
    },
    warehouse_breakdown: []
  };
};

const transformReportData = (rawData, reportType) => {
  if (!rawData || !Array.isArray(rawData)) {
    return { items: [], summary: {}, warehouse_breakdown: [] };
  }

  // Transform based on report type
  switch (reportType) {
    case 'valuation':
    case 'detailed':
    case 'summary':
      return transformValuationData(rawData);
    case 'movement':
      return transformMovementData(rawData);
    default:
      return transformValuationData(rawData);
  }
};

const WarehouseInventoryReporting = ({ organizationId }) => {
  const [reportData, setReportData] = useState(null);
  const [warehouses, setWarehouses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [reportType, setReportType] = useState('summary'); // 'summary', 'detailed', 'movement', 'valuation'
  const [dateRange, setDateRange] = useState({
    start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0]
  });
  const [selectedWarehouses, setSelectedWarehouses] = useState([]);
  const [filters, setFilters] = useState({
    stock_status: 'all', // 'all', 'in_stock', 'low_stock', 'out_of_stock'
    part_type: 'all', // 'all', 'consumable', 'bulk_material'
    min_value: '',
    max_value: ''
  });

  const fetchWarehouses = useCallback(async () => {
    try {
      const data = await warehouseService.getOrganizationWarehouses(organizationId);
      setWarehouses(data);
      // Select all warehouses by default
      setSelectedWarehouses(data.map(w => w.id));
    } catch (err) {
      setError('Failed to fetch warehouses');
      console.error('Failed to fetch warehouses:', err);
    }
  }, [organizationId]);

  const generateReport = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const reportParams = {
        warehouse_ids: selectedWarehouses,
        report_type: reportType,
        start_date: dateRange.start_date,
        end_date: dateRange.end_date,
        ...filters
      };

      const rawData = await inventoryService.getInventoryReport(reportParams);
      
      // Transform the backend response to match frontend expectations
      let transformedData = transformReportData(rawData, reportType);
      
      // Frontend filter: Backend returns all warehouses, so filter here
      if (selectedWarehouses.length > 0 && transformedData.items) {
        const filteredItems = transformedData.items.filter(item => 
          selectedWarehouses.includes(item.warehouse_id)
        );
        
        const filteredBreakdown = transformedData.warehouse_breakdown.filter(wh =>
          selectedWarehouses.includes(wh.warehouse_id)
        );
        
        // Recalculate summary
        const filteredSummary = {
          total_items: filteredItems.length,
          total_value: filteredItems.reduce((sum, item) => sum + (item.estimated_value || 0), 0),
          low_stock_items: filteredItems.filter(item => item.stock_status === 'low_stock').length,
          out_of_stock_items: filteredItems.filter(item => item.stock_status === 'out_of_stock').length
        };
        
        transformedData = {
          items: filteredItems,
          summary: filteredSummary,
          warehouse_breakdown: filteredBreakdown
        };
        
      }
      
      setReportData(transformedData);
    } catch (err) {
      setError('Failed to generate report');
      console.error('Failed to generate report:', err);
    } finally {
      setLoading(false);
    }
  }, [selectedWarehouses, reportType, dateRange, filters]);

  useEffect(() => {
    if (organizationId) {
      fetchWarehouses();
    }
  }, [organizationId, fetchWarehouses]);

  useEffect(() => {
    if (organizationId && selectedWarehouses.length > 0) {
      generateReport();
    } else if (organizationId && selectedWarehouses.length === 0) {
      // Clear report data when no warehouses are selected
      setReportData(null);
    }
  }, [organizationId, selectedWarehouses, reportType, dateRange, filters, generateReport]);

  const handleWarehouseToggle = (warehouseId) => {
    setSelectedWarehouses(prev => {
      if (prev.includes(warehouseId)) {
        return prev.filter(id => id !== warehouseId);
      } else {
        return [...prev, warehouseId];
      }
    });
  };

  const handleSelectAllWarehouses = () => {
    setSelectedWarehouses(warehouses.map(w => w.id));
  };

  const handleDeselectAllWarehouses = () => {
    setSelectedWarehouses([]);
  };

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleDateRangeChange = (field, value) => {
    setDateRange(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const exportReport = () => {
    if (!reportData) return;

    const csvContent = generateCSVContent();
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `inventory_report_${reportType}_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const generateCSVContent = () => {
    if (!reportData || !reportData.items) return '';

    const headers = ['Warehouse', 'Part Number', 'Part Name', 'Current Stock', 'Unit', 'Min Stock', 'Status', 'Value'];
    const rows = reportData.items.map(item => [
      item.warehouse_name,
      item.part_number,
      item.part_name,
      item.current_stock,
      item.unit_of_measure,
      item.minimum_stock_recommendation,
      item.stock_status,
      item.estimated_value || 0
    ]);
    console.log('rows: ',rows);

    return [headers, ...rows].map(row => row.join(',')).join('\n');
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value || 0);
  };

  const formatNumber = (value) => {
    return new Intl.NumberFormat('en-US').format(value || 0);
  };

  const getStockStatusColor = (status) => {
    switch (status) {
      case 'out_of_stock': return 'text-red-600 bg-red-100';
      case 'low_stock': return 'text-orange-600 bg-orange-100';
      case 'in_stock': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStockStatusLabel = (status) => {
    switch (status) {
      case 'out_of_stock': return 'Out of Stock';
      case 'low_stock': return 'Low Stock';
      case 'in_stock': return 'In Stock';
      default: return 'Unknown';
    }
  };



  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium text-gray-900">
          Warehouse Inventory Reporting
        </h3>
        <button
          onClick={exportReport}
          disabled={!reportData || loading}
          className="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50"
        >
          Export CSV
        </button>
      </div>

      {/* Report Configuration */}
      <div className="bg-white p-6 rounded-lg border border-gray-200">
        <h4 className="text-md font-medium text-gray-900 mb-4">Report Configuration</h4>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
          {/* Report Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Report Type
            </label>
            <select
              value={reportType}
              onChange={(e) => setReportType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="summary">Summary Report</option>
              <option value="detailed">Detailed Inventory</option>
              <option value="movement">Movement Analysis</option>
              <option value="valuation">Inventory Valuation</option>
            </select>
          </div>

          {/* Date Range */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              From Date
            </label>
            <input
              type="date"
              value={dateRange.start_date}
              onChange={(e) => handleDateRangeChange('start_date', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              To Date
            </label>
            <input
              type="date"
              value={dateRange.end_date}
              onChange={(e) => handleDateRangeChange('end_date', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Stock Status Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Stock Status
            </label>
            <select
              value={filters.stock_status}
              onChange={(e) => handleFilterChange('stock_status', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Items</option>
              <option value="in_stock">In Stock</option>
              <option value="low_stock">Low Stock</option>
              <option value="out_of_stock">Out of Stock</option>
            </select>
          </div>
        </div>

        {/* Warehouse Selection */}
        <div className="mb-4">
          <div className="flex justify-between items-center mb-2">
            <label className="block text-sm font-medium text-gray-700">
              Select Warehouses
            </label>
            <div className="space-x-2">
              <button
                onClick={handleSelectAllWarehouses}
                className="text-xs text-blue-600 hover:text-blue-800"
              >
                Select All
              </button>
              <button
                onClick={handleDeselectAllWarehouses}
                className="text-xs text-gray-600 hover:text-gray-800"
              >
                Deselect All
              </button>
            </div>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
            {warehouses.map((warehouse) => (
              <label key={warehouse.id} className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={selectedWarehouses.includes(warehouse.id)}
                  onChange={() => handleWarehouseToggle(warehouse.id)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">{warehouse.name}</span>
              </label>
            ))}
          </div>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center p-8">
          <div className="text-gray-500">Generating report...</div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Report Results */}
      {reportData && !loading && (
        <div className="space-y-6">
          {/* Summary Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div key="total-items" className="bg-white p-4 rounded-lg border border-gray-200">
              <div className="text-sm font-medium text-gray-500">Total Items</div>
              <div className="text-2xl font-bold text-gray-900">
                {formatNumber(reportData.summary?.total_items || 0)}
              </div>
            </div>

            <div key="total-value" className="bg-white p-4 rounded-lg border border-gray-200">
              <div className="text-sm font-medium text-gray-500">Total Value</div>
              <div className="text-2xl font-bold text-green-600">
                {formatCurrency(reportData.summary?.total_value || 0)}
              </div>
            </div>

            <div key="low-stock" className="bg-white p-4 rounded-lg border border-gray-200">
              <div className="text-sm font-medium text-gray-500">Low Stock Items</div>
              <div className="text-2xl font-bold text-orange-600">
                {formatNumber(reportData.summary?.low_stock_items || 0)}
              </div>
            </div>

            <div key="out-of-stock" className="bg-white p-4 rounded-lg border border-gray-200">
              <div className="text-sm font-medium text-gray-500">Out of Stock</div>
              <div className="text-2xl font-bold text-red-600">
                {formatNumber(reportData.summary?.out_of_stock_items || 0)}
              </div>
            </div>
          </div>

          {/* Detailed Report Table */}
          {reportData.items && reportData.items.length > 0 && (
            <div className="bg-white shadow overflow-hidden sm:rounded-md">
              <div className="px-4 py-5 sm:px-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900">
                  Detailed Report
                </h3>
                <p className="mt-1 max-w-2xl text-sm text-gray-500">
                  {reportData.items.length} items across {selectedWarehouses.length} warehouse{selectedWarehouses.length !== 1 ? 's' : ''}
                </p>
              </div>

              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Warehouse
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Part
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Current Stock
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Min Stock
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Est. Value
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {reportData.items.map((item, index) => (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {item.warehouse_name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {item.part_name}
                            </div>
                            <div className="text-sm text-gray-500">
                              {item.part_number}
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {formatNumber(item.current_stock)} {item.unit_of_measure}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {formatNumber(item.minimum_stock_recommendation)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStockStatusColor(item.stock_status)}`}>
                            {getStockStatusLabel(item.stock_status)}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {formatCurrency(item.estimated_value || 0)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Warehouse Breakdown */}
          {reportData.warehouse_breakdown && (
            <div className="bg-white p-6 rounded-lg border border-gray-200">
              <h4 className="text-md font-medium text-gray-900 mb-4">Warehouse Breakdown</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {reportData.warehouse_breakdown.map((warehouse, index) => (
                  <div key={`warehouse-${warehouse.warehouse_id}-${index}`} className="border border-gray-200 rounded-lg p-4">
                    <h5 className="font-medium text-gray-900 mb-2">{warehouse.warehouse_name}</h5>
                    <div className="space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Total Items:</span>
                        <span className="font-medium">{formatNumber(warehouse.total_items)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Total Value:</span>
                        <span className="font-medium">{formatCurrency(warehouse.total_value)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Low Stock:</span>
                        <span className="font-medium text-orange-600">{formatNumber(warehouse.low_stock_items)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Out of Stock:</span>
                        <span className="font-medium text-red-600">{formatNumber(warehouse.out_of_stock_items)}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* No Data State */}
      {reportData && reportData.items && reportData.items.length === 0 && !loading && (
        <div className="bg-gray-50 p-8 rounded-lg text-center">
          <div className="text-gray-500">
            No inventory data found for the selected criteria.
          </div>
        </div>
      )}
    </div>
  );
};

export default WarehouseInventoryReporting;