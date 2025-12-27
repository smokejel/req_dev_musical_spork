'use client';

import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card, CardContent } from '@/components/ui/card';
import { Zap, Settings, AlertCircle, CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { ReviewMode, AnalysisMode } from '@/types/workflow';

export interface UploadFormData {
  subsystem: string;
  domain: string;
  reviewMode: ReviewMode;
  analysisMode: AnalysisMode;
  qualityThreshold: number;
  maxIterations: number;
}

interface ConfigPanelProps {
  formData: UploadFormData;
  onChange: (data: Partial<UploadFormData>) => void;
  errors?: Partial<Record<keyof UploadFormData, string>>;
}

const DOMAINS = [
  { value: 'generic', label: 'Generic' },
  { value: 'aerospace', label: 'Aerospace' },
  { value: 'automotive', label: 'Automotive' },
  { value: 'medical', label: 'Medical Devices' },
  { value: 'industrial', label: 'Industrial Controls' },
  { value: 'telecom', label: 'Telecommunications' },
  { value: 'fintech', label: 'Financial Technology' },
];

export function ConfigPanel({ formData, onChange, errors }: ConfigPanelProps) {
  return (
    <div className="space-y-6">
      {/* Target Subsystem */}
      <div className="space-y-2">
        <Label htmlFor="subsystem" className="text-sm font-medium text-text-primary">
          Target Subsystem <span className="text-accent-red">*</span>
        </Label>
        <Input
          id="subsystem"
          placeholder="e.g., Navigation Display, Authentication Module"
          value={formData.subsystem}
          onChange={(e) => onChange({ subsystem: e.target.value })}
          className={cn(
            'bg-bg-tertiary border-border-default',
            errors?.subsystem && 'border-accent-red focus-visible:ring-accent-red'
          )}
        />
        {errors?.subsystem && (
          <p className="text-xs text-accent-red flex items-center gap-1">
            <AlertCircle className="h-3 w-3" />
            {errors.subsystem}
          </p>
        )}
        <p className="text-xs text-text-tertiary">
          Specify which subsystem or module to generate requirements for
        </p>
      </div>

      {/* Domain */}
      <div className="space-y-2">
        <Label htmlFor="domain" className="text-sm font-medium text-text-primary">
          Domain
        </Label>
        <Select value={formData.domain} onValueChange={(value) => onChange({ domain: value })}>
          <SelectTrigger
            id="domain"
            className={cn(
              'bg-bg-tertiary border-border-default',
              errors?.domain && 'border-accent-red focus-visible:ring-accent-red'
            )}
          >
            <SelectValue placeholder="Select a domain" />
          </SelectTrigger>
          <SelectContent>
            {DOMAINS.map((domain) => (
              <SelectItem key={domain.value} value={domain.value}>
                {domain.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {errors?.domain && (
          <p className="text-xs text-accent-red flex items-center gap-1">
            <AlertCircle className="h-3 w-3" />
            {errors.domain}
          </p>
        )}
        <p className="text-xs text-text-tertiary">
          Select domain for specialized terminology and compliance checks
        </p>
      </div>

      {/* Human-in-the-Loop Review */}
      <div className="space-y-2">
        <Label className="text-sm font-medium text-text-primary">
          Human-in-the-Loop Review
        </Label>
        <div className="grid grid-cols-2 gap-3">
          <button
            type="button"
            onClick={() => onChange({ reviewMode: 'before' })}
            className={cn(
              'p-4 rounded-lg border-2 text-left transition-all',
              formData.reviewMode === 'before'
                ? 'border-accent-blue bg-accent-blue/10 ring-1 ring-accent-blue/30'
                : 'border-border-default bg-bg-tertiary hover:border-border-default/50'
            )}
          >
            <div className="flex items-center justify-between mb-1">
              <p className="font-medium text-sm text-text-primary">Review Before</p>
              {formData.reviewMode === 'before' && (
                <CheckCircle2 className="h-4 w-4 text-accent-blue flex-shrink-0" />
              )}
            </div>
            <p className="text-xs text-text-secondary">
              Review decomposition strategy before execution
            </p>
          </button>

          <button
            type="button"
            onClick={() => onChange({ reviewMode: 'after' })}
            className={cn(
              'p-4 rounded-lg border-2 text-left transition-all',
              formData.reviewMode === 'after'
                ? 'border-accent-blue bg-accent-blue/10 ring-1 ring-accent-blue/30'
                : 'border-border-default bg-bg-tertiary hover:border-border-default/50'
            )}
          >
            <div className="flex items-center justify-between mb-1">
              <p className="font-medium text-sm text-text-primary">Review After</p>
              {formData.reviewMode === 'after' && (
                <CheckCircle2 className="h-4 w-4 text-accent-blue flex-shrink-0" />
              )}
            </div>
            <p className="text-xs text-text-secondary">
              Review only if quality validation fails
            </p>
          </button>
        </div>
      </div>

      {/* Analysis Mode */}
      <div className="space-y-2">
        <Label className="text-sm font-medium text-text-primary">Analysis Mode</Label>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card
            onClick={() => onChange({ analysisMode: 'standard' })}
            className={cn(
              'cursor-pointer transition-all border-2',
              formData.analysisMode === 'standard'
                ? 'border-accent-blue bg-accent-blue/10 ring-1 ring-accent-blue/30'
                : 'border-border-default bg-bg-secondary hover:border-border-default/50'
            )}
          >
            <CardContent className="p-4">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-lg bg-accent-blue/10 flex items-center justify-center flex-shrink-0">
                  <Zap className="h-5 w-5 text-accent-blue" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <h4 className="font-semibold text-sm text-text-primary">Standard</h4>
                    {formData.analysisMode === 'standard' && (
                      <CheckCircle2 className="h-4 w-4 text-accent-blue flex-shrink-0" />
                    )}
                  </div>
                  <p className="text-xs text-text-secondary mb-2">
                    Optimized for speed with standard quality checks
                  </p>
                  <div className="flex items-center gap-4 text-xs">
                    <span className="text-text-tertiary">~2-5 min</span>
                    <span className="text-text-tertiary">•</span>
                    <span className="text-text-tertiary">$0.10-$0.30</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card
            onClick={() => onChange({ analysisMode: 'thorough' })}
            className={cn(
              'cursor-pointer transition-all border-2',
              formData.analysisMode === 'thorough'
                ? 'border-accent-purple bg-accent-purple/10 ring-1 ring-accent-purple/30'
                : 'border-border-default bg-bg-secondary hover:border-border-default/50'
            )}
          >
            <CardContent className="p-4">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-lg bg-accent-purple/10 flex items-center justify-center flex-shrink-0">
                  <Settings className="h-5 w-5 text-accent-purple" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <h4 className="font-semibold text-sm text-text-primary">Thorough</h4>
                    {formData.analysisMode === 'thorough' && (
                      <CheckCircle2 className="h-4 w-4 text-accent-purple flex-shrink-0" />
                    )}
                  </div>
                  <p className="text-xs text-text-secondary mb-2">
                    Recursive ISO/IEEE compliance checks with iterative refinement
                  </p>
                  <div className="flex items-center gap-4 text-xs">
                    <span className="text-text-tertiary">~5-15 min</span>
                    <span className="text-text-tertiary">•</span>
                    <span className="text-text-tertiary">$0.50-$1.50</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Advanced Settings (Optional) */}
      <details className="group">
        <summary className="cursor-pointer text-sm font-medium text-text-secondary hover:text-text-primary transition-colors flex items-center gap-2">
          <Settings className="h-4 w-4" />
          Advanced Settings
        </summary>
        <div className="mt-4 space-y-4 pl-6">
          <div className="space-y-2">
            <Label htmlFor="qualityThreshold" className="text-sm font-medium text-text-primary">
              Quality Threshold
            </Label>
            <Input
              id="qualityThreshold"
              type="number"
              min="0"
              max="1"
              step="0.05"
              value={formData.qualityThreshold}
              onChange={(e) => onChange({ qualityThreshold: parseFloat(e.target.value) })}
              className="bg-bg-tertiary border-border-default"
            />
            <p className="text-xs text-text-tertiary">
              Minimum quality score (0.0-1.0). Default: 0.80
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="maxIterations" className="text-sm font-medium text-text-primary">
              Max Iterations
            </Label>
            <Input
              id="maxIterations"
              type="number"
              min="1"
              max="5"
              value={formData.maxIterations}
              onChange={(e) => onChange({ maxIterations: parseInt(e.target.value) })}
              className="bg-bg-tertiary border-border-default"
            />
            <p className="text-xs text-text-tertiary">
              Maximum refinement iterations. Default: 3
            </p>
          </div>
        </div>
      </details>
    </div>
  );
}
