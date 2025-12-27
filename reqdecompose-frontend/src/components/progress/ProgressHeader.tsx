import { StatusBadge } from '@/components/shared/StatusBadge';
import { Button } from '@/components/ui/button';
import { Clock, Coins, Ban } from 'lucide-react';
import { formatDuration } from '@/lib/utils';
import type { WorkflowStatus } from '@/types/workflow';

interface ProgressHeaderProps {
  workflowId: string;
  runNumber?: number;
  projectName?: string;
  initiator?: string;
  status: WorkflowStatus;
  dateCreated: string;
  elapsedTime?: number; // seconds
  totalTokens?: number;
  onCancel?: () => void;
}

export function ProgressHeader({
  workflowId,
  runNumber = 1,
  projectName = 'Untitled Project',
  initiator = 'Admin',
  status,
  dateCreated,
  elapsedTime = 0,
  totalTokens = 0,
  onCancel,
}: ProgressHeaderProps) {
  return (
    <div className="space-y-4">
      {/* Title & Status */}
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-text-primary">
              Decomposition Run #{runNumber}
            </h1>
            <StatusBadge status={status} />
          </div>
          <div className="flex items-center gap-4 text-sm text-text-secondary">
            <span>{projectName}</span>
            <span>•</span>
            <span>Initiated by {initiator}</span>
            <span>•</span>
            <span>{new Date(dateCreated).toLocaleString()}</span>
          </div>
        </div>

        {/* Actions */}
        {status === 'processing' && onCancel && (
          <Button variant="destructive" size="sm" onClick={onCancel}>
            <Ban className="mr-2 h-4 w-4" />
            Cancel Run
          </Button>
        )}
      </div>

      {/* Metrics */}
      <div className="flex items-center gap-6 p-4 bg-bg-secondary border border-border-default rounded-lg">
        <div className="flex items-center gap-2">
          <Clock className="h-4 w-4 text-text-tertiary" />
          <div>
            <p className="text-xs text-text-tertiary">Elapsed Time</p>
            <p className="text-sm font-semibold text-text-primary">
              {elapsedTime > 0 ? formatDuration(elapsedTime) : '0s'}
            </p>
          </div>
        </div>

        <div className="w-px h-8 bg-border-default" />

        <div className="flex items-center gap-2">
          <Coins className="h-4 w-4 text-text-tertiary" />
          <div>
            <p className="text-xs text-text-tertiary">Tokens</p>
            <p className="text-sm font-semibold text-text-primary">
              {totalTokens.toLocaleString()}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
