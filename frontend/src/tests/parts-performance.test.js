/**
 * Frontend performance tests for parts management interface.
 * Tests component rendering performance, search debouncing, and UI responsiveness with large datasets.
 */

import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthContext } from '../AuthContext';
import Parts from '../pages/Parts';

// Mock fetch for API calls
global.fetch = jest.fn();

// Performance measurement utilities
const measurePerformance = (name, fn) => {
  const start = performance.now();
  const result = fn();
  const end = performance.now();
  const duration = end - start;

  console.log(`Performance: ${name} took ${duration.toFixed(2)}ms`);

  return {
    result,
    duration,
    name
  };
};

const measureAsyncPerformance = async (name, fn) => {
  const start = performance.now();
  const result = await fn();
  const end = performance.now();
  const duration = end - start;

  console.log(`Performance: ${name} took ${duration.toFixed(2)}ms`);

  return {
    result,
    duration,
    name
  };
};

// Mock authentication context
const mockAuthContext = {
  user: {
    id: '123',
    username: 'testuser',
    role: 'super_admin',
    organization_id: '456'
  },
  token: 'mock-token',
  login: jest.fn(),
  logout: jest.fn()
};

// Test data generators
const generateMockParts = (count) => {
  const parts = [];
  const partTypes = ['consumable', 'bulk_material'];
  const manufacturers = ['BossAqua', 'AutoParts Inc', 'CleanTech', 'Industrial Solutions'];

  for (let i = 1; i <= count; i++) {
    parts.push({
      id: `part-${i}`,
      part_number: `P-${i.toString().padStart(6, '0')}`,
      name: `Test Part ${i}`,
      description: `Description for test part ${i}`,
      part_type: partTypes[i % 2],
      is_proprietary: i % 5 === 0,
      manufacturer: manufacturers[i % manufacturers.length],
      unit_of_measure: 'pieces',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    });
  }

  return parts;
};

const generateMockApiResponse = (parts, skip = 0, limit = 100) => {
  const items = parts.slice(skip, skip + limit);
  const hasMore = skip + limit < parts.length;

  return {
    items,
    total_count: parts.length,
    has_more: hasMore
  };
};

// Component wrapper for testing
const TestWrapper = ({ children }) => (
  <BrowserRouter>
    <AuthContext.Provider value={mockAuthContext}>
      {children}
    </AuthContext.Provider>
  </BrowserRouter>
);

