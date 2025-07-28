// frontend/src/components/__tests__/WarehouseInventoryView.test.js

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import WarehouseInventoryView from '../WarehouseInventoryView';
import { inventoryService } from '../../services/inventoryService';
import { partsService } from '../../services/partsService';

// Mock the services
jest.mock('../../services/inventoryService');
jest.mock('../../services/partsService');

describe('WarehouseInventoryView Data Validation', () => {
  const mockWarehouseId = 'test-warehouse-id';
  const mockWarehouse = { id: mockWarehouseId, name: 'Test Warehouse' };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('handles valid array response correctly', async () => {
    const mockInventoryData = [
      {
        id: 'inv-1',
        part_id: 'part-1',
        current_stock: 100,
        minimum_stock_recommendation: 20
      }
    ];

    inventoryService.getWarehouseInventory.mockResolvedValue(mockInventoryData);
    partsService.getParts.mockResolvedValue([
      { id: 'part-1', name: 'Test Part', part_number: 'TP-001' }
    ]);

    render(<WarehouseInventoryView warehouseId={mockWarehouseId} warehouse={mockWarehouse} />);

    await waitFor(() => {
      expect(screen.getByText('1')).toBeInTheDocument(); // Total items count
    });

    // Should not show any error messages
    expect(screen.queryByText(/Failed to fetch/)).not.toBeInTheDocument();
  });

  test('handles null API response gracefully', async () => {
    inventoryService.getWarehouseInventory.mockResolvedValue(null);
    partsService.getParts.mockResolvedValue([]);

    render(<WarehouseInventoryView warehouseId={mockWarehouseId} warehouse={mockWarehouse} />);

    await waitFor(() => {
      expect(screen.getByText('0 items')).toBeInTheDocument(); // Total items count should be 0
    });

    expect(screen.getByText('No inventory items found for this warehouse.')).toBeInTheDocument();
  });

  test('handles non-array API response gracefully', async () => {
    // Test case where API returns object instead of array
    const mockApiResponse = {
      warehouse_id: mockWarehouseId,
      inventory_items: [
        {
          id: 'inv-1',
          part_id: 'part-1',
          current_stock: 50,
          minimum_stock_recommendation: 10
        }
      ]
    };

    inventoryService.getWarehouseInventory.mockResolvedValue(mockApiResponse);
    partsService.getParts.mockResolvedValue([
      { id: 'part-1', name: 'Test Part', part_number: 'TP-001' }
    ]);

    render(<WarehouseInventoryView warehouseId={mockWarehouseId} warehouse={mockWarehouse} />);

    await waitFor(() => {
      expect(screen.getByText('0 items')).toBeInTheDocument(); // Should show 0 since it's not a direct array
    });

    // Should not crash or show filter errors
    expect(screen.queryByText(/filter is not a function/)).not.toBeInTheDocument();
  });

  test('handles API error gracefully', async () => {
    inventoryService.getWarehouseInventory.mockRejectedValue(
      new Error('API Error')
    );
    partsService.getParts.mockResolvedValue([]);

    render(<WarehouseInventoryView warehouseId={mockWarehouseId} warehouse={mockWarehouse} />);

    await waitFor(() => {
      expect(screen.getByText('Failed to fetch warehouse inventory')).toBeInTheDocument();
    });

    // Should not crash with filter errors
    expect(screen.queryByText(/filter is not a function/)).not.toBeInTheDocument();
  });

  test('handles undefined/string API response gracefully', async () => {
    // Test edge cases
    const testCases = [
      undefined,
      'not an array',
      123,
      true,
      {},
      { some: 'object' }
    ];

    for (const testCase of testCases) {
      inventoryService.getWarehouseInventory.mockResolvedValue(testCase);
      partsService.getParts.mockResolvedValue([]);

      const { unmount } = render(<WarehouseInventoryView warehouseId={mockWarehouseId} warehouse={mockWarehouse} />);

      await waitFor(() => {
        expect(screen.getByText('0 items')).toBeInTheDocument();
      });

      // Should not crash with filter errors
      expect(screen.queryByText(/filter is not a function/)).not.toBeInTheDocument();

      unmount();
    }
  });

  test('filtering operations work safely with validated data', async () => {
    const mockInventoryData = [
      {
        id: 'inv-1',
        part_id: 'part-1',
        current_stock: 100,
        minimum_stock_recommendation: 20
      },
      {
        id: 'inv-2',
        part_id: 'part-2',
        current_stock: 5,
        minimum_stock_recommendation: 10
      },
      {
        id: 'inv-3',
        part_id: 'part-3',
        current_stock: 0,
        minimum_stock_recommendation: 5
      }
    ];

    inventoryService.getWarehouseInventory.mockResolvedValue(mockInventoryData);
    partsService.getParts.mockResolvedValue([
      { id: 'part-1', name: 'Part 1', part_number: 'P1' },
      { id: 'part-2', name: 'Part 2', part_number: 'P2' },
      { id: 'part-3', name: 'Part 3', part_number: 'P3' }
    ]);

    render(<WarehouseInventoryView warehouseId={mockWarehouseId} warehouse={mockWarehouse} />);

    await waitFor(() => {
      expect(screen.getByText('3')).toBeInTheDocument(); // Total items
    });

    // Check that summary stats work correctly
    const summaryStats = screen.getAllByText(/^\d+$/);
    expect(summaryStats.length).toBeGreaterThan(0);

    // Should not show any filter errors
    expect(screen.queryByText(/filter is not a function/)).not.toBeInTheDocument();
  });
});