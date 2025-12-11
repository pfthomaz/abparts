#!/usr/bin/env node
/**
 * Frontend Integration Test for User Reactivation Fix
 * 
 * This test validates the complete reactivation flow from frontend to backend:
 * - Tests the userService.reactivateUser() function
 * - Validates error handling and response processing
 * - Ensures status field synchronization is properly handled
 * - Tests user list refresh functionality
 * 
 * Requirements: 1.1, 1.2, 1.3, 3.4
 */

const fetch = (...args) => import('node-fetch').then(({ default: fetch }) => fetch(...args));

// Mock localStorage for Node.js environment
global.localStorage = {
  getItem: (key) => {
    if (key === 'authToken') {
      return global.testAuthToken;
    }
    return null;
  },
  setItem: (key, value) => {
    if (key === 'authToken') {
      global.testAuthToken = value;
    }
  },
  removeItem: (key) => {
    if (key === 'authToken') {
      global.testAuthToken = null;
    }
  }
};

// Mock Headers for Node.js environment
global.Headers = fetch.Headers;
global.fetch = fetch;

// Import the API service (we'll need to adjust the import path)
const API_BASE_URL = 'http://localhost:8000';

/**
 * Simplified API service for testing
 */
const api = {
  async request(endpoint, method = 'GET', body = null) {
    const token = global.localStorage.getItem('authToken');
    const headers = new Headers();

    if (!(body instanceof FormData)) {
      headers.append('Content-Type', 'application/json');
    }

    if (token) {
      headers.append('Authorization', `Bearer ${token}`);
    }

    const config = {
      method,
      headers,
    };

    if (body) {
      config.body = body instanceof FormData ? body : JSON.stringify(body);
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        detail: `Request failed with status ${response.status}`
      }));

      const error = new Error(errorData.detail || `Request failed with status ${response.status}`);
      error.response = {
        status: response.status,
        data: errorData,
        headers: response.headers
      };
      throw error;
    }

    if (response.status === 204) {
      return null;
    }

    return response.json();
  },

  get: (endpoint) => api.request(endpoint, 'GET'),
  post: (endpoint, body) => api.request(endpoint, 'POST', body),
  put: (endpoint, body) => api.request(endpoint, 'PUT', body),
  patch: (endpoint, body) => api.request(endpoint, 'PATCH', body),
  delete: (endpoint) => api.request(endpoint, 'DELETE'),
};

/**
 * User service functions for testing
 */
const userService = {
  getUsers: () => api.get('/users'),
  getUser: (userId) => api.get(`/users/${userId}`),
  deactivateUser: (userId) => api.patch(`/users/${userId}/deactivate`),
  reactivateUser: (userId) => api.patch(`/users/${userId}/reactivate`),
};

/**
 * Authentication helper
 */
async function authenticate() {
  console.log('🔐 Authenticating...');

  const loginData = new URLSearchParams({
    username: 'oraseasee_admin',
    password: 'admin'
  });

  const response = await fetch(`${API_BASE_URL}/token`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: loginData
  });

  if (!response.ok) {
    throw new Error(`Authentication failed: ${response.status}`);
  }

  const tokenData = await response.json();
  global.localStorage.setItem('authToken', tokenData.access_token);
  console.log('✅ Authentication successful');
  return tokenData.access_token;
}

/**
 * Test the user reactivation service function
 */
async function testUserReactivationService() {
  console.log('\n🧪 Testing User Reactivation Service');
  console.log('='.repeat(50));

  try {
    // Step 1: Get users to find a test subject
    console.log('📋 Getting user list...');
    const users = await userService.getUsers();

    if (!users || users.length === 0) {
      throw new Error('No users found for testing');
    }

    // Find a user that's not the admin
    const testUser = users.find(u => u.username !== 'oraseasee_admin');
    if (!testUser) {
      throw new Error('No suitable test user found');
    }

    console.log(`✅ Using test user: ${testUser.username} (ID: ${testUser.id})`);
    console.log(`   Current status: is_active=${testUser.is_active}, user_status=${testUser.user_status}`);

    // Step 2: Deactivate the user first (if active)
    if (testUser.is_active && testUser.user_status === 'active') {
      console.log('🔒 Deactivating user for testing...');
      const deactivatedUser = await userService.deactivateUser(testUser.id);
      console.log(`✅ User deactivated: is_active=${deactivatedUser.is_active}, user_status=${deactivatedUser.user_status}`);
    }

    // Step 3: Test reactivation service
    console.log('🔄 Testing reactivation service...');
    const reactivatedUser = await userService.reactivateUser(testUser.id);

    console.log(`✅ Reactivation service successful!`);
    console.log(`   Response: is_active=${reactivatedUser.is_active}, user_status=${reactivatedUser.user_status}`);

    // Step 4: Validate status synchronization
    if (reactivatedUser.is_active === true && reactivatedUser.user_status === 'active') {
      console.log('✅ Status fields are properly synchronized');
    } else {
      throw new Error(`Status fields not synchronized: is_active=${reactivatedUser.is_active}, user_status=${reactivatedUser.user_status}`);
    }

    // Step 5: Verify user list shows updated status
    console.log('📋 Verifying user list refresh...');
    const updatedUsers = await userService.getUsers();
    const updatedUser = updatedUsers.find(u => u.id === testUser.id);

    if (!updatedUser) {
      throw new Error('User not found in updated user list');
    }

    if (updatedUser.is_active === true && updatedUser.user_status === 'active') {
      console.log('✅ User list shows correct updated status');
    } else {
      throw new Error(`User list shows incorrect status: is_active=${updatedUser.is_active}, user_status=${updatedUser.user_status}`);
    }

    return true;

  } catch (error) {
    console.error('❌ User reactivation service test failed:', error.message);
    if (error.response) {
      console.error('   Response status:', error.response.status);
      console.error('   Response data:', error.response.data);
    }
    return false;
  }
}

