// frontend/src/components/OrganizationSelector.js

import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import { isSuperAdmin } from '../utils/permissions';
import { getCountryFlag } from '../utils/countryFlags';
import { organizationsService } from '../services/organizationsService';

const OrganizationSelector = ({ selectedOrganization, onOrganizationChange }) => {
  const { user } = useAuth();
  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchOrganizations = async () => {
      if (!isSuperAdmin(user)) return;

      setLoading(true);
      try {
        const data = await organizationsService.getOrganizations();
        setOrganizations(data);
      } catch (error) {
        console.error('Failed to fetch organizations:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchOrganizations();
  }, [user]);

  // Don't show selector for non-superadmin users
  if (!isSuperAdmin(user)) {
    return null;
  }

  return (
    <div className="flex items-center space-x-3">
      <label htmlFor="organization-selector" className="text-sm font-medium text-gray-700">
        Organization:
      </label>
      <select
        id="organization-selector"
        value={selectedOrganization || ''}
        onChange={(e) => onOrganizationChange(e.target.value || null)}
        className="block w-48 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm bg-white"
        disabled={loading}
      >
        <option value="">All Organizations</option>
        {organizations.map((org) => (
          <option key={org.id} value={org.id}>
            {getCountryFlag(org.country)} {org.name} ({org.organization_type})
          </option>
        ))}
      </select>
      {loading && (
        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
      )}
    </div>
  );
};

export default OrganizationSelector;