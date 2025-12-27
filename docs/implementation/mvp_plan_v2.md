# Requirements Decomposition System - Next.js Web Application MVP Plan

**Project:** AI-Accelerated Requirements Engineering Web Application
**Target:** Full-stack web application with real-time workflow monitoring
**Timeline:** 6-8 weeks to working MVP
**Author:** Michael Sweatt
**Last Updated:** December 4, 2025

---

## Executive Summary

This plan outlines the implementation of a modern web application for the Requirements Decomposition System, building upon the existing Python/LangGraph backend. The MVP features a Next.js frontend with real-time progress monitoring, interactive human review, and professional results visualization.

**Key Design Decisions:**
- **Backend:** Keep existing Python/LangGraph code, wrap with FastAPI for REST + WebSocket API
- **Frontend:** Next.js 14+ with App Router, React Server Components, TypeScript
- **Real-time Updates:** Server-Sent Events (SSE) for workflow progress streaming
- **State Management:** Zustand for client state, React Query for server state
- **UI Components:** shadcn/ui + Tailwind CSS for professional design
- **File Handling:** Direct upload to backend, progress tracking for large files
- **Deployment:** Docker Compose for local dev, Railway/Vercel for cloud

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    NEXT.JS FRONTEND                         │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Upload    │  │   Monitor    │  │   Review     │      │
│  │   Page      │  │   Workflow   │  │   Results    │      │
│  └─────────────┘  └──────────────┘  └──────────────┘      │
│         │                 │                  │              │
│         └─────────────────┴──────────────────┘              │
│                          │                                  │
│                    API Client Layer                         │
│                   (React Query + SSE)                       │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/WebSocket
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  FASTAPI BACKEND                            │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │  REST API  │  │  SSE       │  │  File      │           │
│  │  Endpoints │  │  Streaming │  │  Manager   │           │
│  └────────────┘  └────────────┘  └────────────┘           │
│         │               │               │                   │
│         └───────────────┴───────────────┘                   │
│                          │                                  │
│              ┌───────────▼───────────┐                      │
│              │   Workflow Executor   │                      │
│              │  (Thread Pool/Celery) │                      │
│              └───────────┬───────────┘                      │
└──────────────────────────┬───────────────────────────────── │
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│           EXISTING PYTHON/LANGGRAPH ENGINE                  │
│  ┌─────────┐  ┌─────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Extract │→ │ Analyze │→ │ Decompose│→ │ Validate │    │
│  └─────────┘  └─────────┘  └──────────┘  └──────────┘    │
│                                                             │
│  Skills: requirements-extraction, system-analysis,          │
│          requirements-decomposition, quality-validation     │
│                                                             │
│  Agents: RequirementsAnalyst, SystemArchitect,             │
│          RequirementsEngineer, QualityAssurance            │
└─────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Frontend
- **Framework:** Next.js 14+ (App Router, RSC, TypeScript)
- **UI Library:** React 18+
- **Styling:** Tailwind CSS 3.4+
- **Components:** shadcn/ui (Radix UI primitives)
- **State Management:**
  - **Client State:** Zustand (lightweight, TypeScript-friendly)
  - **Server State:** TanStack Query (React Query v5)
- **Real-time:** EventSource API (Server-Sent Events)
- **File Upload:** react-dropzone + axios
- **Forms:** React Hook Form + Zod validation
- **Charts:** Recharts (quality metrics visualization)
- **Icons:** Lucide React
- **Markdown:** react-markdown + remark-gfm

### Backend
- **API Framework:** FastAPI 0.104+
- **ASGI Server:** Uvicorn
- **Task Queue:** Python threading (MVP), Celery + Redis (production)
- **SSE:** sse-starlette
- **File Storage:** Local filesystem (MVP), S3 (production)
- **Database:** SQLite (state persistence), PostgreSQL (production)
- **Existing Engine:** Python 3.11+ LangGraph workflow

### DevOps
- **Containerization:** Docker + Docker Compose
- **Frontend Deployment:** Vercel (recommended) or Railway
- **Backend Deployment:** Railway, Render, or AWS ECS
- **CI/CD:** GitHub Actions
- **Monitoring:** Sentry (errors), Plausible (analytics)

---

## Phase 0: Project Setup and Architecture (Week 1)

### Phase 0.1: Repository Structure (Days 1-2)

**New Directory Structure:**
```
req-decomp-web/
├── frontend/                    # Next.js application
│   ├── app/                    # App router pages
│   │   ├── layout.tsx          # Root layout
│   │   ├── page.tsx            # Home/dashboard
│   │   ├── upload/
│   │   │   └── page.tsx        # Upload specification
│   │   ├── workflow/
│   │   │   └── [id]/
│   │   │       └── page.tsx    # Monitor workflow
│   │   └── results/
│   │       └── [id]/
│   │           └── page.tsx    # View results
│   ├── components/             # React components
│   │   ├── ui/                 # shadcn components
│   │   ├── workflow/           # Workflow-specific
│   │   ├── upload/             # Upload components
│   │   └── results/            # Results components
│   ├── lib/                    # Utilities
│   │   ├── api.ts              # API client
│   │   ├── sse.ts              # SSE client
│   │   └── types.ts            # TypeScript types
│   ├── hooks/                  # Custom React hooks
│   │   ├── useWorkflow.ts      # Workflow state hook
│   │   └── useSSE.ts           # SSE connection hook
│   └── stores/                 # Zustand stores
│       └── workflowStore.ts    # Global workflow state
│
├── backend/                    # FastAPI wrapper
│   ├── app/
│   │   ├── main.py             # FastAPI app
│   │   ├── routers/
│   │   │   ├── workflows.py    # Workflow endpoints
│   │   │   ├── files.py        # File upload
│   │   │   └── sse.py          # SSE streaming
│   │   ├── services/
│   │   │   ├── workflow_executor.py  # Execute LangGraph
│   │   │   └── file_manager.py       # File handling
│   │   ├── models/
│   │   │   └── schemas.py      # Pydantic models
│   │   └── core/
│   │       ├── config.py       # Configuration
│   │       └── sse_manager.py  # SSE connection manager
│   └── requirements.txt        # Python dependencies
│
├── engine/                     # Existing Python/LangGraph code
│   ├── src/                    # (Keep existing structure)
│   ├── skills/                 # (Keep existing structure)
│   ├── config/                 # (Keep existing structure)
│   └── ...                     # (All existing files)
│
├── docker-compose.yml          # Local development setup
├── .env.example                # Environment template
└── README.md                   # Setup instructions
```

