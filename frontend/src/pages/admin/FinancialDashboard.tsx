import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/Card';
import StatCard from '@/components/dashboard/StatCard';
import { Progress } from '@/components/ui/Progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/Tabs';
import { Badge } from '@/components/ui/Badge';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer } from 'recharts';
import { DollarSign, TrendingUp, CreditCard, Target } from 'lucide-react';
import { apiClient } from '@/lib/api';
import { formatCurrency, formatRelativeTime } from '@/lib/utils';

export const FinancialDashboard: React.FC = () => {
  const [revenueData, setRevenueData] = useState<any>(null);
  const [payments, setPayments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [revenue, paymentsData] = await Promise.all([
        apiClient.getRevenue('month'),
        apiClient.getPayments({ limit: 20 }),
      ]);
      setRevenueData(revenue);
      setPayments(paymentsData.payments || mockPayments);
    } catch (err) {
      console.error('Failed to fetch financial data:', err);
      setPayments(mockPayments);
    } finally {
      setLoading(false);
    }
  };

  // Mock data
  const mrr = 45000;
  const arr = mrr * 12;
  const revenueThisMonth = 42500;
  const revenueTarget = 100000;
  const targetProgress = (revenueThisMonth / revenueTarget) * 100;

  const mockPayments = [
    {
      id: '1',
      user: 'John Trader',
      amount: 1000,
      plan: 'Pro',
      method: 'PayFast',
      status: 'success',
      date: '2025-11-17T08:30:00Z',
    },
    {
      id: '2',
      user: 'Sarah Investor',
      amount: 2000,
      plan: 'Premium',
      method: 'PayFast',
      status: 'success',
      date: '2025-11-16T14:20:00Z',
    },
    {
      id: '3',
      user: 'Mike Charts',
      amount: 500,
      plan: 'Basic',
      method: 'EFT',
      status: 'pending',
      date: '2025-11-15T10:15:00Z',
    },
  ];

  const revenueByPlanData = [
    { name: 'Basic', value: 5000, color: '#94a3b8' },
    { name: 'Pro', value: 18000, color: '#3b82f6' },
    { name: 'Premium', value: 22000, color: '#8b5cf6' },
  ];

  const revenueTrendData = [
    { month: 'Jun', revenue: 12000 },
    { month: 'Jul', revenue: 18000 },
    { month: 'Aug', revenue: 25000 },
    { month: 'Sep', revenue: 32000 },
    { month: 'Oct', revenue: 38000 },
    { month: 'Nov', revenue: 45000 },
  ];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'success':
        return <Badge variant="success">Success</Badge>;
      case 'pending':
        return <Badge variant="warning">Pending</Badge>;
      case 'failed':
        return <Badge variant="destructive">Failed</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Financial Dashboard</h1>
        <p className="mt-2 text-slate-600 dark:text-slate-400">
          Revenue metrics and financial analytics
        </p>
      </div>

      {/* Revenue Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Monthly Recurring Revenue"
          value={formatCurrency(mrr, 'ZAR')}
          icon={DollarSign}
          color="green"
          trend={{ value: 18.4, label: 'vs last month' }}
        />
        <StatCard
          title="Annual Recurring Revenue"
          value={formatCurrency(arr, 'ZAR')}
          icon={TrendingUp}
          color="blue"
        />
        <StatCard
          title="Revenue This Month"
          value={formatCurrency(revenueThisMonth, 'ZAR')}
          icon={CreditCard}
          color="purple"
        />
        <StatCard
          title="Revenue Target Progress"
          value={`${targetProgress.toFixed(1)}%`}
          icon={Target}
          color="yellow"
        />
      </div>

      {/* Target Progress Bar */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-medium">Monthly Revenue Target: {formatCurrency(revenueTarget, 'ZAR')}</h3>
          <span className="text-sm text-slate-600 dark:text-slate-400">
            {formatCurrency(revenueThisMonth, 'ZAR')} / {formatCurrency(revenueTarget, 'ZAR')}
          </span>
        </div>
        <Progress value={targetProgress} className="h-3" />
        <p className="text-sm text-slate-600 dark:text-slate-400 mt-2">
          {formatCurrency(revenueTarget - revenueThisMonth, 'ZAR')} remaining to reach target
        </p>
      </Card>

      <Tabs defaultValue="overview" className="w-full">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="payments">Payments</TabsTrigger>
          <TabsTrigger value="projections">Projections</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Revenue Trend (Last 6 Months)</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={revenueTrendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <RechartsTooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="revenue"
                    stroke="#10b981"
                    strokeWidth={2}
                    dot={{ r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </Card>

            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Revenue by Plan</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={revenueByPlanData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {revenueByPlanData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <RechartsTooltip />
                </PieChart>
              </ResponsiveContainer>
            </Card>
          </div>

          {/* Unit Economics */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Unit Economics</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-800">
                <p className="text-sm text-slate-600 dark:text-slate-400">Customer Lifetime Value</p>
                <p className="text-2xl font-bold mt-2">{formatCurrency(12000, 'ZAR')}</p>
              </div>
              <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-800">
                <p className="text-sm text-slate-600 dark:text-slate-400">Customer Acquisition Cost</p>
                <p className="text-2xl font-bold mt-2">{formatCurrency(500, 'ZAR')}</p>
              </div>
              <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-800">
                <p className="text-sm text-slate-600 dark:text-slate-400">LTV:CAC Ratio</p>
                <p className="text-2xl font-bold mt-2 text-green-600">24:1</p>
              </div>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="payments">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Recent Payments</h3>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-200 dark:border-slate-700">
                    <th className="text-left p-3">User</th>
                    <th className="text-right p-3">Amount</th>
                    <th className="text-left p-3">Plan</th>
                    <th className="text-left p-3">Method</th>
                    <th className="text-left p-3">Status</th>
                    <th className="text-left p-3">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {mockPayments.map((payment) => (
                    <tr key={payment.id} className="border-b border-slate-100 dark:border-slate-800">
                      <td className="p-3 font-medium">{payment.user}</td>
                      <td className="p-3 text-right font-medium">
                        {formatCurrency(payment.amount, 'ZAR')}
                      </td>
                      <td className="p-3">{payment.plan}</td>
                      <td className="p-3">{payment.method}</td>
                      <td className="p-3">{getStatusBadge(payment.status)}</td>
                      <td className="p-3 text-sm text-slate-600 dark:text-slate-400">
                        {formatRelativeTime(payment.date)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="projections">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Revenue Projections</h3>
            <div className="space-y-6">
              <div className="p-4 rounded-lg bg-blue-50 dark:bg-blue-900/20">
                <p className="font-medium text-blue-900 dark:text-blue-200">
                  At current growth rate (18.4% MoM):
                </p>
                <p className="text-2xl font-bold text-blue-900 dark:text-blue-200 mt-2">
                  Reaching {formatCurrency(100000, 'ZAR')} MRR in ~5 months (April 2026)
                </p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 rounded-lg border border-slate-200 dark:border-slate-700">
                  <p className="text-sm text-slate-600 dark:text-slate-400">Projected MRR (3 months)</p>
                  <p className="text-2xl font-bold mt-2">{formatCurrency(75000, 'ZAR')}</p>
                </div>
                <div className="p-4 rounded-lg border border-slate-200 dark:border-slate-700">
                  <p className="text-sm text-slate-600 dark:text-slate-400">Projected MRR (6 months)</p>
                  <p className="text-2xl font-bold mt-2">{formatCurrency(120000, 'ZAR')}</p>
                </div>
                <div className="p-4 rounded-lg border border-slate-200 dark:border-slate-700">
                  <p className="text-sm text-slate-600 dark:text-slate-400">Projected ARR (6 months)</p>
                  <p className="text-2xl font-bold mt-2">{formatCurrency(1440000, 'ZAR')}</p>
                </div>
              </div>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default FinancialDashboard;
