// frontend/src/components/WarehousePerformanceDashboard.js

import React, { useState, useEffect, useCallback } from 'react';
import { warehouseService } from '../services/warehouseService';
import WarehouseInventoryView from './WarehouseInventoryView';
import WarehouseCapacityManagement from './WarehouseCapacityManagement';

const WarehousePerformanceDashboard = ({ warehouseId, warehouse }) => {
  const [performanceData, setPerformanceData] = useState(null);
  const [utilizationData, setUtilizationData] = useState(null);
  const [summaryData, setSummaryData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dateRange, setDateRange] = useState({
    start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 30 days ago
    end_date: new Date().toISOString().split('T')[0] // today
  });
  const [activeTab, setActiveTab] = useState('performance');

  const fetchWarehouseData = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const [performance, utilization, summary] = await Promise.all([
        warehouseService.getWarehousePerformance(warehouseId, dateRange).catch(() => null),
        warehouseService.getWarehouseUtilization(warehouseId).catch(() => null),
        warehouseService.getWarehouseSummary(warehouseId).catch(() => null)
      ]);

      setPerformanceData(performance);
      setUtilizationData(utilization);
      setSummaryData(summary);
    } catch (err) {
      setError('Failed to fetch warehouse data');
      console.error('Failed to fetch warehouse data:', err);
    } finally {
      setLoading(false);
    }
  }, [warehouseId, dateRange]);

  useEffect(() => {
    if (warehouseId) {
      fetchWarehouseData();
    }
  }, [warehouseId, fetchWarehouseData]);

  const handleDateRangeChange = (field, value) => {
    setDateRange(prev => ({
      ...prev,
      [field]: value
    }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-gray-500">Loading warehouse performance data...</div>
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
    <div className="space-y-6">
      {/* Header with Tabs */}
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-medium text-gray-900">
            Warehouse Dashboard
            {warehouse && (
              <span className="text-sm font-normal text-gray-500 ml-2">
                - {warehouse.name}
              </span>
            )}
          </h3>

          {/* Tab Navigation */}
          <div className="mt-4 flex space-x-1 bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setActiveTab('performance')}
              className={`px-3 py-1 rounded text-sm font-medium ${activeTab === 'performance'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
                }`}
            >
              Performance
            </button>
            <button
              onClick={() => setActiveTab('inventory')}
              className={`px-3 py-1 rounded text-sm font-medium ${activeTab === 'inventory'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
                }`}
            >
              Inventory
            </button>
            <button
              onClick={() => setActiveTab('capacity')}
              className={`px-3 py-1 rounded text-sm font-medium ${activeTab === 'capacity'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
                }`}
            >
              Capacity
            </button>
          </div>
        </div>

        {/* Date Range Selector */}
        <div className="flex items-center space-x-2">
          <label className="text-sm text-gray-700">From:</label>
          <input
            type="date"
            value={dateRange.start_date}
            onChange={(e) => handleDateRangeChange('start_date', e.target.value)}
            className="px-2 py-1 border border-gray-300 rounded text-sm"
          />
          <label className="text-sm text-gray-700">To:</label>
          <input
            type="date"
            value={dateRange.end_date}
            onChange={(e) => handleDateRangeChange('end_date', e.target.value)}
            className="px-2 py-1 border border-gray-300 rounded text-sm"
          />
        </div>
      </div>

      {/* Performance Tab */}
      {activeTab === 'performance' && (
        <div className="space-y-6">
          {/* Summary Cards */}
          {summaryData && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-white p-4 rounded-lg border border-gray-200">
                <div className="text-sm font-medium text-gray-500">Total Parts</div>
                <div className="text-2xl font-bold text-gray-900">
                  {summaryData.total_parts || 0}
                </div>
              </div>

              <div className="bg-white p-4 rounded-lg border border-gray-200">
                <div className="text-sm font-medium text-gray-500">Total Stock Value</div>
                <div className="text-2xl font-bold text-green-600">
                  ${(summaryData.total_stock_value || 0).toLocaleString()}
                </div>
              </div>

              <div className="bg-white p-4 rounded-lg border border-gray-200">
                <div className="text-sm font-medium text-gray-500">Low Stock Items</div>
                <div className="text-2xl font-bold text-orange-600">
                  {summaryData.low_stock_items || 0}
                </div>
              </div>

              <div className="bg-white p-4 rounded-lg border border-gray-200">
                <div className="text-sm font-medium text-gray-500">Out of Stock</div>
                <div className="text-2xl font-bold text-red-600">
                  {summaryData.out_of_stock_items || 0}
                </div>
              </div>
            </div>
          )}

          {/* Performance Metrics */}
          {performanceData && (
            <div className="bg-white p-6 rounded-lg border border-gray-200">
              <h4 className="text-md font-medium text-gray-900 mb-4">Performance Metrics</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <div className="text-sm font-medium text-gray-500">Total Transactions</div>
                  <div className="text-xl font-bold text-blue-600">
                    {performanceData.total_transactions || 0}
                  </div>
                </div>

                <div>
                  <div className="text-sm font-medium text-gray-500">Parts Received</div>
                  <div className="text-xl font-bold text-green-600">
                    {performanceData.parts_received || 0}
                  </div>
                </div>

                <div>
                  <div className="text-sm font-medium text-gray-500">Parts Consumed</div>
                  <div className="text-xl font-bold text-orange-600">
                    {performanceData.parts_consumed || 0}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Utilization Metrics */}
          {utilizationData && (
            <div className="bg-white p-6 rounded-lg border border-gray-200">
              <h4 className="text-md font-medium text-gray-900 mb-4">Utilization Metrics</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <div className="text-sm font-medium text-gray-500">Storage Utilization</div>
                  <div className="flex items-center mt-2">
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${Math.min(utilizationData.storage_utilization_percent || 0, 100)}%` }}
                      ></div>
                    </div>
                    <span className="ml-2 text-sm font-medium text-gray-900">
                      {(utilizationData.storage_utilization_percent || 0).toFixed(1)}%
                    </span>
                  </div>
                </div>

                <div>
                  <div className="text-sm font-medium text-gray-500">Turnover Rate</div>
                  <div className="text-xl font-bold text-purple-600">
                    {(utilizationData.turnover_rate || 0).toFixed(2)}x
                  </div>
                  <div className="text-sm text-gray-500">per month</div>
                </div>
              </div>
            </div>
          )}

          {/* No Data Message */}
          {!summaryData && !performanceData && !utilizationData && (
            <div className="bg-gray-50 p-8 rounded-lg text-center">
              <div className="text-gray-500">
                No performance data available for this warehouse.
              </div>
            </div>
          )}
        </div>
      )}

      {/* Inventory Tab */}
      {activeTab === 'inventory' && (
        <WarehouseInventoryView
          warehouseId={warehouseId}
          warehouse={warehouse}
        />
      )}

      {/* Capacity Tab */}
      {activeTab === 'capacity' && (
        <WarehouseCapacityManagement
          warehouse={warehouse}
          onUpdate={(updatedWarehouse) => {
            // Handle warehouse update if needed
            console.log('Warehouse updated:', updatedWarehouse);
          }}
        />
      )}
    </div>
  );
};

export default WarehousePerformanceDashboard;