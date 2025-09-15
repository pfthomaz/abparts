#!/bin/bash
# scripts/dev.sh - Development environment management

set -e

# Load development environment (filter out comments and empty lines)
if [ -f .env.development ]; then
    export $(grep -v '^#' .env.development | grep -v '^$' | xargs)
fi

echo "🚀 Starting ABParts Development Environment..."

case "$1" in
  "start")
    echo "Starting development services..."
    docker compose -f docker-compose.dev.yml --env-file .env.development up -d
    echo "✅ Development environment started!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 API: http://localhost:8000"
    echo "📊 PgAdmin: http://localhost:8080"
    ;;
  "stop")
    echo "Stopping development services..."
    docker compose -f docker-compose.dev.yml down
    echo "✅ Development environment stopped!"
    ;;
  "restart")
    echo "Restarting development services..."
    docker compose -f docker-compose.dev.yml --env-file .env.development restart
    echo "✅ Development environment restarted!"
    ;;
  "build")
    echo "Building development services..."
    docker compose -f docker-compose.dev.yml --env-file .env.development build --no-cache
    echo "✅ Development services built!"
    ;;
  "logs")
    docker compose -f docker-compose.dev.yml logs -f ${2:-}
    ;;
  "shell")
    docker compose -f docker-compose.dev.yml exec ${2:-api} /bin/sh
    ;;
  *)
    echo "Usage: $0 {start|stop|restart|build|logs [service]|shell [service]}"
    echo "Examples:"
    echo "  $0 start          # Start all development services"
    echo "  $0 logs api       # Show API logs"
    echo "  $0 shell api      # Open shell in API container"
    exit 1
    ;;
esac