import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ToastContainer } from '@/components/ui/Toast';
import ProtectedRoute from '@/components/ProtectedRoute';
import DashboardLayout from '@/components/layout/DashboardLayout';
import Login from '@/pages/Login';
import Signup from '@/pages/Signup';
import Dashboard from '@/pages/Dashboard';
import Signals from '@/pages/Signals';
import Subscription from '@/pages/Subscription';
import { useThemeStore } from '@/store/theme';

// Admin Dashboard Pages
import SystemOverview from '@/pages/admin/SystemOverview';
import QuantumSignals from '@/pages/admin/QuantumSignals';
import MT5Monitor from '@/pages/admin/MT5Monitor';
import UserManagement from '@/pages/admin/UserManagement';
import FinancialDashboard from '@/pages/admin/FinancialDashboard';
import Configuration from '@/pages/admin/Configuration';
import AlertsPerformance from '@/pages/admin/AlertsPerformance';

// Placeholder pages
const Analysis: React.FC = () => (
  <div className="text-center py-12">
    <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">
      Analysis
    </h1>
    <p className="text-slate-600 dark:text-slate-400">
      Run quantum analysis on your favorite symbols
    </p>
  </div>
);

const Performance: React.FC = () => (
  <div className="text-center py-12">
    <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">
      Performance
    </h1>
    <p className="text-slate-600 dark:text-slate-400">
      Track your trading performance and metrics
    </p>
  </div>
);

const Settings: React.FC = () => (
  <div className="text-center py-12">
    <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">
      Settings
    </h1>
    <p className="text-slate-600 dark:text-slate-400">
      Manage your account settings and preferences
    </p>
  </div>
);

function App() {
  const { theme } = useThemeStore();

  useEffect(() => {
    // Initialize theme on mount
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  return (
    <BrowserRouter>
      <ToastContainer />
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />

        {/* Protected routes */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="signals" element={<Signals />} />
          <Route path="analysis" element={<Analysis />} />
          <Route path="subscription" element={<Subscription />} />
          <Route path="performance" element={<Performance />} />
          <Route path="settings" element={<Settings />} />

          {/* Admin Dashboard Routes */}
          <Route path="admin">
            <Route index element={<Navigate to="/admin/overview" replace />} />
            <Route path="overview" element={<SystemOverview />} />
            <Route path="quantum-signals" element={<QuantumSignals />} />
            <Route path="mt5-monitor" element={<MT5Monitor />} />
            <Route path="users" element={<UserManagement />} />
            <Route path="financial" element={<FinancialDashboard />} />
            <Route path="configuration" element={<Configuration />} />
            <Route path="alerts" element={<AlertsPerformance />} />
          </Route>
        </Route>

        {/* Catch all */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
