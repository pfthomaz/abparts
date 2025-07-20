// frontend/src/components/PermissionGuard.js

import { useAuth } from '../AuthContext';
import {
  hasPermission,
  hasAnyPermission,
  hasAllPermissions,
  canPerformAction,
  getContextualPermissions,
  canViewOrganization,
  isSuperAdmin
} from '../utils/permissions';

/**
 * Enhanced PermissionGuard component for conditional rendering based on user permissions
 * 
 * @param {Object} props
 * @param {string|string[]} props.permission - Single permission or array of permissions
 * @param {string|string[]} props.permissions - Alternative prop name for array of permissions
 * @param {string} props.mode - 'any' (default) or 'all' - how to evaluate multiple permissions
 * @param {string} props.action - Specific action to check (view, create, edit, delete)
 * @param {string} props.resource - Resource type for contextual permissions
 * @param {Object} props.resourceData - Resource data for context-specific checks
 * @param {string} props.organizationId - Organization ID for organization-scoped checks
 * @param {boolean} props.requireSuperAdmin - Require super admin access
 * @param {boolean} props.requireAdmin - Require admin or super admin access
 * @param {React.ReactNode} props.children - Content to render if permission check passes
 * @param {React.ReactNode} props.fallback - Content to render if permission check fails
 * @param {boolean} props.hideIfNoPermission - If true, renders nothing instead of fallback
 * @param {boolean} props.showAccessScope - Show access scope indicator
 * @param {string} props.className - Additional CSS classes
 */
const PermissionGuard = ({
  permission,
  permissions, // Alternative prop name for array of permissions
  mode = 'any',
  action,
  resource,
  resourceData,
  organizationId,
  requireSuperAdmin = false,
  requireAdmin = false,
  children,
  fallback = null,
  hideIfNoPermission = false,
  showAccessScope = false,
  className = ''
}) => {
  const { user } = useAuth();

  // Early return if user is not available
  if (!user) {
    return hideIfNoPermission ? null : fallback;
  }

  let hasAccess = false;

  // Check super admin requirement
  if (requireSuperAdmin) {
    hasAccess = isSuperAdmin(user);
  }
  // Check admin requirement
  else if (requireAdmin) {
    hasAccess = user.role === 'admin' || user.role === 'super_admin';
  }
  // Check organization-scoped access
  else if (organizationId) {
    hasAccess = canViewOrganization(user, organizationId);
  }
  // Check action-based permissions
  else if (action && resource) {
    hasAccess = canPerformAction(user, action, resource, resourceData);
  }
  // Check contextual permissions
  else if (resource && !permission && !permissions) {
    const contextualPerms = getContextualPermissions(user, resource);
    hasAccess = contextualPerms.canView; // Default to view permission
  }
  // Check specific permissions
  else {
    // Handle both single permission and array of permissions
    const permsToCheck = permission ?
      (Array.isArray(permission) ? permission : [permission]) :
      (permissions || []);

    if (permsToCheck.length === 0) {
      // No permissions specified, allow access
      hasAccess = true;
    } else if (permsToCheck.length === 1) {
      hasAccess = hasPermission(user, permsToCheck[0]);
    } else if (mode === 'all') {
      hasAccess = hasAllPermissions(user, permsToCheck);
    } else {
      hasAccess = hasAnyPermission(user, permsToCheck);
    }
  }

  if (hasAccess) {
    // Render children with optional access scope indicator
    if (showAccessScope) {
      const accessScope = isSuperAdmin(user) ? 'Global Access' : 'Organization Access';
      return (
        <div className={`relative ${className}`}>
          {children}
          <div className="absolute top-0 right-0 -mt-1 -mr-1">
            <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${isSuperAdmin(user)
              ? 'bg-purple-100 text-purple-800'
              : 'bg-blue-100 text-blue-800'
              }`}>
              {accessScope}
            </span>
          </div>
        </div>
      );
    }
    return <div className={className}>{children}</div>;
  }

  if (hideIfNoPermission) {
    return null;
  }

  return fallback;
};

/**
 * Hook for checking permissions in functional components
 * @param {string|string[]} permissions - Permissions to check
 * @param {string} mode - 'any' or 'all'
 * @returns {boolean} - Whether user has the permissions
 */
export const usePermissions = (permissions, mode = 'any') => {
  const { user } = useAuth();

  if (!user) return false;

  const permsToCheck = Array.isArray(permissions) ? permissions : [permissions];

  if (permsToCheck.length === 1) {
    return hasPermission(user, permsToCheck[0]);
  } else if (mode === 'all') {
    return hasAllPermissions(user, permsToCheck);
  } else {
    return hasAnyPermission(user, permsToCheck);
  }
};

/**
 * Hook for getting contextual permissions for a resource
 * @param {string} resource - Resource type
 * @returns {Object} - Contextual permissions object
 */
export const useContextualPermissions = (resource) => {
  const { user } = useAuth();
  return getContextualPermissions(user, resource);
};

/**
 * Component for displaying permission-based action buttons
 */
export const PermissionButton = ({
  action,
  resource,
  resourceData,
  permission,
  onClick,
  children,
  className = '',
  variant = 'primary',
  disabled = false,
  ...props
}) => {
  const { user } = useAuth();

  const hasAccess = permission
    ? hasPermission(user, permission)
    : canPerformAction(user, action, resource, resourceData);

  if (!hasAccess) {
    return null;
  }

  const baseClasses = 'px-4 py-2 rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2';
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
    secondary: 'bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500',
    success: 'bg-green-600 text-white hover:bg-green-700 focus:ring-green-500',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
    warning: 'bg-yellow-600 text-white hover:bg-yellow-700 focus:ring-yellow-500'
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`${baseClasses} ${variantClasses[variant]} ${className} ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
      {...props}
    >
      {children}
    </button>
  );
};

export default PermissionGuard;