/**
 * Test error handling scenarios
 */
async function testErrorHandling() {
  console.log('\n🧪 Testing Error Handling');
  console.log('='.repeat(40));

  const testCases = [
    {
      name: 'Non-existent user (404)',
      userId: '00000000-0000-0000-0000-000000000000',
      expectedStatus: 404
    },
    {
      name: 'Invalid UUID format (422)',
      userId: 'invalid-uuid',
      expectedStatus: 422
    }
  ];

  let passedTests = 0;

  for (const testCase of testCases) {
    try {
      console.log(`🔍 Testing ${testCase.name}...`);
      await userService.reactivateUser(testCase.userId);
      console.log(`❌ Expected error but got success for ${testCase.name}`);
    } catch (error) {
      if (error.response && error.response.status === testCase.expectedStatus) {
        console.log(`✅ Correct ${testCase.expectedStatus} error for ${testCase.name}`);
        passedTests++;
      } else {
        console.log(`❌ Wrong error status for ${testCase.name}: expected ${testCase.expectedStatus}, got ${error.response?.status || 'unknown'}`);
      }
    }
  }

  return passedTests === testCases.length;
}

/**
 * Test unauthorized access
 */
async function testUnauthorizedAccess() {
  console.log('\n🧪 Testing Unauthorized Access');
  console.log('='.repeat(35));

  // Remove auth token temporarily
  const originalToken = global.localStorage.getItem('authToken');
  global.localStorage.removeItem('authToken');

  try {
    await userService.reactivateUser('00000000-0000-0000-0000-000000000000');
    console.log('❌ Expected unauthorized error but got success');
    return false;
  } catch (error) {
    if (error.response && (error.response.status === 401 || error.response.status === 403)) {
      console.log('✅ Correct unauthorized error returned');
      return true;
    } else {
      console.log(`❌ Wrong error status: expected 401/403, got ${error.response?.status || 'unknown'}`);
      return false;
    }
  } finally {
    // Restore auth token
    global.localStorage.setItem('authToken', originalToken);
  }
}

/**
 * Main test runner
 */
async function runFrontendIntegrationTests() {
  console.log('🚀 Starting Frontend Integration Tests for User Reactivation');
  console.log('='.repeat(70));

  const testResults = [];

  try {
    // Authenticate first
    await authenticate();

    // Run tests
    testResults.push({
      name: 'User Reactivation Service',
      passed: await testUserReactivationService()
    });

    testResults.push({
      name: 'Error Handling',
      passed: await testErrorHandling()
    });

    testResults.push({
      name: 'Unauthorized Access',
      passed: await testUnauthorizedAccess()
    });

    // Results summary
    console.log('\n' + '='.repeat(70));
    console.log('📊 FRONTEND INTEGRATION TEST RESULTS');
    console.log('='.repeat(70));

    let passedCount = 0;
    const totalCount = testResults.length;

    testResults.forEach(result => {
      const status = result.passed ? '✅ PASS' : '❌ FAIL';
      console.log(`${status} - ${result.name}`);
      if (result.passed) passedCount++;
    });

    console.log(`\nOverall: ${passedCount}/${totalCount} tests passed`);

    if (passedCount === totalCount) {
      console.log('🎉 All frontend integration tests passed!');
      console.log('✅ User reactivation frontend integration is working correctly.');
      return true;
    } else {
      console.log('⚠️  Some frontend integration tests failed.');
      return false;
    }

  } catch (error) {
    console.error('❌ Frontend integration tests failed with error:', error.message);
    return false;
  }
}

// Run the tests if this file is executed directly
if (require.main === module) {
  runFrontendIntegrationTests()
    .then(success => {
      process.exit(success ? 0 : 1);
    })
    .catch(error => {
      console.error('Fatal error:', error);
      process.exit(1);
    });
}

module.exports = {
  runFrontendIntegrationTests,
  userService,
  api
};