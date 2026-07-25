# AI Assistant Production URL Fix

## Issue
The AI assistant was returning 404 errors in production because the frontend was constructing the wrong URL path.

**Error:** `POST https://abparts.oraseas.com/ai/api/ai/chat 404 (Not Found)`

## Root Cause
The ChatWidget was building the URL incorrectly:
- Base URL in production: `/ai`
- Appending: `/api/ai/chat`
- Result: `/ai/api/ai/chat` ❌

When nginx proxies `/ai/*` to `http://localhost:8001`, it preserves the path, so the request became:
`http://localhost:8001/ai/api/ai/chat` (doesn't exist)

The correct endpoint on the AI assistant is: `http://localhost:8001/api/ai/chat`

## Solution
Updated `frontend/src/components/ChatWidget.js` to use the full correct path in production:
- Production: `/ai/api/ai/chat` (nginx strips `/ai/` and forwards to AI assistant)
- Development: `http://localhost:8001/api/ai/chat`

Wait - this is still wrong! Let me reconsider...

## Nginx Proxy Behavior
```nginx
location /ai/ {
    proxy_pass http://localhost:8001;
}
```

When `proxy_pass` doesn't have a URI path, nginx **preserves** the original request path:
- Request: `/ai/api/ai/chat`
- Proxied to: `http://localhost:8001/ai/api/ai/chat` ❌

## Correct Fix
The nginx config should strip the `/ai/` prefix. Update nginx config:

```nginx
location /ai/ {
    proxy_pass http://localhost:8001/;  # Note the trailing slash
}
```

With trailing slash, nginx **replaces** the location path:
- Request: `/ai/api/ai/chat`
- Proxied to: `http://localhost:8001/api/ai/chat` ✅

## Deployment Steps

### Option 1: Fix Nginx Config (Recommended)
```bash
# On production server
sudo nano /etc/nginx/sites-available/abparts.oraseas.com

# Change this line:
#   proxy_pass http://localhost:8001;
# To:
#   proxy_pass http://localhost:8001/;

# Test and reload nginx
sudo nginx -t
sudo systemctl reload nginx
```

### Option 2: Fix Frontend Code
If you can't change nginx, update the frontend to not include `/ai/` prefix:

```javascript
const apiUrl = process.env.NODE_ENV === 'production' 
  ? '/api/ai/chat' // Let nginx handle routing
  : `${process.env.REACT_APP_AI_ASSISTANT_URL || 'http://localhost:8001'}/api/ai/chat`;
```

Then rebuild and deploy frontend.

## Recommended: Fix Nginx (Simpler)
The nginx fix is simpler and doesn't require rebuilding/redeploying the frontend.
