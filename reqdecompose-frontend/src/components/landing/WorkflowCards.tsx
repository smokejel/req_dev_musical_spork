import { Card, CardContent } from '@/components/ui/card';
import { FileText, Brain, GitBranch, CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { LucideIcon } from 'lucide-react';

interface WorkflowStep {
  icon: LucideIcon;
  title: string;
  description: string;
  color: string;
  bgColor: string;
}

const workflowSteps: WorkflowStep[] = [
  {
    icon: FileText,
    title: 'Extract',
    description: 'Parse specification documents and identify atomic requirements with AI-powered analysis.',
    color: 'text-accent-blue',
    bgColor: 'bg-accent-blue/10',
  },
  {
    icon: Brain,
    title: 'Analyze',
    description: 'Understand system context, constraints, and plan decomposition strategy with architectural reasoning.',
    color: 'text-accent-purple',
    bgColor: 'bg-accent-purple/10',
  },
  {
    icon: GitBranch,
    title: 'Decompose',
    description: 'Transform system requirements into detailed subsystem specs with full traceability.',
    color: 'text-accent-teal',
    bgColor: 'bg-accent-teal/10',
  },
  {
    icon: CheckCircle2,
    title: 'Validate',
    description: 'Automated quality scoring across completeness, clarity, testability, and traceability dimensions.',
    color: 'text-accent-orange',
    bgColor: 'bg-accent-orange/10',
  },
];

export function WorkflowCards() {
  return (
    <div className="py-16">
      <div className="container px-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {workflowSteps.map((step, index) => (
            <Card
              key={index}
              className="border-border-default bg-bg-secondary hover:border-border-default/50 transition-all hover:shadow-lg group"
            >
              <CardContent className="p-6">
                <div className="space-y-4">
                  {/* Icon */}
                  <div
                    className={cn(
                      'w-10 h-10 rounded-lg flex items-center justify-center transition-transform group-hover:scale-110',
                      step.bgColor
                    )}
                  >
                    <step.icon className={cn('w-6 h-6', step.color)} />
                  </div>

                  {/* Title */}
                  <h3 className="text-lg font-semibold text-text-primary">
                    {step.title}
                  </h3>

                  {/* Description */}
                  <p className="text-sm text-text-secondary leading-relaxed">
                    {step.description}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
