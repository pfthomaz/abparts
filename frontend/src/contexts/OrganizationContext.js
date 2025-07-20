// frontend/src/contexts/OrganizationContext.js

import React, { createContext, useState, useContext, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import { organizationsService } from '../services/organizationsService';
import { isSuperAdmin } from '../utils/permissions';

// Create Organization Context
const OrganizationContext = createContext(null);

// Organization Provider Component
export const OrganizationProvider = ({ children }) => {
  const { user } = useAuth();
  const [selectedOrganization, setSelectedOrganization] = useState(null);
  const [availableOrganizations, setAvailableOrganizations] = useState([]);
  const [loading, setLoading] = useState(false);

  // Fetch available organizations for super admin
  useEffect(() => {
    const fetchOrganizations = async () => {
      if (!user) return;

      if (isSuperAdmin(user)) {
        setLoading(true);
        try {
          const response = await organizationsService.getOrganizations();
          const organizations = response.data || response;
          setAvailableOrganizations(organizations);

          // Set default to user's own organization if not already selected
          if (!selectedOrganization && user.organization_id) {
            const userOrg = organizations.find(org => org.id === user.organization_id);
            if (userOrg) {
              setSelectedOrganization(userOrg);
            }
          }
        } catch (error) {
          console.error('Failed to fetch organizations:', error);
          setAvailableOrganizations([]);
        } finally {
          setLoading(false);
        }
      } else {
        // For non-super admins, set their own organization
        if (user.organization) {
          setSelectedOrganization(user.organization);
          setAvailableOrganizations([user.organization]);
        }
      }
    };

    fetchOrganizations();
  }, [user, selectedOrganization]);

  // Switch organization (super admin only)
  const switchOrganization = (organization) => {
    if (isSuperAdmin(user)) {
      setSelectedOrganization(organization);
      // Store in localStorage for persistence
      localStorage.setItem('selectedOrganizationId', organization.id);
    }
  };

  // Get current organization context for data filtering
  const getCurrentOrganizationId = () => {
    if (isSuperAdmin(user)) {
      return selectedOrganization?.id || user.organization_id;
    }
    return user?.organization_id;
  };

  // Check if user can view data for specific organization
  const canViewOrganizationData = (organizationId) => {
    if (isSuperAdmin(user)) {
      return true; // Super admin can view all organizations
    }
    return user?.organization_id === organizationId;
  };

  // Get organization display name
  const getOrganizationDisplayName = (organizationId) => {
    const org = availableOrganizations.find(o => o.id === organizationId);
    return org?.name || 'Unknown Organization';
  };

  // Reset organization context on user change
  useEffect(() => {
    if (!user) {
      setSelectedOrganization(null);
      setAvailableOrganizations([]);
      localStorage.removeItem('selectedOrganizationId');
    }
  }, [user]);

  // Restore selected organization from localStorage on mount
  useEffect(() => {
    if (isSuperAdmin(user) && availableOrganizations.length > 0) {
      const savedOrgId = localStorage.getItem('selectedOrganizationId');
      if (savedOrgId && !selectedOrganization) {
        const savedOrg = availableOrganizations.find(org => org.id === savedOrgId);
        if (savedOrg) {
          setSelectedOrganization(savedOrg);
        }
      }
    }
  }, [user, availableOrganizations, selectedOrganization]);

  const value = {
    selectedOrganization,
    availableOrganizations,
    loading,
    switchOrganization,
    getCurrentOrganizationId,
    canViewOrganizationData,
    getOrganizationDisplayName,
    isSuperAdminMode: isSuperAdmin(user)
  };

  return (
    <OrganizationContext.Provider value={value}>
      {children}
    </OrganizationContext.Provider>
  );
};

// Custom hook to use the Organization Context
export const useOrganization = () => {
  const context = useContext(OrganizationContext);
  if (!context) {
    throw new Error('useOrganization must be used within an OrganizationProvider');
  }
  return context;
};

export default OrganizationContext;