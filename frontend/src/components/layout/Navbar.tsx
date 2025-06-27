import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, Target, Users, Brain, Heart, Settings, LogOut } from 'lucide-react';

interface NavbarProps {
  user?: { email: string; subscription_tier: string };
  onLogout: () => void;
}

const Navbar: React.FC<NavbarProps> = ({ user, onLogout }) => {
  const location = useLocation();

  const navItems = [
    { path: '/dashboard', icon: Home, label: 'Home' },
    { path: '/goals', icon: Target, label: 'Goals' },
    { path: '/contacts', icon: Users, label: 'Contacts' },
    { path: '/intelligence', icon: Brain, label: 'Intelligence' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="glass-card border-0 border-b border-dark-border rounded-none backdrop-blur-xl bg-dark-card/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/dashboard" className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-r from-primary-500 to-purple-500 flex items-center justify-center">
              <span className="text-white font-bold text-sm">R</span>
            </div>
            <span className="font-bold text-xl gradient-text">Rhiz</span>
          </Link>

          {/* Navigation Items */}
          <div className="hidden md:flex items-center space-x-1">
            {navItems.map(({ path, icon: Icon, label }) => (
              <Link
                key={path}
                to={path}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center space-x-2 ${
                  isActive(path)
                    ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
                    : 'text-gray-300 hover:text-white hover:bg-dark-border/50'
                }`}
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