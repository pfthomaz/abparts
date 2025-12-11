// frontend/src/components/SessionsTab.js

import React, { useEffect, useState } from 'react';

const SessionsTab = ({
  sessions,
  loadingSessions,
  fetchSessions,
  handleTerminateSession,
  handleTerminateAllSessions
}) => {
  const [sessionSettings, setSessionSettings] = useState({
    autoLogoutWarning: true,
    rememberDevice: false,
    sessionTimeout: 8, // hours
    sessionNotifications: true,
    suspiciousActivityDetection: true
  });
  const [showTerminateConfirm, setShowTerminateConfirm] = useState(null);
  const [showTerminateAllConfirm, setShowTerminateAllConfirm] = useState(false);
  const [autoRefreshEnabled, setAutoRefreshEnabled] = useState(true);

  useEffect(() => {
    fetchSessions();
    // Set up auto-refresh every 30 seconds if enabled
    if (autoRefreshEnabled) {
      const interval = setInterval(fetchSessions, 30000);
      return () => clearInterval(interval);
    }
  }, [fetchSessions, autoRefreshEnabled]);

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    return new Date(dateString).toLocaleString();
  };

  const getTimeAgo = (dateString) => {
    if (!dateString) return 'Unknown';
    const now = new Date();
    const date = new Date(dateString);
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minutes ago`;
    if (diffHours < 24) return `${diffHours} hours ago`;
    return `${diffDays} days ago`;
  };

  const getSessionStatus = (session) => {
    if (!session.expires_at) return 'active';
    const now = new Date();
    const expiresAt = new Date(session.expires_at);
    const timeLeft = expiresAt - now;
    const hoursLeft = timeLeft / (1000 * 60 * 60);

    if (timeLeft <= 0) return 'expired';
    if (hoursLeft <= 1) return 'expiring';
    return 'active';
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'expiring': return 'bg-yellow-100 text-yellow-800';
      case 'expired': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getDeviceIcon = (userAgent) => {
    if (!userAgent) return '🖥️';

    const ua = userAgent.toLowerCase();
    if (ua.includes('mobile') || ua.includes('android') || ua.includes('iphone')) {
      return '📱';
    } else if (ua.includes('tablet') || ua.includes('ipad')) {
      return '📱';
    } else {
      return '🖥️';
    }
  };

  const getBrowserName = (userAgent) => {
    if (!userAgent) return 'Unknown Browser';

    const ua = userAgent.toLowerCase();
    if (ua.includes('chrome')) return 'Chrome';
    if (ua.includes('firefox')) return 'Firefox';
    if (ua.includes('safari')) return 'Safari';
    if (ua.includes('edge')) return 'Edge';
    if (ua.includes('opera')) return 'Opera';
    return 'Unknown Browser';
  };

  const getLocationFromIP = (ipAddress) => {
    // Mock location detection - in real implementation this would come from backend
    const mockLocations = {
      '192.168.1.1': 'Local Network',
      '10.0.0.1': 'Office Network',
      '203.0.113.1': 'New York, NY',
      '198.51.100.1': 'San Francisco, CA'
    };
    return mockLocations[ipAddress] || 'Unknown Location';
  };

  const handleSessionSettingChange = (setting, value) => {
    setSessionSettings(prev => ({
      ...prev,
      [setting]: value
    }));
    // In real implementation, this would save to backend
    // userService.updateSessionSettings({ [setting]: value });
  };

  const confirmTerminateSession = (sessionToken) => {
    setShowTerminateConfirm(sessionToken);
  };

  const confirmTerminateAllSessions = () => {
    setShowTerminateAllConfirm(true);
  };

  const executeTerminateSession = async (sessionToken) => {
    await handleTerminateSession(sessionToken);
    setShowTerminateConfirm(null);
  };

  const executeTerminateAllSessions = async () => {
    await handleTerminateAllSessions();
    setShowTerminateAllConfirm(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-800">Active Sessions</h3>
        <div className="space-x-3">
          <button
            onClick={fetchSessions}
            disabled={loadingSessions}
            className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 disabled:opacity-50"
          >
            {loadingSessions ? 'Refreshing...' : 'Refresh'}
          </button>
          <button
            onClick={confirmTerminateAllSessions}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
          >
            Terminate All Sessions
          </button>
        </div>
      </div>

      {/* Session Settings */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h4 className="text-md font-semibold text-gray-800 mb-3">Session Settings</h4>
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-gray-800 font-medium">Auto-logout Warning</p>
              <p className="text-sm text-gray-600">Warn me before session expires</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={sessionSettings.autoLogoutWarning}
                onChange={(e) => handleSessionSettingChange('autoLogoutWarning', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div className="flex justify-between items-center">
            <div>
              <p className="text-gray-800 font-medium">Remember Device</p>
              <p className="text-sm text-gray-600">Stay logged in on this device longer</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={sessionSettings.rememberDevice}
                onChange={(e) => handleSessionSettingChange('rememberDevice', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div className="flex justify-between items-center">
            <div>
              <p className="text-gray-800 font-medium">Session Timeout</p>
              <p className="text-sm text-gray-600">Hours before automatic logout</p>
            </div>
            <select
              value={sessionSettings.sessionTimeout}
              onChange={(e) => handleSessionSettingChange('sessionTimeout', parseInt(e.target.value))}
              className="px-3 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={1}>1 hour</option>
              <option value={2}>2 hours</option>
              <option value={4}>4 hours</option>
              <option value={8}>8 hours</option>
              <option value={12}>12 hours</option>
              <option value={24}>24 hours</option>
            </select>
          </div>

          <div className="flex justify-between items-center">
            <div>
              <p className="text-gray-800 font-medium">Session Notifications</p>
              <p className="text-sm text-gray-600">Get notified about new sessions</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={sessionSettings.sessionNotifications}
                onChange={(e) => handleSessionSettingChange('sessionNotifications', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div className="flex justify-between items-center">
            <div>
              <p className="text-gray-800 font-medium">Suspicious Activity Detection</p>
              <p className="text-sm text-gray-600">Monitor for unusual session activity</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={sessionSettings.suspiciousActivityDetection}
                onChange={(e) => handleSessionSettingChange('suspiciousActivityDetection', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div className="flex justify-between items-center">
            <div>
              <p className="text-gray-800 font-medium">Auto-refresh Sessions</p>
              <p className="text-sm text-gray-600">Automatically refresh session list every 30 seconds</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={autoRefreshEnabled}
                onChange={(e) => setAutoRefreshEnabled(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
        </div>
      </div>

      <div className="bg-yellow-50 p-4 rounded-lg">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <span className="text-yellow-600 text-xl">⚠️</span>
          </div>
          <div className="ml-3">
            <h4 className="text-sm font-medium text-yellow-800">Session Management</h4>
            <p className="text-sm text-yellow-700 mt-1">
              Sessions automatically expire after 8 hours of inactivity. Terminating all sessions will log you out immediately.
              If you see any suspicious sessions, terminate them immediately and change your password.
            </p>
          </div>
        </div>
      </div>

      {loadingSessions ? (
        <div className="flex items-center justify-center py-8">
          <p className="text-gray-600">Loading sessions...</p>
        </div>
      ) : sessions.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-600">No active sessions found</p>
        </div>
      ) : (
        <div className="space-y-4">
          {sessions.map((session, index) => {
            const sessionStatus = getSessionStatus(session);
            return (
              <div key={session.token || index} className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div className="flex items-start space-x-3">
                    <div className="text-2xl">
                      {getDeviceIcon(session.user_agent)}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <h4 className="text-md font-semibold text-gray-800">
                          {getBrowserName(session.user_agent)}
                        </h4>
                        {session.is_current && (
                          <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                            Current Session
                          </span>
                        )}
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(sessionStatus)}`}>
                          {sessionStatus.charAt(0).toUpperCase() + sessionStatus.slice(1)}
                        </span>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-gray-600">
                        <div>
                          <span className="font-medium">IP Address:</span> {session.ip_address || 'Unknown'}
                        </div>
                        <div>
                          <span className="font-medium">Location:</span> {getLocationFromIP(session.ip_address)}
                        </div>
                        <div>
                          <span className="font-medium">Last Activity:</span> {getTimeAgo(session.last_activity)}
                        </div>
                        <div>
                          <span className="font-medium">Created:</span> {getTimeAgo(session.created_at)}
                        </div>
                        {session.expires_at && (
                          <>
                            <div>
                              <span className="font-medium">Expires:</span> {formatDate(session.expires_at)}
                            </div>
                            <div>
                              <span className="font-medium">Time Left:</span>
                              <span className={sessionStatus === 'expiring' ? 'text-yellow-600 font-semibold' : ''}>
                                {(() => {
                                  const timeLeft = new Date(session.expires_at) - new Date();
                                  const hoursLeft = Math.floor(timeLeft / (1000 * 60 * 60));
                                  const minsLeft = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
                                  if (timeLeft <= 0) return 'Expired';
                                  if (hoursLeft > 0) return `${hoursLeft}h ${minsLeft}m`;
                                  return `${minsLeft}m`;
                                })()}
                              </span>
                            </div>
                          </>
                        )}
                      </div>

                      {session.user_agent && (
                        <details className="mt-2">
                          <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-700">
                            View User Agent Details
                          </summary>
                          <div className="text-xs text-gray-500 mt-1 bg-gray-50 p-2 rounded">
                            <p className="font-mono">{session.user_agent}</p>
                          </div>
                        </details>
                      )}
                    </div>
                  </div>
                  <div className="flex flex-col space-y-2">
                    {!session.is_current && (
                      <button
                        onClick={() => confirmTerminateSession(session.token)}
                        className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
                      >
                        Terminate
                      </button>
                    )}
                    <div className="text-xs text-gray-500 text-right">
                      {session.is_current ? 'This device' : 'Remote device'}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Confirmation Modals */}
      {showTerminateConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Confirm Session Termination</h3>
            <p className="text-gray-600 mb-6">
              Are you sure you want to terminate this session? This action cannot be undone and the user will be logged out immediately.
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowTerminateConfirm(null)}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={() => executeTerminateSession(showTerminateConfirm)}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
              >
                Terminate Session
              </button>
            </div>
          </div>
        </div>
      )}

      {showTerminateAllConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Confirm Terminate All Sessions</h3>
            <p className="text-gray-600 mb-6">
              Are you sure you want to terminate ALL sessions? This will log you out immediately and end all other active sessions. You will need to log in again.
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowTerminateAllConfirm(false)}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={executeTerminateAllSessions}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
              >
                Terminate All Sessions
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Session Security Information */}
      <div className="bg-blue-50 p-4 rounded-lg">
        <h4 className="text-md font-semibold text-blue-800 mb-3">Session Security</h4>
        <ul className="space-y-2 text-sm text-blue-700">
          <li className="flex items-start">
            <span className="text-blue-500 mr-2">•</span>
            Sessions are automatically terminated after 8 hours of inactivity
          </li>
          <li className="flex items-start">
            <span className="text-blue-500 mr-2">•</span>
            Changing your password will terminate all other sessions
          </li>
          <li className="flex items-start">
            <span className="text-blue-500 mr-2">•</span>
            If you see unfamiliar sessions, terminate them immediately and change your password
          </li>
          <li className="flex items-start">
            <span className="text-blue-500 mr-2">•</span>
            Always log out when using shared or public computers
          </li>
        </ul>
      </div>
    </div>
  );
};

export default SessionsTab;