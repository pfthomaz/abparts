// frontend/src/components/NotificationsTab.js

import React from 'react';

const NotificationsTab = ({
  notificationPreferences,
  setNotificationPreferences,
  handleNotificationPreferencesUpdate
}) => {
  const handlePreferenceChange = (key, value) => {
    setNotificationPreferences(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const notificationSettings = [
    {
      key: 'email_notifications',
      title: 'Email Notifications',
      description: 'Receive general notifications via email',
      icon: '📧'
    },
    {
      key: 'order_updates',
      title: 'Order Updates',
      description: 'Get notified about order status changes and updates',
      icon: '📦'
    },
    {
      key: 'inventory_alerts',
      title: 'Inventory Alerts',
      description: 'Receive alerts for low stock and inventory changes',
      icon: '📊'
    },
    {
      key: 'system_notifications',
      title: 'System Notifications',
      description: 'Important system updates and maintenance notifications',
      icon: '⚙️'
    },
    {
      key: 'security_alerts',
      title: 'Security Alerts',
      description: 'Login attempts, password changes, and security events',
      icon: '🔒'
    },
    {
      key: 'weekly_reports',
      title: 'Weekly Reports',
      description: 'Weekly summary reports of your organization\'s activity',
      icon: '📈'
    }
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-800">Notification Preferences</h3>
        <button
          onClick={handleNotificationPreferencesUpdate}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Save Preferences
        </button>
      </div>

      <div className="bg-blue-50 p-4 rounded-lg">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <span className="text-blue-600 text-xl">ℹ️</span>
          </div>
          <div className="ml-3">
            <h4 className="text-sm font-medium text-blue-800">About Notifications</h4>
            <p className="text-sm text-blue-700 mt-1">
              Customize which notifications you receive to stay informed about important updates while reducing noise.
              Some critical security notifications cannot be disabled.
            </p>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        {notificationSettings.map((setting) => (
          <div key={setting.key} className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-start space-x-3">
                <div className="text-2xl">
                  {setting.icon}
                </div>
                <div className="flex-1">
                  <h4 className="text-md font-semibold text-gray-800">
                    {setting.title}
                  </h4>
                  <p className="text-sm text-gray-600 mt-1">
                    {setting.description}
                  </p>
                </div>
              </div>
              <div className="flex items-center">
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={notificationPreferences[setting.key] || false}
                    onChange={(e) => handlePreferenceChange(setting.key, e.target.checked)}
                    className="sr-only peer"
                    disabled={setting.key === 'security_alerts'} // Security alerts cannot be disabled
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
                {setting.key === 'security_alerts' && (
                  <span className="ml-2 text-xs text-gray-500">Required</span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Notification Delivery Settings */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h4 className="text-md font-semibold text-gray-800 mb-3">Delivery Settings</h4>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-800 font-medium">Email Digest</p>
              <p className="text-sm text-gray-600">
                Receive a daily digest instead of individual emails
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={notificationPreferences.email_digest || false}
                onChange={(e) => handlePreferenceChange('email_digest', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-800 font-medium">Quiet Hours</p>
              <p className="text-sm text-gray-600">
                Reduce non-urgent notifications during specified hours
              </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={notificationPreferences.quiet_hours || false}
                onChange={(e) => handlePreferenceChange('quiet_hours', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
        </div>
      </div>

      {/* Notification History */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h4 className="text-md font-semibold text-gray-800 mb-3">Recent Notifications</h4>
        <div className="space-y-2 max-h-48 overflow-y-auto">
          {/* Placeholder for recent notifications - would be populated from API */}
          <div className="text-sm text-gray-600 text-center py-4">
            Notification history will appear here
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotificationsTab;