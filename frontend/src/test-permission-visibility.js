// Test script for permission-based navigation visibility
// This script tests various user permission combinations to ensure navigation items
// are properly hidden when users lack the required permissions

import { getNavigationItems, getUIConfiguration, PERMISSIONS, USER_ROLES } from './utils/permissions.js';

// Mock user objects with different permission levels
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
  },

  // User with no permissions (edge case)
  noPermissions: {
    id: '4',
    username: 'noperm',
    name: 'No Permissions',
    email: 'noperm@example.com',
    role: 'invalid_role',
    organization_id: '2',
    organization: { name: 'Customer Org' }
  }
};

// Test cases for different permission scenarios
const testCases = [
  {
    name: 'Super Admin Navigation',
    user: mockUsers.superAdmin,
    expectedItems: [
      'Dashboard', 'Organizations', 'Parts', 'Inventory', 'Orders',
      'Stocktake', 'Machines', 'Users', 'Warehouses', 'Transactions'
    ],
    expectedCategories: ['core', 'inventory', 'operations', 'administration'],
    shouldHaveGlobalAccess: true
  },

  {
    name: 'Admin Navigation',
    user: mockUsers.admin,
    expectedItems: [
      'Dashboard', 'Parts', 'Inventory', 'Orders', 'Stocktake',
      'Machines', 'Users', 'Warehouses', 'Transactions'
    ],
    hiddenItems: ['Organizations'],
    expectedCategories: ['core', 'inventory', 'operations', 'administration'],
    shouldHaveGlobalAccess: false
  },

  {
    name: 'Regular User Navigation',
    user: mockUsers.user,
    expectedItems: [
      'Dashboard', 'Parts', 'Inventory', 'Orders', 'Machines', 'Transactions'
    ],
    hiddenItems: ['Organizations', 'Stocktake', 'Users', 'Warehouses'],
    expectedCategories: ['core', 'operations'],
    hiddenCategories: ['administration'],
    shouldHaveGlobalAccess: false
  },

  {
    name: 'No Permissions User',
    user: mockUsers.noPermissions,
    expectedItems: ['Dashboard'],
    hiddenItems: [
      'Organizations', 'Parts', 'Inventory', 'Orders', 'Stocktake',
      'Machines', 'Users', 'Warehouses', 'Transactions'
    ],
    expectedCategories: ['core'],
    hiddenCategories: ['inventory', 'operations', 'administration'],
    shouldHaveGlobalAccess: false
  }
];

// Core navigation items that should be in the 'core' category
const coreNavigationItems = ['Dashboard', 'Parts', 'Inventory', 'Orders', 'Warehouses'];

// Function to run all tests
function runPermissionVisibilityTests() {
  console.log('🧪 Running Permission-Based Navigation Visibility Tests\n');

  let totalTests = 0;
  let passedTests = 0;
  let failedTests = [];

  testCases.forEach(testCase => {
    console.log(`\n📋 Testing: ${testCase.name}`);
    console.log(`👤 User: ${testCase.user.name} (${testCase.user.role})`);

    const navigationItems = getNavigationItems(testCase.user);
    const uiConfig = getUIConfiguration(testCase.user);

    // Test 1: Check expected items are present
    totalTests++;
    const actualItems = navigationItems.map(item => item.label);
    const missingExpected = testCase.expectedItems.filter(item => !actualItems.includes(item));

    if (missingExpected.length === 0) {
      console.log('✅ All expected navigation items are present');
      passedTests++;
    } else {
      console.log(`❌ Missing expected items: ${missingExpected.join(', ')}`);
      failedTests.push(`${testCase.name}: Missing expected items - ${missingExpected.join(', ')}`);
    }

    // Test 2: Check hidden items are not present
    if (testCase.hiddenItems) {
      totalTests++;
      const unexpectedItems = testCase.hiddenItems.filter(item => actualItems.includes(item));

      if (unexpectedItems.length === 0) {
        console.log('✅ All restricted items are properly hidden');
        passedTests++;
      } else {
        console.log(`❌ Unexpected items visible: ${unexpectedItems.join(', ')}`);
        failedTests.push(`${testCase.name}: Unexpected items visible - ${unexpectedItems.join(', ')}`);
      }
    }

    // Test 3: Check category visibility
    totalTests++;
    const visibleCategories = Object.keys(uiConfig.navigationCategories)
      .filter(cat => uiConfig.navigationCategories[cat]);
    const missingCategories = testCase.expectedCategories.filter(cat => !visibleCategories.includes(cat));

    if (missingCategories.length === 0) {
      console.log('✅ All expected categories are visible');
      passedTests++;
    } else {
      console.log(`❌ Missing expected categories: ${missingCategories.join(', ')}`);
      failedTests.push(`${testCase.name}: Missing expected categories - ${missingCategories.join(', ')}`);
    }

    // Test 4: Check hidden categories
    if (testCase.hiddenCategories) {
      totalTests++;
      const unexpectedCategories = testCase.hiddenCategories.filter(cat => visibleCategories.includes(cat));

      if (unexpectedCategories.length === 0) {
        console.log('✅ All restricted categories are properly hidden');
        passedTests++;
      } else {
        console.log(`❌ Unexpected categories visible: ${unexpectedCategories.join(', ')}`);
        failedTests.push(`${testCase.name}: Unexpected categories visible - ${unexpectedCategories.join(', ')}`);
      }
    }

    // Test 5: Check global access scope
    totalTests++;
    const hasGlobalAccess = uiConfig.showGlobalFilters;

    if (hasGlobalAccess === testCase.shouldHaveGlobalAccess) {
      console.log(`✅ Global access scope correct: ${hasGlobalAccess}`);
      passedTests++;
    } else {
      console.log(`❌ Global access scope incorrect. Expected: ${testCase.shouldHaveGlobalAccess}, Got: ${hasGlobalAccess}`);
      failedTests.push(`${testCase.name}: Incorrect global access scope`);
    }

    // Test 6: Check Core category population
    totalTests++;
    const coreItems = navigationItems
      .filter(item => item.category === 'core')
      .map(item => item.label);

    const expectedCoreItems = coreNavigationItems.filter(item => actualItems.includes(item));
    const missingCoreItems = expectedCoreItems.filter(item => !coreItems.includes(item));

    if (missingCoreItems.length === 0) {
      console.log('✅ Core category properly populated');
      passedTests++;
    } else {
      console.log(`❌ Core category missing items: ${missingCoreItems.join(', ')}`);
      failedTests.push(`${testCase.name}: Core category missing items - ${missingCoreItems.join(', ')}`);
    }

    // Display current navigation state
    console.log(`📊 Navigation Items (${actualItems.length}): ${actualItems.join(', ')}`);
    console.log(`📂 Visible Categories: ${visibleCategories.join(', ')}`);
    console.log(`🌐 Global Access: ${hasGlobalAccess ? 'Yes' : 'No'}`);
  });

  // Test specific permission combinations
  console.log('\n🔍 Testing Specific Permission Combinations\n');

  // Test: User with only VIEW_PARTS permission
  totalTests++;
  const partsOnlyUser = {
    ...mockUsers.user,
    role: 'custom_role' // This will result in no default permissions
  };

  // Mock a user that would only have VIEW_PARTS (this is theoretical since our current system uses role-based permissions)
  const partsOnlyNavigation = getNavigationItems(partsOnlyUser);
  const partsOnlyItems = partsOnlyNavigation.map(item => item.label);

  // Since our system is role-based, a user with invalid role should only see Dashboard
  if (partsOnlyItems.length === 1 && partsOnlyItems.includes('Dashboard')) {
    console.log('✅ User with invalid role only sees Dashboard');
    passedTests++;
  } else {
    console.log(`❌ User with invalid role sees unexpected items: ${partsOnlyItems.join(', ')}`);
    failedTests.push('Invalid role user sees unexpected items');
  }

  // Test: Verify permission-based access scope indicators
  totalTests++;
  const adminNavigation = getNavigationItems(mockUsers.admin);
  const adminPartsItem = adminNavigation.find(item => item.label === 'Parts');

  if (adminPartsItem && adminPartsItem.accessScope === 'organization') {
    console.log('✅ Admin user has correct organization-scoped access for Parts');
    passedTests++;
  } else {
    console.log('❌ Admin user access scope incorrect for Parts');
    failedTests.push('Admin user access scope incorrect');
  }

  totalTests++;
  const superAdminNavigation = getNavigationItems(mockUsers.superAdmin);
  const superAdminPartsItem = superAdminNavigation.find(item => item.label === 'Parts');

  if (superAdminPartsItem && superAdminPartsItem.accessScope === 'global') {
    console.log('✅ Super Admin user has correct global access for Parts');
    passedTests++;
  } else {
    console.log('❌ Super Admin user access scope incorrect for Parts');
    failedTests.push('Super Admin user access scope incorrect');
  }

  // Summary
  console.log('\n📈 Test Results Summary');
  console.log('========================');
  console.log(`Total Tests: ${totalTests}`);
  console.log(`Passed: ${passedTests}`);
  console.log(`Failed: ${totalTests - passedTests}`);
  console.log(`Success Rate: ${((passedTests / totalTests) * 100).toFixed(1)}%`);

  if (failedTests.length > 0) {
    console.log('\n❌ Failed Tests:');
    failedTests.forEach((failure, index) => {
      console.log(`${index + 1}. ${failure}`);
    });
  } else {
    console.log('\n🎉 All tests passed!');
  }

  return {
    total: totalTests,
    passed: passedTests,
    failed: totalTests - passedTests,
    failedTests: failedTests
  };
}

