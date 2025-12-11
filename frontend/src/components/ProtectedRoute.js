// frontend/src/components/ProtectedRoute.js

import React from 'react';
import { useAuth } from '../AuthContext';
import { hasPermission, hasAnyPermission, hasAllPermissions } from '../utils/permissions';
import PermissionDenied from './PermissionDenied';

/**
 * ProtectedRoute component for protecting entire routes based on permissions
 * 
 * @param {Object} props
 * @param {React.ReactNode} props.children - Component to render if permission check passes
 * @param {string|string[]} props.permission - Single permission or array of permissions required
 * @param {string} props.mode - 'any' (default) or 'all' - how to evaluate multiple permissions
 * @param {string} props.requiredRole - Required role for display in permission denied message
 * @param {string} props.feature - Feature name for display in permission denied message
 * @param {React.ReactNode} props.fallback - Custom fallback component (defaults to PermissionDenied)
 */
const ProtectedRoute = ({
  children,
  permission,
  permissions, // Alternative prop name for array of permissions
  mode = 'any',
  requiredRole,
  feature,
  fallback
}) => {
  const { user } = useAuth();

  // Handle both single permission and array of permissions
  const permsToCheck = permission ?
    (Array.isArray(permission) ? permission : [permission]) :
    (permissions || []);

  if (permsToCheck.length === 0) {
    // No permissions specified, allow access
    return children;
  }

  let hasAccess = false;

  if (permsToCheck.length === 1) {
    hasAccess = hasPermission(user, permsToCheck[0]);
  } else if (mode === 'all') {
    hasAccess = hasAllPermissions(user, permsToCheck);
  } else {
    hasAccess = hasAnyPermission(user, permsToCheck);
  }

  if (hasAccess) {
    return children;
  }

  // Show custom fallback or default PermissionDenied component
  if (fallback) {
    return fallback;
  }

  return (
    <PermissionDenied
      requiredRole={requiredRole}
      feature={feature}
    />
  );
};

export default ProtectedRoute;