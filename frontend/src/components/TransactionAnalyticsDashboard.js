// frontend/src/components/TransactionAnalyticsDashboard.js

import React, { useState, useEffect } from 'react';
import { transactionService } from '../services/transactionService';
import { useAuth } from '../AuthContext';
import PermissionGuard from './PermissionGuard';
import { PERMISSIONS } from '../utils/permissions';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell
} from 'recharts';

const TransactionAnalyticsDashboard = () => {
  const { user } = useAuth();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState(30); // days

  useEffect(() => {
    const fetchAnalytics = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await transactionService.getTransactionAnalytics(timeRange);
        setAnalytics(data);
      } catch (err) {
        setError(err.message || 'Failed to fetch transaction analytics.');
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [timeRange]);

  const handleTimeRangeChange = (e) => {
    setTimeRange(parseInt(e.target.value));
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  if (loading) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <strong className="font-bold">Error: </strong>
          <span>{error}</span>
        </div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <p className="text-gray-500 text-center">No analytics data available.</p>
      </div>
    );
  }

  return (
    <PermissionGuard permission={PERMISSIONS.VIEW_ORG_TRANSACTIONS}>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-800">Transaction Analytics</h2>
          <div>
            <label htmlFor="timeRange" className="block text-sm font-medium text-gray-700 mb-1">
              Time Range
            </label>
            <select
              id="timeRange"
              value={timeRange}
              onChange={handleTimeRangeChange}
              className="px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
              <option value={365}>Last year</option>
            </select>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold text-gray-700 mb-2">Total Transactions</h3>
            <p className="text-3xl font-bold text-blue-600">{analytics.summary?.total_transactions || 0}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold text-gray-700 mb-2">Total Value</h3>
            <p className="text-3xl font-bold text-green-600">
              ${(analytics.summary?.total_value || 0).toLocaleString()}
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold text-gray-700 mb-2">Most Active Part</h3>
            <p className="text-lg font-semibold text-gray-800">
              {analytics.summary?.most_active_part?.name || 'N/A'}
            </p>
            <p className="text-sm text-gray-500">
              {analytics.summary?.most_active_part?.transaction_count || 0} transactions
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold text-gray-700 mb-2">Most Active Warehouse</h3>
            <p className="text-lg font-semibold text-gray-800">
              {analytics.summary?.most_active_warehouse?.name || 'N/A'}
            </p>
            <p className="text-sm text-gray-500">
              {analytics.summary?.most_active_warehouse?.transaction_count || 0} transactions
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Transaction Types Distribution */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold text-gray-700 mb-4">Transaction Types</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={analytics.transaction_types || []}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {(analytics.transaction_types || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Daily Transaction Volume */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold text-gray-700 mb-4">Daily Transaction Volume</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={analytics.daily_volume || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="date"
                  tickFormatter={(value) => new Date(value).toLocaleDateString()}
                />
                <YAxis />
                <Tooltip
                  labelFormatter={(value) => new Date(value).toLocaleDateString()}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="count"
                  stroke="#8884d8"
                  strokeWidth={2}
                  name="Transactions"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Top Parts by Transaction Count */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold text-gray-700 mb-4">Most Active Parts</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={analytics.top_parts || []} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="part_name" type="category" width={100} />
                <Tooltip />
                <Bar dataKey="transaction_count" fill="#8884d8" name="Transactions" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Warehouse Activity */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold text-gray-700 mb-4">Warehouse Activity</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={analytics.warehouse_activity || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="warehouse_name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="inbound" stackId="a" fill="#00C49F" name="Inbound" />
                <Bar dataKey="outbound" stackId="a" fill="#FF8042" name="Outbound" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Transaction Trends */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-xl font-semibold text-gray-700 mb-4">Transaction Trends by Type</h3>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={analytics.trends || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                tickFormatter={(value) => new Date(value).toLocaleDateString()}
              />
              <YAxis />
              <Tooltip
                labelFormatter={(value) => new Date(value).toLocaleDateString()}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="creation"
                stroke="#00C49F"
                strokeWidth={2}
                name="Creation"
              />
              <Line
                type="monotone"
                dataKey="transfer"
                stroke="#0088FE"
                strokeWidth={2}
                name="Transfer"
              />
              <Line
                type="monotone"
                dataKey="consumption"
                stroke="#FF8042"
                strokeWidth={2}
                name="Consumption"
              />
              <Line
                type="monotone"
                dataKey="adjustment"
                stroke="#FFBB28"
                strokeWidth={2}
                name="Adjustment"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </PermissionGuard>
  );
};

export default TransactionAnalyticsDashboard;