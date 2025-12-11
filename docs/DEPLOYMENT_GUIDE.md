# ABParts Deployment & Setup Guide

**Version:** 1.0  
**Last Updated:** January 18, 2025  
**Target Environment:** Production & Development  

---

## 📋 **Overview**

This comprehensive guide covers the complete deployment and setup process for the ABParts inventory management system. The system is containerized using Docker and designed for scalable deployment in both development and production environments.

### **System Architecture**
- **Frontend:** React 18 SPA with Tailwind CSS
- **Backend:** FastAPI with Python 3.10+
- **Database:** PostgreSQL 15
- **Cache/Queue:** Redis 7
- **Reverse Proxy:** Nginx (production)
- **Containerization:** Docker & Docker Compose

---

## 🚀 **Quick Start (Development)**

### **Prerequisites**
- Docker Desktop 4.0+ or Docker Engine 20.10+
- Docker Compose 2.0+
- Git
- 8GB+ RAM recommended
- 10GB+ free disk space

### **1. Clone Repository**
```bash
git clone <repository-url>
cd abparts
```

### **2. Environment Setup**
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables (see Environment Configuration section)
nano .env
```

### **3. Start Development Environment**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### **4. Initialize Database**
```bash
# Run database migrations
docker-compose exec api alembic upgrade head

# (Optional) Seed initial data
docker-compose exec api python -m app.scripts.seed_data
```

### **5. Access Application**
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **PgAdmin:** http://localhost:8080
- **Redis Commander:** http://localhost:8081

---

## 🏭 **Production Deployment**

### **Production Architecture**
```
Internet → Load Balancer → Nginx → FastAPI Backend
                                 ↓
                              PostgreSQL
                                 ↓
                               Redis
```

### **1. Server Requirements**

#### **Minimum Requirements**
- **CPU:** 2 cores
- **RAM:** 4GB
- **Storage:** 50GB SSD
- **OS:** Ubuntu 20.04+ / CentOS 8+ / RHEL 8+

#### **Recommended Requirements**
- **CPU:** 4+ cores
- **RAM:** 8GB+
- **Storage:** 100GB+ SSD
- **OS:** Ubuntu 22.04 LTS

### **2. Production Environment Setup**

#### **Install Docker**
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### **System Configuration**
```bash
# Create application directory
sudo mkdir -p /opt/abparts
sudo chown $USER:$USER /opt/abparts
cd /opt/abparts

# Clone repository
git clone <repository-url> .

# Set up production environment
cp .env.production .env
```

### **3. Production Environment Variables**
```bash
# .env (Production)
# Database Configuration
DATABASE_URL=postgresql://abparts_user:SECURE_PASSWORD@db:5432/abparts_prod
POSTGRES_DB=abparts_prod
POSTGRES_USER=abparts_user
POSTGRES_PASSWORD=SECURE_PASSWORD

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Security Configuration
SECRET_KEY=your-super-secure-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=8

# Application Configuration
ENVIRONMENT=production
DEBUG=false
API_HOST=0.0.0.0
API_PORT=8000

# Email Configuration (for notifications)
SMTP_HOST=smtp.your-provider.com
SMTP_PORT=587
SMTP_USERNAME=your-email@domain.com
SMTP_PASSWORD=your-email-password
SMTP_FROM_EMAIL=noreply@yourdomain.com

# Frontend Configuration
REACT_APP_API_URL=https://api.yourdomain.com

# SSL/TLS Configuration
SSL_CERT_PATH=/etc/ssl/certs/yourdomain.crt
SSL_KEY_PATH=/etc/ssl/private/yourdomain.key

# Backup Configuration
BACKUP_S3_BUCKET=your-backup-bucket
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
```

### **4. Production Docker Compose**

Create `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  # Database
  db:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init_db:/docker-entrypoint-initdb.d
    networks:
      - abparts-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis Cache
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - abparts-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Backend API
  api:
    build:
      context: ./backend
      dockerfile: Dockerfile.backend
      target: production
    restart: unless-stopped
    environment:
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: ${REDIS_URL}
      SECRET_KEY: ${SECRET_KEY}
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      ENVIRONMENT: production
    volumes:
      - ./backend/static:/app/static
      - ./logs:/app/logs
    networks:
      - abparts-network
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Frontend
  web:
    build:
      context: ./frontend
      dockerfile: Dockerfile.frontend
      target: production
      args:
        REACT_APP_API_URL: ${REACT_APP_API_URL}
    restart: unless-stopped
    networks:
      - abparts-network
    depends_on:
      - api

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/ssl
      - ./logs/nginx:/var/log/nginx
    networks:
      - abparts-network
    depends_on:
      - web
      - api

  # Database Backup Service
  backup:
    image: postgres:15-alpine
    restart: "no"
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - ./backups:/backups
      - ./scripts/backup.sh:/backup.sh
    networks:
      - abparts-network
    depends_on:
      - db
    command: /backup.sh

