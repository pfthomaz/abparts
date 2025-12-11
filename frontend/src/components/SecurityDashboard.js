// frontend/src/components/SecurityDashboard.js

import React, { useState, useEffect } from 'react';
import { userService } from '../services/userService';
import { useAuth } from '../AuthContext';

const SecurityDashboard = () => {
  const { user } = useAuth();
  const [securityMetrics, setSecurityMetrics] = useState({
    activeSessions: 0,
    recentLogins: 0,
    failedAttempts: 0,
    suspiciousActivity: 0,
    lastPasswordChange: null,
    accountStatus: 'active'
  });
  const [recentActivity, setRecentActivity] = useState([]);
  const [securityAlerts, setSecurityAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSecurityDashboardData();
  }, []);

  const fetchSecurityDashboardData = async () => {
    try {
      setLoading(true);

      // Fetch multiple security-related data points
      const [sessions, events, profile] = await Promise.all([
        userService.getMySessions().catch(() => []),
        userService.getSecurityEvents({ limit: 10 }).catch(() => []),
        userService.getMyProfile().catch(() => ({}))
      ]);

      // Calculate security metrics
      const activeSessions = sessions.length;
      const recentLogins = events.filter(e =>
        e.event_type === 'login' &&
        e.success &&
        new Date(e.timestamp) > new Date(Date.now() - 24 * 60 * 60 * 1000)
      ).length;

      const failedAttempts = profile.failed_login_attempts || 0;

      const suspiciousActivity = events.filter(e =>
        e.event_type === 'suspicious_activity' ||
        (e.event_type === 'failed_login' && new Date(e.timestamp) > new Date(Date.now() - 24 * 60 * 60 * 1000))
      ).length;

      setSecurityMetrics({
        activeSessions,
        recentLogins,
        failedAttempts,
        suspiciousActivity,
        lastPasswordChange: profile.last_password_change,
        accountStatus: profile.user_status || 'active'
      });

      setRecentActivity(events.slice(0, 5));

      // Generate security alerts based on the data
      const alerts = [];

      if (failedAttempts >= 3) {
        alerts.push({
          id: 'failed-attempts',
          type: 'warning',
          title: 'Multiple Failed Login Attempts',
          message: `${failedAttempts} failed login attempts detected. Consider changing your password.`,
          action: 'Change Password'
        });
      }

      if (activeSessions > 3) {
        alerts.push({
          id: 'many-sessions',
          type: 'info',
          title: 'Multiple Active Sessions',
          message: `You have ${activeSessions} active sessions. Review and terminate any unfamiliar ones.`,
          action: 'Review Sessions'
        });
      }

      if (profile.last_password_change) {
        const daysSincePasswordChange = Math.floor(
          (Date.now() - new Date(profile.last_password_change)) / (1000 * 60 * 60 * 24)
        );
        if (daysSincePasswordChange > 90) {
          alerts.push({
            id: 'old-password',
            type: 'warning',
            title: 'Password Needs Update',
            message: `Your password was last changed ${daysSincePasswordChange} days ago. Consider updating it.`,
            action: 'Change Password'
          });
        }
      }

      if (suspiciousActivity > 0) {
        alerts.push({
          id: 'suspicious-activity',
          type: 'error',
          title: 'Suspicious Activity Detected',
          message: `${suspiciousActivity} suspicious activities detected in the last 24 hours.`,
          action: 'Review Activity'
        });
      }

      setSecurityAlerts(alerts);

    } catch (error) {
      console.error('Failed to fetch security dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getAlertColor = (type) => {
    switch (type) {
      case 'error': return 'bg-red-50 border-red-200 text-red-800';
      case 'warning': return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      case 'info': return 'bg-blue-50 border-blue-200 text-blue-800';
      default: return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  const getAlertIcon = (type) => {
    switch (type) {
      case 'error': return '🚨';
      case 'warning': return '⚠️';
      case 'info': return 'ℹ️';
      default: return '📝';
    }
  };

  const getMetricColor = (metric, value) => {
    switch (metric) {
      case 'failedAttempts':
        if (value >= 4) return 'text-red-600';
        if (value >= 2) return 'text-yellow-600';
        return 'text-green-600';
      case 'suspiciousActivity':
        if (value > 0) return 'text-red-600';
        return 'text-green-600';
      case 'activeSessions':
        if (value > 5) return 'text-yellow-600';
        return 'text-blue-600';
      default:
        return 'text-gray-600';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString();
  };

  const getEventIcon = (eventType) => {
    switch (eventType) {
      case 'login': return '🔓';
      case 'logout': return '🔒';
      case 'failed_login': return '❌';
      case 'password_change': return '🔑';
      case 'account_locked': return '🚫';
      case 'suspicious_activity': return '⚠️';
      default: return '📝';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <p className="text-gray-600">Loading security dashboard...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-800">Security Dashboard</h2>
        <button
          onClick={fetchSecurityDashboardData}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Refresh
        </button>
      </div>

      {/* Security Alerts */}
      {securityAlerts.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-lg font-semibold text-gray-800">Security Alerts</h3>
          {securityAlerts.map((alert) => (
            <div key={alert.id} className={`border rounded-lg p-4 ${getAlertColor(alert.type)}`}>
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  <span className="text-xl">{getAlertIcon(alert.type)}</span>
                  <div>
                    <h4 className="font-semibold">{alert.title}</h4>
                    <p className="text-sm mt-1">{alert.message}</p>
                  </div>
                </div>
                {alert.action && (
                  <button className="text-sm px-3 py-1 bg-white bg-opacity-50 rounded hover:bg-opacity-75">
                    {alert.action}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Security Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Sessions</p>
              <p className={`text-2xl font-bold ${getMetricColor('activeSessions', securityMetrics.activeSessions)}`}>
                {securityMetrics.activeSessions}
              </p>
            </div>
            <div className="text-3xl">💻</div>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Devices currently logged in
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Recent Logins</p>
              <p className="text-2xl font-bold text-blue-600">
                {securityMetrics.recentLogins}
              </p>
            </div>
            <div className="text-3xl">🔓</div>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Successful logins (24h)
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Failed Attempts</p>
              <p className={`text-2xl font-bold ${getMetricColor('failedAttempts', securityMetrics.failedAttempts)}`}>
                {securityMetrics.failedAttempts}
              </p>
            </div>
            <div className="text-3xl">❌</div>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Failed login attempts
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Suspicious Activity</p>
              <p className={`text-2xl font-bold ${getMetricColor('suspiciousActivity', securityMetrics.suspiciousActivity)}`}>
                {securityMetrics.suspiciousActivity}
              </p>
            </div>
            <div className="text-3xl">⚠️</div>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Alerts in last 24h
          </p>
        </div>
      </div>

      {/* Account Status and Security Info */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow border">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Account Status</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Status</span>
              <span className={`px-2 py-1 text-xs font-semibold rounded-full ${securityMetrics.accountStatus === 'active'
                  ? 'bg-green-100 text-green-800'
                  : securityMetrics.accountStatus === 'locked'
                    ? 'bg-red-100 text-red-800'
                    : 'bg-yellow-100 text-yellow-800'
                }`}>
                {securityMetrics.accountStatus}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Last Password Change</span>
              <span className="text-gray-800">
                {formatDate(securityMetrics.lastPasswordChange)}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">User Role</span>
              <span className="text-gray-800 capitalize">
                {user?.role || 'Unknown'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Organization</span>
              <span className="text-gray-800">
                {user?.organization?.name || 'Unknown'}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Recent Activity</h3>
          {recentActivity.length === 0 ? (
            <p className="text-gray-500 text-center py-4">No recent activity</p>
          ) : (
            <div className="space-y-3">
              {recentActivity.map((event, index) => (
                <div key={event.id || index} className="flex items-center space-x-3">
                  <div className="text-lg">{getEventIcon(event.event_type)}</div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-800">
                      {event.event_type?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </p>
                    <p className="text-xs text-gray-500">
                      {new Date(event.timestamp).toLocaleString()}
                    </p>
                  </div>
                  <div className={`text-xs px-2 py-1 rounded ${event.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                    {event.success ? 'Success' : 'Failed'}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Security Recommendations */}
      <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
        <h3 className="text-lg font-semibold text-blue-800 mb-4">Security Recommendations</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <h4 className="font-medium text-blue-800">Immediate Actions</h4>
            <ul className="space-y-1 text-sm text-blue-700">
              <li className="flex items-start">
                <span className="text-blue-500 mr-2">•</span>
                Review and terminate any unfamiliar active sessions
              </li>
              <li className="flex items-start">
                <span className="text-blue-500 mr-2">•</span>
                Enable all security notifications and alerts
              </li>
              <li className="flex items-start">
                <span className="text-blue-500 mr-2">•</span>
                Update your password if it's older than 90 days
              </li>
            </ul>
          </div>
          <div className="space-y-2">
            <h4 className="font-medium text-blue-800">Best Practices</h4>
            <ul className="space-y-1 text-sm text-blue-700">
              <li className="flex items-start">
                <span className="text-blue-500 mr-2">•</span>
                Use a unique, strong password for this account
              </li>
              <li className="flex items-start">
                <span className="text-blue-500 mr-2">•</span>
                Always log out when using shared computers
              </li>
              <li className="flex items-start">
                <span className="text-blue-500 mr-2">•</span>
                Monitor your account activity regularly
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SecurityDashboard;