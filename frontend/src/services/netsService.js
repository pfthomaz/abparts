// frontend/src/services/netsService.js

import { api } from './api';
import {
  cacheData,
  getCachedData,
  getCachedItem,
  isCacheStale,
} from '../db/indexedDB';
import { isOnline } from '../hooks/useNetworkStatus';

const CACHE_MAX_AGE = 24 * 60 * 60 * 1000; // 24 hours

/**
 * Fetches all nets for the current user's organization.
 * Uses cache when offline or when cache is fresh.
 * @param {string} farmSiteId Optional farm site ID to filter by.
 * @param {boolean} activeOnly Only return active nets.
 * @param {number} skip Number of records to skip.
 * @param {number} limit Maximum number of records to return.
 * @param {boolean} forceRefresh Force refresh from API even if cache is fresh.
 */
const getNets = async (farmSiteId = null, activeOnly = true, skip = 0, limit = 100, forceRefresh = false, userContext = null) => {
  try {
    // Check if online
    const online = isOnline();
    
    // Check cache staleness
    const cacheIsStale = await isCacheStale('nets', CACHE_MAX_AGE);
    
    // Use cache if offline OR if cache is fresh and not forcing refresh
    if (!online || (!cacheIsStale && !forceRefresh)) {
      // console.log('[NetsService] Using cached data');
      const cachedNets = await getCachedData('nets', userContext);
      
      // Filter by farm site if specified
      let filtered = farmSiteId
        ? cachedNets.filter(net => net.farm_site_id === farmSiteId)
        : cachedNets;
      
      // Filter by active status if needed
      filtered = activeOnly 
        ? filtered.filter(net => net.active !== false)
        : filtered;
      
      // Apply pagination
      const paginated = filtered.slice(skip, skip + limit);
      
      return paginated;
    }
    
    // Fetch from API
    // console.log('[NetsService] Fetching from API');
    let url = `/nets/?active_only=${activeOnly}&skip=${skip}&limit=${limit}`;
    if (farmSiteId) {
      url += `&farm_site_id=${farmSiteId}`;
    }
    const response = await api.get(url);
    
    // Cache the results with user context
    if (response && Array.isArray(response)) {
      await cacheData('nets', response, userContext);
      // console.log(`[NetsService] Cached ${response.length} nets`);
    }
    
    return response;
    
  } catch (error) {
    console.error('[NetsService] Error fetching nets:', error);
    
    // If API fails, try to return cached data as fallback
    if (!isOnline()) {
      // console.log('[NetsService] API failed, using cached data as fallback');
      const cachedNets = await getCachedData('nets', userContext);
      let filtered = farmSiteId
        ? cachedNets.filter(net => net.farm_site_id === farmSiteId)
        : cachedNets;
      filtered = activeOnly 
        ? filtered.filter(net => net.active !== false)
        : filtered;
      return filtered.slice(skip, skip + limit);
    }
    
    throw error;
  }
};

/**
 * Searches nets by name or cage number.
 * Searches in cache when offline.
 * @param {string} searchTerm The search query.
 * @param {number} skip Number of records to skip.
 * @param {number} limit Maximum number of records to return.
 */
const searchNets = async (searchTerm, skip = 0, limit = 100, userContext = null) => {
  try {
    const online = isOnline();
    
    if (!online) {
      // Search in cache when offline
      // console.log('[NetsService] Searching in cache (offline)');
      const cachedNets = await getCachedData('nets', userContext);
      
      const searchLower = searchTerm.toLowerCase();
      const filtered = cachedNets.filter(net => 
        net.name?.toLowerCase().includes(searchLower) ||
        net.cage_number?.toLowerCase().includes(searchLower) ||
        net.net_number?.toLowerCase().includes(searchLower)
      );
      
      return filtered.slice(skip, skip + limit);
    }
    
    // Search via API when online
    const response = await api.get(`/nets/search?q=${encodeURIComponent(searchTerm)}&skip=${skip}&limit=${limit}`);
    
    return response;
    
  } catch (error) {
    console.error('[NetsService] Error searching nets:', error);
    
    // Fallback to cache search if API fails
    // console.log('[NetsService] API search failed, searching in cache');
    const cachedNets = await getCachedData('nets', userContext);
    const searchLower = searchTerm.toLowerCase();
    const filtered = cachedNets.filter(net => 
      net.name?.toLowerCase().includes(searchLower) ||
      net.cage_number?.toLowerCase().includes(searchLower) ||
      net.net_number?.toLowerCase().includes(searchLower)
    );
    
    return filtered.slice(skip, skip + limit);
  }
};

/**
 * Fetches a single net by ID with its cleaning history.
 * Uses cache when offline.
 * @param {string} netId The ID of the net to fetch.
 * @param {object} userContext Optional user context for cache operations.
 */
const getNet = async (netId, userContext = null) => {
  try {
    const online = isOnline();
    
    if (!online) {
      // Get from cache when offline
      // console.log('[NetsService] Getting from cache (offline)');
      const cachedNet = await getCachedItem('nets', netId, userContext);
      
      if (!cachedNet) {
        throw new Error('Net not found in cache');
      }
      
      return cachedNet;
    }
    
    // Fetch from API when online
    const response = await api.get(`/nets/${netId}`);
    
    // Update cache with this single item
    if (response) {
      await cacheData('nets', response);
    }
    
    return response;
    
  } catch (error) {
    console.error('[NetsService] Error fetching net:', error);
    
    // Fallback to cache if API fails
    if (!isOnline()) {
      const cachedNet = await getCachedItem('nets', netId, userContext);
      if (cachedNet) {
        return cachedNet;
      }
    }
    
    throw error;
  }
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
 * Uses cache when offline.
 * @param {string} farmSiteId The ID of the farm site.
 * @param {boolean} activeOnly Only return active nets.
 */
const getNetsByFarmSite = async (farmSiteId, activeOnly = true) => {
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
