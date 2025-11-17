import React, { useState, useEffect } from 'react';
import Card from '@/components/ui/Card';
import StatCard from '@/components/dashboard/StatCard';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/Tabs';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer } from 'recharts';
import { AlertCircle, CheckCircle, XCircle, Activity, Cpu, HardDrive, Network } from 'lucide-react';
import { apiClient } from '@/lib/api';

export const AlertsPerformance: React.FC = () => {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [metrics, setMetrics] = useState<any>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [alertsData, metricsData] = await Promise.all([
        apiClient.getAlerts({ status: 'active' }),
        apiClient.getPerformanceMetrics({ timeframe: '1h' }),
      ]);
      setAlerts(alertsData.alerts || mockAlerts);
      setMetrics(metricsData || mockMetrics);
    } catch (err) {
      console.error('Failed to fetch alerts/performance data:', err);
      setAlerts(mockAlerts);
      setMetrics(mockMetrics);
    }
  };

  const handleAcknowledge = async (alertId: string) => {
    try {
      await apiClient.acknowledgeAlert(alertId);
      fetchData();
    } catch (err) {
      console.error('Failed to acknowledge alert:', err);
    }
  };

  const handleResolve = async (alertId: string) => {
    try {
      await apiClient.resolveAlert(alertId);
      fetchData();
    } catch (err) {
      console.error('Failed to resolve alert:', err);
    }
  };

  // Mock data
  const mockAlerts = [
    {
      id: '1',
      severity: 'high',
      type: 'Signal Accuracy Drop',
      message: 'Signal accuracy has fallen below 95% threshold',
      timestamp: '2025-11-17T08:30:00Z',
      status: 'active',
    },
    {
      id: '2',
      severity: 'medium',
      type: 'High API Latency',
      message: 'Average API response time exceeds 2 seconds',
      timestamp: '2025-11-17T07:15:00Z',
      status: 'acknowledged',
    },
  ];

  const mockMetrics = {
    cpu_usage: 45,
    memory_usage: 68,
    disk_usage: 42,
    api_requests_per_sec: 125,
  };

  const cpuData = [
    { time: '10:00', usage: 35 },
    { time: '10:15', usage: 42 },
    { time: '10:30', usage: 45 },
    { time: '10:45', usage: 48 },
    { time: '11:00', usage: 45 },
  ];

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <Badge variant="error">Critical</Badge>;
      case 'high':
        return <Badge variant="error">High</Badge>;
      case 'medium':
        return <Badge variant="warning">Medium</Badge>;
      case 'low':
        return <Badge variant="default">Low</Badge>;
      default:
        return <Badge variant="default">{severity}</Badge>;
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
      case 'high':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'medium':
        return <AlertCircle className="h-5 w-5 text-yellow-500" />;
      default:
        return <CheckCircle className="h-5 w-5 text-blue-500" />;
    }
  };

  const activeAlerts = alerts.filter((a) => a.status === 'active').length;
  const criticalAlerts = alerts.filter((a) => a.severity === 'critical').length;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
          Alerts & Performance Monitoring
        </h1>
        <p className="mt-2 text-slate-600 dark:text-slate-400">
          System alerts and performance metrics
        </p>
      </div>

      <Tabs defaultValue="alerts" className="w-full">
        <TabsList>
          <TabsTrigger value="alerts">Active Alerts</TabsTrigger>
          <TabsTrigger value="performance">System Performance</TabsTrigger>
          <TabsTrigger value="api">API Metrics</TabsTrigger>
        </TabsList>

        <TabsContent value="alerts" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <StatCard
              title="Active Alerts"
              value={activeAlerts}
              icon={AlertCircle}
              color="yellow"
            />
            <StatCard
              title="Critical Alerts"
              value={criticalAlerts}
              icon={XCircle}
              color="red"
            />
            <StatCard
              title="Resolved Today"
              value={8}
              icon={CheckCircle}
              color="green"
            />
          </div>

          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Active Alerts</h3>
            <div className="space-y-3">
              {alerts.map((alert) => (
                <div
                  key={alert.id}
                  className="flex items-start gap-3 p-4 rounded-lg border border-slate-200 dark:border-slate-700"
                >
                  {getSeverityIcon(alert.severity)}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      {getSeverityBadge(alert.severity)}
                      <h4 className="font-medium">{alert.type}</h4>
                    </div>
                    <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">
                      {alert.message}
                    </p>
                    <p className="text-xs text-slate-500 dark:text-slate-500">
                      {new Date(alert.timestamp).toLocaleString()}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    {alert.status === 'active' && (
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => handleAcknowledge(alert.id)}
                      >
                        Acknowledge
                      </Button>
                    )}
                    <Button size="sm" variant="primary" onClick={() => handleResolve(alert.id)}>
                      Resolve
                    </Button>
                  </div>
                </div>
              ))}
              {alerts.length === 0 && (
                <div className="text-center py-12 text-slate-600 dark:text-slate-400">
                  <CheckCircle className="h-12 w-12 mx-auto mb-3 text-green-500" />
                  <p className="font-medium">All systems operational</p>
                  <p className="text-sm">No active alerts</p>
                </div>
              )}
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="performance" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <StatCard title="CPU Usage" value={`${metrics?.cpu_usage || 0}%`} icon={Cpu} color="blue" />
            <StatCard
              title="Memory Usage"
              value={`${metrics?.memory_usage || 0}%`}
              icon={Activity}
              color="purple"
            />
            <StatCard
              title="Disk Usage"
              value={`${metrics?.disk_usage || 0}%`}
              icon={HardDrive}
              color="green"
            />
            <StatCard
              title="API Requests/sec"
              value={metrics?.api_requests_per_sec || 0}
              icon={Network}
              color="yellow"
            />
          </div>

          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">CPU Usage (Last Hour)</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={cpuData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis domain={[0, 100]} />
                <RechartsTooltip />
                <Legend />
                <Line type="monotone" dataKey="usage" stroke="#3b82f6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">System Health</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm">CPU Temperature</span>
                  <span className="font-medium">65°C</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Network I/O</span>
                  <span className="font-medium">125 MB/s</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Active Connections</span>
                  <span className="font-medium">1,245</span>
                </div>
              </div>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Database Performance</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Active Queries</span>
                  <span className="font-medium">12</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Slow Queries ({'>'}1s)</span>
                  <span className="font-medium text-yellow-600">3</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Cache Hit Rate</span>
                  <span className="font-medium text-green-600">97.8%</span>
                </div>
              </div>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="api" className="space-y-4">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">API Endpoint Performance</h3>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-200 dark:border-slate-700">
                    <th className="text-left p-3">Endpoint</th>
                    <th className="text-right p-3">Requests (24h)</th>
                    <th className="text-right p-3">Avg Response</th>
                    <th className="text-right p-3">Error Rate</th>
                    <th className="text-left p-3">Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-slate-100 dark:border-slate-800">
                    <td className="p-3 font-mono text-sm">/api/v1/signals</td>
                    <td className="p-3 text-right">8,542</td>
                    <td className="p-3 text-right">245ms</td>
                    <td className="p-3 text-right">0.12%</td>
                    <td className="p-3">
                      <Badge variant="success">Healthy</Badge>
                    </td>
                  </tr>
                  <tr className="border-b border-slate-100 dark:border-slate-800">
                    <td className="p-3 font-mono text-sm">/api/v1/analyze</td>
                    <td className="p-3 text-right">1,234</td>
                    <td className="p-3 text-right">1,850ms</td>
                    <td className="p-3 text-right">0.05%</td>
                    <td className="p-3">
                      <Badge variant="success">Healthy</Badge>
                    </td>
                  </tr>
                  <tr className="border-b border-slate-100 dark:border-slate-800">
                    <td className="p-3 font-mono text-sm">/api/v1/users</td>
                    <td className="p-3 text-right">3,456</td>
                    <td className="p-3 text-right">180ms</td>
                    <td className="p-3 text-right">0.08%</td>
                    <td className="p-3">
                      <Badge variant="success">Healthy</Badge>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AlertsPerformance;
