// frontend/src/pages/__tests__/PartsErrorHandling.test.js

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { partsService } from '../../services/partsService';

// Mock the parts service
jest.mock('../../services/partsService');

// Mock react-router-dom hooks
const mockNavigate = jest.fn();
const mockLocation = { pathname: '/parts' };

jest.mock('react-router-dom', () => ({
  useNavigate: () => mockNavigate,
  useLocation: () => mockLocation,
  Link: ({ children, to, ...props }) => <a href={to} {...props}>{children}</a>
}));

// Mock AuthContext
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

jest.mock('../../AuthContext', () => {
  const React = require('react');
  return {
    AuthContext: React.createContext(null),
    useAuth: () => mockAuthContext
  };
});

// Mock components
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

// Import Parts component after mocks
import Parts from '../Parts';
import { AuthContext } from '../../AuthContext';

const renderPartsPage = () => {
  return render(
    <AuthContext.Provider value={mockAuthContext}>
      <Parts />
    </AuthContext.Provider>
  );
};

describe('Parts Page - Error Handling Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.spyOn(console, 'error').mockImplementation(() => { });
    jest.spyOn(console, 'warn').mockImplementation(() => { });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('Requirement 1.1-1.6: Error Handling and Display', () => {
    test('1.1: Should display human-readable error message instead of [object Object]', async () => {
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
      const networkError = new Error('Network Error');
      networkError.request = {};
      partsService.getPartsWithInventory.mockRejectedValue(networkError);

      renderPartsPage();

      await waitFor(() => {
        expect(screen.getByText(/Unable to connect to server/)).toBeInTheDocument();
      });
    });

    test('1.3: Should display authentication error message', async () => {
      const authError = new Error('Auth Error');
      authError.response = { status: 401, data: { detail: 'Unauthorized' } };
      partsService.getPartsWithInventory.mockRejectedValue(authError);

      renderPartsPage();

      await waitFor(() => {
        expect(screen.getByText(/Authentication failed/)).toBeInTheDocument();
      });
    });

    test('1.4: Should display permission error message', async () => {
      const permissionError = new Error('Permission Error');
      permissionError.response = { status: 403, data: { detail: 'Forbidden' } };
      partsService.getPartsWithInventory.mockRejectedValue(permissionError);

      renderPartsPage();

      await waitFor(() => {
        expect(screen.getByText(/You don't have permission/)).toBeInTheDocument();
      });
    });

    test('1.5: Should display server error message', async () => {
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

      const mockParts = [
        {
          id: '1',
          name: 'Test Part',
          part_number: 'TP001',
          total_stock: 10,
          warehouse_inventory: []
        }
      ];

      partsService.getPartsWithInventory
        .mockRejectedValueOnce(mockError)
        .mockResolvedValueOnce(mockParts);

      renderPartsPage();

      await waitFor(() => {
        expect(screen.getByText(/Unable to connect to server/)).toBeInTheDocument();
      });

      const retryButton = screen.getByRole('button', { name: /retry/i });
      fireEvent.click(retryButton);

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

      // After max attempts, retry button should not be available
      await waitFor(() => {
        const retryButton = screen.queryByRole('button', { name: /retry/i });
        expect(retryButton).toBeNull();
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

      partsService.getPartsWithInventory
        .mockRejectedValueOnce(mockError)
        .mockResolvedValueOnce(mockParts);

      renderPartsPage();

      // Initial loading state
      expect(screen.getByText(/Loading parts/)).toBeInTheDocument();

      // Error state appears
      await waitFor(() => {
        expect(screen.getByText(/Temporary server error/)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
      });

      // Loading should be false, error should be visible
      expect(screen.queryByText(/Loading parts/)).not.toBeInTheDocument();

      // Click retry
      const retryButton = screen.getByRole('button', { name: /retry/i });
      fireEvent.click(retryButton);

      // Should show retrying state
      await waitFor(() => {
        expect(screen.getByText(/Retrying/)).toBeInTheDocument();
      });

      // Success state - parts should be displayed
      await waitFor(() => {
        expect(screen.getByText('Test Part 1')).toBeInTheDocument();
        expect(screen.getByText('TP001')).toBeInTheDocument();
        expect(screen.getByText('Main Warehouse')).toBeInTheDocument();
      });

      // Error should be cleared
      expect(screen.queryByText(/Temporary server error/)).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /retry/i })).not.toBeInTheDocument();
    });
  });

  describe('User Experience Validation', () => {
    test('Should provide clear feedback during loading states', async () => {
      partsService.getPartsWithInventory.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve([]), 100))
      );

      renderPartsPage();

      expect(screen.getByText(/Loading parts/)).toBeInTheDocument();

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
});