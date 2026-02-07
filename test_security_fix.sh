#!/bin/bash

echo "=========================================="
echo "SECURITY FIX VERIFICATION TEST"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Get organization IDs
echo "1. Getting organization IDs..."
KEF_ORG_ID=$(docker-compose exec -T db psql -U abparts_user -d abparts_dev -t -c "SELECT id FROM organizations WHERE name LIKE '%Kefalonia%' LIMIT 1;" | tr -d ' \n')
ORASEAS_ORG_ID=$(docker-compose exec -T db psql -U abparts_user -d abparts_dev -t -c "SELECT id FROM organizations WHERE name LIKE '%Oraseas%' LIMIT 1;" | tr -d ' \n')

echo "   Kefalonia Org ID: $KEF_ORG_ID"
echo "   Oraseas Org ID: $ORASEAS_ORG_ID"
echo ""

# Get test user credentials
echo "2. Getting test users..."
echo "   Super Admin: dthomaz (Oraseas EE)"
echo "   Org Admin: lefteris (Kefalonia Fisheries)"
echo ""

# Test 1: Super admin login and machine count
echo "3. Testing Super Admin Access..."
SUPER_TOKEN=$(curl -s -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=dthomaz&password=password123" | jq -r '.access_token')

if [ "$SUPER_TOKEN" != "null" ] && [ -n "$SUPER_TOKEN" ]; then
    echo -e "   ${GREEN}✓${NC} Super admin login successful"
    
    SUPER_MACHINES=$(curl -s -H "Authorization: Bearer $SUPER_TOKEN" \
      "http://localhost:8000/machines/" | jq '. | length')
    
    echo "   Super admin sees: $SUPER_MACHINES machines"
    
    if [ "$SUPER_MACHINES" -eq 11 ]; then
        echo -e "   ${GREEN}✓ PASS${NC}: Super admin sees all 11 machines"
        ((PASSED++))
    else
        echo -e "   ${RED}✗ FAIL${NC}: Expected 11 machines, got $SUPER_MACHINES"
        ((FAILED++))
    fi
else
    echo -e "   ${RED}✗ FAIL${NC}: Super admin login failed"
    ((FAILED++))
fi
echo ""

# Test 2: Org admin login and machine count
echo "4. Testing Org Admin Access..."
ORG_TOKEN=$(curl -s -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=lefteris&password=password123" | jq -r '.access_token')

if [ "$ORG_TOKEN" != "null" ] && [ -n "$ORG_TOKEN" ]; then
    echo -e "   ${GREEN}✓${NC} Org admin login successful"
    
    ORG_MACHINES=$(curl -s -H "Authorization: Bearer $ORG_TOKEN" \
      "http://localhost:8000/machines/" | jq '. | length')
    
    echo "   Org admin sees: $ORG_MACHINES machines"
    
    if [ "$ORG_MACHINES" -eq 5 ]; then
        echo -e "   ${GREEN}✓ PASS${NC}: Org admin sees only 5 machines"
        ((PASSED++))
    else
        echo -e "   ${RED}✗ FAIL${NC}: Expected 5 machines, got $ORG_MACHINES"
        ((FAILED++))
    fi
    
    # Verify all machines belong to Kefalonia
    ORG_IDS=$(curl -s -H "Authorization: Bearer $ORG_TOKEN" \
      "http://localhost:8000/machines/" | jq -r '.[].customer_organization_id' | sort -u)
    
    ORG_COUNT=$(echo "$ORG_IDS" | wc -l | tr -d ' ')
    
    if [ "$ORG_COUNT" -eq 1 ]; then
        echo -e "   ${GREEN}✓ PASS${NC}: All machines belong to same organization"
        ((PASSED++))
    else
        echo -e "   ${RED}✗ FAIL${NC}: Machines from multiple organizations detected!"
        echo "   Organization IDs: $ORG_IDS"
        ((FAILED++))
    fi
else
    echo -e "   ${RED}✗ FAIL${NC}: Org admin login failed"
    ((FAILED++))
    ((FAILED++))
fi
echo ""

# Test 3: Verify organization isolation
echo "5. Testing Organization Isolation..."
if [ "$ORG_TOKEN" != "null" ] && [ -n "$ORG_TOKEN" ]; then
    # Get machine names for org admin
    ORG_MACHINE_NAMES=$(curl -s -H "Authorization: Bearer $ORG_TOKEN" \
      "http://localhost:8000/machines/" | jq -r '.[].name' | sort)
    
    echo "   Org admin machines:"
    echo "$ORG_MACHINE_NAMES" | sed 's/^/     - /'
    
    # Check if any non-Kefalonia machines are visible
    if echo "$ORG_MACHINE_NAMES" | grep -qE "AQF|THA|MAR|LER|KIT"; then
        echo -e "   ${RED}✗ FAIL${NC}: Org admin can see machines from other organizations!"
        ((FAILED++))
    else
        echo -e "   ${GREEN}✓ PASS${NC}: Org admin only sees Kefalonia machines"
        ((PASSED++))
    fi
else
    echo -e "   ${YELLOW}⊘ SKIP${NC}: Org admin token not available"
fi
echo ""

# Summary
echo "=========================================="
echo "TEST SUMMARY"
echo "=========================================="
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED!${NC}"
    echo "Backend security is working correctly."
    echo ""
    echo "If frontend still shows all machines:"
    echo "1. Clear browser cache (Cmd+Shift+Delete)"
    echo "2. Hard refresh (Cmd+Shift+R)"
    echo "3. Or use Incognito/Private window"
    exit 0
else
    echo -e "${RED}✗ SOME TESTS FAILED!${NC}"
    echo "Backend security may have issues."
    exit 1
fi
