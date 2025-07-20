// frontend/src/components/PermissionManagementPanel.js

import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import {
  PERMISSIONS,
  USER_ROLES,
  hasPermission,
  isAdmin,
  getAccessScope
} from '../utils/permissions';
import PermissionGuard from './PermissionGuard';
import PermissionVisualization from './PermissionVisualization';
import { userService } from '../services/userService';

/**
 * Comprehensive permission management panel for administrators
 */
const PermissionManagementPanel = () => {
  const { user: currentUser } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedUser, setSelectedUser] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isAdmin(currentUser)) {
      fetchUsers();
    }
  }, [currentUser]);

  // Only admins can access this panel
  if (!isAdmin(currentUser)) {
    return null;
  }

  const fetchUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const userData = await userService.getUsers();
      setUsers(userData);
    } catch (err) {
      setError('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const accessScope = getAccessScope(currentUser);

  const tabs = [
    { id: 'overview', label: 'Permission Overview', icon: 'overview' },
    { id: 'roles', label: 'Role Management', icon: 'roles' },
    { id: 'users', label: 'User Permissions', icon: 'users' },
    { id: 'audit', label: 'Access Audit', icon: 'audit', permission: PERMISSIONS.VIEW_USER_AUDIT_LOGS }
  ];

  const getRoleDisplayName = (role) => {
    switch (role) {
      case USER_ROLES.SUPER_ADMIN:
        return 'Super Administrator';
      case USER_ROLES.ADMIN:
        return 'Administrator';
      case USER_ROLES.USER:
        return 'User';
      default:
        return role;
    }
  };



  const renderOverview = () => (
    <div className="space-y-6">
      {/* Current User Access Summary */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-4">Your Permission Summary</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white rounded-md p-4">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center mr-3">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">Role</p>
                <p className="text-sm text-gray-500">{getRoleDisplayName(currentUser.role)}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-md p-4">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-green-500 text-white rounded-full flex items-center justify-center mr-3">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">Access Scope</p>
                <p className="text-sm text-gray-500">{accessScope.accessLevel}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-md p-4">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-purple-500 text-white rounded-full flex items-center justify-center mr-3">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-4m-5 0H9m0 0H5m0 0h2M7 7h10M7 11h4m6 0h2M7 15h10" />
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">Organization</p>
                <p className="text-sm text-gray-500">{currentUser.organization?.name || 'Unknown'}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-md p-4">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-orange-500 text-white rounded-full flex items-center justify-center mr-3">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-900">Can Manage</p>
                <p className="text-sm text-gray-500">
                  {accessScope.canManageAllUsers ? 'All Users' : 'Org Users'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Permission Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">Role Distribution</h4>
          <div className="space-y-3">
            {Object.values(USER_ROLES).map(role => {
              const roleUsers = users.filter(u => u.role === role);
              const percentage = users.length > 0 ? (roleUsers.length / users.length * 100).toFixed(1) : 0;
              return (
                <div key={role} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">{getRoleDisplayName(role)}</span>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium text-gray-900">{roleUsers.length}</span>
                    <span className="text-xs text-gray-500">({percentage}%)</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">Access Levels</h4>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Global Access</span>
              <span className="text-sm font-medium text-gray-900">
                {users.filter(u => u.role === USER_ROLES.SUPER_ADMIN).length}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Organization Access</span>
              <span className="text-sm font-medium text-gray-900">
                {users.filter(u => u.role !== USER_ROLES.SUPER_ADMIN).length}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Active Users</span>
              <span className="text-sm font-medium text-gray-900">
                {users.filter(u => u.is_active).length}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">Your Capabilities</h4>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Can Invite Users</span>
              <span className={`text-sm font-medium ${hasPermission(currentUser, PERMISSIONS.INVITE_USERS) ? 'text-green-600' : 'text-red-600'}`}>
                {hasPermission(currentUser, PERMISSIONS.INVITE_USERS) ? 'Yes' : 'No'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Can Manage Warehouses</span>
              <span className={`text-sm font-medium ${hasPermission(currentUser, PERMISSIONS.MANAGE_WAREHOUSES) ? 'text-green-600' : 'text-red-600'}`}>
                {hasPermission(currentUser, PERMISSIONS.MANAGE_WAREHOUSES) ? 'Yes' : 'No'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Can Adjust Inventory</span>
              <span className={`text-sm font-medium ${hasPermission(currentUser, PERMISSIONS.ADJUST_INVENTORY) ? 'text-green-600' : 'text-red-600'}`}>
                {hasPermission(currentUser, PERMISSIONS.ADJUST_INVENTORY) ? 'Yes' : 'No'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderUserPermissions = () => (
    <div className="space-y-6">
      {/* User Selection */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Select User to View Permissions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {users.map(user => (
            <button
              key={user.id}
              onClick={() => setSelectedUser(user)}
              className={`p-4 border rounded-lg text-left transition-colors ${selectedUser?.id === user.id
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
            >
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                  <span className="text-sm font-medium text-gray-700">
                    {(user.name || user.username).charAt(0).toUpperCase()}
                  </span>
                </div>
                <div>
                  <p className="font-medium text-gray-900">{user.name || user.username}</p>
                  <p className="text-sm text-gray-500">{getRoleDisplayName(user.role)}</p>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Selected User Permissions */}
      {selectedUser && (
        <PermissionVisualization
          targetUser={selectedUser}
          showRoleComparison={false}
        />
      )}
    </div>
  );

  const renderAuditLog = () => (
    <PermissionGuard permission={PERMISSIONS.VIEW_USER_AUDIT_LOGS}>
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Access Audit Log</h3>
        <div className="text-center py-8">
          <svg className="w-12 h-12 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="text-gray-500">Audit log functionality will be implemented here</p>
          <p className="text-sm text-gray-400 mt-2">Track permission changes, access attempts, and security events</p>
        </div>
      </div>
    </PermissionGuard>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading permission data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error Loading Permissions</h3>
            <div className="mt-2 text-sm text-red-700">
              <p>{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Permission Management</h2>
        <p className="text-gray-600">
          Manage user permissions, roles, and access controls across the system.
        </p>
      </div>

      {/* Tabs */}
      <div className="bg-white border border-gray-200 rounded-lg">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6">
            {tabs.map((tab) => (
              <PermissionGuard
                key={tab.id}
                permission={tab.permission}
                hideIfNoPermission={tab.permission ? true : false}
              >
                <button
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                >
                  {tab.label}
                </button>
              </PermissionGuard>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'overview' && renderOverview()}
          {activeTab === 'roles' && <PermissionVisualization showRoleComparison={true} />}
          {activeTab === 'users' && renderUserPermissions()}
          {activeTab === 'audit' && renderAuditLog()}
        </div>
      </div>
    </div>
  );
};

export default PermissionManagementPanel;