// frontend/src/__tests__/PartsPageE2E.test.js

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import Parts from '../pages/Parts';
import { partsService } from '../services/partsService';
import { AuthContext } from '../AuthContext';

// Mock the entire parts service
jest.mock('../services/partsService');

// Mock other components
jest.mock('../components/Modal', () => {
  return function MockModal({ show, children, title, onClose }) {
    if (!show) return null;
    return (
      <div data-testid="modal">
        <h2>{title}</h2>
        <button onClick={onClose}>Close</button>
        {children}
      </div>
    );
  };
});

jest.mock('../components/PartForm', () => {
  return function MockPartForm({ onSubmit, onClose }) {
    return (
      <div data-testid="part-form">
        <button onClick={() => onSubmit({ name: 'Test Part' })}>Submit</button>
        <button onClick={onClose}>Cancel</button>
      </div>
    );
  };
});

jest.mock('../components/PermissionGuard', () => {
  return function MockPermissionGuard({ children, hideIfNoPermission }) {
    return hideIfNoPermission ? children : <div>{children}</div>;
  };
});

const mockAuthContext = {
  user: {
    id: 'user-1',
    email: 'test@example.com',
    role: 'admin',
    organization_id: 'org-1'
  },
  token: 'mock-token',
  login: jest.fn(),
  logout: jest.fn()
};

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  useNavigate: () => jest.fn(),
  useLocation: () => ({ pathname: '/parts' }),
  Link: ({ children, to, ...props }) => <a href={to} {...props}>{children}</a>
}));

const renderPartsPage = () => {
  return render(
    <AuthContext.Provider value={mockAuthContext}>
      <Parts />
    </AuthContext.Provider>
  );
};

