export type RequirementCategory = 'functional' | 'performance' | 'interface' | 'constraint' | 'quality';
export type RequirementPriority = 'critical' | 'high' | 'medium' | 'low';

export interface Requirement {
  id: string;
  text: string;
  category: RequirementCategory;
  priority?: RequirementPriority;
  parentId?: string;
  rationale?: string;
  acceptanceCriteria?: string[];
  qualityScore?: number;
}

export interface ExtractedRequirement extends Requirement {
  sourceLocation?: string;
  originalText?: string;
}

export interface DecomposedRequirement extends Requirement {
  parentRequirement: string;
  subsystem: string;
  derivationRationale: string;
}

export interface TraceabilityLink {
  parentId: string;
  childId: string;
  relationship: 'derives' | 'refines' | 'implements';
}

export interface TraceabilityMatrix {
  links: TraceabilityLink[];
  orphanedRequirements: string[];
  coveragePercentage: number;
}
