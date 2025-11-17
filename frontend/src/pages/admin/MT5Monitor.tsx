import React, { useState, useEffect } from 'react';
import Card from '@/components/ui/Card';
import StatCard from '@/components/dashboard/StatCard';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import Alert from '@/components/ui/Alert';
import { Activity, DollarSign, TrendingUp, RefreshCw } from 'lucide-react';
import { apiClient } from '@/lib/api';
import { formatCurrency } from '@/lib/utils';

export const MT5Monitor: React.FC = () => {
  const [mt5Status, setMt5Status] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'open' | 'closed'>('open');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const statusData = await apiClient.getMT5Status();
      setMt5Status(statusData);
    } catch (err) {
      console.error('Failed to fetch MT5 data:', err);
    }
  };

  const handleCloseTrade = async (tradeId: string) => {
    try {
      await apiClient.closeTrade(tradeId);
      fetchData(); // Refresh data
    } catch (err) {
      console.error('Failed to close trade:', err);
    }
  };

  // Mock data for demonstration
  const mockOpenTrades = [
    {
      id: '1',
      symbol: 'EURUSD',
      type: 'BUY',
      volume: 0.1,
      openPrice: 1.0850,
      currentPrice: 1.0875,
      sl: 1.0800,
      tp: 1.0950,
      profit: 25.0,
      duration: '2h 15m',
    },
    {
      id: '2',
      symbol: 'GBPUSD',
      type: 'SELL',
      volume: 0.05,
      openPrice: 1.2650,
      currentPrice: 1.2645,
      sl: 1.2700,
      tp: 1.2600,
      profit: 2.5,
      duration: '45m',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">MT5 Trading Monitor</h1>
          <p className="mt-2 text-slate-600 dark:text-slate-400">
            MetaTrader 5 connection and trading activity
          </p>
        </div>
        <Button onClick={fetchData} variant="secondary">
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Connection Status */}
      <Alert
        variant={mt5Status?.connected ? 'success' : 'error'}
        title={mt5Status?.connected ? 'MT5 Connected' : 'MT5 Disconnected'}
        description={
          mt5Status?.connected
            ? `Account: ${mt5Status?.account} | Broker: ${mt5Status?.broker} | Last heartbeat: ${new Date(mt5Status?.last_heartbeat).toLocaleString()}`
            : 'MT5 connection is currently unavailable. Please check your configuration.'
        }
      />

      {/* Account Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Account Balance"
          value={formatCurrency(mt5Status?.balance || 10000, 'ZAR')}
          icon={DollarSign}
          color="green"
        />
        <StatCard
          title="Equity"
          value={formatCurrency(mt5Status?.equity || 10025, 'ZAR')}
          icon={TrendingUp}
          color="blue"
        />
        <StatCard
          title="Open Positions"
          value={mockOpenTrades.length}
          icon={Activity}
          color="purple"
        />
        <StatCard
          title="Floating P/L"
          value={formatCurrency(27.5, 'ZAR')}
          icon={TrendingUp}
          color="green"
          trend={{ value: 0.28, label: 'of balance' }}
        />
      </div>

      {/* Trades Table */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold">
            {activeTab === 'open' ? 'Active Trades' : 'Trade History'}
          </h2>
          <div className="flex gap-2">
            <Button
              variant={activeTab === 'open' ? 'primary' : 'secondary'}
              onClick={() => setActiveTab('open')}
            >
              Open
            </Button>
            <Button
              variant={activeTab === 'closed' ? 'primary' : 'secondary'}
              onClick={() => setActiveTab('closed')}
            >
              Closed
            </Button>
          </div>
        </div>

        {activeTab === 'open' && (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-200 dark:border-slate-700">
                  <th className="text-left p-3">Symbol</th>
                  <th className="text-left p-3">Type</th>
                  <th className="text-right p-3">Volume</th>
                  <th className="text-right p-3">Open Price</th>
                  <th className="text-right p-3">Current</th>
                  <th className="text-right p-3">SL</th>
                  <th className="text-right p-3">TP</th>
                  <th className="text-right p-3">P/L</th>
                  <th className="text-right p-3">Duration</th>
                  <th className="text-right p-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {mockOpenTrades.map((trade) => (
                  <tr key={trade.id} className="border-b border-slate-100 dark:border-slate-800">
                    <td className="p-3 font-medium">{trade.symbol}</td>
                    <td className="p-3">
                      <Badge variant={trade.type === 'BUY' ? 'success' : 'error'}>
                        {trade.type}
                      </Badge>
                    </td>
                    <td className="p-3 text-right">{trade.volume}</td>
                    <td className="p-3 text-right">{trade.openPrice}</td>
                    <td className="p-3 text-right">{trade.currentPrice}</td>
                    <td className="p-3 text-right">{trade.sl}</td>
                    <td className="p-3 text-right">{trade.tp}</td>
                    <td className={`p-3 text-right font-medium ${trade.profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {formatCurrency(trade.profit, 'ZAR')}
                    </td>
                    <td className="p-3 text-right text-sm text-slate-600 dark:text-slate-400">
                      {trade.duration}
                    </td>
                    <td className="p-3 text-right">
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => handleCloseTrade(trade.id)}
                      >
                        Close
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'closed' && (
          <div className="text-center py-12 text-slate-600 dark:text-slate-400">
            No closed trades in the selected period
          </div>
        )}
      </Card>

      {/* Trading Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-6">
          <h3 className="text-sm font-medium text-slate-600 dark:text-slate-400 mb-2">
            Total Trades Today
          </h3>
          <p className="text-3xl font-bold">12</p>
          <div className="mt-2 flex items-center gap-2 text-sm text-green-600">
            <TrendingUp className="h-4 w-4" />
            <span>8 winners</span>
          </div>
        </Card>
        <Card className="p-6">
          <h3 className="text-sm font-medium text-slate-600 dark:text-slate-400 mb-2">
            Win Rate
          </h3>
          <p className="text-3xl font-bold">66.7%</p>
          <div className="mt-2 text-sm text-slate-600 dark:text-slate-400">
            Above 60% target
          </div>
        </Card>
        <Card className="p-6">
          <h3 className="text-sm font-medium text-slate-600 dark:text-slate-400 mb-2">
            Net P/L Today
          </h3>
          <p className="text-3xl font-bold text-green-600">{formatCurrency(145.50, 'ZAR')}</p>
          <div className="mt-2 text-sm text-slate-600 dark:text-slate-400">
            1.45% gain
          </div>
        </Card>
      </div>
    </div>
  );
};

export default MT5Monitor;
