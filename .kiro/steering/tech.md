# ABParts Technical Stack

## Architecture

**Client-Server Architecture** with containerized microservices:
- React SPA frontend
- FastAPI Python backend
- PostgreSQL database
- Redis for caching and task queuing
- Celery for background tasks

## Backend Stack

**Framework:** FastAPI with Uvicorn ASGI server
**Language:** Python 3.8+
**ORM:** SQLAlchemy with Alembic migrations
**Authentication:** JWT with passlib/bcrypt
**Validation:** Pydantic schemas
**Task Queue:** Celery with Redis broker
**Database:** PostgreSQL 15

**Key Libraries:**
- `fastapi` - Core API framework
- `sqlalchemy` - Database ORM
- `pydantic` - Data validation/serialization
- `python-jose` - JWT handling
- `redis` - Caching and message broker
- `celery` - Async task processing

## Frontend Stack

**Framework:** React 18 with Create React App
**Language:** JavaScript ES6+
**Routing:** React Router v7
**Styling:** Tailwind CSS
**State Management:** React Context + hooks
**Charts:** Recharts
**HTTP Client:** Fetch API

## Development Environment

**Containerization:** Docker + Docker Compose
**Database Admin:** PgAdmin4
**Live Reload:** Enabled for both frontend and backend

## Common Commands

```bash
# Start full development environment
docker-compose up

# Backend only (API + DB + Redis)
docker-compose up db redis api

# Run database migrations
docker-compose exec api alembic upgrade head

# Create new migration
docker-compose exec api alembic revision --autogenerate -m "description"

# Access database directly
docker-compose exec db psql -U abparts_user -d abparts_dev

# View logs
docker-compose logs api
docker-compose logs web

# Rebuild containers after dependency changes
docker-compose build --no-cache
```

## Code Organization

**Backend (`backend/app/`):**
- `main.py` - FastAPI app initialization
- `models.py` - SQLAlchemy ORM models
- `schemas.py` - Pydantic request/response schemas
- `auth.py` - Authentication logic
- `database.py` - DB connection and session management
- `routers/` - API endpoints organized by resource
- `crud/` - Database operations (Create, Read, Update, Delete)

**Frontend (`frontend/src/`):**
- `App.js` - Root component with routing
- `AuthContext.js` - Authentication state management
- `components/` - Reusable UI components
- `index.css` - Tailwind CSS imports

## Database Conventions

- **Primary Keys:** UUIDs for all entities
- **Timestamps:** `created_at` and `updated_at` on all tables
- **Soft Deletes:** Use status fields rather than hard deletes
- **Enums:** Use SQLAlchemy Enum types for constrained values
- **Relationships:** Explicit foreign keys with proper constraints

## API Conventions

- **RESTful endpoints:** `/organizations`, `/users`, `/parts`
- **Authentication:** Bearer token in Authorization header
- **Error Handling:** HTTP status codes with JSON error responses
- **Validation:** Pydantic schemas for all request/response data
- **Documentation:** Auto-generated OpenAPI docs at `/docs`

## Security Practices

- JWT tokens with 8-hour expiration
- Password hashing with bcrypt
- Role-based access control enforcement
- Organization-scoped data access
- Input validation on all endpoints
- CORS middleware configured for development