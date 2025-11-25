// c:/abparts/frontend/src/services/partsService.js

import { api } from './api';
import { processError, logError } from '../utils/errorHandling';

/**
 * Fetches all parts without pagination limit.
 * @returns {Promise<Array>} Array of parts
 * @throws {Error} Throws error with user-friendly message
 */
const getParts = async () => {
  try {
    // Fetch with high limit to get all parts (backend max is 1000)
    const response = await api.get('/parts/?limit=1000');
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
    const response = await api.post('/parts/', partData);
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
 * @returns {Promise<Object>} Object with items array and metadata
 * @throws {Error} Throws error with user-friendly message
 */
const getPartsWithInventory = async (filters = {}) => {
  try {
    const queryParams = new URLSearchParams();

    // Always include count for analytics
    queryParams.append('include_count', 'true');

    // Add cache-busting parameter to ensure fresh data
    queryParams.append('_t', Date.now().toString());

    if (filters && typeof filters === 'object') {
      Object.keys(filters).forEach(key => {
        if (filters[key] !== undefined && filters[key] !== null && filters[key] !== '') {
          queryParams.append(key, filters[key]);
        }
      });
    }

    const queryString = queryParams.toString();
    const endpoint = queryString ? `/parts/with-inventory?${queryString}` : '/parts/with-inventory?include_count=true';

    const response = await api.get(endpoint);

    // Handle the correct API response structure: {items: [...], total_count: number, has_more: boolean}
    if (response && typeof response === 'object' && Array.isArray(response.items)) {
      return {
        items: response.items,
        total_count: response.total_count || response.items.length,
        has_more: response.has_more || false
      };
    }

    // Fallback: if response is already an array (for backward compatibility)
    if (Array.isArray(response)) {
      return {
        items: response,
        total_count: response.length,
        has_more: false
      };
    }

    // If response is malformed, log warning and return empty result
    console.warn('API returned unexpected response format for parts with inventory:', response);
    return {
      items: [],
      total_count: 0,
      has_more: false
    };
  } catch (error) {
    logError(error, 'partsService.getPartsWithInventory');
    throw error;
  }
};

/**
 * Fetches all parts for analytics (without pagination limits).
 * @returns {Promise<Object>} Object with all parts and analytics data
 * @throws {Error} Throws error with user-friendly message
 */
const getAllPartsForAnalytics = async () => {
  try {
    // Fetch with a high limit to get all parts for analytics
    const response = await api.get('/parts/with-inventory?include_count=true&limit=10000');

    // Handle the correct API response structure
    if (response && typeof response === 'object' && Array.isArray(response.items)) {
      return {
        items: response.items,
        total_count: response.total_count || response.items.length,
        has_more: response.has_more || false
      };
    }

    // Fallback: if response is already an array
    if (Array.isArray(response)) {
      return {
        items: response,
        total_count: response.length,
        has_more: false
      };
    }

    return {
      items: [],
      total_count: 0,
      has_more: false
    };
  } catch (error) {
    logError(error, 'partsService.getAllPartsForAnalytics');
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

    if (filters && typeof filters === 'object') {
      Object.keys(filters).forEach(key => {
        if (filters[key] !== undefined && filters[key] !== null && filters[key] !== '') {
          queryParams.append(key, filters[key]);
        }
      });
    }

    const response = await api.get(`/parts/search-with-inventory?${queryParams.toString()}`);

    // Handle the correct API response structure: {items: [...], total_count: number, has_more: boolean}
    if (response && typeof response === 'object' && Array.isArray(response.items)) {
      return response.items;
    }

    // Fallback: if response is already an array (for backward compatibility)
    if (Array.isArray(response)) {
      return response;
    }

    // If response is malformed, log warning and return empty array
    console.warn('API returned unexpected response format for parts search with inventory:', response);
    return [];
  } catch (error) {
    logError(error, 'partsService.searchPartsWithInventory');
    throw error;
  }
};

/**
 * Fetches parts sorted by order frequency for a specific organization and order type.
 * @param {string} organizationId The organization ID to get order frequency for
 * @param {string} orderType The order type: 'customer' or 'supplier'
 * @param {object} options Optional parameters like skip and limit
 * @returns {Promise<Array>} Array of parts sorted by order frequency
 * @throws {Error} Throws error with user-friendly message
 */
const getPartsForOrders = async (organizationId, orderType = 'customer', options = {}) => {
  try {
    const queryParams = new URLSearchParams();

    if (organizationId) {
      queryParams.append('organization_id', organizationId);
    }

    queryParams.append('order_type', orderType);

    if (options.skip) {
      queryParams.append('skip', options.skip);
    }

    if (options.limit) {
      queryParams.append('limit', options.limit);
    }

    const response = await api.get(`/parts/for-orders?${queryParams.toString()}`);

    // Handle the correct API response structure: {items: [...], total_count: number, has_more: boolean}
    if (response && typeof response === 'object' && Array.isArray(response.items)) {
      return response.items;
    }

    // Fallback: if response is already an array (for backward compatibility)
    if (Array.isArray(response)) {
      return response;
    }

    // If response is malformed, log warning and return empty array
    console.warn('API returned unexpected response format for parts for orders:', response);
    return [];
  } catch (error) {
    logError(error, 'partsService.getPartsForOrders');
    // Fallback to regular parts if the new endpoint fails
    try {
      const fallbackResponse = await getParts();
      return Array.isArray(fallbackResponse) ? fallbackResponse : fallbackResponse.items || [];
    } catch (fallbackError) {
      throw error; // Throw original error if fallback also fails
    }
  }
};

export const partsService = {
  getParts,
  createPart,
  updatePart,
  deletePart,
  uploadImage,
  getPartsWithInventory,
  getAllPartsForAnalytics,
  getPartWithInventory,
  searchPartsWithInventory,
  getPartsForOrders,
};