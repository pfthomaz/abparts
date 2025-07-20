// frontend/src/components/PermissionVisualization.js

import React, { useState } from 'react';
import {
  USER_ROLES,
  PERMISSIONS,
  getPermissionsForRole,
  hasPermission,
  isAdmin
} from '../utils/permissions';
import { useAuth } from '../AuthContext';
import PermissionGuard from './PermissionGuard';

/**
 * PermissionVisualization component for administrators to view and understand permissions
 */
const PermissionVisualization = ({ targetUser = null, showRoleComparison = true }) => {
  const { user: currentUser } = useAuth();
  const [selectedRole, setSelectedRole] = useState(USER_ROLES.USER);
  const [expandedCategories, setExpandedCategories] = useState({});

  // Only admins and super admins can view this component
  if (!isAdmin(currentUser)) {
    return null;
  }

  const toggleCategory = (category) => {
    setExpandedCategories(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
  };

  // Group permissions by category for better organization
  const permissionCategories = {
    'Organization Management': [
      PERMISSIONS.VIEW_ALL_ORGANIZATIONS,
      PERMISSIONS.MANAGE_ORGANIZATIONS,
      PERMISSIONS.VIEW_OWN_ORGANIZATION
    ],
    'User Management': [
      PERMISSIONS.MANAGE_ALL_USERS,
      PERMISSIONS.MANAGE_ORG_USERS,
      PERMISSIONS.INVITE_USERS,
      PERMISSIONS.VIEW_USER_AUDIT_LOGS
    ],
    'Warehouse Management': [
      PERMISSIONS.MANAGE_WAREHOUSES,
      PERMISSIONS.VIEW_WAREHOUSES
    ],
    'Inventory Management': [
      PERMISSIONS.ADJUST_INVENTORY,
      PERMISSIONS.VIEW_INVENTORY,
      PERMISSIONS.TRANSFER_INVENTORY
    ],
    'Parts Management': [
      PERMISSIONS.MANAGE_PARTS,
      PERMISSIONS.VIEW_PARTS,
      PERMISSIONS.ORDER_PARTS,
      PERMISSIONS.RECEIVE_PARTS,
      PERMISSIONS.RECORD_PART_USAGE
    ],
    'Machine Management': [
      PERMISSIONS.REGISTER_MACHINES,
      PERMISSIONS.VIEW_ALL_MACHINES,
      PERMISSIONS.VIEW_ORG_MACHINES
    ],
    'Transaction Management': [
      PERMISSIONS.VIEW_ALL_TRANSACTIONS,
      PERMISSIONS.VIEW_ORG_TRANSACTIONS
    ],
    'Supplier Management': [
      PERMISSIONS.MANAGE_SUPPLIERS,
      PERMISSIONS.VIEW_SUPPLIERS
    ],
    'Reporting & Analytics': [
      PERMISSIONS.VIEW_GLOBAL_REPORTS,
      PERMISSIONS.VIEW_ORG_REPORTS
    ],
    'System Administration': [
      PERMISSIONS.VIEW_SYSTEM_LOGS,
      PERMISSIONS.MANAGE_SYSTEM_SETTINGS
    ]
  };

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

  const getPermissionDisplayName = (permission) => {
    return permission
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
  };

  const renderPermissionStatus = (permission, role) => {
    const rolePermissions = getPermissionsForRole(role);
    const hasPermissionForRole = rolePermissions.includes(permission);

    return (
      <div className="flex items-center space-x-2">
        <div className={`w-3 h-3 rounded-full ${hasPermissionForRole ? 'bg-green-500' : 'bg-gray-300'
          }`} />
        <span className={`text-sm ${hasPermissionForRole ? 'text-green-700' : 'text-gray-500'
          }`}>
          {getPermissionDisplayName(permission)}
        </span>
      </div>
    );
  };

  const renderUserPermissions = (user) => {
    if (!user) return null;

    return (
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-3">
          Current User Permissions: {user.name || user.username}
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(permissionCategories).map(([category, permissions]) => (
            <div key={category} className="bg-white rounded-md p-3">
              <h4 className="font-medium text-gray-900 mb-2">{category}</h4>
              <div className="space-y-1">
                {permissions.map(permission => (
                  <div key={permission} className="flex items-center space-x-2">
                    <div className={`w-2 h-2 rounded-full ${hasPermission(user, permission) ? 'bg-green-500' : 'bg-gray-300'
                      }`} />
                    <span className={`text-xs ${hasPermission(user, permission) ? 'text-green-700' : 'text-gray-500'
                      }`}>
                      {getPermissionDisplayName(permission)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <PermissionGuard permission={[PERMISSIONS.MANAGE_ORG_USERS, PERMISSIONS.MANAGE_ALL_USERS]}>
      <div className="bg-white shadow rounded-lg p-6">
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Permission Management
          </h2>
          <p className="text-gray-600">
            View and understand user permissions across different roles.
          </p>
        </div>

        {/* Show current user's permissions if targetUser is provided */}
        {targetUser && renderUserPermissions(targetUser)}

        {/* Role comparison section */}
        {showRoleComparison && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Role Permission Comparison
            </h3>

            {/* Role selector */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Role to View Permissions:
              </label>
              <select
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                className="block w-full max-w-xs px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                {Object.values(USER_ROLES).map(role => (
                  <option key={role} value={role}>
                    {getRoleDisplayName(role)}
                  </option>
                ))}
              </select>
            </div>

            {/* Permission categories */}
            <div className="space-y-4">
              {Object.entries(permissionCategories).map(([category, permissions]) => {
                const isExpanded = expandedCategories[category];
                const categoryPermissions = getPermissionsForRole(selectedRole);
                const hasAnyInCategory = permissions.some(p => categoryPermissions.includes(p));

                return (
                  <div key={category} className="border border-gray-200 rounded-lg">
                    <button
                      onClick={() => toggleCategory(category)}
                      className="w-full px-4 py-3 text-left bg-gray-50 hover:bg-gray-100 rounded-t-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <span className="font-medium text-gray-900">{category}</span>
                          <div className={`w-3 h-3 rounded-full ${hasAnyInCategory ? 'bg-green-500' : 'bg-gray-300'
                            }`} />
                        </div>
                        <svg
                          className={`w-5 h-5 text-gray-500 transform transition-transform ${isExpanded ? 'rotate-180' : ''
                            }`}
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </div>
                    </button>

                    {isExpanded && (
                      <div className="px-4 py-3 bg-white rounded-b-lg">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                          {permissions.map(permission => (
                            <div key={permission}>
                              {renderPermissionStatus(permission, selectedRole)}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Permission legend */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-3">Permission Legend</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-green-500" />
              <span>Permission Granted</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-gray-300" />
              <span>Permission Denied</span>
            </div>
            <div className="text-gray-600">
              <strong>Super Admin:</strong> Has all permissions across all organizations
            </div>
          </div>

          <div className="mt-3 text-xs text-gray-600">
            <p><strong>Note:</strong> Permissions are enforced both in the frontend UI and backend API.
              Users will only see features and data they have permission to access.</p>
          </div>
        </div>
      </div>
    </PermissionGuard>
  );
};

export default PermissionVisualization;