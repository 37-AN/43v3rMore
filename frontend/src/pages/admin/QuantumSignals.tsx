import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/Card';
import StatCard from '@/components/dashboard/StatCard';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/Tabs';
import { Alert } from '@/components/ui/Alert';
import { Badge } from '@/components/ui/Badge';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer } from 'recharts';
import { Zap, TrendingUp, Activity, AlertCircle } from 'lucide-react';
import { apiClient } from '@/lib/api';
import { formatPercent, formatRelativeTime } from '@/lib/utils';

export const QuantumSignals: React.FC = () => {
  const [performance, setPerformance] = useState<any>(null);
  const [signals, setSignals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [perfData, signalsData] = await Promise.all([
        apiClient.getSignalPerformance('7d'),
        apiClient.getSignals({ limit: 20 }),
      ]);
      setPerformance(perfData);
      setSignals(signalsData.signals || []);
    } catch (err) {
      console.error('Failed to fetch quantum signals data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading...</div>;
  }

  const mockAccuracyData = [
    { time: '00:00', accuracy: 0.94 },
    { time: '04:00', accuracy: 0.96 },
    { time: '08:00', accuracy: 0.95 },
    { time: '12:00', accuracy: 0.97 },
    { time: '16:00', accuracy: 0.96 },
    { time: '20:00', accuracy: 0.98 },
  ];

  const mockSignalsByPair = [
    { pair: 'EURUSD', count: 45 },
    { pair: 'GBPUSD', count: 38 },
    { pair: 'USDJPY', count: 32 },
    { pair: 'XAUUSD', count: 28 },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Quantum Signal Monitoring</h1>
        <p className="mt-2 text-slate-600 dark:text-slate-400">
          Real-time quantum signal generation and performance analytics
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Signals Today"
          value={performance?.signals_today || 0}
          icon={Zap}
          color="purple"
          trend={{ value: 12, label: 'vs yesterday' }}
        />
        <StatCard
          title="Current Accuracy"
          value={formatPercent(performance?.current_accuracy || 0.96)}
          icon={TrendingUp}
          color="green"
          trend={{ value: 2.1, label: 'vs last week' }}
        />
        <StatCard
          title="Active Circuits"
          value={performance?.active_circuits || 3}
          icon={Activity}
          color="blue"
        />
        <StatCard
          title="Avg Confidence"
          value={formatPercent(performance?.avg_confidence || 0.89)}
          icon={AlertCircle}
          color="yellow"
        />
      </div>

      <Tabs defaultValue="live" className="w-full">
        <TabsList>
          <TabsTrigger value="live">Live Signals</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="circuits">Quantum Circuits</TabsTrigger>
        </TabsList>

        <TabsContent value="live" className="space-y-4">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Recent Signals</h3>
            <div className="space-y-3">
              {signals.map((signal) => (
                <div
                  key={signal.id}
                  className="flex items-center justify-between p-4 rounded-lg border border-slate-200 dark:border-slate-700"
                >
                  <div className="flex items-center gap-4">
                    <Badge variant={signal.action === 'BUY' ? 'success' : 'destructive'}>
                      {signal.action}
                    </Badge>
                    <div>
                      <p className="font-medium">{signal.symbol}</p>
                      <p className="text-sm text-slate-600 dark:text-slate-400">
                        Entry: {signal.entry_price} | SL: {signal.stop_loss} | TP: {signal.take_profit}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">{formatPercent(signal.confidence)}</p>
                    <p className="text-sm text-slate-600 dark:text-slate-400">
                      {formatRelativeTime(signal.created_at)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="performance" className="space-y-4">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Signal Accuracy Trend (Last 24h)</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={mockAccuracyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis domain={[0.9, 1]} />
                <RechartsTooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="accuracy"
                  stroke="#10b981"
                  strokeWidth={2}
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>

          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Signals by Trading Pair</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={mockSignalsByPair}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="pair" />
                <YAxis />
                <RechartsTooltip />
                <Bar dataKey="count" fill="#8b5cf6" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </TabsContent>

        <TabsContent value="circuits" className="space-y-4">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Quantum Circuit Status</h3>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-800">
                  <p className="text-sm text-slate-600 dark:text-slate-400">Qubits</p>
                  <p className="text-2xl font-bold">5</p>
                </div>
                <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-800">
                  <p className="text-sm text-slate-600 dark:text-slate-400">Backend</p>
                  <p className="text-2xl font-bold">IBM Brisbane</p>
                </div>
                <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-800">
                  <p className="text-sm text-slate-600 dark:text-slate-400">Avg Execution Time</p>
                  <p className="text-2xl font-bold">3.2s</p>
                </div>
                <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-800">
                  <p className="text-sm text-slate-600 dark:text-slate-400">Success Rate</p>
                  <p className="text-2xl font-bold">99.8%</p>
                </div>
              </div>

              <Alert variant="info" title="Quantum Backend Status">
                IBM Quantum backend is operational. Queue position: 2. Estimated wait time: 45 seconds.
              </Alert>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default QuantumSignals;
