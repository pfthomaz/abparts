// frontend/src/pages/Dashboard.js

import React, { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { dashboardService } from '../services/dashboardService';
import { isSuperAdmin, hasPermission, PERMISSIONS } from '../utils/permissions';
import PermissionGuard from '../components/PermissionGuard';
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

// Modern metric card component with better visual design
const MetricCard = ({
  title,
  value,
  linkTo,
  icon,
  bgColor = 'bg-white',
  textColor = 'text-gray-900',
  accentColor = 'text-blue-600',
  borderColor = 'border-gray-200',
  subtitle = null
}) => (
  <Link
    to={linkTo}
    className={`group block ${bgColor} ${borderColor} border rounded-2xl p-6 shadow-sm hover:shadow-md transition-all duration-300 hover:scale-105 hover:border-blue-300`}
  >
    <div className="flex items-center justify-between mb-4">
      <div className={`p-3 rounded-xl ${accentColor.replace('text-', 'bg-').replace('-600', '-100')} group-hover:scale-110 transition-transform duration-300`}>
        {icon}
      </div>
      <div className="text-right">
        <div className={`text-3xl font-bold ${textColor} group-hover:text-blue-600 transition-colors duration-300`}>
          {value}
        </div>
      </div>
    </div>
    <div>
      <h3 className="text-sm font-semibold text-gray-600 uppercase tracking-wider mb-1">{title}</h3>
      {subtitle && (
        <p className="text-xs text-gray-500">{subtitle}</p>
      )}
    </div>
  </Link>
);

// Icon components
const PartIcon = () => (
  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
    <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
  </svg>
);

const InventoryIcon = () => (
  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
    <path d="M4 3a2 2 0 100 4h12a2 2 0 100-4H4z" />
    <path fillRule="evenodd" d="M3 8h14v7a2 2 0 01-2 2H5a2 2 0 01-2-2V8zm5 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" clipRule="evenodd" />
  </svg>
);

const WarningIcon = () => (
  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
  </svg>
);

const OrderIcon = () => (
  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
    <path fillRule="evenodd" d="M6 2a2 2 0 00-2 2v12a2 2 0 002 2h8a2 2 0 002-2V4a2 2 0 00-2-2H6zm1 2a1 1 0 000 2h6a1 1 0 100-2H7zm6 7a1 1 0 011 1v3a1 1 0 11-2 0v-3a1 1 0 011-1zm-3 3a1 1 0 100 2h.01a1 1 0 100-2H10zm-4 1a1 1 0 011-1h.01a1 1 0 110 2H7a1 1 0 01-1-1zm1-4a1 1 0 100 2h.01a1 1 0 100-2H7zm2 0a1 1 0 100 2h.01a1 1 0 100-2H9zm2 0a1 1 0 100 2h.01a1 1 0 100-2H11z" clipRule="evenodd" />
  </svg>
);

const Dashboard = () => {
  const { user } = useAuth();
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

  // Loading state with skeleton
  if (loading) {
    return (
      <div className="space-y-8">
        <div className="flex justify-between items-start">
          <div>
            <div className="h-8 bg-gray-200 rounded w-48 mb-2 animate-pulse"></div>
            <div className="h-4 bg-gray-200 rounded w-32 animate-pulse"></div>
          </div>
          <div className="text-right space-y-2">
            <div className="h-4 bg-gray-200 rounded w-40 animate-pulse"></div>
            <div className="h-3 bg-gray-200 rounded w-32 animate-pulse"></div>
            <div className="h-3 bg-gray-200 rounded w-36 animate-pulse"></div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-24 mb-4"></div>
              <div className="h-8 bg-gray-200 rounded w-16"></div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {[...Array(2)].map((_, i) => (
            <div key={i} className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 animate-pulse">
              <div className="h-6 bg-gray-200 rounded w-32 mb-4"></div>
              <div className="h-64 bg-gray-200 rounded"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-start">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        </div>
        <div className="bg-red-50 border border-red-200 text-red-800 px-6 py-4 rounded-xl" role="alert">
          <div className="flex items-center space-x-2">
            <svg className="w-5 h-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <div>
              <strong className="font-semibold">Error loading dashboard</strong>
              <p className="mt-1">{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header Section */}
        <div className="mb-8">
          <div className="flex flex-col lg:flex-row lg:justify-between lg:items-center space-y-4 lg:space-y-0">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">
                Good {new Date().getHours() < 12 ? 'morning' : new Date().getHours() < 18 ? 'afternoon' : 'evening'}!
              </h1>
              <p className="text-lg text-gray-600">Welcome back, {user.name || user.username}</p>
            </div>

            <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-4 shadow-lg border border-white/20">
              <div className="text-right space-y-1">
                <div className="flex items-center justify-end space-x-2">
                  <span className="text-sm font-semibold text-gray-900">
                    {user.role === 'super_admin' ? 'Super Administrator' :
                      user.role === 'admin' ? 'Administrator' : 'User'}
                  </span>
                  {isSuperAdmin(user) && (
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-sm">
                      Global Access
                    </span>
                  )}
                </div>
                {!isSuperAdmin(user) && user.organization && (
                  <p className="text-sm text-gray-600 font-medium">{user.organization.name}</p>
                )}
                <p className="text-xs text-gray-500">
                  Scope: {isSuperAdmin(user) ? 'All Organizations' : 'Organization Only'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Metrics Cards */}
        {metrics && (
          <div className="mb-8">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
              <PermissionGuard permission={PERMISSIONS.VIEW_PARTS} hideIfNoPermission={true}>
                <MetricCard
                  title="Total Parts"
                  value={metrics.total_parts}
                  linkTo="/parts"
                  icon={<PartIcon />}
                  accentColor="text-blue-600"
                  subtitle="Active catalog items"
                />
              </PermissionGuard>

              <PermissionGuard permission={PERMISSIONS.VIEW_INVENTORY} hideIfNoPermission={true}>
                <MetricCard
                  title="Inventory Items"
                  value={metrics.total_inventory_items}
                  linkTo="/inventory"
                  icon={<InventoryIcon />}
                  accentColor="text-green-600"
                  subtitle="Items in stock"
                />
              </PermissionGuard>

              <PermissionGuard permission={PERMISSIONS.VIEW_INVENTORY} hideIfNoPermission={true}>
                <MetricCard
                  title="Low Stock Items"
                  value={metrics.low_stock_items}
                  linkTo="/inventory"
                  icon={<WarningIcon />}
                  bgColor={metrics.low_stock_items > 0 ? 'bg-gradient-to-br from-amber-50 to-orange-50' : 'bg-white'}
                  textColor={metrics.low_stock_items > 0 ? 'text-amber-900' : 'text-gray-900'}
                  accentColor={metrics.low_stock_items > 0 ? 'text-amber-600' : 'text-gray-600'}
                  borderColor={metrics.low_stock_items > 0 ? 'border-amber-200' : 'border-gray-200'}
                  subtitle={metrics.low_stock_items > 0 ? 'Requires attention' : 'All items stocked'}
                />
              </PermissionGuard>

              <PermissionGuard permission={PERMISSIONS.ORDER_PARTS} hideIfNoPermission={true}>
                <MetricCard
                  title="Customer Orders"
                  value={metrics.pending_customer_orders}
                  linkTo="/orders"
                  icon={<OrderIcon />}
                  bgColor={metrics.pending_customer_orders > 0 ? 'bg-gradient-to-br from-blue-50 to-cyan-50' : 'bg-white'}
                  textColor={metrics.pending_customer_orders > 0 ? 'text-blue-900' : 'text-gray-900'}
                  accentColor={metrics.pending_customer_orders > 0 ? 'text-blue-600' : 'text-gray-600'}
                  borderColor={metrics.pending_customer_orders > 0 ? 'border-blue-200' : 'border-gray-200'}
                  subtitle={metrics.pending_customer_orders > 0 ? 'Pending processing' : 'All processed'}
                />
              </PermissionGuard>

              <PermissionGuard permission={PERMISSIONS.ORDER_PARTS} hideIfNoPermission={true}>
                <MetricCard
                  title="Supplier Orders"
                  value={metrics.pending_supplier_orders}
                  linkTo="/orders"
                  icon={<OrderIcon />}
                  bgColor={metrics.pending_supplier_orders > 0 ? 'bg-gradient-to-br from-red-50 to-pink-50' : 'bg-white'}
                  textColor={metrics.pending_supplier_orders > 0 ? 'text-red-900' : 'text-gray-900'}
                  accentColor={metrics.pending_supplier_orders > 0 ? 'text-red-600' : 'text-gray-600'}
                  borderColor={metrics.pending_supplier_orders > 0 ? 'border-red-200' : 'border-gray-200'}
                  subtitle={metrics.pending_supplier_orders > 0 ? 'Awaiting delivery' : 'All delivered'}
                />
              </PermissionGuard>

              {/* Always show user info card for users who might not have other permissions */}
              {(!hasPermission(user, PERMISSIONS.VIEW_PARTS) &&
                !hasPermission(user, PERMISSIONS.VIEW_INVENTORY) &&
                !hasPermission(user, PERMISSIONS.ORDER_PARTS)) && (
                  <div className="col-span-full">
                    <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-lg border border-white/20 text-center">
                      <div className="flex items-center justify-center mb-4">
                        <div className="p-3 bg-blue-100 rounded-xl">
                          <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                          </svg>
                        </div>
                      </div>
                      <h3 className="text-xl font-bold text-gray-900 mb-2">Welcome to ABParts</h3>
                      <p className="text-gray-600 mb-4">
                        You're successfully logged in as {user.role === 'admin' ? 'an Administrator' : 'a User'}.
                      </p>
                      <p className="text-sm text-gray-500">
                        Contact your administrator if you need access to additional features.
                      </p>
                    </div>
                  </div>
                )}
            </div>
          </div>
        )}

        {/* Charts Section */}
        <div className="mb-8">
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
            <PermissionGuard permission={PERMISSIONS.ORDER_PARTS} hideIfNoPermission={true}>
              <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 overflow-hidden">
                <div className="bg-gradient-to-r from-blue-500 to-purple-600 px-6 py-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-bold text-white">Pending Orders Overview</h3>
                    <div className="flex items-center space-x-2 text-blue-100">
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" />
                      </svg>
                      <span className="text-sm font-medium">Real-time</span>
                    </div>
                  </div>
                </div>
                <div className="p-6">
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={pendingOrdersData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis
                        dataKey="name"
                        tick={{ fontSize: 12, fill: '#64748b' }}
                        axisLine={{ stroke: '#cbd5e1' }}
                      />
                      <YAxis
                        allowDecimals={false}
                        tick={{ fontSize: 12, fill: '#64748b' }}
                        axisLine={{ stroke: '#cbd5e1' }}
                      />
                      <Tooltip
                        cursor={{ fill: 'rgba(59, 130, 246, 0.1)' }}
                        contentStyle={{
                          backgroundColor: 'rgba(255, 255, 255, 0.95)',
                          border: '1px solid #e2e8f0',
                          borderRadius: '12px',
                          boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)',
                          backdropFilter: 'blur(10px)'
                        }}
                      />
                      <Bar dataKey="Pending" radius={[6, 6, 0, 0]}>
                        {pendingOrdersData.map((entry, index) => (
                          <Bar key={`cell-${index}`} fill={entry.fill} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </PermissionGuard>

            <PermissionGuard permission={PERMISSIONS.VIEW_INVENTORY} hideIfNoPermission={true}>
              <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 overflow-hidden">
                <div className="bg-gradient-to-r from-amber-500 to-orange-600 px-6 py-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-bold text-white">Low Stock by Organization</h3>
                    <div className="flex items-center space-x-2 text-amber-100">
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                      </svg>
                      <span className="text-sm font-medium">Current status</span>
                    </div>
                  </div>
                </div>
                <div className="p-6">
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={lowStockData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis
                        dataKey="organization_name"
                        tick={{ fontSize: 12, fill: '#64748b' }}
                        axisLine={{ stroke: '#cbd5e1' }}
                      />
                      <YAxis
                        allowDecimals={false}
                        tick={{ fontSize: 12, fill: '#64748b' }}
                        axisLine={{ stroke: '#cbd5e1' }}
                      />
                      <Tooltip
                        cursor={{ fill: 'rgba(245, 158, 11, 0.1)' }}
                        contentStyle={{
                          backgroundColor: 'rgba(255, 255, 255, 0.95)',
                          border: '1px solid #e2e8f0',
                          borderRadius: '12px',
                          boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1)',
                          backdropFilter: 'blur(10px)'
                        }}
                      />
                      <Legend />
                      <Bar
                        dataKey="low_stock_count"
                        name="Low Stock Count"
                        fill="#f59e0b"
                        radius={[6, 6, 0, 0]}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </PermissionGuard>
          </div>
        </div>

        {/* Quick Actions Section */}
        <div className="bg-white/60 backdrop-blur-sm rounded-2xl p-8 shadow-xl border border-white/20">
          <div className="flex items-center space-x-3 mb-6">
            <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-gray-900">Quick Actions</h3>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <PermissionGuard permission={PERMISSIONS.VIEW_PARTS} hideIfNoPermission={true}>
              <Link
                to="/parts"
                className="group flex items-center space-x-4 p-4 bg-white/80 backdrop-blur-sm rounded-xl shadow-md border border-white/20 hover:shadow-lg hover:scale-105 transition-all duration-300"
              >
                <div className="p-2 bg-blue-100 rounded-lg group-hover:bg-blue-200 transition-colors duration-300">
                  <PartIcon />
                </div>
                <span className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors duration-300">Manage Parts</span>
              </Link>
            </PermissionGuard>

            <PermissionGuard permission={PERMISSIONS.VIEW_INVENTORY} hideIfNoPermission={true}>
              <Link
                to="/inventory"
                className="group flex items-center space-x-4 p-4 bg-white/80 backdrop-blur-sm rounded-xl shadow-md border border-white/20 hover:shadow-lg hover:scale-105 transition-all duration-300"
              >
                <div className="p-2 bg-green-100 rounded-lg group-hover:bg-green-200 transition-colors duration-300">
                  <InventoryIcon />
                </div>
                <span className="font-semibold text-gray-900 group-hover:text-green-600 transition-colors duration-300">Check Inventory</span>
              </Link>
            </PermissionGuard>

            <PermissionGuard permission={PERMISSIONS.ORDER_PARTS} hideIfNoPermission={true}>
              <Link
                to="/orders"
                className="group flex items-center space-x-4 p-4 bg-white/80 backdrop-blur-sm rounded-xl shadow-md border border-white/20 hover:shadow-lg hover:scale-105 transition-all duration-300"
              >
                <div className="p-2 bg-purple-100 rounded-lg group-hover:bg-purple-200 transition-colors duration-300">
                  <OrderIcon />
                </div>
                <span className="font-semibold text-gray-900 group-hover:text-purple-600 transition-colors duration-300">View Orders</span>
              </Link>
            </PermissionGuard>

            <PermissionGuard permission={PERMISSIONS.VIEW_WAREHOUSES} hideIfNoPermission={true}>
              <Link
                to="/warehouses"
                className="group flex items-center space-x-4 p-4 bg-white/80 backdrop-blur-sm rounded-xl shadow-md border border-white/20 hover:shadow-lg hover:scale-105 transition-all duration-300"
              >
                <div className="p-2 bg-indigo-100 rounded-lg group-hover:bg-indigo-200 transition-colors duration-300">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2H4zm0 2h12v8H4V6z" clipRule="evenodd" />
                  </svg>
                </div>
                <span className="font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors duration-300">Warehouses</span>
              </Link>
            </PermissionGuard>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
