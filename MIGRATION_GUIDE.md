# Database Migration Guide

## Flask-Migrate Commands

This project uses Flask-Migrate for database version control and schema management.

### Setup
```bash
export FLASK_APP=flask_app.py
```

### Common Commands

#### Check current migration
```bash
python -m flask db current
```

#### View migration history
```bash
python -m flask db history
```

#### Create new migration
```bash
python -m flask db migrate -m "Description of changes"
```

#### Apply migrations
```bash
python -m flask db upgrade
```

#### Rollback migration
```bash
python -m flask db downgrade
```

### Seed Data

To populate the database with demo data:
```bash
python seed.py
```

This creates:
- Demo user: demo@rhiz.app
- 3 sample contacts (Sarah Chen, Marcus Rodriguez, Jennifer Kim)
- 2 sample goals (Fundraising, Partnership)

### Current Database State

The baseline migration `3bee8b128e2c` establishes the current production database schema including:
- users
- contacts
- goals
- user_auth_tokens
- ai_suggestions
- contact_interactions
- journal_entries

All future schema changes should be managed through Flask-Migrate migrations.