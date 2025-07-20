// frontend/src/components/OrganizationSwitcher.js

import React, { useState, useRef, useEffect } from 'react';
import { useOrganization } from '../contexts/OrganizationContext';
import { useAuth } from '../AuthContext';
import { isSuperAdmin } from '../utils/permissions';

/**
 * OrganizationSwitcher component for super admins to switch between organizations
 */
const OrganizationSwitcher = () => {
  const { user } = useAuth();
  const {
    selectedOrganization,
    availableOrganizations,
    switchOrganization,
    loading,
    isSuperAdminMode
  } = useOrganization();

  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Only show for super admins
  if (!isSuperAdmin(user) || !isSuperAdminMode) {
    return null;
  }

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleOrganizationSelect = (organization) => {
    switchOrganization(organization);
    setIsOpen(false);
  };

  const getOrganizationTypeIcon = (orgType) => {
    switch (orgType) {
      case 'oraseas_ee':
        return '🏢';
      case 'bossaqua':
        return '🏭';
      case 'customer':
        return '🏪';
      case 'supplier':
        return '📦';
      default:
        return '🏢';
    }
  };

  const getOrganizationTypeLabel = (orgType) => {
    switch (orgType) {
      case 'oraseas_ee':
        return 'Oraseas EE';
      case 'bossaqua':
        return 'BossAqua';
      case 'customer':
        return 'Customer';
      case 'supplier':
        return 'Supplier';
      default:
        return orgType;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center space-x-2 px-3 py-2 text-sm text-gray-500">
        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
        <span>Loading organizations...</span>
      </div>
    );
  }

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-3 py-2 text-sm bg-blue-50 border border-blue-200 rounded-md hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
      >
        <div className="flex items-center space-x-2">
          <span className="text-lg">
            {selectedOrganization ? getOrganizationTypeIcon(selectedOrganization.organization_type) : '🏢'}
          </span>
          <div className="text-left">
            <div className="font-medium text-blue-900">
              {selectedOrganization?.name || 'Select Organization'}
            </div>
            <div className="text-xs text-blue-600">
              {selectedOrganization ? getOrganizationTypeLabel(selectedOrganization.organization_type) : 'Super Admin View'}
            </div>
          </div>
        </div>
        <svg
          className={`w-4 h-4 text-blue-600 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-md shadow-lg border border-gray-200 z-50 max-h-96 overflow-y-auto">
          <div className="py-2">
            <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wide border-b border-gray-100">
              Switch Organization View
            </div>

            {availableOrganizations.map((org) => (
              <button
                key={org.id}
                onClick={() => handleOrganizationSelect(org)}
                className={`w-full text-left px-4 py-3 hover:bg-gray-50 flex items-center space-x-3 transition-colors ${selectedOrganization?.id === org.id ? 'bg-blue-50 border-r-2 border-blue-500' : ''
                  }`}
              >
                <span className="text-lg">{getOrganizationTypeIcon(org.organization_type)}</span>
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-gray-900 truncate">{org.name}</div>
                  <div className="text-sm text-gray-500 flex items-center space-x-2">
                    <span>{getOrganizationTypeLabel(org.organization_type)}</span>
                    {org.warehouses_count !== undefined && (
                      <span className="text-xs bg-gray-100 px-2 py-0.5 rounded">
                        {org.warehouses_count} warehouses
                      </span>
                    )}
                    {org.users_count !== undefined && (
                      <span className="text-xs bg-gray-100 px-2 py-0.5 rounded">
                        {org.users_count} users
                      </span>
                    )}
                  </div>
                </div>
                {selectedOrganization?.id === org.id && (
                  <svg className="w-5 h-5 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                )}
              </button>
            ))}

            {availableOrganizations.length === 0 && (
              <div className="px-4 py-3 text-sm text-gray-500 text-center">
                No organizations available
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default OrganizationSwitcher;