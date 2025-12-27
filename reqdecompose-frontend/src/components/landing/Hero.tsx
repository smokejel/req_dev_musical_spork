'use client';

import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Sparkles, Play } from 'lucide-react';
import Link from 'next/link';

export function Hero() {
  return (
    <div className="relative overflow-hidden py-20 lg:py-28">
      <div className="container px-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Left: Content */}
          <div className="space-y-8">
            <Badge
              variant="outline"
              className="bg-accent-blue/10 text-accent-blue border-accent-blue/20 hover:bg-accent-blue/20"
            >
              <Sparkles className="mr-1.5 h-3 w-3" />
              AI-POWERED ENGINEERING
            </Badge>

            <div className="space-y-4">
              <h1 className="text-5xl lg:text-6xl font-bold text-text-primary leading-tight">
                Decompose Complex Requirements with{' '}
                <span className="text-accent-blue">AI Precision</span>.
              </h1>
              <p className="text-lg text-text-secondary max-w-2xl">
                Transform high-level system specifications into detailed, testable requirements
                using our LangGraph-powered multi-agent system. Automated quality validation,
                traceability tracking, and domain-aware decomposition.
              </p>
            </div>

            <div className="flex flex-wrap gap-4">
              <Button asChild size="lg" className="text-base">
                <Link href="/upload">
                  <Sparkles className="mr-2 h-5 w-5" />
                  Start New Workflow
                </Link>
              </Button>
              <Button asChild size="lg" variant="outline" className="text-base">
                <Link href="#demo">
                  <Play className="mr-2 h-5 w-5" />
                  View Demo
                </Link>
              </Button>
            </div>
          </div>

          {/* Right: Animated Visualization */}
          <div className="relative flex items-center justify-center">
            <HeroAnimation />
          </div>
        </div>
      </div>
    </div>
  );
}

function HeroAnimation() {
  return (
    <div className="relative w-full max-w-md aspect-square">
      {/* Glowing blue circle with pulse animation */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="w-64 h-64 rounded-full bg-accent-blue/20 blur-3xl animate-pulse" />
      </div>

      {/* Neural network pattern */}
      <div className="relative w-full h-full flex items-center justify-center">
        {/* Center node */}
        <div className="absolute w-16 h-16 rounded-full bg-accent-blue border-2 border-accent-blue/50 shadow-lg shadow-accent-blue/50 flex items-center justify-center">
          <Sparkles className="w-8 h-8 text-white" />
        </div>

        {/* Orbiting nodes */}
        {[0, 1, 2, 3].map((i) => {
          const angle = (i * 90) - 45; // Offset by 45 degrees
          const radius = 120;
          const x = Math.cos((angle * Math.PI) / 180) * radius;
          const y = Math.sin((angle * Math.PI) / 180) * radius;

          return (
            <div
              key={i}
              className="absolute w-12 h-12 rounded-full bg-bg-secondary border-2 border-border-default shadow-lg"
              style={{
                left: `calc(50% + ${x}px - 1.5rem)`,
                top: `calc(50% + ${y}px - 1.5rem)`,
                animation: `float ${3 + i * 0.5}s ease-in-out infinite`,
                animationDelay: `${i * 0.2}s`,
              }}
            >
              <div className="w-full h-full rounded-full bg-gradient-to-br from-accent-purple/20 to-accent-teal/20" />
            </div>
          );
        })}

        {/* Connection lines */}
        <svg className="absolute inset-0 w-full h-full" style={{ zIndex: -1 }}>
          {[0, 1, 2, 3].map((i) => {
            const angle = (i * 90) - 45;
            const radius = 120;
            const x = Math.cos((angle * Math.PI) / 180) * radius;
            const y = Math.sin((angle * Math.PI) / 180) * radius;

            return (
              <line
                key={i}
                x1="50%"
                y1="50%"
                x2={`calc(50% + ${x}px)`}
                y2={`calc(50% + ${y}px)`}
                stroke="rgba(56, 139, 253, 0.2)"
                strokeWidth="2"
                strokeDasharray="4 4"
              />
            );
          })}
        </svg>
      </div>

      {/* Progress indicator */}
      <div className="absolute bottom-0 left-0 right-0 bg-bg-secondary border border-border-default rounded-lg p-3 shadow-lg">
        <div className="flex items-center gap-2 mb-2">
          <div className="w-2 h-2 rounded-full bg-accent-blue animate-pulse" />
          <span className="text-xs text-text-secondary font-mono">
            Processing PRD_v2.pdf...
          </span>
        </div>
        <div className="h-1 w-full bg-bg-tertiary rounded-full overflow-hidden">
          <div
            className="h-full bg-accent-blue rounded-full"
            style={{
              width: '67%',
              animation: 'progress 3s ease-in-out infinite',
            }}
          />
        </div>
      </div>

      {/* Keyframes for animations */}
      <style jsx>{`
        @keyframes float {
          0%, 100% {
            transform: translateY(0px);
          }
          50% {
            transform: translateY(-10px);
          }
        }

        @keyframes progress {
          0% {
            width: 0%;
          }
          50% {
            width: 67%;
          }
          100% {
            width: 100%;
          }
        }
      `}</style>
    </div>
  );
}
