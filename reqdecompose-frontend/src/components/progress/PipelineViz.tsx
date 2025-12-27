import { CheckCircle2, Circle, Loader2 } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';

type NodeStatus = 'pending' | 'processing' | 'completed' | 'failed';

interface PipelineNode {
  id: string;
  label: string;
  status: NodeStatus;
}

interface PipelineVizProps {
  nodes: PipelineNode[];
  progress: number;
  className?: string;
}

export function PipelineViz({ nodes, progress, className }: PipelineVizProps) {
  return (
    <div className={cn('space-y-6', className)}>
      {/* Pipeline Stages */}
      <div className="flex items-center justify-between gap-4">
        {nodes.map((node, index) => {
          const isLast = index === nodes.length - 1;

          return (
            <div key={node.id} className="flex items-center gap-4 flex-1">
              {/* Node */}
              <div className="flex flex-col items-center gap-2 min-w-0">
                <div
                  className={cn(
                    'w-12 h-12 rounded-full flex items-center justify-center border-2 transition-all',
                    node.status === 'completed' &&
                      'bg-accent-green/10 border-accent-green text-accent-green',
                    node.status === 'processing' &&
                      'bg-accent-blue/10 border-accent-blue text-accent-blue',
                    node.status === 'failed' &&
                      'bg-accent-red/10 border-accent-red text-accent-red',
                    node.status === 'pending' &&
                      'bg-bg-tertiary border-border-default text-text-tertiary'
                  )}
                >
                  {node.status === 'completed' && <CheckCircle2 className="w-6 h-6" />}
                  {node.status === 'processing' && <Loader2 className="w-6 h-6 animate-spin" />}
                  {node.status === 'pending' && <Circle className="w-6 h-6" />}
                  {node.status === 'failed' && <CheckCircle2 className="w-6 h-6" />}
                </div>

                <div className="text-center">
                  <p
                    className={cn(
                      'text-sm font-semibold',
                      node.status === 'completed' && 'text-accent-green',
                      node.status === 'processing' && 'text-accent-blue',
                      node.status === 'failed' && 'text-accent-red',
                      node.status === 'pending' && 'text-text-tertiary'
                    )}
                  >
                    {node.label}
                  </p>
                  <p className="text-xs text-text-tertiary capitalize">{node.status}</p>
                </div>
              </div>

              {/* Connector Line */}
              {!isLast && (
                <div className="flex-1 h-0.5 bg-border-default relative">
                  <div
                    className={cn(
                      'absolute inset-y-0 left-0 bg-accent-blue transition-all',
                      node.status === 'completed' && 'w-full'
                    )}
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Overall Progress Bar */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="text-text-secondary">Overall Progress</span>
          <span className="font-semibold text-text-primary">{Math.round(progress)}%</span>
        </div>
        <Progress value={progress} className="h-2" />
      </div>
    </div>
  );
}
