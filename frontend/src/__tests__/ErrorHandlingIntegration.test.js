// frontend/src/__tests__/ErrorHandlingIntegration.test.js

/**
 * Integration tests for error handling functionality
 * Tests the complete error handling flow from API to UI
 * Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 6.1, 6.2, 6.3, 6.4, 6.5
 */

import {
  processError,
  formatErrorForDisplay,
  isRetryableError,
  getRetryDelay,
  ERROR_MESSAGES,
  ERROR_TYPES
} from '../utils/errorHandling';

import { partsService } from '../services/partsService';
import { api } from '../services/api';

// Mock the API client
jest.mock('../services/api');

describe('Error Handling Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.spyOn(console, 'error').mockImplementation(() => { });
    jest.spyOn(console, 'warn').mockImplementation(() => { });
    jest.spyOn(console, 'group').mockImplementation(() => { });
    jest.spyOn(console, 'groupEnd').mockImplementation(() => { });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('Requirement 1.1-1.6: Complete Error Processing Flow', () => {
    test('1.1: Should process API errors into human-readable messages', () => {
      const apiError = {
        response: { status: 500, data: { detail: 'Database connection failed' } }
      };

      const result = processError(apiError);
      expect(result).toBe('Database connection failed');
      expect(result).not.toBe('[object Object]');
    });

    test('1.2: Should handle network errors with appropriate message', () => {
      const networkError = { request: {} };

      const result = processError(networkError);
      expect(result).toBe(ERROR_MESSAGES.NETWORK_ERROR);
      expect(result).toContain('Unable to connect to server');
    });

    test('1.3: Should handle authentication errors', () => {
      const authError = {
        response: { status: 401, data: { detail: 'Token expired' } }
      };

      const result = processError(authError);
      expect(result).toBe(ERROR_MESSAGES.AUTH_ERROR);
      expect(result).toContain('Authentication failed');
    });

    test('1.4: Should handle permission errors', () => {
      const permissionError = {
        response: { status: 403, data: { detail: 'Insufficient permissions' } }
      };

      const result = processError(permissionError);
      expect(result).toBe(ERROR_MESSAGES.PERMISSION_ERROR);
      expect(result).toContain("don't have permission");
    });

    test('1.5: Should handle server errors with specific messages', () => {
      const serverError = {
        response: { status: 500, data: { detail: 'Internal server error occurred' } }
      };

      const result = processError(serverError);
      expect(result).toBe('Internal server error occurred');
    });

    test('1.6: Should format errors for display with all required properties', () => {
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
  });

  describe('Requirement 6.1-6.5: Retry Logic Integration', () => {
    test('6.1: Should identify retryable errors correctly', () => {
      const retryableErrors = [
        { request: {} }, // Network error
        { response: { status: 500 } }, // Server error
        { response: { status: 502 } }, // Bad gateway
        { response: { status: 503 } }, // Service unavailable
        { code: 'ECONNABORTED' } // Timeout
      ];

      const nonRetryableErrors = [
        { response: { status: 401 } }, // Auth error
        { response: { status: 403 } }, // Permission error
        { response: { status: 400 } }, // Validation error
        { response: { status: 404 } } // Not found
      ];

      retryableErrors.forEach(error => {
        expect(isRetryableError(error)).toBe(true);
      });

      nonRetryableErrors.forEach(error => {
        expect(isRetryableError(error)).toBe(false);
      });
    });

    test('6.2: Should calculate retry delays with exponential backoff', () => {
      expect(getRetryDelay(1)).toBe(1000); // First retry: 1 second
      expect(getRetryDelay(2)).toBe(2000); // Second retry: 2 seconds
      expect(getRetryDelay(3)).toBe(4000); // Third retry: 4 seconds
      expect(getRetryDelay(4)).toBe(8000); // Fourth retry: 8 seconds
      expect(getRetryDelay(10)).toBe(10000); // Should be capped at max delay
    });

    test('6.3: Should show retry guidance after multiple attempts', () => {
      const error = { request: {} };

      const result1 = formatErrorForDisplay(error, 1);
      const result2 = formatErrorForDisplay(error, 2);
      const result3 = formatErrorForDisplay(error, 3);

      expect(result1.showRetryGuidance).toBe(false);
      expect(result2.showRetryGuidance).toBe(false);
      expect(result3.showRetryGuidance).toBe(true);
    });

    test('6.4: Should handle different error types appropriately', () => {
      const errorScenarios = [
        {
          error: { request: {} },
          expectedType: ERROR_TYPES.NETWORK,
          expectedRetryable: true
        },
        {
          error: { response: { status: 401 } },
          expectedType: ERROR_TYPES.AUTH,
          expectedRetryable: false
        },
        {
          error: { response: { status: 403 } },
          expectedType: ERROR_TYPES.PERMISSION,
          expectedRetryable: false
        },
        {
          error: { response: { status: 500 } },
          expectedType: ERROR_TYPES.SERVER,
          expectedRetryable: true
        }
      ];

      errorScenarios.forEach(({ error, expectedType, expectedRetryable }) => {
        const result = formatErrorForDisplay(error);
        expect(result.type).toBe(expectedType);
        expect(result.isRetryable).toBe(expectedRetryable);
      });
    });

    test('6.5: Should limit retry attempts appropriately', () => {
      const MAX_RETRY_ATTEMPTS = 3;
      const error = { request: {} };

      for (let attempt = 1; attempt <= MAX_RETRY_ATTEMPTS + 2; attempt++) {
        const result = formatErrorForDisplay(error, attempt);

        if (attempt <= MAX_RETRY_ATTEMPTS) {
          expect(result.isRetryable).toBe(true);
        }

        // Show guidance after multiple attempts
        if (attempt > 2) {
          expect(result.showRetryGuidance).toBe(true);
        }
      }
    });
  });

  describe('Parts Service Error Integration', () => {
    test('Should handle API errors in getPartsWithInventory', async () => {
      const mockError = new Error('API Error');
      mockError.response = { status: 500, data: { detail: 'Database error' } };

      api.get.mockRejectedValue(mockError);

      await expect(partsService.getPartsWithInventory()).rejects.toThrow('Database error');
    });

    test('Should handle network errors in getPartsWithInventory', async () => {
      const networkError = new Error('Network Error');
      networkError.request = {};

      api.get.mockRejectedValue(networkError);

      await expect(partsService.getPartsWithInventory()).rejects.toThrow(
        'Unable to connect to server'
      );
    });

    test('Should handle malformed responses gracefully', async () => {
      api.get.mockResolvedValue('not an array');

      const result = await partsService.getPartsWithInventory();
      expect(result).toEqual([]);
      expect(console.warn).toHaveBeenCalledWith(
        'API returned non-array response for parts with inventory:',
        'not an array'
      );
    });

    test('Should handle authentication errors in service methods', async () => {
      const authError = new Error('Auth Error');
      authError.response = { status: 401, data: { detail: 'Unauthorized' } };

      api.post.mockRejectedValue(authError);

      await expect(partsService.createPart({})).rejects.toThrow('Authentication failed');
    });

    test('Should handle permission errors in service methods', async () => {
      const permissionError = new Error('Permission Error');
      permissionError.response = { status: 403, data: { detail: 'Forbidden' } };

      api.put.mockRejectedValue(permissionError);

      await expect(partsService.updatePart('1', {})).rejects.toThrow(
        "You don't have permission"
      );
    });
  });

  describe('Error Message Clarity Validation', () => {
    test('Should provide specific messages for different HTTP status codes', () => {
      const statusTests = [
        { status: 400, expectedMessage: /Invalid data provided/ },
        { status: 404, expectedMessage: /The requested resource was not found/ },
        { status: 408, expectedMessage: /Request timed out/ },
        { status: 429, expectedMessage: /Too many requests/ },
        { status: 502, expectedMessage: /Server error occurred/ },
        { status: 503, expectedMessage: /Server error occurred/ }
      ];

      statusTests.forEach(({ status, expectedMessage }) => {
        const error = { response: { status, data: {} } };
        const result = processError(error);
        expect(result).toMatch(expectedMessage);
      });
    });

    test('Should handle malformed error responses', () => {
      const malformedErrors = [
        { response: { status: 500, data: null } },
        { response: { status: 500, data: undefined } },
        { response: { status: 500, data: {} } },
        { response: { status: 500 } }
      ];

      malformedErrors.forEach(error => {
        const result = processError(error);
        expect(result).toBe(ERROR_MESSAGES.SERVER_ERROR);
      });
    });

    test('Should extract error messages from different response formats', () => {
      const responseFormats = [
        { data: { detail: 'Detail message' }, expected: 'Detail message' },
        { data: { message: 'Message field' }, expected: 'Message field' },
        { data: { error: 'Error field' }, expected: 'Error field' }
      ];

      responseFormats.forEach(({ data, expected }) => {
        const error = { response: { status: 400, data } };
        const result = processError(error);
        expect(result).toBe(expected);
      });
    });
  });

  describe('Complete Integration Flow', () => {
    test('Should handle complete error-to-success scenario', async () => {
      const mockError = new Error('Temporary Error');
      mockError.response = { status: 500, data: { detail: 'Temporary server error' } };

      const mockParts = [{ id: '1', name: 'Test Part' }];

      // First call fails, second succeeds
      api.get
        .mockRejectedValueOnce(mockError)
        .mockResolvedValueOnce(mockParts);

      // First call should fail
      await expect(partsService.getPartsWithInventory()).rejects.toThrow(
        'Temporary server error'
      );

      // Second call should succeed
      const result = await partsService.getPartsWithInventory();
      expect(result).toEqual(mockParts);
    });

    test('Should handle various error scenarios in sequence', async () => {
      const errorScenarios = [
        {
          error: { request: {} },
          expectedMessage: /Unable to connect to server/
        },
        {
          error: { response: { status: 401, data: { detail: 'Unauthorized' } } },
          expectedMessage: /Authentication failed/
        },
        {
          error: { response: { status: 403, data: { detail: 'Forbidden' } } },
          expectedMessage: /You don't have permission/
        },
        {
          error: { response: { status: 500, data: { detail: 'Internal error' } } },
          expectedMessage: /Internal error/
        }
      ];

      for (const { error, expectedMessage } of errorScenarios) {
        const mockError = new Error('Test Error');
        Object.assign(mockError, error);

        api.get.mockRejectedValueOnce(mockError);

        await expect(partsService.getPartsWithInventory()).rejects.toThrow(expectedMessage);
      }
    });
  });
});