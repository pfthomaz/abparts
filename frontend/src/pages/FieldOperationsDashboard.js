// frontend/src/pages/FieldOperationsDashboard.js

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../AuthContext';
import { useTranslation } from '../hooks/useTranslation';
import { dashboardService } from '../services/dashboardService';

const FieldOperationsDashboard = () => {
  const { user } = useAuth();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const metrics = await dashboardService.getMetrics();
      setStats({
        netsCleanedToday: metrics.nets_cleaned_today || 0,
        servicesCompletedToday: metrics.services_completed_today || 0,
        lowStockAlerts: metrics.low_stock_items || 0
      });
      // TODO: Fetch recent activity from API
      setRecentActivity([]);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return t('dashboard.goodMorning');
    if (hour < 18) return t('dashboard.goodAfternoon');
    return t('dashboard.goodEvening');
  };

  const primaryActions = [
    {
      id: 'wash-nets',
      title: t('fieldOps.washNets'),
      subtitle: t('fieldOps.washNetsDesc'),
      icon: '🌊',
      color: 'from-teal-500 to-cyan-600',
      path: '/net-cleaning-records',
      stats: stats?.netsCleanedToday
    },
    {
      id: 'daily-service',
      title: t('fieldOps.dailyService'),
      subtitle: t('fieldOps.dailyServiceDesc'),
      icon: '🔧',
      color: 'from-orange-500 to-red-600',
      path: '/daily-operations',
      stats: stats?.servicesCompletedToday
    },
    {
      id: 'order-parts',
      title: t('fieldOps.orderParts'),
      subtitle: t('fieldOps.orderPartsDesc'),
      icon: '📦',
      color: 'from-blue-500 to-indigo-600',
      path: '/orders',
      alert: stats?.lowStockAlerts > 0 ? stats.lowStockAlerts : null
    }
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">{t('common.loading')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 pb-20">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">
                {getGreeting()}, {user.name || user.username}!
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                {new Date().toLocaleDateString(undefined, { 
                  weekday: 'long', 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                })}
              </p>
            </div>
            {/* Quick Stats Badge */}
            {stats && (
              <div className="hidden sm:flex items-center space-x-4 text-sm">
                <div className="text-center">
                  <div className="text-2xl font-bold text-teal-600">{stats.netsCleanedToday}</div>
                  <div className="text-gray-600">{t('fieldOps.netsToday')}</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">{stats.servicesCompletedToday}</div>
                  <div className="text-gray-600">{t('fieldOps.servicesToday')}</div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Primary Actions */}
        <div className="space-y-4 mb-8">
          {primaryActions.map((action) => (
            <button
              key={action.id}
              onClick={() => navigate(action.path)}
              className="w-full bg-white rounded-2xl shadow-lg hover:shadow-xl 
                transform transition-all duration-300 hover:scale-[1.02] active:scale-[0.98]
                p-6 text-left relative overflow-hidden group"
            >
              {/* Gradient Background */}
              <div className={`absolute inset-0 bg-gradient-to-r ${action.color} opacity-0 
                group-hover:opacity-10 transition-opacity duration-300`} />
              
              {/* Content */}
              <div className="relative flex items-center space-x-4">
                {/* Icon */}
                <div className={`w-16 h-16 sm:w-20 sm:h-20 rounded-2xl bg-gradient-to-r ${action.color} 
                  flex items-center justify-center text-3xl sm:text-4xl shadow-lg
                  transform group-hover:scale-110 transition-transform duration-300`}>
                  {action.icon}
                </div>
                
                {/* Text */}
                <div className="flex-1">
                  <h3 className="text-xl sm:text-2xl font-bold text-gray-900 mb-1">
                    {action.title}
                  </h3>
                  <p className="text-sm sm:text-base text-gray-600">
                    {action.subtitle}
                  </p>
                  {action.stats !== undefined && (
                    <p className="text-sm text-gray-500 mt-2">
                      {t('fieldOps.completedToday', { count: action.stats })}
                    </p>
                  )}
                </div>

                {/* Badge/Arrow */}
                <div className="flex flex-col items-end space-y-2">
                  {action.alert && (
                    <span className="bg-red-500 text-white text-xs font-bold px-3 py-1 rounded-full">
                      {action.alert}
                    </span>
                  )}
                  <svg 
                    className="w-6 h-6 text-gray-400 group-hover:text-gray-600 group-hover:translate-x-1 transition-all" 
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
            </button>
          ))}
        </div>

        {/* Today's Activity */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900 flex items-center">
              <span className="mr-2">📊</span>
              {t('fieldOps.todaysActivity')}
            </h2>
            <button 
              onClick={() => navigate('/transactions')}
              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              {t('common.viewAll')} →
            </button>
          </div>

          {recentActivity.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🎯</div>
              <p className="text-gray-600 text-lg mb-2">{t('fieldOps.noActivityYet')}</p>
              <p className="text-gray-500 text-sm">{t('fieldOps.startYourDay')}</p>
            </div>
          ) : (
            <div className="space-y-3">
              {recentActivity.map((activity, index) => (
                <div 
                  key={index}
                  className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 
                    flex items-center justify-center text-white font-bold">
                    {activity.user?.charAt(0) || '?'}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{activity.description}</p>
                    <p className="text-xs text-gray-500">{activity.time}</p>
                  </div>
                  <span className="text-green-500">✓</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Quick Links */}
        <div className="mt-6 grid grid-cols-2 gap-4">
          <button
            onClick={() => navigate('/farm-sites')}
            className="bg-white rounded-xl shadow p-4 hover:shadow-md transition-shadow text-center"
          >
            <div className="text-3xl mb-2">🏞️</div>
            <div className="text-sm font-medium text-gray-900">{t('fieldOps.viewFarms')}</div>
          </button>
          <button
            onClick={() => navigate('/machines')}
            className="bg-white rounded-xl shadow p-4 hover:shadow-md transition-shadow text-center"
          >
            <div className="text-3xl mb-2">⚙️</div>
            <div className="text-sm font-medium text-gray-900">{t('fieldOps.viewMachines')}</div>
          </button>
        </div>

        {/* Link to Full Dashboard */}
        <div className="mt-6 text-center">
          <button
            onClick={() => navigate('/dashboard')}
            className="text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            {t('fieldOps.viewFullDashboard')} →
          </button>
        </div>
      </div>
    </div>
  );
};

export default FieldOperationsDashboard;
