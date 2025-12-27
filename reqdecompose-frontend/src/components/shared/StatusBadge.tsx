import { Badge } from '@/components/ui/badge';
import { CheckCircle2, Loader2, XCircle, Clock, Ban } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { WorkflowStatus } from '@/types/workflow';

interface StatusBadgeProps {
  status: WorkflowStatus;
  className?: string;
  showIcon?: boolean;
}

const statusConfig: Record<
  WorkflowStatus,
  {
    label: string;
    icon: typeof CheckCircle2;
    className: string;
  }
> = {
  completed: {
    label: 'Completed',
    icon: CheckCircle2,
    className: 'bg-accent-green/10 text-accent-green border-accent-green/20 hover:bg-accent-green/20',
  },
  processing: {
    label: 'Processing',
    icon: Loader2,
    className: 'bg-accent-blue/10 text-accent-blue border-accent-blue/20 hover:bg-accent-blue/20',
  },
  failed: {
    label: 'Failed',
    icon: XCircle,
    className: 'bg-accent-red/10 text-accent-red border-accent-red/20 hover:bg-accent-red/20',
  },
  pending: {
    label: 'Pending',
    icon: Clock,
    className: 'bg-text-tertiary/10 text-text-secondary border-border-default hover:bg-text-tertiary/20',
  },
  cancelled: {
    label: 'Cancelled',
    icon: Ban,
    className: 'bg-text-tertiary/10 text-text-secondary border-border-default hover:bg-text-tertiary/20',
  },
};

export function StatusBadge({ status, className, showIcon = true }: StatusBadgeProps) {
  const config = statusConfig[status];
  const Icon = config.icon;

  return (
    <Badge variant="outline" className={cn(config.className, className)}>
      {showIcon && (
        <Icon
          className={cn('mr-1.5 h-3 w-3', status === 'processing' && 'animate-spin')}
        />
      )}
      {config.label}
    </Badge>
  );
}
