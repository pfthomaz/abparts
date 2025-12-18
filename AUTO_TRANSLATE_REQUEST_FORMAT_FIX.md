# Auto-Translate Request Format Fix

## 🐛 Issue Identified

The auto-translation feature was returning "422 Unprocessable Content" errors due to a mismatch between the request format expected by the backend and what the frontend was sending.

### Problem Details
- **Backend Expected**: `target_languages` as query parameters
- **Frontend Was Sending**: `target_languages` as JSON body property
- **Error**: `Input should be a valid list` validation error

### Backend Endpoint Signature
```python
@router.post("/protocols/{protocol_id}/auto-translate-complete")
async def auto_translate_complete_protocol(
    protocol_id: UUID,
    target_languages: Optional[List[str]] = None,  # Query parameter
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
```

### Frontend Was Sending (Incorrect)
```javascript
// POST /translations/protocols/{id}/auto-translate-complete
// Body: {"target_languages": ["el", "ar", "es", "tr", "no"]}
```

### Frontend Should Send (Correct)
```javascript
// POST /translations/protocols/{id}/auto-translate-complete?target_languages=el&target_languages=ar&target_languages=es&target_languages=tr&target_languages=no
// Body: (empty)
```

## ✅ Fix Applied

Updated the auto-translation methods in `frontend/src/services/translationService.js` to send `target_languages` as query parameters instead of JSON body:

```javascript
async autoTranslateCompleteProtocol(protocolId, targetLanguages = null) {
  let url = `/translations/protocols/${protocolId}/auto-translate-complete`;
  if (targetLanguages && targetLanguages.length > 0) {
    const params = new URLSearchParams();
    targetLanguages.forEach(lang => params.append('target_languages', lang));
    url += `?${params.toString()}`;
  }
  const response = await api.post(url);
  return response;
}
```

### All Fixed Methods
- ✅ `autoTranslateProtocol()` - Now uses query parameters
- ✅ `autoTranslateProtocolChecklist()` - Now uses query parameters  
- ✅ `autoTranslateCompleteProtocol()` - Now uses query parameters

## 🚀 Next Steps

### 1. Rebuild Frontend (Again)
Since the JavaScript code has changed, you need to rebuild the frontend container:

```bash
# Stop frontend container
docker-compose -f docker-compose.prod.yml stop web

# Rebuild with latest code
docker-compose -f docker-compose.prod.yml build --no-cache web

# Start frontend container
docker-compose -f docker-compose.prod.yml up -d web
```

### 2. Test the Fix
1. Navigate to Protocol Translations page
2. Click "Auto-Translate" on any protocol
3. Select languages and translation type
4. Click "Start Translation"
5. Should now work without 422 errors

## 🎯 Expected Result

After the rebuild, the auto-translation requests will be formatted correctly:
- ✅ Query parameters instead of JSON body
- ✅ Backend validation will pass
- ✅ AI translation will execute successfully
- ✅ Users will see translation results

## 📝 Technical Details

The fix uses `URLSearchParams` to properly encode multiple values for the same parameter name:
- `target_languages=el&target_languages=ar&target_languages=es`
- This creates a proper list that FastAPI can parse as `List[str]`

## ⚠️ Root Cause

The mismatch occurred because:
1. FastAPI endpoint was designed to accept query parameters
2. Frontend was implemented to send JSON body
3. The validation error was cryptic in production (minified React)

This highlights the importance of API contract alignment between frontend and backend.