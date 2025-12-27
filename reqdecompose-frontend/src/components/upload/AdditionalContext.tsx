'use client';

import { useState } from 'react';
import { FileText, ChevronDown, ChevronUp } from 'lucide-react';
import { cn } from '@/lib/utils';

export function AdditionalContext() {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="border border-border-default rounded-lg bg-bg-secondary">
      <button
        type="button"
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-6 py-4 flex items-center justify-between hover:bg-bg-tertiary transition-colors"
      >
        <div className="flex items-center gap-3">
          <FileText className="h-5 w-5 text-accent-teal" />
          <div className="text-left">
            <h3 className="text-sm font-semibold text-text-primary">
              Additional Context / Reference Material
            </h3>
            <p className="text-xs text-text-secondary">
              Optional supplementary documents for context
            </p>
          </div>
        </div>
        {isExpanded ? (
          <ChevronUp className="h-5 w-5 text-text-tertiary" />
        ) : (
          <ChevronDown className="h-5 w-5 text-text-tertiary" />
        )}
      </button>

      {isExpanded && (
        <div className="px-6 pb-6 border-t border-border-default">
          <div className="mt-4 p-8 border-2 border-dashed border-border-default rounded-lg text-center">
            <FileText className="h-8 w-8 text-text-tertiary mx-auto mb-2" />
            <p className="text-sm text-text-secondary">
              Additional context support coming soon
            </p>
            <p className="text-xs text-text-tertiary mt-1">
              Upload reference documents, architecture diagrams, or related specs
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
