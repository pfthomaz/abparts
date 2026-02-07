// Offline Data Preloader Service
// Preloads all essential data into IndexedDB on login for offline access

import { machinesService } from './machinesService';
import { getLocalizedProtocols } from './maintenanceProtocolsService';
import { userService } from './userService';
import farmSitesService from './farmSitesService';
import netsService from './netsService';
import { cacheData, STORES } from '../db/indexedDB';

/**
 * Preload all essential data for offline use
 * Called after successful login
 * 
 * @param {object} user - Current user object
 * @returns {Promise<object>} - Preload results
 */
export async function preloadOfflineData(user) {
  console.log('[OfflinePreloader] Starting data preload for offline mode...');
  
  const userContext = {
    userId: user.id,
    organizationId: user.organization_id,
    isSuperAdmin: user.role === 'super_admin'
  };
  
  const results = {
    machines: { success: false, count: 0, error: null },
    protocols: { success: false, count: 0, error: null },
    users: { success: false, count: 0, error: null },
    farmSites: { success: false, count: 0, error: null },
    nets: { success: false, count: 0, error: null },
  };
  
  const startTime = Date.now();
  
  // Preload machines
  try {
    const machines = await machinesService.getMachines(true, userContext); // Force refresh
    results.machines = { success: true, count: machines.length, error: null };
    console.log(`[OfflinePreloader] ✓ Cached ${machines.length} machines`);
  } catch (error) {
    results.machines.error = error.message;
    console.error('[OfflinePreloader] ✗ Failed to cache machines:', error);
  }
  
  // Preload maintenance protocols
  try {
    const protocols = await getLocalizedProtocols({}, user.preferred_language);
    // Cache protocols with user context
    await cacheData(STORES.MAINTENANCE_PROTOCOLS, protocols, userContext);
    results.protocols = { success: true, count: protocols.length, error: null };
    console.log(`[OfflinePreloader] ✓ Cached ${protocols.length} protocols`);
  } catch (error) {
    results.protocols.error = error.message;
    console.error('[OfflinePreloader] ✗ Failed to cache protocols:', error);
  }
  
  // Preload users (for dropdowns)
  try {
    const usersResponse = await userService.getUsers();
    const users = usersResponse.data || usersResponse;
    // Cache users with user context
    await cacheData(STORES.USERS, users, userContext);
    results.users = { success: true, count: users.length, error: null };
    console.log(`[OfflinePreloader] ✓ Cached ${users.length} users`);
  } catch (error) {
    results.users.error = error.message;
    console.error('[OfflinePreloader] ✗ Failed to cache users:', error);
  }
  
  // Preload farm sites (for net cleaning)
  try {
    const farmSitesResponse = await farmSitesService.getFarmSites();
    const farmSites = farmSitesResponse.data || farmSitesResponse;
    // Cache farm sites with user context
    await cacheData(STORES.FARM_SITES, farmSites, userContext);
    results.farmSites = { success: true, count: farmSites.length, error: null };
    console.log(`[OfflinePreloader] ✓ Cached ${farmSites.length} farm sites`);
  } catch (error) {
    results.farmSites.error = error.message;
    console.error('[OfflinePreloader] ✗ Failed to cache farm sites:', error);
  }
  
  // Preload nets (for net cleaning)
  try {
    const netsResponse = await netsService.getNets();
    const nets = netsResponse.data || netsResponse;
    // Cache nets with user context
    await cacheData(STORES.NETS, nets, userContext);
    results.nets = { success: true, count: nets.length, error: null };
    console.log(`[OfflinePreloader] ✓ Cached ${nets.length} nets`);
  } catch (error) {
    results.nets.error = error.message;
    console.error('[OfflinePreloader] ✗ Failed to cache nets:', error);
  }
  
  const duration = Date.now() - startTime;
  const successCount = Object.values(results).filter(r => r.success).length;
  const totalCount = Object.keys(results).length;
  
  console.log(`[OfflinePreloader] Preload complete: ${successCount}/${totalCount} successful in ${duration}ms`);
  
  // Dispatch event for UI feedback
  window.dispatchEvent(new CustomEvent('offline-data-preloaded', {
    detail: { results, duration }
  }));
  
  return results;
}

/**
 * Check if offline data needs refresh
 * Call this periodically or on app resume
 * 
 * @param {object} user - Current user object
 * @returns {Promise<boolean>} - True if refresh is needed
 */
export async function shouldRefreshOfflineData(user) {
  // Check cache age - refresh if older than 1 hour
  const CACHE_MAX_AGE = 60 * 60 * 1000; // 1 hour
  
  try {
    const { isCacheStale } = await import('../db/indexedDB');
    const userContext = {
      userId: user.id,
      organizationId: user.organization_id,
      isSuperAdmin: user.role === 'super_admin'
    };
    
    // Check if any critical cache is stale
    const machinesStale = await isCacheStale(STORES.MACHINES, userContext, CACHE_MAX_AGE);
    const protocolsStale = await isCacheStale(STORES.MAINTENANCE_PROTOCOLS, userContext, CACHE_MAX_AGE);
    
    return machinesStale || protocolsStale;
  } catch (error) {
    console.error('[OfflinePreloader] Error checking cache staleness:', error);
    return true; // Refresh on error
  }
}

/**
 * Get preload progress (for UI feedback)
 * Returns the current state of cached data
 * 
 * @param {object} user - Current user object
 * @returns {Promise<object>} - Cache status
 */
export async function getPreloadStatus(user) {
  const { getCachedData } = await import('../db/indexedDB');
  
  const userContext = {
    userId: user.id,
    organizationId: user.organization_id,
    isSuperAdmin: user.role === 'super_admin'
  };
  
  try {
    const [machines, protocols, users, farmSites, nets] = await Promise.all([
      getCachedData(STORES.MACHINES, userContext),
      getCachedData(STORES.MAINTENANCE_PROTOCOLS, userContext),
      getCachedData(STORES.USERS, userContext),
      getCachedData(STORES.FARM_SITES, userContext),
      getCachedData(STORES.NETS, userContext),
    ]);
    
    return {
      machines: machines.length,
      protocols: protocols.length,
      users: users.length,
      farmSites: farmSites.length,
      nets: nets.length,
      total: machines.length + protocols.length + users.length + farmSites.length + nets.length,
      ready: machines.length > 0 && protocols.length > 0 && users.length > 0
    };
  } catch (error) {
    console.error('[OfflinePreloader] Error getting preload status:', error);
    return {
      machines: 0,
      protocols: 0,
      users: 0,
      farmSites: 0,
      nets: 0,
      total: 0,
      ready: false
    };
  }
}

export default {
  preloadOfflineData,
  shouldRefreshOfflineData,
  getPreloadStatus
};
