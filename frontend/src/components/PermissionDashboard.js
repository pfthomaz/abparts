// frontend/src/components/PermissionDashboard.js

import React, { useState } from 'react';
import { useAuth } from '../AuthContext';
import {
  PERMISSIONS,
  isSuperAdmin,
  isAdmin,
  getFeatureFlags
} from '../utils/permissions';
import PermissionGuard from './PermissionGuard';
import PermissionVisualization from './PermissionVisualization';
import PermissionManagementPanel from './PermissionManagementPanel';

/**
 * PermissionDashboard component for administrators to manage and view permissions
 */
const PermissionDashboard = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');

  // Only admins and super admins can access this dashboard
  if (!isAdmin(user)) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-yellow-800">
              Access Restricted
            </h3>
            <div className="mt-2 text-sm text-yellow-700">
              <p>You need administrator privileges to access the permission dashboard.</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const featureFlags = getFeatureFlags(user);

  const tabs = [
    { id: 'overview', label: 'Overview', icon: 'dashboard' },
    { id: 'roles', label: 'Role Permissions', icon: 'users' },
    { id: 'features', label: 'Feature Access', icon: 'settings' }
  ];

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Current User Summary */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-4">Your Access Level</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-md p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-900">Role</p>
                <p className="text-sm text-gray-500">
                  {user.role === 'super_admin' ? 'Super Administrator' :
                    user.role === 'admin' ? 'Administrator' : 'User'}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-md p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-500 text-white rounded-full flex items-center justify-center">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-4m-5 0H9m0 0H5m0 0h2M7 7h10M7 11h4m6 0h2M7 15h10" />
                  </svg>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-900">Organization</p>
                <p className="text-sm text-gray-500">{user.organization?.name || 'Unknown'}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-md p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-purple-500 text-white rounded-full flex items-center justify-center">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-900">Access Scope</p>
                <p className="text-sm text-gray-500">
                  {isSuperAdmin(user) ? 'All Organizations' : 'Own Organization'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <PermissionGuard permission={PERMISSIONS.MANAGE_ORG_USERS}>
            <button className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              <div className="flex-shrink-0">
                <svg className="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900">Manage Users</p>
                <p className="text-sm text-gray-500">Add, edit, or deactivate users</p>
              </div>
            </button>
          </PermissionGuard>

          <PermissionGuard permission={PERMISSIONS.INVITE_USERS}>
            <button className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              <div className="flex-shrink-0">
                <svg className="w-6 h-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900">Invite Users</p>
                <p className="text-sm text-gray-500">Send invitations to new users</p>
              </div>
            </button>
          </PermissionGuard>

          <PermissionGuard permission={PERMISSIONS.VIEW_USER_AUDIT_LOGS}>
            <button className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              <div className="flex-shrink-0">
                <svg className="w-6 h-6 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900">View Audit Logs</p>
                <p className="text-sm text-gray-500">Review user activity logs</p>
              </div>
            </button>
          </PermissionGuard>
        </div>
      </div>
    </div>
  );

  const renderFeatureAccess = () => (
    <div className="bg-white shadow rounded-lg p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Feature Access</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {Object.entries(featureFlags).map(([feature, hasAccess]) => (
          <div key={feature} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
            <div>
              <p className="text-sm font-medium text-gray-900">
                {feature.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
              </p>
            </div>
            <div className={`px-2 py-1 rounded-full text-xs font-medium ${hasAccess
              ? 'bg-green-100 text-green-800'
              : 'bg-red-100 text-red-800'
              }`}>
              {hasAccess ? 'Granted' : 'Denied'}
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  return <PermissionManagementPanel />;
};

export default PermissionDashboard;