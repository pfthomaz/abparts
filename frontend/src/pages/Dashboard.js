// frontend/src/pages/Dashboard.js

import React, { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { dashboardService } from '../services/dashboardService';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

// A simple component for a metric card
const MetricCard = ({ title, value, linkTo, bgColor = 'bg-white', textColor = 'text-gray-800' }) => (
  <Link to={linkTo} className={`p-6 rounded-lg shadow-md transition-transform transform hover:-translate-y-1 ${bgColor}`}>
    <h3 className="text-lg font-semibold text-gray-500">{title}</h3>
    <p className={`text-4xl font-bold ${textColor} mt-2`}>{value}</p>
  </Link>
);

const Dashboard = () => {
  const [metrics, setMetrics] = useState(null);
  const [lowStockData, setLowStockData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        setError('');
        const [metricsData, lowStockChartData] = await Promise.all([
          dashboardService.getMetrics(),
          dashboardService.getLowStockByOrg(),
        ]);
        setMetrics(metricsData);
        setLowStockData(lowStockChartData);
      } catch (err) {
        setError(err.message || 'Failed to load dashboard metrics.');
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, []);

  const pendingOrdersData = useMemo(() => {
    if (!metrics) return [];
    return [
      { name: 'Supplier Orders', Pending: metrics.pending_supplier_orders, fill: '#ef4444' },
      { name: 'Customer Orders', Pending: metrics.pending_customer_orders, fill: '#3b82f6' },
    ];
  }, [metrics]);

  if (loading) {
    return (
      <div>
        <h1 className="text-3xl font-bold text-gray-800 mb-6">Dashboard</h1>
        <p className="text-gray-600">Loading metrics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <h1 className="text-3xl font-bold text-gray-800 mb-6">Dashboard</h1>
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded" role="alert">
          <strong className="font-bold">Error: </strong>
          <span>{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Dashboard</h1>
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
          <MetricCard title="Total Parts" value={metrics.total_parts} linkTo="/parts" />
          <MetricCard title="Inventory Items" value={metrics.total_inventory_items} linkTo="/inventory" />
          <MetricCard title="Low Stock Items" value={metrics.low_stock_items} linkTo="/inventory" bgColor={metrics.low_stock_items > 0 ? 'bg-yellow-200' : 'bg-white'} textColor={metrics.low_stock_items > 0 ? 'text-yellow-800' : 'text-gray-800'} />
          <MetricCard title="Pending Customer Orders" value={metrics.pending_customer_orders} linkTo="/orders" bgColor={metrics.pending_customer_orders > 0 ? 'bg-blue-200' : 'bg-white'} textColor={metrics.pending_customer_orders > 0 ? 'text-blue-800' : 'text-gray-800'} />
          <MetricCard title="Pending Supplier Orders" value={metrics.pending_supplier_orders} linkTo="/orders" bgColor={metrics.pending_supplier_orders > 0 ? 'bg-red-200' : 'bg-white'} textColor={metrics.pending_supplier_orders > 0 ? 'text-red-800' : 'text-gray-800'} />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-8">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-xl font-semibold text-gray-700 mb-4">Pending Orders</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={pendingOrdersData} margin={{ top: 5, right: 20, left: -10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis allowDecimals={false} />
              <Tooltip cursor={{fill: 'rgba(243, 244, 246, 0.5)'}} />
              <Bar dataKey="Pending" fill="#8884d8">
                {pendingOrdersData.map((entry, index) => (
                  <Bar key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-xl font-semibold text-gray-700 mb-4">Low Stock Items by Organization</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={lowStockData} margin={{ top: 5, right: 20, left: -10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="organization_name" />
              <YAxis allowDecimals={false} />
              <Tooltip cursor={{fill: 'rgba(243, 244, 246, 0.5)'}} />
              <Legend />
              <Bar dataKey="low_stock_count" name="Low Stock Count" fill="#f59e0b" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
