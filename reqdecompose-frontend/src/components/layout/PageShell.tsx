import { ReactNode } from 'react';
import { Header } from './Header';
import { Breadcrumbs, type BreadcrumbItem } from './Breadcrumbs';
import { cn } from '@/lib/utils';

interface PageShellProps {
  children: ReactNode;
  title?: string;
  description?: string;
  breadcrumbs?: BreadcrumbItem[];
  actions?: ReactNode;
  className?: string;
}

export function PageShell({
  children,
  title,
  description,
  breadcrumbs,
  actions,
  className,
}: PageShellProps) {
  return (
    <div className="min-h-screen bg-bg-primary">
      <Header />
      <main className={cn('container px-6 py-8', className)}>
        {/* Page Header */}
        {(breadcrumbs || title || actions) && (
          <div className="mb-8">
            {breadcrumbs && <Breadcrumbs items={breadcrumbs} className="mb-4" />}
            {(title || actions) && (
              <div className="flex items-start justify-between">
                <div>
                  {title && (
                    <h1 className="text-3xl font-bold text-text-primary mb-2">
                      {title}
                    </h1>
                  )}
                  {description && (
                    <p className="text-text-secondary max-w-3xl">
                      {description}
                    </p>
                  )}
                </div>
                {actions && <div className="flex items-center gap-2">{actions}</div>}
              </div>
            )}
          </div>
        )}

        {/* Page Content */}
        {children}
      </main>
    </div>
  );
}
