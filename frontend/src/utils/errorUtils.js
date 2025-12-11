// frontend/src/utils/errorUtils.js

/**
 * Predefined error messages for common error scenarios
 */
export const ERROR_MESSAGES = {
  NETWORK_ERROR: "Unable to connect to server. Please check your connection and try again.",
  AUTH_ERROR: "Authentication failed. Please log in again.",
  PERMISSION_ERROR: "You don't have permission to view this resource.",
  SERVER_ERROR: "Server error occurred. Please try again later.",
  UNKNOWN_ERROR: "An unexpected error occurred. Please try again.",
  DATA_ERROR: "Failed to load data. Please try again.",
  VALIDATION_ERROR: "The submitted data is invalid. Please check your inputs.",
  TIMEOUT_ERROR: "Request timed out. Please try again."
};

/**
 * Error types for categorizing different errors
 */
export const ERROR_TYPES = {
  NETWORK: 'network',
  AUTH: 'auth',
  PERMISSION: 'permission',
  SERVER: 'server',
  VALIDATION: 'validation',
  UNKNOWN: 'unknown',
  TIMEOUT: 'timeout'
};

/**
 * Processes an error object and returns a user-friendly error message
 * @param {Error|Object} error - The error object to process
 * @returns {string} A user-friendly error message
 */
export const processError = (error) => {
  // Log the full error for debugging
  console.error('Error details:', error);

  // Handle axios error responses
  if (error.response) {
    // Server responded with error status
    const status = error.response.status;
    const message = error.response.data?.detail ||
      error.response.data?.message ||
      error.response.data?.error;

    switch (status) {
      case 401:
        return ERROR_MESSAGES.AUTH_ERROR;
      case 403:
        return ERROR_MESSAGES.PERMISSION_ERROR;
      case 422:
        return message || ERROR_MESSAGES.VALIDATION_ERROR;
      case 500:
      case 502:
      case 503:
      case 504:
        return message || ERROR_MESSAGES.SERVER_ERROR;
      default:
        return message || ERROR_MESSAGES.UNKNOWN_ERROR;
    }
  }
  // Handle network errors (request made but no response received)
  else if (error.request) {
    if (error.code === 'ECONNABORTED') {
      return ERROR_MESSAGES.TIMEOUT_ERROR;
    }
    return ERROR_MESSAGES.NETWORK_ERROR;
  }
  // Handle other errors
  else if (error.message) {
    // If error is already a string message from our API service
    return error.message;
  }

  // If error is just a string
  if (typeof error === 'string') {
    return error;
  }

  // Fallback for unexpected error formats
  return ERROR_MESSAGES.UNKNOWN_ERROR;
};

/**
 * Determines the error type from an error object
 * @param {Error|Object} error - The error object
 * @returns {string} The error type
 */
export const getErrorType = (error) => {
  if (error.response) {
    const status = error.response.status;

    if (status === 401) return ERROR_TYPES.AUTH;
    if (status === 403) return ERROR_TYPES.PERMISSION;
    if (status === 422) return ERROR_TYPES.VALIDATION;
    if (status >= 500) return ERROR_TYPES.SERVER;

    return ERROR_TYPES.UNKNOWN;
  }
  else if (error.request) {
    if (error.code === 'ECONNABORTED') return ERROR_TYPES.TIMEOUT;
    return ERROR_TYPES.NETWORK;
  }

  return ERROR_TYPES.UNKNOWN;
};

/**
 * Creates a React error component props object
 * @param {Error|Object} error - The error object
 * @returns {Object} Props for error display component
 */
export const createErrorProps = (error) => {
  return {
    message: processError(error),
    type: getErrorType(error),
    originalError: error
  };
};

/**
 * Determines if an error should trigger automatic retry
 * @param {Error|Object} error - The error object
 * @returns {boolean} Whether the error should trigger automatic retry
 */
export const shouldAutoRetry = (error) => {
  const errorType = getErrorType(error);

  // Network errors and server errors (except 500) can be auto-retried
  return errorType === ERROR_TYPES.NETWORK ||
    (errorType === ERROR_TYPES.SERVER &&
      error.response?.status !== 500);
};

/**
 * Calculates exponential backoff time for retries
 * @param {number} retryCount - The current retry attempt count
 * @param {number} baseDelay - Base delay in milliseconds
 * @param {number} maxDelay - Maximum delay in milliseconds
 * @returns {number} The delay time in milliseconds
 */
export const getRetryDelay = (retryCount, baseDelay = 1000, maxDelay = 10000) => {
  const delay = Math.min(
    maxDelay,
    baseDelay * Math.pow(2, retryCount)
  );

  // Add some randomness to prevent all clients retrying simultaneously
  return delay + (Math.random() * 1000);
};