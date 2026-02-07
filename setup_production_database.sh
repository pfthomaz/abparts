#!/bin/bash

# Setup Production Database Script
# This script checks if the abparts_prod database exists on the host PostgreSQL
# and creates it if necessary

set -e

echo "=========================================="
echo "ABParts Production Database Setup"
echo "=========================================="
echo ""

# Check if PostgreSQL is running
echo "1. Checking if PostgreSQL is running..."
if sudo systemctl is-active --quiet postgresql; then
    echo "   ✓ PostgreSQL is running"
else
    echo "   ✗ PostgreSQL is not running"
    echo "   Starting PostgreSQL..."
    sudo systemctl start postgresql
    echo "   ✓ PostgreSQL started"
fi
echo ""

# Check if abparts_prod database exists
echo "2. Checking if abparts_prod database exists..."
DB_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='abparts_prod'")

if [ "$DB_EXISTS" = "1" ]; then
    echo "   ✓ Database 'abparts_prod' already exists"
    echo ""
    echo "3. Checking database connection..."
    if sudo -u postgres psql -d abparts_prod -c '\dt' > /dev/null 2>&1; then
        echo "   ✓ Can connect to abparts_prod database"
        echo ""
        echo "4. Listing existing tables:"
        sudo -u postgres psql -d abparts_prod -c '\dt'
    else
        echo "   ✗ Cannot connect to database"
        exit 1
    fi
else
    echo "   ✗ Database 'abparts_prod' does not exist"
    echo ""
    echo "3. Creating database and user..."
    
    # Create user if doesn't exist
    sudo -u postgres psql -c "CREATE USER abparts_user WITH PASSWORD 'abparts_pass';" 2>/dev/null || echo "   User 'abparts_user' already exists"
    
    # Create database
    sudo -u postgres psql -c "CREATE DATABASE abparts_prod OWNER abparts_user;"
    echo "   ✓ Database 'abparts_prod' created"
    
    # Grant privileges
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE abparts_prod TO abparts_user;"
    echo "   ✓ Privileges granted to abparts_user"
fi

echo ""
echo "5. Configuring PostgreSQL to accept connections from Docker..."

# Check if pg_hba.conf allows local connections
PG_VERSION=$(sudo -u postgres psql -tAc "SHOW server_version;" | cut -d'.' -f1)
PG_HBA_FILE="/etc/postgresql/${PG_VERSION}/main/pg_hba.conf"

if [ -f "$PG_HBA_FILE" ]; then
    # Backup pg_hba.conf
    sudo cp "$PG_HBA_FILE" "${PG_HBA_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Check if Docker network rule exists
    if sudo grep -q "172.0.0.0/8" "$PG_HBA_FILE"; then
        echo "   ✓ Docker network access already configured"
    else
        echo "   Adding Docker network access rule..."
        echo "# Allow Docker containers to connect" | sudo tee -a "$PG_HBA_FILE" > /dev/null
        echo "host    all             all             172.0.0.0/8             md5" | sudo tee -a "$PG_HBA_FILE" > /dev/null
        echo "   ✓ Docker network access configured"
        
        # Reload PostgreSQL
        sudo systemctl reload postgresql
        echo "   ✓ PostgreSQL configuration reloaded"
    fi
else
    echo "   ⚠ Could not find pg_hba.conf at $PG_HBA_FILE"
    echo "   You may need to manually configure PostgreSQL to accept connections from Docker"
fi

echo ""
echo "6. Checking postgresql.conf for listen_addresses..."
PG_CONF_FILE="/etc/postgresql/${PG_VERSION}/main/postgresql.conf"

if [ -f "$PG_CONF_FILE" ]; then
    LISTEN_ADDRESSES=$(sudo grep "^listen_addresses" "$PG_CONF_FILE" || echo "not set")
    echo "   Current setting: $LISTEN_ADDRESSES"
    
    if echo "$LISTEN_ADDRESSES" | grep -q "localhost"; then
        echo "   ✓ PostgreSQL is listening on localhost (Docker can connect via host.docker.internal)"
    fi
else
    echo "   ⚠ Could not find postgresql.conf"
fi

echo ""
echo "=========================================="
echo "Database Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Run database migrations:"
echo "   docker compose -f docker-compose.prod.yml up -d api"
echo "   docker compose exec api alembic upgrade head"
echo ""
echo "2. Start all services:"
echo "   docker compose -f docker-compose.prod.yml up -d"
echo ""
echo "3. Check service status:"
echo "   docker compose -f docker-compose.prod.yml ps"
echo ""
