import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, Target, Users, Brain, Share2, Settings, LogOut } from 'lucide-react';

interface NavbarProps {
  user?: { email: string; subscription_tier: string };
  onLogout: () => void;
}

const Navbar: React.FC<NavbarProps> = ({ user, onLogout }) => {
  const location = useLocation();

  const navItems = [
    { path: '/app/dashboard', icon: Home, label: 'Home' },
    { path: '/app/goals', icon: Target, label: 'Goals' },
    { path: '/app/contacts', icon: Users, label: 'Contacts' },
    { path: '/app/network', icon: Share2, label: 'Network' },
    { path: '/app/intelligence', icon: Brain, label: 'Intelligence' },
    { path: '/app/settings', icon: Settings, label: 'Settings' },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="backdrop-blur-xl border-b border-white/10" style={{ backgroundColor: 'rgba(255, 255, 255, 0.05)' }}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/app/dashboard" className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
              <span className="text-white font-bold text-sm">R</span>
            </div>
            <span className="font-bold text-xl" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent' }}>Rhiz</span>
          </Link>

          {/* Navigation Items */}
          <div className="hidden md:flex items-center space-x-1">
            {navItems.map(({ path, icon: Icon, label }) => (
              <Link
                key={path}
                to={path}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center space-x-2 ${
                  isActive(path)
                    ? 'text-white border border-white/30'
                    : 'hover:text-white hover:border-white/20'
                }`}
                style={isActive(path) 
                  ? { backgroundColor: 'rgba(255, 255, 255, 0.1)' }
                  : { color: 'var(--text-secondary)' }
                }
              >
                <Icon size={16} />
                <span>{label}</span>
              </Link>
            ))}
          </div>

          {/* User Menu */}
          <div className="flex items-center space-x-4">
            {user && (
              <div className="hidden sm:flex items-center space-x-3">
                <div className="text-right">
                  <p className="text-sm text-white">{user.email}</p>
                  <p className="text-xs text-gray-400 capitalize">{user.subscription_tier}</p>
                </div>
                <button
                  onClick={onLogout}
                  className="glass-button-secondary p-2 hover:border-red-500"
                  title="Logout"
                >
                  <LogOut size={16} />
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      <div className="md:hidden border-t border-dark-border">
        <div className="px-2 py-3 grid grid-cols-5 gap-1">
          {navItems.map(({ path, icon: Icon, label }) => (
            <Link
              key={path}
              to={path}
              className={`flex flex-col items-center justify-center p-2 rounded-lg text-xs transition-all duration-200 ${
                isActive(path)
                  ? 'text-primary-400 bg-primary-500/20'
                  : 'text-gray-400 hover:text-white hover:bg-dark-border/50'
              }`}
            >
              <Icon size={18} />
              <span className="mt-1">{label}</span>
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;