import { Card, CardContent } from '@/components/ui/card';
import { ArrowUpIcon, ArrowDownIcon } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  icon: LucideIcon;
  label: string;
  value: string | number;
  comparison?: {
    value: string;
    trend: 'up' | 'down' | 'neutral';
  };
  iconColor?: string;
  className?: string;
}

export function MetricCard({
  icon: Icon,
  label,
  value,
  comparison,
  iconColor = 'text-accent-blue',
  className,
}: MetricCardProps) {
  return (
    <Card className={cn('border-border-default bg-bg-secondary', className)}>
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="text-sm text-text-secondary mb-2">{label}</p>
            <p className="text-3xl font-bold text-text-primary">{value}</p>
            {comparison && (
              <div className="mt-2 flex items-center gap-1">
                {comparison.trend === 'up' && (
                  <ArrowUpIcon className="h-3 w-3 text-accent-green" />
                )}
                {comparison.trend === 'down' && (
                  <ArrowDownIcon className="h-3 w-3 text-accent-red" />
                )}
                <span
                  className={cn(
                    'text-xs font-medium',
                    comparison.trend === 'up' && 'text-accent-green',
                    comparison.trend === 'down' && 'text-accent-red',
                    comparison.trend === 'neutral' && 'text-text-secondary'
                  )}
                >
                  {comparison.value}
                </span>
              </div>
            )}
          </div>
          <div
            className={cn(
              'rounded-lg p-2.5 bg-bg-tertiary',
              iconColor
            )}
          >
            <Icon className="h-5 w-5" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
