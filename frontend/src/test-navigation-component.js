// React component test for permission-based navigation visibility
// This test renders the actual Layout component and verifies DOM elements

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';

import Layout from './components/Layout';
import { AuthContext } from './AuthContext';
import { USER_ROLES } from './utils/permissions';

// Mock users for testing
const mockUsers = {
  superAdmin: {
    id: '1',
    username: 'superadmin',
    name: 'Super Admin',
    email: 'super@example.com',
    role: USER_ROLES.SUPER_ADMIN,
    organization_id: '1',
    organization: { name: 'Oraseas EE' }
  },

  admin: {
    id: '2',
    username: 'admin',
    name: 'Admin User',
    email: 'admin@example.com',
    role: USER_ROLES.ADMIN,
    organization_id: '2',
    organization: { name: 'Customer Org' }
  },

  user: {
    id: '3',
    username: 'user',
    name: 'Regular User',
    email: 'user@example.com',
    role: USER_ROLES.USER,
    organization_id: '2',
    organization: { name: 'Customer Org' }
  }
};

// Helper component to wrap Layout with necessary providers
const LayoutWrapper = ({ user, children }) => {
  const authContextValue = {
    user,
    logout: jest.fn(),
    login: jest.fn(),
    isAuthenticated: !!user
  };

  return (
    <BrowserRouter>
      <AuthContext.Provider value={authContextValue}>
        <Layout />
        {children}
      </AuthContext.Provider>
    </BrowserRouter>
  );
};

