export type WorkflowStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';

export type ReviewMode = 'before' | 'after';
export type AnalysisMode = 'standard' | 'thorough';

export interface WorkflowConfig {
  subsystem: string;
  domain: string;
  reviewMode: ReviewMode;
  analysisMode: AnalysisMode;
  qualityThreshold?: number;
  maxIterations?: number;
}

export interface WorkflowRun {
  workflowId: string;
  status: WorkflowStatus;
  projectName?: string;
  sourceDocument: string;
  dateCreated: string;
  dateCompleted?: string;
  config: WorkflowConfig;
  initiator?: string;
  runNumber?: number;
}

export interface WorkflowMetrics {
  elapsedTime: number; // seconds
  totalCost: number; // dollars
  totalEnergy: number; // watt-hours
  totalTokens: number;
  requirementsExtracted: number;
  requirementsGenerated: number;
  qualityScore: number;
}

export interface WorkflowEvent {
  type: 'workflow_started' | 'workflow_completed' | 'workflow_failed' | 'node_started' | 'node_completed' | 'progress_update' | 'review_needed';
  timestamp: string;
  data: Record<string, any>;
}
