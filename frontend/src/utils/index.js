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