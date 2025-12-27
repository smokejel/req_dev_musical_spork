# ReqDecompose AI — Claude Code Implementation Plan

**Version:** 1.0  
**Date:** December 21, 2025  
**Purpose:** Step-by-step technical implementation guide for Claude Code  
**Target:** Next.js 14+ frontend application

---

## Overview

This document provides a structured implementation plan for building the ReqDecompose AI web frontend. Follow each phase in order. Each phase builds on the previous one.

**Tech Stack:**
- Next.js 14+ (App Router)
- TypeScript 5+
- Tailwind CSS
- shadcn/ui components
- Zustand (client state)
- TanStack Query (server state)
- Lucide React (icons)

**Design Reference:** See `reqdecompose-ui-ux-spec.md` for detailed component specifications.

---

## Phase 1: Project Setup

### 1.1 Initialize Next.js Project

```bash
npx create-next-app@latest reqdecompose-frontend --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
cd reqdecompose-frontend
```

### 1.2 Install Dependencies

```bash
# UI Components
npx shadcn@latest init

# When prompted:
# - Style: Default
# - Base color: Slate
# - CSS variables: Yes

# Install specific shadcn components
npx shadcn@latest add button card input label badge progress tabs table alert dialog dropdown-menu select textarea toast separator skeleton avatar

# Additional dependencies
npm install zustand @tanstack/react-query axios lucide-react react-dropzone recharts date-fns clsx tailwind-merge
```

### 1.3 Configure Tailwind for Dark Theme

**File:** `tailwind.config.ts`

```typescript
import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Custom dark theme colors matching Stitch designs
        background: {
          DEFAULT: "#0D1117",
          secondary: "#161B22",
          tertiary: "#21262D",
        },
        border: {
          DEFAULT: "#30363D",
          accent: "#388BFD",
        },
        foreground: {
          DEFAULT: "#F0F6FC",
          secondary: "#8B949E",
          muted: "#6E7681",
        },
        accent: {
          blue: "#388BFD",
          green: "#3FB950",
          yellow: "#D29922",
          red: "#F85149",
          purple: "#A371F7",
        },
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
```

### 1.4 Global Styles

**File:** `src/app/globals.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 5%;
    --foreground: 210 40% 98%;
    --card: 220 13% 9%;
    --card-foreground: 210 40% 98%;
    --primary: 213 94% 60%;
    --primary-foreground: 0 0% 100%;
    --secondary: 215 14% 14%;
    --secondary-foreground: 210 40% 98%;
    --muted: 215 14% 18%;
    --muted-foreground: 215 16% 57%;
    --accent: 213 94% 60%;
    --accent-foreground: 0 0% 100%;
    --destructive: 0 84% 60%;
    --destructive-foreground: 0 0% 100%;
    --border: 215 14% 23%;
    --input: 215 14% 18%;
    --ring: 213 94% 60%;
    --radius: 0.5rem;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #161B22;
}

::-webkit-scrollbar-thumb {
  background: #30363D;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #484F58;
}

/* Code/log styling */
.font-mono {
  font-family: 'JetBrains Mono', monospace;
}
```

### 1.5 Project Structure

Create the following directory structure:

```
src/
├── app/
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Landing page
│   ├── upload/
│   │   └── page.tsx            # Upload & Configure
│   ├── run/
│   │   └── [id]/
│   │       └── page.tsx        # Run Progress
│   └── results/
│       └── [id]/
│           └── page.tsx        # Dashboard/Results
├── components/
│   ├── ui/                     # shadcn components (auto-generated)
│   ├── layout/
│   │   ├── Header.tsx
│   │   ├── Breadcrumb.tsx
│   │   └── Footer.tsx
│   ├── landing/
│   │   ├── HeroSection.tsx
│   │   ├── WorkflowCards.tsx
│   │   └── RecentWorkflows.tsx
│   ├── upload/
│   │   ├── FileUploader.tsx
│   │   ├── ConfigurationPanel.tsx
│   │   ├── DomainSelector.tsx
│   │   └── AnalysisModeSelector.tsx
│   ├── run/
│   │   ├── PipelineVisualization.tsx
│   │   ├── LogPanel.tsx
│   │   ├── HumanReviewPanel.tsx
│   │   └── GeneratedRequirements.tsx
│   └── results/
│       ├── SummaryCards.tsx
│       ├── QualityBreakdown.tsx
│       ├── RequirementsTable.tsx
│       ├── TraceabilityPanel.tsx
│       └── QualityIssuesPanel.tsx
├── lib/
│   ├── api.ts                  # API client
│   ├── sse.ts                  # SSE utilities
│   ├── utils.ts                # General utilities
│   └── constants.ts            # App constants
├── hooks/
│   ├── useWorkflow.ts
│   ├── useSSE.ts
│   └── useFileUpload.ts
├── stores/
│   └── workflowStore.ts        # Zustand store
└── types/
    └── index.ts                # TypeScript types
```

---

## Phase 2: Type Definitions & API Client

### 2.1 Type Definitions

**File:** `src/types/index.ts`

