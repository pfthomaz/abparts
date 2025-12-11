// frontend/src/utils/__tests__/inventoryValidation.test.js

import {
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
} from '../inventoryValidation';

describe('inventoryValidation - Comprehensive Data Validation Tests', () => {
  // Mock console methods to avoid cluttering test output
  beforeEach(() => {
    jest.spyOn(console, 'warn').mockImplementation(() => { });
    jest.spyOn(console, 'error').mockImplementation(() => { });
    jest.spyOn(console, 'log').mockImplementation(() => { });
    jest.spyOn(console, 'group').mockImplementation(() => { });
    jest.spyOn(console, 'groupEnd').mockImplementation(() => { });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('validateInventoryData - Various Input Types', () => {
    test('returns empty array for null/undefined input', () => {
      expect(validateInventoryData(null)).toEqual([]);
      expect(validateInventoryData(undefined)).toEqual([]);
      expect(validateInventoryData('')).toEqual([]);
      expect(validateInventoryData(0)).toEqual([]);
      expect(validateInventoryData(false)).toEqual([]);
      expect(validateInventoryData(NaN)).toEqual([]);
    });

    test('returns filtered array when input is already an array', () => {
      const input = [
        { part_id: '1', part_name: 'Part 1' },
        null,
        { part_id: '2', part_name: 'Part 2' },
        undefined,
        'invalid',
        123,
        false,
        []
      ];
      const result = validateInventoryData(input);
      expect(result).toHaveLength(3); // Only valid objects should remain
      expect(result[0]).toEqual({ part_id: '1', part_name: 'Part 1' });
      expect(result[1]).toEqual({ part_id: '2', part_name: 'Part 2' });
      expect(result[2]).toEqual([]); // Empty array is still an object
    });

    test('handles empty array input', () => {
      expect(validateInventoryData([])).toEqual([]);
    });

    test('handles array with all invalid items', () => {
      const input = [null, undefined, 'string', 123, true];
      const result = validateInventoryData(input);
      expect(result).toEqual([]);
    });

    test('extracts inventory_summary from API response object', () => {
      const apiResponse = {
        organization_id: 'org-123',
        inventory_summary: [
          { part_id: '1', part_name: 'Part 1' },
          { part_id: '2', part_name: 'Part 2' }
        ],
        total_parts: 2,
        low_stock_parts: 0
      };
      const result = validateInventoryData(apiResponse);
      expect(result).toHaveLength(2);
      expect(result[0]).toEqual({ part_id: '1', part_name: 'Part 1' });
    });

    test('extracts and filters inventory_summary with mixed valid/invalid items', () => {
      const apiResponse = {
        organization_id: 'org-123',
        inventory_summary: [
          { part_id: '1', part_name: 'Part 1' },
          null,
          { part_id: '2', part_name: 'Part 2' },
          'invalid',
          undefined
        ],
        total_parts: 2,
        low_stock_parts: 0
      };
      const result = validateInventoryData(apiResponse);
      expect(result).toHaveLength(2);
      expect(result.map(item => item.part_id)).toEqual(['1', '2']);
    });

    test('returns empty array when inventory_summary is not an array', () => {
      const testCases = [
        { inventory_summary: 'not an array' },
        { inventory_summary: 123 },
        { inventory_summary: true },
        { inventory_summary: null },
        { inventory_summary: undefined },
        { inventory_summary: {} }
      ];

      testCases.forEach(apiResponse => {
        const result = validateInventoryData(apiResponse);
        expect(result).toEqual([]);
      });
    });

    test('returns empty array when inventory_summary is empty array', () => {
      const apiResponse = {
        organization_id: 'org-123',
        inventory_summary: [],
        total_parts: 0
      };
      const result = validateInventoryData(apiResponse);
      expect(result).toEqual([]);
    });

    test('returns empty array for unexpected data types', () => {
      const testCases = [
        'string',
        123,
        true,
        false,
        {},
        { no_inventory_summary: 'data' },
        Symbol('test'),
        new Date(),
        /regex/,
        () => { }
      ];

      testCases.forEach(input => {
        const result = validateInventoryData(input);
        expect(result).toEqual([]);
      });
    });

    test('handles deeply nested or complex objects', () => {
      const complexObject = {
        level1: {
          level2: {
            inventory_summary: [{ part_id: '1', part_name: 'Part 1' }]
          }
        }
      };
      const result = validateInventoryData(complexObject);
      expect(result).toEqual([]);
    });

    test('handles circular references gracefully', () => {
      const circularObj = { inventory_summary: [] };
      circularObj.self = circularObj;

      expect(() => {
        const result = validateInventoryData(circularObj);
        expect(result).toEqual([]);
      }).not.toThrow();
    });
  });

  describe('extractInventoryMetadata - Type Validation', () => {
    test('extracts metadata from valid API response', () => {
      const apiResponse = {
        organization_id: 'org-123',
        total_parts: 10,
        low_stock_parts: 3,
        inventory_summary: []
      };
      const result = extractInventoryMetadata(apiResponse);
      expect(result).toEqual({
        organization_id: 'org-123',
        total_parts: 10,
        low_stock_parts: 3
      });
    });

    test('returns default values for invalid input types', () => {
      const defaultMetadata = {
        total_parts: 0,
        low_stock_parts: 0,
        organization_id: null
      };

      const invalidInputs = [
        null,
        undefined,
        'string',
        123,
        true,
        false,
        [],
        Symbol('test'),
        new Date(),
        /regex/,
        () => { }
      ];

      invalidInputs.forEach(input => {
        expect(extractInventoryMetadata(input)).toEqual(defaultMetadata);
      });
    });

    test('handles partial metadata with strict type validation', () => {
      const testCases = [
        {
          input: { organization_id: 123, total_parts: '10', low_stock_parts: 3 },
          expected: { organization_id: null, total_parts: 0, low_stock_parts: 3 }
        },
        {
          input: { organization_id: 'valid', total_parts: null, low_stock_parts: '5' },
          expected: { organization_id: 'valid', total_parts: 0, low_stock_parts: 0 }
        },
        {
          input: { organization_id: '', total_parts: -1, low_stock_parts: 0 },
          expected: { organization_id: '', total_parts: -1, low_stock_parts: 0 }
        },
        {
          input: { organization_id: 'test', total_parts: 0, low_stock_parts: 0 },
          expected: { organization_id: 'test', total_parts: 0, low_stock_parts: 0 }
        }
      ];

      testCases.forEach(({ input, expected }) => {
        const result = extractInventoryMetadata(input);
        expect(result).toEqual(expected);
      });
    });

    test('handles missing properties gracefully', () => {
      const testCases = [
        {},
        { organization_id: 'test' },
        { total_parts: 5 },
        { low_stock_parts: 2 },
        { organization_id: 'test', total_parts: 10 },
        { organization_id: 'test', low_stock_parts: 3 },
        { total_parts: 8, low_stock_parts: 1 }
      ];

      testCases.forEach(input => {
        const result = extractInventoryMetadata(input);
        expect(result).toHaveProperty('organization_id');
        expect(result).toHaveProperty('total_parts');
        expect(result).toHaveProperty('low_stock_parts');
        expect(typeof result.total_parts).toBe('number');
        expect(typeof result.low_stock_parts).toBe('number');
      });
    });

    test('handles extreme numeric values', () => {
      const extremeValues = [
        { total_parts: Number.MAX_SAFE_INTEGER, low_stock_parts: Number.MIN_SAFE_INTEGER },
        { total_parts: Infinity, low_stock_parts: -Infinity },
        { total_parts: NaN, low_stock_parts: NaN },
        { total_parts: 0, low_stock_parts: 0 },
        { total_parts: -1, low_stock_parts: -1 }
      ];

      extremeValues.forEach(input => {
        const result = extractInventoryMetadata(input);
        // NaN and Infinity should be converted to 0
        if (isNaN(input.total_parts) || !isFinite(input.total_parts)) {
          expect(result.total_parts).toBe(0);
        } else {
          expect(result.total_parts).toBe(input.total_parts);
        }
      });
    });
  });

  describe('isValidArray and isArray', () => {
    test('isValidArray returns true for non-empty arrays', () => {
      expect(isValidArray([1, 2, 3])).toBe(true);
      expect(isValidArray(['a'])).toBe(true);
    });

    test('isValidArray returns false for empty arrays or non-arrays', () => {
      expect(isValidArray([])).toBe(false);
      expect(isValidArray(null)).toBe(false);
      expect(isValidArray('string')).toBe(false);
      expect(isValidArray({})).toBe(false);
    });

    test('isArray returns true for any array', () => {
      expect(isArray([])).toBe(true);
      expect(isArray([1, 2, 3])).toBe(true);
    });

    test('isArray returns false for non-arrays', () => {
      expect(isArray(null)).toBe(false);
      expect(isArray('string')).toBe(false);
      expect(isArray({})).toBe(false);
    });
  });

  describe('safeFilter - Comprehensive Error Handling', () => {
    test('filters array correctly with valid input', () => {
      const input = [1, 2, 3, 4, 5];
      const result = safeFilter(input, x => x > 3);
      expect(result).toEqual([4, 5]);
    });

    test('handles complex filter functions', () => {
      const input = [
        { id: 1, active: true, value: 10 },
        { id: 2, active: false, value: 20 },
        { id: 3, active: true, value: 5 },
        { id: 4, active: true, value: 15 }
      ];
      const result = safeFilter(input, item => item.active && item.value > 10);
      expect(result).toHaveLength(1);
      expect(result[0].id).toBe(4);
    });

    test('returns fallback for various non-array input types', () => {
      const fallback = ['fallback'];
      const nonArrayInputs = [
        'not array',
        123,
        true,
        false,
        null,
        undefined,
        {},
        { length: 3 }, // Object with length property but not array
        Symbol('test'),
        new Date(),
        /regex/,
        () => { }
      ];

      nonArrayInputs.forEach(input => {
        expect(safeFilter(input, x => x > 3, fallback)).toEqual(fallback);
      });
    });

    test('returns original array for invalid filter function types', () => {
      const input = [1, 2, 3];
      const invalidFunctions = [
        'not function',
        123,
        true,
        null,
        undefined,
        {},
        [],
        Symbol('test')
      ];

      invalidFunctions.forEach(invalidFn => {
        expect(safeFilter(input, invalidFn)).toEqual(input);
      });
    });

    test('returns fallback when filter throws various error types', () => {
      const input = [1, 2, 3];
      const fallback = ['error fallback'];

      const errorThrowingFilters = [
        () => { throw new Error('Standard error'); },
        () => { throw new TypeError('Type error'); },
        () => { throw new ReferenceError('Reference error'); },
        () => { throw 'String error'; },
        () => { throw { custom: 'error' }; },
        () => { throw null; },
        () => { throw undefined; }
      ];

      errorThrowingFilters.forEach(throwingFilter => {
        expect(safeFilter(input, throwingFilter, fallback)).toEqual(fallback);
      });
    });

    test('handles empty arrays correctly', () => {
      expect(safeFilter([], x => x > 0)).toEqual([]);
      expect(safeFilter([], x => x > 0, ['fallback'])).toEqual([]);
    });

    test('handles arrays with null/undefined elements', () => {
      const input = [1, null, 3, undefined, 5];
      const result = safeFilter(input, x => x != null);
      expect(result).toEqual([1, 3, 5]);
    });

    test('uses default fallback when none provided', () => {
      expect(safeFilter('not array', x => x > 0)).toEqual([]);
      expect(safeFilter(null, x => x > 0)).toEqual([]);
    });

    test('handles filter functions that return non-boolean values', () => {
      const input = [1, 2, 3, 4, 5];
      // JavaScript filter coerces return values to boolean
      const result = safeFilter(input, x => x % 2); // Returns 0 (falsy) or 1 (truthy)
      expect(result).toEqual([1, 3, 5]); // Odd numbers
    });
  });

  describe('safeMap - Comprehensive Error Handling', () => {
    test('maps array correctly with valid input', () => {
      const input = [1, 2, 3];
      const result = safeMap(input, x => x * 2);
      expect(result).toEqual([2, 4, 6]);
    });

    test('handles complex mapping functions', () => {
      const input = [
        { id: 1, name: 'Part A', price: 10.50 },
        { id: 2, name: 'Part B', price: 25.75 },
        { id: 3, name: 'Part C', price: 5.25 }
      ];
      const result = safeMap(input, item => ({
        ...item,
        displayName: `${item.name} ($${item.price})`,
        discountPrice: item.price * 0.9
      }));

      expect(result).toHaveLength(3);
      expect(result[0].displayName).toBe('Part A ($10.5)');
      expect(result[0].discountPrice).toBeCloseTo(9.45);
    });

    test('returns fallback for various non-array input types', () => {
      const fallback = ['fallback'];
      const nonArrayInputs = [
        'not array',
        123,
        true,
        false,
        null,
        undefined,
        {},
        { 0: 'a', 1: 'b', length: 2 }, // Array-like object
        Symbol('test'),
        new Date(),
        /regex/,
        () => { }
      ];

      nonArrayInputs.forEach(input => {
        expect(safeMap(input, x => x * 2, fallback)).toEqual(fallback);
      });
    });

    test('returns original array for invalid map function types', () => {
      const input = [1, 2, 3];
      const invalidFunctions = [
        'not function',
        123,
        true,
        null,
        undefined,
        {},
        [],
        Symbol('test')
      ];

      invalidFunctions.forEach(invalidFn => {
        expect(safeMap(input, invalidFn)).toEqual(input);
      });
    });

    test('returns fallback when map throws various error types', () => {
      const input = [1, 2, 3];
      const fallback = ['error fallback'];

      const errorThrowingMappers = [
        () => { throw new Error('Standard error'); },
        () => { throw new TypeError('Type error'); },
        (x) => { if (x === 2) throw new Error('Conditional error'); return x; },
        () => { throw 'String error'; },
        () => { throw { custom: 'error' }; }
      ];

      errorThrowingMappers.forEach(throwingMapper => {
        expect(safeMap(input, throwingMapper, fallback)).toEqual(fallback);
      });
    });

    test('handles empty arrays correctly', () => {
      expect(safeMap([], x => x * 2)).toEqual([]);
      expect(safeMap([], x => x * 2, ['fallback'])).toEqual([]);
    });

    test('handles arrays with null/undefined elements', () => {
      const input = [1, null, 3, undefined, 5];
      const result = safeMap(input, x => x != null ? x * 2 : 0);
      expect(result).toEqual([2, 0, 6, 0, 10]);
    });

    test('uses default fallback when none provided', () => {
      expect(safeMap('not array', x => x * 2)).toEqual([]);
      expect(safeMap(null, x => x * 2)).toEqual([]);
    });
  });

  describe('safeReduce', () => {
    test('reduces array correctly with valid input', () => {
      const input = [1, 2, 3, 4];
      const result = safeReduce(input, (acc, val) => acc + val, 0);
      expect(result).toBe(10);
    });

    test('returns fallback for non-array input', () => {
      const fallback = 'fallback';
      expect(safeReduce('not array', (acc, val) => acc + val, 0, fallback)).toBe(fallback);
    });

    test('returns initial value when fallback is null', () => {
      const initialValue = 42;
      expect(safeReduce('not array', (acc, val) => acc + val, initialValue, null)).toBe(initialValue);
    });
  });

  describe('safeFind', () => {
    test('finds element correctly with valid input', () => {
      const input = [{ id: 1 }, { id: 2 }, { id: 3 }];
      const result = safeFind(input, item => item.id === 2);
      expect(result).toEqual({ id: 2 });
    });

    test('returns fallback when element not found', () => {
      const input = [{ id: 1 }, { id: 2 }];
      const fallback = 'not found';
      const result = safeFind(input, item => item.id === 99, fallback);
      expect(result).toBe(fallback);
    });

    test('returns fallback for non-array input', () => {
      const fallback = 'fallback';
      expect(safeFind('not array', item => item.id === 1, fallback)).toBe(fallback);
    });
  });

  describe('safeSort', () => {
    test('sorts array correctly with valid input', () => {
      const input = [3, 1, 4, 1, 5];
      const result = safeSort(input);
      expect(result).toEqual([1, 1, 3, 4, 5]);
    });

    test('sorts with custom compare function', () => {
      const input = [{ value: 3 }, { value: 1 }, { value: 2 }];
      const result = safeSort(input, (a, b) => a.value - b.value);
      expect(result).toEqual([{ value: 1 }, { value: 2 }, { value: 3 }]);
    });

    test('returns fallback for non-array input', () => {
      const fallback = ['fallback'];
      expect(safeSort('not array', null, fallback)).toEqual(fallback);
    });

    test('does not mutate original array', () => {
      const input = [3, 1, 2];
      const result = safeSort(input);
      expect(input).toEqual([3, 1, 2]); // Original unchanged
      expect(result).toEqual([1, 2, 3]); // Result is sorted
    });
  });

  describe('validateInventoryItem', () => {
    test('returns true for valid inventory item', () => {
      const validItem = {
        part_id: 'part-123',
        part_number: 'PN-001',
        part_name: 'Test Part',
        total_stock: 10
      };
      expect(validateInventoryItem(validItem)).toBe(true);
    });

    test('returns false for invalid inventory item', () => {
      expect(validateInventoryItem(null)).toBe(false);
      expect(validateInventoryItem({})).toBe(false);
      expect(validateInventoryItem({ part_id: '' })).toBe(false);
      expect(validateInventoryItem({ part_id: 'id', part_number: '' })).toBe(false);
    });

    test('returns false for missing required fields', () => {
      const incompleteItem = {
        part_id: 'part-123',
        part_number: 'PN-001'
        // missing part_name
      };
      expect(validateInventoryItem(incompleteItem)).toBe(false);
    });
  });

  describe('sanitizeInventoryItems', () => {
    test('filters out invalid items', () => {
      const input = [
        { part_id: '1', part_number: 'PN-1', part_name: 'Part 1' },
        null,
        { part_id: '2', part_number: 'PN-2', part_name: 'Part 2' },
        { part_id: '', part_number: 'PN-3', part_name: 'Part 3' },
        { part_id: '4', part_number: 'PN-4', part_name: 'Part 4' }
      ];
      const result = sanitizeInventoryItems(input);
      expect(result).toHaveLength(3);
      expect(result.map(item => item.part_id)).toEqual(['1', '2', '4']);
    });

    test('returns empty array for non-array input', () => {
      expect(sanitizeInventoryItems('not array')).toEqual([]);
      expect(sanitizeInventoryItems(null)).toEqual([]);
    });
  });

  describe('createSafeInventoryResult', () => {
    test('creates safe result from valid API response', () => {
      const apiResponse = {
        organization_id: 'org-123',
        inventory_summary: [
          { part_id: '1', part_number: 'PN-1', part_name: 'Part 1' },
          { part_id: '2', part_number: 'PN-2', part_name: 'Part 2' }
        ],
        total_parts: 2,
        low_stock_parts: 1
      };
      const result = createSafeInventoryResult(apiResponse);

      expect(result.inventory).toHaveLength(2);
      expect(result.metadata.organization_id).toBe('org-123');
      expect(result.metadata.total_parts).toBe(2);
      expect(result.hasData).toBe(true);
      expect(result.isValid).toBe(true);
    });

    test('creates safe result from invalid API response', () => {
      const result = createSafeInventoryResult(null);

      expect(result.inventory).toEqual([]);
      expect(result.metadata.organization_id).toBe(null);
      expect(result.metadata.total_parts).toBe(0);
      expect(result.hasData).toBe(false);
      expect(result.isValid).toBe(true);
    });
  });

  describe('logInventoryValidation', () => {
    test('logs validation information without errors', () => {
      const originalData = { inventory_summary: [{ part_id: '1' }] };
      const validatedData = [{ part_id: '1' }];

      expect(() => {
        logInventoryValidation(originalData, validatedData, 'test context');
      }).not.toThrow();

      expect(console.group).toHaveBeenCalled();
      expect(console.log).toHaveBeenCalled();
      expect(console.groupEnd).toHaveBeenCalled();
    });
  });
});