// Function to test edge cases
function testEdgeCases() {
  console.log('\n🔬 Testing Edge Cases\n');

  let edgeTests = 0;
  let edgePassed = 0;
  let edgeFailures = [];

  // Test 1: Null user
  edgeTests++;
  try {
    const nullNavigation = getNavigationItems(null);
    if (nullNavigation.length === 0) {
      console.log('✅ Null user returns empty navigation');
      edgePassed++;
    } else {
      console.log('❌ Null user should return empty navigation');
      edgeFailures.push('Null user returns navigation items');
    }
  } catch (error) {
    console.log('❌ Null user test threw error:', error.message);
    edgeFailures.push('Null user test error');
  }

  // Test 2: User without organization
  edgeTests++;
  const userWithoutOrg = {
    ...mockUsers.user,
    organization_id: null,
    organization: null
  };

  try {
    const noOrgNavigation = getNavigationItems(userWithoutOrg);
    const noOrgItems = noOrgNavigation.map(item => item.label);

    // Should still get basic navigation items
    if (noOrgItems.includes('Dashboard')) {
      console.log('✅ User without organization gets basic navigation');
      edgePassed++;
    } else {
      console.log('❌ User without organization should get basic navigation');
      edgeFailures.push('User without organization navigation failed');
    }
  } catch (error) {
    console.log('❌ User without organization test threw error:', error.message);
    edgeFailures.push('User without organization test error');
  }

  // Test 3: User with undefined role
  edgeTests++;
  const undefinedRoleUser = {
    ...mockUsers.user,
    role: undefined
  };

  try {
    const undefinedRoleNavigation = getNavigationItems(undefinedRoleUser);
    const undefinedRoleItems = undefinedRoleNavigation.map(item => item.label);

    // Should only get Dashboard
    if (undefinedRoleItems.length === 1 && undefinedRoleItems.includes('Dashboard')) {
      console.log('✅ User with undefined role only gets Dashboard');
      edgePassed++;
    } else {
      console.log(`❌ User with undefined role should only get Dashboard, got: ${undefinedRoleItems.join(', ')}`);
      edgeFailures.push('User with undefined role navigation incorrect');
    }
  } catch (error) {
    console.log('❌ User with undefined role test threw error:', error.message);
    edgeFailures.push('User with undefined role test error');
  }

  console.log(`\n📊 Edge Case Results: ${edgePassed}/${edgeTests} passed`);

  return {
    total: edgeTests,
    passed: edgePassed,
    failed: edgeTests - edgePassed,
    failures: edgeFailures
  };
}

// Main test execution
if (typeof window === 'undefined') {
  // Running in Node.js environment
  const mainResults = runPermissionVisibilityTests();
  const edgeResults = testEdgeCases();

  const totalTests = mainResults.total + edgeResults.total;
  const totalPassed = mainResults.passed + edgeResults.passed;
  const totalFailed = mainResults.failed + edgeResults.failed;

  console.log('\n🏁 Final Results');
  console.log('================');
  console.log(`Overall Tests: ${totalTests}`);
  console.log(`Overall Passed: ${totalPassed}`);
  console.log(`Overall Failed: ${totalFailed}`);
  console.log(`Overall Success Rate: ${((totalPassed / totalTests) * 100).toFixed(1)}%`);

  // Exit with appropriate code
  process.exit(totalFailed === 0 ? 0 : 1);
} else {
  // Running in browser environment
  window.runPermissionVisibilityTests = runPermissionVisibilityTests;
  window.testEdgeCases = testEdgeCases;
  console.log('Permission visibility tests loaded. Run runPermissionVisibilityTests() to execute.');
}

export { runPermissionVisibilityTests, testEdgeCases };