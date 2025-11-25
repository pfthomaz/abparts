// frontend/src/services/warehouseService.js

import { api } from './api';

/**
 * Fetches all warehouses with optional filtering.
 * @param {object} filters Optional filters for warehouses
 */
const getWarehouses = (filters = {}) => {
  // Build query string from filters
  const queryParams = new URLSearchParams();
  if (filters && typeof filters === 'object') {
    Object.keys(filters).forEach(key => {
      if (filters[key] !== undefined && filters[key] !== null && filters[key] !== '') {
        queryParams.append(key, filters[key]);
      }
    });
  }

  const queryString = queryParams.toString();
  const endpoint = queryString ? `/warehouses/?${queryString}` : '/warehouses/';

  return api.get(endpoint);
};

/**
 * Search warehouses by name, location, or description
 * @param {string} query Search query
 * @param {object} filters Optional filters
 */
const searchWarehouses = (query, filters = {}) => {
  const queryParams = new URLSearchParams();
  queryParams.append('q', query);

  if (filters && typeof filters === 'object') {
    Object.keys(filters).forEach(key => {
      if (filters[key] !== undefined && filters[key] !== null && filters[key] !== '') {
        queryParams.append(key, filters[key]);
      }
    });
  }

  return api.get(`/warehouses/search/?${queryParams.toString()}`);
};

/**
 * Get a single warehouse by ID
 * @param {string} id Warehouse ID
 */
const getWarehouse = (id) => {
  return api.get(`/warehouses/${id}`);
};

/**
 * Get warehouse inventory summary
 * @param {string} id Warehouse ID
 */
const getWarehouseSummary = (id) => {
  return api.get(`/warehouses/${id}/summary`);
};

/**
 * Creates a new warehouse.
 * @param {object} warehouseData The data for the new warehouse.
 */
const createWarehouse = (warehouseData) => {
  return api.post('/warehouses/', warehouseData);
};

/**
 * Updates an existing warehouse.
 * @param {string} warehouseId The ID of the warehouse to update.
 * @param {object} warehouseData The updated data for the warehouse.
 */
const updateWarehouse = (warehouseId, warehouseData) => {
  return api.put(`/warehouses/${warehouseId}`, warehouseData);
};

/**
 * Activate a warehouse
 * @param {string} warehouseId The ID of the warehouse to activate
 */
const activateWarehouse = (warehouseId) => {
  return api.post(`/warehouses/${warehouseId}/activate`);
};

/**
 * Deactivate a warehouse
 * @param {string} warehouseId The ID of the warehouse to deactivate
 */
const deactivateWarehouse = (warehouseId) => {
  return api.post(`/warehouses/${warehouseId}/deactivate`);
};

/**
 * Deletes a warehouse.
 * @param {string} warehouseId The ID of the warehouse to delete.
 */
const deleteWarehouse = (warehouseId) => {
  return api.delete(`/warehouses/${warehouseId}`);
};

/**
 * Get warehouses for a specific organization
 * @param {string} organizationId Organization ID
 * @param {object} filters Optional filters
 */
const getOrganizationWarehouses = (organizationId, filters = {}) => {
  const queryParams = new URLSearchParams();
  if (filters && typeof filters === 'object') {
    Object.keys(filters).forEach(key => {
      if (filters[key] !== undefined && filters[key] !== null && filters[key] !== '') {
        queryParams.append(key, filters[key]);
      }
    });
  }

  const queryString = queryParams.toString();
  const endpoint = queryString
    ? `/warehouses/organization/${organizationId}/warehouses?${queryString}`
    : `/warehouses/organization/${organizationId}/warehouses`;

  return api.get(endpoint);
};

/**
 * Get warehouse performance metrics
 * @param {string} warehouseId Warehouse ID
 * @param {object} dateRange Optional date range filter
 */
const getWarehousePerformance = (warehouseId, dateRange = {}) => {
  const queryParams = new URLSearchParams();
  if (dateRange.start_date) queryParams.append('start_date', dateRange.start_date);
  if (dateRange.end_date) queryParams.append('end_date', dateRange.end_date);

  const queryString = queryParams.toString();
  const endpoint = queryString
    ? `/warehouses/${warehouseId}/performance?${queryString}`
    : `/warehouses/${warehouseId}/performance`;

  return api.get(endpoint);
};

/**
 * Get warehouse utilization metrics
 * @param {string} warehouseId Warehouse ID
 */
const getWarehouseUtilization = (warehouseId) => {
  return api.get(`/warehouses/${warehouseId}/utilization`);
};

/**
 * Reset stock levels for multiple parts in a warehouse
 * @param {string} warehouseId Warehouse ID
 * @param {object} resetData Stock reset data {adjustments, reason, notes}
 */
const resetStock = (warehouseId, resetData) => {
  return api.post(`/warehouses/${warehouseId}/stock-reset`, resetData);
};

export const warehouseService = {
  getWarehouses,
  searchWarehouses,
  getWarehouse,
  getWarehouseSummary,
  createWarehouse,
  updateWarehouse,
  activateWarehouse,
  deactivateWarehouse,
  deleteWarehouse,
  getOrganizationWarehouses,
  getWarehousePerformance,
  getWarehouseUtilization,
  resetStock,
};