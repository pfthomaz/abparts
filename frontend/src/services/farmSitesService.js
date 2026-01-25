// frontend/src/services/farmSitesService.js

import { api } from './api';

/**
 * Fetches all farm sites for the current user's organization.
 * @param {boolean} activeOnly Only return active farm sites.
 * @param {number} skip Number of records to skip.
 * @param {number} limit Maximum number of records to return.
 */
const getFarmSites = (activeOnly = true, skip = 0, limit = 100) => {
  return api.get(`/farm-sites/?active_only=${activeOnly}&skip=${skip}&limit=${limit}`);
};

/**
 * Searches farm sites by name or location.
 * @param {string} searchTerm The search query.
 * @param {number} skip Number of records to skip.
 * @param {number} limit Maximum number of records to return.
 */
const searchFarmSites = (searchTerm, skip = 0, limit = 100) => {
  return api.get(`/farm-sites/search?q=${encodeURIComponent(searchTerm)}&skip=${skip}&limit=${limit}`);
};

/**
 * Fetches a single farm site by ID with its nets.
 * @param {string} farmSiteId The ID of the farm site to fetch.
 */
const getFarmSite = (farmSiteId) => {
  return api.get(`/farm-sites/${farmSiteId}`);
};

/**
 * Creates a new farm site.
 * @param {object} farmSiteData The data for the new farm site.
 */
const createFarmSite = (farmSiteData) => {
  return api.post('/farm-sites/', farmSiteData);
};

/**
 * Updates an existing farm site.
 * @param {string} farmSiteId The ID of the farm site to update.
 * @param {object} farmSiteData The updated data for the farm site.
 */
const updateFarmSite = (farmSiteId, farmSiteData) => {
  return api.put(`/farm-sites/${farmSiteId}`, farmSiteData);
};

/**
 * Deletes a farm site (soft delete - sets active=false).
 * @param {string} farmSiteId The ID of the farm site to delete.
 */
const deleteFarmSite = (farmSiteId) => {
  return api.delete(`/farm-sites/${farmSiteId}`);
};

const farmSitesService = {
  getFarmSites,
  searchFarmSites,
  getFarmSite,
  createFarmSite,
  updateFarmSite,
  deleteFarmSite,
};

export default farmSitesService;
