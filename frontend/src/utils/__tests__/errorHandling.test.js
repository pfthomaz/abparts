// frontend/src/utils/__tests__/errorHandling.test.js

import {
  processError,
  getErrorType,
  logError,
  isRetryableError,
  getRetryDelay,
  formatErrorForDisplay,
  ERROR_MESSAGES,
  ERROR_TYPES
} from '../errorHandling';

describe('Error Handling Utilities', () => {
  beforeEach(() => {
    jest.spyOn(console, 'error').mockImplementation(() => { });
    jest.spyOn(console, 'warn').mockImplementation(() => { });
    jest.spyOn(console, 'group').mockImplementation(() => { });
    jest.spyOn(console, 'groupEnd').mockImplementation(() => { });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('processError function', () => {
    test('Should return auth error message for 401 status', () => {
      const error = {
        response: { status: 401, data: { detail: 'Unauthorized' } }
      };

      const result = processError(error);
      expect(result).toBe(ERROR_MESSAGES.AUTH_ERROR);
    });

    test('Should return permission error message for 403 status', () => {
      const error = {
        response: { status: 403, data: { detail: 'Forbidden' } }
      };

      const result = processError(error);
      expect(result).toBe(ERROR_MESSAGES.PERMISSION_ERROR);
    });

    test('Should return server message for 500 status when available', () => {
      const error = {
        response: {
          status: 500,
          data: { detail: 'Database connection failed' }
        }
      };

      const result = processError(error);
      expect(result).toBe('Database connection failed');
    });

    test('Should return default server error for 500 status without message', () => {
      const error = {
        response: { status: 500, data: {} }
      };

      const result = processError(error);
      expect(result).toBe(ERROR_MESSAGES.SERVER_ERROR);
    });

    test('Should return network error for request without response', () => {
      const error = {
        request: {}
      };

      const result = processError(error);
      expect(result).toBe(ERROR_MESSAGES.NETWORK_ERROR);
    });

    test('Should return timeout error for ECONNABORTED', () => {
      const error = {
        code: 'ECONNABORTED',
        message: 'timeout of 5000ms exceeded'
      };

      const result = processError(error);
      expect(result).toBe(ERROR_MESSAGES.TIMEOUT_ERROR);
    });

    test('Should return error message for other errors', () => {
      const error = {
        message: 'Custom error message'
      };

      const result = processError(error);
      expect(result).toBe('Custom error message');
    });

    test('Should return unknown error for errors without message', () => {
      const error = {};

      const result = processError(error);
      expect(result).toBe(ERROR_MESSAGES.UNKNOWN_ERROR);
    });

    test('Should handle different response data formats', () => {
      const testCases = [
        {
          error: { response: { status: 400, data: { detail: 'Detail message' } } },
          expected: 'Detail message'
        },
        {
          error: { response: { status: 400, data: { message: 'Message field' } } },
          expected: 'Message field'
        },
        {
          error: { response: { status: 400, data: { error: 'Error field' } } },
          expected: 'Error field'
        }
      ];

      testCases.forEach(({ error, expected }) => {
        expect(processError(error)).toBe(expected);
      });
    });
  });

  describe('getErrorType function', () => {
    test('Should return correct error types for different scenarios', () => {
      const testCases = [
        {
          error: { response: { status: 401 } },
          expected: ERROR_TYPES.AUTH
        },
        {
          error: { response: { status: 403 } },
          expected: ERROR_TYPES.PERMISSION
        },
        {
          error: { response: { status: 404 } },
          expected: ERROR_TYPES.NOT_FOUND
        },
        {
          error: { response: { status: 500 } },
          expected: ERROR_TYPES.SERVER
        },
        {
          error: { request: {} },
          expected: ERROR_TYPES.NETWORK
        },
        {
          error: { code: 'ECONNABORTED' },
          expected: ERROR_TYPES.TIMEOUT
        },
        {
          error: { message: 'Some error' },
          expected: ERROR_TYPES.UNKNOWN
        }
      ];

      testCases.forEach(({ error, expected }) => {
        expect(getErrorType(error)).toBe(expected);
      });
    });
  });

  describe('isRetryableError function', () => {
    test('Should return true for retryable error types', () => {
      const retryableErrors = [
        { request: {} }, // Network error
        { code: 'ECONNABORTED' }, // Timeout
        { response: { status: 500 } }, // Server error
        { response: { status: 502 } }, // Bad gateway
        { response: { status: 503 } } // Service unavailable
      ];

      retryableErrors.forEach(error => {
        expect(isRetryableError(error)).toBe(true);
      });
    });

    test('Should return false for non-retryable error types', () => {
      const nonRetryableErrors = [
        { response: { status: 401 } }, // Auth error
        { response: { status: 403 } }, // Permission error
        { response: { status: 400 } }, // Validation error
        { response: { status: 404 } } // Not found
      ];

      nonRetryableErrors.forEach(error => {
        expect(isRetryableError(error)).toBe(false);
      });
    });
  });

  describe('getRetryDelay function', () => {
    test('Should implement exponential backoff', () => {
      expect(getRetryDelay(1)).toBe(1000); // 1 * 2^0 = 1000ms
      expect(getRetryDelay(2)).toBe(2000); // 1000 * 2^1 = 2000ms
      expect(getRetryDelay(3)).toBe(4000); // 1000 * 2^2 = 4000ms
      expect(getRetryDelay(4)).toBe(8000); // 1000 * 2^3 = 8000ms
    });

    test('Should respect maximum delay', () => {
      expect(getRetryDelay(10)).toBe(10000); // Should be capped at maxDelay
      expect(getRetryDelay(5, 1000, 5000)).toBe(5000); // Custom maxDelay
    });

    test('Should handle custom base delay', () => {
      expect(getRetryDelay(1, 500)).toBe(500);
      expect(getRetryDelay(2, 500)).toBe(1000);
      expect(getRetryDelay(3, 500)).toBe(2000);
    });
  });

  describe('formatErrorForDisplay function', () => {
    test('Should format error with all required properties', () => {
      const error = {
        response: { status: 500, data: { detail: 'Server error' } }
      };

      const result = formatErrorForDisplay(error, 1);

      expect(result).toHaveProperty('message');
      expect(result).toHaveProperty('type');
      expect(result).toHaveProperty('isRetryable');
      expect(result).toHaveProperty('retryCount', 1);
      expect(result).toHaveProperty('showRetryGuidance');
      expect(result).toHaveProperty('timestamp');
    });

    test('Should set showRetryGuidance to true after 2 retries', () => {
      const error = { request: {} };

      const result1 = formatErrorForDisplay(error, 1);
      const result2 = formatErrorForDisplay(error, 2);
      const result3 = formatErrorForDisplay(error, 3);

      expect(result1.showRetryGuidance).toBe(false);
      expect(result2.showRetryGuidance).toBe(false);
      expect(result3.showRetryGuidance).toBe(true);
    });

    test('Should correctly identify retryable errors', () => {
      const retryableError = { request: {} };
      const nonRetryableError = { response: { status: 401 } };

      const result1 = formatErrorForDisplay(retryableError);
      const result2 = formatErrorForDisplay(nonRetryableError);

      expect(result1.isRetryable).toBe(true);
      expect(result2.isRetryable).toBe(false);
    });
  });

  describe('logError function', () => {
    test('Should log error with proper structure', () => {
      const error = {
        response: {
          status: 500,
          data: { detail: 'Server error' },
          headers: { 'content-type': 'application/json' }
        },
        stack: 'Error stack trace'
      };

      logError(error, 'test context');

      expect(console.group).toHaveBeenCalledWith(
        expect.stringContaining('🚨 Error in test context')
      );
      expect(console.error).toHaveBeenCalledWith('Error Type:', ERROR_TYPES.SERVER);
      expect(console.error).toHaveBeenCalledWith('Error Object:', error);
      expect(console.error).toHaveBeenCalledWith('Response Status:', 500);
      expect(console.error).toHaveBeenCalledWith('Response Data:', { detail: 'Server error' });
      expect(console.error).toHaveBeenCalledWith('Stack Trace:', 'Error stack trace');
      expect(console.groupEnd).toHaveBeenCalled();
    });

    test('Should log network error details', () => {
      const error = {
        request: { url: 'http://example.com/api' },
        stack: 'Network error stack'
      };

      logError(error);

      expect(console.error).toHaveBeenCalledWith('Error Type:', ERROR_TYPES.NETWORK);
      expect(console.error).toHaveBeenCalledWith('Request:', error.request);
    });

    test('Should handle errors without context', () => {
      const error = { message: 'Test error' };

      logError(error);

      expect(console.group).toHaveBeenCalledWith(
        expect.stringContaining('🚨 Error')
      );
      expect(console.group).toHaveBeenCalledWith(
        expect.not.stringContaining('in ')
      );
    });
  });
});