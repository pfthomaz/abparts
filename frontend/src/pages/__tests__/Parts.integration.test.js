// frontend/src/pages/__tests__/Parts.integration.test.js

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import Parts from '../Parts';
import { partsService } from '../../services/partsService';
import { AuthContext } from '../../AuthContext';

// Mock the parts service
jest.mock('../../services/partsService');

// Mock the auth context
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

// Mock components that aren't essential for error handling tests
jest.mock('../../components/Modal', () => {
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

jest.mock('../../components/PartForm', () => {
  return function MockPartForm({ onSubmit, onClose }) {
    return (
      <div data-testid="part-form">
        <button onClick={() => onSubmit({ name: 'Test Part' })}>Submit</button>
        <button onClick={onClose}>Cancel</button>
      </div>
    );
  };
});

jest.mock('../../components/PermissionGuard', () => {
  return function MockPermissionGuard({ children, hideIfNoPermission }) {
    return hideIfNoPermission ? children : <div>{children}</div>;
  };
});

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  useNavigate: () => jest.fn(),
  useLocation: () => ({ pathname: '/parts' }),
  Link: ({ children, to, ...props }) => <a href={to} {...props}>{children}</a>
}));

// Helper function to render Parts component with necessary providers
const renderPartsPage = () => {
  return render(
    <AuthContext.Provider value={mockAuthContext}>
      <Parts />
    </AuthContext.Provider>
  );
};

