#!/bin/bash
# scripts/prod.sh - Production environment management

set -e

# Load production environment (filter out comments and empty lines)
if [ -f .env.production ]; then
    export $(grep -v '^#' .env.production | grep -v '^$' | xargs)
fi

echo "🚀 Managing ABParts Production Environment..."

case "$1" in
  "start")
    echo "Starting production services..."
    docker compose -f docker-compose.prod.yml --env-file .env.production up -d
    echo "✅ Production environment started!"
    echo "🌐 Frontend: http://46.62.153.166:81"
    echo "🔧 API: http://46.62.153.166:8001"
    ;;
  "start-with-admin")
    echo "Starting production services with PgAdmin..."
    docker compose -f docker-compose.prod.yml --env-file .env.production --profile admin up -d
    echo "✅ Production environment started with admin tools!"
    echo "🌐 Frontend: http://46.62.153.166:81"
    echo "🔧 API: http://46.62.153.166:8001"
    echo "📊 PgAdmin: http://46.62.153.166:8080"
    ;;
  "stop")
    echo "Stopping production services..."
    docker compose -f docker-compose.prod.yml down
    echo "✅ Production environment stopped!"
    ;;
  "restart")
    echo "Restarting production services..."
    docker compose -f docker-compose.prod.yml --env-file .env.production restart
    echo "✅ Production environment restarted!"
    ;;
  "build")
    echo "Building production services..."
    docker compose -f docker-compose.prod.yml --env-file .env.production build --no-cache
    echo "✅ Production services built!"
    ;;
  "deploy")
    echo "Deploying to production..."
    docker compose -f docker-compose.prod.yml --env-file .env.production down
    docker compose -f docker-compose.prod.yml --env-file .env.production build --no-cache
    docker compose -f docker-compose.prod.yml --env-file .env.production up -d
    echo "✅ Production deployment complete!"
    ;;
  "logs")
    docker compose -f docker-compose.prod.yml logs -f ${2:-}
    ;;
  "shell")
    docker compose -f docker-compose.prod.yml exec ${2:-api} /bin/sh
    ;;
  "backup")
    echo "Creating database backup..."
    docker compose -f docker-compose.prod.yml exec db pg_dump -U $POSTGRES_USER $POSTGRES_DB > "backup_$(date +%Y%m%d_%H%M%S).sql"
    echo "✅ Database backup created!"
    ;;
  *)
    echo "Usage: $0 {start|start-with-admin|stop|restart|build|deploy|logs [service]|shell [service]|backup}"
    echo "Examples:"
    echo "  $0 start              # Start production services"
    echo "  $0 start-with-admin   # Start with PgAdmin"
    echo "  $0 deploy             # Full deployment"
    echo "  $0 logs api           # Show API logs"
    echo "  $0 backup             # Backup database"
    exit 1
    ;;
esac