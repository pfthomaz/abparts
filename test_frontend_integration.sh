#!/bin/bash

# Frontend Integration Test for User Reactivation Fix
# This script validates the complete reactivation flow from frontend perspective
# Requirements: 1.1, 1.2, 1.3, 3.4

set -e

API_BASE_URL="http://localhost:8000"
AUTH_TOKEN=""
TEST_USER_ID=""

echo "🚀 Starting Frontend Integration Tests for User Reactivation"
echo "======================================================================"

# Function to authenticate and get token
authenticate() {
    echo "🔐 Authenticating..."
    
    response=$(curl -s -X POST "$API_BASE_URL/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=oraseasee_admin&password=admin")
    
    if echo "$response" | grep -q "access_token"; then
        AUTH_TOKEN=$(echo "$response" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
        echo "✅ Authentication successful"
        return 0
    else
        echo "❌ Authentication failed: $response"
        return 1
    fi
}

# Function to get users and find a test user
get_test_user() {
    echo "📋 Getting user list to find test user..."
    
    response=$(curl -s -X GET "$API_BASE_URL/users" \
        -H "Authorization: Bearer $AUTH_TOKEN" \
        -H "Content-Type: application/json")
    
    echo "Debug: User response: $response"
    
    # Extract a user ID that's not the admin (look for superadmin user)
    TEST_USER_ID=$(echo "$response" | grep -o '"id":"[^"]*"' | grep -v "oraseasee_admin" | head -1 | cut -d'"' -f4)
    
    # If that doesn't work, just get the first user ID
    if [ -z "$TEST_USER_ID" ]; then
        TEST_USER_ID=$(echo "$response" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    fi
    
    if [ -n "$TEST_USER_ID" ]; then
        echo "✅ Using test user ID: $TEST_USER_ID"
        return 0
    else
        echo "❌ No suitable test user found"
        echo "Response was: $response"
        return 1
    fi
}

# Function to test user reactivation service
test_user_reactivation() {
    echo ""
    echo "🧪 Testing User Reactivation Service"
    echo "=================================================="
    
    # Step 1: Deactivate user first
    echo "🔒 Deactivating user for testing..."
    deactivate_response=$(curl -s -X PATCH "$API_BASE_URL/users/$TEST_USER_ID/deactivate" \
        -H "Authorization: Bearer $AUTH_TOKEN" \
        -H "Content-Type: application/json")
    
    if echo "$deactivate_response" | grep -q '"is_active":false'; then
        echo "✅ User deactivated successfully"
    else
        echo "❌ Failed to deactivate user: $deactivate_response"
        return 1
    fi
    
    # Step 2: Test reactivation
    echo "🔄 Testing reactivation service..."
    reactivate_response=$(curl -s -X PATCH "$API_BASE_URL/users/$TEST_USER_ID/reactivate" \
        -H "Authorization: Bearer $AUTH_TOKEN" \
        -H "Content-Type: application/json")
    
    if echo "$reactivate_response" | grep -q '"is_active":true'; then
        echo "✅ Reactivation service successful!"
        
        # Check status synchronization
        if echo "$reactivate_response" | grep -q '"user_status":"active"'; then
            echo "✅ Status fields are properly synchronized"
        else
            echo "❌ Status fields not synchronized properly"
            echo "Response: $reactivate_response"
            return 1
        fi
    else
        echo "❌ Reactivation failed: $reactivate_response"
        return 1
    fi
    
    # Step 3: Verify user list shows updated status
    echo "📋 Verifying user list refresh..."
    users_response=$(curl -s -X GET "$API_BASE_URL/users" \
        -H "Authorization: Bearer $AUTH_TOKEN" \
        -H "Content-Type: application/json")
    
    if echo "$users_response" | grep -A5 -B5 "$TEST_USER_ID" | grep -q '"is_active":true'; then
        echo "✅ User list shows correct updated status"
        return 0
    else
        echo "❌ User list does not show updated status"
        return 1
    fi
}

# Function to test error handling
test_error_handling() {
    echo ""
    echo "🧪 Testing Error Handling"
    echo "========================================"
    
    # Test 1: Non-existent user (404)
    echo "🔍 Testing non-existent user (404)..."
    error_response=$(curl -s -w "%{http_code}" -X PATCH "$API_BASE_URL/users/00000000-0000-0000-0000-000000000000/reactivate" \
        -H "Authorization: Bearer $AUTH_TOKEN" \
        -H "Content-Type: application/json")
    
    if echo "$error_response" | grep -q "404"; then
        echo "✅ Correct 404 error for non-existent user"
    else
        echo "❌ Wrong error response for non-existent user: $error_response"
        return 1
    fi
    
    # Test 2: Invalid UUID format (422)
    echo "🔍 Testing invalid UUID format (422)..."
    error_response=$(curl -s -w "%{http_code}" -X PATCH "$API_BASE_URL/users/invalid-uuid/reactivate" \
        -H "Authorization: Bearer $AUTH_TOKEN" \
        -H "Content-Type: application/json")
    
    if echo "$error_response" | grep -q "422"; then
        echo "✅ Correct 422 error for invalid UUID format"
        return 0
    else
        echo "❌ Wrong error response for invalid UUID: $error_response"
        return 1
    fi
}

# Function to test unauthorized access
test_unauthorized_access() {
    echo ""
    echo "🧪 Testing Unauthorized Access"
    echo "==================================="
    
    error_response=$(curl -s -w "%{http_code}" -X PATCH "$API_BASE_URL/users/$TEST_USER_ID/reactivate" \
        -H "Content-Type: application/json")
    
    if echo "$error_response" | grep -q "401"; then
        echo "✅ Correct unauthorized error returned"
        return 0
    else
        echo "❌ Wrong error response for unauthorized access: $error_response"
        return 1
    fi
}

# Main test execution
main() {
    local test_results=()
    local passed_count=0
    local total_count=0
    
    # Authenticate
    if ! authenticate; then
        echo "❌ Cannot proceed without authentication"
        exit 1
    fi
    
    # Get test user
    if ! get_test_user; then
        echo "❌ Cannot proceed without test user"
        exit 1
    fi
    
    # Run tests
    echo ""
    echo "Running integration tests..."
    
    # Test 1: User Reactivation Service
    total_count=$((total_count + 1))
    if test_user_reactivation; then
        test_results+=("✅ PASS - User Reactivation Service")
        passed_count=$((passed_count + 1))
    else
        test_results+=("❌ FAIL - User Reactivation Service")
    fi
    
    # Test 2: Error Handling
    total_count=$((total_count + 1))
    if test_error_handling; then
        test_results+=("✅ PASS - Error Handling")
        passed_count=$((passed_count + 1))
    else
        test_results+=("❌ FAIL - Error Handling")
    fi
    
    # Test 3: Unauthorized Access
    total_count=$((total_count + 1))
    if test_unauthorized_access; then
        test_results+=("✅ PASS - Unauthorized Access")
        passed_count=$((passed_count + 1))
    else
        test_results+=("❌ FAIL - Unauthorized Access")
    fi
    
    # Results summary
    echo ""
    echo "======================================================================"
    echo "📊 FRONTEND INTEGRATION TEST RESULTS"
    echo "======================================================================"
    
    for result in "${test_results[@]}"; do
        echo "$result"
    done
    
    echo ""
    echo "Overall: $passed_count/$total_count tests passed"
    
    if [ $passed_count -eq $total_count ]; then
        echo "🎉 All frontend integration tests passed!"
        echo "✅ User reactivation frontend integration is working correctly."
        exit 0
    else
        echo "⚠️  Some frontend integration tests failed."
        exit 1
    fi
}

# Run main function
main "$@"