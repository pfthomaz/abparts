# Design Document

## Overview

This design addresses the CORS configuration issues in the ABParts FastAPI backend by implementing a flexible, environment-aware CORS setup that supports both development and production scenarios. The solution will properly configure the FastAPI CORSMiddleware to allow cross-origin requests from the React frontend while maintaining security best practices.

## Architecture

The CORS configuration will be implemented as part of the FastAPI application initialization in `backend/app/main.py`. The design follows a layered approach:

1. **Environment Configuration Layer**: Read CORS settings from environment variables
2. **CORS Middleware Layer**: Configure FastAPI's CORSMiddleware with appropriate settings
3. **Request Processing Layer**: Handle preflight and actual CORS requests

## Components and Interfaces

### CORS Configuration Module

**Location**: `backend/app/cors_config.py` (new file)

**Purpose**: Centralize CORS configuration logic and provide environment-aware settings.

**Interface**:
```python
def get_cors_origins() -> List[str]:
    """Get allowed origins from environment or defaults"""
    
def get_cors_settings() -> Dict[str, Any]:
    """Get complete CORS configuration dictionary"""
```

### Environment Variables

**New Environment Variables**:
- `CORS_ALLOWED_ORIGINS`: Comma-separated list of allowed origins
- `CORS_ALLOW_CREDENTIALS`: Boolean flag for credential support
- `ENVIRONMENT`: Environment indicator (development/production)

**Default Behavior**:
- Development: Allow localhost origins and network IP
- Production: Only allow explicitly configured origins

### FastAPI Application Configuration

**Location**: `backend/app/main.py`

**Changes**:
- Import CORS configuration utilities
- Replace hardcoded origins list with dynamic configuration
- Add environment-aware CORS settings

## Data Models

### CORS Configuration Structure

```python
@dataclass
class CORSConfig:
    allowed_origins: List[str]
    allow_credentials: bool
    allow_methods: List[str]
    allow_headers: List[str]
    max_age: int
```

### Environment Detection

```python
class Environment(Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"
```

## Error Handling

### CORS Error Scenarios

1. **Invalid Origin**: Return 403 Forbidden with appropriate error message
2. **Missing Preflight Headers**: Return 400 Bad Request with required headers
3. **Configuration Errors**: Log warnings and fall back to safe defaults

### Error Response Format

```json
{
    "detail": "CORS policy violation: Origin not allowed",
    "error_code": "CORS_ORIGIN_NOT_ALLOWED",
    "allowed_origins": ["http://localhost:3000"]
}
```

## Testing Strategy

### Unit Tests

**Location**: `backend/tests/test_cors_config.py`

**Test Cases**:
- Environment variable parsing
- Default configuration generation
- Origin validation logic
- CORS settings generation

### Integration Tests

**Location**: `backend/tests/test_cors_integration.py`

**Test Cases**:
- Preflight request handling
- Actual CORS request processing
- Multiple origin support
- Credential handling

### Manual Testing Scenarios

1. **Localhost Development**:
   - Frontend: `http://localhost:3000`
   - Backend: `http://localhost:8000`
   - Expected: Successful CORS

2. **Network IP Development**:
   - Frontend: `http://localhost:3000`
   - Backend: `http://192.168.1.67:8000`
   - Expected: Successful CORS

3. **Mobile Testing**:
   - Frontend: `http://192.168.1.67:3000`
   - Backend: `http://192.168.1.67:8000`
   - Expected: Successful CORS

## Implementation Details

### CORS Middleware Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config.allowed_origins,
    allow_credentials=cors_config.allow_credentials,
    allow_methods=cors_config.allow_methods,
    allow_headers=cors_config.allow_headers,
    max_age=cors_config.max_age,
)
```

### Environment-Based Origin Detection

```python
def get_development_origins() -> List[str]:
    """Get default development origins including network IP detection"""
    origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost",
    ]
    
    # Add network IP if available
    network_ip = get_network_ip()
    if network_ip:
        origins.extend([
            f"http://{network_ip}:3000",
            f"http://{network_ip}:8000",
        ])
    
    return origins
```

### Docker Compose Integration

**Environment Variables in docker-compose.yml**:
```yaml
api:
  environment:
    CORS_ALLOWED_ORIGINS: "http://localhost:3000,http://192.168.1.67:3000"
    CORS_ALLOW_CREDENTIALS: "true"
    ENVIRONMENT: "development"
```

## Security Considerations

### Development vs Production

**Development**:
- Allow localhost and network IP origins
- Enable credentials for authentication
- Permissive header and method configuration

**Production**:
- Only allow explicitly configured origins
- Strict header and method configuration
- Enhanced logging for CORS violations

### Origin Validation

- Exact string matching for origins
- No wildcard origins in production
- Case-sensitive origin comparison
- Protocol enforcement (http/https)

## Performance Considerations

### Caching

- Cache CORS configuration on application startup
- Avoid repeated environment variable reads
- Pre-compile origin validation patterns

### Request Processing

- Efficient origin matching using sets
- Minimal overhead for non-CORS requests
- Fast preflight response generation

## Monitoring and Logging

### CORS Event Logging

```python
logger.info(f"CORS request from origin: {origin}")
logger.warning(f"CORS violation: {origin} not in allowed origins")
logger.error(f"CORS configuration error: {error}")
```

### Metrics Collection

- Track CORS request counts by origin
- Monitor CORS violation rates
- Alert on configuration errors