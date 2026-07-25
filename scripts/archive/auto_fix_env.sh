#!/bin/bash

echo "========================================="
echo "Auto-fixing .env Configuration"
echo "========================================="
echo ""

# Backup .env
if [ -f .env ]; then
    BACKUP=".env.backup.$(date +%Y%m%d_%H%M%S)"
    cp .env "$BACKUP"
    echo "✓ Backed up .env to $BACKUP"
else
    echo "✗ .env file not found!"
    echo "  Creating from template..."
    cp .env.production.example .env
    echo "✓ Created .env from template"
fi
echo ""

# Function to update or add env variable
update_env() {
    local key=$1
    local value=$2
    local file=".env"
    
    if grep -q "^${key}=" "$file"; then
        # Update existing
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "s|^${key}=.*|${key}=${value}|" "$file"
        else
            # Linux
            sed -i "s|^${key}=.*|${key}=${value}|" "$file"
        fi
        echo "  Updated: $key"
    else
        # Add new
        echo "${key}=${value}" >> "$file"
        echo "  Added: $key"
    fi
}

echo "Fixing environment variables..."

# Fix CORS
update_env "CORS_ALLOWED_ORIGINS" "https://abparts.oraseas.com"
update_env "CORS_ALLOW_CREDENTIALS" "true"

# Fix ENVIRONMENT
update_env "ENVIRONMENT" "production"

# Generate SECRET_KEY if missing or too short
if ! grep -q "^SECRET_KEY=.\{20,\}" .env; then
    SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    update_env "SECRET_KEY" "$SECRET"
fi

# Generate JWT_SECRET_KEY if missing or too short
if ! grep -q "^JWT_SECRET_KEY=.\{20,\}" .env; then
    JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    update_env "JWT_SECRET_KEY" "$JWT_SECRET"
fi

echo ""
echo "✓ .env file updated"
echo ""
echo "Key settings:"
grep -E "^(CORS_ALLOWED_ORIGINS|ENVIRONMENT|SECRET_KEY|JWT_SECRET_KEY)=" .env | sed 's/=.*/=***/' | head -4
echo ""
echo "Next steps:"
echo "  1. Review .env file: nano .env"
echo "  2. Restart services: docker compose restart"
echo "  3. Verify: ./verify_production_setup.sh"
echo ""