volumes:
  postgres_data:
  redis_data:

networks:
  abparts-network:
    driver: bridge
```

### **5. Nginx Configuration**

Create `nginx/nginx.conf`:
```nginx
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:8000;
    }

    upstream frontend {
        server web:3000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/m;

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # API Server
    server {
        listen 443 ssl http2;
        server_name api.yourdomain.com;

        ssl_certificate /etc/ssl/yourdomain.crt;
        ssl_certificate_key /etc/ssl/yourdomain.key;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # API endpoints
        location / {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Authentication endpoints (stricter rate limiting)
        location /token {
            limit_req zone=auth burst=5 nodelay;
            
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }

    # Frontend Server
    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        ssl_certificate /etc/ssl/yourdomain.crt;
        ssl_certificate_key /etc/ssl/yourdomain.key;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Static files caching
        location /static/ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # HTTP to HTTPS redirect
    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com api.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }
}
```

### **6. Production Deployment Steps**

#### **Initial Production Deployment**
```bash
# 1. Prepare production environment
cd /opt/abparts
git clone <repository-url> .
cp .env.production .env
# Edit .env with production values

# 2. Build and start services
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# 3. Wait for database to be ready
docker-compose -f docker-compose.prod.yml exec db pg_isready -U abparts_user

# 4. Run database migrations
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head

# 5. Create Oraseas EE organization (required first)
docker-compose -f docker-compose.prod.yml exec api python -c "
from app.database import SessionLocal
from app.models import Organization, OrganizationType
from app.crud.organizations import create_organization
from app.schemas import OrganizationCreate

db = SessionLocal()
oraseas_data = OrganizationCreate(
    name='Oraseas EE',
    organization_type=OrganizationType.oraseas_ee,
    address='Your Company Address',
    contact_info='Your Contact Information'
)
oraseas_org = create_organization(db, oraseas_data)
print(f'Created Oraseas EE organization: {oraseas_org.id}')
db.close()
"

# 6. Create initial super admin user
docker-compose -f docker-compose.prod.yml exec api python -m app.scripts.create_superuser

# 7. Create BossAqua organization
docker-compose -f docker-compose.prod.yml exec api python -c "
from app.database import SessionLocal
from app.models import Organization, OrganizationType
from app.crud.organizations import create_organization
from app.schemas import OrganizationCreate

db = SessionLocal()
bossaqua_data = OrganizationCreate(
    name='BossAqua',
    organization_type=OrganizationType.bossaqua,
    address='BossAqua Manufacturing Address',
    contact_info='BossAqua Contact Information'
)
bossaqua_org = create_organization(db, bossaqua_data)
print(f'Created BossAqua organization: {bossaqua_org.id}')
db.close()
"

# 8. Seed initial parts catalog (optional)
docker-compose -f docker-compose.prod.yml exec api python -m app.scripts.seed_parts_catalog

# 9. Verify deployment
docker-compose -f docker-compose.prod.yml ps
curl -f https://api.yourdomain.com/health

# 10. Test authentication
curl -X POST "https://api.yourdomain.com/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=superadmin@oraseas.com&password=your-password"

# 11. Set up monitoring and logging
docker-compose -f docker-compose.prod.yml logs -f
```

#### **Production Update Deployment**
```bash
# 1. Backup current database
docker-compose -f docker-compose.prod.yml exec db pg_dump -U abparts_user abparts_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Pull latest code
git pull origin main

# 3. Build updated containers
docker-compose -f docker-compose.prod.yml build --no-cache

# 4. Stop services (keep database running)
docker-compose -f docker-compose.prod.yml stop api web nginx

# 5. Run database migrations
docker-compose -f docker-compose.prod.yml up -d db redis
docker-compose -f docker-compose.prod.yml run --rm api alembic upgrade head

# 6. Start updated services
docker-compose -f docker-compose.prod.yml up -d

# 7. Verify update
curl -f https://api.yourdomain.com/health
docker-compose -f docker-compose.prod.yml logs api | tail -50

# 8. Clean up old containers and images
docker system prune -f
```

#### **Zero-Downtime Deployment (Advanced)**
```bash
# 1. Use blue-green deployment strategy
cp docker-compose.prod.yml docker-compose.blue.yml
# Modify ports in blue configuration

# 2. Start blue environment
docker-compose -f docker-compose.blue.yml up -d

# 3. Run health checks on blue
curl -f http://localhost:8001/health

# 4. Switch nginx upstream to blue
# Update nginx configuration and reload

# 5. Stop green environment
docker-compose -f docker-compose.prod.yml down

# 6. Rename blue to production
mv docker-compose.blue.yml docker-compose.prod.yml
```

---

## 🔧 **Environment Configuration**

### **Development Environment (.env)**
```bash
# Database
DATABASE_URL=postgresql://abparts_user:abparts_password@db:5432/abparts_dev
POSTGRES_DB=abparts_dev
POSTGRES_USER=abparts_user
POSTGRES_PASSWORD=abparts_password

# Redis
REDIS_URL=redis://redis:6379/0

# Security (Development - Use secure keys in production)
SECRET_KEY=dev-secret-key-change-in-production
JWT_SECRET_KEY=dev-jwt-secret-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=8

# Application
ENVIRONMENT=development
DEBUG=true
API_HOST=0.0.0.0
API_PORT=8000

# Frontend
REACT_APP_API_URL=http://localhost:8000

# Email (Development - Optional)
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=noreply@localhost

# PgAdmin
PGADMIN_DEFAULT_EMAIL=admin@abparts.com
PGADMIN_DEFAULT_PASSWORD=admin123
```

### **Environment Variables Reference**

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `REDIS_URL` | Redis connection string | Yes | - |
| `SECRET_KEY` | Application secret key | Yes | - |
| `JWT_SECRET_KEY` | JWT signing key | Yes | - |
| `ENVIRONMENT` | Environment (development/production) | No | development |
| `DEBUG` | Enable debug mode | No | false |
| `API_HOST` | API host binding | No | 0.0.0.0 |
| `API_PORT` | API port | No | 8000 |
| `SMTP_HOST` | Email server host | No | - |
| `SMTP_PORT` | Email server port | No | 587 |
| `REACT_APP_API_URL` | Frontend API URL | Yes | - |

---

## 🗄️ **Database Management**

### **Migrations**
```bash
# Create new migration
docker-compose exec api alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec api alembic upgrade head

# Rollback migration
docker-compose exec api alembic downgrade -1

# View migration history
docker-compose exec api alembic history

# Check current migration status
docker-compose exec api alembic current

# Show migration details
docker-compose exec api alembic show <revision_id>
```

### **Business Model Alignment Migration**

The ABParts system has undergone a major business model alignment. If upgrading from version 1.x to 2.x, follow these steps:

#### **Pre-Migration Checklist**
```bash
# 1. Backup existing database
docker-compose exec db pg_dump -U abparts_user abparts_dev > backup_pre_alignment_$(date +%Y%m%d_%H%M%S).sql

# 2. Verify current schema version
docker-compose exec api alembic current

# 3. Check for any pending data issues
docker-compose exec api python -m app.scripts.validate_pre_migration

# 4. Stop application services (keep database running)
docker-compose stop api web
```

#### **Migration Execution**
```bash
# 1. Apply business model alignment migrations
docker-compose exec api alembic upgrade head

# 2. Run data migration scripts
docker-compose exec api python -m app.scripts.migrate_business_model

# 3. Validate migrated data
docker-compose exec api python -m app.scripts.validate_post_migration

# 4. Restart services
docker-compose up -d api web
```

#### **Post-Migration Verification**
```bash
# 1. Verify organization types
docker-compose exec api python -c "
from app.database import SessionLocal
from app.models import Organization
db = SessionLocal()
orgs = db.query(Organization).all()
for org in orgs:
    print(f'{org.name}: {org.organization_type.value}')
db.close()
"

# 2. Check user roles and permissions
docker-compose exec api python -c "
from app.database import SessionLocal
from app.models import User
db = SessionLocal()
users = db.query(User).all()
for user in users:
    print(f'{user.username}: {user.role.value} ({user.organization.name})')
db.close()
"

# 3. Verify warehouse-inventory relationships
docker-compose exec api python -c "
from app.database import SessionLocal
from app.models import Warehouse, Inventory
db = SessionLocal()
warehouses = db.query(Warehouse).count()
inventory_items = db.query(Inventory).count()
print(f'Warehouses: {warehouses}, Inventory items: {inventory_items}')
db.close()
"
```

#### **Rollback Procedure (Emergency Only)**
```bash
# 1. Stop services
docker-compose stop api web

# 2. Restore from backup
docker-compose exec -T db psql -U abparts_user abparts_dev < backup_pre_alignment_YYYYMMDD_HHMMSS.sql

# 3. Downgrade migrations
docker-compose exec api alembic downgrade <previous_revision>

# 4. Restart with previous version
git checkout v1.x.x
docker-compose build
docker-compose up -d
```

### **Database Backup & Restore**

#### **Backup**
```bash
# Create backup
docker-compose exec db pg_dump -U abparts_user abparts_dev > backup_$(date +%Y%m%d_%H%M%S).sql

# Automated backup script
#!/bin/bash
BACKUP_DIR="/opt/abparts/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
docker-compose exec db pg_dump -U abparts_user abparts_prod > $BACKUP_DIR/backup_$TIMESTAMP.sql
gzip $BACKUP_DIR/backup_$TIMESTAMP.sql

# Keep only last 30 days of backups
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete
```

#### **Restore**
```bash
# Restore from backup
docker-compose exec -T db psql -U abparts_user abparts_dev < backup_file.sql
```

### **Database Monitoring**
```bash
# Check database connections
docker-compose exec db psql -U abparts_user -d abparts_dev -c "SELECT count(*) FROM pg_stat_activity;"

# Check database size
docker-compose exec db psql -U abparts_user -d abparts_dev -c "SELECT pg_size_pretty(pg_database_size('abparts_dev'));"

# Monitor slow queries
docker-compose exec db psql -U abparts_user -d abparts_dev -c "SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

---

## 🔄 **Migration Guide: Version 1.x to 2.x**

### **Overview**
Version 2.0 introduces significant business model alignment changes. This guide covers the complete migration process from version 1.x to 2.x.

### **Breaking Changes**
- Organization model restructured with types and hierarchy
- User roles refined (user, admin, super_admin)
- Inventory moved from organization-based to warehouse-based
- New transaction tracking system
- Enhanced security and session management

### **Pre-Migration Requirements**
- ABParts version 1.x running successfully
- Database backup capability
- Downtime window (estimated 30-60 minutes)
- Admin access to all systems

### **Step-by-Step Migration Process**

#### **Phase 1: Preparation (15 minutes)**
```bash
# 1. Create comprehensive backup
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec db pg_dump -U abparts_user abparts_dev > backup_pre_v2_migration_$DATE.sql
gzip backup_pre_v2_migration_$DATE.sql

# 2. Export current data for validation
docker-compose exec api python -m app.scripts.export_v1_data > v1_data_export_$DATE.json

# 3. Stop application services (keep database)
docker-compose stop api web

# 4. Pull version 2.0 code
git fetch origin
git checkout v2.0.0

# 5. Update environment variables
cp .env .env.v1.backup
cp .env.v2.template .env
# Edit .env with your specific values
```

#### **Phase 2: Database Migration (20 minutes)**
```bash
# 1. Build new containers
docker-compose build --no-cache

# 2. Start database and redis only
docker-compose up -d db redis

# 3. Run migration validation
docker-compose run --rm api python -m app.scripts.validate_migration_readiness

# 4. Execute database schema migrations
docker-compose run --rm api alembic upgrade head

# 5. Run data transformation scripts
docker-compose run --rm api python -m app.scripts.migrate_v1_to_v2_data

# 6. Validate migrated data
docker-compose run --rm api python -m app.scripts.validate_v2_migration
```

#### **Phase 3: Organization Setup (10 minutes)**
```bash
# 1. Create required singleton organizations
docker-compose run --rm api python -m app.scripts.setup_v2_organizations

# 2. Migrate existing organizations to new structure
docker-compose run --rm api python -m app.scripts.migrate_organization_hierarchy

# 3. Update user roles and permissions
docker-compose run --rm api python -m app.scripts.migrate_user_roles

# 4. Create default warehouses for existing organizations
docker-compose run --rm api python -m app.scripts.create_default_warehouses
```

#### **Phase 4: Inventory Migration (15 minutes)**
```bash
# 1. Migrate inventory from organization-based to warehouse-based
docker-compose run --rm api python -m app.scripts.migrate_inventory_to_warehouses

# 2. Create transaction history from existing data
docker-compose run --rm api python -m app.scripts.create_transaction_history

# 3. Validate inventory balances
docker-compose run --rm api python -m app.scripts.validate_inventory_migration

# 4. Update part classifications
docker-compose run --rm api python -m app.scripts.update_part_classifications
```

#### **Phase 5: Verification and Startup (10 minutes)**
```bash
# 1. Run comprehensive data validation
docker-compose run --rm api python -m app.scripts.final_migration_validation

# 2. Start all services
docker-compose up -d

# 3. Wait for services to be ready
sleep 30

# 4. Run health checks
curl -f http://localhost:8000/health

# 5. Test authentication with migrated users
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your-admin@example.com&password=your-password"

# 6. Verify key functionality
docker-compose exec api python -m app.scripts.test_v2_functionality
```

### **Migration Scripts Reference**

#### **validate_migration_readiness.py**
```python
# Checks:
# - Database connectivity
# - Required tables exist
# - Data integrity
# - Backup availability
# - Sufficient disk space
```

#### **migrate_v1_to_v2_data.py**
```python
# Performs:
# - Schema updates
# - Data type conversions
# - Relationship restructuring
# - Index creation
# - Constraint addition
```

#### **setup_v2_organizations.py**
```python
# Creates:
# - Oraseas EE organization (singleton)
# - BossAqua organization (singleton)
# - Updates existing organizations with types
# - Establishes parent-child relationships
```

#### **migrate_inventory_to_warehouses.py**
```python
# Migrates:
# - Organization inventory to warehouse inventory
# - Creates default warehouses
# - Preserves stock levels
# - Updates relationships
```

### **Rollback Procedure**

If migration fails or issues are discovered:

```bash
# 1. Stop all services immediately
docker-compose down

# 2. Restore database from backup
docker-compose up -d db
docker-compose exec -T db psql -U abparts_user abparts_dev < backup_pre_v2_migration_YYYYMMDD_HHMMSS.sql

# 3. Checkout previous version
git checkout v1.x.x

# 4. Restore environment
cp .env.v1.backup .env

# 5. Rebuild and start v1.x
docker-compose build
docker-compose up -d

# 6. Verify rollback success
curl -f http://localhost:8000/health
```

### **Post-Migration Tasks**

#### **User Communication**
```bash
# 1. Send migration completion notification
docker-compose exec api python -m app.scripts.send_migration_notification

# 2. Update user documentation
# - New login procedures
# - Updated role permissions
# - New warehouse features
```

#### **System Validation**
```bash
# 1. Run full system tests
docker-compose exec api python -m pytest tests/integration/

# 2. Performance validation
docker-compose exec api python -m app.scripts.performance_validation

# 3. Security audit
docker-compose exec api python -m app.scripts.security_audit
```

#### **Monitoring Setup**
```bash
# 1. Update monitoring dashboards
# 2. Set up new alerts for v2.0 features
# 3. Configure log aggregation
# 4. Test backup procedures
```

### **Common Migration Issues**

#### **Issue: Organization Type Conflicts**
```bash
# Symptom: Multiple Oraseas EE organizations
# Solution:
docker-compose exec api python -c "
from app.database import SessionLocal
from app.models import Organization, OrganizationType
db = SessionLocal()
orgs = db.query(Organization).filter(Organization.organization_type == OrganizationType.oraseas_ee).all()
if len(orgs) > 1:
    # Keep first, convert others to customer
    for org in orgs[1:]:
        org.organization_type = OrganizationType.customer
    db.commit()
db.close()
"
```

#### **Issue: Inventory Discrepancies**
```bash
# Symptom: Stock levels don't match
# Solution:
docker-compose exec api python -m app.scripts.reconcile_inventory_migration
```

#### **Issue: User Role Conflicts**
```bash
# Symptom: Super admin in non-Oraseas organization
# Solution:
docker-compose exec api python -m app.scripts.fix_user_role_conflicts
```

### **Migration Validation Checklist**

- [ ] All organizations have correct types
- [ ] Singleton constraints enforced (Oraseas EE, BossAqua)
- [ ] User roles properly assigned
- [ ] Warehouses created for all organizations
- [ ] Inventory migrated to warehouse-based
- [ ] Transaction history created
- [ ] Stock levels match pre-migration
- [ ] All users can authenticate
- [ ] Permissions work correctly
- [ ] API endpoints respond properly
- [ ] Frontend loads without errors
- [ ] Reports generate correctly

---

## 📊 **Monitoring & Logging**

### **Health Checks**
```bash
# Application health
curl http://localhost:8000/health

# Database health
docker-compose exec db pg_isready -U abparts_user

# Redis health
docker-compose exec redis redis-cli ping
```

### **Log Management**
```bash
# View application logs
docker-compose logs -f api

# View database logs
docker-compose logs -f db

# View all logs
docker-compose logs -f

# Log rotation (production)
# Add to /etc/logrotate.d/abparts
/opt/abparts/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
    postrotate
        docker-compose -f /opt/abparts/docker-compose.prod.yml restart nginx
    endscript
}
```

### **Performance Monitoring**
```bash
# Container resource usage
docker stats

# Database performance
docker-compose exec db psql -U abparts_user -d abparts_dev -c "
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation 
FROM pg_stats 
WHERE schemaname = 'public' 
ORDER BY n_distinct DESC;
"

# API response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health
```

---

## 🔒 **Security Configuration**

### **SSL/TLS Setup**
```bash
# Generate self-signed certificate (development)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/yourdomain.key \
    -out nginx/ssl/yourdomain.crt

# Let's Encrypt (production)
certbot certonly --webroot -w /var/www/html -d yourdomain.com -d www.yourdomain.com
```

### **Firewall Configuration**
```bash
# Ubuntu UFW
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# CentOS/RHEL Firewalld
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### **Security Hardening**
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban

# Configure automatic security updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Database Connection Issues**
```bash
# Check database container
docker-compose ps db

# Check database logs
docker-compose logs db

# Test connection
docker-compose exec api python -c "
from app.database import engine
try:
    engine.connect()
    print('Database connection successful')
except Exception as e:
    print(f'Database connection failed: {e}')
"
```

#### **API Not Starting**
```bash
# Check API logs
docker-compose logs api

# Check dependencies
docker-compose exec api pip list

# Test API manually
docker-compose exec api python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### **Frontend Build Issues**
```bash
# Check frontend logs
docker-compose logs web

# Rebuild frontend
docker-compose build --no-cache web

# Check Node.js version
docker-compose exec web node --version
```

#### **Performance Issues**
```bash
# Check resource usage
docker stats

# Check database performance
docker-compose exec db psql -U abparts_user -d abparts_dev -c "
SELECT 
    query,
    calls,
    total_time,
    mean_time
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
"

# Check Redis memory usage
docker-compose exec redis redis-cli info memory
```

### **Debug Mode**
```bash
# Enable debug logging
export DEBUG=true
docker-compose up -d

# Run API in debug mode
docker-compose exec api python -m debugpy --listen 0.0.0.0:5678 --wait-for-client -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 📋 **Maintenance Tasks**

### **Regular Maintenance**
```bash
# Weekly tasks
- Database backup
- Log rotation
- Security updates
- Performance monitoring

# Monthly tasks
- Database optimization
- Disk space cleanup
- SSL certificate renewal
- Dependency updates
```

### **Maintenance Scripts**
```bash
# Create maintenance script
#!/bin/bash
# /opt/abparts/scripts/maintenance.sh

echo "Starting maintenance tasks..."

# Backup database
./backup.sh

# Clean up old logs
find /opt/abparts/logs -name "*.log" -mtime +7 -delete

# Update containers
docker-compose -f /opt/abparts/docker-compose.prod.yml pull
docker-compose -f /opt/abparts/docker-compose.prod.yml up -d

# Clean up unused Docker resources
docker system prune -f

echo "Maintenance tasks completed."
```

### **Automated Maintenance (Cron)**
```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /opt/abparts/scripts/backup.sh

# Weekly maintenance on Sunday at 3 AM
0 3 * * 0 /opt/abparts/scripts/maintenance.sh

# Monthly SSL renewal
0 4 1 * * certbot renew --quiet
```

---

## 📞 **Support & Resources**

### **Documentation**
- **API Documentation:** `/docs` endpoint
- **Database Schema:** `docs/DATABASE_SCHEMA.md`
- **Development Guide:** `docs/DEVELOPMENT_GUIDE.md`

### **Monitoring Endpoints**
- **Health Check:** `/health`
- **Metrics:** `/metrics` (if enabled)
- **OpenAPI Schema:** `/openapi.json`

### **Support Contacts**
- **Technical Issues:** Create GitHub issue
- **Security Issues:** Email security@yourdomain.com
- **General Support:** Email support@yourdomain.com

---

**Last Updated:** January 18, 2025  
**Version:** 1.0  
**Next Review:** February 2025