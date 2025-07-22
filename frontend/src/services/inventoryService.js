// frontend/src/services/inventoryService.js

import { api } from './api';

/**
 * Fetches all inventory items with optional filtering.
 * @param {object} filters Optional filters for inventory
 */
const getInventory = (filters = {}) => {
  // Build query string from filters
  const queryParams = new URLSearchParams();
  Object.keys(filters).forEach(key => {
    if (filters[key] !== undefined && filters[key] !== null && filters[key] !== '') {
      queryParams.append(key, filters[key]);
    }
  });

  const queryString = queryParams.toString();
  const endpoint = queryString ? `/inventory?${queryString}` : '/inventory';

  return api.get(endpoint);
};

/**
 * Get inventory for a specific warehouse
 * @param {string} warehouseId Warehouse ID
 * @param {object} filters Optional additional filters
 */
const getWarehouseInventory = (warehouseId, filters = {}) => {
  const queryParams = new URLSearchParams();

  Object.keys(filters).forEach(key => {
    if (filters[key] !== undefined && filters[key] !== null && filters[key] !== '') {
      queryParams.append(key, filters[key]);
    }
  });

  const queryString = queryParams.toString();
  const endpoint = queryString ? `/inventory/warehouse/${warehouseId}?${queryString}` : `/inventory/warehouse/${warehouseId}`;

  return api.get(endpoint);
};

/**
 * Get aggregated inventory across all warehouses for an organization
 * @param {string} organizationId Organization ID
 */
const getOrganizationInventoryAggregation = (organizationId) => {
  return api.get(`/inventory/organization/${organizationId}/aggregated`);
};

/**
 * Get inventory analytics for a warehouse
 * @param {string} warehouseId Warehouse ID
 * @param {object} dateRange Optional date range filter
 */
const getWarehouseInventoryAnalytics = (warehouseId, dateRange = {}) => {
  const queryParams = new URLSearchParams();
  if (dateRange.start_date) queryParams.append('start_date', dateRange.start_date);
  if (dateRange.end_date) queryParams.append('end_date', dateRange.end_date);

  const queryString = queryParams.toString();
  const endpoint = queryString
    ? `/inventory/warehouse/${warehouseId}/analytics?${queryString}`
    : `/inventory/warehouse/${warehouseId}/analytics`;

  return api.get(endpoint);
};

/**
 * Transfer inventory between warehouses
 * @param {object} transferData Transfer details
 */
const transferInventory = (transferData) => {
  return api.post('/inventory/transfer', transferData);
};

/**
 * Get inventory transfer history
 * @param {object} filters Optional filters
 */
const getInventoryTransfers = (filters = {}) => {
  const queryParams = new URLSearchParams();
  Object.keys(filters).forEach(key => {
    if (filters[key] !== undefined && filters[key] !== null && filters[key] !== '') {
      queryParams.append(key, filters[key]);
    }
  });

  const queryString = queryParams.toString();
  const endpoint = queryString ? `/inventory/transfers?${queryString}` : '/inventory/transfers';

  return api.get(endpoint);
};

/**
 * Create warehouse-specific stock adjustment
 * @param {string} warehouseId Warehouse ID
 * @param {object} adjustmentData Adjustment details
 */
const createWarehouseStockAdjustment = (warehouseId, adjustmentData) => {
  return api.post(`/inventory/warehouse/${warehouseId}/adjustment`, adjustmentData);
};

/**
 * Get stock adjustment history for a warehouse
 * @param {string} warehouseId Warehouse ID
 * @param {object} filters Optional filters
 */
const getWarehouseStockAdjustments = (warehouseId, filters = {}) => {
  const queryParams = new URLSearchParams();
  Object.keys(filters).forEach(key => {
    if (filters[key] !== undefined && filters[key] !== null && filters[key] !== '') {
      queryParams.append(key, filters[key]);
    }
  });

  const queryString = queryParams.toString();
  const endpoint = queryString
    ? `/inventory/warehouse/${warehouseId}/adjustments?${queryString}`
    : `/inventory/warehouse/${warehouseId}/adjustments`;

  return api.get(endpoint);
};

/**
 * Creates a new inventory item.
 * @param {object} inventoryData The data for the new item.
 */
const createInventoryItem = (inventoryData) => {
  return api.post('/inventory', inventoryData);
};

/**
 * Updates an existing inventory item.
 * @param {string} inventoryId The ID of the item to update.
 * @param {object} inventoryData The updated data for the item.
 */
const updateInventoryItem = (inventoryId, inventoryData) => {
  return api.put(`/inventory/${inventoryId}`, inventoryData);
};

/**
 * Deletes an inventory item.
 * @param {string} inventoryId The ID of the item to delete.
 */
const deleteInventoryItem = (inventoryId) => {
  return api.delete(`/inventory/${inventoryId}`);
};

/**
 * Generate comprehensive inventory report
 * @param {object} reportParams Report parameters
 */
const getInventoryReport = (reportParams) => {
  const queryParams = new URLSearchParams();
  Object.keys(reportParams).forEach(key => {
    if (reportParams[key] !== undefined && reportParams[key] !== null && reportParams[key] !== '') {
      if (Array.isArray(reportParams[key])) {
        reportParams[key].forEach(value => queryParams.append(key, value));
      } else {
        queryParams.append(key, reportParams[key]);
      }
    }
  });

  return api.get(`/inventory/reports?${queryParams.toString()}`);
};

export const inventoryService = {
  getInventory,
  getWarehouseInventory,
  getOrganizationInventoryAggregation,
  getWarehouseInventoryAnalytics,
  transferInventory,
  getInventoryTransfers,
  createWarehouseStockAdjustment,
  getWarehouseStockAdjustments,
  createInventoryItem,
  updateInventoryItem,
  deleteInventoryItem,
  getInventoryReport,
};