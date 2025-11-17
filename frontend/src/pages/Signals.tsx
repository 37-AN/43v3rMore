import React, { useEffect, useState } from 'react';
import { TrendingUp, TrendingDown, RefreshCw, Filter } from 'lucide-react';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import Loading from '@/components/ui/Loading';
import { api } from '@/lib/api';
import type { TradingSignal } from '@/types';
import { toast } from '@/components/ui/Toast';
import { formatDistanceToNow } from 'date-fns';

const Signals: React.FC = () => {
  const [signals, setSignals] = useState<TradingSignal[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [filterSymbol, setFilterSymbol] = useState<string>('');

  useEffect(() => {
    fetchSignals();
  }, [filterSymbol]);

  const fetchSignals = async () => {
    try {
      const params = filterSymbol ? { symbol: filterSymbol, limit: 20 } : { limit: 20 };
      const data = await api.getSignals(params);
      setSignals(data.signals);
    } catch (error) {
      toast.error('Failed to fetch signals');
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  const handleRefresh = () => {
    setIsRefreshing(true);
    fetchSignals();
  };

  const symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'BTCUSD'];

  if (isLoading) {
    return <Loading text="Loading signals..." />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
            Trading Signals
          </h1>
          <p className="text-slate-600 dark:text-slate-400 mt-1">
            High-accuracy quantum-powered trading signals
          </p>
        </div>
        <Button
          variant="ghost"
          leftIcon={<RefreshCw className="w-4 h-4" />}
          onClick={handleRefresh}
          isLoading={isRefreshing}
        >
          Refresh
        </Button>
      </div>

      {/* Filters */}
      <Card padding="md">
        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-slate-600 dark:text-slate-400" />
            <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
              Filter by symbol:
            </span>
          </div>
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={() => setFilterSymbol('')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                filterSymbol === ''
                  ? 'bg-primary-600 text-white'
                  : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
              }`}
            >
              All
            </button>
            {symbols.map((symbol) => (
              <button
                key={symbol}
                onClick={() => setFilterSymbol(symbol)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  filterSymbol === symbol
                    ? 'bg-primary-600 text-white'
                    : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
                }`}
              >
                {symbol}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {/* Signals Grid */}
      {signals.length === 0 ? (
        <Card padding="lg">
          <div className="text-center py-12 text-slate-500 dark:text-slate-400">
            <TrendingUp className="w-16 h-16 mx-auto mb-4 opacity-50" />
            <p className="text-lg font-medium">No signals available</p>
            <p className="text-sm mt-2">
              Check back later for new trading opportunities
            </p>
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {signals.map((signal) => (
            <Card key={signal.id} padding="md" variant="elevated">
              <div className="space-y-4">
                {/* Header */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div
                      className={`p-3 rounded-lg ${
                        signal.action === 'BUY'
                          ? 'bg-green-50 dark:bg-green-900/20'
                          : 'bg-red-50 dark:bg-red-900/20'
                      }`}
                    >
                      {signal.action === 'BUY' ? (
                        <TrendingUp className="w-6 h-6 text-green-600" />
                      ) : (
                        <TrendingDown className="w-6 h-6 text-red-600" />
                      )}
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-slate-900 dark:text-white">
                        {signal.symbol}
                      </h3>
                      <p className="text-sm text-slate-500 dark:text-slate-400">
                        {signal.timeframe}
                      </p>
                    </div>
                  </div>
                  <Badge
                    variant={signal.action === 'BUY' ? 'success' : 'error'}
                  >
                    {signal.action}
                  </Badge>
                </div>

                {/* Details Grid */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      Entry Price
                    </p>
                    <p className="text-lg font-semibold text-slate-900 dark:text-white">
                      {signal.entry_price.toFixed(5)}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      Confidence
                    </p>
                    <p className="text-lg font-semibold text-green-600">
                      {(signal.confidence * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      Take Profit
                    </p>
                    <p className="text-sm font-medium text-slate-900 dark:text-white">
                      {signal.take_profit?.toFixed(5) || 'N/A'}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      Stop Loss
                    </p>
                    <p className="text-sm font-medium text-slate-900 dark:text-white">
                      {signal.stop_loss?.toFixed(5) || 'N/A'}
                    </p>
                  </div>
                </div>

                {/* Reason */}
                <div className="p-3 bg-slate-50 dark:bg-slate-900/50 rounded-lg">
                  <p className="text-sm text-slate-700 dark:text-slate-300">
                    <span className="font-medium">Reason:</span> {signal.reason}
                  </p>
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between pt-2 border-t border-slate-200 dark:border-slate-800">
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    {formatDistanceToNow(new Date(signal.created_at), {
                      addSuffix: true,
                    })}
                  </p>
                  {signal.risk_reward && (
                    <Badge variant="info">
                      R:R {signal.risk_reward.toFixed(2)}
                    </Badge>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default Signals;
