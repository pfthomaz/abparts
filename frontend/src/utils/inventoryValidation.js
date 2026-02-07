// frontend/src/utils/inventoryValidation.js

/**
 * @fileoverview Data validation utilities for inventory aggregation operations
 * Provides safe data extraction and array operation wrappers to prevent runtime errors
 */

/**
 * @typedef {Object} InventoryAggregationItem
 * @property {string} part_id - Unique identifier for the part
 * @property {string} part_number - Part number/SKU
 * @property {string} part_name - Human-readable part name
 * @property {string} unit_of_measure - Unit of measurement (e.g., 'pieces', 'liters')
 * @property {number} total_stock - Total stock quantity across all warehouses
 * @property {number} warehouse_count - Number of warehouses containing this part
 * @property {number} total_minimum_stock - Total minimum stock threshold
 * @property {boolean} is_low_stock - Whether the part is below minimum stock
 */

/**
 * @typedef {Object} InventoryAggregationResponse
 * @property {string} organization_id - Organization UUID
 * @property {InventoryAggregationItem[]} inventory_summary - Array of aggregated inventory items
 * @property {number} total_parts - Total number of different parts
 * @property {number} low_stock_parts - Number of parts below minimum stock
 */

/**
 * @typedef {Object} InventoryMetadata
 * @property {number} total_parts - Total number of different parts
 * @property {number} low_stock_parts - Number of parts below minimum stock
 * @property {string|null} organization_id - Organization UUID or null
 */

/**
 * Validates and extracts inventory data from API response
 * Handles various response formats and provides fallback values
 * 
 * @param {any} data - Raw API response data
 * @returns {InventoryAggregationItem[]} - Validated array of inventory items
 */
export const validateInventoryData = (data) => {
  // Handle null, undefined, or falsy values
  if (!data) {
    console.warn('validateInventoryData: Received null/undefined data, returning empty array');
    return [];
  }

  // If data is already an array, validate its contents
  if (Array.isArray(data)) {
    return data.filter(item => item && typeof item === 'object');
  }

  // Handle object response with inventory_summary property
  if (typeof data === 'object' && data.inventory_summary) {
    if (Array.isArray(data.inventory_summary)) {
      return data.inventory_summary.filter(item => item && typeof item === 'object');
    } else {
      console.warn('validateInventoryData: inventory_summary is not an array, returning empty array');
      return [];
    }
  }

  // Handle unexpected data types
  console.warn('validateInventoryData: Unexpected data format:', typeof data, data);
  return [];
};

/**
 * Extracts metadata from inventory aggregation API response
 * 
 * @param {any} data - Raw API response data
 * @returns {InventoryMetadata} - Extracted metadata with fallback values
 */
export const extractInventoryMetadata = (data) => {
  const defaultMetadata = {
    total_parts: 0,
    low_stock_parts: 0,
    organization_id: null
  };

  if (!data || typeof data !== 'object') {
    return defaultMetadata;
  }

  return {
    total_parts: typeof data.total_parts === 'number' && isFinite(data.total_parts) ? data.total_parts : 0,
    low_stock_parts: typeof data.low_stock_parts === 'number' && isFinite(data.low_stock_parts) ? data.low_stock_parts : 0,
    organization_id: typeof data.organization_id === 'string' ? data.organization_id : null
  };
};

/**
 * Validates that a value is a non-empty array
 * 
 * @param {any} value - Value to validate
 * @returns {boolean} - True if value is a non-empty array
 */
export const isValidArray = (value) => {
  return Array.isArray(value) && value.length > 0;
};

/**
 * Validates that a value is an array (can be empty)
 * 
 * @param {any} value - Value to validate
 * @returns {boolean} - True if value is an array
 */
export const isArray = (value) => {
  return Array.isArray(value);
};

/**
 * Safe wrapper for array filter operations
 * Prevents "filter is not a function" errors
 * 
 * @param {any} array - Array to filter (may not be an array)
 * @param {Function} filterFn - Filter function to apply
 * @param {any[]} fallback - Fallback value if operation fails
 * @returns {any[]} - Filtered array or fallback value
 */
export const safeFilter = (array, filterFn, fallback = []) => {
  if (!Array.isArray(array)) {
    console.warn('safeFilter: Attempted to filter non-array value:', typeof array);
    return fallback;
  }

  if (typeof filterFn !== 'function') {
    console.warn('safeFilter: Filter function is not a function:', typeof filterFn);
    return array;
  }

  try {
    return array.filter(filterFn);
  } catch (error) {
    console.error('safeFilter: Filter operation failed:', error);
    return fallback;
  }
};

/**
 * Safe wrapper for array map operations
 * 
 * @param {any} array - Array to map (may not be an array)
 * @param {Function} mapFn - Map function to apply
 * @param {any[]} fallback - Fallback value if operation fails
 * @returns {any[]} - Mapped array or fallback value
 */
export const safeMap = (array, mapFn, fallback = []) => {
  if (!Array.isArray(array)) {
    console.warn('safeMap: Attempted to map non-array value:', typeof array);
    return fallback;
  }

  if (typeof mapFn !== 'function') {
    console.warn('safeMap: Map function is not a function:', typeof mapFn);
    return array;
  }

  try {
    return array.map(mapFn);
  } catch (error) {
    console.error('safeMap: Map operation failed:', error);
    return fallback;
  }
};

