// frontend/src/pages/Dashboard.js

import React, { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { dashboardService } from '../services/dashboardService';
import { isSuperAdmin, hasPermission, PERMISSIONS, getContextualPermissions } from '../utils/permissions';
import PermissionGuard from '../components/PermissionGuard';
import OrganizationSelector from '../components/OrganizationSelector';
import { useTranslation } from '../hooks/useTranslation';
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

// Enhanced Dashboard box component for three-column layout with mobile-first touch-friendly design
const DashboardBox = ({
  title,
  value,
  linkTo,
  icon,
  bgColor = 'bg-white',
  textColor = 'text-gray-900',
  accentColor = 'text-blue-600',
  borderColor = 'border-gray-200',
  subtitle = null,
  onClick = null,
  alertLevel = null, // 'warning', 'error', 'success'
  showBadge = false,
  badgeText = null
}) => {
  // Alert styling based on level
  const getAlertStyling = () => {
    switch (alertLevel) {
      case 'error':
        return {
          bgColor: 'bg-red-50',
          borderColor: 'border-red-200',
          accentColor: 'text-red-600',
          textColor: 'text-red-900'
        };
      case 'warning':
        return {
          bgColor: 'bg-yellow-50',
          borderColor: 'border-yellow-200',
          accentColor: 'text-yellow-600',
          textColor: 'text-yellow-900'
        };
      case 'success':
        return {
          bgColor: 'bg-green-50',
          borderColor: 'border-green-200',
          accentColor: 'text-green-600',
          textColor: 'text-green-900'
        };
      default:
        return { bgColor, borderColor, accentColor, textColor };
    }
  };

  const styling = getAlertStyling();

  const content = (
    <div className={`group block ${styling.bgColor} ${styling.borderColor} border rounded-xl 
      p-3 sm:p-4 shadow-sm hover:shadow-md transition-all duration-300 
      hover:scale-105 hover:border-blue-300 cursor-pointer relative
      min-h-[100px] sm:min-h-[110px] 
      touch-manipulation select-none
      active:scale-95 active:shadow-lg
      focus:outline-none focus:ring-4 focus:ring-blue-200 focus:ring-opacity-50`}>

      {/* Badge for notifications - larger on mobile */}
      {showBadge && badgeText && (
        <div className="absolute -top-2 -right-2 bg-red-500 text-white text-xs sm:text-sm font-bold 
          px-2 py-1 sm:px-3 sm:py-1.5 rounded-full min-w-[24px] sm:min-w-[28px] text-center
          shadow-lg border-2 border-white">
          {badgeText}
        </div>
      )}

      <div className="flex items-center justify-between mb-2 sm:mb-3">
        <div className={`p-2 sm:p-2 rounded-lg ${styling.accentColor.replace('text-', 'bg-').replace('-600', '-100')} 
          group-hover:scale-110 transition-transform duration-300 shadow-sm`}>
          <div className="w-5 h-5 sm:w-5 sm:h-5">
            {icon}
          </div>
        </div>
        <div className="text-right">
          <div className={`text-2xl sm:text-2xl font-bold ${styling.textColor} 
            group-hover:text-blue-600 transition-colors duration-300`}>
            {value}
          </div>
        </div>
      </div>
      <div>
        <h3 className="text-base sm:text-sm font-semibold text-gray-700 mb-1 sm:mb-1">{title}</h3>
        {subtitle && (
          <p className="text-sm sm:text-xs text-gray-500 leading-relaxed">{subtitle}</p>
        )}
      </div>
    </div>
  );

  if (onClick) {
    return <div onClick={onClick} role="button" tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onClick()}>{content}</div>;
  }

  return linkTo ? <Link to={linkTo}>{content}</Link> : content;
};

