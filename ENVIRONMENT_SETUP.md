# ABParts Environment Setup

This project supports multiple environments with separate configurations for development and production.

## Environment Structure

```
├── .env.development          # Development environment variables
├── .env.production          # Production environment variables
├── docker-compose.dev.yml   # Development Docker configuration
├── docker-compose.prod.yml  # Production Docker configuration
├── scripts/
│   ├── dev.sh              # Development management script
│   └── prod.sh             # Production management script
```

## Development Environment

### Setup
1. Copy environment file:
   ```bash
   cp .env.development .env
   ```

2. Start development environment:
   ```bash
   ./scripts/dev.sh start
   ```

### Available Commands
```bash
./scripts/dev.sh start          # Start all services
./scripts/dev.sh stop           # Stop all services
./scripts/dev.sh restart        # Restart all services
./scripts/dev.sh build          # Rebuild containers
./scripts/dev.sh logs [service] # View logs
./scripts/dev.sh shell [service] # Open shell in container
```

### Development URLs
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **PgAdmin**: http://localhost:8080

## Production Environment (Hetzner VM)

### Setup
1. Copy and configure production environment:
   ```bash
   cp .env.production .env
   # Edit .env with your production values
   ```

2. Update production configuration:
   - Set secure passwords
   - Configure proper CORS origins
   - Set production URLs

### Deployment Commands
```bash
./scripts/prod.sh deploy        # Full deployment
./scripts/prod.sh start         # Start services
./scripts/prod.sh start-with-admin # Start with PgAdmin
./scripts/prod.sh stop          # Stop services
./scripts/prod.sh restart       # Restart services
./scripts/prod.sh build         # Rebuild containers
./scripts/prod.sh logs [service] # View logs
./scripts/prod.sh backup        # Backup database
```

### Production URLs
- **Frontend**: http://46.62.153.166:81
- **API**: http://46.62.153.166:8000
- **PgAdmin**: http://46.62.153.166:8080 (if started with admin profile)

## Environment Variables

### Required Production Variables
Update `.env.production` with:
- `POSTGRES_PASSWORD`: Secure database password
- `PGADMIN_DEFAULT_PASSWORD`: Secure PgAdmin password
- `SECRET_KEY`: Application secret key
- `JWT_SECRET_KEY`: JWT signing key
- `CORS_ALLOWED_ORIGINS`: Production frontend URLs

### CORS Configuration
Development:
```
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000
```

Production:
```
CORS_ALLOWED_ORIGINS=http://46.62.153.166:81,http://46.62.153.166:3000,http://46.62.153.166:8000
```

## Migration Between Environments

### From Development to Production
1. Test locally with development environment
2. Update `.env.production` with production values
3. Deploy to production server:
   ```bash
   ./scripts/prod.sh deploy
   ```

### Database Migrations
```bash
# Development
./scripts/dev.sh shell api
alembic upgrade head

# Production
./scripts/prod.sh shell api
alembic upgrade head
```

## Security Notes

- Never commit `.env` files to version control
- Use strong passwords in production
- Regularly backup production database
- Monitor logs for security issues
- Keep Docker images updated

## Troubleshooting

### CORS Issues
1. Check `CORS_ALLOWED_ORIGINS` in environment file
2. Verify frontend is using correct API URL
3. Check browser developer console for exact error

### Database Connection Issues
1. Verify database container is healthy
2. Check database credentials
3. Ensure database migrations are applied

### Port Conflicts
1. Check if ports are already in use: `netstat -tlnp`
2. Update port mappings in docker-compose files
3. Update environment variables accordingly