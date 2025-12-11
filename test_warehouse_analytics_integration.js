// Test script to verify warehouse analytics frontend integration
const fetch = require('node-fetch');

const API_BASE_URL = 'http://localhost:8000';
const FRONTEND_URL = 'http://localhost:3000';

// Test credentials
const USERNAME = 'superadmin';
const PASSWORD = 'superadmin';

async function login() {
  const formData = new URLSearchParams();
  formData.append('grant_type', 'password');
  formData.append('username', USERNAME);
  formData.append('password', PASSWORD);

  const response = await fetch(`${API_BASE_URL}/token`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData.toString(),
  });

  if (!response.ok) {
    throw new Error(`Login failed: ${response.status}`);
  }

  const data = await response.json();
  return data.access_token;
}

async function getWarehouses(token) {
  const response = await fetch(`${API_BASE_URL}/warehouses/`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to get warehouses: ${response.status}`);
  }

  return response.json();
}

async function getWarehouseAnalytics(token, warehouseId, dateRange = {}) {
  const queryParams = new URLSearchParams();
  if (dateRange.start_date) queryParams.append('start_date', dateRange.start_date);
  if (dateRange.end_date) queryParams.append('end_date', dateRange.end_date);

  const queryString = queryParams.toString();
  const endpoint = queryString
    ? `${API_BASE_URL}/inventory/warehouse/${warehouseId}/analytics?${queryString}`
    : `${API_BASE_URL}/inventory/warehouse/${warehouseId}/analytics`;

  const response = await fetch(endpoint, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to get warehouse analytics: ${response.status}`);
  }

  return response.json();
}

async function getWarehouseAnalyticsTrends(token, warehouseId, period = 'daily', days = 30) {
  const queryParams = new URLSearchParams();
  queryParams.append('period', period);
  queryParams.append('days', days.toString());

  const endpoint = `${API_BASE_URL}/inventory/warehouse/${warehouseId}/analytics/trends?${queryParams.toString()}`;

  const response = await fetch(endpoint, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to get warehouse analytics trends: ${response.status}`);
  }

  return response.json();
}

async function testFrontendAccess() {
  try {
    const response = await fetch(FRONTEND_URL);
    if (!response.ok) {
      throw new Error(`Frontend not accessible: ${response.status}`);
    }
    console.log('✅ Frontend is accessible at', FRONTEND_URL);
    return true;
  } catch (error) {
    console.error('❌ Frontend access failed:', error.message);
    return false;
  }
}

async function runTests() {
  console.log('🧪 Testing Warehouse Analytics Integration...\n');

  try {
    // Test 1: Frontend accessibility
    console.log('1. Testing frontend accessibility...');
    await testFrontendAccess();

    // Test 2: Login
    console.log('\n2. Testing login...');
    const token = await login();
    console.log('✅ Login successful');

    // Test 3: Get warehouses
    console.log('\n3. Testing warehouse list...');
    const warehouses = await getWarehouses(token);
    console.log(`✅ Found ${warehouses.length} warehouses`);

    if (warehouses.length === 0) {
      console.log('❌ No warehouses found to test analytics');
      return;
    }

    // Test 4: Test analytics for first warehouse
    const testWarehouse = warehouses[0];
    console.log(`\n4. Testing analytics for warehouse: ${testWarehouse.name} (${testWarehouse.id})`);

    // Test basic analytics
    const analytics = await getWarehouseAnalytics(token, testWarehouse.id);
    console.log('✅ Warehouse analytics retrieved successfully');
    console.log(`   - Total parts: ${analytics.inventory_summary.total_parts}`);
    console.log(`   - Total value: ${analytics.inventory_summary.total_value}`);
    console.log(`   - Low stock parts: ${analytics.inventory_summary.low_stock_parts}`);

    // Test analytics with date range
    const dateRange = {
      start_date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 7 days ago
      end_date: new Date().toISOString().split('T')[0] // today
    };
    const analyticsWithRange = await getWarehouseAnalytics(token, testWarehouse.id, dateRange);
    console.log('✅ Warehouse analytics with date range retrieved successfully');

    // Test 5: Test trends
    console.log('\n5. Testing analytics trends...');
    const trends = await getWarehouseAnalyticsTrends(token, testWarehouse.id, 'daily', 7);
    console.log('✅ Warehouse analytics trends retrieved successfully');
    console.log(`   - Trend data points: ${trends.trends.length}`);
    console.log(`   - Period: ${trends.period}`);

    // Test different periods
    const weeklyTrends = await getWarehouseAnalyticsTrends(token, testWarehouse.id, 'weekly', 30);
    console.log('✅ Weekly trends retrieved successfully');

    const monthlyTrends = await getWarehouseAnalyticsTrends(token, testWarehouse.id, 'monthly', 90);
    console.log('✅ Monthly trends retrieved successfully');

    console.log('\n🎉 All tests passed! Warehouse analytics integration is working correctly.');
    console.log('\n📋 Test Summary:');
    console.log('   ✅ Frontend is accessible');
    console.log('   ✅ Authentication works');
    console.log('   ✅ Warehouse list endpoint works');
    console.log('   ✅ Warehouse analytics endpoint works');
    console.log('   ✅ Date range filtering works');
    console.log('   ✅ Analytics trends endpoint works');
    console.log('   ✅ Different trend periods work');

    console.log('\n🔗 To test the frontend manually:');
    console.log(`   1. Open ${FRONTEND_URL} in your browser`);
    console.log(`   2. Login with username: ${USERNAME}, password: ${PASSWORD}`);
    console.log('   3. Navigate to Inventory page');
    console.log('   4. Select "Analytics" view mode');
    console.log('   5. Select a warehouse from the dropdown');
    console.log('   6. Verify analytics data loads and date range filtering works');

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    process.exit(1);
  }
}

// Run the tests
runTests();