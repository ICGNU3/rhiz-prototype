# Founder Network AI - Contact Intelligence CRM

## Overview

This is a comprehensive Flask-based contact intelligence and CRM system specifically designed for founders to manage their network relationships with AI-powered insights. The system combines traditional CRM functionality with advanced AI features including semantic goal matching, natural language query processing, and intelligent outreach suggestions.

## System Architecture

The application follows an enhanced Flask MVC architecture with AI-powered contact intelligence:

- **Frontend**: Bootstrap 5.3 responsive UI with dark theme, featuring dashboard views, Kanban pipeline, and natural language interface
- **Backend**: Flask web framework with Python 3.11, modular CRM intelligence system
- **Database**: SQLite with comprehensive contact relationship schema supporting warmth tracking, interaction logging, and pipeline management
- **AI Integration**: OpenAI GPT-4o for embeddings, content generation, and natural language processing
- **CRM Intelligence**: Advanced contact scoring, outreach suggestions, and relationship pipeline management
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

## Recent Changes
- **June 26, 2025**: Ultra Modern 2025 Landing Page implementation completed
  - Created stunning modern homepage with Inter fonts and contemporary design aesthetics
  - Implemented hero section with goal-first messaging and animated network visualization
  - Added three-step "How It Works" cards with hover animations and clean iconography
  - Built feature showcase with grid layout and sophisticated hover effects
  - Created philosophy strip emphasizing outcomes over contacts with refined typography
  - Added network map preview with animated pulse nodes and gradient backgrounds
  - Implemented dual CTA strategy with primary and final call-to-action sections
  - Established modern color palette (off-white backgrounds, charcoal text, electric blue accents)
  - Applied consistent spacing, rounded corners, and subtle shadow effects throughout
  - Set landing page as homepage with dashboard accessible via /dashboard route
  - Maintained goal-first navigation philosophy while creating compelling first impression

- **June 26, 2025**: Goal-First Navigation & UX Reorganization completed
  - Restructured navigation to follow "Start with a goal, find your people, act with intention" philosophy
  - Simplified navigation from 8 top-level items to 5 focused sections: Home, Goals, Relationships, Intelligence, Map, Settings
  - Transformed home dashboard into dynamic feed surfacing today's most relevant goals, contacts, and AI suggestions
  - Reorganized features under logical groupings: Relationships (pipeline, contacts, import), Intelligence (AI suggestions, network analysis, progress), Settings (integrations, conference mode, motivation preferences)
  - Created goal-centric homepage that prioritizes active goals with direct "Find People" actions
  - Enhanced contact display with warmth indicators and relationship context
  - Built AI insights column showing intelligent suggestions based on goal alignment
  - Maintained background gamification with subtle XP counter integrated into new layout

- **June 26, 2025**: Background Gamification Engine implementation completed
  - Transformed gamification from explicit dashboard to invisible background system
  - Created subtle feedback engine with toast notifications, glow effects, and micro-rewards
  - Built contextual quest hints that appear organically in goal and contact workflows
  - Implemented user preference modes: Motivated (full feedback), Clean (minimal), Quiet (silent)
  - Added XP tracking with level progression (Contact Seeker → Connection Master) operating behind the scenes
  - Created JavaScript gamification engine for real-time feedback without breaking user immersion
  - Integrated background XP rewards into all major networking actions with contextual messaging
  - Built achievement system that celebrates meaningful progress toward user-defined goals
  - Removed explicit gamification navigation to maintain focus on core networking functionality
  - Enhanced dashboard with subtle XP counter and progress indicators

- **June 26, 2025**: Conference Mode feature implementation completed
  - Created comprehensive Conference Mode for networking events and conferences
  - Built smart contact capture system with AI-powered enhancement and analysis
  - Implemented voice memo processing to extract contact information automatically
  - Added AI-generated follow-up suggestions with personalized messages and timing
  - Created daily follow-up summary dashboard showing priority contacts
  - Built conference contact management with auto-tagging and goal relevance scoring
  - Added conference activation/deactivation system with location and date tracking
  - Integrated Conference Mode into main navigation for easy access during events

- **June 26, 2025**: Contact relationship mapping and network visualization implemented
  - Built interactive network graph with vis.js showing contact relationships and connection strength
  - Created comprehensive relationship management system with strength scoring (1-5 scale)
  - Added network metrics dashboard showing density, total relationships, and average connections
  - Implemented introduction suggestions based on mutual connections and relationship analysis
  - Added relationship creation interface with multiple relationship types (knows, worked_with, invested_in, etc.)
  - Created network export functionality for CSV and JSON formats
  - Added network visualization to main navigation with dedicated "Network Map" section

