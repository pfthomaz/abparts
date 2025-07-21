// frontend/src/utils/errorHandling.js

/**
 * Predefined error messages for different error scenarios
 */
export const ERROR_MESSAGES = {
  NETWORK_ERROR: "Unable to connect to server. Please check your connection and try again.",
  AUTH_ERROR: "Authentication failed. Please log in again.",
  PERMISSION_ERROR: "You don't have permission to view parts.",
  SERVER_ERROR: "Server error occurred. Please try again later.",
  UNKNOWN_ERROR: "An unexpected error occurred. Please try again.",
  TIMEOUT_ERROR: "Request timed out. Please try again.",
  VALIDATION_ERROR: "Invalid data provided. Please check your input.",
  NOT_FOUND_ERROR: "The requested resource was not found.",
  RATE_LIMIT_ERROR: "Too many requests. Please wait a moment and try again."
};

/**
 * Error types for categorizing different kinds of errors
 */
export const ERROR_TYPES = {
  NETWORK: 'NETWORK',
  AUTH: 'AUTH',
  PERMISSION: 'PERMISSION',
  SERVER: 'SERVER',
  VALIDATION: 'VALIDATION',
  NOT_FOUND: 'NOT_FOUND',
  TIMEOUT: 'TIMEOUT',
  RATE_LIMIT: 'RATE_LIMIT',
  UNKNOWN: 'UNKNOWN'
};

/**
 * HTTP status code to error type mapping
 */
const STATUS_CODE_TO_ERROR_TYPE = {
  400: ERROR_TYPES.VALIDATION,
  401: ERROR_TYPES.AUTH,
  403: ERROR_TYPES.PERMISSION,
  404: ERROR_TYPES.NOT_FOUND,
  408: ERROR_TYPES.TIMEOUT,
  429: ERROR_TYPES.RATE_LIMIT,
  500: ERROR_TYPES.SERVER,
  502: ERROR_TYPES.SERVER,
  503: ERROR_TYPES.SERVER,
  504: ERROR_TYPES.TIMEOUT
};

/**
 * Processes an error object and returns a user-friendly error message
 * @param {Error|Object} error - The error object to process
 * @returns {string} - User-friendly error message
 */
export const processError = (error) => {
  // Log the full error for debugging
  console.error('Processing error:', error);

  if (error.response) {
    // Server responded with error status
    const status = error.response.status;
    const serverMessage = error.response.data?.detail ||
      error.response.data?.message ||
      error.response.data?.error;

    switch (status) {
      case 401:
        return ERROR_MESSAGES.AUTH_ERROR;
      case 403:
        return ERROR_MESSAGES.PERMISSION_ERROR;
      case 404:
        return ERROR_MESSAGES.NOT_FOUND_ERROR;
      case 408:
      case 504:
        return ERROR_MESSAGES.TIMEOUT_ERROR;
      case 429:
        return ERROR_MESSAGES.RATE_LIMIT_ERROR;
      case 500:
      case 502:
      case 503:
        return serverMessage || ERROR_MESSAGES.SERVER_ERROR;
      case 400:
        return serverMessage || ERROR_MESSAGES.VALIDATION_ERROR;
      default:
        return serverMessage || ERROR_MESSAGES.UNKNOWN_ERROR;
    }
  } else if (error.request) {
    // Network error - request was made but no response received
    return ERROR_MESSAGES.NETWORK_ERROR;
  } else if (error.code === 'ECONNABORTED') {
    // Request timeout
    return ERROR_MESSAGES.TIMEOUT_ERROR;
  } else {
    // Other error
    return error.message || ERROR_MESSAGES.UNKNOWN_ERROR;
  }
};

/**
 * Gets the error type based on the error object
 * @param {Error|Object} error - The error object to categorize
 * @returns {string} - Error type from ERROR_TYPES
 */
export const getErrorType = (error) => {
  if (error.response) {
    const status = error.response.status;
    return STATUS_CODE_TO_ERROR_TYPE[status] || ERROR_TYPES.UNKNOWN;
  } else if (error.request) {
    return ERROR_TYPES.NETWORK;
  } else if (error.code === 'ECONNABORTED') {
    return ERROR_TYPES.TIMEOUT;
  } else {
    return ERROR_TYPES.UNKNOWN;
  }
};

/**
 * Logs error details for debugging purposes
 * @param {Error|Object} error - The error to log
 * @param {string} context - Additional context about where the error occurred
 */
export const logError = (error, context = '') => {
  const errorType = getErrorType(error);
  const timestamp = new Date().toISOString();

  console.group(`🚨 Error ${context ? `in ${context}` : ''} - ${timestamp}`);
  console.error('Error Type:', errorType);
  console.error('Error Object:', error);

  if (error.response) {
    console.error('Response Status:', error.response.status);
    console.error('Response Data:', error.response.data);
    console.error('Response Headers:', error.response.headers);
  } else if (error.request) {
    console.error('Request:', error.request);
  }

  console.error('Stack Trace:', error.stack);
  console.groupEnd();
};

/**
 * Creates a standardized error object for consistent error handling
 * @param {string} message - User-friendly error message
 * @param {string} type - Error type from ERROR_TYPES
 * @param {Object} originalError - Original error object for debugging
 * @returns {Object} - Standardized error object
 */
export const createStandardError = (message, type = ERROR_TYPES.UNKNOWN, originalError = null) => {
  return {
    message,
    type,
    timestamp: new Date().toISOString(),
    originalError
  };
};

/**
 * Determines if an error is retryable based on its type
 * @param {Error|Object} error - The error to check
 * @returns {boolean} - Whether the error is retryable
 */
export const isRetryableError = (error) => {
  const errorType = getErrorType(error);

  // Network errors, timeouts, and server errors are typically retryable
  const retryableTypes = [
    ERROR_TYPES.NETWORK,
    ERROR_TYPES.TIMEOUT,
    ERROR_TYPES.SERVER
  ];

  return retryableTypes.includes(errorType);
};

/**
 * Gets retry delay in milliseconds based on attempt count (exponential backoff)
 * @param {number} attemptCount - Current retry attempt (starting from 1)
 * @param {number} baseDelay - Base delay in milliseconds (default: 1000)
 * @param {number} maxDelay - Maximum delay in milliseconds (default: 10000)
 * @returns {number} - Delay in milliseconds
 */
export const getRetryDelay = (attemptCount, baseDelay = 1000, maxDelay = 10000) => {
  const delay = baseDelay * Math.pow(2, attemptCount - 1);
  return Math.min(delay, maxDelay);
};

/**
 * Formats error for display in UI components
 * @param {Error|Object} error - The error to format
 * @param {number} retryCount - Number of retry attempts made
 * @returns {Object} - Formatted error object for UI display
 */
export const formatErrorForDisplay = (error, retryCount = 0) => {
  const message = processError(error);
  const type = getErrorType(error);
  const isRetryable = isRetryableError(error);

  return {
    message,
    type,
    isRetryable,
    retryCount,
    showRetryGuidance: retryCount > 2,
    timestamp: new Date().toISOString()
  };
};