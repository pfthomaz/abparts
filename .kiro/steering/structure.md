# ABParts Project Structure

## Root Directory Organization

```
abparts/
├── backend/           # FastAPI Python backend
├── frontend/          # React frontend application
├── docs/             # Project documentation
├── init_db/          # Database initialization scripts
├── .kiro/            # Kiro AI assistant configuration
├── docker-compose.yml # Development environment orchestration
└── README.md         # Project overview and setup
```

## Backend Structure (`backend/`)

```
backend/
├── app/                    # Main application package
│   ├── main.py            # FastAPI app initialization and routing
│   ├── models.py          # SQLAlchemy ORM models
│   ├── schemas.py         # Pydantic request/response schemas
│   ├── auth.py            # Authentication and authorization
│   ├── database.py        # Database connection and session management
│   ├── celery_app.py      # Celery task queue configuration
│   ├── tasks.py           # Background task definitions
│   ├── routers/           # API endpoint modules by resource
│   │   ├── organizations.py
│   │   ├── users.py
│   │   ├── parts.py
│   │   ├── inventory.py
│   │   ├── warehouses.py
│   │   ├── machines.py
│   │   ├── customer_orders.py
│   │   ├── supplier_orders.py
│   │   ├── stock_adjustments.py
│   │   ├── dashboard.py
│   │   └── ...
│   └── crud/              # Database operation modules
│       ├── organizations.py
│       ├── users.py
│       ├── parts.py
│       └── ...
├── alembic/               # Database migration files
├── static/                # Static file storage (images, etc.)
├── requirements.txt       # Python dependencies
├── Dockerfile.backend     # Backend container definition
└── alembic.ini           # Alembic migration configuration
```

## Frontend Structure (`frontend/`)

```
frontend/
├── public/               # Static assets and HTML template
├── src/                  # React application source
│   ├── index.js         # Application entry point
│   ├── App.js           # Root component with routing
│   ├── AuthContext.js   # Authentication state management
│   ├── index.css        # Global styles and Tailwind imports
│   └── components/      # Reusable UI components
│       ├── LoginForm.js
│       ├── Modal.js
│       ├── OrganizationForm.js
│       ├── PartForm.js
│       ├── UserForm.js
│       └── ...
├── package.json         # Node.js dependencies and scripts
├── tailwind.config.js   # Tailwind CSS configuration
├── postcss.config.js    # PostCSS configuration
└── Dockerfile.frontend  # Frontend container definition
```

## Documentation Structure (`docs/`)

```
docs/
├── PRODUCT_REQUIREMENTS.md    # Detailed product requirements
├── DEVELOPMENT_PLAN.md        # Implementation roadmap
├── BACKEND_STATUS.md          # Backend development status
├── FRONTEND_STATUS.md         # Frontend development status
└── Phase 3 - User Management & Authentication Enhancements.md
```

## Configuration Files

- **`.env`** - Environment variables (not in version control)
- **`docker-compose.yml`** - Development environment services
- **`.gitignore`** - Git ignore patterns
- **`validate_migration.py`** - Database migration validation
- **`validate_models.py`** - Model validation utilities

## Kiro AI Configuration (`.kiro/`)

```
.kiro/
├── steering/             # AI assistant guidance documents
│   ├── product.md       # Product overview and business model
│   ├── tech.md          # Technical stack and conventions
│   └── structure.md     # Project organization (this file)
└── specs/               # Feature specifications and implementation plans
    └── abparts-business-model-alignment/
        ├── requirements.md
        └── tasks.md
```

## File Naming Conventions

**Backend:**
- **Models:** Singular nouns (`user.py`, `organization.py`)
- **Routers:** Plural nouns matching resource (`users.py`, `organizations.py`)
- **CRUD modules:** Match model names (`user.py`, `organization.py`)
- **Database tables:** Plural snake_case (`users`, `customer_orders`)

**Frontend:**
- **Components:** PascalCase (`LoginForm.js`, `UserProfile.js`)
- **Utilities:** camelCase (`apiClient.js`, `dateUtils.js`)
- **Pages/Views:** PascalCase with descriptive names

## Import Conventions

**Backend:**
```python
# Relative imports within app package
from .database import get_db
from .models import User, Organization
from .schemas import UserCreate, UserResponse
from .auth import get_current_user

# Router imports in main.py
from .routers.users import router as users_router
```

**Frontend:**
```javascript
// React and external libraries
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// Internal components and utilities
import AuthContext from './AuthContext';
import LoginForm from './components/LoginForm';
```

## Development Workflow

1. **Backend changes:** Modify models → Update schemas → Implement CRUD → Add router endpoints
2. **Database changes:** Create Alembic migration → Test migration → Update models/schemas
3. **Frontend changes:** Update components → Test integration → Update routing if needed
4. **Full feature:** Backend API → Frontend integration → Documentation → Testing

## Key Architectural Principles

- **Separation of concerns:** Clear boundaries between data, business logic, and presentation
- **Resource-based organization:** Group related functionality by business entity
- **Dependency injection:** Use FastAPI's Depends system for database sessions and auth
- **Component reusability:** Build modular, reusable React components
- **Configuration management:** Environment-based configuration with sensible defaults