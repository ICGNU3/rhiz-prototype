# Backend Architecture

## Directory Structure

### `/services/`
Business logic and core intelligence engines:
- `contact_intelligence.py` - AI-powered relationship signal analysis
- `trust_insights.py` - Trust scoring and relationship strength computation
- `social_integrations.py` - OAuth sync with LinkedIn, Google Contacts, X.com
- `unified_email_service.py` - Email delivery with Resend API
- `unified_utilities.py` - Database, validation, security utilities

### `/routes/`
Flask route modules organized by feature:
- `auth_routes.py` - Authentication, magic links, session management
- `contact_routes.py` - Contact CRUD, pipeline management
- `goal_routes.py` - Goal creation, AI matching, suggestions
- `intelligence_routes.py` - Trust insights, AI chat, analytics

### `/models/`
SQLAlchemy ORM models:
- Database entity definitions
- Relationship mappings
- Data validation

### `/utils/`
Helper functions and utilities:
- Decorators
- OpenAI handlers
- Validation helpers
- Performance utilities

## Development Instructions

1. **Local Development**: 
   ```bash
   python main.py
   ```

2. **Database Migrations**:
   ```bash
   flask db migrate -m "description"
   flask db upgrade
   ```

3. **API Testing**:
   ```bash
   curl -b cookies.txt http://localhost:5000/api/health
   ```

4. **Environment Setup**:
   Copy `.env.example` to `.env` and configure required secrets.

## Architecture Principles

- Separation of concerns between routes, services, and models
- Dependency injection for services
- Comprehensive error handling and logging
- Type hints throughout Python codebase
- API-first design for React frontend integration