```typescript
// Workflow status
export type WorkflowStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'paused';

// Node status
export type NodeStatus = 'pending' | 'active' | 'complete' | 'error';

// Requirement types
export type RequirementType = 'functional' | 'performance' | 'safety' | 'interface' | 'constraint';

// Issue severity
export type IssueSeverity = 'critical' | 'major' | 'minor';

// Human review mode
export type ReviewMode = 'before' | 'after';

// Analysis mode
export type AnalysisMode = 'standard' | 'thorough';

// Domain options
export type Domain = 'generic' | 'aerospace' | 'automotive' | 'rail' | 'medical' | 'software';

// Requirement
export interface Requirement {
  id: string;
  text: string;
  type: RequirementType;
  parentId: string | null;
  subsystem: string;
  score: number | null;
  rationale?: string;
  acceptanceCriteria?: string;
  sourceReference?: string;
  hasIssues: boolean;
}

// Quality metrics
export interface QualityMetrics {
  overallScore: number;
  completeness: number;
  clarity: number;
  testability: number;
  traceability: number;
  domainCompliance?: number;
}

// Quality issue
export interface QualityIssue {
  requirementId: string;
  severity: IssueSeverity;
  category: string;
  description: string;
  suggestion: string;
}

// Workflow configuration
export interface WorkflowConfig {
  targetSubsystem: string;
  domain: Domain;
  reviewMode: ReviewMode;
  analysisMode: AnalysisMode;
  qualityThreshold?: number;
  maxIterations?: number;
}

// Workflow run
export interface WorkflowRun {
  id: string;
  projectName: string;
  sourceDocument: string;
  status: WorkflowStatus;
  config: WorkflowConfig;
  createdAt: string;
  startedAt?: string;
  completedAt?: string;
  
  // Progress
  currentNode?: string;
  progress: number;
  elapsedTime: number;
  tokenCount: number;
  
  // Results
  extractedCount?: number;
  generatedCount?: number;
  qualityMetrics?: QualityMetrics;
  requirements?: Requirement[];
  issues?: QualityIssue[];
  
  // Operational metrics
  totalCost?: number;
  energyWh?: number;
}

// Node progress event
export interface NodeProgress {
  node: string;
  status: NodeStatus;
  message?: string;
}

// Log entry
export interface LogEntry {
  timestamp: string;
  level: 'info' | 'success' | 'warning' | 'error';
  message: string;
}

// Human review request
export interface HumanReviewRequest {
  requirementId: string;
  reason: string;
  currentDraft: string;
  conflictRef?: string;
}

// SSE Event types
export type SSEEventType = 
  | 'node_started'
  | 'node_completed'
  | 'log_entry'
  | 'requirement_generated'
  | 'human_review_required'
  | 'progress_update'
  | 'workflow_completed'
  | 'workflow_failed';

export interface SSEEvent {
  type: SSEEventType;
  data: unknown;
}

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export interface UploadResponse {
  workflowId: string;
  message: string;
}

export interface StartWorkflowResponse {
  workflowId: string;
  status: WorkflowStatus;
}
```

### 2.2 API Client

**File:** `src/lib/api.ts`

```typescript
import axios, { AxiosInstance, AxiosError } from 'axios';
import { 
  WorkflowRun, 
  WorkflowConfig, 
  UploadResponse, 
  StartWorkflowResponse,
  ApiResponse 
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        console.error('API Error:', error.response?.data || error.message);
        throw error;
      }
    );
  }

  // Upload specification document
  async uploadDocument(
    file: File,
    config: WorkflowConfig,
    additionalFiles?: File[]
  ): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('subsystem', config.targetSubsystem);
    formData.append('domain', config.domain);
    formData.append('review_mode', config.reviewMode);
    formData.append('analysis_mode', config.analysisMode);
    
    if (config.qualityThreshold) {
      formData.append('quality_threshold', config.qualityThreshold.toString());
    }
    if (config.maxIterations) {
      formData.append('max_iterations', config.maxIterations.toString());
    }
    
    if (additionalFiles) {
      additionalFiles.forEach((f, i) => {
        formData.append(`context_file_${i}`, f);
      });
    }

    const response = await this.client.post<UploadResponse>(
      '/api/workflows/upload',
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );
    
    return response.data;
  }

  // Start workflow execution
  async startWorkflow(workflowId: string): Promise<StartWorkflowResponse> {
    const response = await this.client.post<StartWorkflowResponse>(
      `/api/workflows/${workflowId}/start`
    );
    return response.data;
  }

  // Get workflow status
  async getWorkflowStatus(workflowId: string): Promise<WorkflowRun> {
    const response = await this.client.get<WorkflowRun>(
      `/api/workflows/${workflowId}/status`
    );
    return response.data;
  }

  // Get recent workflows
  async getRecentWorkflows(limit: number = 10): Promise<WorkflowRun[]> {
    const response = await this.client.get<WorkflowRun[]>(
      `/api/workflows/recent?limit=${limit}`
    );
    return response.data;
  }

  // Get workflow results
  async getWorkflowResults(workflowId: string): Promise<WorkflowRun> {
    const response = await this.client.get<WorkflowRun>(
      `/api/workflows/${workflowId}/results`
    );
    return response.data;
  }

  // Submit human review feedback
  async submitReview(
    workflowId: string,
    requirementId: string,
    action: 'approve' | 'edit',
    editedText?: string
  ): Promise<void> {
    await this.client.post(`/api/workflows/${workflowId}/review`, {
      requirement_id: requirementId,
      action,
      edited_text: editedText,
    });
  }

  // Cancel workflow
  async cancelWorkflow(workflowId: string): Promise<void> {
    await this.client.post(`/api/workflows/${workflowId}/cancel`);
  }

  // Export results
  async exportResults(
    workflowId: string,
    format: 'markdown' | 'docx' | 'csv' | 'json' | 'zip'
  ): Promise<Blob> {
    const response = await this.client.get(
      `/api/workflows/${workflowId}/export?format=${format}`,
      { responseType: 'blob' }
    );
    return response.data;
  }

  // Get SSE stream URL
  getStreamUrl(workflowId: string): string {
    return `${API_BASE_URL}/api/workflows/${workflowId}/stream`;
  }
}

export const api = new ApiClient();
```

