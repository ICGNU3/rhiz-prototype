# Rhiz Project Structure

## Overview
This document defines the standardized folder structure for the Rhiz platform, implementing clean separation of concerns between frontend React components and backend Python services.

## Directory Organization

### Frontend Structure
```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── auth/           # Authentication components
│   │   ├── contacts/       # Contact management components
│   │   ├── layout/         # Layout components (Navbar, etc.)
│   │   ├── network/        # Network visualization components
│   │   ├── trust/          # Trust insights components
│   │   └── index.ts        # Component exports
│   ├── pages/              # Main page components
│   │   ├── ContactsPage.tsx    # Modern contact management
│   │   ├── CrmPage.tsx         # CRM pipeline interface
│   │   ├── DashboardPage.tsx   # Main dashboard
│   │   ├── GoalsPage.tsx       # Goal management
│   │   ├── IntelligencePage.tsx # AI intelligence interface
│   │   ├── NetworkPage.tsx     # Network visualization
│   │   ├── OnboardingPage.tsx  # User onboarding
│   │   ├── Settings.tsx        # User settings
│   │   └── TrustPage.tsx       # Trust insights dashboard
│   ├── services/           # API and external services
│   │   └── api.ts          # API client functions
│   ├── context/            # React context providers
│   │   └── AppContext.tsx  # Global app state
│   ├── types/              # TypeScript type definitions
│   │   └── api.ts          # API response types
│   └── styles/             # CSS and styling
│       └── globals.css     # Global styles
```

### Backend Structure
```
backend/
├── models/                 # Data models and database schemas
│   └── models.py          # Database models (User, Contact, Goal, etc.)
├── routes/                # API endpoints and route handlers
│   ├── api_routes.py      # Main REST API routes
│   └── routes.py          # Legacy Flask routes
├── services/              # Business logic and external services
│   ├── auth.py            # Authentication service
│   └── database_helpers.py # Database utilities
└── utils/                 # Utility functions and helpers
    └── linkedin_scraper.py # LinkedIn integration utilities
```

### Root Level Organization
```
project-root/
├── frontend/              # React frontend application
├── backend/               # Python backend services
├── deprecated/            # Legacy code and deprecated components
│   ├── templates/         # Old Flask HTML templates
│   └── components/        # Deprecated React components
├── static/               # Static assets and builds
├── app.py                # Flask application configuration
├── main.py               # Application entry point
├── package.json          # Node.js dependencies
├── pyproject.toml        # Python dependencies
└── replit.md            # Project documentation and architecture
```

## Component Organization Principles

### Frontend Components
- **Atomic Design**: Components organized by complexity (atoms → molecules → organisms)
- **Feature-based Grouping**: Related components grouped by functionality
- **Single Responsibility**: Each component has one clear purpose
- **TypeScript Integration**: All components use TypeScript for type safety

### Backend Services
- **Domain Separation**: Services organized by business domain
- **API Layer**: Clean REST API interface for frontend integration
- **Data Layer**: Centralized database models and utilities
- **Business Logic**: Service layer handles complex operations

## Deprecated Code Management
All legacy code is moved to the `deprecated/` directory to maintain project history while keeping the active codebase clean:

- **templates/**: Old Flask HTML templates replaced by React components
- **components/pages/**: Superseded React components with "Old" or original names
- ***.py files**: Deprecated Python modules and utilities

## File Naming Conventions

### Frontend
- **Components**: PascalCase (e.g., `ContactsPage.tsx`, `TrustPanel.tsx`)
- **Services**: camelCase (e.g., `api.ts`, `authService.ts`)
- **Types**: camelCase with `.ts` extension (e.g., `api.ts`, `models.ts`)

### Backend
- **Models**: snake_case (e.g., `models.py`, `user_model.py`)
- **Services**: snake_case (e.g., `auth.py`, `database_helpers.py`)
- **Routes**: snake_case (e.g., `api_routes.py`, `auth_routes.py`)

## Import Patterns

### Frontend Imports
```typescript
// Relative imports for local components
import ContactsPage from './pages/ContactsPage';
import { api } from '../services/api';

// Absolute imports for external libraries
import { useQuery } from '@tanstack/react-query';
import { Routes, Route } from 'react-router-dom';
```

### Backend Imports
```python
# Relative imports within backend
from backend.models.models import User, Contact
from backend.services.auth import AuthManager
from backend.routes.api_routes import register_api_routes

# External library imports
from flask import Flask, request, jsonify
from sqlalchemy import Column, String, DateTime
```

## Development Workflow

### Adding New Features
1. **Frontend**: Create components in appropriate `frontend/src/components/` subdirectory
2. **Backend**: Add services to `backend/services/`, routes to `backend/routes/`
3. **Integration**: Connect via API calls in `frontend/src/services/api.ts`
4. **Types**: Update TypeScript types in `frontend/src/types/api.ts`

### Code Organization Rules
- **No Root-Level Code**: All active code belongs in `frontend/` or `backend/`
- **Clear Boundaries**: Frontend handles UI/UX, backend handles data/logic
- **Consistent Naming**: Follow established naming conventions
- **Deprecation Process**: Move outdated code to `deprecated/` rather than deletion

## Architecture Benefits

### Maintainability
- Clear separation of concerns
- Predictable file locations
- Consistent naming patterns
- Isolated deprecated code

### Scalability
- Domain-based organization
- Modular component structure
- Service-oriented backend
- Type-safe interfaces

### Developer Experience
- Intuitive project navigation
- Reduced cognitive load
- Clear import patterns
- Self-documenting structure

## Migration Status

### Completed
✅ Backend services moved to `backend/` structure
✅ Old page components moved to `deprecated/components/`
✅ React components renamed (removed "New" suffixes)
✅ Import paths updated for new structure
✅ Legacy HTML templates moved to `deprecated/templates/`

### Architecture Compliance
This structure ensures Rhiz follows modern full-stack development best practices with clear frontend/backend separation, type safety, and maintainable code organization.