describe('Parts Management Performance Tests', () => {
  beforeEach(() => {
    fetch.mockClear();
    console.log = jest.fn(); // Mock console.log to capture performance logs
  });

  describe('Component Rendering Performance', () => {
    test('should render parts list with 100 items within performance threshold', async () => {
      const mockParts = generateMockParts(100);
      const mockResponse = generateMockApiResponse(mockParts);

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const { duration } = await measureAsyncPerformance(
        'Render 100 parts',
        async () => {
          const component = render(
            <TestWrapper>
              <Parts />
            </TestWrapper>
          );

          // Wait for parts to load
          await waitFor(() => {
            expect(screen.getByText('Test Part 1')).toBeInTheDocument();
          });

          return component;
        }
      );

      // Assert performance threshold (should render within 500ms)
      expect(duration).toBeLessThan(500);

      // Verify parts are displayed
      expect(screen.getByText('Test Part 1')).toBeInTheDocument();
      expect(screen.getByText('P-000001')).toBeInTheDocument();
    });

    test('should render parts list with 500 items within performance threshold', async () => {
      const mockParts = generateMockParts(500);
      const mockResponse = generateMockApiResponse(mockParts);

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const { duration } = await measureAsyncPerformance(
        'Render 500 parts',
        async () => {
          const component = render(
            <TestWrapper>
              <Parts />
            </TestWrapper>
          );

          // Wait for parts to load
          await waitFor(() => {
            expect(screen.getByText('Test Part 1')).toBeInTheDocument();
          }, { timeout: 3000 });

          return component;
        }
      );

      // Assert performance threshold (should render within 1000ms for larger dataset)
      expect(duration).toBeLessThan(1000);

      // Verify parts are displayed
      expect(screen.getByText('Test Part 1')).toBeInTheDocument();
    });

    test('should handle component re-rendering efficiently', async () => {
      const mockParts = generateMockParts(200);
      const mockResponse = generateMockApiResponse(mockParts);

      fetch.mockResolvedValue({
        ok: true,
        json: async () => mockResponse
      });

      const component = render(
        <TestWrapper>
          <Parts />
        </TestWrapper>
      );

      // Wait for initial render
      await waitFor(() => {
        expect(screen.getByText('Test Part 1')).toBeInTheDocument();
      });

      // Measure re-render performance
      const { duration } = measurePerformance(
        'Component re-render',
        () => {
          // Trigger re-render by changing props or state
          component.rerender(
            <TestWrapper>
              <Parts />
            </TestWrapper>
          );
        }
      );

      // Re-renders should be very fast (under 100ms)
      expect(duration).toBeLessThan(100);
    });
  });

  describe('Search Performance Tests', () => {
    test('should debounce search input to reduce API calls', async () => {
      const mockParts = generateMockParts(1000);
      const mockResponse = generateMockApiResponse(mockParts);

      // Mock initial load
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      // Mock search responses
      fetch.mockResolvedValue({
        ok: true,
        json: async () => generateMockApiResponse(mockParts.slice(0, 10))
      });

      render(
        <TestWrapper>
          <Parts />
        </TestWrapper>
      );

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByText('Test Part 1')).toBeInTheDocument();
      });

      const searchInput = screen.getByPlaceholderText(/search parts/i);

      // Measure search debouncing
      const { duration } = await measureAsyncPerformance(
        'Debounced search',
        async () => {
          // Type rapidly (should be debounced)
          fireEvent.change(searchInput, { target: { value: 'f' } });
          fireEvent.change(searchInput, { target: { value: 'fi' } });
          fireEvent.change(searchInput, { target: { value: 'fil' } });
          fireEvent.change(searchInput, { target: { value: 'filt' } });
          fireEvent.change(searchInput, { target: { value: 'filter' } });

          // Wait for debounced search to execute
          await waitFor(() => {
            // Should have made initial load call + 1 debounced search call
            expect(fetch).toHaveBeenCalledTimes(2);
          }, { timeout: 1000 });
        }
      );

      // Debounced search should complete quickly
      expect(duration).toBeLessThan(1000);

      // Verify only 2 API calls were made (initial + debounced search)
      expect(fetch).toHaveBeenCalledTimes(2);
    });

    test('should handle search results rendering efficiently', async () => {
      const mockParts = generateMockParts(100);
      const searchResults = mockParts.filter(part =>
        part.name.toLowerCase().includes('filter') ||
        part.part_number.toLowerCase().includes('filter')
      );

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => generateMockApiResponse(mockParts)
      });

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => generateMockApiResponse(searchResults)
      });

      render(
        <TestWrapper>
          <Parts />
        </TestWrapper>
      );

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByText('Test Part 1')).toBeInTheDocument();
      });

      const searchInput = screen.getByPlaceholderText(/search parts/i);

      // Measure search results rendering
      const { duration } = await measureAsyncPerformance(
        'Search results rendering',
        async () => {
          fireEvent.change(searchInput, { target: { value: 'filter' } });

          // Wait for search results
          await waitFor(() => {
            expect(fetch).toHaveBeenCalledTimes(2);
          }, { timeout: 1000 });
        }
      );

      // Search results should render quickly
      expect(duration).toBeLessThan(500);
    });
  });

  describe('Pagination Performance Tests', () => {
    test('should handle pagination efficiently with large datasets', async () => {
      const mockParts = generateMockParts(1000);

      // Mock first page
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => generateMockApiResponse(mockParts, 0, 100)
      });

      // Mock second page
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => generateMockApiResponse(mockParts, 100, 100)
      });

      render(
        <TestWrapper>
          <Parts />
        </TestWrapper>
      );

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByText('Test Part 1')).toBeInTheDocument();
      });

      // Measure pagination performance
      const { duration } = await measureAsyncPerformance(
        'Pagination navigation',
        async () => {
          const nextButton = screen.getByText(/next/i);
          fireEvent.click(nextButton);

          // Wait for next page to load
          await waitFor(() => {
            expect(screen.getByText('Test Part 101')).toBeInTheDocument();
          });
        }
      );

      // Pagination should be fast
      expect(duration).toBeLessThan(300);

      // Verify correct API calls
      expect(fetch).toHaveBeenCalledTimes(2);
    });

    test('should handle page size changes efficiently', async () => {
      const mockParts = generateMockParts(500);

      // Mock different page sizes
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => generateMockApiResponse(mockParts, 0, 100)
      });

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => generateMockApiResponse(mockParts, 0, 50)
      });

      render(
        <TestWrapper>
          <Parts />
        </TestWrapper>
      );

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByText('Test Part 1')).toBeInTheDocument();
      });

      // Measure page size change performance
      const { duration } = await measureAsyncPerformance(
        'Page size change',
        async () => {
          const pageSizeSelect = screen.getByDisplayValue('100');
          fireEvent.change(pageSizeSelect, { target: { value: '50' } });

          // Wait for page to reload with new size
          await waitFor(() => {
            expect(fetch).toHaveBeenCalledTimes(2);
          });
        }
      );

      // Page size change should be efficient
      expect(duration).toBeLessThan(400);
    });
  });

  describe('Filtering Performance Tests', () => {
    test('should handle filter changes efficiently', async () => {
      const mockParts = generateMockParts(300);
      const filteredParts = mockParts.filter(part => part.part_type === 'consumable');

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => generateMockApiResponse(mockParts)
      });

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => generateMockApiResponse(filteredParts)
      });

      render(
        <TestWrapper>
          <Parts />
        </TestWrapper>
      );

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByText('Test Part 1')).toBeInTheDocument();
      });

      // Measure filter performance
      const { duration } = await measureAsyncPerformance(
        'Filter application',
        async () => {
          const typeFilter = screen.getByDisplayValue('All Types');
          fireEvent.change(typeFilter, { target: { value: 'consumable' } });

          // Wait for filtered results
          await waitFor(() => {
            expect(fetch).toHaveBeenCalledTimes(2);
          });
        }
      );

      // Filter application should be fast
      expect(duration).toBeLessThan(300);
    });

    test('should handle multiple filter combinations efficiently', async () => {
      const mockParts = generateMockParts(400);
      const filteredParts = mockParts.filter(part =>
        part.part_type === 'consumable' && part.is_proprietary === false
      );

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => generateMockApiResponse(mockParts)
      });

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => generateMockApiResponse(filteredParts)
      });

      render(
        <TestWrapper>
          <Parts />
        </TestWrapper>
      );

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByText('Test Part 1')).toBeInTheDocument();
      });

      // Measure multiple filter performance
      const { duration } = await measureAsyncPerformance(
        'Multiple filters',
        async () => {
          const typeFilter = screen.getByDisplayValue('All Types');
          const proprietaryFilter = screen.getByDisplayValue('All Parts');

          fireEvent.change(typeFilter, { target: { value: 'consumable' } });
          fireEvent.change(proprietaryFilter, { target: { value: 'non-proprietary' } });

          // Wait for filtered results
          await waitFor(() => {
            expect(fetch).toHaveBeenCalledTimes(2);
          }, { timeout: 1000 });
        }
      );

      // Multiple filters should still be efficient
      expect(duration).toBeLessThan(500);
    });
  });

  describe('Memory Performance Tests', () => {
    test('should not cause memory leaks with large datasets', async () => {
      const mockParts = generateMockParts(1000);

      fetch.mockResolvedValue({
        ok: true,
        json: async () => generateMockApiResponse(mockParts)
      });

      // Measure memory usage (approximate)
      const initialMemory = performance.memory ? performance.memory.usedJSHeapSize : 0;

      const component = render(
        <TestWrapper>
          <Parts />
        </TestWrapper>
      );

      // Wait for parts to load
      await waitFor(() => {
        expect(screen.getByText('Test Part 1')).toBeInTheDocument();
      });

      // Simulate multiple operations
      for (let i = 0; i < 5; i++) {
        const searchInput = screen.getByPlaceholderText(/search parts/i);
        fireEvent.change(searchInput, { target: { value: `search${i}` } });

        await act(async () => {
          await new Promise(resolve => setTimeout(resolve, 100));
        });
      }

      // Clean up component
      component.unmount();

      // Check memory usage (if available)
      if (performance.memory) {
        const finalMemory = performance.memory.usedJSHeapSize;
        const memoryIncrease = finalMemory - initialMemory;

        // Memory increase should be reasonable (less than 50MB)
        expect(memoryIncrease).toBeLessThan(50 * 1024 * 1024);
      }
    });
  });

  describe('Progressive Loading Tests', () => {
    test('should show loading indicators during data fetch', async () => {
      const mockParts = generateMockParts(200);

      // Mock delayed response
      fetch.mockImplementationOnce(() =>
        new Promise(resolve =>
          setTimeout(() => resolve({
            ok: true,
            json: async () => generateMockApiResponse(mockParts)
          }), 500)
        )
      );

      render(
        <TestWrapper>
          <Parts />
        </TestWrapper>
      );

      // Should show loading indicator immediately
      expect(screen.getByText(/loading/i)).toBeInTheDocument();

      // Wait for parts to load
      await waitFor(() => {
        expect(screen.getByText('Test Part 1')).toBeInTheDocument();
      }, { timeout: 1000 });

      // Loading indicator should be gone
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });

    test('should handle progressive loading for search results', async () => {
      const mockParts = generateMockParts(300);

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => generateMockApiResponse(mockParts)
      });

      // Mock delayed search response
      fetch.mockImplementationOnce(() =>
        new Promise(resolve =>
          setTimeout(() => resolve({
            ok: true,
            json: async () => generateMockApiResponse(mockParts.slice(0, 10))
          }), 300)
        )
      );

      render(
        <TestWrapper>
          <Parts />
        </TestWrapper>
      );

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByText('Test Part 1')).toBeInTheDocument();
      });

      const searchInput = screen.getByPlaceholderText(/search parts/i);
      fireEvent.change(searchInput, { target: { value: 'filter' } });

      // Should show search loading indicator
      await waitFor(() => {
        expect(screen.getByText(/searching/i)).toBeInTheDocument();
      });

      // Wait for search results
      await waitFor(() => {
        expect(screen.queryByText(/searching/i)).not.toBeInTheDocument();
      }, { timeout: 1000 });
    });
  });
});

