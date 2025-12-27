import { Hero } from '@/components/landing/Hero';
import { WorkflowCards } from '@/components/landing/WorkflowCards';
import { RecentWorkflowsTable } from '@/components/landing/RecentWorkflowsTable';
import { PageShell } from '@/components/layout/PageShell';

export default function Home() {
  return (
    <PageShell>
      <div className="space-y-0 -mt-8">
        <Hero />
        <WorkflowCards />
        <RecentWorkflowsTable />
      </div>
    </PageShell>
  );
}
