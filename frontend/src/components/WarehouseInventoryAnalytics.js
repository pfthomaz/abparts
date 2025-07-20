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
          <div className="text-sm font-medium text-gray-500">Total Items</div>
          <div className="text-2xl font-bold text-gray-900">
            {formatNumber(analytics.total_items)}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Unique parts in warehouse
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm font-medium text-gray-500">Total Stock Value</div>
          <div className="text-2xl font-bold text-green-600">
            {formatCurrency(analytics.total_stock_value)}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Estimated inventory value
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm font-medium text-gray-500">Turnover Rate</div>
          <div className="text-2xl font-bold text-blue-600">
            {formatPercentage(analytics.turnover_rate)}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Inventory turnover
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border border-gray-200">
          <div className="text-sm font-medium text-gray-500">Stock Accuracy</div>
          <div className="text-2xl font-bold text-purple-600">
            {formatPercentage(analytics.stock_accuracy)}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Based on recent adjustments
          </div>
        </div>
      </div>

      {/* Stock Status Breakdown */}
      <div className="bg-white p-6 rounded-lg border border-gray-200">
        <h4 className="text-md font-medium text-gray-900 mb-4">Stock Status Breakdown</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">
              {formatNumber(analytics.in_stock_items)}
            </div>
            <div className="text-sm text-gray-500">In Stock</div>
            <div className="text-xs text-gray-400">
              {formatPercentage((analytics.in_stock_items / analytics.total_items) * 100)}
            </div>
          </div>

          <div className="text-center">
            <div className="text-3xl font-bold text-orange-600">
              {formatNumber(analytics.low_stock_items)}
            </div>
            <div className="text-sm text-gray-500">Low Stock</div>
            <div className="text-xs text-gray-400">
              {formatPercentage((analytics.low_stock_items / analytics.total_items) * 100)}
            </div>
          </div>

          <div className="text-center">
            <div className="text-3xl font-bold text-red-600">
              {formatNumber(analytics.out_of_stock_items)}
            </div>
            <div className="text-sm text-gray-500">Out of Stock</div>
            <div className="text-xs text-gray-400">
              {formatPercentage((analytics.out_of_stock_items / analytics.total_items) * 100)}
            </div>
          </div>
        </div>
      </div>

      {/* Activity Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h4 className="text-md font-medium text-gray-900 mb-4">Recent Activity</h4>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Adjustments</span>
              <span className="text-sm font-medium text-gray-900">
                {formatNumber(analytics.recent_adjustments)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Transfers In</span>
              <span className="text-sm font-medium text-green-600">
                {formatNumber(analytics.transfers_in)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Transfers Out</span>
              <span className="text-sm font-medium text-red-600">
                {formatNumber(analytics.transfers_out)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Usage Records</span>
              <span className="text-sm font-medium text-gray-900">
                {formatNumber(analytics.usage_records)}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <h4 className="text-md font-medium text-gray-900 mb-4">Top Moving Parts</h4>
          {analytics.top_moving_parts && analytics.top_moving_parts.length > 0 ? (
            <div className="space-y-3">
              {analytics.top_moving_parts.slice(0, 5).map((part, index) => (
                <div key={index} className="flex justify-between items-center">
                  <div className="flex-1">
                    <div className="text-sm font-medium text-gray-900">
                      {part.part_name}
                    </div>
                    <div className="text-xs text-gray-500">
                      {part.part_number}
                    </div>
                  </div>
                  <div className="text-sm font-medium text-blue-600">
                    {formatNumber(part.movement_count)} moves
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-sm text-gray-500">No movement data available</div>
          )}
        </div>
      </div>

      {/* Recommendations */}
      {analytics.recommendations && analytics.recommendations.length > 0 && (
        <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
          <h4 className="text-md font-medium text-blue-900 mb-4">Recommendations</h4>
          <div className="space-y-2">
            {analytics.recommendations.map((recommendation, index) => (
              <div key={index} className="flex items-start space-x-2">
                <div className="flex-shrink-0 w-2 h-2 bg-blue-400 rounded-full mt-2"></div>
                <div className="text-sm text-blue-800">{recommendation}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default WarehouseInventoryAnalytics;