// frontend/src/services/netsService.js

import { api } from './api';

/**
 * Fetches all nets for the current user's organization.
 * @param {string} farmSiteId Optional farm site ID to filter by.
 * @param {boolean} activeOnly Only return active nets.
 * @param {number} skip Number of records to skip.
 * @param {number} limit Maximum number of records to return.
 */
const getNets = (farmSiteId = null, activeOnly = true, skip = 0, limit = 100) => {
  let url = `/nets/?active_only=${activeOnly}&skip=${skip}&limit=${limit}`;
  if (farmSiteId) {
    url += `&farm_site_id=${farmSiteId}`;
  }
  return api.get(url);
};

/**
 * Searches nets by name.
 * @param {string} searchTerm The search query.
 * @param {number} skip Number of records to skip.
 * @param {number} limit Maximum number of records to return.
 */
const searchNets = (searchTerm, skip = 0, limit = 100) => {
  return api.get(`/nets/search?q=${encodeURIComponent(searchTerm)}&skip=${skip}&limit=${limit}`);
};

/**
 * Fetches a single net by ID with its cleaning history.
 * @param {string} netId The ID of the net to fetch.
 */
const getNet = (netId) => {
  return api.get(`/nets/${netId}`);
};

/**
 * Creates a new net.
 * @param {object} netData The data for the new net.
 */
const createNet = (netData) => {
  return api.post('/nets/', netData);
};

/**
 * Updates an existing net.
 * @param {string} netId The ID of the net to update.
 * @param {object} netData The updated data for the net.
 */
const updateNet = (netId, netData) => {
  return api.put(`/nets/${netId}`, netData);
};

/**
 * Deletes a net (soft delete - sets active=false).
 * @param {string} netId The ID of the net to delete.
 */
const deleteNet = (netId) => {
  return api.delete(`/nets/${netId}`);
};

/**
 * Gets all nets for a specific farm site.
 * @param {string} farmSiteId The ID of the farm site.
 * @param {boolean} activeOnly Only return active nets.
 */
const getNetsByFarmSite = (farmSiteId, activeOnly = true) => {
  return getNets(farmSiteId, activeOnly, 0, 1000);
};

const netsService = {
  getNets,
  searchNets,
  getNet,
  createNet,
  updateNet,
  deleteNet,
  getNetsByFarmSite,
};

export default netsService;
