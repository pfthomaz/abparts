// frontend/src/components/PermissionDenied.js

import React from 'react';
import { useAuth } from '../AuthContext';
import { getAccessScope, getContextualPermissions, isSuperAdmin } from '../utils/permissions';

/**
 * Enhanced PermissionDenied component to display when user lacks required permissions
 * 
 * @param {Object} props
 * @param {string} props.message - Custom message to display
 * @param {string} props.requiredRole - Role required for access
 * @param {string} props.feature - Feature name that requires permission
 * @param {string} props.resource - Resource type for contextual information
 * @param {string} props.action - Action that was attempted
 * @param {string[]} props.requiredPermissions - List of required permissions
 * @param {boolean} props.showContactInfo - Whether to show contact information
 * @param {boolean} props.showPermissionDetails - Whether to show detailed permission info
 * @param {boolean} props.isInline - Whether to render as inline component instead of full page
 */
const PermissionDenied = ({
  message,
  requiredRole,
  feature,
  resource,
  action,
  requiredPermissions = [],
  showContactInfo = true,
  showPermissionDetails = true,
  isInline = false
}) => {
  const { user } = useAuth();

  const accessScope = getAccessScope(user);
  const contextualPermissions = resource ? getContextualPermissions(user, resource) : null;

  const defaultMessage = message ||
    `You don't have permission to ${action || 'access'} ${feature || resource || 'this feature'}.`;

  const getRoleDisplayName = (role) => {
    switch (role) {
      case 'super_admin':
        return 'Super Administrator';
      case 'admin':
        return 'Administrator';
      case 'user':
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

  const getSuggestions = () => {
    const suggestions = [];

    if (requiredRole === 'admin' && user?.role === 'user') {
      suggestions.push('Request administrator privileges from your organization admin');
    }

    if (requiredRole === 'super_admin' && user?.role !== 'super_admin') {
      suggestions.push('This feature requires super administrator access');
    }

    if (resource === 'organizations' && !isSuperAdmin(user)) {
      suggestions.push('Organization management is restricted to super administrators');
    }

    if (accessScope.accessLevel === 'organization' && action === 'view' && resource) {
      suggestions.push('You can only access data from your own organization');
    }

    return suggestions;
  };

  const suggestions = getSuggestions();

  const content = (
    <>
      {/* Icon and Title */}
      <div className="text-center mb-6">
        <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
          <svg
            className="h-6 w-6 text-red-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
            />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Access Denied
        </h2>
        <p className="text-gray-600">
          {defaultMessage}
        </p>
      </div>

      {/* User Information */}
      <div className="bg-gray-50 rounded-lg p-4 mb-6">
        <h3 className="text-sm font-medium text-gray-900 mb-3">Your Access Level</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-500">Role:</span>
            <span className="font-medium text-gray-900">
              {getRoleDisplayName(user?.role)}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Organization:</span>
            <span className="font-medium text-gray-900">
              {user?.organization?.name || 'Unknown'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Access Scope:</span>
            <span className="font-medium text-gray-900">
              {accessScope.accessLevel === 'global' ? 'All Organizations' : 'Own Organization'}
            </span>
          </div>
          {requiredRole && (
            <div className="flex justify-between">
              <span className="text-gray-500">Required Role:</span>
              <span className="font-medium text-red-600">
                {getRoleDisplayName(requiredRole)}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Permission Details */}
      {showPermissionDetails && (contextualPermissions || requiredPermissions.length > 0) && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
          <h3 className="text-sm font-medium text-yellow-800 mb-3">Permission Details</h3>

          {contextualPermissions && (
            <div className="mb-3">
              <p className="text-sm text-yellow-700 mb-2">
                Your permissions for {resource}:
              </p>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className={`flex items-center ${contextualPermissions.canView ? 'text-green-700' : 'text-red-700'}`}>
                  <span className={`w-2 h-2 rounded-full mr-2 ${contextualPermissions.canView ? 'bg-green-500' : 'bg-red-500'}`}></span>
                  View
                </div>
                <div className={`flex items-center ${contextualPermissions.canCreate ? 'text-green-700' : 'text-red-700'}`}>
                  <span className={`w-2 h-2 rounded-full mr-2 ${contextualPermissions.canCreate ? 'bg-green-500' : 'bg-red-500'}`}></span>
                  Create
                </div>
                <div className={`flex items-center ${contextualPermissions.canEdit ? 'text-green-700' : 'text-red-700'}`}>
                  <span className={`w-2 h-2 rounded-full mr-2 ${contextualPermissions.canEdit ? 'bg-green-500' : 'bg-red-500'}`}></span>
                  Edit
                </div>
                <div className={`flex items-center ${contextualPermissions.canDelete ? 'text-green-700' : 'text-red-700'}`}>
                  <span className={`w-2 h-2 rounded-full mr-2 ${contextualPermissions.canDelete ? 'bg-green-500' : 'bg-red-500'}`}></span>
                  Delete
                </div>
              </div>
            </div>
          )}

          {requiredPermissions.length > 0 && (
            <div>
              <p className="text-sm text-yellow-700 mb-2">Required permissions:</p>
              <ul className="text-xs text-yellow-600 space-y-1">
                {requiredPermissions.map((perm, index) => (
                  <li key={index} className="flex items-center">
                    <span className="w-1 h-1 bg-yellow-400 rounded-full mr-2"></span>
                    {getPermissionDisplayName(perm)}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Suggestions */}
      {suggestions.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <h3 className="text-sm font-medium text-blue-800 mb-3">Suggestions</h3>
          <ul className="text-sm text-blue-700 space-y-2">
            {suggestions.map((suggestion, index) => (
              <li key={index} className="flex items-start">
                <span className="w-1 h-1 bg-blue-400 rounded-full mr-2 mt-2 flex-shrink-0"></span>
                {suggestion}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Contact Information */}
      {showContactInfo && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-green-400"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-green-800">
                Need Access?
              </h3>
              <div className="mt-2 text-sm text-green-700">
                <p>
                  Contact your {isSuperAdmin(user) ? 'system administrator' : 'organization administrator'}
                  {' '}to request the necessary permissions for this feature.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Actions */}
      {!isInline && (
        <div className="flex flex-col space-y-3">
          <button
            onClick={() => window.history.back()}
            className="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Go Back
          </button>
          <button
            onClick={() => window.location.href = '/'}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Return to Dashboard
          </button>
        </div>
      )}
    </>
  );

  if (isInline) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        {content}
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-2xl">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          {content}
        </div>
      </div>
    </div>
  );
};

export default PermissionDenied;