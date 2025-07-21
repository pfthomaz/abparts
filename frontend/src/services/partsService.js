// c:/abparts/frontend/src/services/partsService.js

import { api } from './api';
import { processError, logError } from '../utils/errorHandling';

/**
 * Fetches all parts.
 * @returns {Promise<Array>} Array of parts
 * @throws {Error} Throws error with user-friendly message
 */
const getParts = async () => {
  try {
    const response = await api.get('/parts');
    return response;
  } catch (error) {
    logError(error, 'partsService.getParts');
    throw error;
  }
};

/**
 * Creates a new part.
 * @param {object} partData The data for the new part.
 * @returns {Promise<Object>} Created part object
 * @throws {Error} Throws error with user-friendly message
 */
const createPart = async (partData) => {
  try {
    const response = await api.post('/parts', partData);
    return response;
  } catch (error) {
    logError(error, 'partsService.createPart');
    throw error;
  }
};

/**
 * Updates an existing part.
 * @param {string} partId The ID of the part to update.
 * @param {object} partData The updated data for the part.
 * @returns {Promise<Object>} Updated part object
 * @throws {Error} Throws error with user-friendly message
 */
const updatePart = async (partId, partData) => {
  try {
    const response = await api.put(`/parts/${partId}`, partData);
    return response;
  } catch (error) {
    logError(error, 'partsService.updatePart');
    throw error;
  }
};

/**
 * Deletes a part.
 * @param {string} partId The ID of the part to delete.
 * @returns {Promise<void>} 
 * @throws {Error} Throws error with user-friendly message
 */
const deletePart = async (partId) => {
  try {
    const response = await api.delete(`/parts/${partId}`);
    return response;
  } catch (error) {
    logError(error, 'partsService.deletePart');
    throw error;
  }
};

/**
 * Uploads an image file for a part.
 * @param {FormData} formData The form data containing the file.
 * @returns {Promise<Object>} Upload response with image URL
 * @throws {Error} Throws error with user-friendly message
 */
const uploadImage = async (formData) => {
  try {
    // The generic api client will handle the content type for FormData.
    const response = await api.post('/parts/upload-image', formData);
    return response;
  } catch (error) {
    logError(error, 'partsService.uploadImage');
    throw error;
  }
};

/**
 * Fetches all parts with inventory information across warehouses.
 * @param {object} filters Optional filters for parts and inventory
 * @returns {Promise<Array>} Array of parts with inventory information
 * @throws {Error} Throws error with user-friendly message
 */
const getPartsWithInventory = async (filters = {}) => {
  try {
    const queryParams = new URLSearchParams();
    Object.keys(filters).forEach(key => {
      if (filters[key] !== undefined && filters[key] !== null && filters[key] !== '') {
        queryParams.append(key, filters[key]);
      }
    });

    const queryString = queryParams.toString();
    const endpoint = queryString ? `/parts/with-inventory?${queryString}` : '/parts/with-inventory';

    const response = await api.get(endpoint);

    // Ensure we always return an array, even if the response is malformed
    if (!Array.isArray(response)) {
      console.warn('API returned non-array response for parts with inventory:', response);
      return [];
    }

    return response;
  } catch (error) {
    logError(error, 'partsService.getPartsWithInventory');
    throw error;
  }
};

/**
 * Get a specific part with inventory information.
 * @param {string} partId The ID of the part.
 * @param {string} organizationId Optional organization ID filter.
 * @returns {Promise<Object>} Part with inventory information
 * @throws {Error} Throws error with user-friendly message
 */
const getPartWithInventory = async (partId, organizationId = null) => {
  try {
    const queryParams = new URLSearchParams();
    if (organizationId) {
      queryParams.append('organization_id', organizationId);
    }

    const queryString = queryParams.toString();
    const endpoint = queryString ? `/parts/${partId}/with-inventory?${queryString}` : `/parts/${partId}/with-inventory`;

    const response = await api.get(endpoint);
    return response;
  } catch (error) {
    logError(error, 'partsService.getPartWithInventory');
    throw error;
  }
};

/**
 * Search parts with inventory information.
 * @param {string} searchTerm The search query.
 * @param {object} filters Optional additional filters.
 * @returns {Promise<Array>} Array of parts matching search criteria with inventory information
 * @throws {Error} Throws error with user-friendly message
 */
const searchPartsWithInventory = async (searchTerm, filters = {}) => {
  try {
    const queryParams = new URLSearchParams();
    queryParams.append('q', searchTerm);

    Object.keys(filters).forEach(key => {
      if (filters[key] !== undefined && filters[key] !== null && filters[key] !== '') {
        queryParams.append(key, filters[key]);
      }
    });

    const response = await api.get(`/parts/search-with-inventory?${queryParams.toString()}`);

    // Ensure we always return an array, even if the response is malformed
    if (!Array.isArray(response)) {
      console.warn('API returned non-array response for parts search with inventory:', response);
      return [];
    }

    return response;
  } catch (error) {
    logError(error, 'partsService.searchPartsWithInventory');
    throw error;
  }
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