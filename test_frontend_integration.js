// Simple frontend integration test for organization form endpoints
const API_BASE_URL = 'http://localhost:8000';

// Mock authentication token (in real app this would come from login)
const mockToken = 'test-token';

// Test data
const testOrganizationData = {
  name: 'Test Supplier Organization',
  organization_type: 'supplier',
  parent_organization_id: '', // Will be set after getting potential parents
  address: '123 Test Street',
  contact_info: 'test@example.com',
  is_active: true
};

// Helper function to make API requests
async function apiRequest(endpoint, options = {}) {
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${mockToken}`
    }
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...defaultOptions,
    ...options,
    headers: { ...defaultOptions.headers, ...options.headers }
  });

  return response;
}

// Test 1: Get potential parent organizations
async function testPotentialParents() {
  console.log('Testing potential parents endpoint...');

  try {
    const response = await apiRequest('/organizations/potential-parents?organization_type=supplier');

    if (response.ok) {
      const data = await response.json();
      console.log('✅ Potential parents endpoint working');
      console.log('Response:', JSON.stringify(data, null, 2));
      return data;
    } else {
      console.log('❌ Potential parents endpoint failed');
      console.log('Status:', response.status);
      console.log('Response:', await response.text());
      return null;
    }
  } catch (error) {
    console.log('❌ Network error:', error.message);
    return null;
  }
}

// Test 2: Validate organization data
async function testValidateOrganization(orgData) {
  console.log('\nTesting validation endpoint...');

  try {
    const response = await apiRequest('/organizations/validate', {
      method: 'POST',
      body: JSON.stringify(orgData)
    });

    if (response.ok) {
      const data = await response.json();
      console.log('✅ Validation endpoint working');
      console.log('Response:', JSON.stringify(data, null, 2));
      return data;
    } else {
      console.log('❌ Validation endpoint failed');
      console.log('Status:', response.status);
      console.log('Response:', await response.text());
      return null;
    }
  } catch (error) {
    console.log('❌ Network error:', error.message);
    return null;
  }
}

// Test 3: Simulate frontend workflow
async function testFrontendWorkflow() {
  console.log('\n=== Testing Frontend Integration Workflow ===\n');

  // Step 1: Get potential parents (simulates dropdown loading)
  const potentialParents = await testPotentialParents();

  if (potentialParents && potentialParents.data && potentialParents.data.length > 0) {
    // Use first potential parent
    testOrganizationData.parent_organization_id = potentialParents.data[0].id;
    console.log(`Selected parent: ${potentialParents.data[0].name}`);
  } else {
    console.log('⚠️  No potential parents found, testing without parent');
  }

  // Step 2: Validate organization data (simulates form validation)
  const validationResult = await testValidateOrganization(testOrganizationData);

  if (validationResult) {
    if (validationResult.valid) {
      console.log('✅ Organization data is valid - form would allow submission');
    } else {
      console.log('❌ Organization data is invalid:');
      validationResult.errors.forEach(error => {
        console.log(`  - ${error.field}: ${error.message}`);
      });
    }
  }

  console.log('\n=== Frontend Integration Test Complete ===');
}

// Run the test
testFrontendWorkflow().catch(console.error);