// Enhanced Action button component with mobile-first touch-friendly design
const ActionButton = ({
  title,
  description,
  linkTo,
  icon,
  color = 'blue',
  onClick = null,
  disabled = false,
  shortcut = null,
  priority = 'normal' // 'high', 'normal', 'low'
}) => {
  const colorClasses = {
    blue: 'bg-blue-50 hover:bg-blue-100 active:bg-blue-200 text-blue-700 border-blue-200',
    green: 'bg-green-50 hover:bg-green-100 active:bg-green-200 text-green-700 border-green-200',
    purple: 'bg-purple-50 hover:bg-purple-100 active:bg-purple-200 text-purple-700 border-purple-200',
    orange: 'bg-orange-50 hover:bg-orange-100 active:bg-orange-200 text-orange-700 border-orange-200',
    red: 'bg-red-50 hover:bg-red-100 active:bg-red-200 text-red-700 border-red-200',
    teal: 'bg-teal-50 hover:bg-teal-100 active:bg-teal-200 text-teal-700 border-teal-200',
  };

  const priorityClasses = {
    high: 'ring-2 ring-blue-300 shadow-lg',
    normal: '',
    low: 'opacity-75'
  };

  const content = (
    <div className={`group block border rounded-xl 
      p-4 sm:p-4 transition-all duration-300 hover:scale-105 cursor-pointer relative 
      ${colorClasses[color]} ${priorityClasses[priority]} 
      ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
      min-h-[100px] sm:min-h-[90px]
      touch-manipulation select-none
      active:scale-95 active:shadow-lg
      focus:outline-none focus:ring-4 focus:ring-opacity-50
      ${color === 'blue' ? 'focus:ring-blue-200' :
        color === 'green' ? 'focus:ring-green-200' :
          color === 'purple' ? 'focus:ring-purple-200' :
            color === 'orange' ? 'focus:ring-orange-200' :
              color === 'red' ? 'focus:ring-red-200' : 'focus:ring-teal-200'}`}>

      {/* Shortcut indicator - hidden on mobile */}
      {shortcut && (
        <div className="absolute top-2 right-2 text-xs bg-white/80 px-2 py-1 rounded-md font-mono text-gray-500
          hidden sm:block">
          {shortcut}
        </div>
      )}

      <div className="flex items-center space-x-3 sm:space-x-3 mb-3 sm:mb-2">
        <div className="p-3 sm:p-2 bg-white rounded-lg shadow-sm group-hover:scale-110 transition-transform duration-300">
          <div className="w-6 h-6 sm:w-5 sm:h-5">
            {icon}
          </div>
        </div>
        <h3 className="font-semibold text-base sm:text-sm">{title}</h3>
      </div>
      <p className="text-sm sm:text-sm opacity-80 leading-relaxed">{description}</p>
    </div>
  );

  if (disabled) {
    return <div className="cursor-not-allowed">{content}</div>;
  }

  if (onClick) {
    return <div onClick={onClick} role="button" tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onClick()}>{content}</div>;
  }

  return linkTo ? <Link to={linkTo}>{content}</Link> : content;
};

