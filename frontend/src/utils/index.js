// frontend/src/utils/index.js

// Export error handling utilities
export {
  ERROR_MESSAGES,
  ERROR_TYPES,
  processError,
  getErrorType,
  logError,
  createStandardError,
  isRetryableError,
  getRetryDelay,
  formatErrorForDisplay
} from './errorHandling';

// Export constants
export {
  MAX_RETRY_ATTEMPTS,
  RETRY_DELAYS,
  TIMEOUTS,
  ERROR_DISPLAY,
  API_ENDPOINTS,
  LOADING_STATES,
  USER_GUIDANCE,
  SUCCESS_MESSAGES,
  DISPLAY_CONSTANTS
} from './constants';

// Export existing permissions utility
export * from './permissions';

// Export inventory validation utilities
export {
  validateInventoryData,
  extractInventoryMetadata,
  isValidArray,
  isArray,
  safeFilter,
  safeMap,
  safeReduce,
  safeFind,
  safeSort,
  validateInventoryItem,
  sanitizeInventoryItems,
  createSafeInventoryResult,
  logInventoryValidation
} from './inventoryValidation';

// Export formatting utilities
export const formatDate = (dateString) => {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

export const formatNumber = (value, unitOfMeasure = null) => {
  if (value === null || value === undefined) return '-';
  const num = parseFloat(value);
  if (isNaN(num)) return '-';
  
  // For consumables (pieces, units, boxes, sets), show as integer without decimals
  const consumableUnits = ['pieces', 'units', 'pcs', 'boxes', 'sets'];
  if (consumableUnits.includes(unitOfMeasure)) {
    return Math.floor(num).toLocaleString('en-US', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    });
  }
  
  // For liquids or other measures, show with up to 2 decimals
  return num.toLocaleString('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  });
};

// Function to get translated unit of measure
export const getTranslatedUnit = (unitOfMeasure, t) => {
  if (!unitOfMeasure || !t) return unitOfMeasure || '';
  
  // Map of unit keys to translation keys
  const unitTranslationMap = {
    'pieces': 'partForm.units.pieces',
    'liters': 'partForm.units.liters',
    'kilograms': 'partForm.units.kilograms',
    'kg': 'partForm.units.kilograms',
    'meters': 'partForm.units.meters',
    'gallons': 'partForm.units.gallons',
    'pounds': 'partForm.units.pounds',
    'feet': 'partForm.units.feet',
    'boxes': 'partForm.units.boxes',
    'sets': 'partForm.units.sets',
    'units': 'partForm.units.pieces', // Map 'units' to 'pieces' translation
    'pcs': 'partForm.units.pieces'    // Map 'pcs' to 'pieces' translation
  };
  
  const translationKey = unitTranslationMap[unitOfMeasure.toLowerCase()];
  return translationKey ? t(translationKey, unitOfMeasure) : unitOfMeasure;
};