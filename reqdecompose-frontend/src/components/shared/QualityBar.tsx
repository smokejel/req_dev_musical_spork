import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';

interface QualityBarProps {
  label: string;
  score: number; // 0-1
  className?: string;
  showPercentage?: boolean;
}

export function QualityBar({ label, score, className, showPercentage = true }: QualityBarProps) {
  const percentage = Math.round(score * 100);

  // Determine color based on score
  const getColorClass = (score: number): string => {
    if (score >= 0.9) return 'bg-accent-green';
    if (score >= 0.75) return 'bg-accent-blue';
    if (score >= 0.65) return 'bg-accent-yellow';
    return 'bg-accent-red';
  };

  const getTextColor = (score: number): string => {
    if (score >= 0.9) return 'text-accent-green';
    if (score >= 0.75) return 'text-accent-blue';
    if (score >= 0.65) return 'text-accent-yellow';
    return 'text-accent-red';
  };

  return (
    <div className={cn('space-y-2', className)}>
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-text-primary capitalize">
          {label}
        </span>
        {showPercentage && (
          <span className={cn('text-sm font-semibold', getTextColor(score))}>
            {percentage}%
          </span>
        )}
      </div>
      <div className="relative h-2 w-full overflow-hidden rounded-full bg-bg-tertiary">
        <div
          className={cn(
            'h-full transition-all duration-500 ease-out rounded-full',
            getColorClass(score)
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
