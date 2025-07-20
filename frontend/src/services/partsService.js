// c:/abparts/frontend/src/services/partsService.js

import { api } from './api';

/**
 * Fetches all parts.
 */
const getParts = () => {
  return api.get('/parts');
};

/**
 * Creates a new part.
 * @param {object} partData The data for the new part.
 */
const createPart = (partData) => {
  return api.post('/parts', partData);
};

/**
 * Updates an existing part.
 * @param {string} partId The ID of the part to update.
 * @param {object} partData The updated data for the part.
 */
const updatePart = (partId, partData) => {
  return api.put(`/parts/${partId}`, partData);
};

/**
 * Deletes a part.
 * @param {string} partId The ID of the part to delete.
 */
const deletePart = (partId) => {
  return api.delete(`/parts/${partId}`);
};

/**
 * Uploads an image file for a part.
 * @param {FormData} formData The form data containing the file.
 */
const uploadImage = (formData) => {
  // The generic api client will handle the content type for FormData.
  return api.post('/parts/upload-image', formData);
};

/**
 * Fetches all parts with inventory information across warehouses.
 * @param {object} filters Optional filters for parts and inventory
 */
const getPartsWithInventory = (filters = {}) => {
  const queryParams = new URLSearchParams();
  Object.keys(filters).forEach(key => {
    if (filters[key] !== undefined && filters[key] !== null && filters[key] !== '') {
      queryParams.append(key, filters[key]);
    }
  });

  const queryString = queryParams.toString();
  const endpoint = queryString ? `/parts/with-inventory?${queryString}` : '/parts/with-inventory';
  return api.get(endpoint);
};

/**
 * Get a specific part with inventory information.
 * @param {string} partId The ID of the part.
 * @param {string} organizationId Optional organization ID filter.
 */
const getPartWithInventory = (partId, organizationId = null) => {
  const queryParams = new URLSearchParams();
  if (organizationId) {
    queryParams.append('organization_id', organizationId);
  }

  const queryString = queryParams.toString();
  const endpoint = queryString ? `/parts/${partId}/with-inventory?${queryString}` : `/parts/${partId}/with-inventory`;
  return api.get(endpoint);
};

/**
 * Search parts with inventory information.
 * @param {string} searchTerm The search query.
 * @param {object} filters Optional additional filters.
 */
const searchPartsWithInventory = (searchTerm, filters = {}) => {
  const queryParams = new URLSearchParams();
  queryParams.append('q', searchTerm);

  Object.keys(filters).forEach(key => {
    if (filters[key] !== undefined && filters[key] !== null && filters[key] !== '') {
      queryParams.append(key, filters[key]);
    }
  });

  return api.get(`/parts/search-with-inventory?${queryParams.toString()}`);
};

export const partsService = {
  getParts,
  createPart,
  updatePart,
  deletePart,
  uploadImage,
  getPartsWithInventory,
  getPartWithInventory,
  searchPartsWithInventory,
};