// Test script to verify Core dropdown displays correctly
// This test verifies that the Core navigation category contains the expected items

import { getNavigationItems, getUIConfiguration, USER_ROLES, PERMISSIONS } from './utils/permissions.js';

// Mock user objects for testing different roles
const mockUsers = {
  superAdmin: {
    id: 1,
    username: 'superadmin',
    name: 'Super Admin',
    email: 'super@example.com',
    role: USER_ROLES.SUPER_ADMIN,
    organization_id: 1,
    organization: { name: 'Oraseas EE' }
  },
  admin: {
    id: 2,
    username: 'admin',
    name: 'Admin User',
    email: 'admin@example.com',
    role: USER_ROLES.ADMIN,
    organization_id: 2,
    organization: { name: 'Customer Org' }
  },
  user: {
    id: 3,
    username: 'user',
    name: 'Regular User',
    email: 'user@example.com',
    role: USER_ROLES.USER,
    organization_id: 2,
    organization: { name: 'Customer Org' }
  }
};

// Test function to verify Core dropdown content
function testCoreDropdownContent() {
  console.log('=== Testing Core Dropdown Content ===\n');

  Object.entries(mockUsers).forEach(([userType, user]) => {
    console.log(`Testing ${userType.toUpperCase()} user:`);
    console.log(`- Role: ${user.role}`);
    console.log(`- Organization: ${user.organization.name}`);

    const navigationItems = getNavigationItems(user);
    const uiConfig = getUIConfiguration(user);

    // Filter items that belong to 'core' category
    const coreItems = navigationItems.filter(item => item.category === 'core');

    console.log(`- Core category enabled: ${uiConfig.navigationCategories.core}`);
    console.log(`- Core items count: ${coreItems.length}`);

    if (coreItems.length > 0) {
      console.log('- Core items:');
      coreItems.forEach(item => {
        console.log(`  * ${item.label} (${item.path}) - ${item.description}`);
        if (item.accessScope) {
          console.log(`    Access scope: ${item.accessScope}`);
        }
      });
    } else {
      console.log('- No core items found!');
    }

    console.log('');
  });
}

// Test function to verify navigation categorization
function testNavigationCategorization() {
  console.log('=== Testing Navigation Categorization ===\n');

  const user = mockUsers.superAdmin; // Use super admin to see all items
  const navigationItems = getNavigationItems(user);

  // Group items by category
  const itemsByCategory = navigationItems.reduce((acc, item) => {
    const category = item.category || 'uncategorized';
    if (!acc[category]) acc[category] = [];
    acc[category].push(item);
    return acc;
  }, {});

  console.log('Items by category:');
  Object.entries(itemsByCategory).forEach(([category, items]) => {
    console.log(`\n${category.toUpperCase()}:`);
    items.forEach(item => {
      console.log(`  - ${item.label} (${item.path})`);
    });
  });
}

// Test function to verify expected core items are present
function testExpectedCoreItems() {
  console.log('\n=== Testing Expected Core Items ===\n');

  const expectedCoreItems = [
    { path: '/', label: 'Dashboard' },
    { path: '/parts', label: 'Parts' },
    { path: '/inventory', label: 'Inventory' },
    { path: '/orders', label: 'Orders' },
    { path: '/warehouses', label: 'Warehouses' } // Only for admin users
  ];

  Object.entries(mockUsers).forEach(([userType, user]) => {
    console.log(`Testing expected core items for ${userType.toUpperCase()}:`);

    const navigationItems = getNavigationItems(user);
    const coreItems = navigationItems.filter(item => item.category === 'core');

    expectedCoreItems.forEach(expectedItem => {
      const foundItem = coreItems.find(item => item.path === expectedItem.path);

      if (foundItem) {
        console.log(`  ✓ ${expectedItem.label} - Found`);
      } else {
        // Check if this item should be available to this user type
        if (expectedItem.path === '/warehouses' && user.role === USER_ROLES.USER) {
          console.log(`  - ${expectedItem.label} - Not available to regular users (expected)`);
        } else {
          console.log(`  ✗ ${expectedItem.label} - Missing!`);
        }
      }
    });

    console.log('');
  });
}

// Test function to verify dropdown visibility logic
function testDropdownVisibility() {
  console.log('=== Testing Dropdown Visibility Logic ===\n');

  Object.entries(mockUsers).forEach(([userType, user]) => {
    console.log(`Testing dropdown visibility for ${userType.toUpperCase()}:`);

    const navigationItems = getNavigationItems(user);
    const uiConfig = getUIConfiguration(user);

    // Group items by category
    const itemsByCategory = navigationItems.reduce((acc, item) => {
      const category = item.category || 'other';
      if (!acc[category]) acc[category] = [];
      acc[category].push(item);
      return acc;
    }, {});

    const categoryOrder = ['core', 'inventory', 'operations', 'administration'];

    categoryOrder.forEach(category => {
      const categoryEnabled = uiConfig.navigationCategories[category];
      const hasItems = itemsByCategory[category] && itemsByCategory[category].length > 0;

      console.log(`  ${category}: enabled=${categoryEnabled}, hasItems=${hasItems}`);

      if (categoryEnabled && !hasItems) {
        console.log(`    ⚠️  Category is enabled but has no items!`);
      } else if (!categoryEnabled && hasItems) {
        console.log(`    ⚠️  Category has items but is disabled!`);
      } else if (categoryEnabled && hasItems) {
        console.log(`    ✓ Category properly configured`);
      }
    });

    console.log('');
  });
}

// Run all tests
function runAllTests() {
  console.log('Core Dropdown Verification Tests');
  console.log('================================\n');

  try {
    testCoreDropdownContent();
    testNavigationCategorization();
    testExpectedCoreItems();
    testDropdownVisibility();

    console.log('=== Test Summary ===');
    console.log('All tests completed. Review the output above for any issues.');

  } catch (error) {
    console.error('Test failed with error:', error);
  }
}

// Export for use in other contexts
export {
  testCoreDropdownContent,
  testNavigationCategorization,
  testExpectedCoreItems,
  testDropdownVisibility,
  runAllTests
};

// Run tests if this file is executed directly
if (typeof window === 'undefined') {
  runAllTests();
}