### 2.3 SSE Utilities

**File:** `src/lib/sse.ts`

```typescript
import { SSEEvent, SSEEventType } from '@/types';

export type SSEEventHandler = (event: SSEEvent) => void;

export class SSEClient {
  private eventSource: EventSource | null = null;
  private handlers: Map<SSEEventType | 'all', SSEEventHandler[]> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 3;
  private reconnectDelay = 1000;

  constructor(private url: string) {}

  connect(): void {
    if (this.eventSource) {
      this.disconnect();
    }

    this.eventSource = new EventSource(this.url);

    this.eventSource.onopen = () => {
      console.log('SSE connected');
      this.reconnectAttempts = 0;
    };

    this.eventSource.onerror = (error) => {
      console.error('SSE error:', error);
      this.handleError();
    };

    this.eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.emit({ type: data.event, data: data.data });
      } catch (e) {
        console.error('Failed to parse SSE message:', e);
      }
    };

    // Listen for specific event types
    const eventTypes: SSEEventType[] = [
      'node_started',
      'node_completed',
      'log_entry',
      'requirement_generated',
      'human_review_required',
      'progress_update',
      'workflow_completed',
      'workflow_failed',
    ];

    eventTypes.forEach((eventType) => {
      this.eventSource?.addEventListener(eventType, (event: MessageEvent) => {
        try {
          const data = JSON.parse(event.data);
          this.emit({ type: eventType, data });
        } catch (e) {
          console.error(`Failed to parse ${eventType} event:`, e);
        }
      });
    });
  }

  disconnect(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }

  on(eventType: SSEEventType | 'all', handler: SSEEventHandler): void {
    const handlers = this.handlers.get(eventType) || [];
    handlers.push(handler);
    this.handlers.set(eventType, handlers);
  }

  off(eventType: SSEEventType | 'all', handler: SSEEventHandler): void {
    const handlers = this.handlers.get(eventType) || [];
    const index = handlers.indexOf(handler);
    if (index > -1) {
      handlers.splice(index, 1);
    }
  }

  private emit(event: SSEEvent): void {
    // Emit to specific handlers
    const specificHandlers = this.handlers.get(event.type) || [];
    specificHandlers.forEach((handler) => handler(event));

    // Emit to 'all' handlers
    const allHandlers = this.handlers.get('all') || [];
    allHandlers.forEach((handler) => handler(event));
  }

  private handleError(): void {
    this.disconnect();

    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Reconnecting... attempt ${this.reconnectAttempts}`);
      setTimeout(() => this.connect(), this.reconnectDelay * this.reconnectAttempts);
    } else {
      console.error('Max reconnect attempts reached');
      this.emit({ type: 'workflow_failed', data: { error: 'Connection lost' } });
    }
  }
}
```

### 2.4 Zustand Store

**File:** `src/stores/workflowStore.ts`

```typescript
import { create } from 'zustand';
import { 
  WorkflowRun, 
  WorkflowConfig, 
  NodeStatus, 
  LogEntry, 
  Requirement,
  HumanReviewRequest 
} from '@/types';

interface WorkflowState {
  // Current workflow
  currentWorkflow: WorkflowRun | null;
  
  // Node statuses
  nodeStatuses: Record<string, NodeStatus>;
  
  // Log entries
  logs: LogEntry[];
  
  // Generated requirements (live)
  liveRequirements: Requirement[];
  
  // Human review
  humanReviewRequest: HumanReviewRequest | null;
  
  // Loading states
  isUploading: boolean;
  isStarting: boolean;
  
  // Actions
  setCurrentWorkflow: (workflow: WorkflowRun | null) => void;
  updateNodeStatus: (node: string, status: NodeStatus) => void;
  addLogEntry: (entry: LogEntry) => void;
  addRequirement: (req: Requirement) => void;
  setHumanReviewRequest: (request: HumanReviewRequest | null) => void;
  updateProgress: (progress: number, tokens: number, elapsed: number) => void;
  setUploading: (isUploading: boolean) => void;
  setStarting: (isStarting: boolean) => void;
  reset: () => void;
}

const initialState = {
  currentWorkflow: null,
  nodeStatuses: {
    extract: 'pending' as NodeStatus,
    analyze: 'pending' as NodeStatus,
    decompose: 'pending' as NodeStatus,
    validate: 'pending' as NodeStatus,
  },
  logs: [],
  liveRequirements: [],
  humanReviewRequest: null,
  isUploading: false,
  isStarting: false,
};

