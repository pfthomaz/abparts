# AI Assistant Development Connection Fix - Complete

## Issue
In development environment, when submitting messages to the AI Assistant:
- Error: `POST http://localhost:8001/api/ai/chat net::ERR_CONNECTION_RESET`
- Message: "Your message has been queued and will be sent when you're back online"
- Console error: `TypeError: Failed to fetch`

## Root Cause
The AI Assistant Docker container was running but **unhealthy** due to a missing Python dependency:
```
ModuleNotFoundError: No module named 'cryptography'
```

The `cryptography` module was added to `requirements.txt` for security features (Task 12), but the Docker image wasn't rebuilt, so the module wasn't installed in the container.

## Solution
Rebuilt the AI Assistant Docker container to install all dependencies including `cryptography`:

```bash
# Rebuild the AI Assistant container
docker-compose build ai_assistant

# Restart with the new image
docker-compose up -d ai_assistant
```

## Verification

### Container Status
```bash
docker ps --filter "name=abparts_ai_assistant"
```
**Result**: Container now shows `Up X seconds (healthy)` instead of `Up X days (unhealthy)`

### Service Logs
```bash
docker logs abparts_ai_assistant --tail 20
```
**Result**: Shows successful startup:
```
Database connection established
Redis connection established
OpenAI API connection test successful
LLM client initialized successfully
AI Assistant service started successfully
Application startup complete
```

### Health Check
```bash
curl http://localhost:8001/health
```
**Result**: Service responds successfully (previously failed)

## Files Involved
- `ai_assistant/requirements.txt` - Contains `cryptography==41.0.7`
- `ai_assistant/Dockerfile` - Docker build configuration
- `docker-compose.yml` - Service orchestration
- `ai_assistant/app/services/security_service.py` - Uses cryptography module

## Why This Happened
1. Security features (Task 12) added `cryptography` dependency
2. `requirements.txt` was updated
3. Docker container was not rebuilt after the update
4. Container continued running with old image (without cryptography)
5. Service failed to start properly, marked as unhealthy
6. Frontend detected connection failure and queued messages

## Prevention
When adding new Python dependencies to `ai_assistant/requirements.txt`:
1. Always rebuild the container: `docker-compose build ai_assistant`
2. Restart the service: `docker-compose up -d ai_assistant`
3. Verify health: `docker logs abparts_ai_assistant`

## Testing
After the fix, test the AI Assistant:
1. Open the ABParts frontend (http://localhost:3000)
2. Click the chat icon in the bottom-right
3. Send a test message
4. Should receive a response from the AI (not queued message)

## Related Issues
- Mobile UI fix: `AI_ASSISTANT_MOBILE_UI_FIX.md`
- Security implementation: `ai_assistant/TASK_12_IMPLEMENTATION_SUMMARY.md`

---

**Fixed**: January 31, 2026  
**Status**: ✅ Complete  
**Impact**: HIGH - AI Assistant now functional in development  
**Environment**: Development (docker-compose.yml)

