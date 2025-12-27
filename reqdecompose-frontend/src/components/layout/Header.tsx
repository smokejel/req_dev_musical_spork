'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Sparkles, Plus } from 'lucide-react';
import { cn } from '@/lib/utils';

export function Header() {
  const pathname = usePathname();

  const navLinks = [
    { href: '/', label: 'Dashboard', active: pathname === '/' },
    { href: '/workflows', label: 'Workflows', active: pathname.startsWith('/workflows') },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border-default bg-bg-primary/95 backdrop-blur supports-[backdrop-filter]:bg-bg-primary/75">
      <div className="container flex h-16 items-center px-6">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 mr-8">
          <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-accent-blue/10">
            <Sparkles className="h-5 w-5 text-accent-blue" />
          </div>
          <span className="font-bold text-lg text-text-primary">
            ReqDecompose
          </span>
        </Link>

        {/* Navigation */}
        <nav className="flex items-center gap-6 flex-1">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={cn(
                'text-sm font-medium transition-colors hover:text-text-primary',
                link.active
                  ? 'text-text-primary'
                  : 'text-text-secondary'
              )}
            >
              {link.label}
            </Link>
          ))}
        </nav>

        {/* Actions */}
        <div className="flex items-center gap-4">
          <Button asChild size="sm">
            <Link href="/upload">
              <Plus className="mr-2 h-4 w-4" />
              New Project
            </Link>
          </Button>

          <Avatar className="h-8 w-8">
            <AvatarFallback className="bg-accent-purple/10 text-accent-purple text-xs font-semibold">
              AD
            </AvatarFallback>
          </Avatar>
        </div>
      </div>
    </header>
  );
}