export const useWorkflowStore = create<WorkflowState>((set) => ({
  ...initialState,

  setCurrentWorkflow: (workflow) => set({ currentWorkflow: workflow }),

  updateNodeStatus: (node, status) =>
    set((state) => ({
      nodeStatuses: { ...state.nodeStatuses, [node]: status },
    })),

  addLogEntry: (entry) =>
    set((state) => ({
      logs: [...state.logs, entry],
    })),

  addRequirement: (req) =>
    set((state) => ({
      liveRequirements: [...state.liveRequirements, req],
    })),

  setHumanReviewRequest: (request) => set({ humanReviewRequest: request }),

  updateProgress: (progress, tokens, elapsed) =>
    set((state) => ({
      currentWorkflow: state.currentWorkflow
        ? {
            ...state.currentWorkflow,
            progress,
            tokenCount: tokens,
            elapsedTime: elapsed,
          }
        : null,
    })),

  setUploading: (isUploading) => set({ isUploading }),
  
  setStarting: (isStarting) => set({ isStarting }),

  reset: () => set(initialState),
}));
```

---

## Phase 3: Global Layout Components

### 3.1 Root Layout

**File:** `src/app/layout.tsx`

```typescript
import type { Metadata } from 'next';
import { Inter, JetBrains_Mono } from 'next/font/google';
import './globals.css';
import { Header } from '@/components/layout/Header';
import { Toaster } from '@/components/ui/toaster';
import { QueryProvider } from '@/components/providers/QueryProvider';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });
const jetbrainsMono = JetBrains_Mono({ 
  subsets: ['latin'], 
  variable: '--font-mono' 
});

export const metadata: Metadata = {
  title: 'ReqDecompose AI',
  description: 'AI-powered requirements decomposition',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} ${jetbrainsMono.variable} font-sans`}>
        <QueryProvider>
          <div className="min-h-screen bg-background">
            <Header />
            <main>{children}</main>
          </div>
          <Toaster />
        </QueryProvider>
      </body>
    </html>
  );
}
```

### 3.2 Query Provider

**File:** `src/components/providers/QueryProvider.tsx`

```typescript
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';

export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000,
            retry: 1,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}
```

### 3.3 Header Component

**File:** `src/components/layout/Header.tsx`

```typescript
'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Download, Plus, Bell } from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { label: 'Dashboard', href: '/dashboard' },
  { label: 'Projects', href: '/projects' },
  { label: 'Settings', href: '/settings' },
];

export function Header() {
  const pathname = usePathname();
  const showExport = pathname.startsWith('/results');

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur">
      <div className="container flex h-14 items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-6">
          <Link href="/" className="flex items-center gap-2">
            <div className="h-8 w-8 rounded bg-accent-blue flex items-center justify-center">
              <svg
                className="h-5 w-5 text-white"
                viewBox="0 0 24 24"
                fill="currentColor"
              >
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
              </svg>
            </div>
            <span className="font-semibold text-foreground">ReqDecompose AI</span>
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  'px-3 py-2 text-sm font-medium rounded-md transition-colors',
                  pathname === item.href
                    ? 'text-foreground bg-background-tertiary'
                    : 'text-foreground-secondary hover:text-foreground hover:bg-background-tertiary'
                )}
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-3">
          {showExport && (
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
          )}
          
          <Button asChild>
            <Link href="/upload">
              <Plus className="h-4 w-4 mr-2" />
              New Workflow
            </Link>
          </Button>

          <Button variant="ghost" size="icon" className="hidden md:flex">
            <Bell className="h-5 w-5" />
          </Button>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                <Avatar className="h-8 w-8">
                  <AvatarImage src="/avatar.png" alt="User" />
                  <AvatarFallback>U</AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem>Profile</DropdownMenuItem>
              <DropdownMenuItem>Settings</DropdownMenuItem>
              <DropdownMenuItem>Sign out</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}
```

### 3.4 Breadcrumb Component

**File:** `src/components/layout/Breadcrumb.tsx`

```typescript
import Link from 'next/link';
import { ChevronRight } from 'lucide-react';

interface BreadcrumbItem {
  label: string;
  href?: string;
}

interface BreadcrumbProps {
  items: BreadcrumbItem[];
}

export function Breadcrumb({ items }: BreadcrumbProps) {
  return (
    <nav className="flex items-center gap-1 text-sm text-foreground-secondary mb-4">
      {items.map((item, index) => (
        <div key={index} className="flex items-center gap-1">
          {index > 0 && <ChevronRight className="h-4 w-4" />}
          {item.href ? (
            <Link
              href={item.href}
              className="hover:text-foreground transition-colors"
            >
              {item.label}
            </Link>
          ) : (
            <span className="text-foreground font-medium">{item.label}</span>
          )}
        </div>
      ))}
    </nav>
  );
}
```

---

## Phase 4: Landing Page

### 4.1 Landing Page

**File:** `src/app/page.tsx`

```typescript
import { HeroSection } from '@/components/landing/HeroSection';
import { WorkflowCards } from '@/components/landing/WorkflowCards';
import { RecentWorkflows } from '@/components/landing/RecentWorkflows';

export default function LandingPage() {
  return (
    <div className="container py-8">
      <HeroSection />
      <WorkflowCards />
      <RecentWorkflows />
    </div>
  );
}
```

### 4.2 Hero Section

**File:** `src/components/landing/HeroSection.tsx`

