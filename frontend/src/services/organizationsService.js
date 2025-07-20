// c:/abparts/frontend/src/services/organizationsService.js

import { api } from './api';

/**
 * Organization types enum
 */
export const OrganizationType = {
  ORASEAS_EE: "oraseas_ee",
  BOSSAQUA: "bossaqua",
  CUSTOMER: "customer",
  SUPPLIER: "supplier"
};

/**
 * Organization type display configuration
 */
export const ORGANIZATION_TYPE_CONFIG = {
  [OrganizationType.ORASEAS_EE]: {
    label: 'Oraseas EE',
    description: 'App owner and primary distributor',
    color: 'bg-blue-100 text-blue-800',
    icon: '🏢',
    singleton: true
  },
  [OrganizationType.BOSSAQUA]: {
    label: 'BossAqua',
    description: 'Manufacturer of AutoBoss machines',
    color: 'bg-green-100 text-green-800',
    icon: '🏭',
    singleton: true
  },
  [OrganizationType.CUSTOMER]: {
    label: 'Customer',
    description: 'Organizations that purchase machines',
    color: 'bg-purple-100 text-purple-800',
    icon: '🏪',
    singleton: false
  },
  [OrganizationType.SUPPLIER]: {
    label: 'Supplier',
    description: 'Third-party parts suppliers',
    color: 'bg-orange-100 text-orange-800',
    icon: '📦',
    singleton: false
  }
};

/**
 * Fetches all organizations with optional filtering.
 * @param {object} filters Optional filters for organizations
 */
const getOrganizations = (filters = {}) => {
  // Build query string from filters
  const queryParams = new URLSearchParams();
  Object.keys(filters).forEach(key => {
    if (filters[key] !== undefined && filters[key] !== null && filters[key] !== '') {
      queryParams.append(key, filters[key]);
    }
  });

  const queryString = queryParams.toString();
  const endpoint = queryString ? `/organizations?${queryString}` : '/organizations';

  return api.get(endpoint);
};

/**
 * Get a single organization by ID
 * @param {string} id Organization ID
 */
const getOrganization = (id) => {
  return api.get(`/organizations/${id}`);
};

/**
 * Creates a new organization.
 * @param {object} orgData The data for the new organization.
 */
const createOrganization = (orgData) => {
  return api.post('/organizations', orgData);
};

/**
 * Updates an existing organization.
 * @param {string} orgId The ID of the organization to update.
 * @param {object} orgData The updated data for the organization.
 */
const updateOrganization = (orgId, orgData) => {
  return api.put(`/organizations/${orgId}`, orgData);
};

/**
 * Deletes an organization.
 * @param {string} orgId The ID of the organization to delete.
 */
const deleteOrganization = (orgId) => {
  return api.delete(`/organizations/${orgId}`);
};

/**
 * Get organization hierarchy for tree visualization
 */
const getOrganizationHierarchy = () => {
  return api.get('/organizations/hierarchy');
};

/**
 * Get organization statistics
 */
const getOrganizationStats = () => {
  return api.get('/organizations/stats');
};

/**
 * Get potential parent organizations for a given organization type
 * @param {string} organizationType Organization type
 */
const getPotentialParentOrganizations = (organizationType) => {
  const queryParams = new URLSearchParams();
  queryParams.append('organization_type', organizationType);
  return api.get(`/organizations/potential-parents?${queryParams.toString()}`);
};

/**
 * Validate organization creation/update
 * @param {object} data Organization data
 * @param {string} id Optional organization ID for updates
 */
const validateOrganization = (data, id = null) => {
  return api.post('/organizations/validate', { ...data, id });
};

/**
 * Get organization children
 * @param {string} parentId Parent organization ID
 */
const getOrganizationChildren = (parentId) => {
  return api.get(`/organizations/${parentId}/children`);
};

/**
 * Transfer organization ownership (super admin only)
 * @param {string} organizationId Organization ID
 * @param {string} newParentId New parent organization ID
 */
const transferOrganizationOwnership = (organizationId, newParentId) => {
  return api.post(`/organizations/${organizationId}/transfer`, {
    new_parent_id: newParentId
  });
};

export const organizationsService = {
  getOrganizations,
  getOrganization,
  createOrganization,
  updateOrganization,
  deleteOrganization,
  getOrganizationHierarchy,
  getOrganizationStats,
  getPotentialParentOrganizations,
  validateOrganization,
  getOrganizationChildren,
  transferOrganizationOwnership,
};