**Tasks:**
1. Create new `frontend/` directory with Next.js 14 setup
2. Create `backend/` directory for FastAPI wrapper
3. Move existing Python code to `engine/` directory
4. Set up Docker Compose for integrated development
5. Configure environment variables across services
6. Set up TypeScript configuration with strict mode
7. Initialize Git submodules/monorepo structure

**Success Criteria:**
- ✅ Next.js dev server runs on `localhost:3000`
- ✅ FastAPI server runs on `localhost:8000`
- ✅ Docker Compose starts all services together
- ✅ Hot reload works for both frontend and backend
- ✅ TypeScript compilation succeeds with strict mode

---

### Phase 0.2: FastAPI Backend Wrapper (Days 3-4)

**Implementation: `backend/app/main.py`**

```python
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import asyncio
import uuid
from typing import Dict
import sys
sys.path.append("../engine")

from src.workflow import create_decomposition_graph
from src.state import create_initial_state

app = FastAPI(title="Requirements Decomposition API")

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory workflow storage (use Redis in production)
workflows: Dict[str, dict] = {}
sse_connections: Dict[str, asyncio.Queue] = {}


@app.post("/api/workflows/upload")
async def upload_specification(
    file: UploadFile = File(...),
    subsystem: str = "",
    domain: str = "generic"
):
    """Upload specification and create workflow."""
    workflow_id = str(uuid.uuid4())

    # Save uploaded file
    file_path = f"/tmp/uploads/{workflow_id}_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Create workflow state
    workflows[workflow_id] = {
        "id": workflow_id,
        "status": "pending",
        "file_path": file_path,
        "subsystem": subsystem,
        "domain": domain,
        "progress": {}
    }

    return {"workflow_id": workflow_id, "status": "pending"}


@app.post("/api/workflows/{workflow_id}/start")
async def start_workflow(
    workflow_id: str,
    background_tasks: BackgroundTasks
):
    """Start workflow execution in background."""
    if workflow_id not in workflows:
        return {"error": "Workflow not found"}, 404

    workflows[workflow_id]["status"] = "running"

    # Execute workflow in background
    background_tasks.add_task(execute_workflow, workflow_id)

    return {"workflow_id": workflow_id, "status": "running"}


@app.get("/api/workflows/{workflow_id}/stream")
async def stream_workflow_progress(workflow_id: str):
    """Stream workflow progress via Server-Sent Events."""
    if workflow_id not in workflows:
        return {"error": "Workflow not found"}, 404

    # Create SSE queue for this client
    queue = asyncio.Queue()
    sse_connections[workflow_id] = queue

    async def event_generator():
        try:
            while True:
                # Wait for events from workflow executor
                event = await queue.get()
                yield event

                # Stop streaming when complete
                if event.get("event") == "complete":
                    break
        finally:
            # Clean up connection
            if workflow_id in sse_connections:
                del sse_connections[workflow_id]

    return EventSourceResponse(event_generator())


@app.get("/api/workflows/{workflow_id}/status")
async def get_workflow_status(workflow_id: str):
    """Get current workflow status."""
    if workflow_id not in workflows:
        return {"error": "Workflow not found"}, 404

    return workflows[workflow_id]


async def execute_workflow(workflow_id: str):
    """Execute LangGraph workflow with progress updates."""
    workflow_data = workflows[workflow_id]

    try:
        # Send start event
        await send_sse_event(workflow_id, {
            "event": "started",
            "data": {"node": "extract", "status": "running"}
        })

        # Create initial state
        initial_state = create_initial_state(
            spec_document_path=workflow_data["file_path"],
            target_subsystem=workflow_data["subsystem"],
            domain_name=workflow_data["domain"]
        )

        # Create graph
        graph = create_decomposition_graph()

        # Execute with streaming
        async for event in graph.astream(initial_state):
            # Send progress update
            await send_sse_event(workflow_id, {
                "event": "progress",
                "data": event
            })

            # Update workflow storage
            workflows[workflow_id]["progress"] = event

        # Mark complete
        workflows[workflow_id]["status"] = "completed"
        await send_sse_event(workflow_id, {
            "event": "complete",
            "data": {"status": "completed"}
        })

    except Exception as e:
        workflows[workflow_id]["status"] = "error"
        workflows[workflow_id]["error"] = str(e)

        await send_sse_event(workflow_id, {
            "event": "error",
            "data": {"error": str(e)}
        })


async def send_sse_event(workflow_id: str, event: dict):
    """Send SSE event to connected clients."""
    if workflow_id in sse_connections:
        await sse_connections[workflow_id].put(event)
```

