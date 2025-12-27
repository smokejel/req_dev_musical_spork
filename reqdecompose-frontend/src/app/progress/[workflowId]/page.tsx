'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { PageShell } from '@/components/layout/PageShell';
import { ProgressHeader } from '@/components/progress/ProgressHeader';
import { PipelineViz } from '@/components/progress/PipelineViz';
import { LogStream } from '@/components/progress/LogStream';
import { GeneratedReqsList } from '@/components/progress/GeneratedReqsList';
import { LoadingState } from '@/components/shared/LoadingState';
import { useWorkflowStatus, useCancelWorkflow } from '@/lib/queries';
import { useWorkflowStream } from '@/lib/sse';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertCircle } from 'lucide-react';
import { toast } from 'sonner';

type NodeStatus = 'pending' | 'processing' | 'completed' | 'failed';

const PIPELINE_NODES = [
  { id: 'extract', label: 'Extract' },
  { id: 'analyze', label: 'Analyze' },
  { id: 'decompose', label: 'Decompose' },
  { id: 'validate', label: 'Validate' },
];

export default function ProgressPage() {
  const params = useParams();
  const router = useRouter();
  const workflowId = params.workflowId as string;

  const { data: statusData, isLoading } = useWorkflowStatus(workflowId);
  const sseState = useWorkflowStream(workflowId);
  const cancelMutation = useCancelWorkflow();

  const [elapsedTime, setElapsedTime] = useState(0);
  const [generatedReqs, setGeneratedReqs] = useState<any[]>([]);

  // Calculate elapsed time
  useEffect(() => {
    if (statusData?.status !== 'processing') return;

    const interval = setInterval(() => {
      setElapsedTime((prev) => prev + 1);
    }, 1000);

    return () => clearInterval(interval);
  }, [statusData?.status]);

  // Redirect to results page when completed
  useEffect(() => {
    if (statusData?.status === 'completed') {
      setTimeout(() => {
        router.push(`/results/${workflowId}`);
      }, 2000);
    }
  }, [statusData?.status, workflowId, router]);

  // Extract generated requirements from events
  useEffect(() => {
    const reqs = sseState.events
      .filter((e) => e.data.requirements)
      .flatMap((e) => e.data.requirements || []);
    setGeneratedReqs(reqs);
  }, [sseState.events]);

  const handleCancel = async () => {
    try {
      await cancelMutation.mutateAsync(workflowId);
      toast.success('Workflow cancelled successfully');
      router.push('/');
    } catch (error) {
      toast.error('Failed to cancel workflow');
    }
  };

  // Determine node statuses based on current node
  const getPipelineNodes = () => {
    const currentNode = sseState.currentNode || statusData?.currentNode;
    const status = statusData?.status || 'pending';

    return PIPELINE_NODES.map((node) => {
      let nodeStatus: NodeStatus = 'pending';

      if (status === 'completed') {
        nodeStatus = 'completed';
      } else if (status === 'failed') {
        nodeStatus = currentNode === node.id ? 'failed' : 'pending';
      } else if (currentNode) {
        const currentIndex = PIPELINE_NODES.findIndex((n) => n.id === currentNode);
        const nodeIndex = PIPELINE_NODES.findIndex((n) => n.id === node.id);

        if (nodeIndex < currentIndex) {
          nodeStatus = 'completed';
        } else if (nodeIndex === currentIndex) {
          nodeStatus = 'processing';
        }
      }

      return {
        ...node,
        status: nodeStatus,
      };
    });
  };

  if (isLoading) {
    return (
      <PageShell
        breadcrumbs={[
          { label: 'Dashboard', href: '/' },
          { label: 'Progress' },
        ]}
      >
        <LoadingState variant="card" count={3} />
      </PageShell>
    );
  }

  if (!statusData) {
    return (
      <PageShell
        breadcrumbs={[
          { label: 'Dashboard', href: '/' },
          { label: 'Progress' },
        ]}
      >
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Workflow not found. Please check the workflow ID and try again.
          </AlertDescription>
        </Alert>
      </PageShell>
    );
  }

  const pipelineNodes = getPipelineNodes();
  const progress = sseState.progress || (statusData.progress ?? 0);

  return (
    <PageShell
      breadcrumbs={[
        { label: 'Dashboard', href: '/' },
        { label: 'Workflows', href: '/' },
        { label: `Run #${workflowId.slice(0, 8)}` },
      ]}
    >
      <div className="space-y-6">
        {/* Header */}
        <ProgressHeader
          workflowId={workflowId}
          status={statusData.status}
          dateCreated={new Date().toISOString()}
          elapsedTime={elapsedTime}
          totalTokens={0}
          onCancel={statusData.status === 'processing' ? handleCancel : undefined}
        />

        {/* Pipeline Visualization */}
        <PipelineViz nodes={pipelineNodes} progress={progress} />

        {/* SSE Connection Error */}
        {sseState.error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{sseState.error}</AlertDescription>
          </Alert>
        )}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Log Stream */}
          <div className="lg:col-span-2">
            <LogStream events={sseState.events} />
          </div>

          {/* Right: Generated Requirements */}
          <div className="lg:col-span-1">
            <GeneratedReqsList
              requirements={generatedReqs}
              totalCount={generatedReqs.length}
            />
          </div>
        </div>
      </div>
    </PageShell>
  );
}
