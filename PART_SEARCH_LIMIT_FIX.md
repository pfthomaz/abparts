# Part Search Limit Fix

## Problem
Part search was limited to 100 parts due to the backend's default limit parameter. This caused issues when:
- Using PartUsageRecorder component
- Using StockResetTab component
- Any component calling `partsService.getParts()`

## Solution
Updated all part fetching to use the backend's maximum allowed limit of 1000 parts.

## Changes Made

### 1. `frontend/src/services/partsService.js`
**Function:** `getParts()`
- **Before:** `api.get('/parts/')` (used default limit of 100)
- **After:** `api.get('/parts/?limit=1000')` (explicitly requests 1000 parts)

### 2. `frontend/src/components/StockResetTab.js`
**Line 36:**
- **Before:** `api.get('/parts/?limit=10000')` (exceeded backend max, capped at 1000)
- **After:** `api.get('/parts/?limit=1000')` (uses correct backend maximum)
- Updated comment to reflect backend's actual maximum limit

## Backend Limit Configuration
The backend (`backend/app/routers/parts.py`) has the following limit configuration:
```python
limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return")
```
- Default: 100
- Minimum: 1
- Maximum: 1000

## Impact
- ✅ PartUsageRecorder now shows all available parts (up to 1000)
- ✅ StockResetTab now shows all available parts (up to 1000)
- ✅ Any component using `partsService.getParts()` will get up to 1000 parts
- ✅ Parts page already uses `getPartsWithInventory({ limit: 1000 })` - no change needed

## Testing Recommendations
1. Open PartUsageRecorder modal and verify all parts are available in the dropdown
2. Open StockResetTab and verify part search shows all parts
3. Verify performance is acceptable with larger parts lists
4. If you have more than 1000 parts in the future, consider implementing pagination or infinite scroll

## Notes
- The backend maximum limit of 1000 is a reasonable limit for performance
- If the parts catalog grows beyond 1000, consider:
  - Implementing server-side search/filtering
  - Adding pagination to the parts list
  - Using infinite scroll for better UX