/**
 * Safe wrapper for array reduce operations
 * 
 * @param {any} array - Array to reduce (may not be an array)
 * @param {Function} reduceFn - Reduce function to apply
 * @param {any} initialValue - Initial value for reduction
 * @param {any} fallback - Fallback value if operation fails
 * @returns {any} - Reduced value or fallback value
 */
export const safeReduce = (array, reduceFn, initialValue, fallback = null) => {
  if (!Array.isArray(array)) {
    console.warn('safeReduce: Attempted to reduce non-array value:', typeof array);
    return fallback !== null ? fallback : initialValue;
  }

  if (typeof reduceFn !== 'function') {
    console.warn('safeReduce: Reduce function is not a function:', typeof reduceFn);
    return fallback !== null ? fallback : initialValue;
  }

  try {
    return array.reduce(reduceFn, initialValue);
  } catch (error) {
    console.error('safeReduce: Reduce operation failed:', error);
    return fallback !== null ? fallback : initialValue;
  }
};

/**
 * Safe wrapper for array find operations
 * 
 * @param {any} array - Array to search (may not be an array)
 * @param {Function} findFn - Find function to apply
 * @param {any} fallback - Fallback value if operation fails
 * @returns {any} - Found item or fallback value
 */
export const safeFind = (array, findFn, fallback = null) => {
  if (!Array.isArray(array)) {
    console.warn('safeFind: Attempted to find in non-array value:', typeof array);
    return fallback;
  }

  if (typeof findFn !== 'function') {
    console.warn('safeFind: Find function is not a function:', typeof findFn);
    return fallback;
  }

  try {
    const result = array.find(findFn);
    return result !== undefined ? result : fallback;
  } catch (error) {
    console.error('safeFind: Find operation failed:', error);
    return fallback;
  }
};

/**
 * Safe wrapper for array sort operations
 * 
 * @param {any} array - Array to sort (may not be an array)
 * @param {Function} [compareFn] - Optional compare function
 * @param {any[]} fallback - Fallback value if operation fails
 * @returns {any[]} - Sorted array or fallback value
 */
export const safeSort = (array, compareFn, fallback = []) => {
  if (!Array.isArray(array)) {
    console.warn('safeSort: Attempted to sort non-array value:', typeof array);
    return fallback;
  }

  if (compareFn && typeof compareFn !== 'function') {
    console.warn('safeSort: Compare function is not a function:', typeof compareFn);
    return [...array]; // Return copy of original array
  }

  try {
    // Create a copy to avoid mutating the original array
    const arrayCopy = [...array];
    return compareFn ? arrayCopy.sort(compareFn) : arrayCopy.sort();
  } catch (error) {
    console.error('safeSort: Sort operation failed:', error);
    return fallback;
  }
};

/**
 * Validates an individual inventory item structure
 * 
 * @param {any} item - Item to validate
 * @returns {boolean} - True if item has required properties
 */
export const validateInventoryItem = (item) => {
  if (!item || typeof item !== 'object') {
    return false;
  }

  const requiredFields = ['part_id', 'part_number', 'part_name'];
  return requiredFields.every(field =>
    item.hasOwnProperty(field) &&
    typeof item[field] === 'string' &&
    item[field].length > 0
  );
};

/**
 * Sanitizes inventory data by removing invalid items
 * 
 * @param {any[]} items - Array of inventory items to sanitize
 * @returns {InventoryAggregationItem[]} - Array of valid inventory items
 */
export const sanitizeInventoryItems = (items) => {
  if (!Array.isArray(items)) {
    console.warn('sanitizeInventoryItems: Input is not an array');
    return [];
  }

  return items.filter(item => {
    const isValid = validateInventoryItem(item);
    if (!isValid) {
      console.warn('sanitizeInventoryItems: Removing invalid item:', item);
    }
    return isValid;
  });
};

/**
 * Creates a safe inventory aggregation result object
 * Combines data validation with metadata extraction
 * 
 * @param {any} apiResponse - Raw API response
 * @returns {Object} - Object with validated inventory data and metadata
 */
export const createSafeInventoryResult = (apiResponse) => {
  const inventoryData = validateInventoryData(apiResponse);
  const metadata = extractInventoryMetadata(apiResponse);
  const sanitizedData = sanitizeInventoryItems(inventoryData);

  return {
    inventory: sanitizedData,
    metadata,
    hasData: sanitizedData.length > 0,
    isValid: true
  };
};

/**
 * Logs inventory data validation results for debugging
 * 
 * @param {any} originalData - Original API response data
 * @param {any[]} validatedData - Validated inventory array
 * @param {string} context - Context where validation occurred
 */
export const logInventoryValidation = (originalData, validatedData, context = '') => {
  const timestamp = new Date().toISOString();

  console.group(`📊 Inventory Validation ${context ? `- ${context}` : ''} - ${timestamp}`);
  // console.log('Original data type:', typeof originalData);
  // console.log('Original data:', originalData);
  // console.log('Validated array length:', validatedData.length);
  // console.log('Validated data:', validatedData);

  if (originalData && typeof originalData === 'object' && !Array.isArray(originalData)) {
    // Check for inventory_summary structure
  }

  console.groupEnd();
};