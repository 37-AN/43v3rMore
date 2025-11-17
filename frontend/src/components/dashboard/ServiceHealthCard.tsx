import React from 'react';
import Card from '@/components/ui/Card';
import { cn } from '@/lib/utils';
import { Circle, RefreshCw } from 'lucide-react';
import Button from '@/components/ui/Button';

export interface ServiceHealth {
  name: string;
  status: 'healthy' | 'degraded' | 'down';
  lastCheck?: string;
  responseTime?: number;
}

export interface ServiceHealthCardProps {
  service: ServiceHealth;
  onRefresh?: () => void;
}

const statusConfig = {
  healthy: {
    color: 'text-green-600 dark:text-green-400',
    bg: 'bg-green-100 dark:bg-green-900/20',
    label: 'Healthy',
  },
  degraded: {
    color: 'text-yellow-600 dark:text-yellow-400',
    bg: 'bg-yellow-100 dark:bg-yellow-900/20',
    label: 'Degraded',
  },
  down: {
    color: 'text-red-600 dark:text-red-400',
    bg: 'bg-red-100 dark:bg-red-900/20',
    label: 'Down',
  },
};

export const ServiceHealthCard: React.FC<ServiceHealthCardProps> = ({ service, onRefresh }) => {
  const config = statusConfig[service.status];

  return (
    <Card className="p-4 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={cn('rounded-full p-2', config.bg)}>
            <Circle className={cn('h-4 w-4 fill-current', config.color)} />
          </div>
          <div>
            <h3 className="font-medium text-slate-900 dark:text-white">{service.name}</h3>
            <p className={cn('text-sm font-medium', config.color)}>{config.label}</p>
          </div>
        </div>
        {onRefresh && (
          <Button variant="ghost" size="sm" onClick={onRefresh}>
            <RefreshCw className="h-4 w-4" />
          </Button>
        )}
      </div>
      {service.responseTime && (
        <div className="mt-3 text-xs text-slate-600 dark:text-slate-400">
          Response time: {service.responseTime}ms
        </div>
      )}
      {service.lastCheck && (
        <div className="mt-1 text-xs text-slate-600 dark:text-slate-400">
          Last checked: {service.lastCheck}
        </div>
      )}
    </Card>
  );
};

export default ServiceHealthCard;
