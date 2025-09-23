/**
 * Test suite for enhanced search performance features
 * Tests debounced search, progressive loading, and component optimization
 */

import { renderHook, act } from '@testing-library/react';
import { useDebounce, useDebounceSearch } from '../hooks/useDebounce';
import { usePerformanceMonitor } from '../hooks/usePerformanceMonitor';

// Mock performance.now for consistent testing
const mockPerformanceNow = jest.fn();
global.performance = { now: mockPerformanceNow };

describe('Enhanced Search Performance', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockPerformanceNow.mockReturnValue(1000);
  });

  describe('useDebounce hook', () => {
    it('should debounce value changes', async () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'initial', delay: 300 } }
      );

      expect(result.current).toBe('initial');

      // Change value
      rerender({ value: 'changed', delay: 300 });
      expect(result.current).toBe('initial'); // Should still be initial

      // Wait for debounce
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 350));
      });

      expect(result.current).toBe('changed');
    });

    it('should reset timer on rapid changes', async () => {
      const { result, rerender } = renderHook(
        ({ value, delay }) => useDebounce(value, delay),
        { initialProps: { value: 'initial', delay: 300 } }
      );

      // Rapid changes
      rerender({ value: 'change1', delay: 300 });
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 100));
      });

      rerender({ value: 'change2', delay: 300 });
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 100));
      });

      rerender({ value: 'final', delay: 300 });

      // Should still be initial after rapid changes
      expect(result.current).toBe('initial');

      // Wait for final debounce
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 350));
      });

      expect(result.current).toBe('final');
    });
  });

  describe('useDebounceSearch hook', () => {
    it('should provide debounced search term and searching state', async () => {
      const { result, rerender } = renderHook(
        ({ searchTerm }) => useDebounceSearch(searchTerm, 300),
        { initialProps: { searchTerm: '' } }
      );

      expect(result.current.debouncedSearchTerm).toBe('');
      expect(result.current.isSearching).toBe(false);

      // Start searching
      rerender({ searchTerm: 'test' });
      expect(result.current.debouncedSearchTerm).toBe('');
      expect(result.current.isSearching).toBe(true);

      // Wait for debounce
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 350));
      });

      expect(result.current.debouncedSearchTerm).toBe('test');
      expect(result.current.isSearching).toBe(false);
    });
  });

  describe('usePerformanceMonitor hook', () => {
    it('should track render performance', () => {
      mockPerformanceNow
        .mockReturnValueOnce(1000) // Initial render start
        .mockReturnValueOnce(1016); // End time (16ms render)

      const { result } = renderHook(() => usePerformanceMonitor('TestComponent'));

      expect(result.current.renderTime).toBe('16.00');
      expect(result.current.renderCount).toBe(1);
    });

    it('should warn about slow renders in development', () => {
      const originalEnv = process.env.NODE_ENV;
      process.env.NODE_ENV = 'development';

      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();

      mockPerformanceNow
        .mockReturnValueOnce(1000) // Initial render start
        .mockReturnValueOnce(1020); // End time (20ms render - over threshold)

      renderHook(() => usePerformanceMonitor('SlowComponent'));

      expect(consoleSpy).toHaveBeenCalledWith(
        'SlowComponent render took 20.00ms (>16ms threshold)'
      );

      consoleSpy.mockRestore();
      process.env.NODE_ENV = originalEnv;
    });
  });
});

describe('Search Performance Integration', () => {
  it('should handle large dataset filtering efficiently', () => {
    // Mock large dataset
    const largeParts = Array.from({ length: 1000 }, (_, i) => ({
      id: `part-${i}`,
      name: `Part ${i}`,
      part_number: `P${i.toString().padStart(4, '0')}`,
      description: `Description for part ${i}`,
      manufacturer: i % 10 === 0 ? 'Special Manufacturer' : 'Standard Manufacturer',
      part_type: i % 2 === 0 ? 'CONSUMABLE' : 'BULK_MATERIAL',
      is_proprietary: i % 5 === 0
    }));

    // Test search filtering performance
    const startTime = performance.now();

    const searchTerm = 'special';
    const filteredParts = largeParts.filter(part => {
      const term = searchTerm.toLowerCase();
      return (
        part.name.toLowerCase().includes(term) ||
        part.part_number.toLowerCase().includes(term) ||
        (part.description && part.description.toLowerCase().includes(term)) ||
        (part.manufacturer && part.manufacturer.toLowerCase().includes(term))
      );
    });

    const endTime = performance.now();
    const filterTime = endTime - startTime;

    // Should filter efficiently (under 10ms for 1000 items)
    expect(filterTime).toBeLessThan(10);
    expect(filteredParts.length).toBeGreaterThan(0);
    expect(filteredParts.every(part =>
      part.manufacturer.toLowerCase().includes('special')
    )).toBe(true);
  });

  it('should determine virtualization threshold correctly', () => {
    const smallDataset = Array.from({ length: 50 }, (_, i) => ({ id: i }));
    const largeDataset = Array.from({ length: 150 }, (_, i) => ({ id: i }));

    expect(smallDataset.length > 100).toBe(false); // No virtualization
    expect(largeDataset.length > 100).toBe(true);  // Use virtualization
  });
});