// frontend/src/services/warehouseLocationsService.js

import { api, API_BASE_URL } from './api';

/**
 * Service for warehouse location management API calls.
 */

/**
 * Helper: trigger a browser download from a Blob.
 * Creates a temporary object URL, clicks a hidden <a>, then cleans up.
 * @param {Blob} blob - The file blob to download
 * @param {string} filename - Suggested filename for the download
 */
const downloadBlob = (blob, filename) => {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.style.display = 'none';
  document.body.appendChild(a);
  a.click();
  // Clean up
  setTimeout(() => {
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }, 100);
};

/**
 * Generate label PDF for selected locations and trigger download.
 * @param {string} warehouseId - The warehouse UUID
 * @param {Array<string>} locationIds - Array of location UUIDs to generate labels for
 * @returns {Promise<void>}
 */
const generateLabels = async (warehouseId, locationIds) => {
  const token = localStorage.getItem('authToken');
  const response = await fetch(`${API_BASE_URL}/warehouses/${warehouseId}/locations/labels`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ location_ids: locationIds }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Failed to generate labels' }));
    throw new Error(errorData.detail || 'Failed to generate labels');
  }

  const blob = await response.blob();
  downloadBlob(blob, `labels-${warehouseId}.pdf`);
};

/**
 * Generate label PDF for ALL locations in a warehouse and trigger download.
 * @param {string} warehouseId - The warehouse UUID
 * @returns {Promise<void>}
 */
const generateAllLabels = async (warehouseId) => {
  const token = localStorage.getItem('authToken');
  const response = await fetch(`${API_BASE_URL}/warehouses/${warehouseId}/locations/labels/all`, {
    method: 'GET',
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Failed to generate labels' }));
    throw new Error(errorData.detail || 'Failed to generate labels');
  }

  const blob = await response.blob();
  downloadBlob(blob, `all-labels-${warehouseId}.pdf`);
};

/**
 * Get all locations for a warehouse.
 * @param {string} warehouseId - The warehouse UUID
 * @returns {Promise<Array>} Array of location objects
 */
const getLocations = async (warehouseId) => {
  const response = await api.get(`/warehouses/${warehouseId}/locations`);
  return response;
};

/**
 * Create a new location in a warehouse.
 * @param {string} warehouseId - The warehouse UUID
 * @param {object} locationData - { location_code, description }
 * @returns {Promise<Object>} Created location object
 */
const createLocation = async (warehouseId, locationData) => {
  const response = await api.post(`/warehouses/${warehouseId}/locations`, locationData);
  return response;
};

/**
 * Update an existing location.
 * @param {string} locationId - The location UUID
 * @param {object} locationData - { location_code?, description? }
 * @returns {Promise<Object>} Updated location object
 */
const updateLocation = async (locationId, locationData) => {
  const response = await api.put(`/warehouse-locations/${locationId}`, locationData);
  return response;
};

/**
 * Delete a location.
 * @param {string} locationId - The location UUID
 * @returns {Promise<null>} 204 No Content
 */
const deleteLocation = async (locationId) => {
  const response = await api.delete(`/warehouse-locations/${locationId}`);
  return response;
};

/**
 * Assign one or more inventory items to a location.
 * @param {string} locationId - The location UUID
 * @param {Array<string>} inventoryIds - Array of inventory UUIDs to assign
 * @returns {Promise<Array>} Array of parts now at this location
 */
const assignParts = async (locationId, inventoryIds) => {
  const response = await api.post(`/warehouse-locations/${locationId}/assign`, {
    inventory_ids: inventoryIds,
  });
  return response;
};

/**
 * Remove an inventory item from a location.
 * @param {string} locationId - The location UUID
 * @param {string} inventoryId - The inventory UUID to unassign
 * @returns {Promise<null>} 204 No Content
 */
const unassignPart = async (locationId, inventoryId) => {
  const response = await api.delete(`/warehouse-locations/${locationId}/unassign/${inventoryId}`);
  return response;
};

/**
 * Get all parts stored at a specific location.
 * @param {string} locationId - The location UUID
 * @returns {Promise<Array>} Array of part location info objects
 */
const getPartsAtLocation = async (locationId) => {
  const response = await api.get(`/warehouse-locations/${locationId}/parts`);
  return response;
};

/**
 * Get all locations where a specific inventory item (part) is stored.
 * Used by the "Where is this?" / "Find Part" feature.
 * @param {string} inventoryId - The inventory UUID
 * @returns {Promise<Array>} Array of WarehouseLocationResponse objects
 */
const getLocationsForPart = async (inventoryId) => {
  const response = await api.get(`/warehouse-locations/find-part/${inventoryId}`);
  return response;
};

export const warehouseLocationsService = {
  getLocations,
  createLocation,
  updateLocation,
  deleteLocation,
  assignParts,
  unassignPart,
  getPartsAtLocation,
  getLocationsForPart,
  generateLabels,
  generateAllLabels,
};
