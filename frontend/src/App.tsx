import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import './styles/globals.css';
import { AppProvider, useAuth } from './context/AppContext';
import Navbar from './components/layout/Navbar';
import DashboardPage from './pages/DashboardPage';
import GoalsPage from './pages/GoalsPage';
import ContactsPage from './pages/ContactsPage';
import IntelligencePage from './pages/IntelligencePage';
import TrustPage from './pages/TrustPage';
import CrmPage from './pages/CrmPage';
import Settings from './pages/Settings';
import OnboardingPage from './pages/OnboardingPage';
import NetworkPage from './pages/NetworkPage';
import LandingPage from './pages/LandingPage';
import Login from './components/auth/Login';

// Create a query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function AppContent() {
  const { user, isLoading, isAuthenticated, logout } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 flex items-center justify-center">
        <div className="glass-card p-8 text-center">
          <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-white">Loading your network...</p>
        </div>
      </div>
    );
  }

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={!isAuthenticated ? <LandingPage /> : <Navigate to="/app/dashboard" replace />} />
      <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/app/dashboard" replace />} />
      
      {/* Protected app routes */}
      {isAuthenticated && user ? (
        <>
          <Route path="/app/*" element={
            <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 flex flex-col">
              <Navbar user={user} onLogout={logout} />
              <main className="flex-1 p-6">
                <div className="max-w-7xl mx-auto">
                  <Routes>
                    <Route path="onboarding" element={<OnboardingPage />} />
                    <Route path="dashboard" element={<DashboardPage />} />
                    <Route path="goals" element={<GoalsPage />} />
                    <Route path="contacts" element={<ContactsPage />} />
                    <Route path="intelligence" element={<IntelligencePage />} />
                    <Route path="network" element={<NetworkPage />} />
                    <Route path="trust" element={<TrustPage />} />
                    <Route path="crm" element={<CrmPage />} />
                    <Route path="settings" element={<Settings />} />
                  </Routes>
                </div>
              </main>
            </div>
          } />
          
          {/* Legacy route redirects */}
          <Route path="/onboarding" element={<Navigate to="/app/onboarding" replace />} />
          <Route path="/dashboard" element={<Navigate to="/app/dashboard" replace />} />
          <Route path="/goals" element={<Navigate to="/app/goals" replace />} />
          <Route path="/contacts" element={<Navigate to="/app/contacts" replace />} />
          <Route path="/intelligence" element={<Navigate to="/app/intelligence" replace />} />
          <Route path="/settings" element={<Navigate to="/app/settings" replace />} />
        </>
      ) : (
        /* Redirect unauthenticated users to landing page */
        <Route path="*" element={<Navigate to="/" replace />} />
      )}
    </Routes>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppProvider>
        <Router>
          <AppContent />
        </Router>
      </AppProvider>
    </QueryClientProvider>
  );
}

export default App;