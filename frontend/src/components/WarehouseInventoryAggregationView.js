// frontend/src/components/WarehouseInventoryAggregationView.js

import React, { useState, useEffect } from 'react';
import { inventoryService } from '../services/inventoryService';
import { warehouseService } from '../services/warehouseService';
import { partsService } from '../services/partsService';
import { useAuth } from '../AuthContext';
import { useTranslation } from '../hooks/useTranslation';

const WarehouseInventoryAggregationView = ({ organizationId }) => {
  const { user } = useAuth();
  const { t } = useTranslation();
  const [aggregatedInventory, setAggregatedInventory] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [parts, setParts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [retryCount, setRetryCount] = useState(0);
  const [lastErrorDetails, setLastErrorDetails] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all'); // 'all', 'low_stock', 'out_of_stock'
  const [selectedPart, setSelectedPart] = useState(null);

  useEffect(() => {
    if (organizationId) {
      fetchData();
    }
  }, [organizationId]);

  // Auto-refresh every 10 minutes (reduced frequency to avoid API overload)
  useEffect(() => {
    if (!organizationId) return;

    const interval = setInterval(() => {
      fetchData();
    }, 10 * 60 * 1000);

    return () => clearInterval(interval);
  }, [organizationId]);

  /**
   * Validates and extracts inventory data from API response
   * @param {*} data - API response data
   * @returns {Array} - Validated inventory array
   */
  const validateInventoryData = (data) => {
    if (!data) return [];
    if (Array.isArray(data)) return data;
    if (data.inventory_summary && Array.isArray(data.inventory_summary)) {
      return data.inventory_summary;
    }
    return [];
  };

  /**
   * Enhanced error logging with context and user-friendly messages
   * @param {Error} error - The error object
   * @param {string} context - Context where the error occurred
   * @param {Object} additionalData - Additional data for debugging
   * @returns {string} - User-friendly error message
   */
  const logErrorWithContext = (error, context, additionalData = {}) => {
    const errorDetails = {
      timestamp: new Date().toISOString(),
      context,
      error: {
        message: error?.message || 'Unknown error',
        stack: error?.stack,
        name: error?.name
      },
      user: user?.id || 'anonymous',
      organizationId,
      retryCount,
      additionalData
    };

    // Log detailed error for debugging
    console.error(`[InventoryAggregation] Error in ${context}:`, errorDetails);

    // Store error details for potential retry or support
    setLastErrorDetails(errorDetails);

    // Return user-friendly message based on context
    switch (context) {
      case 'data_fetch':
        return 'Unable to load inventory data. This might be due to a network issue or server problem.';
      case 'data_processing':
        return 'There was an issue processing the inventory data. The data format may be unexpected.';
      case 'user_interaction':
        return 'An error occurred while processing your request. Please try again.';
      case 'component_render':
        return 'There was a display issue with the inventory view. Please refresh the page.';
      default:
        return 'An unexpected error occurred. Please try refreshing the page or contact support if the issue persists.';
    }
  };

  /**
   * Safe wrapper for array operations to prevent runtime errors
   * @param {*} array - Potential array to operate on
   * @param {Function} operation - Operation to perform on array
   * @param {*} fallback - Fallback value if operation fails
   * @returns {*} - Result of operation or fallback
   */
  const safeArrayOperation = (array, operation, fallback = []) => {
    if (!Array.isArray(array)) {
      if (array !== null && array !== undefined) {
        logErrorWithContext(
          new Error(`Expected array but received ${typeof array}`),
          'data_processing',
          { receivedType: typeof array, receivedValue: array }
        );
      }
      return fallback;
    }
    try {
      return operation(array);
    } catch (error) {
      logErrorWithContext(error, 'data_processing', { arrayLength: array?.length });
      return fallback;
    }
  };

  /**
   * Safe wrapper for object property access to prevent runtime errors
   * @param {*} obj - Object to access property from
   * @param {string} property - Property name to access
   * @param {*} fallback - Fallback value if property doesn't exist
   * @returns {*} - Property value or fallback
   */
  const safePropertyAccess = (obj, property, fallback = null) => {
    try {
      if (!obj || typeof obj !== 'object') return fallback;
      return obj.hasOwnProperty(property) ? obj[property] : fallback;
    } catch (error) {
      logErrorWithContext(error, 'data_processing', {
        objectType: typeof obj,
        property,
        hasProperty: obj?.hasOwnProperty?.(property)
      });
      return fallback;
    }
  };

  /**
   * Safe number parsing with fallback
   * @param {*} value - Value to parse as number
   * @param {number} fallback - Fallback value if parsing fails
   * @returns {number} - Parsed number or fallback
   */
  const safeParseFloat = (value, fallback = 0) => {
    try {
      if (value === null || value === undefined || value === '') return fallback;
      const parsed = parseFloat(value);
      if (isNaN(parsed)) {
        logErrorWithContext(
          new Error(`Failed to parse number from value: ${value}`),
          'data_processing',
          { originalValue: value, valueType: typeof value }
        );
        return fallback;
      }
      return parsed;
    } catch (error) {
      logErrorWithContext(error, 'data_processing', { value, valueType: typeof value });
      return fallback;
    }
  };

  /**
   * Safe string operations wrapper
   * @param {*} str - String to operate on
   * @param {Function} operation - Operation to perform
   * @param {*} fallback - Fallback value if operation fails
   * @returns {*} - Result of operation or fallback
   */
  const safeStringOperation = (str, operation, fallback = '') => {
    try {
      if (typeof str !== 'string') {
        if (str !== null && str !== undefined) {
          logErrorWithContext(
            new Error(`Expected string but received ${typeof str}`),
            'data_processing',
            { receivedType: typeof str, receivedValue: str }
          );
        }
        return fallback;
      }
      return operation(str);
    } catch (error) {
      logErrorWithContext(error, 'data_processing', { stringValue: str });
      return fallback;
    }
  };

  const fetchData = async (isRetry = false) => {
    // Prevent operations on undefined data during loading
    if (loading && !isRetry) {
      console.warn('Fetch already in progress, skipping duplicate request');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Validate organization ID before making requests
      if (!organizationId) {
        throw new Error('Organization ID is required to fetch inventory data');
      }

      const startTime = Date.now();

      const [aggregatedData, warehousesData, partsResponse] = await Promise.all([
        inventoryService.getOrganizationInventoryAggregation(organizationId),
        warehouseService.getOrganizationWarehouses(organizationId),
        partsService.getParts()
      ]);

      const fetchDuration = Date.now() - startTime;

      // Validate API responses
      if (!aggregatedData && !warehousesData && !partsResponse) {
        throw new Error('All API endpoints returned empty responses');
      }

      // Extract and validate inventory data from API response
      const validatedInventory = validateInventoryData(aggregatedData);
      setAggregatedInventory(validatedInventory);

      // Validate and set warehouses data
      const validatedWarehouses = Array.isArray(warehousesData) ? warehousesData : [];
      if (!Array.isArray(warehousesData)) {
        logErrorWithContext(
          new Error('Warehouses data is not an array'),
          'data_processing',
          { receivedType: typeof warehousesData, dataLength: warehousesData?.length }
        );
      }
      setWarehouses(validatedWarehouses);

      // Extract parts data from response (could be array or object with parts property)
      let partsData = partsResponse;
      if (partsResponse && typeof partsResponse === 'object' && !Array.isArray(partsResponse)) {
        // If response is an object, try to extract parts array
        partsData = partsResponse.parts || partsResponse.data || partsResponse.items || [];
      }

      // Validate parts data
      const validatedParts = Array.isArray(partsData) ? partsData : [];
      
      if (!Array.isArray(partsData)) {
        logErrorWithContext(
          new Error('Parts data is not an array after extraction'),
          'data_processing',
          { receivedType: typeof partsData, responseType: typeof partsResponse }
        );
      }
      setParts(validatedParts);

      // Store metadata if available
      if (aggregatedData && typeof aggregatedData === 'object' && !Array.isArray(aggregatedData)) {
        // Metadata is available for debugging if needed
      }

      // Reset retry count on successful fetch
      setRetryCount(0);
      setLastErrorDetails(null);

    } catch (err) {
      const userFriendlyMessage = logErrorWithContext(err, 'data_fetch', {
        organizationId,
        isRetry,
        retryCount
      });

      // Set user-friendly error message with actionable guidance
      let errorMessage = userFriendlyMessage;

      if (err.message?.includes('Organization ID')) {
        errorMessage = 'Invalid organization selected. Please refresh the page and try again.';
      } else if (err.message?.includes('Network Error') || err.message?.includes('fetch')) {
        errorMessage = 'Network connection issue. Please check your internet connection and try again.';
      } else if (err.message?.includes('401') || err.message?.includes('Unauthorized')) {
        errorMessage = 'Your session has expired. Please log in again to continue.';
      } else if (err.message?.includes('403') || err.message?.includes('Forbidden')) {
        errorMessage = 'You do not have permission to view this inventory data. Please contact your administrator.';
      } else if (err.message?.includes('404')) {
        errorMessage = 'The requested inventory data was not found. The organization may not exist or may not have any inventory.';
      } else if (err.message?.includes('500')) {
        errorMessage = 'Server error occurred while loading inventory data. Please try again in a few moments.';
      }

      setError(errorMessage);

      // Set fallback empty arrays to prevent filter errors
      setAggregatedInventory([]);
      setWarehouses([]);
      setParts([]);

      // Increment retry count for potential automatic retry
      setRetryCount(prev => prev + 1);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Retry data fetch with exponential backoff
   */
  const retryFetch = async () => {
    if (retryCount >= 3) {
      setError('Maximum retry attempts reached. Please refresh the page or contact support if the issue persists.');
      return;
    }

    // Exponential backoff: 1s, 2s, 4s
    const delay = Math.pow(2, retryCount) * 1000;

    setError(`Retrying in ${delay / 1000} seconds... (Attempt ${retryCount + 1} of 3)`);

    setTimeout(() => {
      fetchData(true);
    }, delay);
  };

  const getPartDetails = (partId) => {
    try {
      if (!partId) return {};

      // Prevent operations during loading state
      if (loading) {
        return {};
      }

      return safeArrayOperation(
        parts,
        (partsArray) => partsArray.find(p => p && p.id === partId) || {},
        {}
      );
    } catch (error) {
      logErrorWithContext(error, 'data_processing', { partId, partsLength: parts?.length });
      return {};
    }
  };

  const getWarehouseName = (warehouseId) => {
    try {
      if (!warehouseId) return 'Unknown Warehouse';

      // Prevent operations during loading state
      if (loading) {
        return 'Loading...';
      }

      const warehouse = safeArrayOperation(
        warehouses,
        (warehousesArray) => warehousesArray.find(w => w && w.id === warehouseId),
        null
      );
      return safePropertyAccess(warehouse, 'name', 'Unknown Warehouse');
    } catch (error) {
      logErrorWithContext(error, 'data_processing', { warehouseId, warehousesLength: warehouses?.length });
      return 'Unknown Warehouse';
    }
  };

  const filteredInventory = safeArrayOperation(
    aggregatedInventory,
    (inventory) => {
      // Prevent filtering operations during loading to avoid undefined data operations
      if (loading) {
        return [];
      }

      return inventory.filter(item => {
        try {
          if (!item) return false;

          const part = getPartDetails(safePropertyAccess(item, 'part_id'));
          const partName = safePropertyAccess(part, 'name', '');
          const partNumber = safePropertyAccess(part, 'part_number', '');

          const matchesSearch = !searchTerm ||
            safeStringOperation(partName, (name) => name.toLowerCase().includes(searchTerm.toLowerCase()), false) ||
            safeStringOperation(partNumber, (number) => number.toLowerCase().includes(searchTerm.toLowerCase()), false);

          const totalStock = safeParseFloat(safePropertyAccess(item, 'total_stock'), 0);
          const minStock = safeParseFloat(safePropertyAccess(item, 'min_stock_recommendation'), 0);

          const matchesFilter = filterType === 'all' ||
            (filterType === 'low_stock' && totalStock <= minStock && totalStock > 0) ||
            (filterType === 'out_of_stock' && totalStock === 0);

          return matchesSearch && matchesFilter;
        } catch (error) {
          logErrorWithContext(error, 'data_processing', {
            action: 'filter_inventory_item',
            itemId: item?.part_id,
            searchTerm,
            filterType
          });
          return false;
        }
      });
    },
    []
  );

  const getStockStatus = (totalStock, minStock) => {
    try {
      const total = safeParseFloat(totalStock, 0);
      const minimum = safeParseFloat(minStock, 0);

      if (total === 0) {
        return { status: 'out_of_stock', color: 'text-red-600', bg: 'bg-red-100' };
      } else if (total <= minimum) {
        return { status: 'low_stock', color: 'text-orange-600', bg: 'bg-orange-100' };
      } else {
        return { status: 'in_stock', color: 'text-green-600', bg: 'bg-green-100' };
      }
    } catch (error) {
      console.error('Failed to determine stock status:', error);
      return { status: 'unknown', color: 'text-gray-600', bg: 'bg-gray-100' };
    }
  };

  const getStockStatusLabel = (status) => {
    try {
      switch (status) {
        case 'out_of_stock': return 'Out of Stock';
        case 'low_stock': return 'Low Stock';
        case 'in_stock': return 'In Stock';
        case 'unknown': return 'Status Unknown';
        default: return 'Unknown';
      }
    } catch (error) {
      console.error('Failed to get stock status label:', error);
      return 'Unknown';
    }
  };

  const showPartDetails = (item) => {
    try {
      if (!item) {
        const errorMsg = logErrorWithContext(
          new Error('Cannot show details for null/undefined item'),
          'user_interaction',
          { item }
        );
        setError(errorMsg);
        return;
      }

      // Prevent operations during loading state
      if (loading) {
        setError('Please wait for data to finish loading before viewing details.');
        return;
      }

      setSelectedPart(item);
    } catch (error) {
      const errorMsg = logErrorWithContext(error, 'user_interaction', { item });
      setError(errorMsg);
    }
  };

  const closePartDetails = () => {
    try {
      setSelectedPart(null);
      // Clear any error that might have been set when opening details
      if (error && error.includes('details')) {
        setError('');
      }
    } catch (error) {
      logErrorWithContext(error, 'user_interaction');
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        {/* Loading Header */}
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-medium text-gray-900">
            {t('warehouses.aggregatedTitle')}
          </h3>
          <div className="text-sm text-gray-500">
            {t('common.loading')}
          </div>
        </div>

        {/* Loading State */}
        <div className="flex items-center justify-center p-12">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-4"></div>
            <div className="text-gray-500 text-lg">{t('warehouses.loadingAggregated')}</div>
            <div className="text-gray-400 text-sm mt-2">
              {retryCount > 0 ? `${t('warehouses.retryAttempt')} ${retryCount}` : t('warehouses.fetchingData')}
            </div>
          </div>
        </div>

        {/* Loading Skeleton */}
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 h-10 bg-gray-200 rounded animate-pulse"></div>
            <div className="w-32 h-10 bg-gray-200 rounded animate-pulse"></div>
          </div>

          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <div className="bg-gray-50 px-6 py-3">
              <div className="flex space-x-4">
                {[1, 2, 3, 4, 5, 6].map(i => (
                  <div key={i} className="h-4 bg-gray-300 rounded flex-1 animate-pulse"></div>
                ))}
              </div>
            </div>
            {[1, 2, 3, 4, 5].map(i => (
              <div key={i} className="border-t border-gray-200 px-6 py-4">
                <div className="flex space-x-4">
                  {[1, 2, 3, 4, 5, 6].map(j => (
                    <div key={j} className="h-4 bg-gray-200 rounded flex-1 animate-pulse"></div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error && !loading) {
    return (
      <div className="space-y-4">
        {/* Error Header */}
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-medium text-gray-900">
            {t('warehouses.aggregatedTitle')}
          </h3>
          <div className="text-sm text-red-500">
            {t('common.error')}
          </div>
        </div>

        {/* Enhanced Error Display */}
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3 flex-1">
              <h3 className="text-sm font-medium text-red-800">
                {t('warehouses.unableToLoad')}
              </h3>
              <div className="mt-2 text-sm text-red-700">
                {error}
              </div>

              {/* Action Buttons */}
              <div className="mt-4 flex space-x-3">
                <button
                  onClick={() => fetchData(true)}
                  disabled={loading}
                  className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? t('common.loading') : t('warehouses.tryAgain')}
                </button>

                {retryCount < 3 && (
                  <button
                    onClick={retryFetch}
                    disabled={loading}
                    className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {t('warehouses.autoRetry')} ({3 - retryCount} {t('warehouses.attemptsLeft')})
                  </button>
                )}

                <button
                  onClick={() => window.location.reload()}
                  className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  {t('warehouses.refreshPage')}
                </button>
              </div>

              {/* Technical Details (for debugging) */}
              {lastErrorDetails && process.env.NODE_ENV === 'development' && (
                <details className="mt-4">
                  <summary className="text-xs text-red-600 cursor-pointer hover:text-red-800">
                    Technical Details (Development Only)
                  </summary>
                  <pre className="mt-2 text-xs text-red-600 bg-red-100 p-2 rounded overflow-auto max-h-32">
                    {JSON.stringify(lastErrorDetails, null, 2)}
                  </pre>
                </details>
              )}
            </div>
          </div>
        </div>

        {/* Fallback Content */}
        <div className="bg-gray-50 p-8 rounded-lg text-center">
          <div className="text-gray-500">
            <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2M4 13h2m13-8l-4 4m0 0l-4-4m4 4V3" />
            </svg>
            <p className="text-lg font-medium text-gray-900 mb-2">{t('warehouses.inventoryUnavailable')}</p>
            <p className="text-gray-600">
              {t('warehouses.troubleLoading')}
            </p>
          </div>
        </div>
      </div>
    );
  }

  try {
    return (
      <div className="space-y-4">
        {/* Header */}
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-medium text-gray-900">
            {t('warehouses.aggregatedTitle')}
          </h3>
          <div className="text-sm text-gray-500">
            {filteredInventory.length} {t('warehouses.parts')}
          </div>
        </div>

        {/* Non-critical Error Display */}
        {error && loading && (
          <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 px-4 py-2 rounded text-sm">
            {error}
          </div>
        )}

        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder={t('warehouses.searchParts')}
              value={searchTerm}
              onChange={(e) => {
                try {
                  if (loading) {
                    return; // Prevent operations during loading
                  }
                  const value = safePropertyAccess(e, 'target.value', '');
                  setSearchTerm(value);
                } catch (error) {
                  logErrorWithContext(error, 'user_interaction', { action: 'search_term_update' });
                }
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <select
              value={filterType}
              onChange={(e) => {
                try {
                  if (loading) {
                    return; // Prevent operations during loading
                  }
                  const value = safePropertyAccess(e, 'target.value', 'all');
                  setFilterType(value);
                } catch (error) {
                  logErrorWithContext(error, 'user_interaction', { action: 'filter_type_update' });
                }
              }}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">{t('warehouses.allItems')}</option>
              <option value="low_stock">{t('warehouses.lowStock')}</option>
              <option value="out_of_stock">{t('warehouses.outOfStock')}</option>
            </select>
          </div>
        </div>

        {/* Inventory Table */}
        {filteredInventory.length === 0 ? (
          <div className="bg-gray-50 p-8 rounded-lg text-center">
            <div className="text-gray-500">
              {searchTerm || filterType !== 'all'
                ? t('warehouses.noItemsMatch')
                : t('warehouses.noItemsFound')}
            </div>
          </div>
        ) : (
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {t('warehouses.part')}
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {t('warehouses.totalStockLabel')}
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {t('warehouses.minStock')}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {t('warehouses.statusLabel')}
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {t('warehouses.warehousesLabel')}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {t('warehouses.actions')}
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {safeArrayOperation(filteredInventory, (inventory) =>
                  inventory.map((item) => {
                    try {
                      if (!item) return null;

                      const partId = safePropertyAccess(item, 'part_id', 'unknown');
                      const stockStatus = getStockStatus(
                        safePropertyAccess(item, 'total_stock'),
                        safePropertyAccess(item, 'min_stock_recommendation')
                      );

                      const totalStock = safeParseFloat(safePropertyAccess(item, 'total_stock'), 0);
                      const minStock = safeParseFloat(safePropertyAccess(item, 'min_stock_recommendation'), 0);
                      const warehouseCount = safeParseFloat(safePropertyAccess(item, 'warehouse_count'), 0);
                      
                      // Use part info from aggregated inventory (already included in response)
                      const partName = safePropertyAccess(item, 'part_name', 'Unknown Part');
                      const partNumber = safePropertyAccess(item, 'part_number', 'N/A');

                      return (
                        <tr key={partId} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div>
                              <div className="text-sm font-medium text-gray-900">
                                {partName}
                              </div>
                              <div className="text-sm text-gray-500">
                                {partNumber}
                              </div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right">
                            <div className="text-sm font-medium text-gray-900">
                              {totalStock.toLocaleString()}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right">
                            <div className="text-sm text-gray-900">
                              {minStock.toLocaleString()}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${safePropertyAccess(stockStatus, 'bg', 'bg-gray-100')} ${safePropertyAccess(stockStatus, 'color', 'text-gray-600')}`}>
                              {getStockStatusLabel(safePropertyAccess(stockStatus, 'status', 'unknown'))}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right">
                            <div className="text-sm text-gray-900">
                              {warehouseCount} warehouse{warehouseCount !== 1 ? 's' : ''}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <button
                              onClick={() => showPartDetails(item)}
                              className="text-blue-600 hover:text-blue-900"
                            >
                              {t('warehouses.viewDetails')}
                            </button>
                          </td>
                        </tr>
                      );
                    } catch (error) {
                      console.error('Error rendering inventory row:', error);
                      return null;
                    }
                  }).filter(Boolean), // Remove null entries
                  []
                )}
              </tbody>
            </table>
          </div>
        )}

        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <div className="text-sm font-medium text-gray-500">{t('warehouses.totalParts')}</div>
            <div className="text-2xl font-bold text-gray-900">
              {safeArrayOperation(aggregatedInventory, (arr) => arr.length, 0)}
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <div className="text-sm font-medium text-gray-500">{t('warehouses.totalWarehouses')}</div>
            <div className="text-2xl font-bold text-blue-600">
              {safeArrayOperation(warehouses, (arr) => arr.length, 0)}
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <div className="text-sm font-medium text-gray-500">{t('warehouses.lowStockItems')}</div>
            <div className="text-2xl font-bold text-orange-600">
              {safeArrayOperation(
                aggregatedInventory,
                (arr) => arr.filter(item => {
                  try {
                    if (!item) return false;
                    const total = safeParseFloat(safePropertyAccess(item, 'total_stock'), 0);
                    const min = safeParseFloat(safePropertyAccess(item, 'min_stock_recommendation'), 0);
                    return total <= min && total > 0;
                  } catch (error) {
                    console.error('Error filtering low stock items:', error);
                    return false;
                  }
                }).length,
                0
              )}
            </div>
          </div>

          <div className="bg-white p-4 rounded-lg border border-gray-200">
            <div className="text-sm font-medium text-gray-500">{t('warehouses.outOfStockItems')}</div>
            <div className="text-2xl font-bold text-red-600">
              {safeArrayOperation(
                aggregatedInventory,
                (arr) => arr.filter(item => {
                  try {
                    if (!item) return false;
                    return safeParseFloat(safePropertyAccess(item, 'total_stock'), 0) === 0;
                  } catch (error) {
                    console.error('Error filtering out of stock items:', error);
                    return false;
                  }
                }).length,
                0
              )}
            </div>
          </div>
        </div>

        {/* Part Details Modal */}
        {selectedPart && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  {t('warehouses.partDetails')}: {safePropertyAccess(getPartDetails(safePropertyAccess(selectedPart, 'part_id')), 'name', 'Unknown Part')}
                </h3>
                <button
                  onClick={closePartDetails}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <span className="sr-only">{t('warehouses.close')}</span>
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-sm font-medium text-gray-500">{t('warehouses.partNumber')}:</span>
                    <p className="text-sm text-gray-900">
                      {safePropertyAccess(getPartDetails(safePropertyAccess(selectedPart, 'part_id')), 'part_number', 'N/A')}
                    </p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-gray-500">{t('warehouses.unitOfMeasure')}:</span>
                    <p className="text-sm text-gray-900">
                      {safePropertyAccess(getPartDetails(safePropertyAccess(selectedPart, 'part_id')), 'unit_of_measure', 'N/A')}
                    </p>
                  </div>
                </div>

                <div>
                  <h4 className="text-md font-medium text-gray-900 mb-2">{t('warehouses.warehouseBreakdown')}</h4>
                  <div className="bg-gray-50 rounded-lg p-4">
                    {safeArrayOperation(
                      safePropertyAccess(selectedPart, 'warehouse_details', []),
                      (details) => details.length > 0 ? (
                        <div className="space-y-2">
                          {details.map((detail, index) => {
                            try {
                              if (!detail) return null;
                              const warehouseId = safePropertyAccess(detail, 'warehouse_id');
                              const currentStock = safeParseFloat(safePropertyAccess(detail, 'current_stock'), 0);
                              const unitOfMeasure = safePropertyAccess(getPartDetails(safePropertyAccess(selectedPart, 'part_id')), 'unit_of_measure', '');

                              return (
                                <div key={index} className="flex justify-between items-center">
                                  <span className="text-sm text-gray-700">
                                    {getWarehouseName(warehouseId)}
                                  </span>
                                  <span className="text-sm font-medium text-gray-900">
                                    {currentStock.toLocaleString()} {unitOfMeasure}
                                  </span>
                                </div>
                              );
                            } catch (error) {
                              console.error('Error rendering warehouse detail:', error);
                              return null;
                            }
                          }).filter(Boolean)}
                        </div>
                      ) : (
                        <p className="text-sm text-gray-500">{t('warehouses.noWarehouseDetails')}</p>
                      ),
                      <p className="text-sm text-gray-500">{t('warehouses.noWarehouseDetails')}</p>
                    )}
                  </div>
                </div>
              </div>

              <div className="mt-6 flex justify-end">
                <button
                  onClick={closePartDetails}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200"
                >
                  {t('warehouses.close')}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  } catch (error) {
    console.error('Critical error in WarehouseInventoryAggregationView:', error);
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
        <div className="font-medium">Component Error</div>
        <div className="text-sm mt-1">
          An unexpected error occurred while rendering the inventory view. Please refresh the page and try again.
        </div>
      </div>
    );
  }
};

export default WarehouseInventoryAggregationView;