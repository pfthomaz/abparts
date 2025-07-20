// frontend/src/components/SecurityTab.js

import React, { useState, useEffect } from 'react';
import { userService } from '../services/userService';

const SecurityTab = ({
  setShowPasswordModal,
  setShowEmailModal,
  setShowPasswordResetModal
}) => {
  const [securityEvents, setSecurityEvents] = useState([]);
  const [loadingEvents, setLoadingEvents] = useState(false);
  const [accountStatus, setAccountStatus] = useState(null);
  const [suspiciousActivity, setSuspiciousActivity] = useState([]);
  const [securitySettings, setSecuritySettings] = useState({
    emailNotifications: true,
    loginAlerts: true,
    suspiciousActivityAlerts: true,
    sessionTimeoutWarning: true,
    twoFactorEnabled: false,
    loginNotifications: true
  });
  const [showUnlockConfirm, setShowUnlockConfirm] = useState(false);
  const [unlockRequestSent, setUnlockRequestSent] = useState(false);

  useEffect(() => {
    fetchSecurityEvents();
    fetchAccountStatus();
    checkSuspiciousActivity();
  }, []);

  const fetchSecurityEvents = async () => {
    try {
      setLoadingEvents(true);
      const events = await userService.getSecurityEvents({ limit: 10 });
      setSecurityEvents(events);
    } catch (err) {
      console.error('Failed to fetch security events:', err);
    } finally {
      setLoadingEvents(false);
    }
  };

  const fetchAccountStatus = async () => {
    try {
      const profile = await userService.getMyProfile();
      setAccountStatus({
        status: profile.user_status || 'active',
        failedAttempts: profile.failed_login_attempts || 0,
        lockedUntil: profile.locked_until,
        lastLogin: profile.last_login
      });
    } catch (err) {
      console.error('Failed to fetch account status:', err);
    }
  };

  const checkSuspiciousActivity = async () => {
    try {
      // Mock suspicious activity detection - in real implementation this would come from backend
      const mockSuspiciousActivity = [
        {
          id: 1,
          type: 'unusual_location',
          description: 'Login from new location: New York, NY',
          timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
          severity: 'medium',
          resolved: false
        },
        {
          id: 2,
          type: 'multiple_failed_attempts',
          description: '3 failed login attempts in 5 minutes',
          timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
          severity: 'high',
          resolved: true
        }
      ];
      setSuspiciousActivity(mockSuspiciousActivity);
    } catch (err) {
      console.error('Failed to check suspicious activity:', err);
    }
  };

  const handleUnlockAccount = async () => {
    try {
      setShowUnlockConfirm(true);
    } catch (err) {
      console.error('Failed to show unlock confirmation:', err);
    }
  };

  const confirmUnlockAccount = async () => {
    try {
      // In real implementation, this would call a backend endpoint
      // await userService.unlockMyAccount();
      setUnlockRequestSent(true);
      setShowUnlockConfirm(false);
      await fetchAccountStatus();
    } catch (err) {
      console.error('Failed to unlock account:', err);
    }
  };

  const handleDismissSuspiciousActivity = (activityId) => {
    setSuspiciousActivity(prev =>
      prev.map(activity =>
        activity.id === activityId
          ? { ...activity, resolved: true }
          : activity
      )
    );
  };

  const handleSecuritySettingsChange = (setting, value) => {
    setSecuritySettings(prev => ({
      ...prev,
      [setting]: value
    }));
    // In real implementation, this would save to backend
    // userService.updateSecuritySettings({ [setting]: value });
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleString();
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

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return 'text-red-600 bg-red-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-blue-600 bg-blue-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold text-gray-800">Security Settings</h3>

      {/* Account Status */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h4 className="text-md font-semibold text-gray-800 mb-3">Account Status</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600">Account Status</p>
            <div className="flex items-center space-x-2">
              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${accountStatus?.status === 'active'
                ? 'bg-green-100 text-green-800'
                : accountStatus?.status === 'locked'
                  ? 'bg-red-100 text-red-800'
                  : 'bg-yellow-100 text-yellow-800'
                }`}>
                {accountStatus?.status || 'Unknown'}
              </span>
              {accountStatus?.status === 'locked' && (
                <button
                  onClick={handleUnlockAccount}
                  className="text-xs px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Request Unlock
                </button>
              )}
            </div>
          </div>
          <div>
            <p className="text-sm text-gray-600">Last Login</p>
            <p className="text-sm font-medium text-gray-800">
              {formatDate(accountStatus?.lastLogin)}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Failed Login Attempts</p>
            <p className="text-sm font-medium text-gray-800">
              {accountStatus?.failedAttempts || 0} / 5
            </p>
          </div>
          {accountStatus?.lockedUntil && (
            <div>
              <p className="text-sm text-gray-600">Locked Until</p>
              <p className="text-sm font-medium text-red-600">
                {formatDate(accountStatus.lockedUntil)}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Suspicious Activity Alerts */}
      {suspiciousActivity.filter(activity => !activity.resolved).length > 0 && (
        <div className="bg-red-50 border border-red-200 p-4 rounded-lg">
          <h4 className="text-md font-semibold text-red-800 mb-3">
            🚨 Suspicious Activity Detected
          </h4>
          <div className="space-y-3">
            {suspiciousActivity
              .filter(activity => !activity.resolved)
              .map((activity) => (
                <div key={activity.id} className="flex justify-between items-start bg-white p-3 rounded border">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getSeverityColor(activity.severity)}`}>
                        {activity.severity.toUpperCase()}
                      </span>
                      <span className="text-sm text-gray-500">
                        {formatDate(activity.timestamp)}
                      </span>
                    </div>
                    <p className="text-sm text-gray-800 mt-1">{activity.description}</p>
                  </div>
                  <button
                    onClick={() => handleDismissSuspiciousActivity(activity.id)}
                    className="text-xs px-2 py-1 bg-gray-600 text-white rounded hover:bg-gray-700"
                  >
                    Dismiss
                  </button>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Password Management */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h4 className="text-md font-semibold text-gray-800 mb-3">Password Management</h4>
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-gray-800 font-medium">Change Password</p>
              <p className="text-sm text-gray-600">
                Update your password to keep your account secure
              </p>
            </div>
            <button
              onClick={() => setShowPasswordModal(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Change Password
            </button>
          </div>

          <div className="border-t pt-3">
            <div className="flex justify-between items-center">
              <div>
                <p className="text-gray-800 font-medium">Password Reset</p>
                <p className="text-sm text-gray-600">
                  Request a password reset link via email
                </p>
              </div>
              <button
                onClick={() => setShowPasswordResetModal(true)}
                className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500"
              >
                Request Reset
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Email Management */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h4 className="text-md font-semibold text-gray-800 mb-3">Email Management</h4>
        <div className="flex justify-between items-center">
          <div>
            <p className="text-gray-800 font-medium">Change Email Address</p>
            <p className="text-sm text-gray-600">
              Update your email address with verification
            </p>
          </div>
          <button
            onClick={() => setShowEmailModal(true)}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            Change Email
          </button>
        </div>
      </div>

      {/* Security Settings and Preferences */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h4 className="text-md font-semibold text-gray-800 mb-3">Security Preferences</h4>
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-gray-800 font-medium">Email Notifications</p>
              <p className="text-sm text-gray-600">Receive security alerts via email</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={securitySettings.emailNotifications}
                onChange={(e) => handleSecuritySettingsChange('emailNotifications', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div className="flex justify-between items-center">
            <div>
              <p className="text-gray-800 font-medium">Login Alerts</p>
              <p className="text-sm text-gray-600">Get notified of new login sessions</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={securitySettings.loginAlerts}
                onChange={(e) => handleSecuritySettingsChange('loginAlerts', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div className="flex justify-between items-center">
            <div>
              <p className="text-gray-800 font-medium">Suspicious Activity Alerts</p>
              <p className="text-sm text-gray-600">Alert me of unusual account activity</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={securitySettings.suspiciousActivityAlerts}
                onChange={(e) => handleSecuritySettingsChange('suspiciousActivityAlerts', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div className="flex justify-between items-center">
            <div>
              <p className="text-gray-800 font-medium">Session Timeout Warning</p>
              <p className="text-sm text-gray-600">Warn me before session expires</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={securitySettings.sessionTimeoutWarning}
                onChange={(e) => handleSecuritySettingsChange('sessionTimeoutWarning', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
        </div>
      </div>

      {/* Login History and Security Events */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <div className="flex justify-between items-center mb-3">
          <h4 className="text-md font-semibold text-gray-800">Recent Security Events</h4>
          <button
            onClick={fetchSecurityEvents}
            disabled={loadingEvents}
            className="px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-700 disabled:opacity-50"
          >
            {loadingEvents ? 'Loading...' : 'Refresh'}
          </button>
        </div>

        {loadingEvents ? (
          <div className="flex items-center justify-center py-4">
            <p className="text-gray-600">Loading security events...</p>
          </div>
        ) : securityEvents.length === 0 ? (
          <div className="text-center py-4">
            <p className="text-gray-600">No recent security events</p>
          </div>
        ) : (
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {securityEvents.map((event, index) => (
              <div key={event.id || index} className="flex items-center space-x-3 bg-white p-3 rounded border">
                <div className="text-lg">{getEventIcon(event.event_type)}</div>
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <p className="text-sm font-medium text-gray-800">
                      {event.event_type?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Unknown Event'}
                    </p>
                    <span className="text-xs text-gray-500">
                      {formatDate(event.timestamp)}
                    </span>
                  </div>
                  <div className="text-xs text-gray-600 space-x-4">
                    <span>IP: {event.ip_address || 'Unknown'}</span>
                    <span>Status: {event.success ? '✅ Success' : '❌ Failed'}</span>
                  </div>
                  {event.details && (
                    <p className="text-xs text-gray-500 mt-1">{event.details}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Unlock Request Success Notification */}
      {unlockRequestSent && (
        <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <span className="text-green-600 text-xl">✅</span>
            </div>
            <div className="ml-3">
              <h4 className="text-sm font-medium text-green-800">Unlock Request Sent</h4>
              <p className="text-sm text-green-700 mt-1">
                Your account unlock request has been sent to the administrators. You will receive an email notification once your account is unlocked.
              </p>
              <button
                onClick={() => setUnlockRequestSent(false)}
                className="text-xs text-green-600 hover:text-green-800 mt-2"
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Security Tips */}
      <div className="bg-blue-50 p-4 rounded-lg">
        <h4 className="text-md font-semibold text-blue-800 mb-3">Security Tips</h4>
        <ul className="space-y-2 text-sm text-blue-700">
          <li className="flex items-start">
            <span className="text-blue-500 mr-2">•</span>
            Use a strong password with at least 8 characters, including uppercase, lowercase, numbers, and symbols
          </li>
          <li className="flex items-start">
            <span className="text-blue-500 mr-2">•</span>
            Don't share your password with anyone or use the same password for multiple accounts
          </li>
          <li className="flex items-start">
            <span className="text-blue-500 mr-2">•</span>
            Change your password regularly and immediately if you suspect it has been compromised
          </li>
          <li className="flex items-start">
            <span className="text-blue-500 mr-2">•</span>
            Always log out when using shared or public computers
          </li>
          <li className="flex items-start">
            <span className="text-blue-500 mr-2">•</span>
            Keep your email address up to date for important security notifications
          </li>
          <li className="flex items-start">
            <span className="text-blue-500 mr-2">•</span>
            Review your active sessions regularly and terminate any unfamiliar ones
          </li>
          <li className="flex items-start">
            <span className="text-blue-500 mr-2">•</span>
            Enable security notifications to stay informed about account activity
          </li>
        </ul>
      </div>

      {/* Unlock Account Confirmation Modal */}
      {showUnlockConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Request Account Unlock</h3>
            <p className="text-gray-600 mb-6">
              Your account is currently locked due to multiple failed login attempts.
              Would you like to send an unlock request to the administrators?
            </p>
            <div className="bg-yellow-50 p-3 rounded-lg mb-4">
              <p className="text-sm text-yellow-800">
                <strong>Note:</strong> The unlock request will be reviewed by administrators.
                You will receive an email notification once your account is unlocked.
              </p>
            </div>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowUnlockConfirm(false)}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={confirmUnlockAccount}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Send Unlock Request
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SecurityTab;