**Tasks:**
1. Implement FastAPI app with CORS middleware
2. Create file upload endpoint
3. Implement SSE streaming for progress updates
4. Integrate with existing LangGraph workflow
5. Add error handling and logging
6. Create Pydantic schemas for API contracts
7. Write API documentation with Swagger/OpenAPI

**Success Criteria:**
- ✅ File upload endpoint accepts .docx, .pdf, .txt files
- ✅ Workflow execution starts in background
- ✅ SSE stream sends real-time progress updates
- ✅ API documentation available at `/docs`
- ✅ CORS allows Next.js frontend access

---

### Phase 0.3: Next.js Frontend Foundation (Days 5-7)

**Implementation: Frontend Core Setup**

```bash
# Initialize Next.js with TypeScript
npx create-next-app@latest frontend \
  --typescript \
  --tailwind \
  --app \
  --src-dir \
  --import-alias "@/*"

# Install dependencies
cd frontend
npm install \
  @tanstack/react-query \
  zustand \
  axios \
  react-dropzone \
  react-hook-form \
  zod \
  @hookform/resolvers \
  lucide-react \
  recharts \
  react-markdown \
  remark-gfm

# Install shadcn/ui
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card input label progress textarea tabs table badge alert
```

**TypeScript Types: `frontend/lib/types.ts`**

```typescript
export interface WorkflowState {
  id: string;
  status: 'pending' | 'running' | 'completed' | 'error';
  filePath: string;
  subsystem: string;
  domain: string;
  progress: {
    currentNode?: string;
    extractedReqs?: number;
    qualityScore?: number;
    iterationCount?: number;
  };
  error?: string;
  results?: WorkflowResults;
}

export interface WorkflowResults {
  requirements: Requirement[];
  qualityMetrics: QualityMetrics;
  traceabilityMatrix: TraceabilityMatrix;
}

export interface Requirement {
  id: string;
  text: string;
  type: 'functional' | 'performance' | 'constraint' | 'interface';
  parentId?: string;
  subsystem: string;
  acceptanceCriteria?: string;
  rationale?: string;
}

export interface QualityMetrics {
  overallScore: number;
  completeness: number;
  clarity: number;
  testability: number;
  traceability: number;
  domainCompliance?: number;
  issues: QualityIssue[];
}

export interface QualityIssue {
  requirementId: string;
  severity: 'critical' | 'major' | 'minor';
  category: string;
  description: string;
  suggestion: string;
}

export interface SSEEvent {
  event: 'started' | 'progress' | 'complete' | 'error';
  data: any;
}
```

**API Client: `frontend/lib/api.ts`**

```typescript
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const workflowAPI = {
  uploadFile: async (
    file: File,
    subsystem: string,
    domain: string = 'generic'
  ) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('subsystem', subsystem);
    formData.append('domain', domain);

    const { data } = await api.post('/api/workflows/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  startWorkflow: async (workflowId: string) => {
    const { data } = await api.post(`/api/workflows/${workflowId}/start`);
    return data;
  },

  getWorkflowStatus: async (workflowId: string) => {
    const { data } = await api.get(`/api/workflows/${workflowId}/status`);
    return data;
  },

  streamWorkflowProgress: (workflowId: string) => {
    return new EventSource(
      `${API_BASE_URL}/api/workflows/${workflowId}/stream`
    );
  },
};
```

**SSE Hook: `frontend/hooks/useSSE.ts`**

```typescript
import { useEffect, useState } from 'react';
import { SSEEvent } from '@/lib/types';

export function useSSE(workflowId: string | null) {
  const [events, setEvents] = useState<SSEEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!workflowId) return;

    const eventSource = new EventSource(
      `${process.env.NEXT_PUBLIC_API_URL}/api/workflows/${workflowId}/stream`
    );

    eventSource.onopen = () => {
      setIsConnected(true);
      setError(null);
    };

    eventSource.onmessage = (event) => {
      const data: SSEEvent = JSON.parse(event.data);
      setEvents((prev) => [...prev, data]);

      if (data.event === 'complete' || data.event === 'error') {
        eventSource.close();
        setIsConnected(false);
      }
    };

    eventSource.onerror = () => {
      setError('Connection lost');
      setIsConnected(false);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [workflowId]);

  return { events, isConnected, error };
}
```

**Tasks:**
1. Set up Next.js project with TypeScript
2. Install and configure dependencies
3. Create TypeScript type definitions
4. Implement API client with axios
5. Create SSE connection hook
6. Set up React Query for server state
7. Configure Tailwind CSS and shadcn/ui

**Success Criteria:**
- ✅ Next.js dev server runs without errors
- ✅ TypeScript compiles with strict mode
- ✅ API client can communicate with backend
- ✅ SSE hook receives real-time events
- ✅ shadcn/ui components render correctly

---

## Phase 1: Core UI Pages (Week 2)

### Phase 1.1: Upload Page (Days 8-10)

**Implementation: `frontend/app/upload/page.tsx`**