```typescript
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Sparkles, ArrowRight } from 'lucide-react';

export function HeroSection() {
  return (
    <section className="py-12 md:py-20">
      <div className="grid md:grid-cols-2 gap-12 items-center">
        <div>
          <Badge variant="secondary" className="mb-4">
            <Sparkles className="h-3 w-3 mr-1" />
            AI-POWERED ENGINEERING
          </Badge>
          
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">
            Decompose Complex Requirements with AI Precision.
          </h1>
          
          <p className="text-lg text-foreground-secondary mb-8 max-w-md">
            Automate the engineering workflow. Transform raw PRDs and
            functional specs into validated, granular engineering tickets in
            seconds.
          </p>
          
          <div className="flex gap-4">
            <Button asChild size="lg">
              <Link href="/upload">
                Start New Workflow
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button variant="outline" size="lg">
              View Demo
            </Button>
          </div>
        </div>
        
        <div className="relative">
          {/* Hero visualization - can be replaced with actual animation */}
          <div className="aspect-video rounded-lg bg-gradient-to-br from-accent-blue/20 to-accent-purple/20 border border-border flex items-center justify-center">
            <div className="text-center">
              <div className="w-24 h-24 mx-auto rounded-full bg-accent-blue/30 animate-pulse" />
              <p className="mt-4 text-sm text-foreground-secondary font-mono">
                Processing PRD_v2.pdf...
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
```

### 4.3 Workflow Cards

**File:** `src/components/landing/WorkflowCards.tsx`

```typescript
import { Card, CardContent } from '@/components/ui/card';
import { FileText, Search, GitBranch, CheckCircle } from 'lucide-react';

const steps = [
  {
    icon: FileText,
    title: 'Extract',
    description: 'Ingest raw PRDs, functional specs, and legacy documentation automatically.',
    color: 'bg-accent-blue',
  },
  {
    icon: Search,
    title: 'Analyze',
    description: 'Identify core logic, edge cases, and hidden dependencies using semantic AI.',
    color: 'bg-accent-green',
  },
  {
    icon: GitBranch,
    title: 'Decompose',
    description: 'Break down high-level features into atomic, actionable engineering tasks.',
    color: 'bg-accent-purple',
  },
  {
    icon: CheckCircle,
    title: 'Validate',
    description: 'Cross-reference tasks against technical constraints and architectural standards.',
    color: 'bg-teal-500',
  },
];

export function WorkflowCards() {
  return (
    <section className="py-12">
      <h2 className="text-2xl font-semibold mb-2">The Workflow</h2>
      <p className="text-foreground-secondary mb-8">
        Our 4-step process ensures accuracy, depth, and technical consistency in every requirement analysis cycle.
      </p>
      
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {steps.map((step, index) => (
          <Card key={index} className="bg-background-secondary border-border">
            <CardContent className="pt-6">
              <div className={`w-10 h-10 rounded-lg ${step.color} flex items-center justify-center mb-4`}>
                <step.icon className="h-5 w-5 text-white" />
              </div>
              <h3 className="font-semibold mb-2">{step.title}</h3>
              <p className="text-sm text-foreground-secondary">
                {step.description}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  );
}
```

### 4.4 Recent Workflows

**File:** `src/components/landing/RecentWorkflows.tsx`

```typescript
'use client';

import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { FileText, ArrowRight } from 'lucide-react';
import { format } from 'date-fns';

const statusColors = {
  completed: 'bg-accent-green/20 text-accent-green',
  processing: 'bg-accent-blue/20 text-accent-blue',
  failed: 'bg-accent-red/20 text-accent-red',
  pending: 'bg-foreground-muted/20 text-foreground-muted',
  paused: 'bg-accent-yellow/20 text-accent-yellow',
};

export function RecentWorkflows() {
  const { data: workflows, isLoading, error } = useQuery({
    queryKey: ['recentWorkflows'],
    queryFn: () => api.getRecentWorkflows(5),
  });

  return (
    <section className="py-12">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-semibold">Recent Workflows</h2>
        <Button variant="ghost" asChild>
          <Link href="/workflows">
            View All
            <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
        </Button>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <Skeleton key={i} className="h-16 w-full" />
          ))}
        </div>
      ) : error ? (
        <div className="text-center py-8 text-foreground-secondary">
          Unable to load recent workflows.
          <Button variant="link" onClick={() => window.location.reload()}>
            Retry
          </Button>
        </div>
      ) : workflows?.length === 0 ? (
        <div className="text-center py-12 border border-dashed border-border rounded-lg">
          <p className="text-foreground-secondary mb-4">
            No workflows yet. Start your first workflow to see results here.
          </p>
          <Button asChild>
            <Link href="/upload">Start New Workflow</Link>
          </Button>
        </div>
      ) : (
        <div className="border border-border rounded-lg overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow className="bg-background-secondary">
                <TableHead>Project Name</TableHead>
                <TableHead>Source Doc</TableHead>
                <TableHead>Date Created</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {workflows?.map((workflow) => (
                <TableRow key={workflow.id} className="hover:bg-background-tertiary">
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <FileText className="h-4 w-4 text-foreground-muted" />
                      <span className="font-medium">{workflow.projectName}</span>
                    </div>
                  </TableCell>
                  <TableCell className="font-mono text-sm text-foreground-secondary">
                    {workflow.sourceDocument}
                  </TableCell>
                  <TableCell className="text-foreground-secondary">
                    {format(new Date(workflow.createdAt), 'MMM d, yyyy')}
                  </TableCell>
                  <TableCell>
                    <Badge className={statusColors[workflow.status]}>
                      {workflow.status}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {workflow.status === 'completed' && (
                      <Link
                        href={`/results/${workflow.id}`}
                        className="text-accent-blue hover:underline text-sm"
                      >
                        View
                      </Link>
                    )}
                    {workflow.status === 'processing' && (
                      <Link
                        href={`/run/${workflow.id}`}
                        className="text-accent-blue hover:underline text-sm"
                      >
                        Cancel
                      </Link>
                    )}
                    {workflow.status === 'failed' && (
                      <Link
                        href={`/upload?retry=${workflow.id}`}
                        className="text-accent-blue hover:underline text-sm"
                      >
                        Retry
                      </Link>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </section>
  );
}
```

