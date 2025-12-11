// frontend/src/services/__tests__/partsService.test.js

import { partsService } from '../partsService';
import { api } from '../api';
import { processError, logError } from '../../utils/errorHandling';

// Mock the API client
jest.mock('../api');

// Mock the error handling utilities
jest.mock('../../utils/errorHandling');

describe('Parts Service - Error Handling Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Mock console methods
    jest.spyOn(console, 'error').mockImplementation(() => { });
    jest.spyOn(console, 'warn').mockImplementation(() => { });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('Requirement 4.1-4.5: Frontend Service Integration', () => {
    describe('getPartsWithInventory', () => {
      test('4.1: Should return data on success', async () => {
        const mockData = [
          {
            id: '1',
            name: 'Test Part',
            part_number: 'TP001',
            total_stock: 10,
            warehouse_inventory: []
          }
        ];

        api.get.mockResolvedValue(mockData);

        const result = await partsService.getPartsWithInventory();

        expect(result).toEqual(mockData);
        expect(api.get).toHaveBeenCalledWith('/parts/with-inventory');
      });

      test('4.2: Should throw error with meaningful message on API error', async () => {
        const mockError = new Error('API Error');
        mockError.response = { status: 500, data: { detail: 'Server error' } };

        api.get.mockRejectedValue(mockError);
        processError.mockReturnValue('Server error occurred. Please try again later.');

        await expect(partsService.getPartsWithInventory()).rejects.toThrow(
          'Server error occurred. Please try again later.'
        );

        expect(logError).toHaveBeenCalledWith(mockError, 'partsService.getPartsWithInventory');
        expect(processError).toHaveBeenCalledWith(mockError);
      });

      test('4.3: Should handle malformed response gracefully', async () => {
        // API returns non-array response
        api.get.mockResolvedValue({ message: 'Not an array' });

        const result = await partsService.getPartsWithInventory();

        expect(result).toEqual([]);
        expect(console.warn).toHaveBeenCalledWith(
          'API returned non-array response for parts with inventory:',
          { message: 'Not an array' }
        );
      });

      test('4.4: Should extract and return error message from API response', async () => {
        const mockError = new Error('API Error');
        mockError.response = {
          status: 400,
          data: { detail: 'Invalid request parameters' }
        };

        api.get.mockRejectedValue(mockError);
        processError.mockReturnValue('Invalid request parameters');

        await expect(partsService.getPartsWithInventory()).rejects.toThrow(
          'Invalid request parameters'
        );

        expect(processError).toHaveBeenCalledWith(mockError);
      });

      test('4.5: Should provide user-friendly error message for network issues', async () => {
        const networkError = new Error('Network Error');
        networkError.request = {}; // Indicates network error

        api.get.mockRejectedValue(networkError);
        processError.mockReturnValue('Unable to connect to server. Please check your connection and try again.');

        await expect(partsService.getPartsWithInventory()).rejects.toThrow(
          'Unable to connect to server. Please check your connection and try again.'
        );

        expect(processError).toHaveBeenCalledWith(networkError);
      });

      test('Should handle filters correctly', async () => {
        const mockData = [];
        const filters = {
          part_type: 'consumable',
          is_proprietary: true,
          organization_id: 'org-1'
        };

        api.get.mockResolvedValue(mockData);

        await partsService.getPartsWithInventory(filters);

        expect(api.get).toHaveBeenCalledWith(
          '/parts/with-inventory?part_type=consumable&is_proprietary=true&organization_id=org-1'
        );
      });

      test('Should filter out empty filter values', async () => {
        const mockData = [];
        const filters = {
          part_type: 'consumable',
          is_proprietary: '',
          organization_id: null,
          search: undefined
        };

        api.get.mockResolvedValue(mockData);

        await partsService.getPartsWithInventory(filters);

        expect(api.get).toHaveBeenCalledWith('/parts/with-inventory?part_type=consumable');
      });
    });

    describe('Other service methods error handling', () => {
      test('createPart should handle errors properly', async () => {
        const mockError = new Error('Validation Error');
        mockError.response = { status: 400, data: { detail: 'Invalid part data' } };

        api.post.mockRejectedValue(mockError);
        processError.mockReturnValue('Invalid part data');

        const partData = { name: 'Test Part', part_number: 'TP001' };

        await expect(partsService.createPart(partData)).rejects.toThrow('Invalid part data');

        expect(logError).toHaveBeenCalledWith(mockError, 'partsService.createPart');
        expect(api.post).toHaveBeenCalledWith('/parts', partData);
      });

      test('updatePart should handle errors properly', async () => {
        const mockError = new Error('Not Found Error');
        mockError.response = { status: 404, data: { detail: 'Part not found' } };

        api.put.mockRejectedValue(mockError);
        processError.mockReturnValue('Part not found');

        const partId = 'part-1';
        const partData = { name: 'Updated Part' };

        await expect(partsService.updatePart(partId, partData)).rejects.toThrow('Part not found');

        expect(logError).toHaveBeenCalledWith(mockError, 'partsService.updatePart');
        expect(api.put).toHaveBeenCalledWith(`/parts/${partId}`, partData);
      });

      test('deletePart should handle errors properly', async () => {
        const mockError = new Error('Permission Error');
        mockError.response = { status: 403, data: { detail: 'Insufficient permissions' } };

        api.delete.mockRejectedValue(mockError);
        processError.mockReturnValue('Insufficient permissions');

        const partId = 'part-1';

        await expect(partsService.deletePart(partId)).rejects.toThrow('Insufficient permissions');

        expect(logError).toHaveBeenCalledWith(mockError, 'partsService.deletePart');
        expect(api.delete).toHaveBeenCalledWith(`/parts/${partId}`);
      });

      test('searchPartsWithInventory should handle malformed response', async () => {
        // API returns non-array response
        api.get.mockResolvedValue('not an array');

        const result = await partsService.searchPartsWithInventory('test');

        expect(result).toEqual([]);
        expect(console.warn).toHaveBeenCalledWith(
          'API returned non-array response for parts search with inventory:',
          'not an array'
        );
      });
    });
  });

  describe('Error Logging and Debugging', () => {
    test('Should log errors with proper context', async () => {
      const mockError = new Error('Test Error');
      api.get.mockRejectedValue(mockError);
      processError.mockReturnValue('Processed error message');

      try {
        await partsService.getPartsWithInventory();
      } catch (error) {
        // Expected to throw
      }

      expect(logError).toHaveBeenCalledWith(mockError, 'partsService.getPartsWithInventory');
    });

    test('Should preserve original error information', async () => {
      const mockError = new Error('Original Error');
      mockError.response = {
        status: 500,
        data: { detail: 'Server error' },
        headers: { 'content-type': 'application/json' }
      };

      api.get.mockRejectedValue(mockError);
      processError.mockReturnValue('Processed error');

      try {
        await partsService.getPartsWithInventory();
      } catch (error) {
        // The service should throw a new Error with processed message
        expect(error.message).toBe('Processed error');
      }

      // But the original error should be logged
      expect(logError).toHaveBeenCalledWith(mockError, 'partsService.getPartsWithInventory');
    });
  });
});