'use client';

import { useEffect, useRef } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Terminal } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { WorkflowEvent } from '@/types/workflow';

interface LogStreamProps {
  events: WorkflowEvent[];
  className?: string;
}

type LogEntry = {
  timestamp: string;
  type: 'info' | 'success' | 'warning' | 'error' | 'generated';
  message: string;
  category: 'strategy' | 'data' | 'quality';
};

export function LogStream({ events, className }: LogStreamProps) {
  const logEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new events arrive
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [events]);

  // Convert workflow events to log entries
  const logs: LogEntry[] = events.map((event) => {
    const timestamp = new Date(event.timestamp).toLocaleTimeString('en-US', {
      hour12: false,
    });

    let type: LogEntry['type'] = 'info';
    let message = '';
    let category: LogEntry['category'] = 'strategy';

    switch (event.type) {
      case 'workflow_started':
        type = 'info';
        message = 'Workflow execution started';
        category = 'strategy';
        break;
      case 'node_started':
        type = 'info';
        message = `Started ${event.data.node} node`;
        category = 'strategy';
        break;
      case 'node_completed':
        type = 'success';
        message = `Completed ${event.data.node} node`;
        category = event.data.node === 'extract' ? 'data' : 'strategy';
        break;
      case 'progress_update':
        type = 'info';
        message = event.data.message || 'Processing...';
        category = 'strategy';
        break;
      case 'workflow_completed':
        type = 'success';
        message = 'Workflow completed successfully';
        category = 'quality';
        break;
      case 'workflow_failed':
        type = 'error';
        message = `Workflow failed: ${event.data.error || 'Unknown error'}`;
        category = 'quality';
        break;
      default:
        message = JSON.stringify(event.data);
    }

    return { timestamp, type, message, category };
  });

  const strategyLogs = logs.filter((log) => log.category === 'strategy');
  const dataLogs = logs.filter((log) => log.category === 'data');
  const qualityLogs = logs.filter((log) => log.category === 'quality');

  const renderLogs = (logList: LogEntry[]) => {
    if (logList.length === 0) {
      return (
        <div className="text-center py-8 text-text-tertiary text-sm">
          No logs yet. Waiting for workflow events...
        </div>
      );
    }

    return (
      <div className="space-y-1 font-mono text-xs">
        {logList.map((log, index) => (
          <div
            key={index}
            className={cn(
              'flex items-start gap-3 p-2 rounded hover:bg-bg-tertiary transition-colors',
              log.type === 'error' && 'bg-accent-red/5',
              log.type === 'success' && 'bg-accent-green/5'
            )}
          >
            <span className="text-text-tertiary flex-shrink-0">[{log.timestamp}]</span>
            <span
              className={cn(
                'flex-1',
                log.type === 'info' && 'text-text-primary',
                log.type === 'success' && 'text-accent-green',
                log.type === 'warning' && 'text-accent-yellow',
                log.type === 'error' && 'text-accent-red',
                log.type === 'generated' && 'text-accent-teal'
              )}
            >
              {log.message}
            </span>
          </div>
        ))}
        <div ref={logEndRef} />
      </div>
    );
  };

  return (
    <Card className={cn('border-border-default bg-bg-secondary', className)}>
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <Terminal className="h-4 w-4 text-accent-blue" />
          Live Stream
          <Badge variant="outline" className="bg-accent-green/10 text-accent-green border-accent-green/20">
            <div className="w-2 h-2 rounded-full bg-accent-green mr-1.5 animate-pulse" />
            Live
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="strategy" className="w-full">
          <TabsList className="grid w-full grid-cols-3 bg-bg-tertiary">
            <TabsTrigger value="strategy">
              Strategy Log
              {strategyLogs.length > 0 && (
                <Badge variant="secondary" className="ml-2 bg-bg-primary">
                  {strategyLogs.length}
                </Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="data">
              Extracted Data
              {dataLogs.length > 0 && (
                <Badge variant="secondary" className="ml-2 bg-bg-primary">
                  {dataLogs.length}
                </Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="quality">
              Quality Checks
              {qualityLogs.length > 0 && (
                <Badge variant="secondary" className="ml-2 bg-bg-primary">
                  {qualityLogs.length}
                </Badge>
              )}
            </TabsTrigger>
          </TabsList>

          <TabsContent value="strategy" className="mt-4">
            <div className="bg-bg-primary border border-border-default rounded-lg p-4 max-h-96 overflow-y-auto">
              {renderLogs(strategyLogs)}
            </div>
          </TabsContent>

          <TabsContent value="data" className="mt-4">
            <div className="bg-bg-primary border border-border-default rounded-lg p-4 max-h-96 overflow-y-auto">
              {renderLogs(dataLogs)}
            </div>
          </TabsContent>

          <TabsContent value="quality" className="mt-4">
            <div className="bg-bg-primary border border-border-default rounded-lg p-4 max-h-96 overflow-y-auto">
              {renderLogs(qualityLogs)}
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