- **June 26, 2025**: Rhizomatic Intelligence Layer implementation completed
  - Created living, non-linear AI network analysis system with Neo4j-style bloom animations
  - Built interactive network visualization using vis.js with dynamic connection mapping
  - Implemented PostgreSQL-compatible database queries and API endpoints
  - Restructured navigation to house Rhizomatic Intelligence under CRM Intelligence dropdown
  - Added comprehensive rhizomatic prompt system for AI-powered relationship insights
  - Created database table for storing rhizomatic insights and network data

- **June 25, 2025**: Mobile-First Progressive Web App (PWA) implementation completed
  - Comprehensive PWA manifest with app shortcuts and share targets
  - Service worker with intelligent caching strategies (cache-first, network-first, stale-while-revalidate)
  - Offline contact management with IndexedDB storage and background sync
  - Push notification infrastructure for follow-up reminders
  - Voice command integration through Web Speech API and Telegram bridge
  - Mobile-optimized templates with touch-friendly interfaces and accessibility
  - Auto-saving forms with localStorage for offline capability
  - Pull-to-refresh, swipe gestures, and mobile navigation patterns
  - Safe area handling for modern mobile devices with notches/islands

- **June 25, 2025**: Telegram bot integration completed with comprehensive automation features
  - Full-featured Telegram bot with interactive commands (/stats, /contacts, /goals, /followups, /digest, /export)
  - Natural language processing for conversational queries ("Show warm contacts", "What's due?")
  - Automated networking notifications for email sends, follow-ups, and daily digests
  - Interactive inline buttons for quick actions (mark follow-ups complete, refresh data)
  - CSV export functionality directly through Telegram with automatic file delivery
  - Comprehensive setup instructions and configuration interface
  - Integration with existing automation engine for dual Slack/Telegram notifications

- **June 25, 2025**: Network visualization and relationship mapping completed
  - Interactive network graph with vis.js rendering (12 contacts, 15 relationships)
  - Network metrics analysis (22.7% density, 2.5 avg connections per contact)
  - Intelligent introduction suggestions with mutual connection scoring
  - Relationship strength mapping (1-5 scale) with visual edge representation
  - Network clustering by company and relationship type analysis
  - API endpoints for real-time network data (/network/api/graph, /network/api/metrics)
  - Contact relationship management with business context (investor/founder, mentor/mentee)

- **June 25, 2025**: Analytics dashboard with outreach success rates completed
  - Comprehensive outreach performance metrics (87.5% email success rate, 28.6% response rate)
  - Contact effectiveness analysis by relationship type and warmth level
  - Goal performance tracking with interaction success rates
  - Network growth trends and pipeline analytics
  - Top performing contacts with response rate rankings
  - Daily activity trends and interaction timeline visualization
  - API endpoints for real-time analytics data and dashboard integration

- **June 25, 2025**: Email integration for direct message sending completed
  - SMTP configuration with auto-detection for Gmail, Outlook, and Yahoo
  - Direct email sending from goal matcher interface with pre-filled AI messages
  - Email configuration management with setup instructions for major providers
  - Interaction logging for sent emails with success/failure tracking
  - Modal-based email composition with editable subjects and messages
  - Fallback to email client integration for users without SMTP setup
  - Environment variable configuration for secure credential management

- **June 25, 2025**: CSV import functionality for bulk contact uploads completed
  - Automatic field detection supporting various CSV formats and column names
  - Data validation with comprehensive error handling and warnings
  - Duplicate contact detection based on email addresses
  - Sample CSV template download functionality
  - Import statistics and detailed error reporting
  - Support for all contact fields including company, title, LinkedIn, relationship type
  - Navigation integration with dedicated import interface

- **June 25, 2025**: Single-page goal-based contact matcher implemented
  - Fast template-based message generation with multiple tone options (warm, professional, casual, urgent)
  - Streamlined goal creation form with instant contact matching
  - Copy-to-clipboard functionality for quick outreach
  - Semantic similarity matching using OpenAI embeddings
  - Fallback message templates to ensure reliable operation
  - Multiple goals support with historical goal management
  - Working tool prioritizing functionality over aesthetics per user preference

- **June 25, 2025**: Complete CRM intelligence module implemented
  - Enhanced database schema with warmth tracking, interaction logging, and pipeline management
  - Natural language query interface for contact intelligence
  - Kanban pipeline view for relationship stages (Cold → Aware → Warm → Active → Contributor)
  - AI-powered daily outreach suggestions with priority scoring
  - Comprehensive contact detail views with interaction timelines
  - Auto-running schema.sql on first boot with migration support

## User Preferences

Preferred communication style: Simple, everyday language.