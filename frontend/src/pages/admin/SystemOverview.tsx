import React, { useState, useEffect } from 'react';
import StatCard from '@/components/dashboard/StatCard';
import ServiceHealthCard, { type ServiceHealth } from '@/components/dashboard/ServiceHealthCard';
import Card from '@/components/ui/Card';
import Alert from '@/components/ui/Alert';
import { Activity, Users, TrendingUp, DollarSign, Zap, Clock } from 'lucide-react';
import { apiClient } from '@/lib/api';
import { wsClient } from '@/lib/websocket';
import { formatCurrency, formatPercentage } from '@/lib/utils';

interface OverviewData {
  active_users: number;
  signals_today: number;
  current_accuracy: number;
  mrr: number;
  uptime: number;
  services_health: ServiceHealth[];
  recent_events: Array<{
    id: string;
    type: string;
    message: string;
    timestamp: string;
  }>;
}

export const SystemOverview: React.FC = () => {
  const [data, setData] = useState<OverviewData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchOverviewData();

    // Set up WebSocket listeners for real-time updates
    wsClient.on('metric_update', handleMetricUpdate);
    wsClient.on('signal_generated', handleSignalGenerated);
    wsClient.on('user_registered', handleUserRegistered);

    return () => {
      wsClient.off('metric_update', handleMetricUpdate);
      wsClient.off('signal_generated', handleSignalGenerated);
      wsClient.off('user_registered', handleUserRegistered);
    };
  }, []);

  const fetchOverviewData = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getDashboardOverview();
      setData(response);
      setError(null);
    } catch (err) {
      setError('Failed to load overview data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleMetricUpdate = (update: any) => {
    setData((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        [update.metric_name]: update.value,
      };
    });
  };

  const handleSignalGenerated = () => {
    setData((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        signals_today: prev.signals_today + 1,
      };
    });
  };

  const handleUserRegistered = () => {
    setData((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        active_users: prev.active_users + 1,
      };
    });
  };

  const handleRefreshService = (serviceName: string) => {
    console.log('Refreshing service:', serviceName);
    fetchOverviewData();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-600 dark:text-slate-400">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="error" title="Error" description={error} className="mb-6" />
    );
  }

  if (!data) {
    return null;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white">System Overview</h1>
        <p className="mt-2 text-slate-600 dark:text-slate-400">
          Real-time monitoring of all system components
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <StatCard
          title="Active Users"
          value={data.active_users}
          icon={Users}
          color="blue"
          trend={{ value: 12, label: 'vs last month' }}
        />
        <StatCard
          title="Signals Today"
          value={data.signals_today}
          icon={Zap}
          color="purple"
          trend={{ value: 8, label: 'vs yesterday' }}
        />
        <StatCard
          title="Signal Accuracy"
          value={formatPercentage(data.current_accuracy)}
          icon={TrendingUp}
          color="green"
          trend={{ value: 2.5, label: 'vs last week' }}
        />
        <StatCard
          title="Monthly Revenue"
          value={formatCurrency(data.mrr, 'ZAR')}
          icon={DollarSign}
          color="green"
        />
        <StatCard
          title="System Uptime"
          value={`${Math.floor(data.uptime / 3600)}h ${Math.floor((data.uptime % 3600) / 60)}m`}
          icon={Clock}
          color="blue"
        />
        <StatCard
          title="Active Trades"
          value={15}
          icon={Activity}
          color="yellow"
        />
      </div>

      {/* Service Health Grid */}
      <div>
        <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-4">Service Health</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {data.services_health?.map((service) => (
            <ServiceHealthCard
              key={service.name}
              service={service}
              onRefresh={() => handleRefreshService(service.name)}
            />
          ))}
        </div>
      </div>

      {/* Real-Time Activity Feed */}
      <Card className="p-6">
        <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-4">Real-Time Activity</h2>
        <div className="space-y-3">
          {data.recent_events?.map((event) => (
            <div
              key={event.id}
              className="flex items-start gap-3 p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50"
            >
              <div className="flex-shrink-0">
                <Activity className="h-5 w-5 text-primary-600" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-slate-900 dark:text-white">
                  {event.message}
                </p>
                <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                  {new Date(event.timestamp).toLocaleString()}
                </p>
              </div>
            </div>
          ))}
          {(!data.recent_events || data.recent_events.length === 0) && (
            <div className="text-center py-8 text-slate-600 dark:text-slate-400">
              No recent activity
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};

export default SystemOverview;