```typescript
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card } from '@/components/ui/card';
import { FileUploader } from '@/components/upload/FileUploader';
import { workflowAPI } from '@/lib/api';

const formSchema = z.object({
  file: z.instanceof(File),
  subsystem: z.string().min(1, 'Subsystem name is required'),
  domain: z.string().default('generic'),
});

type FormData = z.infer<typeof formSchema>;

export default function UploadPage() {
  const router = useRouter();
  const [isUploading, setIsUploading] = useState(false);

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
  });

  const onSubmit = async (data: FormData) => {
    setIsUploading(true);

    try {
      const { workflow_id } = await workflowAPI.uploadFile(
        data.file,
        data.subsystem,
        data.domain
      );

      // Start workflow immediately
      await workflowAPI.startWorkflow(workflow_id);

      // Redirect to workflow monitoring page
      router.push(`/workflow/${workflow_id}`);
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Failed to upload file. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="container mx-auto py-10">
      <Card className="max-w-2xl mx-auto p-8">
        <h1 className="text-3xl font-bold mb-6">
          Upload Specification Document
        </h1>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div>
            <Label>Specification File</Label>
            <FileUploader
              onFileSelect={(file) => setValue('file', file)}
              accept={{
                'application/pdf': ['.pdf'],
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
                'text/plain': ['.txt'],
              }}
            />
            {errors.file && (
              <p className="text-sm text-red-500 mt-1">{errors.file.message}</p>
            )}
          </div>

          <div>
            <Label htmlFor="subsystem">Target Subsystem</Label>
            <Input
              id="subsystem"
              placeholder="e.g., Train Management, Navigation System"
              {...register('subsystem')}
            />
            {errors.subsystem && (
              <p className="text-sm text-red-500 mt-1">
                {errors.subsystem.message}
              </p>
            )}
          </div>

          <div>
            <Label htmlFor="domain">Domain (Optional)</Label>
            <select
              id="domain"
              className="w-full border rounded-md p-2"
              {...register('domain')}
            >
              <option value="generic">Generic</option>
              <option value="csx_dispatch">CSX Railway Dispatch</option>
            </select>
          </div>

          <Button type="submit" className="w-full" disabled={isUploading}>
            {isUploading ? 'Uploading...' : 'Start Decomposition'}
          </Button>
        </form>
      </Card>
    </div>
  );
}
```

**File Uploader Component: `frontend/components/upload/FileUploader.tsx`**

```typescript
'use client';

import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload } from 'lucide-react';

interface FileUploaderProps {
  onFileSelect: (file: File) => void;
  accept?: Record<string, string[]>;
}

export function FileUploader({ onFileSelect, accept }: FileUploaderProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        onFileSelect(acceptedFiles[0]);
      }
    },
    [onFileSelect]
  );

  const { getRootProps, getInputProps, isDragActive, acceptedFiles } =
    useDropzone({
      onDrop,
      accept,
      maxFiles: 1,
    });

  return (
    <div
      {...getRootProps()}
      className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
        isDragActive
          ? 'border-primary bg-primary/10'
          : 'border-gray-300 hover:border-primary'
      }`}
    >
      <input {...getInputProps()} />
      <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
      {acceptedFiles.length > 0 ? (
        <p className="text-sm font-medium">{acceptedFiles[0].name}</p>
      ) : isDragActive ? (
        <p className="text-sm">Drop the file here...</p>
      ) : (
        <div>
          <p className="text-sm font-medium mb-1">
            Drop your specification file here
          </p>
          <p className="text-xs text-gray-500">
            Supports PDF, DOCX, and TXT files
          </p>
        </div>
      )}
    </div>
  );
}
```

**Tasks:**
1. Create upload page with form
2. Implement file upload component with drag-and-drop
3. Add form validation with Zod
4. Integrate with backend upload API
5. Add loading states and error handling
6. Create domain selector dropdown
7. Test with various file types and sizes

**Success Criteria:**
- ✅ Drag-and-drop file upload works
- ✅ Form validation prevents invalid submissions
- ✅ File uploads successfully to backend
- ✅ Redirects to workflow page after upload
- ✅ Shows clear error messages on failure

---

### Phase 1.2: Workflow Monitoring Page (Days 11-13)

**Implementation: `frontend/app/workflow/[id]/page.tsx`**

```typescript
'use client';

import { use, useEffect } from 'react';
import { useSSE } from '@/hooks/useSSE';
import { WorkflowProgress } from '@/components/workflow/WorkflowProgress';
import { NodeStatus } from '@/components/workflow/NodeStatus';
import { Card } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2 } from 'lucide-react';

export default function WorkflowPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { events, isConnected, error } = useSSE(id);

  const currentEvent = events[events.length - 1];
  const isComplete = currentEvent?.event === 'complete';
  const hasError = currentEvent?.event === 'error';

  return (
    <div className="container mx-auto py-10">
      <h1 className="text-3xl font-bold mb-6">Workflow Progress</h1>

      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Progress Timeline */}
        <div className="lg:col-span-2">
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4">
              Decomposition Pipeline
            </h2>
            <WorkflowProgress events={events} />
          </Card>

          {/* Current Node Details */}
          {currentEvent && !isComplete && !hasError && (
            <Card className="p-6 mt-6">
              <div className="flex items-center gap-2 mb-4">
                <Loader2 className="h-5 w-5 animate-spin" />
                <h3 className="text-lg font-semibold">
                  Processing: {currentEvent.data.node}
                </h3>
              </div>
              <NodeStatus event={currentEvent} />
            </Card>
          )}

          {/* Completion Message */}
          {isComplete && (
            <Card className="p-6 mt-6 bg-green-50 border-green-200">
              <h3 className="text-lg font-semibold text-green-900">
                ✅ Workflow Complete!
              </h3>
              <p className="text-sm text-green-700 mt-2">
                Your requirements have been successfully decomposed.
              </p>
              <button
                className="mt-4 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                onClick={() => (window.location.href = `/results/${id}`)}
              >
                View Results
              </button>
            </Card>
          )}
        </div>

        {/* Metadata Sidebar */}
        <div>
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Workflow Info</h3>
            <dl className="space-y-2 text-sm">
              <div>
                <dt className="text-gray-500">Workflow ID</dt>
                <dd className="font-mono text-xs">{id}</dd>
              </div>
              <div>
                <dt className="text-gray-500">Status</dt>
                <dd>
                  <span
                    className={`inline-block px-2 py-1 rounded text-xs ${
                      isComplete
                        ? 'bg-green-100 text-green-800'
                        : hasError
                        ? 'bg-red-100 text-red-800'
                        : 'bg-blue-100 text-blue-800'
                    }`}
                  >
                    {isComplete ? 'Complete' : hasError ? 'Error' : 'Running'}
                  </span>
                </dd>
              </div>
              <div>
                <dt className="text-gray-500">Connection</dt>
                <dd>
                  <span
                    className={`inline-block w-2 h-2 rounded-full mr-2 ${
                      isConnected ? 'bg-green-500' : 'bg-gray-300'
                    }`}
                  />
                  {isConnected ? 'Connected' : 'Disconnected'}
                </dd>
              </div>
            </dl>
          </Card>
        </div>
      </div>
    </div>
  );
}
```

**Workflow Progress Component: `frontend/components/workflow/WorkflowProgress.tsx`**

```typescript
import { SSEEvent } from '@/lib/types';
import { Check, Loader2, AlertCircle } from 'lucide-react';

