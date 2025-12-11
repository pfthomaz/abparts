#!/bin/bash

# Test script to validate the removal of the 200 parts limit
# This script creates 500+ parts and tests system performance

echo "🚀 Testing Parts Limit Removal"
echo "================================"

# Check if Docker containers are running
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ Docker containers are not running. Starting them..."
    docker-compose up -d
    echo "⏳ Waiting for containers to be ready..."
    sleep 10
fi

# Check if the API is responding
echo "🔍 Checking API health..."
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ API is not responding. Please check the backend container."
    exit 1
fi

echo "✅ API is responding"

# Run the parts creation test
echo ""
echo "🔧 Running parts creation test..."
echo "================================"

# Execute the test script inside the backend container
docker-compose exec -T api python test_create_500_parts.py

# Check the exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Parts creation test completed successfully!"
    echo ""
    echo "🌐 Now testing API endpoints..."
    echo "================================"
    
    # Test the API endpoints
    docker-compose exec -T api python test_api_with_500_parts.py
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 All tests completed successfully!"
        echo ""
        echo "📋 Frontend Testing Instructions:"
        echo "1. Open the web interface: http://localhost:3000"
        echo "2. Login with:"
        echo "   - Username: superadmin"
        echo "   - Password: superadmin"
        echo "3. Navigate to the Parts page"
        echo "4. Verify you can see more than 200 parts"
        echo "5. Try creating a new part"
        echo "6. Test search and filtering functionality"
        echo "7. Check that pagination works correctly"
    else
        echo ""
        echo "❌ API tests failed!"
        echo "The parts were created but API access has issues."
        exit 1
    fi
else
    echo ""
    echo "❌ Parts creation test failed!"
    echo "Check the error messages above for details."
    exit 1
fi