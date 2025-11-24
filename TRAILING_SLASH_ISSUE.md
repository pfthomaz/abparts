# Trailing Slash Issue - Production vs Development

## Problem

API endpoints work in local development without trailing slashes but fail in production with **405 Method Not Allowed** errors.

### Example:
- ❌ `/customer_order_items` - Works locally, fails in production
- ✅ `/customer_order_items/` - Works everywhere

## Root Cause

### Local Development
- Frontend connects directly to FastAPI (port 8000)
- FastAPI automatically redirects non-trailing-slash URLs to trailing-slash versions
- No issues

### Production
- Frontend → nginx → FastAPI
- nginx configuration doesn't preserve the redirect properly
- POST/PUT/DELETE requests fail with 405 errors
- GET requests might work due to different nginx handling

## Solution

**Always use trailing slashes in API calls:**

```javascript
// ❌ BAD - Will fail in production
api.post('/customer_orders', data);
api.get('/machines');

// ✅ GOOD - Works everywhere
api.post('/customer_orders/', data);
api.get('/machines/');
```

## Why This Happens

1. **FastAPI's behavior**: FastAPI adds trailing slashes to all routes by default
2. **nginx proxy**: When nginx proxies a POST request with a redirect (307), some configurations don't handle it correctly
3. **HTTP method preservation**: Redirects can change POST → GET in some cases

## nginx Configuration

The production nginx config should handle this, but it's safer to always use trailing slashes:

```nginx
# In frontend/nginx.conf
location /api/ {
    proxy_pass http://api:8000/;
    # This strips /api/ and forwards to FastAPI
    # But redirects might not work properly for POST/PUT/DELETE
}
```

## Checklist for All API Calls

When adding new API endpoints, ensure:

- [ ] All `api.get()` calls have trailing slashes
- [ ] All `api.post()` calls have trailing slashes
- [ ] All `api.put()` calls have trailing slashes
- [ ] All `api.delete()` calls have trailing slashes
- [ ] Service functions consistently use trailing slashes
- [ ] Test in production environment

## Files to Check

Common locations for API calls:
- `frontend/src/services/*.js` - Service layer
- `frontend/src/pages/*.js` - Page components
- `frontend/src/components/*.js` - Components making direct API calls

## Quick Fix Script

To find all API calls without trailing slashes:

```bash
# Search for API calls without trailing slashes
grep -r "api\.\(get\|post\|put\|delete\)(['\"][^'\"]*[^/]['\"]" frontend/src/
```

## Prevention

1. **Code review**: Check for trailing slashes in all API calls
2. **Linting rule**: Consider adding an ESLint rule to enforce trailing slashes
3. **Testing**: Always test new features in production-like environment
4. **Documentation**: Document this requirement for all developers

## Related Issues

This same issue affects:
- `/machines` vs `/machines/`
- `/parts` vs `/parts/`
- `/warehouses` vs `/warehouses/`
- `/organizations` vs `/organizations/`
- Any custom endpoint

## Summary

**Golden Rule**: Always end API endpoint paths with a trailing slash (`/`) to ensure consistent behavior between development and production environments.