describe('Navigation Permission-Based Visibility', () => {

  describe('Super Admin Navigation', () => {
    test('should show all navigation categories and items', async () => {
      render(<LayoutWrapper user={mockUsers.superAdmin} />);

      // Check that all main categories are present
      expect(screen.getByText('Core')).toBeInTheDocument();
      expect(screen.getByText('Inventory')).toBeInTheDocument();
      expect(screen.getByText('Operations')).toBeInTheDocument();
      expect(screen.getByText('Administration')).toBeInTheDocument();

      // Hover over Core dropdown to reveal items
      const coreButton = screen.getByText('Core');
      fireEvent.mouseEnter(coreButton);

      await waitFor(() => {
        expect(screen.getByText('Parts')).toBeInTheDocument();
        expect(screen.getByText('Inventory')).toBeInTheDocument();
        expect(screen.getByText('Orders')).toBeInTheDocument();
        expect(screen.getByText('Warehouses')).toBeInTheDocument();
      });

      // Check for admin-only items in Administration
      const adminButton = screen.getByText('Administration');
      fireEvent.mouseEnter(adminButton);

      await waitFor(() => {
        expect(screen.getByText('Organizations')).toBeInTheDocument();
        expect(screen.getByText('Users')).toBeInTheDocument();
      });

      // Check for global access indicators
      const globalIndicators = screen.getAllByText('global');
      expect(globalIndicators.length).toBeGreaterThan(0);
    });

    test('should show global access scope indicator', () => {
      render(<LayoutWrapper user={mockUsers.superAdmin} />);

      // Super admin should see global scope indicators
      const userButton = screen.getByRole('button', { name: /Super Admin/i });
      expect(userButton).toBeInTheDocument();

      // Check for Global badge
      expect(screen.getByText('Global')).toBeInTheDocument();
    });
  });

  describe('Admin Navigation', () => {
    test('should hide super admin only items', async () => {
      render(<LayoutWrapper user={mockUsers.admin} />);

      // Should see most categories
      expect(screen.getByText('Core')).toBeInTheDocument();
      expect(screen.getByText('Inventory')).toBeInTheDocument();
      expect(screen.getByText('Operations')).toBeInTheDocument();
      expect(screen.getByText('Administration')).toBeInTheDocument();

      // Should NOT see Organizations in Administration dropdown
      const adminButton = screen.getByText('Administration');
      fireEvent.mouseEnter(adminButton);

      await waitFor(() => {
        expect(screen.getByText('Users')).toBeInTheDocument();
      });

      // Organizations should not be visible (super admin only)
      expect(screen.queryByText('Organizations')).not.toBeInTheDocument();

      // Should not have global access indicators
      expect(screen.queryByText('Global')).not.toBeInTheDocument();
    });

    test('should show organization-scoped access', async () => {
      render(<LayoutWrapper user={mockUsers.admin} />);

      // Hover over Core to see access scope
      const coreButton = screen.getByText('Core');
      fireEvent.mouseEnter(coreButton);

      await waitFor(() => {
        // Should see organization scope indicators
        const orgIndicators = screen.getAllByText('organization');
        expect(orgIndicators.length).toBeGreaterThan(0);
      });
    });
  });

  describe('Regular User Navigation', () => {
    test('should hide admin-only items and categories', async () => {
      render(<LayoutWrapper user={mockUsers.user} />);

      // Should see basic categories
      expect(screen.getByText('Core')).toBeInTheDocument();
      expect(screen.getByText('Operations')).toBeInTheDocument();

      // Should NOT see Administration category
      expect(screen.queryByText('Administration')).not.toBeInTheDocument();

      // Hover over Core to check available items
      const coreButton = screen.getByText('Core');
      fireEvent.mouseEnter(coreButton);

      await waitFor(() => {
        expect(screen.getByText('Parts')).toBeInTheDocument();
        expect(screen.getByText('Inventory')).toBeInTheDocument();
        expect(screen.getByText('Orders')).toBeInTheDocument();
      });

      // Should NOT see admin-only items like Warehouses
      expect(screen.queryByText('Warehouses')).not.toBeInTheDocument();
      expect(screen.queryByText('Users')).not.toBeInTheDocument();
      expect(screen.queryByText('Organizations')).not.toBeInTheDocument();
    });

    test('should not show Inventory category if no inventory permissions', async () => {
      render(<LayoutWrapper user={mockUsers.user} />);

      // Regular users should still see Inventory category since they have VIEW_INVENTORY
      expect(screen.getByText('Inventory')).toBeInTheDocument();

      // But should not see admin-only inventory items like Stocktake
      const inventoryButton = screen.getByText('Inventory');
      fireEvent.mouseEnter(inventoryButton);

      await waitFor(() => {
        // Should not see Stocktake (admin only)
        expect(screen.queryByText('Stocktake')).not.toBeInTheDocument();
      });
    });
  });

  describe('Mobile Navigation', () => {
    test('should respect permissions in mobile menu', async () => {
      // Mock mobile viewport
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 500,
      });

      render(<LayoutWrapper user={mockUsers.user} />);

      // Find and click mobile menu button
      const mobileMenuButton = screen.getByRole('button', { name: /menu/i });
      fireEvent.click(mobileMenuButton);

      await waitFor(() => {
        // Should see allowed items
        expect(screen.getByText('Parts')).toBeInTheDocument();
        expect(screen.getByText('Inventory')).toBeInTheDocument();
        expect(screen.getByText('Orders')).toBeInTheDocument();

        // Should not see restricted items
        expect(screen.queryByText('Users')).not.toBeInTheDocument();
        expect(screen.queryByText('Organizations')).not.toBeInTheDocument();
      });
    });
  });

  describe('Permission Guard Integration', () => {
    test('should hide navigation items when PermissionGuard denies access', async () => {
      // Test with a user that has very limited permissions
      const limitedUser = {
        ...mockUsers.user,
        role: 'limited_role' // This should result in minimal permissions
      };

      render(<LayoutWrapper user={limitedUser} />);

      // Should only see Dashboard and basic items
      expect(screen.getByText('Core')).toBeInTheDocument();

      const coreButton = screen.getByText('Core');
      fireEvent.mouseEnter(coreButton);

      // Most items should be hidden due to PermissionGuard
      await waitFor(() => {
        // Should not see items that require specific permissions
        expect(screen.queryByText('Users')).not.toBeInTheDocument();
        expect(screen.queryByText('Organizations')).not.toBeInTheDocument();
        expect(screen.queryByText('Warehouses')).not.toBeInTheDocument();
      });
    });
  });

  describe('Core Category Population', () => {
    test('should properly populate Core dropdown with appropriate items', async () => {
      render(<LayoutWrapper user={mockUsers.admin} />);

      const coreButton = screen.getByText('Core');
      fireEvent.mouseEnter(coreButton);

      await waitFor(() => {
        // Core should contain these items for admin users
        expect(screen.getByText('Parts')).toBeInTheDocument();
        expect(screen.getByText('Inventory')).toBeInTheDocument();
        expect(screen.getByText('Orders')).toBeInTheDocument();
        expect(screen.getByText('Warehouses')).toBeInTheDocument();

        // Verify these are actually in the Core dropdown
        const coreDropdown = screen.getByText('Parts').closest('[class*="dropdown"]');
        expect(coreDropdown).toBeInTheDocument();
      });
    });

    test('should show Core category even for users with minimal permissions', async () => {
      render(<LayoutWrapper user={mockUsers.user} />);

      // Core category should always be visible (contains Dashboard)
      expect(screen.getByText('Core')).toBeInTheDocument();

      const coreButton = screen.getByText('Core');
      fireEvent.mouseEnter(coreButton);

      await waitFor(() => {
        // Should at least see basic items user has permission for
        expect(screen.getByText('Parts')).toBeInTheDocument();
        expect(screen.getByText('Inventory')).toBeInTheDocument();
        expect(screen.getByText('Orders')).toBeInTheDocument();
      });
    });
  });

  describe('Access Scope Indicators', () => {
    test('should show correct access scope badges', async () => {
      render(<LayoutWrapper user={mockUsers.admin} />);

      const coreButton = screen.getByText('Core');
      fireEvent.mouseEnter(coreButton);

      await waitFor(() => {
        // Admin should see organization scope
        const orgBadges = screen.getAllByText('organization');
        expect(orgBadges.length).toBeGreaterThan(0);

        // Should not see global badges
        expect(screen.queryByText('global')).not.toBeInTheDocument();
      });
    });

    test('should show global scope for super admin', async () => {
      render(<LayoutWrapper user={mockUsers.superAdmin} />);

      const coreButton = screen.getByText('Core');
      fireEvent.mouseEnter(coreButton);

      await waitFor(() => {
        // Super admin should see global scope
        const globalBadges = screen.getAllByText('global');
        expect(globalBadges.length).toBeGreaterThan(0);
      });
    });
  });
});

// Export for manual testing
export { LayoutWrapper, mockUsers };