---

## Phase 5: Upload & Configure Page

### 5.1 Upload Page

**File:** `src/app/upload/page.tsx`

```typescript
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Breadcrumb } from '@/components/layout/Breadcrumb';
import { FileUploader } from '@/components/upload/FileUploader';
import { ConfigurationPanel } from '@/components/upload/ConfigurationPanel';
import { useWorkflowStore } from '@/stores/workflowStore';
import { api } from '@/lib/api';
import { useToast } from '@/components/ui/use-toast';
import { WorkflowConfig, Domain, ReviewMode, AnalysisMode } from '@/types';

export default function UploadPage() {
  const router = useRouter();
  const { toast } = useToast();
  const { setCurrentWorkflow, setUploading, isUploading } = useWorkflowStore();
  
  const [mainFile, setMainFile] = useState<File | null>(null);
  const [contextFiles, setContextFiles] = useState<File[]>([]);
  const [config, setConfig] = useState<WorkflowConfig>({
    targetSubsystem: '',
    domain: 'generic',
    reviewMode: 'before',
    analysisMode: 'standard',
  });

  const canStart = mainFile && config.targetSubsystem.trim().length > 0;

  const handleStartDecomposition = async () => {
    if (!mainFile || !canStart) return;

    setUploading(true);
    
    try {
      // Upload document and create workflow
      const uploadResponse = await api.uploadDocument(
        mainFile,
        config,
        contextFiles.length > 0 ? contextFiles : undefined
      );

      // Start workflow execution
      const startResponse = await api.startWorkflow(uploadResponse.workflowId);
      
      // Get initial workflow state
      const workflow = await api.getWorkflowStatus(uploadResponse.workflowId);
      setCurrentWorkflow(workflow);

      // Navigate to run page
      router.push(`/run/${uploadResponse.workflowId}`);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to start workflow. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="container py-8">
      <Breadcrumb
        items={[
          { label: 'Projects', href: '/projects' },
          { label: 'New Workflow' },
        ]}
      />

      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Upload & Configure</h1>
        <p className="text-foreground-secondary">
          Import your requirements document and configure the AI analysis parameters to begin decomposition.
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Left Column - Upload */}
        <div className="space-y-6">
          <FileUploader
            label="Specification Document"
            file={mainFile}
            onFileChange={setMainFile}
            accept={{
              'application/pdf': ['.pdf'],
              'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
              'text/plain': ['.txt'],
            }}
            maxSize={20 * 1024 * 1024} // 20MB
          />
          
          <FileUploader
            label="Additional Context / Reference Material"
            files={contextFiles}
            onFilesChange={setContextFiles}
            multiple
            collapsible
            defaultCollapsed
          />
        </div>

        {/* Right Column - Configuration */}
        <ConfigurationPanel
          config={config}
          onConfigChange={setConfig}
          onStart={handleStartDecomposition}
          canStart={canStart}
          isLoading={isUploading}
        />
      </div>
    </div>
  );
}
```

### 5.2 File Uploader Component

**File:** `src/components/upload/FileUploader.tsx`

