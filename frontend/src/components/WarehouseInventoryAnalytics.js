// frontend/src/components/WarehouseInventoryAnalytics.js

import React, { useState, useEffect } from 'react';
import { inventoryService } from '../services/inventoryService';
import { warehouseService } from '../services/warehouseService';

const WarehouseInventoryAnalytics = ({ warehouseId, warehouse }) => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dateRange, setDateRange] = useState({
    start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 30 days ago
    end_date: new Date().toISOString().split('T')[0] // today
  });

  useEffect(() => {
    if (warehouseId) {
      fetchAnalytics();
    }
  }, [warehouseId, dateRange]);

  const fetchAnalytics = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await inventoryService.getWarehouseInventoryAnalytics(warehouseId, dateRange);
      setAnalytics(data);
    } catch (err) {
      setError('Failed to fetch warehouse analytics');
      console.error('Failed to fetch warehouse analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDateRangeChange = (field, value) => {
    setDateRange(prev => ({
      ...prev,
      [field]: value
    }));
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

  const formatPercentage = (value) => {
    return `${(value || 0).toFixed(1)}%`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-gray-500">Loading analytics...</div>
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

  if (!analytics) {
    return (
      <div className="bg-gray-50 p-8 rounded-lg text-center">
        <div className="text-gray-500">No analytics data available</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium text-gray-900">
          Inventory Analytics
          {warehouse && (
            <span className="text-sm font-normal text-gray-500 ml-2">
              - {warehouse.name}
            </span>
          )}
        </h3>

        {/* Date Range Selector */}
        <div className="flex items-center space-x-2">
          <label className="text-sm text-gray-700">From:</label>
          <input
            type="date"
            value={dateRange.start_date}
            onChange={(e) => handleDateRangeChange('start_date', e.target.value)}
            className="px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <label className="text-sm text-gray-700">To:</label>
          <input
            type="date"
            value={dateRange.end_date}
            onChange={(e) => handleDateRangeChange('end_date', e.target.value)}
            className="px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm font-medium text-gray-500">Total Parts</div>
          <div className="text-2xl font-bold text-gray-900">
            {formatNumber(analytics.inventory_summary?.total_parts)}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Unique parts in warehouse
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm font-medium text-gray-500">Total Stock Value</div>
          <div className="text-2xl font-bold text-green-600">
            {formatCurrency(analytics.inventory_summary?.total_value)}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Estimated inventory value
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm font-medium text-gray-500">Average Turnover</div>
          <div className="text-2xl font-bold text-blue-600">
            {formatNumber(analytics.turnover_metrics?.average_turnover_days)} days
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Average days between transactions
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm font-medium text-gray-500">Net Stock Change</div>
          <div className={`text-2xl font-bold ${parseFloat(analytics.stock_movements?.net_change || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {formatNumber(analytics.stock_movements?.net_change)}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Net inventory movement
          </div>
        </div>
      </div>

      {/* Stock Status Breakdown */}
      <div className="bg-white p-6 rounded-lg border border-gray-200">
        <h4 className="text-md font-medium text-gray-900 mb-4">Stock Status Breakdown</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">
              {formatNumber((analytics.inventory_summary?.total_parts || 0) - (analytics.inventory_summary?.low_stock_parts || 0) - (analytics.inventory_summary?.out_of_stock_parts || 0))}
            </div>
            <div className="text-sm text-gray-500">In Stock</div>
            <div className="text-xs text-gray-400">
              {analytics.inventory_summary?.total_parts > 0 ?
                formatPercentage(((analytics.inventory_summary.total_parts - analytics.inventory_summary.low_stock_parts - analytics.inventory_summary.out_of_stock_parts) / analytics.inventory_summary.total_parts) * 100) :
                '0%'
              }
            </div>
          </div>

          <div className="text-center">
            <div className="text-3xl font-bold text-orange-600">
              {formatNumber(analytics.inventory_summary?.low_stock_parts)}
            </div>
            <div className="text-sm text-gray-500">Low Stock</div>
            <div className="text-xs text-gray-400">
              {analytics.inventory_summary?.total_parts > 0 ?
                formatPercentage((analytics.inventory_summary.low_stock_parts / analytics.inventory_summary.total_parts) * 100) :
                '0%'
              }
            </div>
          </div>

          <div className="text-center">
            <div className="text-3xl font-bold text-red-600">
              {formatNumber(analytics.inventory_summary?.out_of_stock_parts)}
            </div>
            <div className="text-sm text-gray-500">Out of Stock</div>
            <div className="text-xs text-gray-400">
              {analytics.inventory_summary?.total_parts > 0 ?
                formatPercentage((analytics.inventory_summary.out_of_stock_parts / analytics.inventory_summary.total_parts) * 100) :
                '0%'
              }
            </div>
          </div>
        </div>
      </div>

      {/* Activity Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h4 className="text-md font-medium text-gray-900 mb-4">Stock Movements</h4>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Total Inbound</span>
              <span className="text-sm font-medium text-green-600">
                {formatNumber(analytics.stock_movements?.total_inbound)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Total Outbound</span>
              <span className="text-sm font-medium text-red-600">
                {formatNumber(analytics.stock_movements?.total_outbound)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Net Change</span>
              <span className={`text-sm font-medium ${parseFloat(analytics.stock_movements?.net_change || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatNumber(analytics.stock_movements?.net_change)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Fast Moving Parts</span>
              <span className="text-sm font-medium text-blue-600">
                {formatNumber(analytics.turnover_metrics?.fast_moving_parts)}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h4 className="text-md font-medium text-gray-900 mb-4">Top Parts by Value</h4>
          {analytics.top_parts_by_value && analytics.top_parts_by_value.length > 0 ? (
            <div className="space-y-3">
              {analytics.top_parts_by_value.slice(0, 5).map((part, index) => (
                <div key={index} className="flex justify-between items-center">
                  <div className="flex-1">
                    <div className="text-sm font-medium text-gray-900">
                      {part.part_name}
                    </div>
                    <div className="text-xs text-gray-500">
                      Qty: {formatNumber(part.quantity)}
                    </div>
                  </div>
                  <div className="text-sm font-medium text-blue-600">
                    {formatCurrency(part.total_value)}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-sm text-gray-500">No parts data available</div>
          )}
        </div>
      </div>

      {/* Analytics Period Info */}
      <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
        <h4 className="text-md font-medium text-blue-900 mb-4">Analytics Period</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <span className="text-blue-700 font-medium">Period:</span>
            <div className="text-blue-800">{analytics.analytics_period?.days} days</div>
          </div>
          <div>
            <span className="text-blue-700 font-medium">From:</span>
            <div className="text-blue-800">
              {analytics.analytics_period?.start_date ?
                new Date(analytics.analytics_period.start_date).toLocaleDateString() :
                'N/A'
              }
            </div>
          </div>
          <div>
            <span className="text-blue-700 font-medium">To:</span>
            <div className="text-blue-800">
              {analytics.analytics_period?.end_date ?
                new Date(analytics.analytics_period.end_date).toLocaleDateString() :
                'N/A'
              }
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WarehouseInventoryAnalytics;