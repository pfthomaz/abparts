// Test script to verify Core dropdown displays correctly with different user roles
const { getNavigationItems, getUIConfiguration, USER_ROLES, ORGANIZATION_TYPES } = require('./utils/permissions.js');

// Mock user objects for different roles
const mockUsers = {
  superAdmin: {
    id: '1',
    name: 'Super Admin',
    email: 'super@example.com',
    role: USER_ROLES.SUPER_ADMIN,
    organization_id: '1',
    organization: {
      id: '1',
      name: 'Oraseas EE',
      type: ORGANIZATION_TYPES.ORASEAS_EE
    }
  },
  admin: {
    id: '2',
    name: 'Admin User',
    email: 'admin@example.com',
    role: USER_ROLES.ADMIN,
    organization_id: '2',
    organization: {
      id: '2',
      name: 'Customer Org',
      type: ORGANIZATION_TYPES.CUSTOMER
    }
  },
  user: {
    id: '3',
    name: 'Regular User',
    email: 'user@example.com',
    role: USER_ROLES.USER,
    organization_id: '2',
    organization: {
      id: '2',
      name: 'Customer Org',
      type: ORGANIZATION_TYPES.CUSTOMER
    }
  }
};

// Function to test navigation for a specific user role
function testNavigationForRole(roleName, user) {
  console.log(`\n=== Testing Navigation for ${roleName} ===`);

  const navigationItems = getNavigationItems(user);
  const uiConfig = getUIConfiguration(user);

  // Group navigation items by category
  const navigationByCategory = navigationItems.reduce((acc, item) => {
    const category = item.category || 'other';
    if (!acc[category]) acc[category] = [];
    acc[category].push(item);
    return acc;
  }, {});

  console.log('UI Configuration:');
  console.log('- Show Global Filters:', uiConfig.showGlobalFilters);
  console.log('- Navigation Categories:', uiConfig.navigationCategories);

  console.log('\nCore Category Items:');
  if (navigationByCategory.core && navigationByCategory.core.length > 0) {
    navigationByCategory.core.forEach((item, index) => {
      console.log(`${index + 1}. ${item.label}`);
      console.log(`   - Path: ${item.path}`);
      console.log(`   - Description: ${item.description}`);
      console.log(`   - Access Scope: ${item.accessScope || 'organization'}`);
      console.log(`   - Permission: ${item.permission || 'none'}`);
    });
  } else {
    console.log('No items in Core category');
  }

  console.log('\nAll Categories:');
  Object.keys(navigationByCategory).forEach(category => {
    console.log(`- ${category}: ${navigationByCategory[category].length} items`);
  });

  return {
    coreItems: navigationByCategory.core || [],
    allCategories: navigationByCategory,
    uiConfig
  };
}

// Test all user roles
console.log('=== Navigation Core Dropdown Verification Test ===');

const results = {};
results.superAdmin = testNavigationForRole('Super Admin', mockUsers.superAdmin);
results.admin = testNavigationForRole('Admin', mockUsers.admin);
results.user = testNavigationForRole('Regular User', mockUsers.user);

// Verify Core dropdown requirements
console.log('\n=== Verification Results ===');

// Check if Core category has items for each role
Object.keys(results).forEach(role => {
  const result = results[role];
  const coreItemCount = result.coreItems.length;

  console.log(`\n${role.toUpperCase()}:`);
  console.log(`- Core items count: ${coreItemCount}`);
  console.log(`- Core category enabled: ${result.uiConfig.navigationCategories.core}`);

  if (coreItemCount > 0) {
    console.log('- Core items in logical order:');
    result.coreItems.forEach((item, index) => {
      console.log(`  ${index + 1}. ${item.label} (${item.path})`);
    });

    // Check for expected core items based on requirements
    const expectedCoreItems = ['Dashboard', 'Parts', 'Inventory', 'Orders', 'Warehouses'];
    const actualCoreItems = result.coreItems.map(item => item.label);

    console.log('- Expected vs Actual core items:');
    expectedCoreItems.forEach(expected => {
      const found = actualCoreItems.includes(expected);
      console.log(`  ${expected}: ${found ? '✓' : '✗'}`);
    });
  } else {
    console.log('- ✗ Core dropdown is empty');
  }
});

// Summary
console.log('\n=== Summary ===');
const allRolesHaveCoreItems = Object.values(results).every(result => result.coreItems.length > 0);
console.log(`All roles have Core items: ${allRolesHaveCoreItems ? '✓' : '✗'}`);

if (!allRolesHaveCoreItems) {
  console.log('ISSUE: Some user roles do not have items in the Core dropdown');
} else {
  console.log('SUCCESS: All user roles have appropriate items in the Core dropdown');
}