```typescript
'use client';

import { useCallback, useState } from 'react';
import { useDropzone, Accept } from 'react-dropzone';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  Upload, 
  FileText, 
  X, 
  ChevronDown, 
  ChevronUp,
  AlertCircle 
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface FileUploaderProps {
  label: string;
  file?: File | null;
  files?: File[];
  onFileChange?: (file: File | null) => void;
  onFilesChange?: (files: File[]) => void;
  multiple?: boolean;
  accept?: Accept;
  maxSize?: number;
  collapsible?: boolean;
  defaultCollapsed?: boolean;
}

export function FileUploader({
  label,
  file,
  files = [],
  onFileChange,
  onFilesChange,
  multiple = false,
  accept,
  maxSize = 20 * 1024 * 1024,
  collapsible = false,
  defaultCollapsed = false,
}: FileUploaderProps) {
  const [isCollapsed, setIsCollapsed] = useState(defaultCollapsed);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(
    (acceptedFiles: File[], rejectedFiles: any[]) => {
      setError(null);

      if (rejectedFiles.length > 0) {
        const rejection = rejectedFiles[0];
        if (rejection.errors[0]?.code === 'file-too-large') {
          setError(`File exceeds ${Math.round(maxSize / 1024 / 1024)}MB limit`);
        } else if (rejection.errors[0]?.code === 'file-invalid-type') {
          setError('Unsupported file type');
        }
        return;
      }

      if (multiple) {
        onFilesChange?.([...files, ...acceptedFiles]);
      } else {
        onFileChange?.(acceptedFiles[0] || null);
      }
    },
    [multiple, files, onFileChange, onFilesChange, maxSize]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept,
    maxSize,
    multiple,
  });

  const removeFile = (index: number) => {
    if (multiple) {
      const newFiles = [...files];
      newFiles.splice(index, 1);
      onFilesChange?.(newFiles);
    } else {
      onFileChange?.(null);
    }
  };

  const currentFiles = multiple ? files : file ? [file] : [];

  const content = (
    <>
      {currentFiles.length === 0 ? (
        <div
          {...getRootProps()}
          className={cn(
            'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors',
            isDragActive
              ? 'border-accent-blue bg-accent-blue/10'
              : 'border-border hover:border-foreground-muted',
            error && 'border-accent-red'
          )}
        >
          <input {...getInputProps()} />
          <Upload className="h-12 w-12 mx-auto text-foreground-muted mb-4" />
          <p className="text-foreground mb-1">Click to upload or drag and drop</p>
          <p className="text-sm text-foreground-secondary">
            PDF, DOCX, or TXT (MAX. {Math.round(maxSize / 1024 / 1024)}MB)
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {currentFiles.map((f, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-3 bg-background-tertiary rounded-lg"
            >
              <div className="flex items-center gap-3">
                <FileText className="h-5 w-5 text-accent-blue" />
                <div>
                  <p className="text-sm font-medium">{f.name}</p>
                  <p className="text-xs text-foreground-secondary">
                    {(f.size / 1024).toFixed(1)} KB
                  </p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => removeFile(index)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          ))}
          {multiple && (
            <div
              {...getRootProps()}
              className="border border-dashed border-border rounded-lg p-4 text-center cursor-pointer hover:border-foreground-muted transition-colors"
            >
              <input {...getInputProps()} />
              <p className="text-sm text-foreground-secondary">
                Add more files
              </p>
            </div>
          )}
        </div>
      )}

      {error && (
        <div className="flex items-center gap-2 mt-2 text-accent-red text-sm">
          <AlertCircle className="h-4 w-4" />
          {error}
        </div>
      )}
    </>
  );

  if (collapsible) {
    return (
      <Card className="bg-background-secondary border-border">
        <CardHeader
          className="cursor-pointer"
          onClick={() => setIsCollapsed(!isCollapsed)}
        >
          <div className="flex items-center justify-between">
            <CardTitle className="text-base flex items-center gap-2">
              <FileText className="h-4 w-4" />
              {label}
            </CardTitle>
            {isCollapsed ? (
              <ChevronDown className="h-4 w-4" />
            ) : (
              <ChevronUp className="h-4 w-4" />
            )}
          </div>
        </CardHeader>
        {!isCollapsed && <CardContent>{content}</CardContent>}
      </Card>
    );
  }

  return (
    <Card className="bg-background-secondary border-border">
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          <FileText className="h-4 w-4" />
          {label}
        </CardTitle>
      </CardHeader>
      <CardContent>{content}</CardContent>
    </Card>
  );
}
```

### 5.3 Configuration Panel

**File:** `src/components/upload/ConfigurationPanel.tsx`

