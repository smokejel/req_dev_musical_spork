export type QualityDimension = 'completeness' | 'clarity' | 'testability' | 'traceability' | 'domainCompliance';
export type IssueSeverity = 'critical' | 'warning' | 'info';

export interface DimensionScore {
  dimension: QualityDimension;
  score: number; // 0-1
  weight: number; // 0-1
  issues: QualityIssue[];
}

export interface QualityMetrics {
  overallScore: number; // 0-1
  dimensions: DimensionScore[];
  passed: boolean;
  threshold: number;
  iterationCount: number;
}

export interface QualityIssue {
  id: string;
  requirementId?: string;
  severity: IssueSeverity;
  dimension: QualityDimension;
  description: string;
  suggestion?: string;
  location?: string;
}

export interface ValidationResult {
  passed: boolean;
  score: number;
  issues: QualityIssue[];
  suggestions: string[];
}
