// frontend/src/services/farmSitesService.js

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
 * Fetches all farm sites for the current user's organization.
 * Uses cache when offline or when cache is fresh.
 * @param {boolean} activeOnly Only return active farm sites.
 * @param {number} skip Number of records to skip.
 * @param {number} limit Maximum number of records to return.
 * @param {boolean} forceRefresh Force refresh from API even if cache is fresh.
 */
const getFarmSites = async (activeOnly = true, skip = 0, limit = 100, forceRefresh = false, userContext = null) => {
  try {
    // Check if online
    const online = isOnline();
    
    // Check cache staleness
    const cacheIsStale = await isCacheStale('farmSites', CACHE_MAX_AGE);
    
    // Use cache if offline OR if cache is fresh and not forcing refresh
    if (!online || (!cacheIsStale && !forceRefresh)) {
      console.log('[FarmSitesService] Using cached data, userContext:', userContext);
      const cachedSites = await getCachedData('farmSites', userContext);
      console.log('[FarmSitesService] Retrieved from cache:', cachedSites.length, 'farm sites');
      
      // Filter by active status if needed
      const filtered = activeOnly 
        ? cachedSites.filter(site => site.active !== false)
        : cachedSites;
      console.log('[FarmSitesService] After active filter:', filtered.length, 'farm sites');
      
      // Apply pagination
      const paginated = filtered.slice(skip, skip + limit);
      console.log('[FarmSitesService] After pagination:', paginated.length, 'farm sites');
      
      return paginated;
    }
    
    // Fetch from API
    // console.log('[FarmSitesService] Fetching from API');
    const response = await api.get(`/farm-sites/?active_only=${activeOnly}&skip=${skip}&limit=${limit}`);
    
    // Cache the results with user context
    if (response && Array.isArray(response)) {
      await cacheData('farmSites', response, userContext);
      // console.log(`[FarmSitesService] Cached ${response.length} farm sites`);
    }
    
    return response;
    
  } catch (error) {
    console.error('[FarmSitesService] Error fetching farm sites:', error);
    
    // If API fails, try to return cached data as fallback
    if (!isOnline()) {
      // console.log('[FarmSitesService] API failed, using cached data as fallback');
      const cachedSites = await getCachedData('farmSites', userContext);
      const filtered = activeOnly 
        ? cachedSites.filter(site => site.active !== false)
        : cachedSites;
      return filtered.slice(skip, skip + limit);
    }
    
    throw error;
  }
};

/**
 * Searches farm sites by name or location.
 * Searches in cache when offline.
 * @param {string} searchTerm The search query.
 * @param {number} skip Number of records to skip.
 * @param {number} limit Maximum number of records to return.
 */
const searchFarmSites = async (searchTerm, skip = 0, limit = 100, userContext = null) => {
  try {
    const online = isOnline();
    
    if (!online) {
      // Search in cache when offline
      // console.log('[FarmSitesService] Searching in cache (offline)');
      const cachedSites = await getCachedData('farmSites', userContext);
      
      const searchLower = searchTerm.toLowerCase();
      const filtered = cachedSites.filter(site => 
        site.name?.toLowerCase().includes(searchLower) ||
        site.location?.toLowerCase().includes(searchLower)
      );
      
      return filtered.slice(skip, skip + limit);
    }
    
    // Search via API when online
    const response = await api.get(`/farm-sites/search?q=${encodeURIComponent(searchTerm)}&skip=${skip}&limit=${limit}`);
    
    return response;
    
  } catch (error) {
    console.error('[FarmSitesService] Error searching farm sites:', error);
    
    // Fallback to cache search if API fails
    // console.log('[FarmSitesService] API search failed, searching in cache');
    const cachedSites = await getCachedData('farmSites', userContext);
    const searchLower = searchTerm.toLowerCase();
    const filtered = cachedSites.filter(site => 
      site.name?.toLowerCase().includes(searchLower) ||
      site.location?.toLowerCase().includes(searchLower)
    );
    
    return filtered.slice(skip, skip + limit);
  }
};

/**
 * Fetches a single farm site by ID with its nets.
 * Uses cache when offline.
 * @param {string} farmSiteId The ID of the farm site to fetch.
 * @param {object} userContext Optional user context for cache operations.
 */
const getFarmSite = async (farmSiteId, userContext = null) => {
  try {
    const online = isOnline();
    
    if (!online) {
      // Get from cache when offline
      // console.log('[FarmSitesService] Getting from cache (offline)');
      const cachedSite = await getCachedItem('farmSites', farmSiteId, userContext);
      
      if (!cachedSite) {
        throw new Error('Farm site not found in cache');
      }
      
      return cachedSite;
    }
    
    // Fetch from API when online
    const response = await api.get(`/farm-sites/${farmSiteId}`);
    
    // Update cache with this single item
    if (response) {
      await cacheData('farmSites', response);
    }
    
    return response;
    
  } catch (error) {
    console.error('[FarmSitesService] Error fetching farm site:', error);
    
    // Fallback to cache if API fails
    if (!isOnline()) {
      const cachedSite = await getCachedItem('farmSites', farmSiteId, userContext);
      if (cachedSite) {
        return cachedSite;
      }
    }
    
    throw error;
  }
};

/**
 * Creates a new farm site.
 * @param {object} farmSiteData The data for the new farm site.
 */
const createFarmSite = (farmSiteData) => {
  return api.post('/farm-sites/', farmSiteData);
};

/**
 * Updates an existing farm site.
 * @param {string} farmSiteId The ID of the farm site to update.
 * @param {object} farmSiteData The updated data for the farm site.
 */
const updateFarmSite = (farmSiteId, farmSiteData) => {
  return api.put(`/farm-sites/${farmSiteId}`, farmSiteData);
};

/**
 * Deletes a farm site (soft delete - sets active=false).
 * @param {string} farmSiteId The ID of the farm site to delete.
 */
const deleteFarmSite = (farmSiteId) => {
  return api.delete(`/farm-sites/${farmSiteId}`);
};

const farmSitesService = {
  getFarmSites,
  searchFarmSites,
  getFarmSite,
  createFarmSite,
  updateFarmSite,
  deleteFarmSite,
};

export default farmSitesService;
