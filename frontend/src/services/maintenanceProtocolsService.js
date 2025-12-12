// frontend/src/services/maintenanceProtocolsService.js

import { api } from './api';
import translationService from './translationService';

// Protocol Management

export const listProtocols = async (filters = {}) => {
  const params = new URLSearchParams();
  if (filters.protocol_type) params.append('protocol_type', filters.protocol_type);
  if (filters.machine_model) params.append('machine_model', filters.machine_model);
  if (filters.is_active !== undefined) params.append('is_active', filters.is_active);
  if (filters.search) params.append('search', filters.search);
  
  return api.get(`/maintenance-protocols/?${params}`);
};

export const getProtocol = async (protocolId) => {
  return api.get(`/maintenance-protocols/${protocolId}`);
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
  return api.get(`/maintenance-protocols/${protocolId}/checklist-items`);
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

export const getLocalizedProtocols = async (filters = {}, userLanguage = null) => {
  console.log('🌍 getLocalizedProtocols called with language:', userLanguage);
  
  // Get base protocols first
  const protocols = await listProtocols(filters);
  console.log('📋 Base protocols loaded:', protocols.length);
  
  if (!userLanguage || userLanguage === 'en') {
    console.log('🇺🇸 Using English (base language)');
    return protocols;
  }
  
  // Get localized versions for each protocol
  console.log(`🔄 Getting localized versions for ${protocols.length} protocols in language: ${userLanguage}`);
  
  const localizedProtocols = await Promise.all(
    protocols.map(async (protocol) => {
      try {
        console.log(`🌍 Getting translation for protocol: "${protocol.name}" (${protocol.id})`);
        const localizedProtocol = await translationService.getLocalizedProtocol(protocol.id, userLanguage);
        console.log(`✅ Translation result:`, localizedProtocol);
        
        const result = {
          ...protocol,
          name: localizedProtocol.name || protocol.name,
          description: localizedProtocol.description || protocol.description,
          isTranslated: localizedProtocol.isTranslated || false
        };
        
        console.log(`📝 Final protocol: "${result.name}" (translated: ${result.isTranslated})`);
        return result;
      } catch (error) {
        // If translation fails, return original protocol
        console.warn(`❌ Failed to get translation for protocol ${protocol.id}:`, error);
        return protocol;
      }
    })
  );
  
  console.log(`🎯 Returning ${localizedProtocols.length} localized protocols`);
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
  console.log('📝 getLocalizedChecklistItems called for protocol:', protocolId, 'language:', userLanguage);
  
  if (!userLanguage || userLanguage === 'en') {
    console.log('🇺🇸 Using English checklist items');
    return getChecklistItems(protocolId);
  }
  
  try {
    console.log(`🌍 Getting localized checklist items for protocol ${protocolId} in ${userLanguage}`);
    const localizedItems = await translationService.getLocalizedChecklistItems(protocolId, userLanguage);
    console.log('✅ Localized checklist items received:', localizedItems);
    return localizedItems;
  } catch (error) {
    // Fallback to original checklist items
    console.warn(`❌ Failed to get localized checklist items for protocol ${protocolId}:`, error);
    return getChecklistItems(protocolId);
  }
};