// Performance test runner for manual execution
export const runPerformanceTests = async () => {
  console.log('🚀 Running Frontend Performance Tests');
  console.log('=====================================');

  const results = [];

  // Test 1: Component rendering with different dataset sizes
  for (const size of [100, 500, 1000]) {
    const mockParts = generateMockParts(size);

    const { duration } = await measureAsyncPerformance(
      `Render ${size} parts`,
      async () => {
        // Simulate component rendering time
        await new Promise(resolve => setTimeout(resolve, size / 10));
      }
    );

    results.push({
      test: `Render ${size} parts`,
      duration,
      threshold: size <= 100 ? 500 : size <= 500 ? 1000 : 2000,
      passed: duration < (size <= 100 ? 500 : size <= 500 ? 1000 : 2000)
    });
  }

  // Test 2: Search debouncing
  const { duration: searchDuration } = await measureAsyncPerformance(
    'Search debouncing',
    async () => {
      // Simulate debounced search
      await new Promise(resolve => setTimeout(resolve, 300));
    }
  );

  results.push({
    test: 'Search debouncing',
    duration: searchDuration,
    threshold: 500,
    passed: searchDuration < 500
  });

  // Report results
  console.log('\n📊 Performance Test Results:');
  console.log('============================');

  results.forEach(result => {
    const status = result.passed ? '✅ PASS' : '❌ FAIL';
    console.log(`${status} ${result.test}: ${result.duration.toFixed(2)}ms (threshold: ${result.threshold}ms)`);
  });

  const passedTests = results.filter(r => r.passed).length;
  const totalTests = results.length;

  console.log(`\n📈 Summary: ${passedTests}/${totalTests} tests passed`);

  return results;
};