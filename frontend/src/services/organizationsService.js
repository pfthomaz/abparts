// c:/abparts/frontend/src/services/organizationsService.js

import { api } from './api';

/**
 * Fetches all organizations.
 */
const getOrganizations = () => {
  return api.get('/organizations');
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

export const organizationsService = {
  getOrganizations,
  createOrganization,
  updateOrganization,
  deleteOrganization,
};