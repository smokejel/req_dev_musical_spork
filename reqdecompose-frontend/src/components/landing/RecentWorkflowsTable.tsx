'use client';

import { useRecentWorkflows } from '@/lib/queries';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { EmptyState } from '@/components/shared/EmptyState';
import { LoadingState } from '@/components/shared/LoadingState';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { FileText, ExternalLink, Sparkles, Lock, AlertCircle } from 'lucide-react';
import { formatRelativeTime } from '@/lib/utils';
import Link from 'next/link';
import { cn } from '@/lib/utils';

export function RecentWorkflowsTable() {
  const { data, isLoading, error } = useRecentWorkflows(10);

  return (
    <div className="py-16">
      <div className="container px-6">
        <Card className="border-border-default bg-bg-secondary">
          <CardHeader className="pb-4">
            <CardTitle className="text-2xl font-bold text-text-primary">
              Recent Workflows
            </CardTitle>
            {/* View All button removed - /workflows route doesn't exist */}
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <LoadingState variant="table" count={5} />
            ) : error ? (
              <div className="py-8">
                <EmptyState
                  icon={AlertCircle}
                  title="Failed to load workflows"
                  description="There was an error loading recent workflows. Please try again."
                />
              </div>
            ) : !data || data.workflows.length === 0 ? (
              <div className="py-8">
                <EmptyState
                  icon={FileText}
                  title="No workflows yet"
                  description="Start your first workflow to see it appear here."
                  action={
                    <Button asChild>
                      <Link href="/upload">
                        <Sparkles className="mr-2 h-4 w-4" />
                        Start New Workflow
                      </Link>
                    </Button>
                  }
                />
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow className="border-border-default hover:bg-transparent">
                    <TableHead className="text-text-secondary font-semibold w-[30%]">
                      Project Name
                    </TableHead>
                    <TableHead className="text-text-secondary font-semibold w-[20%]">
                      Source Document
                    </TableHead>
                    <TableHead className="text-text-secondary font-semibold w-[20%]">
                      Date Created
                    </TableHead>
                    <TableHead className="text-text-secondary font-semibold w-[15%]">
                      Status
                    </TableHead>
                    <TableHead className="text-text-secondary font-semibold w-[15%] text-right">
                      Actions
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.workflows.map((workflow) => (
                    <TableRow
                      key={workflow.id}
                      className="border-border-default hover:bg-bg-tertiary cursor-pointer transition-colors"
                      onClick={() => {
                        if (workflow.status === 'completed') {
                          window.location.href = `/results/${workflow.id}`;
                        } else if (workflow.status === 'processing') {
                          window.location.href = `/progress/${workflow.id}`;
                        }
                      }}
                    >
                      {/* Project Name */}
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <div className="flex-shrink-0">
                            <WorkflowIcon status={workflow.status} />
                          </div>
                          <div className="min-w-0">
                            <p className="font-medium text-text-primary truncate">
                              {workflow.projectName || 'Untitled Project'}
                            </p>
                            {workflow.qualityScore !== undefined && (
                              <p className="text-xs text-text-tertiary">
                                Quality: {Math.round(workflow.qualityScore * 100)}%
                              </p>
                            )}
                          </div>
                        </div>
                      </TableCell>

                      {/* Source Document */}
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <FileText className="h-4 w-4 text-text-tertiary flex-shrink-0" />
                          <span className="text-sm text-text-secondary truncate">
                            {workflow.sourceDocument}
                          </span>
                        </div>
                      </TableCell>

                      {/* Date Created */}
                      <TableCell>
                        <span className="text-sm text-text-secondary">
                          {formatRelativeTime(workflow.createdAt)}
                        </span>
                      </TableCell>

                      {/* Status */}
                      <TableCell>
                        <StatusBadge status={workflow.status} />
                      </TableCell>

                      {/* Actions */}
                      <TableCell className="text-right">
                        <Button
                          variant="ghost"
                          size="sm"
                          asChild
                          onClick={(e) => e.stopPropagation()}
                        >
                          <Link
                            href={
                              workflow.status === 'completed'
                                ? `/results/${workflow.id}`
                                : workflow.status === 'processing'
                                ? `/progress/${workflow.id}`
                                : '#'
                            }
                          >
                            View
                            <ExternalLink className="ml-2 h-3 w-3" />
                          </Link>
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function WorkflowIcon({ status }: { status: string }) {
  const iconClass = 'h-5 w-5';

  if (status === 'completed') {
    return (
      <div className="w-10 h-10 rounded-lg bg-accent-green/10 flex items-center justify-center">
        <Sparkles className={cn(iconClass, 'text-accent-green')} />
      </div>
    );
  }

  if (status === 'processing') {
    return (
      <div className="w-10 h-10 rounded-lg bg-accent-blue/10 flex items-center justify-center">
        <Sparkles className={cn(iconClass, 'text-accent-blue animate-pulse')} />
      </div>
    );
  }

  if (status === 'failed') {
    return (
      <div className="w-10 h-10 rounded-lg bg-accent-red/10 flex items-center justify-center">
        <AlertCircle className={cn(iconClass, 'text-accent-red')} />
      </div>
    );
  }

  return (
    <div className="w-10 h-10 rounded-lg bg-text-tertiary/10 flex items-center justify-center">
      <Lock className={cn(iconClass, 'text-text-tertiary')} />
    </div>
  );
}
