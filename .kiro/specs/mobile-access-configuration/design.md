# Design Document

## Overview

The mobile access configuration will modify the Docker Compose setup to enable network-wide access to the ABParts application. Currently, services are bound to localhost only, restricting access to the host machine. This design will configure services to bind to all network interfaces and update CORS settings to allow cross-origin requests from mobile devices.

## Architecture

### Current Architecture
- **Frontend**: React app running on `localhost:3000`
- **Backend**: FastAPI running on `localhost:8000` 
- **Database**: PostgreSQL on `localhost:5432`
- **Admin**: pgAdmin on `localhost:8080`
- **Network Binding**: Services bound to `127.0.0.1` (localhost only)

### Target Architecture
- **Frontend**: React app accessible via `{HOST_IP}:3000`
- **Backend**: FastAPI accessible via `{HOST_IP}:8000`
- **Database**: PostgreSQL accessible via `{HOST_IP}:5432` 
- **Admin**: pgAdmin accessible via `{HOST_IP}:8080`
- **Network Binding**: Services bound to `0.0.0.0` (all interfaces)
- **CORS Configuration**: Updated to include host IP addresses

## Components and Interfaces

### Docker Compose Configuration Changes

#### Port Binding Updates
```yaml
# Current binding (localhost only)
ports:
  - "3000:3000"
  - "8000:8000"

# New binding (all interfaces)
ports:
  - "0.0.0.0:3000:3000"
  - "0.0.0.0:8000:8000"
```

#### Environment Variable Updates
```yaml
# Frontend service environment
environment:
  REACT_APP_API_BASE_URL: http://{HOST_IP}:8000

# Backend service environment  
environment:
  CORS_ALLOWED_ORIGINS: http://localhost:3000,http://127.0.0.1:3000,http://{HOST_IP}:3000,http://{HOST_IP}:8000
```

### Network Discovery Component

A mechanism to automatically detect the host machine's IP address for configuration:

```bash
# Windows command to get IP
ipconfig | findstr "IPv4" | head -1

# Cross-platform alternative
hostname -I | awk '{print $1}'
```

### CORS Configuration Component

The FastAPI backend already includes CORS middleware configuration through environment variables. The design will extend the allowed origins to include:

- `http://localhost:3000` (existing)
- `http://127.0.0.1:3000` (existing) 
- `http://{HOST_IP}:3000` (new - for mobile frontend access)
- `http://{HOST_IP}:8000` (new - for mobile API access)

## Data Models

No new data models are required. This is purely a configuration change that affects network accessibility without modifying application logic or data structures.

## Error Handling

### Network Connectivity Issues
- **Problem**: Mobile device cannot reach services
- **Detection**: Connection timeout or refused connection errors
- **Resolution**: Verify firewall settings and network connectivity

### CORS Errors
- **Problem**: Browser blocks cross-origin requests from mobile
- **Detection**: CORS error messages in browser console
- **Resolution**: Verify CORS_ALLOWED_ORIGINS includes mobile access URLs

### IP Address Changes
- **Problem**: Host IP address changes, breaking mobile access
- **Detection**: Mobile access stops working after network changes
- **Resolution**: Update configuration with new IP address and restart services

### Firewall Blocking
- **Problem**: Windows firewall blocks incoming connections
- **Detection**: Services unreachable from external devices
- **Resolution**: Configure Windows firewall to allow connections on ports 3000, 8000, 8080

## Testing Strategy

### Unit Testing
- No new unit tests required as this is configuration-only

### Integration Testing
1. **Local Access Verification**
   - Test localhost access still works after changes
   - Verify all services respond correctly

2. **Network Access Testing**
   - Test frontend access from mobile device
   - Test API access from mobile device
   - Test pgAdmin access from mobile device

3. **CORS Testing**
   - Verify API calls from mobile frontend work correctly
   - Test authentication flow from mobile device
   - Validate all CRUD operations work from mobile

### Manual Testing Checklist
- [ ] Frontend loads on mobile browser at `http://{HOST_IP}:3000`
- [ ] User can log in from mobile device
- [ ] All application features work on mobile
- [ ] API documentation accessible at `http://{HOST_IP}:8000/docs`
- [ ] pgAdmin accessible at `http://{HOST_IP}:8080`
- [ ] Localhost access still works from host machine
- [ ] No CORS errors in browser console

### Performance Considerations
- Network latency may be slightly higher when accessing from mobile devices
- No significant performance impact expected as this is local network access
- Consider mobile-responsive UI improvements as a future enhancement

### Security Considerations
- Services will be accessible to any device on the local network
- Ensure network is trusted (home/office WiFi)
- Authentication still required for application access
- Consider VPN access for remote scenarios beyond local network