```typescript
'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { Settings2, Play, Zap, Settings } from 'lucide-react';
import { cn } from '@/lib/utils';
import { WorkflowConfig, Domain, ReviewMode, AnalysisMode } from '@/types';

interface ConfigurationPanelProps {
  config: WorkflowConfig;
  onConfigChange: (config: WorkflowConfig) => void;
  onStart: () => void;
  canStart: boolean;
  isLoading: boolean;
}

const domains: { value: Domain; label: string }[] = [
  { value: 'generic', label: 'Generic' },
  { value: 'aerospace', label: 'Aerospace' },
  { value: 'automotive', label: 'Automotive' },
  { value: 'rail', label: 'Rail' },
  { value: 'medical', label: 'Medical' },
  { value: 'software', label: 'Software' },
];

export function ConfigurationPanel({
  config,
  onConfigChange,
  onStart,
  canStart,
  isLoading,
}: ConfigurationPanelProps) {
  const updateConfig = (updates: Partial<WorkflowConfig>) => {
    onConfigChange({ ...config, ...updates });
  };

  return (
    <Card className="bg-background-secondary border-border">
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          <Settings2 className="h-4 w-4" />
          Configuration
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Target Subsystem */}
        <div className="space-y-2">
          <Label htmlFor="subsystem">Target Subsystem</Label>
          <Input
            id="subsystem"
            placeholder="e.g., Propulsion Control Unit"
            value={config.targetSubsystem}
            onChange={(e) => updateConfig({ targetSubsystem: e.target.value })}
            className="bg-background-tertiary border-border"
          />
        </div>

        {/* Domain */}
        <div className="space-y-2">
          <Label htmlFor="domain">Domain</Label>
          <Select
            value={config.domain}
            onValueChange={(value: Domain) => updateConfig({ domain: value })}
          >
            <SelectTrigger className="bg-background-tertiary border-border">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {domains.map((domain) => (
                <SelectItem key={domain.value} value={domain.value}>
                  {domain.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Human-in-the-Loop Review */}
        <div className="space-y-2">
          <Label>Human-in-the-Loop Review</Label>
          <div className="flex gap-2">
            <Button
              type="button"
              variant={config.reviewMode === 'before' ? 'default' : 'outline'}
              className="flex-1"
              onClick={() => updateConfig({ reviewMode: 'before' })}
            >
              Review Before
            </Button>
            <Button
              type="button"
              variant={config.reviewMode === 'after' ? 'default' : 'outline'}
              className="flex-1"
              onClick={() => updateConfig({ reviewMode: 'after' })}
            >
              Review After
            </Button>
          </div>
          <p className="text-xs text-foreground-secondary">
            {config.reviewMode === 'before'
              ? '"Review Before" allows you to approve the component breakdown structure before full requirement generation.'
              : '"Review After" lets you review and edit generated requirements before finalizing.'}
          </p>
        </div>

        {/* Analysis Mode */}
        <div className="space-y-2">
          <Label>Analysis Mode</Label>
          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => updateConfig({ analysisMode: 'standard' })}
              className={cn(
                'p-4 rounded-lg border text-left transition-colors',
                config.analysisMode === 'standard'
                  ? 'border-accent-blue bg-accent-blue/10'
                  : 'border-border bg-background-tertiary hover:border-foreground-muted'
              )}
            >
              <div className="flex items-center gap-2 mb-1">
                <Zap className="h-4 w-4" />
                <span className="font-medium">Standard</span>
              </div>
              <p className="text-xs text-foreground-secondary">
                Optimized for speed. Single pass analysis.
              </p>
            </button>
            <button
              type="button"
              onClick={() => updateConfig({ analysisMode: 'thorough' })}
              className={cn(
                'p-4 rounded-lg border text-left transition-colors',
                config.analysisMode === 'thorough'
                  ? 'border-accent-blue bg-accent-blue/10'
                  : 'border-border bg-background-tertiary hover:border-foreground-muted'
              )}
            >
              <div className="flex items-center gap-2 mb-1">
                <Settings className="h-4 w-4" />
                <span className="font-medium">Thorough</span>
              </div>
              <p className="text-xs text-foreground-secondary">
                Recursive ISO/IEEE compliance checks.
              </p>
            </button>
          </div>
        </div>

        {/* Thorough Mode Options */}
        {config.analysisMode === 'thorough' && (
          <div className="space-y-4 p-4 bg-background-tertiary rounded-lg">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label>Quality Threshold</Label>
                <span className="text-sm text-foreground-secondary">
                  {((config.qualityThreshold || 0.85) * 100).toFixed(0)}%
                </span>
              </div>
              <Slider
                value={[(config.qualityThreshold || 0.85) * 100]}
                onValueChange={([value]) =>
                  updateConfig({ qualityThreshold: value / 100 })
                }
                min={70}
                max={95}
                step={5}
              />
            </div>
            <div className="space-y-2">
              <Label>Max Iterations</Label>
              <Select
                value={String(config.maxIterations || 3)}
                onValueChange={(value) =>
                  updateConfig({ maxIterations: parseInt(value) })
                }
              >
                <SelectTrigger className="bg-background border-border">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {[1, 2, 3, 4, 5].map((n) => (
                    <SelectItem key={n} value={String(n)}>
                      {n} iteration{n > 1 ? 's' : ''}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        )}

        {/* Start Button */}
        <Button
          className="w-full"
          size="lg"
          onClick={onStart}
          disabled={!canStart || isLoading}
        >
          {isLoading ? (
            <>
              <span className="animate-spin mr-2">⏳</span>
              Starting...
            </>
          ) : (
            <>
              <Play className="h-4 w-4 mr-2" />
              Start Decomposition
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
}
```

---

## Phase 6: Run Progress Page

*[Implementation continues with Run Progress page components including PipelineVisualization, LogPanel, HumanReviewPanel, and SSE integration]*

---

## Phase 7: Dashboard / Results Page

*[Implementation continues with Results page components including SummaryCards, QualityBreakdown, RequirementsTable, TraceabilityPanel, and QualityIssuesPanel]*

---

## Phase 8: Integration & Testing

### 8.1 Environment Variables

**File:** `.env.local`

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 8.2 Testing Checklist

- [ ] Landing page renders correctly
- [ ] File upload accepts PDF, DOCX, TXT
- [ ] Configuration options update correctly
- [ ] Start button disabled until requirements met
- [ ] Run page receives SSE events
- [ ] Pipeline visualization updates in real-time
- [ ] Human review panel appears when triggered
- [ ] Results page displays all metrics
- [ ] Requirements table filters and sorts
- [ ] Export downloads files correctly

### 8.3 Build & Deploy

```bash
# Development
npm run dev

# Build
npm run build

# Production
npm start

# Lint
npm run lint
```

---

## Implementation Order Summary

1. **Phase 1:** Project setup, dependencies, Tailwind config
2. **Phase 2:** Types, API client, SSE utilities, Zustand store
3. **Phase 3:** Global layout (Header, Breadcrumb)
4. **Phase 4:** Landing page (Hero, WorkflowCards, RecentWorkflows)
5. **Phase 5:** Upload page (FileUploader, ConfigurationPanel)
6. **Phase 6:** Run page (Pipeline, Logs, Human Review)
7. **Phase 7:** Results page (Summary, Quality, Table, Export)
8. **Phase 8:** Integration testing and deployment

---

## Notes for Claude Code

1. **Follow the component structure exactly** — files should be created in the specified locations
2. **Use shadcn/ui components** — install via `npx shadcn@latest add [component]`
3. **Dark theme is default** — all colors should use the custom tokens defined in Tailwind config
4. **API integration** — the backend API endpoints follow the pattern in `src/lib/api.ts`
5. **State management** — use Zustand for client state, TanStack Query for server state
6. **SSE handling** — use the `SSEClient` class for real-time updates on the Run page

---

*End of Implementation Plan*
