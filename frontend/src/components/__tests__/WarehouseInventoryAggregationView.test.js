// frontend/src/components/__tests__/WarehouseInventoryAggregationView.test.js

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import WarehouseInventoryAggregationView from '../WarehouseInventoryAggregationView';
import { inventoryService } from '../../services/inventoryService';
import { warehouseService } from '../../services/warehouseService';
import { partsService } from '../../services/partsService';

// Mock the services
jest.mock('../../services/inventoryService');
jest.mock('../../services/warehouseService');
jest.mock('../../services/partsService');
jest.mock('../../AuthContext', () => ({
  useAuth: () => ({ user: { id: 'test-user', role: 'admin' } })
}));

describe('WarehouseInventoryAggregationView Data Validation', () => {
  const mockOrganizationId = 'test-org-id';

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('handles API response with inventory_summary correctly', async () => {
    const mockApiResponse = {
      organization_id: mockOrganizationId,
      inventory_summary: [
        {
          part_id: 'part-1',
          total_stock: 100,
          min_stock_recommendation: 20,
          warehouse_count: 2
        }
      ],
      total_parts: 1,
      low_stock_parts: 0
    };

    inventoryService.getOrganizationInventoryAggregation.mockResolvedValue(mockApiResponse);
    warehouseService.getOrganizationWarehouses.mockResolvedValue([]);
    partsService.getParts.mockResolvedValue([]);

    render(<WarehouseInventoryAggregationView organizationId={mockOrganizationId} />);

    await waitFor(() => {
      expect(screen.getByText('1 parts')).toBeInTheDocument();
    });

    // Should not show any error messages
    expect(screen.queryByText(/Failed to fetch/)).not.toBeInTheDocument();
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

  test('handles API response without inventory_summary', async () => {
    const mockApiResponse = {
      organization_id: mockOrganizationId,
      total_parts: 0,
      low_stock_parts: 0
      // Missing inventory_summary
    };

    inventoryService.getOrganizationInventoryAggregation.mockResolvedValue(mockApiResponse);
    warehouseService.getOrganizationWarehouses.mockResolvedValue([]);
    partsService.getParts.mockResolvedValue([]);

    render(<WarehouseInventoryAggregationView organizationId={mockOrganizationId} />);

    await waitFor(() => {
      expect(screen.getByText('0 parts')).toBeInTheDocument();
    });

    expect(screen.getByText('No inventory items found.')).toBeInTheDocument();
  });

  test('handles API error gracefully', async () => {
    inventoryService.getOrganizationInventoryAggregation.mockRejectedValue(
      new Error('API Error')
    );
    warehouseService.getOrganizationWarehouses.mockResolvedValue([]);
    partsService.getParts.mockResolvedValue([]);

    render(<WarehouseInventoryAggregationView organizationId={mockOrganizationId} />);

    await waitFor(() => {
      expect(screen.getByText('Unable to load inventory data. This might be due to a network issue or server problem.')).toBeInTheDocument();
    });

    // Should also show the enhanced error UI
    expect(screen.getByText('Unable to Load Inventory Data')).toBeInTheDocument();
    expect(screen.getByText('Try Again')).toBeInTheDocument();
    expect(screen.getByText('Refresh Page')).toBeInTheDocument();
  });

  test('handles network error with specific message', async () => {
    inventoryService.getOrganizationInventoryAggregation.mockRejectedValue(
      new Error('Network Error: fetch failed')
    );
    warehouseService.getOrganizationWarehouses.mockResolvedValue([]);
    partsService.getParts.mockResolvedValue([]);

    render(<WarehouseInventoryAggregationView organizationId={mockOrganizationId} />);

    await waitFor(() => {
      expect(screen.getByText('Network connection issue. Please check your internet connection and try again.')).toBeInTheDocument();
    });
  });

  test('handles 401 unauthorized error with specific message', async () => {
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

  test('handles 404 not found error with specific message', async () => {
    inventoryService.getOrganizationInventoryAggregation.mockRejectedValue(
      new Error('404 Not Found')
    );
    warehouseService.getOrganizationWarehouses.mockResolvedValue([]);
    partsService.getParts.mockResolvedValue([]);

    render(<WarehouseInventoryAggregationView organizationId={mockOrganizationId} />);

    await waitFor(() => {
      expect(screen.getByText('The requested inventory data was not found. The organization may not exist or may not have any inventory.')).toBeInTheDocument();
    });
  });

  test('prevents operations during loading state', async () => {
    // Mock a slow API response
    inventoryService.getOrganizationInventoryAggregation.mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve({ inventory_summary: [] }), 1000))
    );
    warehouseService.getOrganizationWarehouses.mockResolvedValue([]);
    partsService.getParts.mockResolvedValue([]);

    render(<WarehouseInventoryAggregationView organizationId={mockOrganizationId} />);

    // Should show loading state
    expect(screen.getByText('Loading aggregated inventory...')).toBeInTheDocument();
    expect(screen.getByText('Fetching data from server')).toBeInTheDocument();

    // Should show loading skeleton
    expect(document.querySelector('.animate-pulse')).toBeInTheDocument();
  });

  test('handles malformed API response (direct array)', async () => {
    // Test case where API returns array directly instead of object
    const mockApiResponse = [
      {
        part_id: 'part-1',
        total_stock: 100,
        min_stock_recommendation: 20,
        warehouse_count: 2
      }
    ];

    inventoryService.getOrganizationInventoryAggregation.mockResolvedValue(mockApiResponse);
    warehouseService.getOrganizationWarehouses.mockResolvedValue([]);
    partsService.getParts.mockResolvedValue([]);

    render(<WarehouseInventoryAggregationView organizationId={mockOrganizationId} />);

    await waitFor(() => {
      expect(screen.getByText('1 parts')).toBeInTheDocument();
    });

    // Should handle direct array response correctly
    expect(screen.queryByText(/Failed to fetch/)).not.toBeInTheDocument();
  });
});