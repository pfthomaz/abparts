# Nginx AI Assistant Proxy Fix - FINAL SOLUTION

## Problem
AI Assistant admin page shows "Error loading documents" and "Error loading stats" with 404 errors.

**Browser shows:**
```
GET https://abparts.oraseas.com/ai/knowledge/stats 404 (Not Found)
GET https://abparts.oraseas.com/ai/knowledge/documents 404 (Not Found)
```

**AI Assistant logs show:**
```
INFO: 172.18.0.1:53536 - "GET /knowledge/documents HTTP/1.1" 404 Not Found
INFO: 172.18.0.1:53550 - "GET /knowledge/stats HTTP/1.1" 404 Not Found
```

## Root Cause
Nginx was stripping the `/ai/` prefix when proxying to the AI assistant. The issue was in the `proxy_pass` directive:

**WRONG:**
```nginx
location /ai/ {
    proxy_pass http://localhost:8001/;  # Trailing slash strips /ai/ prefix!
}
```

This caused `/ai/knowledge/stats` to be forwarded as `/knowledge/stats`, which doesn't exist.

## Solution
Change the proxy_pass to preserve the full path:

**CORRECT:**
```nginx
location /ai/ {
    proxy_pass http://localhost:8001/ai/;  # Preserves /ai/ prefix
}
```

Now `/ai/knowledge/stats` is correctly forwarded to `http://localhost:8001/ai/knowledge/stats`.

## Deploy on Production Server

```bash
# 1. Copy updated config
sudo cp nginx-production.conf /etc/nginx/sites-available/abparts.oraseas.com

# 2. Test configuration
sudo nginx -t

# 3. Reload nginx
sudo systemctl reload nginx

# 4. Verify
curl https://abparts.oraseas.com/ai/knowledge/stats
```

## Verification
After deployment:
1. Access `https://abparts.oraseas.com/ai/admin`
2. Documents section should load
3. Statistics section should load
4. No 404 errors in console

## Technical Details

### Nginx Proxy Pass Behavior
- `proxy_pass http://backend/;` (with trailing slash) = strips location prefix
- `proxy_pass http://backend/path/;` (with path) = replaces location with path
- `proxy_pass http://backend` (no trailing slash) = appends full URI

### AI Assistant Route Registration
In `ai_assistant/app/main.py`:
```python
app.include_router(knowledge_base.router, prefix="/ai/knowledge", tags=["knowledge"])
```

Routes are:
- `/ai/knowledge/documents`
- `/ai/knowledge/stats`
- `/ai/knowledge/search`
- etc.

## Files Modified
- `nginx-production.conf` - Fixed proxy_pass directive for `/ai/` location

## Related
- `deploy_nginx_ai_routes.sh` - Automated deployment script
- `ai_assistant/app/main.py` - AI assistant route registration