describe('Parts Page - Integration Testing and Error Handling', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset console methods
    jest.spyOn(console, 'error').mockImplementation(() => { });
    jest.spyOn(console, 'warn').mockImplementation(() => { });
    jest.spyOn(console, 'log').mockImplementation(() => { });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('Requirement 1.1-1.6: Error Handling and Display', () => {
    test('1.1: Should display human-readable error message instead of [object Object]', async () => {
      // Mock API failure
      const mockError = new Error('API Error');
      mockError.response = { status: 500, data: { detail: 'Internal server error' } };
      partsService.getPartsWithInventory.mockRejectedValue(mockError);

      renderPartsPage();

      await waitFor(() => {
        expect(screen.getByText(/Internal server error/)).toBeInTheDocument();
        expect(screen.queryByText('[object Object]')).not.toBeInTheDocument();
      });
    });

    test('1.2: Should display network error message for connection issues', async () => {
      // Mock network error
      const networkError = new Error('Network Error');
      networkError.request = {}; // Indicates network error
      partsService.getPartsWithInventory.mockRejectedValue(networkError);

      renderPartsPage();

      await waitFor(() => {
        expect(screen.getByText(/Unable to connect to server/)).toBeInTheDocument();
      });
    });

    test('1.3: Should display authentication error message', async () => {
      // Mock auth error
      const authError = new Error('Auth Error');
      authError.response = { status: 401, data: { detail: 'Unauthorized' } };
      partsService.getPartsWithInventory.mockRejectedValue(authError);

      renderPartsPage();

      await waitFor(() => {
        expect(screen.getByText(/Authentication failed/)).toBeInTheDocument();
      });
    });

    test('1.4: Should display permission error message', async () => {
      // Mock permission error
      const permissionError = new Error('Permission Error');
      permissionError.response = { status: 403, data: { detail: 'Forbidden' } };
      partsService.getPartsWithInventory.mockRejectedValue(permissionError);

      renderPartsPage();

      await waitFor(() => {
        expect(screen.getByText(/You don't have permission/)).toBeInTheDocument();
      });
    });

    test('1.5: Should display server error message', async () => {
      // Mock server error
      const serverError = new Error('Server Error');
      serverError.response = { status: 500, data: { detail: 'Database connection failed' } };
      partsService.getPartsWithInventory.mockRejectedValue(serverError);

      renderPartsPage();

      await waitFor(() => {
        expect(screen.getByText(/Database connection failed/)).toBeInTheDocument();
      });
    });

    test('1.6: Should log full error details to console for debugging', async () => {
      const mockError = new Error('Test Error');
      mockError.response = { status: 500, data: { detail: 'Server error' } };
      partsService.getPartsWithInventory.mockRejectedValue(mockError);

      renderPartsPage();

      await waitFor(() => {
        expect(console.error).toHaveBeenCalledWith('Error fetching parts:', mockError);
      });
    });
  });

  describe('Requirement 6.1-6.5: Retry Functionality and Recovery', () => {
    test('6.1: Should provide retry button when error occurs', async () => {
      const mockError = new Error('Network Error');
      mockError.request = {};
      partsService.getPartsWithInventory.mockRejectedValue(mockError);

      renderPartsPage();

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
      });
    });

    test('6.2: Should clear error state and retry when retry button is clicked', async () => {
      const mockError = new Error('Network Error');
      mockError.request = {};

      // First call fails, second call succeeds
      partsService.getPartsWithInventory
        .mockRejectedValueOnce(mockError)
        .mockResolvedValueOnce([
          {
            id: '1',
            name: 'Test Part',
            part_number: 'TP001',
            total_stock: 10,
            warehouse_inventory: []
          }
        ]);

      renderPartsPage();

      // Wait for error to appear
      await waitFor(() => {
        expect(screen.getByText(/Unable to connect to server/)).toBeInTheDocument();
      });

      // Click retry button
      const retryButton = screen.getByRole('button', { name: /retry/i });
      fireEvent.click(retryButton);

      // Wait for success
      await waitFor(() => {
        expect(screen.getByText('Test Part')).toBeInTheDocument();
        expect(screen.queryByText(/Unable to connect to server/)).not.toBeInTheDocument();
      });

      expect(partsService.getPartsWithInventory).toHaveBeenCalledTimes(2);
    });

    test('6.3: Should show guidance for multiple consecutive errors', async () => {
      const mockError = new Error('Network Error');
      mockError.request = {};
      partsService.getPartsWithInventory.mockRejectedValue(mockError);

      renderPartsPage();

      // Wait for initial error
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
      });

      // Retry multiple times
      for (let i = 0; i < 3; i++) {
        const retryButton = screen.getByRole('button', { name: /retry/i });
        fireEvent.click(retryButton);

        await waitFor(() => {
          expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
        });
      }

      // Should show guidance after multiple failures
      await waitFor(() => {
        expect(screen.getByText(/Multiple attempts failed/)).toBeInTheDocument();
      });
    });

    test('6.4: Should provide guidance for backend unavailability', async () => {
      const serverError = new Error('Server Error');
      serverError.response = { status: 503, data: { detail: 'Service unavailable' } };
      partsService.getPartsWithInventory.mockRejectedValue(serverError);

      renderPartsPage();

      await waitFor(() => {
        expect(screen.getByText(/Service unavailable/)).toBeInTheDocument();
      });

      // Retry multiple times to trigger guidance
      for (let i = 0; i < 3; i++) {
        const retryButton = screen.getByRole('button', { name: /retry/i });
        fireEvent.click(retryButton);

        await waitFor(() => {
          expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
        });
      }

      await waitFor(() => {
        expect(screen.getByText(/Our servers are experiencing issues/)).toBeInTheDocument();
      });
    });

    test('6.5: Should limit retry attempts and disable retry button after max attempts', async () => {
      const mockError = new Error('Network Error');
      mockError.request = {};
      partsService.getPartsWithInventory.mockRejectedValue(mockError);

      renderPartsPage();

      // Wait for initial error
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
      });

      // Retry maximum number of times (3 attempts)
      for (let i = 0; i < 3; i++) {
        const retryButton = screen.getByRole('button', { name: /retry/i });
        expect(retryButton).not.toBeDisabled();
        fireEvent.click(retryButton);

        await waitFor(() => {
          expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
        });
      }

      // After max attempts, retry button should not be available or should be disabled
      await waitFor(() => {
        const retryButton = screen.queryByRole('button', { name: /retry/i });
        expect(retryButton).toBeNull(); // Button should not be present after max attempts
      });
    });
  });

  describe('Complete Error Handling Flow Integration', () => {
    test('Should handle complete error-to-success flow', async () => {
      const mockError = new Error('Temporary Error');
      mockError.response = { status: 500, data: { detail: 'Temporary server error' } };

      const mockParts = [
        {
          id: '1',
          name: 'Test Part 1',
          part_number: 'TP001',
          description: 'Test description',
          part_type: 'consumable',
          unit_of_measure: 'pieces',
          is_proprietary: true,
          total_stock: 50,
          is_low_stock: false,
          warehouse_inventory: [
            {
              warehouse_name: 'Main Warehouse',
              current_stock: 50,
              is_low_stock: false
            }
          ]
        }
      ];

      // First call fails, second call succeeds
      partsService.getPartsWithInventory
        .mockRejectedValueOnce(mockError)
        .mockResolvedValueOnce(mockParts);

      renderPartsPage();

      // 1. Initial loading state
      expect(screen.getByText(/Loading parts/)).toBeInTheDocument();

      // 2. Error state appears
      await waitFor(() => {
        expect(screen.getByText(/Temporary server error/)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
      });

      // 3. Loading should be false, error should be visible
      expect(screen.queryByText(/Loading parts/)).not.toBeInTheDocument();

      // 4. Click retry
      const retryButton = screen.getByRole('button', { name: /retry/i });
      fireEvent.click(retryButton);

      // 5. Should show retrying state
      await waitFor(() => {
        expect(screen.getByText(/Retrying/)).toBeInTheDocument();
      });

      // 6. Success state - parts should be displayed
      await waitFor(() => {
        expect(screen.getByText('Test Part 1')).toBeInTheDocument();
        expect(screen.getByText('TP001')).toBeInTheDocument();
        expect(screen.getByText('Main Warehouse')).toBeInTheDocument();
      });

      // 7. Error should be cleared
      expect(screen.queryByText(/Temporary server error/)).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /retry/i })).not.toBeInTheDocument();
    });

    test('Should handle various error scenarios in sequence', async () => {
      const scenarios = [
        {
          error: { request: {} }, // Network error
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

      for (const scenario of scenarios) {
        const mockError = new Error('Test Error');
        Object.assign(mockError, scenario.error);

        partsService.getPartsWithInventory.mockRejectedValueOnce(mockError);

        renderPartsPage();

        await waitFor(() => {
          expect(screen.getByText(scenario.expectedMessage)).toBeInTheDocument();
        });

        // Clear for next test
        jest.clearAllMocks();
      }
    });
  });

  describe('User Experience Validation', () => {
    test('Should provide clear feedback during loading states', async () => {
      // Mock a delayed response
      partsService.getPartsWithInventory.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve([]), 100))
      );

      renderPartsPage();

      // Should show loading indicator
      expect(screen.getByText(/Loading parts/)).toBeInTheDocument();
      expect(screen.getByRole('status', { hidden: true })).toBeInTheDocument(); // Loading spinner

      await waitFor(() => {
        expect(screen.queryByText(/Loading parts/)).not.toBeInTheDocument();
      });
    });

    test('Should show appropriate empty state when no parts exist', async () => {
      partsService.getPartsWithInventory.mockResolvedValue([]);

      renderPartsPage();

      await waitFor(() => {
        expect(screen.getByText(/No Parts Found/)).toBeInTheDocument();
        expect(screen.getByText(/There are no parts in the system yet/)).toBeInTheDocument();
      });
    });

    test('Should display retry count to user', async () => {
      const mockError = new Error('Network Error');
      mockError.request = {};
      partsService.getPartsWithInventory.mockRejectedValue(mockError);

      renderPartsPage();

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
      });

      // First retry
      fireEvent.click(screen.getByRole('button', { name: /retry/i }));

      await waitFor(() => {
        expect(screen.getByText(/Retry attempt 1 of 3/)).toBeInTheDocument();
      });

      // Second retry
      fireEvent.click(screen.getByRole('button', { name: /retry/i }));

      await waitFor(() => {
        expect(screen.getByText(/Retry attempt 2 of 3/)).toBeInTheDocument();
      });
    });
  });

  describe('Error Message Clarity Validation', () => {
    test('Should provide specific error messages for different HTTP status codes', async () => {
      const statusTests = [
        { status: 400, message: /Invalid data provided/ },
        { status: 404, message: /The requested resource was not found/ },
        { status: 408, message: /Request timed out/ },
        { status: 429, message: /Too many requests/ },
        { status: 502, message: /Server error occurred/ },
        { status: 503, message: /Server error occurred/ }
      ];

      for (const test of statusTests) {
        const mockError = new Error('Test Error');
        mockError.response = {
          status: test.status,
          data: { detail: `Status ${test.status} error` }
        };

        partsService.getPartsWithInventory.mockRejectedValueOnce(mockError);

        renderPartsPage();

        await waitFor(() => {
          expect(screen.getByText(test.message)).toBeInTheDocument();
        });

        // Clear for next test
        jest.clearAllMocks();
      }
    });

    test('Should handle malformed error responses gracefully', async () => {
      const mockError = new Error('Test Error');
      mockError.response = {
        status: 500,
        data: null // Malformed response
      };

      partsService.getPartsWithInventory.mockRejectedValue(mockError);

      renderPartsPage();

      await waitFor(() => {
        expect(screen.getByText(/Server error occurred/)).toBeInTheDocument();
      });
    });
  });
});