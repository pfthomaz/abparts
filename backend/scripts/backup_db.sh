#!/bin/bash

# Database backup script for ABParts
# Usage: ./backup_db.sh [environment]

set -e

ENVIRONMENT=${1:-development}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Set database connection parameters based on environment
case $ENVIRONMENT in
    "development")
        DB_HOST="localhost"
        DB_PORT="5432"
        DB_NAME="abparts_dev"
        DB_USER="abparts_user"
        ;;
    "test")
        DB_HOST="localhost"
        DB_PORT="5432"
        DB_NAME="abparts_test"
        DB_USER="abparts_user"
        ;;
    "production")
        # These should be set as environment variables in production
        DB_HOST=${PROD_DB_HOST:-"localhost"}
        DB_PORT=${PROD_DB_PORT:-"5432"}
        DB_NAME=${PROD_DB_NAME:-"abparts_prod"}
        DB_USER=${PROD_DB_USER:-"abparts_user"}
        ;;
    *)
        echo "Unknown environment: $ENVIRONMENT"
        echo "Usage: $0 [development|test|production]"
        exit 1
        ;;
esac

BACKUP_FILE="$BACKUP_DIR/abparts_${ENVIRONMENT}_${TIMESTAMP}.sql"

echo "Creating backup of $DB_NAME database..."
echo "Backup file: $BACKUP_FILE"

# Create backup
if [ "$ENVIRONMENT" = "development" ] || [ "$ENVIRONMENT" = "test" ]; then
    # For local development, use Docker
    docker-compose exec -T db pg_dump -U $DB_USER -d $DB_NAME > $BACKUP_FILE
else
    # For production, use direct connection
    pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME > $BACKUP_FILE
fi

# Compress backup
gzip $BACKUP_FILE

echo "Backup completed: ${BACKUP_FILE}.gz"
echo "Backup size: $(du -h ${BACKUP_FILE}.gz | cut -f1)"

# Clean up old backups (keep last 10)
echo "Cleaning up old backups..."
ls -t $BACKUP_DIR/abparts_${ENVIRONMENT}_*.sql.gz | tail -n +11 | xargs -r rm

echo "Backup process completed successfully!"