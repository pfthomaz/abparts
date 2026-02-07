// frontend/src/services/maintenanceProtocolsService.js

import { api } from './api';
import translationService from './translationService';
import { isOnline } from '../hooks/useNetworkStatus';
import { 
  cacheData, 
  getCachedData, 
  getCachedItem,
  isCacheStale, 
  STORES 
} from '../db/indexedDB';

// Protocol Management

export const listProtocols = async (filters = {}, forceRefresh = false) => {
  const online = isOnline();
  
  // Helper function to filter cached data
  const filterCachedData = (data) => {
    return data.filter(p => {
      if (filters.protocol_type && p.protocol_type !== filters.protocol_type) return false;
      if (filters.is_active !== undefined && p.is_active !== filters.is_active) return false;
      if (filters.machine_model && p.machine_model !== filters.machine_model) return false;
      if (filters.search) {
        const searchLower = filters.search.toLowerCase();
        const matchesName = p.name?.toLowerCase().includes(searchLower);
        const matchesDesc = p.description?.toLowerCase().includes(searchLower);
        if (!matchesName && !matchesDesc) return false;
      }
      return true;
    });
  };
  
  // If offline, use cache immediately
  if (!online) {
    const cached = await getCachedData(STORES.PROTOCOLS);
    if (cached.length > 0) {
      // console.log('[MaintenanceService] Using cached protocols (offline):', cached.length);
      return filterCachedData(cached);
    }
    throw new Error('No cached data available offline');
  }
  
  // Check cache staleness (with timeout to prevent blocking)
  let cacheStale = true;
  try {
    const staleCheckPromise = isCacheStale(STORES.PROTOCOLS);
    const timeoutPromise = new Promise((resolve) => setTimeout(() => resolve(true), 1000));
    cacheStale = await Promise.race([staleCheckPromise, timeoutPromise]);
  } catch (error) {
    console.warn('[MaintenanceService] Cache staleness check failed:', error);
    cacheStale = true; // Assume stale on error
  }
  
  // Use cache if fresh and not forcing refresh
  if (!cacheStale && !forceRefresh) {
    const cached = await getCachedData(STORES.PROTOCOLS);
    if (cached.length > 0) {
      // console.log('[MaintenanceService] Using cached protocols (fresh):', cached.length);
      return filterCachedData(cached);
    }
  }
  
  // Fetch from API with timeout
  try {
    const params = new URLSearchParams();
    if (filters.protocol_type) params.append('protocol_type', filters.protocol_type);
    if (filters.machine_model) params.append('machine_model', filters.machine_model);
    if (filters.is_active !== undefined) params.append('is_active', filters.is_active);
    if (filters.search) params.append('search', filters.search);
    
    const data = await api.get(`/maintenance-protocols/?${params}`);
    
    // Cache the response
    await cacheData(STORES.PROTOCOLS, data);
    // console.log('[MaintenanceService] Cached protocols:', data.length);
    
    return data;
  } catch (error) {
    // Fallback to cache on error
    console.warn('[MaintenanceService] API failed, attempting cache fallback:', error.message);
    const cached = await getCachedData(STORES.PROTOCOLS);
    if (cached.length > 0) {
      // console.log('[MaintenanceService] Using cached protocols (fallback):', cached.length);
      return filterCachedData(cached);
    }
    throw error;
  }
};

export const getProtocol = async (protocolId) => {
  const online = isOnline();
  
  // Try cache first if offline
  if (!online) {
    const cached = await getCachedItem(STORES.PROTOCOLS, protocolId);
    if (cached) {
      // console.log('[MaintenanceService] Using cached protocol:', protocolId);
      return cached;
    }
  }
  
  // Fetch from API
  try {
    const data = await api.get(`/maintenance-protocols/${protocolId}`);
    
    // Update cache
    await cacheData(STORES.PROTOCOLS, data);
    
    return data;
  } catch (error) {
    // Fallback to cache on error
    const cached = await getCachedItem(STORES.PROTOCOLS, protocolId);
    if (cached) {
      // console.log('[MaintenanceService] Using cached protocol (fallback):', protocolId);
      return cached;
    }
    throw error;
  }
};

export const createProtocol = async (protocolData) => {
  return api.post('/maintenance-protocols/', protocolData);
};

export const updateProtocol = async (protocolId, protocolData) => {
  return api.put(`/maintenance-protocols/${protocolId}`, protocolData);
};

export const deleteProtocol = async (protocolId) => {
  return api.delete(`/maintenance-protocols/${protocolId}`);
};

export const duplicateProtocol = async (protocolId, duplicateData) => {
  return api.post(`/maintenance-protocols/${protocolId}/duplicate`, duplicateData);
};

// Checklist Item Management

