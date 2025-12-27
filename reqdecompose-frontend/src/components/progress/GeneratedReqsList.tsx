import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { FileText, CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface GeneratedReq {
  id: string;
  text: string;
  score?: number;
}

interface GeneratedReqsListProps {
  requirements: GeneratedReq[];
  totalCount: number;
  className?: string;
}

export function GeneratedReqsList({
  requirements,
  totalCount,
  className,
}: GeneratedReqsListProps) {
  return (
    <Card className={cn('border-border-default bg-bg-secondary', className)}>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center justify-between">
          <span className="flex items-center gap-2">
            <FileText className="h-4 w-4 text-accent-teal" />
            Generated Requirements
          </span>
          <Badge variant="secondary" className="bg-accent-teal/10 text-accent-teal">
            {requirements.length}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {requirements.length === 0 ? (
            <div className="text-center py-8 text-text-tertiary text-sm">
              <FileText className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p>No requirements generated yet</p>
              <p className="text-xs mt-1">Requirements will appear as they're created</p>
            </div>
          ) : (
            requirements.map((req) => (
              <div
                key={req.id}
                className="p-3 bg-bg-primary border border-border-default rounded-lg hover:border-accent-teal/50 transition-colors group"
              >
                <div className="flex items-start gap-2 mb-2">
                  <CheckCircle2 className="h-4 w-4 text-accent-green flex-shrink-0 mt-0.5" />
                  <span className="text-xs font-mono text-text-tertiary">{req.id}</span>
                  {req.score !== undefined && (
                    <Badge
                      variant="outline"
                      className={cn(
                        'ml-auto',
                        req.score >= 0.9 && 'bg-accent-green/10 text-accent-green border-accent-green/20',
                        req.score >= 0.65 && req.score < 0.9 && 'bg-accent-yellow/10 text-accent-yellow border-accent-yellow/20',
                        req.score < 0.65 && 'bg-accent-red/10 text-accent-red border-accent-red/20'
                      )}
                    >
                      {Math.round(req.score * 100)}%
                    </Badge>
                  )}
                </div>
                <p className="text-sm text-text-secondary leading-relaxed line-clamp-3 group-hover:line-clamp-none transition-all">
                  {req.text}
                </p>
              </div>
            ))
          )}
        </div>

        {requirements.length > 0 && (
          <div className="mt-4 pt-3 border-t border-border-default">
            <p className="text-xs text-text-tertiary text-center">
              View All ({totalCount} Generated) →
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
