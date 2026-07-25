#!/bin/bash

# Get token by logging in with dthomaz
echo "Logging in as dthomaz..."
TOKEN_RESPONSE=$(curl -s -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=dthomaz&password=amFT1999!")

TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "Failed to get token"
  echo "Response: $TOKEN_RESPONSE"
  exit 1
fi

echo "Got token: ${TOKEN:0:20}..."

# Get executions to find an execution ID
echo "Getting executions..."
EXECUTIONS=$(curl -s -X GET "http://localhost:8000/maintenance-protocols/executions" \
  -H "Authorization: Bearer $TOKEN")

echo "Executions response (first 500 chars):"
echo "$EXECUTIONS" | head -c 500

# Extract first execution ID
EXECUTION_ID=$(echo "$EXECUTIONS" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)

if [ -z "$EXECUTION_ID" ]; then
  echo ""
  echo "No executions found"
  exit 1
fi

echo ""
echo "Testing report download for execution: $EXECUTION_ID"

# Test DOCX download
echo "Testing DOCX download..."
HTTP_CODE=$(curl -s -o /tmp/test_report.docx -w "%{http_code}" \
  -X GET "http://localhost:8000/maintenance-protocols/executions/$EXECUTION_ID/report/docx" \
  -H "Authorization: Bearer $TOKEN")

echo "DOCX download HTTP code: $HTTP_CODE"
if [ "$HTTP_CODE" = "200" ]; then
  echo "✓ DOCX file downloaded successfully!"
  echo "  File size: $(ls -lh /tmp/test_report.docx | awk '{print $5}')"
else
  echo "✗ DOCX download failed"
fi

# Test PDF download
echo ""
echo "Testing PDF download..."
HTTP_CODE=$(curl -s -o /tmp/test_report.pdf -w "%{http_code}" \
  -X GET "http://localhost:8000/maintenance-protocols/executions/$EXECUTION_ID/report/pdf" \
  -H "Authorization: Bearer $TOKEN")

echo "PDF download HTTP code: $HTTP_CODE"
if [ "$HTTP_CODE" = "200" ]; then
  echo "✓ PDF file downloaded successfully!"
  echo "  File size: $(ls -lh /tmp/test_report.pdf | awk '{print $5}')"
else
  echo "✗ PDF download failed"
fi

echo ""
echo "Test complete!"