export const getChecklistItems = async (protocolId) => {
  const online = isOnline();
  
  // Try to get from cached protocol first
  if (!online) {
    const cachedProtocol = await getCachedItem(STORES.PROTOCOLS, protocolId);
    if (cachedProtocol && cachedProtocol.checklist_items) {
      // console.log('[MaintenanceService] Using cached checklist items (offline):', cachedProtocol.checklist_items.length);
      return cachedProtocol.checklist_items;
    }
  }
  
  // Fetch from API
  try {
    const items = await api.get(`/maintenance-protocols/${protocolId}/checklist-items`);
    
    // Update the cached protocol with checklist items
    const cachedProtocol = await getCachedItem(STORES.PROTOCOLS, protocolId);
    if (cachedProtocol) {
      cachedProtocol.checklist_items = items;
      await cacheData(STORES.PROTOCOLS, cachedProtocol);
      // console.log('[MaintenanceService] Cached checklist items:', items.length);
    }
    
    return items;
  } catch (error) {
    // Fallback to cached protocol
    console.warn('[MaintenanceService] API failed, attempting cache fallback for checklist items');
    const cachedProtocol = await getCachedItem(STORES.PROTOCOLS, protocolId);
    if (cachedProtocol && cachedProtocol.checklist_items) {
      // console.log('[MaintenanceService] Using cached checklist items (fallback):', cachedProtocol.checklist_items.length);
      return cachedProtocol.checklist_items;
    }
    throw error;
  }
};

export const createChecklistItem = async (protocolId, itemData) => {
  return api.post(`/maintenance-protocols/${protocolId}/checklist-items`, itemData);
};

export const updateChecklistItem = async (protocolId, itemId, itemData) => {
  return api.put(`/maintenance-protocols/${protocolId}/checklist-items/${itemId}`, itemData);
};

export const deleteChecklistItem = async (protocolId, itemId) => {
  return api.delete(`/maintenance-protocols/${protocolId}/checklist-items/${itemId}`);
};

export const reorderChecklistItems = async (protocolId, itemOrders) => {
  return api.post(`/maintenance-protocols/${protocolId}/checklist-items/reorder`, { item_orders: itemOrders });
};

// User-facing endpoints

export const getProtocolsForMachine = async (machineId, userLanguage = null) => {
  const protocols = await api.get(`/maintenance-protocols/for-machine/${machineId}`);
  
  if (!userLanguage || userLanguage === 'en') {
    return protocols;
  }
  
  // Get localized versions
  const localizedProtocols = await Promise.all(
    protocols.map(async (protocol) => {
      try {
        const localizedProtocol = await translationService.getLocalizedProtocol(protocol.id, userLanguage);
        return {
          ...protocol,
          name: localizedProtocol.name || protocol.name,
          description: localizedProtocol.description || protocol.description,
          isTranslated: localizedProtocol.isTranslated || false
        };
      } catch (error) {
        return protocol;
      }
    })
  );
  
  return localizedProtocols;
};

export const getExecutions = async (skip = 0, limit = 100) => {
  return api.get(`/maintenance-protocols/executions?skip=${skip}&limit=${limit}`);
};

export const createExecution = async (executionData) => {
  return api.post('/maintenance-protocols/executions', executionData);
};

export const completeChecklistItem = async (executionId, itemId, completionData) => {
  return api.post(`/maintenance-protocols/executions/${executionId}/checklist/${itemId}/complete`, completionData);
};

export const completeExecution = async (executionId) => {
  return api.put(`/maintenance-protocols/executions/${executionId}/complete`);
};

export const getExecutionsForMachine = async (machineId, skip = 0, limit = 50) => {
  return api.get(`/maintenance-protocols/executions/machine/${machineId}?skip=${skip}&limit=${limit}`);
};

export const getPendingReminders = async () => {
  return api.get('/maintenance-protocols/reminders/pending/');
};

export const acknowledgeReminder = async (reminderId) => {
  return api.put(`/maintenance-protocols/reminders/${reminderId}/acknowledge`);
};

// Localized Protocol Functions (Language-aware)

export const getLocalizedProtocols = async (filters = {}, userLanguage = null, forceRefresh = false) => {
  // Get base protocols first (with caching)
  const protocols = await listProtocols(filters, forceRefresh);
  
  if (!userLanguage || userLanguage === 'en') {
    return protocols;
  }
  
  // Get localized versions for each protocol
  const localizedProtocols = await Promise.all(
    protocols.map(async (protocol) => {
      try {
        const localizedProtocol = await translationService.getLocalizedProtocol(protocol.id, userLanguage);
        
        const result = {
          ...protocol,
          name: localizedProtocol.name || protocol.name,
          description: localizedProtocol.description || protocol.description,
          isTranslated: localizedProtocol.isTranslated || false
        };
        
        return result;
      } catch (error) {
        // If translation fails, return original protocol
        console.warn(`Failed to get translation for protocol ${protocol.id}:`, error);
        return protocol;
      }
    })
  );
  
  return localizedProtocols;
};

export const getLocalizedProtocol = async (protocolId, userLanguage = null) => {
  if (!userLanguage || userLanguage === 'en') {
    return getProtocol(protocolId);
  }
  
  try {
    const localizedProtocol = await translationService.getLocalizedProtocol(protocolId, userLanguage);
    return localizedProtocol;
  } catch (error) {
    // Fallback to original protocol
    console.warn(`Failed to get localized protocol ${protocolId}:`, error);
    return getProtocol(protocolId);
  }
};

export const getLocalizedChecklistItems = async (protocolId, userLanguage = null) => {
  if (!userLanguage || userLanguage === 'en') {
    return getChecklistItems(protocolId);
  }
  
  try {
    const localizedItems = await translationService.getLocalizedChecklistItems(protocolId, userLanguage);
    return localizedItems;
  } catch (error) {
    // Fallback to original checklist items
    console.warn(`Failed to get localized checklist items for protocol ${protocolId}:`, error);
    return getChecklistItems(protocolId);
  }
};

export const deleteExecution = async (executionId) => {
  return api.delete(`/maintenance-protocols/executions/${executionId}`);
};

