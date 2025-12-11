// frontend/src/hooks/useOrganizationScope.js

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../AuthContext';
import { getAccessScope, isSuperAdmin } from '../utils/permissions';
import { organizationsService } from '../services/organizationsService';

/**
 * Custom hook for managing organization-scoped data access
 * Provides utilities for filtering data based on user's organization access level
 */
export const useOrganizationScope = () => {
  const { user } = useAuth();
  const [selectedOrganizationId, setSelectedOrganizationId] = useState(null);
  const [availableOrganizations, setAvailableOrganizations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const accessScope = getAccessScope(user);

  // Fetch available organizations for super admins
  useEffect(() => {
    if (isSuperAdmin(user)) {
      fetchOrganizations();
    }
  }, [user]);

  const fetchOrganizations = async () => {
    setLoading(true);
    setError(null);
    try {
      const organizations = await organizationsService.getOrganizations();
      setAvailableOrganizations(organizations);
    } catch (err) {
      setError('Failed to load organizations');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Get the current effective organization ID for data filtering
   */
  const getEffectiveOrganizationId = useCallback(() => {
    if (isSuperAdmin(user)) {
      return selectedOrganizationId; // null means all organizations
    }
    return user?.organization_id; // Regular users are limited to their organization
  }, [user, selectedOrganizationId]);

  /**
   * Get query parameters for API calls that need organization filtering
   */
  const getOrganizationQueryParams = useCallback(() => {
    const effectiveOrgId = getEffectiveOrganizationId();
    return effectiveOrgId ? { organization_id: effectiveOrgId } : {};
  }, [getEffectiveOrganizationId]);

  /**
   * Filter data array based on organization access
   */
  const filterByOrganizationAccess = useCallback((data, orgIdField = 'organization_id') => {
    if (!data || !Array.isArray(data)) return data;

    const effectiveOrgId = getEffectiveOrganizationId();

    // Super admin with no specific organization selected sees all data
    if (isSuperAdmin(user) && !effectiveOrgId) {
      return data;
    }

    // Filter data to match the effective organization
    return data.filter(item => {
      const itemOrgId = item[orgIdField];
      return itemOrgId === effectiveOrgId;
    });
  }, [user, getEffectiveOrganizationId]);

  /**
   * Check if user can access data from a specific organization
   */
  const canAccessOrganization = useCallback((organizationId) => {
    if (isSuperAdmin(user)) {
      return true; // Super admins can access all organizations
    }
    return user?.organization_id === organizationId;
  }, [user]);

  /**
   * Get display information for the current scope
   */
  const getScopeDisplayInfo = useCallback(() => {
    const effectiveOrgId = getEffectiveOrganizationId();

    if (isSuperAdmin(user)) {
      if (effectiveOrgId) {
        const org = availableOrganizations.find(o => o.id === effectiveOrgId);
        return {
          scope: 'organization',
          label: `Viewing: ${org?.name || 'Selected Organization'}`,
          canSwitch: true
        };
      }
      return {
        scope: 'global',
        label: 'Viewing: All Organizations',
        canSwitch: true
      };
    }

    return {
      scope: 'organization',
      label: `Limited to: ${user?.organization?.name || 'Your Organization'}`,
      canSwitch: false
    };
  }, [user, availableOrganizations, getEffectiveOrganizationId]);

  /**
   * Handle organization selection change (super admin only)
   */
  const handleOrganizationChange = useCallback((organizationId) => {
    if (isSuperAdmin(user)) {
      setSelectedOrganizationId(organizationId);
    }
  }, [user]);

  /**
   * Reset to default scope
   */
  const resetScope = useCallback(() => {
    setSelectedOrganizationId(null);
  }, []);

  /**
   * Get organization-aware API service wrapper
   */
  const createScopedApiCall = useCallback((apiFunction) => {
    return async (...args) => {
      const queryParams = getOrganizationQueryParams();

      // If the API function expects query parameters, merge them
      if (args.length > 0 && typeof args[args.length - 1] === 'object') {
        args[args.length - 1] = { ...args[args.length - 1], ...queryParams };
      } else {
        args.push(queryParams);
      }

      return apiFunction(...args);
    };
  }, [getOrganizationQueryParams]);

  return {
    // State
    selectedOrganizationId,
    availableOrganizations,
    loading,
    error,

    // Access information
    accessScope,
    canSwitchOrganizations: isSuperAdmin(user),

    // Utility functions
    getEffectiveOrganizationId,
    getOrganizationQueryParams,
    filterByOrganizationAccess,
    canAccessOrganization,
    getScopeDisplayInfo,

    // Actions
    handleOrganizationChange,
    resetScope,
    refreshOrganizations: fetchOrganizations,

    // API helpers
    createScopedApiCall
  };
};

/**
 * Hook for organization-scoped data fetching
 * Automatically applies organization filtering to API calls
 */
export const useOrganizationScopedData = (fetchFunction, dependencies = []) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const { getOrganizationQueryParams, getEffectiveOrganizationId } = useOrganizationScope();

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const queryParams = getOrganizationQueryParams();
      const result = await fetchFunction(queryParams);
      setData(result);
    } catch (err) {
      setError(err.message || 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  }, [fetchFunction, getOrganizationQueryParams, ...dependencies]);

  useEffect(() => {
    fetchData();
  }, [fetchData, getEffectiveOrganizationId()]);

  return {
    data,
    loading,
    error,
    refetch: fetchData
  };
};

export default useOrganizationScope;