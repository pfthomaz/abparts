// frontend/src/utils/constants.js

/**
 * Application-wide constants for error handling and retry logic
 */

// Maximum number of retry attempts before giving up
export const MAX_RETRY_ATTEMPTS = 3;

// Default retry delays (in milliseconds)
export const RETRY_DELAYS = {
  BASE_DELAY: 1000,      // 1 second
  MAX_DELAY: 10000,      // 10 seconds
  NETWORK_DELAY: 2000,   // 2 seconds for network errors
  SERVER_DELAY: 5000     // 5 seconds for server errors
};

// Timeout values (in milliseconds)
export const TIMEOUTS = {
  API_REQUEST: 30000,    // 30 seconds
  RETRY_REQUEST: 15000,  // 15 seconds for retry attempts
  QUICK_REQUEST: 5000    // 5 seconds for quick operations
};

// Error display durations (in milliseconds)
export const ERROR_DISPLAY = {
  AUTO_DISMISS: 5000,    // Auto-dismiss errors after 5 seconds
  PERSISTENT: -1,        // Don't auto-dismiss (-1 means persistent)
  QUICK_FLASH: 2000      // Quick flash for minor errors
};

// API endpoint paths
export const API_ENDPOINTS = {
  PARTS: '/parts',
  PARTS_WITH_INVENTORY: '/parts/with-inventory',
  PARTS_SEARCH: '/parts/search',
  PARTS_SEARCH_WITH_INVENTORY: '/parts/search-with-inventory'
};

// Loading states
export const LOADING_STATES = {
  IDLE: 'idle',
  LOADING: 'loading',
  SUCCESS: 'success',
  ERROR: 'error',
  RETRYING: 'retrying'
};

// User guidance messages for different scenarios
export const USER_GUIDANCE = {
  MULTIPLE_FAILURES: "Multiple attempts failed. Please check your network connection or contact support.",
  NETWORK_ISSUES: "Having trouble connecting? Try refreshing the page or checking your internet connection.",
  SERVER_ISSUES: "Our servers are experiencing issues. Please try again in a few minutes.",
  PERMISSION_ISSUES: "You may need to log in again or contact your administrator for access.",
  GENERAL_HELP: "If this problem persists, please contact support with the error details."
};

// Success messages
export const SUCCESS_MESSAGES = {
  PARTS_LOADED: "Parts loaded successfully",
  RETRY_SUCCESS: "Connection restored successfully",
  DATA_REFRESHED: "Data refreshed successfully"
};

// Component display constants
export const DISPLAY_CONSTANTS = {
  EMPTY_STATE_TITLE: "No Parts Found",
  EMPTY_STATE_MESSAGE: "There are no parts in the system yet.",
  LOADING_MESSAGE: "Loading parts...",
  RETRY_BUTTON_TEXT: "Retry",
  ADD_PART_BUTTON_TEXT: "Add Part"
};