const WORKFLOW_NODES = [
  { id: 'extract', label: 'Extract Requirements', description: 'Parsing specification document' },
  { id: 'analyze', label: 'Analyze System', description: 'Developing decomposition strategy' },
  { id: 'decompose', label: 'Decompose Requirements', description: 'Generating subsystem requirements' },
  { id: 'validate', label: 'Validate Quality', description: 'Assessing requirement quality' },
];

export function WorkflowProgress({ events }: { events: SSEEvent[] }) {
  const getNodeStatus = (nodeId: string) => {
    const nodeEvents = events.filter((e) => e.data?.node === nodeId);
    if (nodeEvents.length === 0) return 'pending';

    const latest = nodeEvents[nodeEvents.length - 1];
    if (latest.event === 'error') return 'error';
    if (latest.data?.status === 'completed') return 'completed';
    return 'running';
  };

  return (
    <div className="space-y-6">
      {WORKFLOW_NODES.map((node, index) => {
        const status = getNodeStatus(node.id);

        return (
          <div key={node.id} className="flex items-start gap-4">
            {/* Status Icon */}
            <div
              className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
                status === 'completed'
                  ? 'bg-green-100'
                  : status === 'running'
                  ? 'bg-blue-100'
                  : status === 'error'
                  ? 'bg-red-100'
                  : 'bg-gray-100'
              }`}
            >
              {status === 'completed' && (
                <Check className="w-5 h-5 text-green-600" />
              )}
              {status === 'running' && (
                <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
              )}
              {status === 'error' && (
                <AlertCircle className="w-5 h-5 text-red-600" />
              )}
              {status === 'pending' && (
                <span className="w-3 h-3 rounded-full bg-gray-400" />
              )}
            </div>

            {/* Node Info */}
            <div className="flex-1">
              <h4 className="font-semibold text-sm">{node.label}</h4>
              <p className="text-xs text-gray-500">{node.description}</p>
            </div>

            {/* Connector Line */}
            {index < WORKFLOW_NODES.length - 1 && (
              <div className="absolute left-9 mt-10 w-0.5 h-6 bg-gray-300" />
            )}
          </div>
        );
      })}
    </div>
  );
}
```

**Tasks:**
1. Create workflow monitoring page
2. Implement real-time progress visualization
3. Create node status components
4. Add timeline/stepper UI for workflow stages
5. Display current node details
6. Handle completion and error states
7. Add metadata sidebar

**Success Criteria:**
- ✅ Real-time progress updates as workflow executes
- ✅ Clear visual indication of current node
- ✅ Completion state shows "View Results" button
- ✅ Error states display clearly
- ✅ SSE connection status visible

---

### Phase 1.3: Results Page (Days 14-16)

**Implementation: `frontend/app/results/[id]/page.tsx`**

```typescript
'use client';

import { use } from 'react';
import { useQuery } from '@tanstack/react-query';
import { workflowAPI } from '@/lib/api';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { RequirementsTable } from '@/components/results/RequirementsTable';
import { QualityMetricsChart } from '@/components/results/QualityMetricsChart';
import { TraceabilityMatrix } from '@/components/results/TraceabilityMatrix';
import { DownloadButton } from '@/components/results/DownloadButton';

export default function ResultsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  const { data: workflow, isLoading } = useQuery({
    queryKey: ['workflow', id],
    queryFn: () => workflowAPI.getWorkflowStatus(id),
  });

  if (isLoading) {
    return <div>Loading results...</div>;
  }

  const { results } = workflow;

  return (
    <div className="container mx-auto py-10">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Decomposition Results</h1>
        <DownloadButton workflowId={id} results={results} />
      </div>

      <Tabs defaultValue="requirements" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="requirements">Requirements</TabsTrigger>
          <TabsTrigger value="quality">Quality Metrics</TabsTrigger>
          <TabsTrigger value="traceability">Traceability</TabsTrigger>
        </TabsList>

        <TabsContent value="requirements">
          <Card className="p-6">
            <h2 className="text-2xl font-semibold mb-4">
              Subsystem Requirements ({results.requirements.length})
            </h2>
            <RequirementsTable requirements={results.requirements} />
          </Card>
        </TabsContent>

        <TabsContent value="quality">
          <Card className="p-6">
            <h2 className="text-2xl font-semibold mb-4">Quality Assessment</h2>
            <QualityMetricsChart metrics={results.qualityMetrics} />
          </Card>
        </TabsContent>

        <TabsContent value="traceability">
          <Card className="p-6">
            <h2 className="text-2xl font-semibold mb-4">
              Traceability Matrix
            </h2>
            <TraceabilityMatrix matrix={results.traceabilityMatrix} />
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
```

**Quality Metrics Chart: `frontend/components/results/QualityMetricsChart.tsx`**

```typescript
import { QualityMetrics } from '@/lib/types';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
} from 'recharts';

export function QualityMetricsChart({ metrics }: { metrics: QualityMetrics }) {
  const data = [
    { dimension: 'Completeness', score: metrics.completeness * 100 },
    { dimension: 'Clarity', score: metrics.clarity * 100 },
    { dimension: 'Testability', score: metrics.testability * 100 },
    { dimension: 'Traceability', score: metrics.traceability * 100 },
  ];

  if (metrics.domainCompliance !== undefined) {
    data.push({
      dimension: 'Domain Compliance',
      score: metrics.domainCompliance * 100,
    });
  }

  return (
    <div className="space-y-6">
      {/* Overall Score */}
      <div className="text-center">
        <div className="text-5xl font-bold text-green-600">
          {(metrics.overallScore * 100).toFixed(0)}%
        </div>
        <p className="text-sm text-gray-500 mt-2">Overall Quality Score</p>
      </div>

      {/* Radar Chart */}
      <ResponsiveContainer width="100%" height={400}>
        <RadarChart data={data}>
          <PolarGrid />
          <PolarAngleAxis dataKey="dimension" />
          <PolarRadiusAxis domain={[0, 100]} />
          <Radar
            name="Quality"
            dataKey="score"
            stroke="#22c55e"
            fill="#22c55e"
            fillOpacity={0.5}
          />
        </RadarChart>
      </ResponsiveContainer>

      {/* Issues List */}
      {metrics.issues.length > 0 && (
        <div className="mt-8">
          <h3 className="text-lg font-semibold mb-4">
            Quality Issues ({metrics.issues.length})
          </h3>
          <div className="space-y-3">
            {metrics.issues.map((issue, index) => (
              <div
                key={index}
                className="p-4 border rounded-lg bg-yellow-50 border-yellow-200"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-xs font-semibold uppercase text-yellow-800">
                      {issue.severity}
                    </span>
                    <h4 className="font-medium mt-1">{issue.description}</h4>
                    <p className="text-sm text-gray-600 mt-1">
                      Requirement: {issue.requirementId}
                    </p>
                  </div>
                </div>
                <div className="mt-2 text-sm text-green-700">
                  💡 {issue.suggestion}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
```

**Tasks:**
1. Create results page with tabbed interface
2. Implement requirements table with filtering/sorting
3. Create quality metrics visualization (radar chart)
4. Build traceability matrix component
5. Add download functionality (PDF, Markdown, CSV)
6. Implement search and filtering
7. Add print-friendly styling

**Success Criteria:**
- ✅ Requirements displayed in sortable table
- ✅ Quality metrics shown in interactive chart
- ✅ Traceability matrix shows parent-child relationships
- ✅ Download generates formatted documents
- ✅ Results are responsive and print-friendly

---

## Phase 2: Advanced Features (Week 3-4)

### Phase 2.1: Human Review Interface (Days 17-19)

**Implementation: Human Review Modal**

```typescript
'use client';

import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { QualityMetrics, Requirement } from '@/lib/types';

interface HumanReviewModalProps {
  open: boolean;
  onClose: () => void;
  requirements: Requirement[];
  qualityMetrics: QualityMetrics;
  onApprove: () => void;
  onRevise: (feedback: string) => void;
}

export function HumanReviewModal({
  open,
  onClose,
  requirements,
  qualityMetrics,
  onApprove,
  onRevise,
}: HumanReviewModalProps) {
  const [feedback, setFeedback] = useState('');

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Human Review Required</DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Quality Summary */}
          <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
            <h3 className="font-semibold mb-2">Quality Assessment</h3>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                Overall Score:{' '}
                <span className="font-bold">
                  {(qualityMetrics.overallScore * 100).toFixed(0)}%
                </span>
              </div>
              <div>
                Issues Found:{' '}
                <span className="font-bold">{qualityMetrics.issues.length}</span>
              </div>
            </div>
          </div>

          {/* Requirements Preview */}
          <div>
            <h3 className="font-semibold mb-2">
              Generated Requirements ({requirements.length})
            </h3>
            <div className="max-h-64 overflow-y-auto border rounded-lg">
              {requirements.slice(0, 10).map((req) => (
                <div key={req.id} className="p-3 border-b last:border-b-0">
                  <div className="text-xs text-gray-500">{req.id}</div>
                  <div className="text-sm mt-1">{req.text}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Feedback Input */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Revision Guidance (Optional)
            </label>
            <Textarea
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="Provide specific feedback for improvement..."
              rows={4}
            />
          </div>

          {/* Actions */}
          <div className="flex gap-3 justify-end">
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button
              variant="secondary"
              onClick={() => onRevise(feedback)}
              disabled={!feedback.trim()}
            >
              Request Revision
            </Button>
            <Button onClick={onApprove} className="bg-green-600 hover:bg-green-700">
              Approve & Continue
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
```

**Tasks:**
1. Create human review modal component
2. Display quality metrics summary
3. Show requirements preview
4. Add feedback text area
5. Implement approve/revise actions
6. Integrate with workflow SSE stream
7. Update backend to handle human review decisions

**Success Criteria:**
- ✅ Modal triggers when workflow requires human review
- ✅ Shows clear quality assessment
- ✅ Allows detailed feedback input
- ✅ Approve continues workflow
- ✅ Revise sends feedback back to decompose node

---

### Phase 2.2: Domain Management UI (Days 20-22)

**Domain Selection Component:**

```typescript
'use client';

import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

const AVAILABLE_DOMAINS = [
  {
    id: 'generic',
    name: 'Generic',
    description: 'No domain-specific requirements',
    subsystems: [],
  },
  {
    id: 'csx_dispatch',
    name: 'CSX Railway Dispatch',
    description: 'Railway dispatch and train management system',
    subsystems: [
      { id: 'train_management', name: 'Train Management' },
      { id: 'track_control', name: 'Track Control' },
      { id: 'billing', name: 'Billing & Accounting' },
    ],
  },
];

export function DomainSelector({
  onSelect,
}: {
  onSelect: (domain: string, subsystem?: string) => void;
}) {
  const [selectedDomain, setSelectedDomain] = useState<string | null>(null);
  const [selectedSubsystem, setSelectedSubsystem] = useState<string | null>(
    null
  );

  const handleSelect = () => {
    if (selectedDomain) {
      onSelect(selectedDomain, selectedSubsystem || undefined);
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <h3 className="font-semibold mb-3">Select Domain</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {AVAILABLE_DOMAINS.map((domain) => (
            <Card
              key={domain.id}
              className={`p-4 cursor-pointer transition-all ${
                selectedDomain === domain.id
                  ? 'border-primary ring-2 ring-primary'
                  : 'hover:border-gray-400'
              }`}
              onClick={() => setSelectedDomain(domain.id)}
            >
              <h4 className="font-semibold">{domain.name}</h4>
              <p className="text-sm text-gray-500 mt-1">
                {domain.description}
              </p>
              {domain.subsystems.length > 0 && (
                <div className="mt-2">
                  <Badge variant="secondary">
                    {domain.subsystems.length} subsystems
                  </Badge>
                </div>
              )}
            </Card>
          ))}
        </div>
      </div>

      {/* Subsystem Selection */}
      {selectedDomain &&
        AVAILABLE_DOMAINS.find((d) => d.id === selectedDomain)?.subsystems
          .length! > 0 && (
          <div>
            <h3 className="font-semibold mb-3">Select Subsystem (Optional)</h3>
            <div className="grid grid-cols-2 gap-2">
              {AVAILABLE_DOMAINS.find((d) => d.id === selectedDomain)?.subsystems.map(
                (subsystem) => (
                  <Button
                    key={subsystem.id}
                    variant={
                      selectedSubsystem === subsystem.id ? 'default' : 'outline'
                    }
                    onClick={() => setSelectedSubsystem(subsystem.id)}
                  >
                    {subsystem.name}
                  </Button>
                )
              )}
            </div>
          </div>
        )}

      <Button onClick={handleSelect} disabled={!selectedDomain} className="w-full">
        Confirm Selection
      </Button>
    </div>
  );
}
```

**Tasks:**
1. Create domain selection interface
2. Fetch available domains from backend
3. Show subsystem options for selected domain
4. Display domain conventions preview
5. Integrate with upload workflow
6. Add domain info tooltips
7. Create domain management admin page (optional)

**Success Criteria:**
- ✅ Users can browse available domains
- ✅ Subsystem selection updates dynamically
- ✅ Domain context applied to workflow
- ✅ Domain compliance scored correctly
- ✅ 5-dimension quality metrics shown for domain-aware workflows

---

## Phase 3: Testing & Polish (Week 5)

### Phase 3.1: End-to-End Testing (Days 23-25)

**Test Scenarios:**

1. **Happy Path:** Upload → Extract → Analyze → Decompose → Validate → Complete
2. **Quality Gate Failure:** Trigger revision loop with feedback
3. **Human Review:** Approve or revise during validation
4. **Error Handling:** Invalid file, API timeout, LLM errors
5. **Domain-Aware:** CSX Railway domain with Train Management subsystem
6. **Large Files:** 100+ page PDF with 200+ requirements

**Integration Tests:**

```typescript
// frontend/__tests__/integration/workflow.test.ts
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { UploadPage } from '@/app/upload/page';

describe('Workflow Integration', () => {
  it('completes full workflow successfully', async () => {
    render(<UploadPage />);

    // Upload file
    const file = new File(['test content'], 'test.pdf', {
      type: 'application/pdf',
    });
    const input = screen.getByLabelText(/specification file/i);
    await userEvent.upload(input, file);

    // Enter subsystem
    const subsystemInput = screen.getByLabelText(/target subsystem/i);
    await userEvent.type(subsystemInput, 'Train Management');

    // Submit
    const submitButton = screen.getByRole('button', { name: /start decomposition/i });
    await userEvent.click(submitButton);

    // Wait for redirect to workflow page
    await waitFor(() => {
      expect(window.location.pathname).toContain('/workflow/');
    });

    // Verify progress updates
    await waitFor(() => {
      expect(screen.getByText(/extract requirements/i)).toBeInTheDocument();
    }, { timeout: 10000 });
  });
});
```

**Tasks:**
1. Write E2E tests for all user flows
2. Test SSE connection handling
3. Test error scenarios and recovery
4. Load test with concurrent workflows
5. Test file upload limits and validation
6. Cross-browser testing (Chrome, Firefox, Safari)
7. Mobile responsiveness testing

**Success Criteria:**
- ✅ All E2E tests pass
- ✅ No console errors during workflow
- ✅ SSE reconnects automatically on disconnect
- ✅ Handles 10+ concurrent workflows
- ✅ Works on mobile devices
- ✅ Load time < 3 seconds

---

### Phase 3.2: Performance Optimization (Days 26-27)

**Optimization Strategies:**

1. **Frontend:**
   - Code splitting with Next.js dynamic imports
   - Image optimization with next/image
   - React Query caching for API responses
   - Debounce SSE event processing
   - Virtualized tables for large result sets

2. **Backend:**
   - Redis caching for domain contexts
   - Connection pooling for database
   - Async task queue (Celery) for workflows
   - CDN for static assets
   - Gzip compression for API responses

3. **Database:**
   - Indexing for workflow queries
   - Archiving old workflow results
   - Read replicas for analytics

**Tasks:**
1. Profile frontend bundle size
2. Implement code splitting
3. Add Redis caching for backend
4. Optimize LLM API calls (batch when possible)
5. Add CDN configuration
6. Database query optimization
7. Load testing with k6/Artillery

**Success Criteria:**
- ✅ Frontend bundle size < 200KB (gzipped)
- ✅ Time to Interactive < 2 seconds
- ✅ API response time < 200ms (p95)
- ✅ Supports 100 concurrent users
- ✅ Workflow execution time unchanged

---

## Phase 4: Deployment (Week 6)

### Phase 4.1: Docker & Deployment (Days 28-30)

**Docker Compose: `docker-compose.yml`**

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - '3000:3000'
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - '8000:8000'
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - DATABASE_URL=postgresql://user:pass@postgres:5432/reqdecomp
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    volumes:
      - ./engine:/app/engine

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=reqdecomp
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - '6379:6379'

volumes:
  postgres_data:
```

**Frontend Dockerfile:**

```dockerfile
FROM node:20-alpine AS base

# Install dependencies
FROM base AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# Build application
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Production image
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000

ENV PORT 3000

CMD ["node", "server.js"]
```

**Backend Dockerfile:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app ./app
COPY ./engine ./engine

# Expose port
EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Tasks:**
1. Create Dockerfiles for frontend and backend
2. Set up Docker Compose for local development
3. Configure environment variables
4. Deploy frontend to Vercel
5. Deploy backend to Railway/Render
6. Set up PostgreSQL and Redis
7. Configure DNS and SSL certificates
8. Set up monitoring and logging

**Success Criteria:**
- ✅ Docker Compose starts all services
- ✅ Frontend accessible at public URL
- ✅ Backend API accessible and functional
- ✅ Database migrations run automatically
- ✅ SSL certificates configured
- ✅ Health checks passing

---

## MVP Feature Comparison

| Feature | CLI Version | Web Application |
|---------|-------------|-----------------|
| **File Upload** | Command-line argument | Drag-and-drop UI |
| **Progress Monitoring** | CLI logs | Real-time dashboard with SSE |
| **Human Review** | Terminal prompts | Interactive modal with rich UI |
| **Results Viewing** | Markdown files in outputs/ | Tabbed interface with charts |
| **Quality Metrics** | Text report | Interactive radar chart |
| **Traceability** | CSV matrix | Searchable table with filters |
| **Domain Selection** | CLI flag | Visual domain picker |
| **Error Handling** | Stack traces | User-friendly error messages |
| **Multiple Workflows** | Sequential execution | Concurrent with job queue |
| **Persistence** | SQLite checkpoints | PostgreSQL with full history |
| **Collaboration** | None | Share workflow URLs (future) |
| **Deployment** | Local Python install | Cloud-hosted web app |

---

## Success Metrics

### Technical
- ✅ **Uptime:** 99.9% availability
- ✅ **Performance:** < 2s page load, < 5min workflow execution
- ✅ **Scalability:** Handles 100+ concurrent workflows
- ✅ **Quality:** Same LangGraph quality as CLI version
- ✅ **Real-time:** < 500ms latency for SSE events

### User Experience
- ✅ **Usability:** Non-technical users can use without training
- ✅ **Accessibility:** WCAG 2.1 AA compliant
- ✅ **Mobile:** Fully responsive design
- ✅ **Reliability:** Automatic reconnection on network issues
- ✅ **Clarity:** Clear progress indication at all times

---

## Future Enhancements (Post-MVP)

1. **Authentication & Multi-tenancy**
   - User accounts with NextAuth.js
   - Team workspaces
   - Project management

2. **Advanced Features**
   - Requirement editing and refinement
   - Comparison between workflow runs
   - Export to DOORS/Polarion
   - PDF generation with branding
   - Email notifications

3. **Collaboration**
   - Real-time collaborative review
   - Comments and annotations
   - Approval workflows
   - Version history

4. **Analytics**
   - Quality trends dashboard
   - Cost analysis
   - Model performance comparison
   - Usage statistics

5. **Integrations**
   - Jira/Linear integration
   - GitHub/GitLab sync
   - Slack notifications
   - API for external tools

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| SSE connection drops | High | Auto-reconnect, status polling fallback |
| LLM API rate limits | High | Queue system, retries, fallback models |
| Large file handling | Medium | Stream parsing, chunking, progress indicators |
| Concurrent workflow limits | Medium | Job queue, user notifications |
| Browser compatibility | Low | Polyfills, progressive enhancement |

---

**END OF WEB APPLICATION IMPLEMENTATION PLAN**