// Enhanced Report card component with mobile-first touch-friendly design
const ReportCard = ({
  title,
  description,
  linkTo,
  icon,
  color = 'indigo',
  onClick = null,
  dataValue = null,
  trend = null, // 'up', 'down', 'stable'
  lastUpdated = null
}) => {
  const colorClasses = {
    indigo: 'bg-indigo-50 hover:bg-indigo-100 active:bg-indigo-200 text-indigo-700 border-indigo-200',
    teal: 'bg-teal-50 hover:bg-teal-100 active:bg-teal-200 text-teal-700 border-teal-200',
    pink: 'bg-pink-50 hover:bg-pink-100 active:bg-pink-200 text-pink-700 border-pink-200',
    amber: 'bg-amber-50 hover:bg-amber-100 active:bg-amber-200 text-amber-700 border-amber-200',
    emerald: 'bg-emerald-50 hover:bg-emerald-100 active:bg-emerald-200 text-emerald-700 border-emerald-200',
    violet: 'bg-violet-50 hover:bg-violet-100 active:bg-violet-200 text-violet-700 border-violet-200',
  };

  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <svg className="w-4 h-4 sm:w-3 sm:h-3 text-green-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M3.293 9.707a1 1 0 010-1.414l6-6a1 1 0 011.414 0l6 6a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L4.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" /></svg>;
      case 'down':
        return <svg className="w-4 h-4 sm:w-3 sm:h-3 text-red-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 10.293a1 1 0 010 1.414l-6 6a1 1 0 01-1.414 0l-6-6a1 1 0 111.414-1.414L9 14.586V3a1 1 0 012 0v11.586l4.293-4.293a1 1 0 011.414 0z" clipRule="evenodd" /></svg>;
      case 'stable':
        return <svg className="w-4 h-4 sm:w-3 sm:h-3 text-gray-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" /></svg>;
      default:
        return null;
    }
  };

  const content = (
    <div className={`group block border rounded-xl 
      p-4 sm:p-4 transition-all duration-300 hover:scale-105 cursor-pointer 
      ${colorClasses[color]}
      min-h-[110px] sm:min-h-[100px]
      touch-manipulation select-none
      active:scale-95 active:shadow-lg
      focus:outline-none focus:ring-4 focus:ring-opacity-50
      ${color === 'indigo' ? 'focus:ring-indigo-200' :
        color === 'teal' ? 'focus:ring-teal-200' :
          color === 'pink' ? 'focus:ring-pink-200' :
            color === 'amber' ? 'focus:ring-amber-200' :
              color === 'emerald' ? 'focus:ring-emerald-200' : 'focus:ring-violet-200'}`}>

      <div className="flex items-center justify-between mb-3 sm:mb-2">
        <div className="flex items-center space-x-3">
          <div className="p-3 sm:p-2 bg-white rounded-lg shadow-sm group-hover:scale-110 transition-transform duration-300">
            <div className="w-6 h-6 sm:w-5 sm:h-5">
              {icon}
            </div>
          </div>
          <h3 className="font-semibold text-base sm:text-sm">{title}</h3>
        </div>
        {dataValue && (
          <div className="flex items-center space-x-1 sm:space-x-1">
            <span className="text-xl sm:text-lg font-bold">{dataValue}</span>
            {getTrendIcon()}
          </div>
        )}
      </div>
      <p className="text-sm sm:text-sm opacity-80 mb-2 leading-relaxed">{description}</p>
      {lastUpdated && (
        <p className="text-xs text-gray-500">Updated {lastUpdated}</p>
      )}
    </div>
  );

  if (onClick) {
    return <div onClick={onClick} role="button" tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onClick()}>{content}</div>;
  }

  return linkTo ? <Link to={linkTo}>{content}</Link> : content;
};

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
  const { t } = useTranslation();
  const { user } = useAuth();
  const [metrics, setMetrics] = useState(null);
  const [lowStockData, setLowStockData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedOrganization, setSelectedOrganization] = useState(null);
  const fetchMetrics = async () => {
    try {
      setLoading(true);
      setError('');
      const [metricsData, lowStockChartData] = await Promise.all([
        dashboardService.getMetrics(),
        dashboardService.getLowStockByOrg(),
      ]);
      // console.log('DEBUG: Received metrics data:', metricsData);
      // console.log('DEBUG: total_farm_sites =', metricsData?.total_farm_sites);
      // console.log('DEBUG: total_nets =', metricsData?.total_nets);
      setMetrics(metricsData);
      setLowStockData(lowStockChartData);
    } catch (err) {
      setError(err.message || 'Failed to load dashboard metrics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, [selectedOrganization]);

  // Auto-refresh every 5 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      fetchMetrics();
    }, 5 * 60 * 1000);

    return () => clearInterval(interval);
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
          {/* Good afternoon greeting card with rounded corners */}
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/20 mb-4">
            <div className="flex items-center space-x-4">
              <div>
                <h1 className="text-4xl font-bold text-gray-900 mb-2">
                  {t(`dashboard.${new Date().getHours() < 12 ? 'goodMorning' : new Date().getHours() < 18 ? 'goodAfternoon' : 'goodEvening'}`)}!
                </h1>
                <p className="text-lg text-gray-600">{t('dashboard.welcomeBack', { name: user.name || user.username })}</p>
                {metrics && (
                  <p className="text-sm text-gray-500 mt-1">
                    {isSuperAdmin(user)
                      ? t('dashboard.managingOrganizations', { organizations: metrics.total_organizations, users: metrics.total_users })
                      : t('dashboard.organizationParts', { organization: user.organization?.name || 'Your organization', parts: metrics.total_inventory_items || 0 })
                    }
                  </p>
                )}
              </div>


            </div>
          </div>

          {/* Global Access card with full width matching the page */}
          <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-4 shadow-md border border-white/30">
            <div className="text-right space-y-2">
              <div className="flex items-center justify-end space-x-2">
                <span className="text-sm font-semibold text-gray-900">
                  {user.role === 'super_admin' ? t('dashboard.superAdministrator') :
                    user.role === 'admin' ? t('dashboard.administrator') : t('dashboard.user')}
                </span>
                {isSuperAdmin(user) && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-sm">
                    {t('dashboard.globalAccess')}
                  </span>
                )}
              </div>
              {!isSuperAdmin(user) && user.organization && (
                <p className="text-sm text-gray-600 font-medium">{user.organization.name}</p>
              )}
              <p className="text-xs text-gray-500">
                {t('common.scope')}: {isSuperAdmin(user) ? t('dashboard.scopeAllOrganizations') : t('dashboard.scopeOrganizationOnly')}
              </p>
              {/* Organization Selector for Superadmin */}
              <OrganizationSelector
                selectedOrganization={selectedOrganization}
                onOrganizationChange={setSelectedOrganization}
              />
            </div>
          </div>
        </div>

        {/* Enhanced Three-Column Dashboard Layout - Mobile-First Responsive */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6 lg:gap-8">
          {/* Column 1: Entities */}
          <div className="space-y-4">
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/20">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                    </svg>
                  </div>
                  <h2 className="text-xl font-bold text-gray-900">{t('dashboard.entities')}</h2>
                </div>
                {/* Context indicator */}
                <div className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                  {isSuperAdmin(user) ? (selectedOrganization ? t('dashboard.contextFiltered') : t('dashboard.contextGlobal')) : t('dashboard.contextOrganization')}
                </div>
              </div>

              <div className="space-y-3">
                {/* Organizations - Superadmin only */}
                <PermissionGuard permission={PERMISSIONS.VIEW_ALL_ORGANIZATIONS} hideIfNoPermission={true}>
                  <DashboardBox
                    title={t('dashboard.organizations')}
                    value={metrics?.total_organizations || '0'}
                    linkTo="/organizations"
                    icon={<svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
                    accentColor="text-purple-600"
                    subtitle={t('dashboard.customersSuppliers', { customers: metrics?.customer_organizations || 0, suppliers: metrics?.supplier_organizations || 0 })}
                  />
                </PermissionGuard>

                {/* Users */}
                <PermissionGuard permission={PERMISSIONS.MANAGE_ORG_USERS} hideIfNoPermission={true}>
                  <DashboardBox
                    title={t('dashboard.users')}
                    value={metrics?.total_users || '0'}
                    linkTo="/users"
                    icon={<svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z" /></svg>}
                    accentColor="text-green-600"
                    subtitle={t('dashboard.activeUsersPending', { active: metrics?.active_users || 0, pending: metrics?.pending_invitations || 0 })}
                    showBadge={metrics?.pending_invitations > 0}
                    badgeText={metrics?.pending_invitations > 0 ? metrics.pending_invitations.toString() : null}
                  />
                </PermissionGuard>

                {/* Warehouses */}
                <PermissionGuard permission={PERMISSIONS.VIEW_WAREHOUSES} hideIfNoPermission={true}>
                  <DashboardBox
                    title={t('dashboard.warehouses')}
                    value={metrics?.total_warehouses || '0'}
                    linkTo="/warehouses"
                    icon={<svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2H4zm0 2h12v8H4V6z" clipRule="evenodd" /></svg>}
                    accentColor="text-indigo-600"
                    subtitle={metrics ? t('dashboard.partsInStock', { count: metrics.total_inventory_items }) : t('dashboard.storageLocations')}
                  />
                </PermissionGuard>

                {/* Machines */}
                <PermissionGuard permission={PERMISSIONS.VIEW_ORG_MACHINES} hideIfNoPermission={true}>
                  <DashboardBox
                    title={t('dashboard.machines')}
                    value={metrics?.total_machines || '0'}
                    linkTo="/machines"
                    icon={<svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" /></svg>}
                    accentColor="text-orange-600"
                    subtitle={t('dashboard.activeMachines', { count: metrics?.active_machines || 0 })}
                  />
                </PermissionGuard>

                {/* Parts */}
                <PermissionGuard permission={PERMISSIONS.VIEW_PARTS} hideIfNoPermission={true}>
                  <DashboardBox
                    title={t('dashboard.parts')}
                    value={metrics?.total_parts || '0'}
                    linkTo="/parts"
                    icon={<PartIcon />}
                    accentColor="text-blue-600"
                    subtitle={metrics?.low_stock_items > 0 ? t('dashboard.lowStockAlerts', { count: metrics.low_stock_items }) : t('dashboard.allPartsInStock')}
                    alertLevel={metrics?.low_stock_items > 0 ? 'warning' : null}
                    showBadge={metrics?.low_stock_items > 0}
                    badgeText={metrics?.low_stock_items > 0 ? metrics.low_stock_items.toString() : null}
                  />
                </PermissionGuard>

                {/* Farms - All users can view */}
                <div>
                  <DashboardBox
                    title={t('dashboard.farms')}
                    value={metrics?.total_farm_sites || '0'}
                    linkTo="/farm-sites"
                    icon={<svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd"/></svg>}
                    accentColor="text-teal-600"
                    subtitle={t('dashboard.farmsSubtitle')}
                  />
                </div>

                {/* Cages - All users can view */}
                <div>
                  <DashboardBox
                    title={t('dashboard.cages')}
                    value={metrics?.total_nets || '0'}
                    linkTo="/nets"
                    icon={<svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"/></svg>}
                    accentColor="text-cyan-600"
                    subtitle={t('dashboard.cagesSubtitle')}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Column 2: Actions */}
          <div className="space-y-6">
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/20">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-gradient-to-r from-green-500 to-teal-600 rounded-xl">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <h2 className="text-xl font-bold text-gray-900">{t('dashboard.quickActions')}</h2>
                </div>
                {/* Role indicator */}
                <div className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                  {user.role === 'super_admin' ? t('dashboard.allActions') : user.role === 'admin' ? t('dashboard.adminActions') : t('dashboard.userActions')}
                </div>
              </div>

              <div className="space-y-4">
                {/* Let's Wash Nets - Primary action for daily operations */}
                <ActionButton
                  title={t('dashboard.letsWashNets')}
                  description={t('dashboard.letsWashNetsDesc')}
                  linkTo="/daily-operations"
                  icon={<svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" /></svg>}
                  color="cyan"
                  priority="high"
                  shortcut="Ctrl+W"
                />

                {/* Record Net Cleaning - Second from top */}
                <div className="mt-4">
                  <ActionButton
                    title={t('dashboard.recordNetCleaning')}
                    description={t('dashboard.recordNetCleaningDesc')}
                    linkTo="/net-cleaning-records"
                    icon={<svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"/><path fillRule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clipRule="evenodd"/></svg>}
                    color="teal"
                    priority="high"
                    shortcut="Ctrl+N"
                  />
                </div>

                {/* Order Parts - High priority for all users */}
                <PermissionGuard permission={PERMISSIONS.ORDER_PARTS} hideIfNoPermission={true}>
                  <ActionButton
                    title={t('dashboard.orderParts')}
                    description={t('dashboard.orderPartsDesc')}
                    linkTo="/orders"
                    icon={<OrderIcon />}
                    color="blue"
                    priority="high"
                    shortcut="Ctrl+O"
                  />
                </PermissionGuard>

                {/* Use Parts - High priority for field operations */}
                <PermissionGuard permission={PERMISSIONS.RECORD_PART_USAGE} hideIfNoPermission={true}>
                  <ActionButton
                    title={t('dashboard.useParts')}
                    description={t('dashboard.usePartsDesc')}
                    linkTo="/transactions"
                    icon={<svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.293l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z" clipRule="evenodd" /></svg>}
                    color="green"
                    priority="high"
                    shortcut="Ctrl+U"
                  />
                </PermissionGuard>

                {/* Record Hours - Important for service tracking */}
                <PermissionGuard permission={PERMISSIONS.VIEW_ORG_MACHINES} hideIfNoPermission={true}>
                  <ActionButton
                    title={t('dashboard.recordHours')}
                    description={t('dashboard.recordHoursDesc')}
                    linkTo="/machines"
                    icon={<svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" /></svg>}
                    color="purple"
                    shortcut="Ctrl+H"
                  />
                </PermissionGuard>

                {/* Adjust Inventory - Admin action */}
                <PermissionGuard permission={PERMISSIONS.ADJUST_INVENTORY} hideIfNoPermission={true}>
                  <ActionButton
                    title={t('dashboard.adjustInventory')}
                    description={t('dashboard.adjustInventoryDesc')}
                    linkTo="/stocktake"
                    icon={<InventoryIcon />}
                    color="orange"
                    shortcut="Ctrl+I"
                  />
                </PermissionGuard>

                {/* Register Machine - Superadmin only */}
                <PermissionGuard permission={PERMISSIONS.REGISTER_MACHINES} hideIfNoPermission={true}>
                  <ActionButton
                    title={t('dashboard.registerMachine')}
                    description={t('dashboard.registerMachineDesc')}
                    linkTo="/machines"
                    icon={<svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" /></svg>}
                    color="red"
                    priority="low"
                  />
                </PermissionGuard>

                {/* Create Organization - Superadmin only */}
                <PermissionGuard permission={PERMISSIONS.MANAGE_ORGANIZATIONS} hideIfNoPermission={true}>
                  <ActionButton
                    title={t('dashboard.createOrganization')}
                    description={t('dashboard.createOrganizationDesc')}
                    linkTo="/organizations"
                    icon={<svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" /></svg>}
                    color="teal"
                    priority="low"
                  />
                </PermissionGuard>

                {/* Invite Users - Admin action */}
                <PermissionGuard permission={PERMISSIONS.INVITE_USERS} hideIfNoPermission={true}>
                  <ActionButton
                    title={t('dashboard.inviteUsers')}
                    description={t('dashboard.inviteUsersDesc')}
                    linkTo="/users"
                    icon={<svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M8 9a3 3 0 100-6 3 3 0 000 6zM8 11a6 6 0 016 6H2a6 6 0 016-6zM16 7a1 1 0 10-2 0v1h-1a1 1 0 100 2h1v1a1 1 0 102 0v-1h1a1 1 0 100-2h-1V7z" /></svg>}
                    color="purple"
                  />
                </PermissionGuard>
              </div>
            </div>
          </div>

          {/* Column 3: Reports & Analytics */}
          <div className="space-y-6">
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/20">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-gradient-to-r from-amber-500 to-orange-600 rounded-xl">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <h2 className="text-xl font-bold text-gray-900">{t('dashboard.reportsAnalytics')}</h2>
                </div>
                {/* Data freshness indicator */}
                <div className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                  {t('dashboard.liveData')}
                </div>
              </div>

              <div className="space-y-4">
                {/* Inventory Reports */}
                <PermissionGuard permission={PERMISSIONS.VIEW_INVENTORY} hideIfNoPermission={true}>
                  <ReportCard
                    title={t('dashboard.inventoryReports')}
                    description={t('dashboard.inventoryReportsDesc')}
                    linkTo="/inventory"
                    icon={<InventoryIcon />}
                    color="indigo"
                    dataValue={`${metrics?.total_inventory_items || 0}`}
                    trend={metrics?.low_stock_items > 0 ? 'down' : 'stable'}
                    lastUpdated={t('dashboard.justNow')}
                  />
                </PermissionGuard>

                {/* Machine Reports */}
                <PermissionGuard permission={PERMISSIONS.VIEW_ORG_MACHINES} hideIfNoPermission={true}>
                  <ReportCard
                    title={t('dashboard.machineReports')}
                    description={t('dashboard.machineReportsDesc')}
                    linkTo="/machines"
                    icon={<svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" /></svg>}
                    color="teal"
                    dataValue={`${metrics?.total_machines || 0}`}
                    trend="stable"
                    lastUpdated={t('dashboard.minAgo', { count: 5 })}
                  />
                </PermissionGuard>

                {/* Transaction Reports */}
                <PermissionGuard permission={PERMISSIONS.VIEW_ORG_TRANSACTIONS} hideIfNoPermission={true}>
                  <ReportCard
                    title={t('dashboard.transactionReports')}
                    description={t('dashboard.transactionReportsDesc')}
                    linkTo="/transactions"
                    icon={<svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" /></svg>}
                    color="pink"
                    dataValue={`${metrics?.recent_transactions || 0}`}
                    trend="stable"
                    lastUpdated={t('dashboard.minAgo', { count: 2 })}
                  />
                </PermissionGuard>

                {/* Order Reports */}
                <PermissionGuard permission={PERMISSIONS.ORDER_PARTS} hideIfNoPermission={true}>
                  <ReportCard
                    title={t('dashboard.orderReports')}
                    description={t('dashboard.orderReportsDesc')}
                    linkTo="/orders"
                    icon={<OrderIcon />}
                    color="violet"
                    dataValue={`${(metrics?.pending_customer_orders || 0) + (metrics?.pending_supplier_orders || 0)}`}
                    trend={((metrics?.pending_customer_orders || 0) + (metrics?.pending_supplier_orders || 0)) > 0 ? 'up' : 'stable'}
                    lastUpdated={t('dashboard.minAgo', { count: 1 })}
                  />
                </PermissionGuard>

                {/* Organization Reports - Superadmin only */}
                <PermissionGuard permission={PERMISSIONS.VIEW_GLOBAL_REPORTS} hideIfNoPermission={true}>
                  <ReportCard
                    title={t('dashboard.organizationReports')}
                    description={t('dashboard.organizationReportsDesc')}
                    linkTo="/organizations"
                    icon={<svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
                    color="amber"
                    dataValue={`${metrics?.total_organizations || 0}`}
                    trend="stable"
                    lastUpdated={t('dashboard.justNow')}
                  />
                </PermissionGuard>

                {/* Warehouse Analytics */}
                <PermissionGuard permission={PERMISSIONS.VIEW_WAREHOUSES} hideIfNoPermission={true}>
                  <ReportCard
                    title={t('dashboard.warehouseAnalytics')}
                    description={t('dashboard.warehouseAnalyticsDesc')}
                    linkTo="/warehouses"
                    icon={<svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2H4zm0 2h12v8H4V6z" clipRule="evenodd" /></svg>}
                    color="emerald"
                    dataValue={`${metrics?.total_warehouses || 0}`}
                    trend="stable"
                    lastUpdated={t('dashboard.minAgo', { count: 3 })}
                  />
                </PermissionGuard>
              </div>
            </div>
          </div>
        </div>

        {/* Enhanced System Status & Alerts Section */}
        {metrics && (
          <div className="mt-8 space-y-6">
            {/* System Status Overview */}
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/20">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">{t('dashboard.systemStatus')}</h3>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-sm text-gray-600">{t('dashboard.allSystemsOperational')}</span>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                {/* Active Users */}
                <div className="text-center p-3 bg-green-50 rounded-lg border border-green-200">
                  <div className="text-2xl font-bold text-green-600">{metrics.active_users}</div>
                  <div className="text-xs text-gray-600 font-medium">{t('dashboard.activeUsers')}</div>
                  <div className="text-xs text-green-600 mt-1">{t('dashboard.onlineNow')}</div>
                </div>

                {/* Low Stock Items */}
                <div className={`text-center p-3 rounded-lg border ${metrics.low_stock_items > 0 ? 'bg-yellow-50 border-yellow-200' : 'bg-green-50 border-green-200'}`}>
                  <div className={`text-2xl font-bold ${metrics.low_stock_items > 0 ? 'text-yellow-600' : 'text-green-600'}`}>
                    {metrics.low_stock_items}
                  </div>
                  <div className="text-xs text-gray-600 font-medium">{t('dashboard.lowStock')}</div>
                  <div className={`text-xs mt-1 ${metrics.low_stock_items > 0 ? 'text-yellow-600' : 'text-green-600'}`}>
                    {metrics.low_stock_items > 0 ? t('dashboard.needsAttention') : t('dashboard.allGood')}
                  </div>
                </div>

                {/* Out of Stock */}
                <div className={`text-center p-3 rounded-lg border ${metrics.out_of_stock_items > 0 ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'}`}>
                  <div className={`text-2xl font-bold ${metrics.out_of_stock_items > 0 ? 'text-red-600' : 'text-green-600'}`}>
                    {metrics.out_of_stock_items}
                  </div>
                  <div className="text-xs text-gray-600 font-medium">{t('dashboard.outOfStock')}</div>
                  <div className={`text-xs mt-1 ${metrics.out_of_stock_items > 0 ? 'text-red-600' : 'text-green-600'}`}>
                    {metrics.out_of_stock_items > 0 ? t('dashboard.critical') : t('dashboard.allStocked')}
                  </div>
                </div>

                {/* Pending Orders */}
                <div className={`text-center p-3 rounded-lg border ${(metrics.pending_customer_orders + metrics.pending_supplier_orders) > 0 ? 'bg-blue-50 border-blue-200' : 'bg-gray-50 border-gray-200'}`}>
                  <div className={`text-2xl font-bold ${(metrics.pending_customer_orders + metrics.pending_supplier_orders) > 0 ? 'text-blue-600' : 'text-gray-400'}`}>
                    {metrics.pending_customer_orders + metrics.pending_supplier_orders}
                  </div>
                  <div className="text-xs text-gray-600 font-medium">{t('dashboard.pendingOrders')}</div>
                  <div className={`text-xs mt-1 ${(metrics.pending_customer_orders + metrics.pending_supplier_orders) > 0 ? 'text-blue-600' : 'text-gray-500'}`}>
                    {(metrics.pending_customer_orders + metrics.pending_supplier_orders) > 0 ? t('dashboard.inProgress') : t('dashboard.noPending')}
                  </div>
                </div>

                {/* Recent Transactions */}
                <div className="text-center p-3 bg-purple-50 rounded-lg border border-purple-200">
                  <div className="text-2xl font-bold text-purple-600">{metrics.recent_transactions}</div>
                  <div className="text-xs text-gray-600 font-medium">{t('dashboard.recentActivity')}</div>
                  <div className="text-xs text-purple-600 mt-1">{t('dashboard.last24h')}</div>
                </div>

                {/* Total Warehouses */}
                <div className="text-center p-3 bg-indigo-50 rounded-lg border border-indigo-200">
                  <div className="text-2xl font-bold text-indigo-600">{metrics.total_warehouses}</div>
                  <div className="text-xs text-gray-600 font-medium">{t('dashboard.warehouses')}</div>
                  <div className="text-xs text-indigo-600 mt-1">{t('dashboard.activeLocations')}</div>
                </div>
              </div>
            </div>

            {/* Alerts & Notifications */}
            {(metrics.low_stock_items > 0 || metrics.out_of_stock_items > 0 || metrics.pending_invitations > 0) && (
              <div className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-2xl p-6 shadow-lg border border-yellow-200">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="p-2 bg-yellow-500 rounded-xl">
                    <WarningIcon />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900">{t('dashboard.attentionRequired')}</h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {metrics.out_of_stock_items > 0 && (
                    <div className="bg-white rounded-lg p-4 border border-red-200">
                      <div className="flex items-center space-x-2 mb-2">
                        <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                        <span className="font-semibold text-red-700">{t('dashboard.criticalStockAlert')}</span>
                      </div>
                      <p className="text-sm text-gray-600">{t('dashboard.partsOutOfStock', { count: metrics.out_of_stock_items })}</p>
                      <Link to="/inventory" className="text-sm text-red-600 hover:text-red-800 font-medium mt-2 inline-block">
                        {t('dashboard.viewDetails')} →
                      </Link>
                    </div>
                  )}

                  {metrics.low_stock_items > 0 && (
                    <div className="bg-white rounded-lg p-4 border border-yellow-200">
                      <div className="flex items-center space-x-2 mb-2">
                        <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                        <span className="font-semibold text-yellow-700">{t('dashboard.lowStockWarning')}</span>
                      </div>
                      <p className="text-sm text-gray-600">{t('dashboard.partsRunningLow', { count: metrics.low_stock_items })}</p>
                      <Link to="/inventory" className="text-sm text-yellow-600 hover:text-yellow-800 font-medium mt-2 inline-block">
                        {t('dashboard.reorderNow')} →
                      </Link>
                    </div>
                  )}

                  {metrics.pending_invitations > 0 && (
                    <div className="bg-white rounded-lg p-4 border border-blue-200">
                      <div className="flex items-center space-x-2 mb-2">
                        <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                        <span className="font-semibold text-blue-700">{t('dashboard.pendingInvitations')}</span>
                      </div>
                      <p className="text-sm text-gray-600">{t('dashboard.invitationsAwaiting', { count: metrics.pending_invitations })}</p>
                      <Link to="/users" className="text-sm text-blue-600 hover:text-blue-800 font-medium mt-2 inline-block">
                        {t('dashboard.manageUsers')} →
                      </Link>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Charts Section - Below the three columns */}
        {(hasPermission(user, PERMISSIONS.ORDER_PARTS) || hasPermission(user, PERMISSIONS.VIEW_INVENTORY)) && (
          <div className="mt-8">
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
              <PermissionGuard permission={PERMISSIONS.ORDER_PARTS} hideIfNoPermission={true}>
                <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 overflow-hidden">
                  <div className="bg-gradient-to-r from-blue-500 to-purple-600 px-6 py-4">
                    <div className="flex items-center justify-between">
                      <h3 className="text-lg font-bold text-white">{t('dashboard.pendingOrdersOverview')}</h3>
                      <div className="flex items-center space-x-2 text-blue-100">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" />
                        </svg>
                        <span className="text-sm font-medium">{t('dashboard.realTime')}</span>
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
                      <h3 className="text-lg font-bold text-white">{t('dashboard.lowStockByOrganization')}</h3>
                      <div className="flex items-center space-x-2 text-amber-100">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                        </svg>
                        <span className="text-sm font-medium">{t('dashboard.currentStatus')}</span>
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
        )}
      </div>
    </div>
  );
};

export default Dashboard;
