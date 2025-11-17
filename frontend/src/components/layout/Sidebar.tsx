import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  TrendingUp,
  CreditCard,
  Settings,
  BarChart3,
  Zap,
} from 'lucide-react';

const navigation = [
  {
    name: 'Dashboard',
    path: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    name: 'Signals',
    path: '/signals',
    icon: TrendingUp,
  },
  {
    name: 'Analysis',
    path: '/analysis',
    icon: BarChart3,
  },
  {
    name: 'Subscription',
    path: '/subscription',
    icon: CreditCard,
  },
  {
    name: 'Performance',
    path: '/performance',
    icon: Zap,
  },
  {
    name: 'Settings',
    path: '/settings',
    icon: Settings,
  },
];

const Sidebar: React.FC = () => {
  return (
    <aside className="hidden md:flex md:flex-shrink-0">
      <div className="flex flex-col w-64 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800">
        <nav className="flex-1 px-4 py-6 space-y-1">
          {navigation.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 text-sm font-medium rounded-lg transition-all ${
                  isActive
                    ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400'
                    : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <item.icon
                    className={`w-5 h-5 ${
                      isActive ? 'text-primary-600 dark:text-primary-400' : ''
                    }`}
                  />
                  {item.name}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Upgrade Card */}
        <div className="p-4 m-4 bg-gradient-to-br from-primary-600 to-secondary-600 rounded-lg text-white">
          <h3 className="font-semibold mb-1">Upgrade to Pro</h3>
          <p className="text-xs text-white/80 mb-3">
            Get unlimited signals and advanced features
          </p>
          <button className="w-full px-3 py-2 bg-white text-primary-600 rounded-lg text-sm font-medium hover:bg-white/90 transition-colors">
            Upgrade Now
          </button>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
