# Maintenance Report Download Fix

## Issue
Report downloads were failing with 401 authentication errors. The logs showed:
```
PDF Report - Token received: null...
PDF Report - Token length: 4
```

## Root Cause
The frontend was reading the token from the wrong localStorage key:
- Token is stored as: `localStorage.setItem('authToken', token)`
- Frontend was reading: `localStorage.getItem('token')` ❌
- This returned the string `"null"` instead of the actual session token

## Solution
Fixed `frontend/src/components/ExecutionHistory.js` to use the correct localStorage key:

```javascript
// BEFORE (wrong)
const token = localStorage.getItem('token');

// AFTER (correct)
const token = localStorage.getItem('authToken');
```

Also updated `backend/app/middleware.py` to skip `/reports/` endpoints from permission middleware, allowing them to handle their own authentication.

## Files Modified
1. `frontend/src/components/ExecutionHistory.js` - Fixed localStorage key for both DOCX and PDF buttons
2. `backend/app/middleware.py` - Added `/reports/` prefix to middleware skip list

## Testing
1. Log in to the application at `http://localhost:3000`
2. Navigate to Maintenance Executions
3. Click on an execution to view details
4. Click the "📄 DOCX" or "📑 PDF" button
5. The report should download successfully

## Report Features
- DOCX and PDF format support
- Professional formatting with organization logo
- Execution metadata (protocol, machine, technician, date)
- Complete checklist items with status and notes
- AI-powered insights for each checklist item (requires OPENAI_API_KEY)
- Organization-level access control

## API Endpoints
- `GET /reports/maintenance-executions/{execution_id}/docx` - Download DOCX report
- `GET /reports/maintenance-executions/{execution_id}/pdf` - Download PDF report

Both endpoints:
- Require Bearer token authentication
- Validate session tokens from Redis
- Check organization-level access permissions
- Generate reports with AI insights (if OpenAI API key is configured)

## Status
✅ Fixed - Reports should now download successfully from the browser
