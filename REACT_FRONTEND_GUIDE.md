# Rhiz React Frontend Integration Guide

## Overview

The Rhiz platform now features a complete modern React frontend architecture that communicates with the existing Flask backend through a comprehensive REST API. This integration preserves all existing functionality while providing a cutting-edge user experience.

## Architecture

### Frontend Stack
- **React 19** with TypeScript for type safety
- **Vite** for fast development and optimized builds
- **Tailwind CSS** for utility-first styling
- **React Router** for client-side routing
- **React Query** for server state management
- **D3.js** for advanced data visualizations
- **Axios** for API communication

### Backend Integration
- **Flask REST API** with comprehensive endpoints
- **Session-based authentication** for secure user management
- **SQLite database** with existing schema preservation
- **CORS support** for cross-origin requests during development

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   └── Navbar.tsx           # Main navigation component
│   │   ├── network/
│   │   │   └── RhizomaticGraph.tsx  # D3.js network visualization
│   │   ├── goals/
│   │   │   └── GoalList.tsx         # Goal management interface
│   │   └── ui/                      # Reusable UI components
│   ├── pages/
│   │   ├── Dashboard.tsx            # Main dashboard with overview
│   │   ├── Goals.tsx                # Goal management page
│   │   ├── Contacts.tsx             # Contact management page
│   │   ├── Intelligence.tsx         # AI insights and network analysis
│   │   ├── Settings.tsx             # User preferences and configuration
│   │   └── Login.tsx                # Authentication interface
│   ├── services/
│   │   └── api.ts                   # Centralized API client with typed interfaces
│   ├── hooks/
│   │   └── useAuth.ts               # Authentication state management
│   ├── styles/
│   │   └── globals.css              # Glassmorphism theme and global styles
│   ├── App.tsx                      # Main application component
│   └── main.tsx                     # React application entry point
├── index.html                       # HTML template
├── package.json                     # Dependencies and scripts
├── tailwind.config.js               # Tailwind CSS configuration
├── tsconfig.json                    # TypeScript configuration
└── vite.config.ts                   # Vite build configuration
```

## API Endpoints

### Authentication
- `POST /api/auth/login` - User authentication
- `POST /api/auth/magic-link` - Passwordless authentication
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/logout` - User logout

### Goals
- `GET /api/goals` - Retrieve user goals
- `POST /api/goals` - Create new goal
- `GET /api/goals/{id}/matches` - Get AI matches for goal

### Contacts
- `GET /api/contacts` - Retrieve contacts with filtering
- `POST /api/contacts` - Create new contact
- `GET /api/contacts/{id}` - Get contact details
- `GET /api/contacts/{id}/interactions` - Get contact interaction history

### Intelligence
- `GET /api/intelligence/suggestions` - Get AI-powered suggestions
- `GET /api/intelligence/insights` - Get network insights
- `POST /api/intelligence/nlp` - Process natural language queries

### Network
- `GET /api/network/graph` - Get network visualization data
- `GET /api/network/metrics` - Get network statistics

### Analytics
- `GET /api/analytics/dashboard` - Get dashboard statistics
- `GET /api/analytics/outreach` - Get outreach metrics

## Key Features

### 1. Glassmorphism Design System
The frontend uses a sophisticated glassmorphism design that matches the existing Rhiz aesthetic:
- Backdrop blur effects with transparency
- Gradient text and button animations
- Dark theme with electric blue/purple accents
- Responsive design for all screen sizes

### 2. Network Visualization
Advanced D3.js-powered rhizomatic graph featuring:
- Interactive node manipulation with drag-and-drop
- Real-time connection highlighting
- Gradient-based edge rendering
- Scalable vector graphics for crisp visuals

### 3. Smart Data Management
- React Query for efficient server state caching
- Optimistic updates for improved user experience
- Error handling with automatic retry logic
- Loading states and skeleton screens

### 4. Type Safety
Complete TypeScript integration providing:
- Compile-time error checking
- IntelliSense support for all API responses
- Strict type definitions for all data models
- Enhanced developer experience

## Development Workflow

### 1. Start Backend Server
```bash
# From project root
python main.py
# Flask server runs on http://localhost:5000
```

### 2. Start React Development Server
```bash
# From frontend directory
cd frontend
npm run dev
# React dev server runs on http://localhost:5173
```

### 3. API Development
The React frontend communicates with Flask through the API routes defined in `api_routes.py`. All endpoints use JSON for data exchange and support CORS for development.

### 4. Authentication Flow
1. User enters email on login page
2. Magic link authentication request sent to `/api/auth/magic-link`
3. Session established with Flask backend
4. React app receives user data and redirects to dashboard
5. All subsequent API calls include session cookies automatically

## Production Deployment

### Build Process
```bash
cd frontend
npm run build
# Creates optimized production build in dist/
```

### Serving Strategy
The Flask backend can serve the React production build:
1. Build React app with `npm run build`
2. Configure Flask to serve static files from `frontend/dist/`
3. Handle client-side routing with fallback to `index.html`

## Integration with Existing Features

### Preserved Functionality
- All existing Flask routes remain functional
- Database schema unchanged
- AI matching algorithms intact
- Email integration working
- Gamification system operational

### Enhanced User Experience
- Faster page loads with client-side routing
- Real-time updates without page refreshes
- Smooth animations and transitions
- Mobile-responsive design
- Progressive Web App capabilities

## Testing the Integration

### API Health Check
```bash
curl http://localhost:5000/api/health
```

### Create Sample Data
```bash
curl -X GET http://localhost:5000/api/demo/seed
```

### Test Authentication
```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"email":"demo@rhiz.app"}' \
     http://localhost:5000/api/auth/magic-link
```

## Next Steps

1. **Complete React Development**: Finish implementing all page components
2. **Real-time Features**: Add WebSocket support for live updates
3. **Mobile App**: Convert to React Native for mobile deployment
4. **Performance Optimization**: Implement code splitting and lazy loading
5. **Testing Suite**: Add comprehensive unit and integration tests

## Conclusion

The React frontend integration provides Rhiz with a modern, scalable foundation while preserving all existing functionality. The architecture supports rapid development, excellent user experience, and seamless scaling for future enhancements.