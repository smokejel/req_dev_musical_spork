import { WorkflowRun, WorkflowStatus, WorkflowMetrics } from './workflow';
import { Requirement, DecomposedRequirement, TraceabilityMatrix } from './requirement';
import { QualityMetrics } from './quality';

// API Request Types
export interface UploadWorkflowRequest {
  file: File;
  subsystem: string;
  domain: string;
  reviewMode: 'before' | 'after';
  analysisMode: 'standard' | 'thorough';
  qualityThreshold?: number;
  maxIterations?: number;
}

// API Response Types
export interface HealthCheckResponse {
  status: 'healthy' | 'unhealthy';
  service: string;
  version: string;
}

export interface UploadWorkflowResponse {
  workflowId: string;
  message: string;
}

export interface StartWorkflowResponse {
  workflowId: string;
  status: WorkflowStatus;
  message?: string;
}

export interface WorkflowStatusResponse {
  workflowId: string;
  status: WorkflowStatus;
  currentNode?: string;
  progress?: number; // 0-100
  message?: string;
  error?: string;
}

export interface SystemContext {
  projectName: string;
  subsystemName: string;
  subsystemDescription: string;
  domainContext?: string;
  constraints: string[];
  assumptions: string[];
}

export interface DecompositionStrategy {
  approach: string;
  allocationRules: {
    category: string;
    criteria: string[];
  }[];
  traceabilityPlan: string;
  qualityFocus: string[];
}

export interface WorkflowResultsResponse {
  workflowId: string;
  status: WorkflowStatus;
  dateCreated: string;
  dateCompleted?: string;

  // Configuration
  config: {
    subsystem: string;
    domain: string;
    reviewMode: string;
    analysisMode: string;
    qualityThreshold: number;
    maxIterations: number;
  };

  // Results
  extractedRequirements: Requirement[];
  systemContext: SystemContext;
  decompositionStrategy: DecompositionStrategy;
  decomposedRequirements: DecomposedRequirement[];
  qualityMetrics: QualityMetrics;
  traceabilityMatrix: TraceabilityMatrix;

  // Metadata
  metrics: WorkflowMetrics;
  costBreakdown: Record<string, number>;
  timingBreakdown: Record<string, number>;
  energyBreakdown: Record<string, number>;

  // Error info
  errors?: string[];
  errorLog?: Array<{
    timestamp: string;
    errorType: string;
    node: string;
    message: string;
  }>;
}

export interface RecentWorkflowsResponse {
  workflows: Array<{
    id: string;
    projectName: string;
    sourceDocument: string;
    createdAt: string;
    status: WorkflowStatus;
    qualityScore?: number;
  }>;
  total?: number;
}

export interface CancelWorkflowResponse {
  workflowId: string;
  status: WorkflowStatus;
  message: string;
}

export type ExportFormat = 'md' | 'docx' | 'csv' | 'json' | 'zip';