describe('Parts Page - End-to-End Error Handling Scenarios', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.spyOn(console, 'error').mockImplementation(() => { });
    jest.spyOn(console, 'warn').mockImplementation(() => { });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('Real-world Error Scenarios', () => {
    test('Scenario 1: Network disconnection during page load', async () => {
      // Simulate network disconnection
      const networkError = new Error('Network Error');
      networkError.request = { url: '/parts/with-inventory' };
      partsService.getPartsWithInventory.mockRejectedValue(networkError);

      renderPartsPage();

      // User sees loading state first
      expect(screen.getByText(/Loading parts/)).toBeInTheDocument();

      // Then sees network error
      await waitFor(() => {
        expect(screen.getByText(/Unable to connect to server/)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
      });

      // User clicks retry - network is restored
      const mockParts = [
        {
          id: '1',
          name: 'Network Test Part',
          part_number: 'NTP001',
          description: 'Test part after network recovery',
          part_type: 'consumable',
          unit_of_measure: 'pieces',
          is_proprietary: false,
          total_stock: 25,
          is_low_stock: false,
          warehouse_inventory: [
            {
              warehouse_name: 'Main Warehouse',
              current_stock: 25,
              is_low_stock: false
            }
          ]
        }
      ];

      partsService.getPartsWithInventory.mockResolvedValueOnce(mockParts);

      fireEvent.click(screen.getByRole('button', { name: /retry/i }));

      // User sees success
      await waitFor(() => {
        expect(screen.getByText('Network Test Part')).toBeInTheDocument();
        expect(screen.getByText('NTP001')).toBeInTheDocument();
        expect(screen.queryByText(/Unable to connect to server/)).not.toBeInTheDocument();
      });
    });

    test('Scenario 2: Authentication expires during session', async () => {
      // Initial load succeeds
      const initialParts = [
        {
          id: '1',
          name: 'Initial Part',
          part_number: 'IP001',
          part_type: 'consumable',
          unit_of_measure: 'pieces',
          is_proprietary: true,
          total_stock: 10,
          is_low_stock: false,
          warehouse_inventory: []
        }
      ];

      partsService.getPartsWithInventory.mockResolvedValueOnce(initialParts);

      renderPartsPage();

      await waitFor(() => {
        expect(screen.getByText('Initial Part')).toBeInTheDocument();
      });

      // User tries to delete a part - auth has expired
      const authError = new Error('Auth Error');
      authError.response = { status: 401, data: { detail: 'Token expired' } };
      partsService.deletePart.mockRejectedValue(authError);

      // Simulate delete action
      const deleteButton = screen.getByRole('button', { name: /delete/i });

      // Mock window.confirm to return true
      window.confirm = jest.fn(() => true);

      fireEvent.click(deleteButton);

      // User sees auth error
      await waitFor(() => {
        expect(screen.getByText(/Authentication failed/)).toBeInTheDocument();
      });

      // Verify the error is displayed properly
      expect(screen.getByText(/Please log in again/)).toBeInTheDocument();
    });

    test('Scenario 3: Server overload with multiple retry attempts', async () => {
      // Server returns 503 Service Unavailable
      const serverError = new Error('Server Overloaded');
      serverError.response = {
        status: 503,
        data: { detail: 'Service temporarily unavailable due to high load' }
      };

      partsService.getPartsWithInventory.mockRejectedValue(serverError);

      renderPartsPage();

      // User sees server error
      await waitFor(() => {
        expect(screen.getByText(/Service temporarily unavailable/)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
      });

      // User retries multiple times
      for (let attempt = 1; attempt <= 3; attempt++) {
        const retryButton = screen.getByRole('button', { name: /retry/i });
        fireEvent.click(retryButton);

        await waitFor(() => {
          expect(screen.getByText(`Retry attempt ${attempt} of 3`)).toBeInTheDocument();
        });

        // Still failing
        await waitFor(() => {
          expect(screen.getByText(/Service temporarily unavailable/)).toBeInTheDocument();
        });
      }

      // After 3 attempts, user sees guidance
      await waitFor(() => {
        expect(screen.getByText(/Multiple attempts failed/)).toBeInTheDocument();
        expect(screen.getByText(/Our servers are experiencing issues/)).toBeInTheDocument();
      });

      // Retry button should not be available after max attempts
      await waitFor(() => {
        const retryButton = screen.queryByRole('button', { name: /retry/i });
        expect(retryButton).toBeNull();
      });
    });

    test('Scenario 4: Permission changes during session', async () => {
      // Initial load succeeds
      const initialParts = [
        {
          id: '1',
          name: 'Permission Test Part',
          part_number: 'PTP001',
          part_type: 'consumable',
          unit_of_measure: 'pieces',
          is_proprietary: false,
          total_stock: 5,
          is_low_stock: true,
          warehouse_inventory: []
        }
      ];

      partsService.getPartsWithInventory.mockResolvedValueOnce(initialParts);

      renderPartsPage();

      await waitFor(() => {
        expect(screen.getByText('Permission Test Part')).toBeInTheDocument();
      });

      // User tries to edit - permissions have been revoked
      const permissionError = new Error('Permission Error');
      permissionError.response = {
        status: 403,
        data: { detail: 'Insufficient permissions to modify parts' }
      };
      partsService.updatePart.mockRejectedValue(permissionError);

      // Simulate edit action by opening modal and submitting
      const editButton = screen.getByRole('button', { name: /edit/i });
      fireEvent.click(editButton);

      await waitFor(() => {
        expect(screen.getByTestId('modal')).toBeInTheDocument();
      });

      const submitButton = screen.getByRole('button', { name: /submit/i });
      fireEvent.click(submitButton);

      // User sees permission error
      await waitFor(() => {
        expect(screen.getByText(/You don't have permission/)).toBeInTheDocument();
      });
    });

    test('Scenario 5: Intermittent connectivity with eventual success', async () => {
      const networkError = new Error('Intermittent Network Error');
      networkError.request = {};

      const successData = [
        {
          id: '1',
          name: 'Connectivity Test Part',
          part_number: 'CTP001',
          part_type: 'bulk_material',
          unit_of_measure: 'kg',
          is_proprietary: true,
          total_stock: 100.5,
          is_low_stock: false,
          warehouse_inventory: [
            {
              warehouse_name: 'Warehouse A',
              current_stock: 50.25,
              is_low_stock: false
            },
            {
              warehouse_name: 'Warehouse B',
              current_stock: 50.25,
              is_low_stock: false
            }
          ]
        }
      ];

      // Fail twice, then succeed
      partsService.getPartsWithInventory
        .mockRejectedValueOnce(networkError)
        .mockRejectedValueOnce(networkError)
        .mockResolvedValueOnce(successData);

      renderPartsPage();

      // First failure
      await waitFor(() => {
        expect(screen.getByText(/Unable to connect to server/)).toBeInTheDocument();
      });

      // First retry - still fails
      fireEvent.click(screen.getByRole('button', { name: /retry/i }));

      await waitFor(() => {
        expect(screen.getByText(/Retry attempt 1 of 3/)).toBeInTheDocument();
      });

      // Second retry - succeeds
      fireEvent.click(screen.getByRole('button', { name: /retry/i }));

      await waitFor(() => {
        expect(screen.getByText('Connectivity Test Part')).toBeInTheDocument();
        expect(screen.getByText('CTP001')).toBeInTheDocument();
        expect(screen.getByText('Warehouse A')).toBeInTheDocument();
        expect(screen.getByText('Warehouse B')).toBeInTheDocument();
        expect(screen.queryByText(/Unable to connect to server/)).not.toBeInTheDocument();
      });
    });

    test('Scenario 6: Malformed server response handling', async () => {
      // Server returns unexpected data format
      partsService.getPartsWithInventory.mockResolvedValue({
        message: 'This should be an array',
        data: 'not parts data'
      });

      renderPartsPage();

      // Should handle gracefully and show empty state
      await waitFor(() => {
        expect(screen.getByText(/No Parts Found/)).toBeInTheDocument();
        expect(screen.getByText(/There are no parts in the system yet/)).toBeInTheDocument();
      });

      // Should log warning about malformed response
      expect(console.warn).toHaveBeenCalledWith(
        'API returned non-array response for parts with inventory:',
        expect.any(Object)
      );
    });

    test('Scenario 7: Mixed success and error operations', async () => {
      // Initial load succeeds
      const initialParts = [
        {
          id: '1',
          name: 'Mixed Test Part',
          part_number: 'MTP001',
          part_type: 'consumable',
          unit_of_measure: 'pieces',
          is_proprietary: false,
          total_stock: 15,
          is_low_stock: false,
          warehouse_inventory: []
        }
      ];

      partsService.getPartsWithInventory.mockResolvedValue(initialParts);

      renderPartsPage();

      await waitFor(() => {
        expect(screen.getByText('Mixed Test Part')).toBeInTheDocument();
      });

      // Create operation fails
      const validationError = new Error('Validation Error');
      validationError.response = {
        status: 400,
        data: { detail: 'Part number already exists' }
      };
      partsService.createPart.mockRejectedValue(validationError);

      // User tries to add a part
      const addButton = screen.getByRole('button', { name: /add part/i });
      fireEvent.click(addButton);

      await waitFor(() => {
        expect(screen.getByTestId('modal')).toBeInTheDocument();
      });

      const submitButton = screen.getByRole('button', { name: /submit/i });
      fireEvent.click(submitButton);

      // Should see validation error but parts list should remain
      await waitFor(() => {
        expect(screen.getByText(/Part number already exists/)).toBeInTheDocument();
        expect(screen.getByText('Mixed Test Part')).toBeInTheDocument(); // Original data still there
      });
    });
  });

  describe('User Experience Validation', () => {
    test('Loading states are properly managed', async () => {
      let resolvePromise;
      const promise = new Promise(resolve => {
        resolvePromise = resolve;
      });

      partsService.getPartsWithInventory.mockReturnValue(promise);

      renderPartsPage();

      // Should show loading state
      expect(screen.getByText(/Loading parts/)).toBeInTheDocument();
      expect(screen.getByRole('status', { hidden: true })).toBeInTheDocument();

      // Resolve the promise
      act(() => {
        resolvePromise([]);
      });

      // Loading should disappear
      await waitFor(() => {
        expect(screen.queryByText(/Loading parts/)).not.toBeInTheDocument();
      });
    });

    test('Error messages are accessible and clear', async () => {
      const error = new Error('Accessibility Test Error');
      error.response = { status: 500, data: { detail: 'Server error for accessibility test' } };
      partsService.getPartsWithInventory.mockRejectedValue(error);

      renderPartsPage();

      await waitFor(() => {
        const errorElement = screen.getByRole('alert');
        expect(errorElement).toBeInTheDocument();
        expect(errorElement).toHaveTextContent('Server error for accessibility test');
      });
    });

    test('Retry functionality provides proper feedback', async () => {
      const error = new Error('Retry Test Error');
      error.request = {};
      partsService.getPartsWithInventory.mockRejectedValue(error);

      renderPartsPage();

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
      });

      // Click retry
      fireEvent.click(screen.getByRole('button', { name: /retry/i }));

      // Should show retrying state
      await waitFor(() => {
        expect(screen.getByText(/Retrying/)).toBeInTheDocument();
      });
    });
  });
});