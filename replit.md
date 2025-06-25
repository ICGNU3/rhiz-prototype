# Founder Network AI

## Overview

This is a Flask-based web application that helps founders connect with the right people in their network to achieve specific goals. The system uses OpenAI's embedding API to match contacts with goals based on semantic similarity, providing AI-powered networking recommendations.

## System Architecture

The application follows a traditional Flask MVC architecture with the following key components:

- **Frontend**: HTML templates with Bootstrap for UI, using a dark theme optimized for Replit
- **Backend**: Flask web framework with Python 3.11
- **Database**: SQLite for local data storage with a well-defined schema
- **AI Integration**: OpenAI API for embeddings and content generation
- **Deployment**: Gunicorn WSGI server with autoscale deployment on Replit

## Key Components

### Database Layer
- **SQLite Database**: Single-file database (`db.sqlite3`) for simplicity and portability
- **Models**: Object-oriented database access through custom model classes (`User`, `Contact`, `Goal`, `AISuggestion`, `ContactInteraction`)
- **Schema**: Well-structured tables supporting users, contacts, goals, AI suggestions, and interaction tracking

### AI Integration
- **Embeddings**: Uses OpenAI's `text-embedding-3-small` model for semantic vector representations
- **Content Generation**: Leverages GPT-4o for personalized outreach message creation
- **Similarity Matching**: Cosine similarity algorithm to match contacts with goals

### Web Interface
- **Dashboard**: Overview of goals, contacts, and AI-powered insights
- **Goal Management**: Create and manage founder objectives with AI processing
- **Contact Management**: Maintain network relationships with detailed profiles
- **AI Suggestions**: View and act on intelligent contact recommendations

### Core Features
- **Semantic Goal Matching**: AI analyzes goal descriptions and contact information to suggest relevant connections
- **Personalized Outreach**: Generates custom messages based on goals and contact context
- **Interaction Tracking**: Maintains history of contact engagements
- **Demo Data Seeding**: Automatically populates sample data for demonstration

## Data Flow

1. **Goal Creation**: User creates a goal → System generates embedding → Stores in database
2. **Contact Management**: User adds contacts with notes → Data stored for AI analysis
3. **AI Matching**: System calculates cosine similarity between goal and contact embeddings
4. **Suggestion Generation**: Top matches presented with confidence scores and generated outreach messages
5. **Interaction Tracking**: User actions and follow-ups recorded for relationship management

## External Dependencies

### Required APIs
- **OpenAI API**: Essential for embeddings and content generation (requires `OPENAI_API_KEY`)

### Python Packages
- **Flask**: Web framework and routing
- **OpenAI**: API client for AI services
- **NumPy**: Vector operations and similarity calculations
- **Gunicorn**: Production WSGI server
- **Werkzeug**: WSGI utilities and middleware

### Frontend Dependencies
- **Bootstrap 5.3**: UI framework with Replit dark theme
- **Bootstrap Icons**: Icon library for enhanced UX

## Deployment Strategy

### Development Environment
- **Local Development**: Flask development server with hot reload
- **Database**: SQLite with automatic schema initialization
- **Configuration**: Environment variables for API keys and secrets

### Production Deployment
- **Server**: Gunicorn with autoscale deployment target
- **Process Management**: Replit's workflow system for application lifecycle
- **Static Assets**: CDN-hosted Bootstrap and icons for performance
- **Session Management**: Flask sessions with configurable secret key

### Environment Configuration
- **Database Path**: `db.sqlite3` in project root
- **API Keys**: Stored in Replit Secrets or environment variables
- **Logging**: Debug-level logging for development, configurable for production

## Changelog
- June 25, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.