import React from 'react';
import { Bell, Moon, Sun, User, LogOut, Settings } from 'lucide-react';
import { useThemeStore } from '@/store/theme';
import { useAuthStore } from '@/store/auth';
import { useNavigate } from 'react-router-dom';

const Header: React.FC = () => {
  const { theme, toggleTheme } = useThemeStore();
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const [showUserMenu, setShowUserMenu] = React.useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-40">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-primary-600 to-secondary-600 rounded-lg" />
              <span className="text-xl font-bold text-slate-900 dark:text-white">
                Quantum Trading AI
              </span>
            </div>
          </div>

          {/* Right Section */}
          <div className="flex items-center gap-4">
            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              aria-label="Toggle theme"
            >
              {theme === 'light' ? (
                <Moon className="w-5 h-5 text-slate-600 dark:text-slate-400" />
              ) : (
                <Sun className="w-5 h-5 text-slate-600 dark:text-slate-400" />
              )}
            </button>

            {/* Notifications */}
            <button
              className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors relative"
              aria-label="Notifications"
            >
              <Bell className="w-5 h-5 text-slate-600 dark:text-slate-400" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
            </button>

            {/* User Menu */}
            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center gap-2 p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              >
                <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center text-white font-medium">
                  {user?.name?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || 'U'}
                </div>
                <div className="hidden md:block text-left">
                  <p className="text-sm font-medium text-slate-900 dark:text-white">
                    {user?.name || 'User'}
                  </p>
                  <p className="text-xs text-slate-500 dark:text-slate-400 capitalize">
                    {user?.plan || 'Free'}
                  </p>
                </div>
              </button>

              {/* Dropdown Menu */}
              {showUserMenu && (
                <>
                  <div
                    className="fixed inset-0 z-10"
                    onClick={() => setShowUserMenu(false)}
                  />
                  <div className="absolute right-0 mt-2 w-56 bg-white dark:bg-slate-900 rounded-lg shadow-lg border border-slate-200 dark:border-slate-800 z-20">
                    <div className="p-4 border-b border-slate-200 dark:border-slate-800">
                      <p className="text-sm font-medium text-slate-900 dark:text-white">
                        {user?.email}
                      </p>
                      <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                        {user?.plan} Plan
                      </p>
                    </div>
                    <div className="p-2">
                      <button
                        onClick={() => {
                          navigate('/profile');
                          setShowUserMenu(false);
                        }}
                        className="flex items-center gap-2 w-full px-3 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
                      >
                        <User className="w-4 h-4" />
                        Profile
                      </button>
                      <button
                        onClick={() => {
                          navigate('/settings');
                          setShowUserMenu(false);
                        }}
                        className="flex items-center gap-2 w-full px-3 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
                      >
                        <Settings className="w-4 h-4" />
                        Settings
                      </button>
                      <div className="border-t border-slate-200 dark:border-slate-800 my-2" />
                      <button
                        onClick={handleLogout}
                        className="flex items-center gap-2 w-full px-3 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                      >
                        <LogOut className="w-4 h-4" />
                        Logout
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
