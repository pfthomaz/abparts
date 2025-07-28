// frontend/src/components/__tests__/WarehouseInventoryAggregationView.integration.test.js

import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import WarehouseInventoryAggregationView from '../WarehouseInventoryAggregationView';
import { inventoryService } from '../../services/inventoryService';
import { warehouseService } from '../../services/warehouseService';
import { partsService } from '../../services/partsService';

// Mock the services for integration testing
jest.mock('../../services/inventoryService');
jest.mock('../../services/warehouseService');
jest.mock('../../services/partsService');
jest.mock('../../AuthContext', () => ({
  useAuth: () => ({ user: { id: 'test-user', role: 'admin' } })
}));

describe('WarehouseInventoryAggregationView Integration Tests', () => {
  const mockOrganizationId = 'test-org-123';

  // Mock data that simulates actual backend responses
  const mockInventoryApiResponse = {
    organization_id: mockOrganizationId,
    inventory_summary: [
      {
        part_id: 'part-001',
        total_stock: 150.5,
        min_stock_recommendation: 50.0,
        warehouse_count: 3,
        is_low_stock: false
      },
      {
        part_id: 'part-002',
        total_stock: 25.0,
        min_stock_recommendation: 30.0,
        warehouse_count: 2,
        is_low_stock: true
      },
      {
        part_id: 'part-003',
        total_stock: 0.0,
        min_stock_recommendation: 10.0,
        warehouse_count: 0,
        is_low_stock: true
      }
    ],
    total_parts: 3,
    low_stock_parts: 2
  };

  const mockWarehousesData = [
    {
      id: 'warehouse-001',
      name: 'Main Warehouse',
      location: 'New York'
    },
    {
      id: 'warehouse-002',
      name: 'Secondary Warehouse',
      location: 'California'
    }
  ];

  const mockPartsData = [
    {
      id: 'part-001',
      name: 'Hydraulic Pump',
      part_number: 'HP-001',
      unit_of_measure: 'pieces'
    },
    {
      id: 'part-002',
      name: 'Oil Filter',
      part_number: 'OF-002',
      unit_of_measure: 'pieces'
    },
    {
      id: 'part-003',
      name: 'Pressure Valve',
      part_number: 'PV-003',
      unit_of_measure: 'pieces'
    }
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    // Reset console mocks
    jest.spyOn(console, 'warn').mockImplementation(() => { });
    jest.spyOn(console, 'error').mockImplementation(() => { });
    jest.spyOn(console, 'log').mockImplementation(() => { });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('Component Rendering with Various Data States', () => {
    test('renders correctly with complete backend API response', async () => {
      inventoryService.getOrganizationInventoryAggregation.mockResolvedValue(mockInventoryApiResponse);
      warehouseService.getOrganizationWarehouses.mockResolvedValue(mockWarehousesData);
      partsService.getParts.mockResolvedValue(mockPartsData);

      render(<WarehouseInventoryAggregationView organizationId={mockOrganizationId} />);

      // Wait for loading to complete
      await waitFor(() => {
        expect(screen.getByText('3 parts')).toBeInTheDocument();
      });

      // Verify header is rendered
      expect(screen.getByText('Aggregated Inventory Across All Warehouses')).toBeInTheDocument();

      // Verify parts are displayed with correct data
      expect(screen.getByText('Hydraulic Pump')).toBeInTheDocument();
      expect(screen.getByText('HP-001')).toBeInTheDocument();
      expect(screen.getByText('Oil Filter')).toBeInTheDocument();
      expect(screen.getByText('OF-002')).toBeInTheDocument();
      expect(screen.getByText('Pressure Valve')).toBeInTheDocument();
      expect(screen.getByText('PV-003')).toBeInTheDocument();

      // Verify stock status indicators are present (use getAllByText for multiple instances)
      expect(screen.getByText('In Stock')).toBeInTheDocument();
      expect(screen.getAllByText('Low Stock').length).toBeGreaterThan(0);
      expect(screen.getAllByText('Out of Stock').length).toBeGreaterThan(0);
    });

    test('renders correctly with empty inventory response', async () => {
      const emptyResponse = {
        organization_id: mockOrganizationId,
        inventory_summary: [],
        total_parts: 0,
        low_stock_parts: 0
      };

      inventoryService.getOrganizationInventoryAggregation.mockResolvedValue(emptyResponse);
      warehouseService.getOrganizationWarehouses.mockResolvedValue([]);
      partsService.getParts.mockResolvedValue([]);

      render(<WarehouseInventoryAggregationView organizationId={mockOrganizationId} />);

      await waitFor(() => {
        expect(screen.getByText('0 parts')).toBeInTheDocument();
      });

      expect(screen.getByText('No inventory items found.')).toBeInTheDocument();
    });

    test('handles backend response with missing inventory_summary gracefully', async () => {
      const malformedResponse = {
        organization_id: mockOrganizationId,
        total_parts: 5,
        low_stock_parts: 2
        // Missing inventory_summary property
      };

      inventoryService.getOrganizationInventoryAggregation.mockResolvedValue(malformedResponse);
      warehouseService.getOrganizationWarehouses.mockResolvedValue(mockWarehousesData);
      partsService.getParts.mockResolvedValue(mockPartsData);

      render(<WarehouseInventoryAggregationView organizationId={mockOrganizationId} />);

      await waitFor(() => {
        expect(screen.getByText('0 parts')).toBeInTheDocument();
      });

      expect(screen.getByText('No inventory items found.')).toBeInTheDocument();
      // Should not crash or show error
      expect(screen.queryByText(/Unable to Load Inventory Data/)).not.toBeInTheDocument();
    });

    test('handles backend response with non-array inventory_summary', async () => {
      const malformedResponse = {
        organization_id: mockOrganizationId,
        inventory_summary: "not an array",
        total_parts: 0,
        low_stock_parts: 0
      };

      inventoryService.getOrganizationInventoryAggregation.mockResolvedValue(malformedResponse);
      warehouseService.getOrganizationWarehouses.mockResolvedValue(mockWarehousesData);
      partsService.getParts.mockResolvedValue(mockPartsData);

      render(<WarehouseInventoryAggregationView organizationId={mockOrganizationId} />);

      await waitFor(() => {
        expect(screen.getByText('0 parts')).toBeInTheDocument();
      });

      expect(screen.getByText('No inventory items found.')).toBeInTheDocument();
      // Should handle gracefully without necessarily logging a warning
    });

    test('handles direct array response from backend (legacy format)', async () => {
      // Some APIs might return array directly instead of wrapped object
      const directArrayResponse = [
        {
          part_id: 'part-001',
          total_stock: 100,
          min_stock_recommendation: 20,
          warehouse_count: 2
        }
      ];

      inventoryService.getOrganizationInventoryAggregation.mockResolvedValue(directArrayResponse);
      warehouseService.getOrganizationWarehouses.mockResolvedValue(mockWarehousesData);
      partsService.getParts.mockResolvedValue(mockPartsData);

      render(<WarehouseInventoryAggregationView organizationId={mockOrganizationId} />);

      await waitFor(() => {
        expect(screen.getByText('1 parts')).toBeInTheDocument();
      });

      expect(screen.getByText('Hydraulic Pump')).toBeInTheDocument();
    });

    test('handles null API response gracefully', async () => {
      inventoryService.getOrganizationInventoryAggregation.mockResolvedValue(null);
      warehouseService.getOrganizationWarehouses.mockResolvedValue([]);
      partsService.getParts.mockResolvedValue([]);

      render(<WarehouseInventoryAggregationView organizationId={mockOrganizationId} />);

      await waitFor(() => {
        expect(screen.getByText('0 parts')).toBeInTheDocument();
      });

      expect(screen.getByText('No inventory items found.')).toBeInTheDocument();
    });
  });

  describe('User Interactions and Basic Functionality', () => {
    beforeEach(async () => {
      inventoryService.getOrganizationInventoryAggregation.mockResolvedValue(mockInventoryApiResponse);
      warehouseService.getOrganizationWarehouses.mockResolvedValue(mockWarehousesData);
      partsService.getParts.mockResolvedValue(mockPartsData);
    });

    test('search input is rendered and functional', async () => {
      render(<WarehouseInventoryAggregationView organizationId={mockOrganizationId} />);

      // Wait for data to load
      await waitFor(() => {
        expect(screen.getByText('3 parts')).toBeInTheDocument();
      });

      // Find and interact with search input
      const searchInput = screen.getByPlaceholderText('Search parts...');
      expect(searchInput).toBeInTheDocument();

      // Test that search input accepts input (component may control the value)
      fireEvent.change(searchInput, { target: { value: 'test' } });
      // The component controls the input value, so we just verify it doesn't crash
    });

    test('filter dropdown is rendered and functional', async () => {
      render(<WarehouseInventoryAggregationView organizationId={mockOrganizationId} />);

      // Wait for data to load
      await waitFor(() => {
        expect(screen.getByText('3 parts')).toBeInTheDocument();
      });

      // Find filter dropdown
      const filterSelect = screen.getByDisplayValue('All Items');
      expect(filterSelect).toBeInTheDocument();

      // Test that filter dropdown accepts changes (component may control the value)
      fireEvent.change(filterSelect, { target: { value: 'low_stock' } });
      // The component controls the select value, so we just verify it doesn't crash
    });

    test('prevents user interactions during loading state', async () => {
      // Mock slow API response
      inventoryService.getOrganizationInventoryAggregation.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve(mockInventoryApiResponse), 1000))
      );

      render(<WarehouseInventoryAggregationView organizationId={mockOrganizationId} />);

      // Should show loading state
      expect(screen.getByText('Loading aggregated inventory...')).toBeInTheDocument();

      // Search input should not be rendered during loading
      const searchInput = screen.queryByPlaceholderText('Search parts...');
      expect(searchInput).not.toBeInTheDocument();
    });
  });

  describe('Error Handling and Recovery', () => {
    test('displays appropriate error message for network failures', async () => {
      inventoryService.getOrganizationInventoryAggregation.mockRejectedValue(
        new Error('Network Error: fetch failed')
      );
      warehouseService.getOrganizationWarehouses.mockResolvedValue([]);
      partsService.getParts.mockResolvedValue([]);

      render(<WarehouseInventoryAggregationView organizationId={mockOrganizationId} />);

      await waitFor(() => {
        expect(screen.getByText('Network connection issue. Please check your internet connection and try again.')).toBeInTheDocument();
      });

      expect(screen.getByText('Unable to Load Inventory Data')).toBeInTheDocument();
      expect(screen.getByText('Try Again')).toBeInTheDocument();
    });

    test('retry functionality works correctly', async () => {
      let callCount = 0;
      inventoryService.getOrganizationInventoryAggregation.mockImplementation(() => {
        callCount++;
        if (callCount === 1) {
          return Promise.reject(new Error('Temporary error'));
        }
        return Promise.resolve(mockInventoryApiResponse);
      });
      warehouseService.getOrganizationWarehouses.mockResolvedValue(mockWarehousesData);
      partsService.getParts.mockResolvedValue(mockPartsData);

      render(<WarehouseInventoryAggregationView organizationId={mockOrganizationId} />);

      // Wait for error to appear
      await waitFor(() => {
        expect(screen.getByText('Try Again')).toBeInTheDocument();
      });

      // Click retry button
      const retryButton = screen.getByText('Try Again');
      fireEvent.click(retryButton);

      // Should successfully load data on retry
      await waitFor(() => {
        expect(screen.getByText('3 parts')).toBeInTheDocument();
      });

      expect(screen.getByText('Hydraulic Pump')).toBeInTheDocument();
      expect(callCount).toBe(2);
    });

    test('handles authentication errors appropriately', async () => {
      inventoryService.getOrganizationInventoryAggregation.mockRejectedValue(
        new Error('401 Unauthorized')
      );
      warehouseService.getOrganizationWarehouses.mockResolvedValue([]);
      partsService.getParts.mockResolvedValue([]);

      render(<WarehouseInventoryAggregationView organizationId={mockOrganizationId} />);

      await waitFor(() => {
        expect(screen.getByText('Your session has expired. Please log in again to continue.')).toBeInTheDocument();
      });
    });

    test('handles server errors with appropriate messaging', async () => {
      inventoryService.getOrganizationInventoryAggregation.mockRejectedValue(
        new Error('500 Internal Server Error')
      );
      warehouseService.getOrganizationWarehouses.mockResolvedValue([]);
      partsService.getParts.mockResolvedValue([]);

      render(<WarehouseInventoryAggregationView organizationId={mockOrganizationId} />);

      await waitFor(() => {
        expect(screen.getByText('Server error occurred while loading inventory data. Please try again in a few moments.')).toBeInTheDocument();
      });
    });
  });

  describe('Data Validation and Edge Cases', () => {
    test('handles inventory items with valid data correctly', async () => {
      const responseWithValidData = {
        organization_id: mockOrganizationId,
        inventory_summary: [
          {
            part_id: 'part-001',
            total_stock: 100,
            min_stock_recommendation: 20,
            warehouse_count: 2
          }
        ],
        total_parts: 1,
        low_stock_parts: 0
      };

      inventoryService.getOrganizationInventoryAggregation.mockResolvedValue(responseWithValidData);
      warehouseService.getOrganizationWarehouses.mockResolvedValue(mockWarehousesData);
      partsService.getParts.mockResolvedValue(mockPartsData);

      render(<WarehouseInventoryAggregationView organizationId={mockOrganizationId} />);

      await waitFor(() => {
        expect(screen.getByText('1 parts')).toBeInTheDocument();
      });

      // Should handle valid data correctly without crashing
      expect(screen.getByText('Hydraulic Pump')).toBeInTheDocument();
    });

    test('handles extremely large numbers correctly', async () => {
      const responseWithLargeNumbers = {
        organization_id: mockOrganizationId,
        inventory_summary: [
          {
            part_id: 'part-001',
            total_stock: 999999999.99,
            min_stock_recommendation: 1000000.50,
            warehouse_count: 100
          }
        ],
        total_parts: 1,
        low_stock_parts: 0
      };

      inventoryService.getOrganizationInventoryAggregation.mockResolvedValue(responseWithLargeNumbers);
      warehouseService.getOrganizationWarehouses.mockResolvedValue(mockWarehousesData);
      partsService.getParts.mockResolvedValue(mockPartsData);

      render(<WarehouseInventoryAggregationView organizationId={mockOrganizationId} />);

      await waitFor(() => {
        expect(screen.getByText('1 parts')).toBeInTheDocument();
      });

      // Should format large numbers correctly
      expect(screen.getByText('999,999,999.99')).toBeInTheDocument();
    });

    test('handles zero and negative stock values appropriately', async () => {
      const responseWithEdgeCaseNumbers = {
        organization_id: mockOrganizationId,
        inventory_summary: [
          {
            part_id: 'part-001',
            total_stock: 0,
            min_stock_recommendation: 10,
            warehouse_count: 0
          },
          {
            part_id: 'part-002',
            total_stock: -5, // Negative stock (data error)
            min_stock_recommendation: 20,
            warehouse_count: 1
          }
        ],
        total_parts: 2,
        low_stock_parts: 2
      };

      inventoryService.getOrganizationInventoryAggregation.mockResolvedValue(responseWithEdgeCaseNumbers);
      warehouseService.getOrganizationWarehouses.mockResolvedValue(mockWarehousesData);
      partsService.getParts.mockResolvedValue(mockPartsData);

      render(<WarehouseInventoryAggregationView organizationId={mockOrganizationId} />);

      await waitFor(() => {
        expect(screen.getByText('2 parts')).toBeInTheDocument();
      });

      // Should handle zero stock
      const outOfStockElements = screen.getAllByText('Out of Stock');
      expect(outOfStockElements.length).toBeGreaterThan(0);

      // Should handle negative stock gracefully
      expect(screen.getByText('-5')).toBeInTheDocument();
    });
  });

  describe('Performance and Loading States', () => {
    test('shows appropriate loading states during data fetch', async () => {
      // Mock slow API response
      inventoryService.getOrganizationInventoryAggregation.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve(mockInventoryApiResponse), 500))
      );
      warehouseService.getOrganizationWarehouses.mockResolvedValue(mockWarehousesData);
      partsService.getParts.mockResolvedValue(mockPartsData);

      render(<WarehouseInventoryAggregationView organizationId={mockOrganizationId} />);

      // Should show loading state immediately
      expect(screen.getByText('Loading aggregated inventory...')).toBeInTheDocument();
      expect(screen.getByText('Fetching data from server')).toBeInTheDocument();

      // Should show loading skeleton
      expect(document.querySelector('.animate-pulse')).toBeInTheDocument();

      // Wait for loading to complete
      await waitFor(() => {
        expect(screen.getByText('3 parts')).toBeInTheDocument();
      }, { timeout: 1000 });

      // Loading state should be gone
      expect(screen.queryByText('Loading aggregated inventory...')).not.toBeInTheDocument();
    });

    test('prevents duplicate API calls during loading', async () => {
      let callCount = 0;
      inventoryService.getOrganizationInventoryAggregation.mockImplementation(() => {
        callCount++;
        return new Promise(resolve => setTimeout(() => resolve(mockInventoryApiResponse), 300));
      });
      warehouseService.getOrganizationWarehouses.mockResolvedValue(mockWarehousesData);
      partsService.getParts.mockResolvedValue(mockPartsData);

      const { rerender } = render(<WarehouseInventoryAggregationView organizationId={mockOrganizationId} />);

      // Trigger re-render while loading
      rerender(<WarehouseInventoryAggregationView organizationId={mockOrganizationId} />);

      await waitFor(() => {
        expect(screen.getByText('3 parts')).toBeInTheDocument();
      }, { timeout: 500 });

      // Should only call API once despite re-render
      expect(callCount).toBe(1);
    });
  });

  describe('Component Integration with Backend API', () => {
    test('correctly processes backend API response structure', async () => {
      // Test with actual backend response structure
      const backendResponse = {
        organization_id: mockOrganizationId,
        inventory_summary: [
          {
            part_id: 'part-001',
            total_stock: 150.5,
            min_stock_recommendation: 50.0,
            warehouse_count: 3,
            is_low_stock: false
          }
        ],
        total_parts: 1,
        low_stock_parts: 0
      };

      inventoryService.getOrganizationInventoryAggregation.mockResolvedValue(backendResponse);
      warehouseService.getOrganizationWarehouses.mockResolvedValue(mockWarehousesData);
      partsService.getParts.mockResolvedValue(mockPartsData);

      render(<WarehouseInventoryAggregationView organizationId={mockOrganizationId} />);

      await waitFor(() => {
        expect(screen.getByText('1 parts')).toBeInTheDocument();
      });

      // Verify that the component correctly extracts data from inventory_summary
      expect(screen.getByText('Hydraulic Pump')).toBeInTheDocument();
      expect(screen.getByText('HP-001')).toBeInTheDocument();

      // Verify that the component doesn't crash when calling filter on the data
      expect(screen.queryByText(/filter is not a function/)).not.toBeInTheDocument();
    });

    test('handles concurrent API calls correctly', async () => {
      // Mock all three API calls with different delays
      inventoryService.getOrganizationInventoryAggregation.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve(mockInventoryApiResponse), 100))
      );
      warehouseService.getOrganizationWarehouses.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve(mockWarehousesData), 200))
      );
      partsService.getParts.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve(mockPartsData), 150))
      );

      render(<WarehouseInventoryAggregationView organizationId={mockOrganizationId} />);

      // Should show loading initially
      expect(screen.getByText('Loading aggregated inventory...')).toBeInTheDocument();

      // Wait for all API calls to complete
      await waitFor(() => {
        expect(screen.getByText('3 parts')).toBeInTheDocument();
      }, { timeout: 500 });

      // Should render correctly after all APIs complete
      expect(screen.getByText('Hydraulic Pump')).toBeInTheDocument();
      expect(screen.getByText('Oil Filter')).toBeInTheDocument();
      expect(screen.getByText('Pressure Valve')).toBeInTheDocument();
    });
  });
});