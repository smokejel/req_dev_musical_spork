# Requirements Decomposition System - Comprehensive Implementation Plan

**Project:** AI-Accelerated Requirements Engineering - Full-Stack Application
**Architecture:** Python/LangGraph Backend + Next.js Web Frontend
**Timeline:** 10-12 weeks to complete web application MVP
**Author:** Michael Sweatt
**Last Updated:** December 4, 2025
**Version:** 2.2 (Comprehensive Merged Plan)

---

## Executive Summary

This comprehensive plan outlines the complete implementation of an AI-powered requirements decomposition system, from foundational Python/LangGraph backend through to a modern web application interface. The system decomposes high-level system specifications into detailed, testable subsystem requirements using multi-agent LLM orchestration.

**Architecture Components:**

1. **Backend Engine (Weeks 1-4):** Python/LangGraph-based multi-agent workflow with 4 core nodes
2. **API Wrapper (Week 5):** FastAPI REST + Server-Sent Events for real-time streaming
3. **Web Frontend (Weeks 6-9):** Next.js 14+ application with TypeScript and modern UI
4. **Testing & Deployment (Weeks 10-12):** E2E testing, optimization, production deployment

**Key Design Principles:**

- **Skills-Based Architecture:** LLM behavior guided by version-controlled SKILL.md files
- **Binding Strategy Execution:** Decomposition strategy is 100% binding contract
- **Iterative Refinement with Feedback:** Specific, actionable feedback drives quality improvement
- **Intelligent LLM Fallback:** Error taxonomy with automatic model switching
- **Real-time Monitoring:** Server-Sent Events stream workflow progress to frontend
- **Human-in-the-Loop:** Interactive review at critical checkpoints
- **Domain-Aware Processing:** Optional domain-specific context for specialized requirements

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Technology Stack](#technology-stack)
3. [Complete Directory Structure](#complete-directory-structure)
4. [Backend Implementation (Weeks 1-4)](#backend-implementation-weeks-1-4)
   - Phase 0: Skills Validation
   - Phase 1: Foundation & State Management
   - Phase 2: Core Workflow Nodes
   - Phase 3: Graph Assembly & Control Flow
   - Phase 4: Testing & Observability
5. [API Layer Implementation (Week 5)](#api-layer-implementation-week-5)
6. [Frontend Implementation (Weeks 6-9)](#frontend-implementation-weeks-6-9)
7. [Testing & Deployment (Weeks 10-12)](#testing--deployment-weeks-10-12)
8. [Appendices](#appendices)

---

## System Architecture

### High-Level Architecture Diagram

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
│                  FASTAPI API WRAPPER                        │
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
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│           PYTHON/LANGGRAPH WORKFLOW ENGINE                  │
│                                                             │
│    START                                                    │
│      ↓                                                      │
│  ┌─────────────────────┐                                   │
│  │ 1. EXTRACT NODE     │  Agent: RequirementsAnalyst       │
│  │    Parse Document   │  Skill: requirements-extraction   │
│  │    Identify Reqs    │  Model: Gemini 2.5 Flash-Lite     │
│  └─────────────────────┘                                   │
│      ↓                                                      │
│  ┌─────────────────────┐                                   │
│  │ 2. ANALYZE NODE     │  Agent: SystemArchitect           │
│  │    Understand       │  Skill: system-analysis           │
│  │    Architecture     │  Model: Claude Sonnet 3.5         │
│  │    Create Strategy  │                                   │
│  └─────────────────────┘                                   │
│      ↓                                                      │
│  ┌─────────────────────┐                                   │
│  │ 3. DECOMPOSE NODE   │  Agent: RequirementsEngineer      │
│  │    Generate         │  Skill: requirements-decomposition│
│  │    Subsystem Reqs   │  Model: GPT-5 Nano                │
│  └─────────────────────┘                                   │
│      ↓                                                      │
│  ┌─────────────────────┐                                   │
│  │ 4. VALIDATE NODE    │  Agent: QualityAssurance          │
│  │    Quality Check    │  Skill: quality-validation        │
│  │    Score & Issues   │  Model: Gemini 2.5 Flash          │
│  └─────────────────────┘                                   │
│      ↓                                                      │
│    Quality Gate                                             │
│      ├─ PASS → Generate Docs → END                         │
│      └─ FAIL → [Human Review] → Revise → DECOMPOSE         │
│                                                             │
│  State Persistence: SQLite Checkpointing                    │
│  Observability: LangSmith Tracing (optional)                │
│  Domain Context: Optional domain-specific guidance          │
└─────────────────────────────────────────────────────────────┘
```

### 4-Node LangGraph Workflow Detail

**Node 1: Extract**
- **Purpose:** Parse specification documents, identify atomic requirements
- **Input:** PDF/DOCX/TXT specification document
- **Output:** List of extracted requirements with metadata
- **LLM:** Gemini 2.5 Flash-Lite (1M context, handles 88K+ token PDFs)
- **Skill:** `requirements-extraction/SKILL.md`

**Node 2: Analyze**
- **Purpose:** Understand system architecture, develop decomposition strategy
- **Input:** Extracted requirements + architecture context
- **Output:** Decomposition strategy (approach, allocation rules, templates)
- **LLM:** Claude Sonnet 3.5 (architectural reasoning excellence)
- **Skill:** `system-analysis/SKILL.md`

**Node 3: Decompose**
- **Purpose:** Transform system requirements into subsystem requirements
- **Input:** System requirements + binding strategy
- **Output:** Subsystem requirements with traceability
- **LLM:** GPT-5 Nano (no TPM limits, cost-efficient)
- **Skill:** `requirements-decomposition/SKILL.md`

**Node 4: Validate**
- **Purpose:** Automated quality scoring with iterative refinement
- **Input:** Decomposed requirements + strategy
- **Output:** Quality metrics (4 or 5 dimensions) + issues + feedback
- **LLM:** Gemini 2.5 Flash (best price-performance for QA)
- **Skill:** `quality-validation/SKILL.md`

---

## Technology Stack

### Backend Engine (Python)
- **Language:** Python 3.11+
- **Orchestration:** LangGraph 0.0.40+
- **LLM Framework:** LangChain 0.1.0+
- **LLM Providers:**
  - langchain-anthropic (Claude)
  - langchain-openai (GPT)
  - langchain-google-genai (Gemini)
- **State Management:** SQLite (dev), PostgreSQL (production)
- **Document Parsing:** python-docx, PyPDF2
- **Validation:** Pydantic 2.5+
- **Configuration:** python-dotenv
- **Testing:** pytest 7.4+
- **CLI Output:** rich 13.0+

### API Wrapper (Python)
- **Framework:** FastAPI 0.104+
- **ASGI Server:** Uvicorn
- **Real-time:** sse-starlette (Server-Sent Events)
- **Task Queue:** Python threading (MVP), Celery + Redis (production)
- **File Storage:** Local filesystem (MVP), S3 (production)
- **Caching:** Redis (production)

### Frontend (TypeScript)
- **Framework:** Next.js 14+ (App Router, React Server Components)
- **UI Library:** React 18+
- **Language:** TypeScript 5+
- **Styling:** Tailwind CSS 3.4+
- **Components:** shadcn/ui (Radix UI primitives)
- **State Management:**
  - Client State: Zustand
  - Server State: TanStack Query (React Query v5)
- **Real-time:** EventSource API (SSE client)
- **File Upload:** react-dropzone + axios
- **Forms:** React Hook Form + Zod validation
- **Charts:** Recharts (quality visualization)
- **Icons:** Lucide React
- **Markdown:** react-markdown + remark-gfm

### DevOps & Infrastructure
- **Containerization:** Docker + Docker Compose
- **Frontend Deployment:** Vercel (recommended) or Railway
- **Backend Deployment:** Railway, Render, or AWS ECS
- **Database:** PostgreSQL 15+ (production)
- **Cache/Queue:** Redis 7+
- **CI/CD:** GitHub Actions
- **Monitoring:** Sentry (errors), Plausible (analytics)
- **Observability:** LangSmith (LLM tracing, optional)

---

## Complete Directory Structure

This is the **complete, explicit** directory structure for the entire project. No references to "existing files" - everything is listed here.

```
req-decomp-web/
├── README.md                           # Project overview and setup
├── .env.example                        # Environment variable template
├── .gitignore                          # Git ignore rules
├── docker-compose.yml                  # Multi-service local development
├── LICENSE                             # Project license
│
├── docs/                               # Documentation
│   ├── implementation/
│   │   ├── mvp_plan.md                 # Original CLI plan
│   │   ├── mvp_plan_v2.md              # Web app plan
│   │   └── mvp_plan_v2.2.md            # THIS FILE - comprehensive plan
│   ├── phases/
│   │   ├── README.md                   # Phase history
│   │   ├── phase0/
│   │   ├── phase1/
│   │   └── ... (phase directories)
│   ├── user_guide.md                   # End-user documentation
│   ├── api_documentation.md            # API reference
│   ├── OBSERVABILITY.md                # Cost tracking, metrics
│   └── reference/
│       └── gemini_cli.md               # Large codebase analysis
│
├── frontend/                           # Next.js Web Application
│   ├── .next/                          # Next.js build output (gitignored)
│   ├── node_modules/                   # NPM dependencies (gitignored)
│   ├── public/                         # Static assets
│   │   ├── favicon.ico
│   │   └── images/
│   ├── src/
│   │   ├── app/                        # Next.js App Router pages
│   │   │   ├── layout.tsx              # Root layout with providers
│   │   │   ├── page.tsx                # Home/dashboard page
│   │   │   ├── upload/
│   │   │   │   └── page.tsx            # Upload specification page
│   │   │   ├── workflow/
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx        # Monitor workflow progress
│   │   │   └── results/
│   │   │       └── [id]/
│   │   │           └── page.tsx        # View workflow results
│   │   ├── components/                 # React components
│   │   │   ├── ui/                     # shadcn/ui base components
│   │   │   │   ├── button.tsx
│   │   │   │   ├── card.tsx
│   │   │   │   ├── input.tsx
│   │   │   │   ├── label.tsx
│   │   │   │   ├── progress.tsx
│   │   │   │   ├── textarea.tsx
│   │   │   │   ├── tabs.tsx
│   │   │   │   ├── table.tsx
│   │   │   │   ├── badge.tsx
│   │   │   │   ├── alert.tsx
│   │   │   │   └── dialog.tsx
│   │   │   ├── workflow/               # Workflow-specific components
│   │   │   │   ├── WorkflowProgress.tsx
│   │   │   │   ├── NodeStatus.tsx
│   │   │   │   └── HumanReviewModal.tsx
│   │   │   ├── upload/                 # Upload components
│   │   │   │   ├── FileUploader.tsx
│   │   │   │   └── DomainSelector.tsx
│   │   │   └── results/                # Results components
│   │   │       ├── RequirementsTable.tsx
│   │   │       ├── QualityMetricsChart.tsx
│   │   │       ├── TraceabilityMatrix.tsx
│   │   │       └── DownloadButton.tsx
│   │   ├── lib/                        # Utilities and helpers
│   │   │   ├── api.ts                  # API client (axios)
│   │   │   ├── sse.ts                  # SSE client utilities
│   │   │   ├── types.ts                # TypeScript type definitions
│   │   │   └── utils.ts                # General utilities
│   │   ├── hooks/                      # Custom React hooks
│   │   │   ├── useWorkflow.ts          # Workflow state management
│   │   │   └── useSSE.ts               # SSE connection hook
│   │   └── stores/                     # Zustand state stores
│   │       └── workflowStore.ts        # Global workflow state
│   ├── __tests__/                      # Frontend tests
│   │   ├── unit/
│   │   └── integration/
│   │       └── workflow.test.ts
│   ├── package.json                    # NPM dependencies
│   ├── package-lock.json
│   ├── tsconfig.json                   # TypeScript configuration
│   ├── next.config.js                  # Next.js configuration
│   ├── tailwind.config.js              # Tailwind CSS config
│   ├── postcss.config.js               # PostCSS config
│   ├── components.json                 # shadcn/ui configuration
│   ├── .eslintrc.json                  # ESLint configuration
│   └── Dockerfile                      # Frontend container
│
├── backend/                            # FastAPI Wrapper
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                     # FastAPI application entry
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── workflows.py            # Workflow CRUD endpoints
│   │   │   ├── files.py                # File upload endpoints
│   │   │   └── sse.py                  # SSE streaming endpoints
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── workflow_executor.py    # Execute LangGraph workflows
│   │   │   └── file_manager.py         # File handling service
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py              # Pydantic request/response models
│   │   └── core/
│   │       ├── __init__.py
│   │       ├── config.py               # FastAPI configuration
│   │       └── sse_manager.py          # SSE connection manager
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_workflows.py
│   │   └── test_sse.py
│   ├── requirements.txt                # Python dependencies
│   ├── Dockerfile                      # Backend container
│   └── .env.example                    # Environment template
│
├── engine/                             # Python/LangGraph Workflow Engine
│   ├── src/
│   │   ├── __init__.py
│   │   ├── graph/
│   │   │   ├── __init__.py
│   │   │   ├── state.py                # State schema (TypedDict + Pydantic)
│   │   │   ├── graph.py                # LangGraph definition
│   │   │   └── nodes.py                # Node implementations
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── base_agent.py           # BaseAgent class with skill loading
│   │   │   ├── requirements_analyst.py # RequirementsAnalystAgent
│   │   │   ├── system_architect.py     # SystemArchitectAgent
│   │   │   ├── requirements_engineer.py # RequirementsEngineerAgent
│   │   │   └── quality_assurance.py    # QualityAssuranceAgent
│   │   ├── skills/
│   │   │   ├── __init__.py
│   │   │   └── skill_loader.py         # Load SKILL.md files
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── document_parser.py      # PDF/DOCX → text
│   │       ├── quality_checker.py      # Automated quality validation
│   │       ├── output_generator.py     # Generate markdown docs
│   │       └── domain_loader.py        # Load domain contexts (Phase 7)
│   │
│   ├── skills/                         # Skills Library (SKILL.md files)
│   │   ├── README.md                   # Skills documentation
│   │   ├── requirements-extraction/
│   │   │   ├── SKILL.md                # Extraction methodology
│   │   │   └── CHANGELOG.md            # Version history
│   │   ├── system-analysis/
│   │   │   ├── SKILL.md                # System analysis methodology
│   │   │   └── CHANGELOG.md
│   │   ├── requirements-decomposition/
│   │   │   ├── SKILL.md                # Decomposition patterns
│   │   │   └── CHANGELOG.md
│   │   └── requirements-quality-validation/
│   │       ├── SKILL.md                # Quality validation criteria
│   │       └── CHANGELOG.md
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── llm_config.py               # LLM model assignments, fallbacks
│   │   ├── settings.py                 # App settings (quality thresholds, etc.)
│   │   ├── domain_config.py            # Domain configuration (Phase 7)
│   │   └── quality_config.py           # Quality dimension weights (Phase 7)
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── README.md                   # Testing documentation
│   │   ├── test_nodes.py               # Node unit tests
│   │   ├── test_agents.py              # Agent unit tests
│   │   ├── test_integration.py         # End-to-end workflow tests
│   │   ├── test_validate_node.py       # Validation node tests
│   │   ├── test_base_agent_domain.py   # Domain integration tests (Phase 7)
│   │   ├── test_domain_loader.py       # Domain loader tests (Phase 7)
│   │   └── test_workflow_domain_integration.py  # Full domain workflow tests
│   │
│   ├── examples/
│   │   ├── sample_spec.md              # Sample specification
│   │   ├── expected_output.md          # Expected results
│   │   ├── phase0_simple_spec.txt      # Phase 0 validation: simple
│   │   ├── phase0_simple_expected.json
│   │   ├── phase0_medium_spec.txt      # Phase 0 validation: medium
│   │   ├── phase0_medium_expected.json
│   │   ├── phase0_complex_spec.txt     # Phase 0 validation: complex
│   │   └── phase0_complex_expected.json
│   │
│   ├── outputs/                        # Generated artifacts (gitignored)
│   │   ├── requirements_*.md
│   │   ├── traceability_*.md
│   │   └── quality_report_*.md
│   │
│   ├── checkpoints/                    # SQLite checkpoints (gitignored)
│   │   └── decomposition_state.db
│   │
│   ├── domain_contexts/                # Domain-specific contexts (Phase 7)
│   │   ├── csx_dispatch/
│   │   │   ├── domain_config.json      # Domain metadata
│   │   │   ├── conventions.md          # Common conventions (Layer 1)
│   │   │   ├── glossary.md             # Domain glossary (Layer 1)
│   │   │   └── subsystems/
│   │   │       ├── train_management/
│   │   │       │   └── examples.md     # Subsystem examples (Layer 2)
│   │   │       ├── track_control/
│   │   │       │   └── examples.md
│   │   │       └── billing/
│   │   │           └── examples.md
│   │   └── generic/
│   │       ├── domain_config.json
│   │       └── examples.md             # Generic examples (Layer 3)
│   │
│   ├── main.py                         # CLI entry point
│   ├── requirements.txt                # Python dependencies
│   ├── pytest.ini                      # Pytest configuration
│   └── .env.example                    # Environment template
│
├── .github/                            # GitHub workflows
│   └── workflows/
│       ├── frontend-ci.yml             # Frontend CI/CD
│       └── backend-ci.yml              # Backend CI/CD
│
└── infrastructure/                     # Deployment configurations
    ├── terraform/                      # Infrastructure as Code (optional)
    ├── k8s/                            # Kubernetes manifests (optional)
    └── docker/
        ├── frontend.Dockerfile
        └── backend.Dockerfile
```

---

## Backend Implementation (Weeks 1-4)

This section covers the Python/LangGraph workflow engine implementation. This is the foundation that the web application will build upon.

### Phase 0: Skills Architecture Validation (Days 1-3)

**Goal:** Validate that the skills-based approach works reliably before committing to full implementation.

#### Why Phase 0 is Critical

The entire architecture depends on LLMs following SKILL.md methodology documents. If skills don't guide LLM behavior effectively, the system will produce inconsistent or low-quality outputs. **This validation de-risks the entire investment** by confirming the approach works in 2-3 days.

**Risk Without Validation:**
- Build for 2 weeks, discover skills don't work consistently
- Forced to pivot to structured prompts mid-project
- Wasted time and effort rebuilding architecture

**Investment:**
- 2-3 days now vs. 2+ weeks of potential rework
- Empirical validation with measurable success criteria
- Clear pivot strategy if validation fails

#### Phase 0.1: Create Minimal Extraction Skill (Day 1, Morning)

**File:** `engine/skills/requirements-extraction/SKILL.md` (Minimal Version)

```markdown
# Requirements Extraction Methodology

## Purpose
Extract atomic, testable requirements from system specifications.

## Process

### Step 1: Identify Requirements
Look for statements with modal verbs (shall, must, should, may) or imperative language.

### Step 2: Categorize
- **Functional:** What the system does
- **Performance:** How well it does it (speed, accuracy, capacity)
- **Constraint:** Limitations or restrictions
- **Interface:** External system interactions

### Step 3: Extract with Metadata
Each requirement must include:
- Unique ID: `EXTRACT-{TYPE}-{NUM}`
- Full text (exact quote)
- Type classification
- Source reference (section, page)

### Step 4: Quality Check
Each requirement must be:
- ✓ Atomic (single, testable statement)
- ✓ Unambiguous (single interpretation)
- ✓ Measurable (clear acceptance criteria)

## Output Format
```json
[
  {
    "id": "EXTRACT-FUNC-001",
    "text": "[exact quote from document]",
    "type": "functional|performance|constraint|interface",
    "source_reference": "Section X.Y, Page N"
  }
]
```

## Example
**Source:** "The system shall process requests within 100ms."
**Output:**
```json
{
  "id": "EXTRACT-PERF-001",
  "text": "The system shall process requests within 100ms",
  "type": "performance",
  "source_reference": "Section 3.2, Page 15"
}
```
```

**Tasks:**
1. Create `engine/skills/` directory
2. Create `engine/skills/requirements-extraction/` subdirectory
3. Write minimal SKILL.md (above)
4. Keep it focused: ~500-800 tokens

**Success Criteria:**
- ✅ Skill file created and readable
- ✅ Contains clear methodology and examples
- ✅ Under 1000 tokens (concise)

#### Phase 0.2: Create Test Corpus (Day 1, Afternoon)

**Test Specification 1: Simple (Happy Path)**

**File:** `engine/examples/phase0_simple_spec.txt`

```
System Requirements Specification

3.1 Functional Requirements

REQ-001: The system shall authenticate users using OAuth2.

REQ-002: The system shall log all user actions to the audit database.

3.2 Performance Requirements

REQ-003: The system shall process login requests within 500ms.

REQ-004: The system shall support 1000 concurrent users.

3.3 Constraints

REQ-005: The system shall operate on Linux kernel 5.15 or later.
```

**File:** `engine/examples/phase0_simple_expected.json`

```json
[
  {
    "id": "EXTRACT-FUNC-001",
    "text": "The system shall authenticate users using OAuth2",
    "type": "functional",
    "source_reference": "Section 3.1"
  },
  {
    "id": "EXTRACT-FUNC-002",
    "text": "The system shall log all user actions to the audit database",
    "type": "functional",
    "source_reference": "Section 3.1"
  },
  {
    "id": "EXTRACT-PERF-001",
    "text": "The system shall process login requests within 500ms",
    "type": "performance",
    "source_reference": "Section 3.2"
  },
  {
    "id": "EXTRACT-PERF-002",
    "text": "The system shall support 1000 concurrent users",
    "type": "performance",
    "source_reference": "Section 3.2"
  },
  {
    "id": "EXTRACT-CONS-001",
    "text": "The system shall operate on Linux kernel 5.15 or later",
    "type": "constraint",
    "source_reference": "Section 3.3"
  }
]
```

**Test Specification 2: Medium (Ambiguity Testing)**

Create `engine/examples/phase0_medium_spec.txt` with:
- 15 requirements
- Some compound statements (multiple requirements in one sentence)
- Ambiguous language ("quickly", "user-friendly")
- Mixed formatting (some with IDs, some without)

**Test Specification 3: Complex (Edge Cases)**

Create `engine/examples/phase0_complex_spec.txt` with:
- 30+ requirements
- Poor formatting (no section headers)
- Implied requirements (not explicitly stated)
- Tables and lists
- Background text mixed with requirements

**Tasks:**
1. Create all 3 specs + expected outputs
2. Manually extract requirements (ground truth)
3. Document edge cases to test

**Success Criteria:**
- ✅ 3 spec files created with varying complexity
- ✅ Ground truth extractions documented
- ✅ Expected outputs in JSON format

#### Phase 0.3: Build Test Harness (Day 2)

**File:** `engine/tests/test_phase0_skills.py`

```python
"""
Phase 0: Skills Validation Test Suite

Tests whether SKILL.md files can reliably guide LLM behavior.
"""

import json
from pathlib import Path
from typing import List, Dict
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate


def load_skill(skill_name: str) -> str:
    """Load skill content from markdown file."""
    skill_path = Path(f"skills/{skill_name}/SKILL.md")
    return skill_path.read_text()


def load_spec(spec_name: str) -> str:
    """Load test specification."""
    spec_path = Path(f"examples/{spec_name}.txt")
    return spec_path.read_text()


def load_expected(spec_name: str) -> List[Dict]:
    """Load expected extraction results."""
    expected_path = Path(f"examples/{spec_name}_expected.json")
    return json.loads(expected_path.read_text())


def extract_with_skill(spec_text: str, skill_content: str) -> List[Dict]:
    """Extract requirements using skill-guided LLM."""

    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        temperature=0.0
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", f"{skill_content}\n\nApply this methodology to extract requirements."),
        ("human", f"Specification document:\n\n{spec_text}\n\nExtract all requirements as JSON array.")
    ])

    chain = prompt | llm
    response = chain.invoke({})

    # Parse JSON from response
    content = response.content
    if "```json" in content:
        json_text = content.split("```json")[1].split("```")[0].strip()
    else:
        json_text = content

    return json.loads(json_text)


def extract_without_skill(spec_text: str) -> List[Dict]:
    """Extract requirements using baseline prompt (no skill)."""

    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        temperature=0.0
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a requirements analyst. Extract all requirements from the specification."),
        ("human", f"Specification:\n\n{spec_text}\n\nExtract requirements as JSON array with fields: id, text, type, source_reference.")
    ])

    chain = prompt | llm
    response = chain.invoke({})

    content = response.content
    if "```json" in content:
        json_text = content.split("```json")[1].split("```")[0].strip()
    else:
        json_text = content

    return json.loads(json_text)


def calculate_precision_recall(extracted: List[Dict], expected: List[Dict]) -> Dict:
    """Calculate precision and recall metrics."""

    # Normalize for comparison (use text)
    extracted_texts = {req["text"].lower().strip() for req in extracted}
    expected_texts = {req["text"].lower().strip() for req in expected}

    true_positives = len(extracted_texts & expected_texts)
    false_positives = len(extracted_texts - expected_texts)
    false_negatives = len(expected_texts - extracted_texts)

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives
    }


def test_consistency(spec_text: str, skill_content: str, runs: int = 3) -> float:
    """Test output consistency across multiple runs."""

    results = []
    for i in range(runs):
        extracted = extract_with_skill(spec_text, skill_content)
        # Normalize to text only for comparison
        result_texts = sorted([req["text"].lower().strip() for req in extracted])
        results.append(result_texts)

    # Calculate pairwise agreement
    total_agreements = 0
    comparisons = 0

    for i in range(len(results)):
        for j in range(i + 1, len(results)):
            set_i = set(results[i])
            set_j = set(results[j])
            agreement = len(set_i & set_j) / len(set_i | set_j) if len(set_i | set_j) > 0 else 0
            total_agreements += agreement
            comparisons += 1

    consistency = total_agreements / comparisons if comparisons > 0 else 0
    return consistency


def run_phase0_validation():
    """Run complete Phase 0 validation suite."""

    print("="*80)
    print("PHASE 0: SKILLS ARCHITECTURE VALIDATION")
    print("="*80)

    skill_content = load_skill("requirements-extraction")

    results = {}

    for spec_name in ["phase0_simple_spec", "phase0_medium_spec", "phase0_complex_spec"]:
        print(f"\n--- Testing: {spec_name} ---")

        spec_text = load_spec(spec_name)
        expected = load_expected(spec_name)

        # Test with skill
        print("Extracting WITH skill...")
        extracted_with_skill = extract_with_skill(spec_text, skill_content)
        metrics_with_skill = calculate_precision_recall(extracted_with_skill, expected)

        # Test without skill (baseline)
        print("Extracting WITHOUT skill (baseline)...")
        extracted_without_skill = extract_without_skill(spec_text)
        metrics_without_skill = calculate_precision_recall(extracted_without_skill, expected)

        # Test consistency
        print("Testing consistency (3 runs)...")
        consistency = test_consistency(spec_text, skill_content, runs=3)

        # Calculate improvement
        improvement = ((metrics_with_skill["f1"] - metrics_without_skill["f1"]) / metrics_without_skill["f1"] * 100) if metrics_without_skill["f1"] > 0 else 0

        results[spec_name] = {
            "with_skill": metrics_with_skill,
            "without_skill": metrics_without_skill,
            "improvement_percent": improvement,
            "consistency": consistency
        }

        # Print results
        print(f"\nResults for {spec_name}:")
        print(f"  WITH Skill    - Precision: {metrics_with_skill['precision']:.2f}, Recall: {metrics_with_skill['recall']:.2f}, F1: {metrics_with_skill['f1']:.2f}")
        print(f"  WITHOUT Skill - Precision: {metrics_without_skill['precision']:.2f}, Recall: {metrics_without_skill['recall']:.2f}, F1: {metrics_without_skill['f1']:.2f}")
        print(f"  Improvement: {improvement:.1f}%")
        print(f"  Consistency: {consistency:.2%}")

    # Overall assessment
    print("\n" + "="*80)
    print("OVERALL ASSESSMENT")
    print("="*80)

    avg_improvement = sum(r["improvement_percent"] for r in results.values()) / len(results)
    avg_consistency = sum(r["consistency"] for r in results.values()) / len(results)
    avg_f1_with_skill = sum(r["with_skill"]["f1"] for r in results.values()) / len(results)

    print(f"\nAverage Improvement: {avg_improvement:.1f}%")
    print(f"Average Consistency: {avg_consistency:.2%}")
    print(f"Average F1 with Skill: {avg_f1_with_skill:.2f}")

    # Go/No-Go Decision
    print("\n" + "="*80)
    print("GO/NO-GO DECISION")
    print("="*80)

    success_criteria = {
        "Quality Improvement ≥20%": avg_improvement >= 20,
        "Consistency ≥85%": avg_consistency >= 0.85,
        "Follows Instructions": avg_f1_with_skill >= 0.70
    }

    all_passed = all(success_criteria.values())

    for criterion, passed in success_criteria.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {criterion}")

    print("\n" + "="*80)
    if all_passed:
        print("✅ GO: Skills approach is validated. Proceed with Phase 1.")
    else:
        print("❌ NO-GO: Skills approach needs refinement or pivot to structured prompts.")
    print("="*80)

    return results, all_passed


if __name__ == "__main__":
    results, passed = run_phase0_validation()
```

**Tasks:**
1. Create test harness script
2. Implement skill loading
3. Implement LLM calling (with and without skill)
4. Implement metrics calculation
5. Implement consistency testing

**Success Criteria:**
- ✅ Test harness runs without errors
- ✅ Measures precision, recall, F1
- ✅ Tests consistency across 3 runs
- ✅ Compares with/without skill
- ✅ Outputs clear go/no-go recommendation

#### Phase 0.4: Run Validation and Decide (Day 3)

**Execution:**
```bash
# Setup environment
cd engine
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install langchain langchain-anthropic python-dotenv

# Set API key
export ANTHROPIC_API_KEY=your_key_here

# Run validation
python tests/test_phase0_skills.py
```

**Expected Output:**
```
================================================================================
PHASE 0: SKILLS ARCHITECTURE VALIDATION
================================================================================

--- Testing: phase0_simple_spec ---
Extracting WITH skill...
Extracting WITHOUT skill (baseline)...
Testing consistency (3 runs)...

Results for phase0_simple_spec:
  WITH Skill    - Precision: 0.95, Recall: 1.00, F1: 0.97
  WITHOUT Skill - Precision: 0.80, Recall: 0.90, F1: 0.85
  Improvement: 14.1%
  Consistency: 92%

[... similar for medium and complex specs ...]

================================================================================
OVERALL ASSESSMENT
================================================================================

Average Improvement: 25.3%
Average Consistency: 88%
Average F1 with Skill: 0.89

================================================================================
GO/NO-GO DECISION
================================================================================

✅ PASS - Quality Improvement ≥20%
✅ PASS - Consistency ≥85%
✅ PASS - Follows Instructions

================================================================================
✅ GO: Skills approach is validated. Proceed with Phase 1.
================================================================================
```

**Decision Matrix:**

| Scenario | Avg Improvement | Consistency | Action |
|----------|----------------|-------------|--------|
| **Best Case** | ≥30% | ≥90% | ✅ GO - Skills work great, proceed confidently |
| **Good Case** | ≥20% | ≥85% | ✅ GO - Skills work well, proceed as planned |
| **Marginal** | 10-20% | 75-85% | ⚠️ REFINE - Improve skill, re-test |
| **Failure** | <10% | <75% | ❌ PIVOT - Use structured prompts instead |

**Pivot Strategy (if validation fails):**

If skills don't meet success criteria:
1. **Option A:** Refine skill and re-test (1 day)
   - Add more examples
   - Clarify methodology
   - Simplify instructions
2. **Option B:** Hybrid approach (use skills + few-shot examples)
3. **Option C:** Pivot to structured prompts with function calling
   - Define Pydantic schemas for outputs
   - Use JSON mode for LLM calls
   - Hardcode methodology in system prompts

### Phase 1: Foundation (Week 1, Days 4-7)

**Goal:** Set up project structure, implement state management, and create first node.

#### Phase 1.1: Project Setup (Days 4-5)

**Dependencies File:** `engine/requirements.txt`

```txt
# LangGraph and LangChain
langgraph>=0.0.40
langchain>=0.1.0
langchain-openai>=0.0.5
langchain-anthropic>=0.1.0
langchain-google-genai>=0.0.5

# Document parsing
python-docx>=1.0.0
PyPDF2>=3.0.0

# Data validation
pydantic>=2.5.0

# Configuration
python-dotenv>=1.0.0

# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0

# CLI output
rich>=13.0.0

# Utilities
requests>=2.31.0
```

**Environment Template:** `engine/.env.example`

```bash
# LLM API Keys
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_key_here

# LangSmith (optional, for observability)
LANGCHAIN_TRACING_V2=false
LANGCHAIN_PROJECT=requirements-decomposition-mvp
LANGCHAIN_API_KEY=your_langsmith_key_here

# Quality Settings
QUALITY_THRESHOLD=0.80
MAX_ITERATIONS=3
TEMPERATURE=0.0

# Cost Tracking
COST_TRACKING_ENABLED=true
COST_BUDGET_WARNING=1.00
COST_BUDGET_MAX=5.00

# Quality Dimension Weights (4D generic, 5D domain-aware)
QUALITY_WEIGHT_COMPLETENESS=0.25
QUALITY_WEIGHT_CLARITY=0.25
QUALITY_WEIGHT_TESTABILITY=0.25
QUALITY_WEIGHT_TRACEABILITY=0.25
QUALITY_WEIGHT_DOMAIN_COMPLIANCE=0.20  # Only for domain-aware workflows
```

**Tasks:**
1. Create `engine/` directory structure (as shown in Complete Directory Structure)
2. Set up virtual environment
3. Install dependencies from requirements.txt
4. Create .env file from .env.example
5. Configure LangSmith for observability (optional)
6. Create basic logging infrastructure
7. Write configuration loader

**Success Criteria:**
- ✅ Can import all packages without errors
- ✅ Configuration loads from .env file
- ✅ Logging outputs to console and file
- ✅ pytest discovers and runs basic tests

#### Phase 1.2: State Schema Implementation (Day 6)

**File:** `engine/src/state.py`

```python
"""
State Schema for Requirements Decomposition Workflow

This module defines the complete state structure for the LangGraph workflow,
including all input parameters, intermediate results, quality tracking,
human review, observability metrics, and error handling.
"""

from typing import TypedDict, List, Optional, Literal, Annotated, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
import operator


# ============================================================================
# Pydantic Models for Validation
# ============================================================================

class Requirement(BaseModel):
    """Individual requirement with metadata."""
    id: str = Field(..., description="Unique requirement identifier")
    text: str = Field(..., min_length=10, description="Requirement text")
    type: Literal["functional", "performance", "constraint", "interface"]
    parent_id: Optional[str] = None
    subsystem: Optional[str] = None
    rationale: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    source_reference: Optional[str] = None

    @validator('id')
    def validate_id_format(cls, v):
        """Enforce naming convention: SYS-FUNC-001 or TM-PERF-002."""
        if not v or len(v.split('-')) < 3:
            raise ValueError("ID must follow format: {SYSTEM}-{TYPE}-{NUM}")
        return v


class DecompositionStrategy(BaseModel):
    """Strategy for decomposing requirements."""
    approach: Literal["functional", "architectural", "hybrid"]
    subsystem_list: List[str]
    allocation_rules: str
    templates: dict = Field(default_factory=dict)
    rationale: Optional[str] = None


class QualityIssue(BaseModel):
    """Individual quality issue with suggestion."""
    requirement_id: str
    severity: Literal["critical", "major", "minor"]
    category: str
    description: str
    suggestion: str


class QualityMetrics(BaseModel):
    """Quality assessment metrics (4D or 5D)."""
    overall_score: float = Field(ge=0.0, le=1.0)
    completeness: float = Field(ge=0.0, le=1.0)
    clarity: float = Field(ge=0.0, le=1.0)
    testability: float = Field(ge=0.0, le=1.0)
    traceability: float = Field(ge=0.0, le=1.0)
    domain_compliance: Optional[float] = Field(None, ge=0.0, le=1.0)  # 5th dimension (Phase 7)
    issues: List[QualityIssue] = Field(default_factory=list)


class DomainContext(BaseModel):
    """Domain-specific context (Phase 7)."""
    domain_name: str
    subsystem_id: Optional[str] = None
    conventions: Optional[str] = None  # Layer 1: Common conventions
    glossary: Optional[str] = None     # Layer 1: Domain glossary
    examples: Optional[str] = None     # Layer 2 or 3: Examples


class ErrorLog(BaseModel):
    """Error log entry."""
    timestamp: str
    error_type: Literal["INFO", "WARNING", "TRANSIENT", "CONTENT", "FATAL"]
    node: str
    message: str
    details: Optional[Dict[str, Any]] = None


# ============================================================================
# LangGraph State (TypedDict)
# ============================================================================

class DecompositionState(TypedDict):
    """
    Complete state for requirements decomposition workflow.

    This TypedDict defines all state fields used by the LangGraph workflow.
    Fields with Annotated[List, operator.add] are reducers that concatenate values.
    """

    # -------------------------------------------------------------------------
    # Input Parameters
    # -------------------------------------------------------------------------
    spec_document_path: str                     # Path to specification file
    target_subsystem: str                       # Subsystem to decompose for
    review_before_decompose: bool               # Optional pre-decomposition review
    knowledge_base_path: Optional[str]          # Path to knowledge base (optional)
    domain_name: Optional[str]                  # Domain name (Phase 7, default: "generic")
    subsystem_id: Optional[str]                 # Subsystem ID for domain context (Phase 7)

    # -------------------------------------------------------------------------
    # Intermediate Results
    # -------------------------------------------------------------------------
    extracted_requirements: Annotated[List[dict], operator.add]  # From extract node
    system_context: str                         # Architectural context
    decomposition_strategy: Optional[dict]      # BINDING contract from analyze node
    subsystem_requirements: Annotated[List[dict], operator.add]  # From decompose node
    domain_context: Optional[dict]              # Domain-specific context (Phase 7)

    # -------------------------------------------------------------------------
    # Quality Tracking & Refinement
    # -------------------------------------------------------------------------
    quality_metrics: Optional[dict]             # Quality assessment results
    validation_passed: bool                     # Quality gate status
    iteration_count: int                        # Current iteration number
    max_iterations: int                         # Maximum allowed iterations
    refinement_feedback: Optional[str]          # Specific feedback for improvement
    validation_issues: List[dict]               # Detailed quality issues
    previous_attempt: Optional[List[dict]]      # Last decomposition for comparison

    # -------------------------------------------------------------------------
    # Human Review
    # -------------------------------------------------------------------------
    human_feedback: Optional[str]               # Human reviewer feedback
    requires_human_review: bool                 # Flag to trigger human review

    # -------------------------------------------------------------------------
    # Output
    # -------------------------------------------------------------------------
    final_document_path: Optional[str]          # Generated requirements document
    traceability_matrix: Optional[dict]         # Parent-child traceability

    # -------------------------------------------------------------------------
    # Observability (Phase 6+)
    # -------------------------------------------------------------------------
    total_cost: float                           # Total LLM API cost (USD)
    cost_breakdown: Dict[str, float]            # Cost per node
    timing_breakdown: Dict[str, float]          # Execution time per node
    total_energy_wh: float                      # Total energy consumption (Wh)
    energy_breakdown: Dict[str, float]          # Energy per node

    # -------------------------------------------------------------------------
    # Error Handling & Fallback Tracking
    # -------------------------------------------------------------------------
    errors: Annotated[List[str], operator.add]  # Error messages
    fallback_count: int                         # Number of LLM fallback events
    error_log: List[dict]                       # Detailed error tracking


# ============================================================================
# Helper Functions
# ============================================================================

def create_initial_state(
    spec_document_path: str,
    target_subsystem: str,
    review_before_decompose: bool = False,
    domain_name: str = "generic",
    subsystem_id: Optional[str] = None,
    max_iterations: int = 3
) -> DecompositionState:
    """
    Create initial workflow state with default values.

    Args:
        spec_document_path: Path to specification document
        target_subsystem: Target subsystem for decomposition
        review_before_decompose: Enable pre-decomposition human review
        domain_name: Domain name for domain-aware processing (default: "generic")
        subsystem_id: Subsystem ID for domain-specific examples
        max_iterations: Maximum refinement iterations

    Returns:
        Initial DecompositionState
    """
    return DecompositionState(
        # Input
        spec_document_path=spec_document_path,
        target_subsystem=target_subsystem,
        review_before_decompose=review_before_decompose,
        knowledge_base_path=None,
        domain_name=domain_name,
        subsystem_id=subsystem_id,

        # Intermediate
        extracted_requirements=[],
        system_context="",
        decomposition_strategy=None,
        subsystem_requirements=[],
        domain_context=None,

        # Quality
        quality_metrics=None,
        validation_passed=False,
        iteration_count=0,
        max_iterations=max_iterations,
        refinement_feedback=None,
        validation_issues=[],
        previous_attempt=None,

        # Human Review
        human_feedback=None,
        requires_human_review=False,

        # Output
        final_document_path=None,
        traceability_matrix=None,

        # Observability
        total_cost=0.0,
        cost_breakdown={},
        timing_breakdown={},
        total_energy_wh=0.0,
        energy_breakdown={},

        # Error Handling
        errors=[],
        fallback_count=0,
        error_log=[]
    )


def validate_state(state: DecompositionState) -> tuple[bool, List[str]]:
    """
    Validate state integrity.

    Args:
        state: Workflow state to validate

    Returns:
        (is_valid, error_messages)
    """
    errors = []

    # Required fields
    if not state.get("spec_document_path"):
        errors.append("Missing spec_document_path")
    if not state.get("target_subsystem"):
        errors.append("Missing target_subsystem")

    # Iteration count
    if state.get("iteration_count", 0) > state.get("max_iterations", 3):
        errors.append("Iteration count exceeds maximum")

    # Quality metrics validation
    if state.get("quality_metrics"):
        metrics = state["quality_metrics"]
        if metrics.get("overall_score", 0) < 0 or metrics.get("overall_score", 0) > 1:
            errors.append("Invalid quality score (must be 0-1)")

    return (len(errors) == 0, errors)
```

**Tasks:**
1. Define all state types using Pydantic for validation
2. Add validators for requirement ID format, score ranges
3. Implement state serialization (to/from JSON)
4. Write unit tests for state validation
5. Create helper functions for state manipulation

**Success Criteria:**
- ✅ State schema passes type checking (mypy)
- ✅ Invalid states raise appropriate validation errors
- ✅ State can be serialized/deserialized without data loss
- ✅ All unit tests pass

#### Phase 1.3: First Node - Requirements Extraction (Day 7)

**File:** `engine/src/agents/base_agent.py`

```python
"""
Base Agent class with skill loading and domain context injection.
"""

from pathlib import Path
from typing import Optional
from langchain.llms.base import BaseLanguageModel


class BaseAgent:
    """Base class for all LLM agents with skill loading."""

    def __init__(
        self,
        model: BaseLanguageModel,
        skill_name: str,
        temperature: float = 0.0
    ):
        """
        Initialize base agent.

        Args:
            model: LLM instance
            skill_name: Name of skill directory (e.g., "requirements-extraction")
            temperature: LLM temperature
        """
        self.model = model
        self.skill_name = skill_name
        self.temperature = temperature

    def get_skill_content(self, domain_context: Optional[dict] = None) -> str:
        """
        Load skill content and inject domain context if provided.

        Domain context injection (Phase 7):
        - If domain_context provided, inject between methodology and examples
        - Structure: [Methodology] → [Domain Conventions/Glossary] → [Examples]

        Args:
            domain_context: Optional domain-specific context

        Returns:
            Complete skill content with optional domain injection
        """
        skill_path = Path(f"skills/{self.skill_name}/SKILL.md")
        skill_content = skill_path.read_text()

        # Inject domain context if provided (Phase 7)
        if domain_context:
            # Find insertion point (before examples section)
            if "## Example" in skill_content:
                parts = skill_content.split("## Example", 1)
                domain_section = self._format_domain_context(domain_context)
                skill_content = parts[0] + domain_section + "\n## Example" + parts[1]
            else:
                # Append to end if no examples section
                domain_section = self._format_domain_context(domain_context)
                skill_content += "\n" + domain_section

        return skill_content

    def _format_domain_context(self, domain_context: dict) -> str:
        """
        Format domain context for injection into skill.

        Args:
            domain_context: Domain context dictionary

        Returns:
            Formatted markdown section
        """
        sections = ["\n## Domain-Specific Context\n"]

        if domain_context.get("conventions"):
            sections.append("### Conventions\n")
            sections.append(domain_context["conventions"])
            sections.append("\n")

        if domain_context.get("glossary"):
            sections.append("### Glossary\n")
            sections.append(domain_context["glossary"])
            sections.append("\n")

        if domain_context.get("examples"):
            sections.append("### Domain Examples\n")
            sections.append(domain_context["examples"])
            sections.append("\n")

        return "".join(sections)
```

**File:** `engine/src/agents/requirements_analyst.py`

```python
"""
Requirements Analyst Agent - Extracts requirements from specifications.
"""

from typing import List, Dict
from langchain.prompts import ChatPromptTemplate
from .base_agent import BaseAgent


class RequirementsAnalystAgent(BaseAgent):
    """Agent for extracting requirements from specification documents."""

    def __init__(self, model, temperature: float = 0.1):
        super().__init__(
            model=model,
            skill_name="requirements-extraction",
            temperature=temperature
        )

    def extract_requirements(
        self,
        document_text: str,
        target_subsystem: str = "",
        domain_context: dict = None
    ) -> List[Dict]:
        """
        Extract requirements from document text.

        Args:
            document_text: Parsed specification text
            target_subsystem: Optional subsystem filter
            domain_context: Optional domain-specific context (Phase 7)

        Returns:
            List of extracted requirements
        """
        # Load skill with optional domain context
        skill_content = self.get_skill_content(domain_context)

        # Build prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"{skill_content}\n\nApply this methodology to extract requirements."),
            ("human", f"Specification document:\n\n{document_text}\n\n"
                     f"Target subsystem (if applicable): {target_subsystem}\n\n"
                     f"Extract all requirements as JSON array.")
        ])

        # Execute
        chain = prompt | self.model
        response = chain.invoke({})

        # Parse JSON response
        import json
        content = response.content
        if "```json" in content:
            json_text = content.split("```json")[1].split("```")[0].strip()
        else:
            json_text = content

        requirements = json.loads(json_text)
        return requirements
```

**File:** `engine/src/utils/document_parser.py`

```python
"""
Document parsing utilities for PDF, DOCX, and TXT files.
"""

from pathlib import Path
from typing import Union
import PyPDF2
from docx import Document


def parse_document(file_path: Union[str, Path]) -> str:
    """
    Parse document and extract text.

    Args:
        file_path: Path to document file

    Returns:
        Extracted text content

    Raises:
        ValueError: If file format not supported
    """
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        return parse_pdf(file_path)
    elif suffix == ".docx":
        return parse_docx(file_path)
    elif suffix == ".txt":
        return parse_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format: {suffix}")


def parse_pdf(file_path: Path) -> str:
    """Extract text from PDF."""
    text = []
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text.append(page.extract_text())
    return "\n".join(text)


def parse_docx(file_path: Path) -> str:
    """Extract text from DOCX."""
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])


def parse_txt(file_path: Path) -> str:
    """Extract text from TXT."""
    return file_path.read_text(encoding="utf-8")
```

**File:** `engine/src/nodes/extract_node.py`

```python
"""
Extract Node - Parses specification and extracts requirements.
"""

from datetime import datetime
from ..state import DecompositionState
from ..agents.requirements_analyst import RequirementsAnalystAgent
from ..utils.document_parser import parse_document
from ..utils.domain_loader import DomainLoader, DomainLoadError
from langchain_google_genai import ChatGoogleGenerativeAI


def extract_node(state: DecompositionState) -> dict:
    """
    Extract requirements from specification document.

    This node:
    1. Parses the document (PDF/DOCX/TXT)
    2. Loads domain context if specified (Phase 7)
    3. Extracts requirements using RequirementsAnalystAgent
    4. Returns extracted requirements and domain context

    Args:
        state: Current workflow state

    Returns:
        State updates with extracted requirements and domain context
    """
    error_log = state.get("error_log", [])

    try:
        # Parse document
        doc_text = parse_document(state["spec_document_path"])

        # Load domain context (Phase 7)
        domain_context = None
        domain_name = state.get('domain_name', 'generic')
        subsystem_id = state.get('subsystem_id')

        if domain_name and domain_name != 'generic':
            try:
                # Load domain context
                domain_context = DomainLoader.load_context(
                    domain_name=domain_name,
                    subsystem_id=subsystem_id
                )

                # Log successful load
                error_log.append({
                    'timestamp': datetime.utcnow().isoformat(),
                    'error_type': 'INFO',
                    'node': 'extract',
                    'message': f"Loaded domain context: {domain_name}" +
                              (f"/{subsystem_id}" if subsystem_id else "")
                })
            except DomainLoadError as e:
                # Non-fatal: fall back to generic domain
                error_log.append({
                    'timestamp': datetime.utcnow().isoformat(),
                    'error_type': 'CONTENT',
                    'node': 'extract',
                    'message': f"Domain loading failed, using generic domain: {str(e)}"
                })
                domain_context = None  # Explicit fallback

        # Initialize agent with Gemini 2.5 Flash-Lite (1M context)
        model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            temperature=0.1
        )
        agent = RequirementsAnalystAgent(model=model)

        # Extract requirements
        requirements = agent.extract_requirements(
            document_text=doc_text,
            target_subsystem=state.get("target_subsystem", ""),
            domain_context=domain_context
        )

        return {
            "extracted_requirements": requirements,
            "domain_context": domain_context,
            "error_log": error_log
        }

    except Exception as e:
        error_log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'error_type': 'FATAL',
            'node': 'extract',
            'message': f"Extraction failed: {str(e)}"
        })

        return {
            "errors": [f"Extraction failed: {str(e)}"],
            "requires_human_review": True,
            "error_log": error_log
        }
```

**Tasks:**
1. Implement document parser (PDF/DOCX → text)
2. Write complete requirements extraction skill
3. Create base agent class with skill loading
4. Implement RequirementsAnalystAgent
5. Build extraction node with error handling
6. Write integration test with sample specification
7. Add logging and debugging output

**Success Criteria:**
- ✅ Parser handles PDF and DOCX files
- ✅ Agent successfully loads and uses skill
- ✅ Extracts ≥90% of requirements from test document
- ✅ Correctly categorizes requirement types
- ✅ Generates valid requirement IDs
- ✅ Integration test passes

### Phase 2: Core Decomposition Logic (Week 2, Days 8-12)

[Continue with Phase 2.1-2.3 following the same detailed pattern, implementing Analyze, Decompose, and Validate nodes with their respective skills and agents...]

Due to space constraints, I'll provide the structure but not the full code for all remaining phases. The pattern continues:

- **Phase 2.1:** Analyze Node (system-analysis skill, SystemArchitectAgent)
- **Phase 2.2:** Decompose Node (requirements-decomposition skill, RequirementsEngineerAgent)
- **Phase 2.3:** Validate Node (quality-validation skill, QualityAssuranceAgent)

### Phase 3: Graph Assembly (Week 3, Days 13-17)

- **Phase 3.1:** Complete graph with conditional routing
- **Phase 3.2:** Human-in-the-loop review node
- **Phase 3.3:** Documentation generation

### Phase 4: Backend Testing (Week 4, Days 18-21)

- **Phase 4.1:** Integration testing
- **Phase 4.2:** Optimization and observability
- **Phase 4.3:** LLM fallback implementation
- **Phase 4.4:** Cost tracking and energy monitoring

---

## API Layer Implementation (Week 5)

### FastAPI Wrapper Architecture

**File:** `backend/app/main.py`

```python
"""
FastAPI application for Requirements Decomposition System.

Provides REST API + Server-Sent Events for real-time workflow monitoring.
"""

from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import asyncio
import uuid
from typing import Dict
import sys
from pathlib import Path

# Add engine to path
sys.path.append(str(Path(__file__).parent.parent.parent / "engine"))

from src.graph.graph import create_decomposition_graph
from src.state import create_initial_state

app = FastAPI(
    title="Requirements Decomposition API",
    description="AI-powered requirements decomposition with real-time monitoring",
    version="1.0.0"
)

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (use Redis in production)
workflows: Dict[str, dict] = {}
sse_connections: Dict[str, asyncio.Queue] = {}


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "service": "requirements-decomposition-api"}


@app.post("/api/workflows/upload")
async def upload_specification(
    file: UploadFile = File(...),
    subsystem: str = "",
    domain: str = "generic",
    subsystem_id: str = None
):
    """
    Upload specification document and create workflow.

    Args:
        file: Specification file (PDF, DOCX, TXT)
        subsystem: Target subsystem name
        domain: Domain name (default: "generic")
        subsystem_id: Subsystem ID for domain-specific examples

    Returns:
        Workflow ID and initial status
    """
    workflow_id = str(uuid.uuid4())

    # Save uploaded file
    upload_dir = Path("/tmp/uploads")
    upload_dir.mkdir(exist_ok=True)
    file_path = upload_dir / f"{workflow_id}_{file.filename}"

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Create workflow state
    workflows[workflow_id] = {
        "id": workflow_id,
        "status": "pending",
        "file_path": str(file_path),
        "subsystem": subsystem,
        "domain": domain,
        "subsystem_id": subsystem_id,
        "progress": {},
        "created_at": datetime.utcnow().isoformat()
    }

    return {
        "workflow_id": workflow_id,
        "status": "pending",
        "message": "Workflow created successfully"
    }


@app.post("/api/workflows/{workflow_id}/start")
async def start_workflow(
    workflow_id: str,
    background_tasks: BackgroundTasks
):
    """
    Start workflow execution in background.

    Args:
        workflow_id: Workflow identifier

    Returns:
        Workflow status
    """
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")

    workflows[workflow_id]["status"] = "running"
    workflows[workflow_id]["started_at"] = datetime.utcnow().isoformat()

    # Execute workflow in background
    background_tasks.add_task(execute_workflow, workflow_id)

    return {
        "workflow_id": workflow_id,
        "status": "running",
        "message": "Workflow execution started"
    }


@app.get("/api/workflows/{workflow_id}/stream")
async def stream_workflow_progress(workflow_id: str):
    """
    Stream workflow progress via Server-Sent Events.

    Args:
        workflow_id: Workflow identifier

    Returns:
        EventSourceResponse with real-time updates
    """
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Create SSE queue for this client
    queue = asyncio.Queue()
    sse_connections[workflow_id] = queue

    async def event_generator():
        try:
            while True:
                # Wait for events from workflow executor
                event = await queue.get()

                # Format as SSE
                yield {
                    "event": event.get("event", "message"),
                    "data": json.dumps(event.get("data", {}))
                }

                # Stop streaming when complete
                if event.get("event") in ["complete", "error"]:
                    break
        finally:
            # Clean up connection
            if workflow_id in sse_connections:
                del sse_connections[workflow_id]

    return EventSourceResponse(event_generator())


@app.get("/api/workflows/{workflow_id}/status")
async def get_workflow_status(workflow_id: str):
    """
    Get current workflow status.

    Args:
        workflow_id: Workflow identifier

    Returns:
        Complete workflow state
    """
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")

    return workflows[workflow_id]


async def execute_workflow(workflow_id: str):
    """
    Execute LangGraph workflow with progress updates.

    Args:
        workflow_id: Workflow identifier
    """
    workflow_data = workflows[workflow_id]

    try:
        # Send start event
        await send_sse_event(workflow_id, {
            "event": "started",
            "data": {"status": "started", "timestamp": datetime.utcnow().isoformat()}
        })

        # Create initial state
        initial_state = create_initial_state(
            spec_document_path=workflow_data["file_path"],
            target_subsystem=workflow_data["subsystem"],
            domain_name=workflow_data.get("domain", "generic"),
            subsystem_id=workflow_data.get("subsystem_id")
        )

        # Create graph
        graph = create_decomposition_graph()

        # Execute with streaming
        async for event in graph.astream(initial_state):
            # Send progress update
            await send_sse_event(workflow_id, {
                "event": "progress",
                "data": {
                    "node": event.get("__node__"),
                    "state_update": event,
                    "timestamp": datetime.utcnow().isoformat()
                }
            })

            # Update workflow storage
            workflows[workflow_id]["progress"] = event

        # Mark complete
        workflows[workflow_id]["status"] = "completed"
        workflows[workflow_id]["completed_at"] = datetime.utcnow().isoformat()

        await send_sse_event(workflow_id, {
            "event": "complete",
            "data": {
                "status": "completed",
                "final_state": event,
                "timestamp": datetime.utcnow().isoformat()
            }
        })

    except Exception as e:
        workflows[workflow_id]["status"] = "error"
        workflows[workflow_id]["error"] = str(e)

        await send_sse_event(workflow_id, {
            "event": "error",
            "data": {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        })


async def send_sse_event(workflow_id: str, event: dict):
    """
    Send SSE event to connected clients.

    Args:
        workflow_id: Workflow identifier
        event: Event data
    """
    if workflow_id in sse_connections:
        await sse_connections[workflow_id].put(event)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Tasks (Week 5):**
1. Implement FastAPI application with all endpoints
2. Set up CORS middleware for frontend
3. Implement SSE streaming for real-time updates
4. Create file upload and storage
5. Integrate with LangGraph workflow executor
6. Add comprehensive error handling
7. Write API documentation (OpenAPI/Swagger)
8. Test all endpoints with Postman/HTTPie
9. Implement health checks and monitoring endpoints

**Success Criteria:**
- ✅ All API endpoints functional
- ✅ SSE stream sends real-time progress
- ✅ File uploads work for PDF/DOCX/TXT
- ✅ Workflow execution integrates with backend
- ✅ API documentation complete
- ✅ Error responses are informative

---

## Frontend Implementation (Weeks 6-9)

[This section would continue with the detailed Next.js implementation from mvp_plan_v2.md, including:]

### Week 6: Frontend Foundation
- Phase 6.1: Next.js setup, TypeScript configuration
- Phase 6.2: shadcn/ui components, Tailwind CSS
- Phase 6.3: API client, SSE hooks
- Phase 6.4: Upload page implementation

### Week 7: Core UI Pages
- Phase 7.1: Workflow monitoring page with real-time updates
- Phase 7.2: Results visualization (tables, charts)
- Phase 7.3: Quality metrics dashboard
- Phase 7.4: Traceability matrix viewer

### Week 8: Advanced Features
- Phase 8.1: Human review modal
- Phase 8.2: Domain selection UI
- Phase 8.3: Download/export functionality
- Phase 8.4: Responsive design and mobile optimization

### Week 9: Integration Testing
- Phase 9.1: Component unit tests
- Phase 9.2: Integration tests (React Testing Library)
- Phase 9.3: E2E tests (Playwright)
- Phase 9.4: Accessibility testing (WCAG 2.1 AA)

---

## Testing & Deployment (Weeks 10-12)

### Week 10: Comprehensive Testing
- **Phase 10.1:** End-to-end workflow testing
- **Phase 10.2:** Load testing (concurrent workflows)
- **Phase 10.3:** Security testing
- **Phase 10.4:** Performance optimization

### Week 11: Deployment Preparation
- **Phase 11.1:** Docker containerization
- **Phase 11.2:** Database migration to PostgreSQL
- **Phase 11.3:** Redis caching setup
- **Phase 11.4:** Environment configuration

### Week 12: Production Deployment
- **Phase 12.1:** Frontend deployment (Vercel)
- **Phase 12.2:** Backend deployment (Railway/Render)
- **Phase 12.3:** Monitoring and logging (Sentry, CloudWatch)
- **Phase 12.4:** Documentation and handoff

---

## Appendices

### Appendix A: Critical Implementation Requirements

#### 1. Refinement Feedback Loop (MANDATORY)

**Problem:** Without feedback, iteration cannot improve quality.

**Solution:**
```python
# In validate node - generate specific feedback
if not validation_passed:
    feedback = generate_refinement_guidance(
        issues=metrics["issues"],
        requirements=state["subsystem_requirements"],
        strategy=state["decomposition_strategy"]
    )
    return {
        "refinement_feedback": feedback,  # Actionable instructions
        "validation_issues": metrics["issues"],
        "previous_attempt": state["subsystem_requirements"]
    }

# In decompose node - consume feedback
if state.get("refinement_feedback"):
    subsystem_reqs = agent.decompose_with_refinement(
        requirements=state["extracted_requirements"],
        strategy=state["decomposition_strategy"],
        previous_attempt=state.get("previous_attempt"),
        feedback=state["refinement_feedback"]  # Tell agent what to fix
    )
```

#### 2. LLM Fallback with Error Taxonomy (MANDATORY)

**Error Classification:**
```python
class ErrorType(Enum):
    TRANSIENT = "transient"  # RateLimitError, TimeoutError, APIError
    CONTENT = "content"      # ValidationError, JSONDecodeError, ParseError
    FATAL = "fatal"          # AuthError, MissingResourceError

# Transient → Retry with exponential backoff (same model)
# Content → Switch to fallback model
# Fatal → Stop execution, human intervention
```

**Implementation Pattern:**
```python
class LLMFallbackHandler:
    def call_with_fallback(self, primary_model, fallback_model, prompt, max_retries=3):
        for attempt in range(max_retries):
            try:
                return primary_model.invoke(prompt)
            except Exception as e:
                error_type = self.classify_error(e)
                if error_type == ErrorType.TRANSIENT:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                elif error_type == ErrorType.CONTENT:
                    self.fallback_count += 1
                    return fallback_model.invoke(prompt)
                else:  # FATAL
                    raise
```

#### 3. Binding Strategy Execution (MANDATORY)

**Requirement:** Decomposition strategy from analyze node is 100% binding (not advisory).

**Validation Pattern:**
```python
def decompose_node(state: DecompositionState) -> dict:
    strategy = state["decomposition_strategy"]

    # Execute decomposition strictly following strategy
    subsystem_reqs = agent.decompose_requirements(
        requirements=state["extracted_requirements"],
        strategy=strategy,  # Must follow exactly
        strict_mode=True
    )

    # Validate strategy adherence
    adherence_check = validate_strategy_adherence(
        requirements=subsystem_reqs,
        strategy=strategy
    )

    if not adherence_check["passed"]:
        # Strategy violation is a BUG, not a quality issue
        return {
            "errors": [f"Agent violated strategy: {adherence_check['violations']}"],
            "requires_human_review": True
        }

    return {"subsystem_requirements": subsystem_reqs}
```

#### 4. State Persistence Fix (MANDATORY)

**Problem:** Using `:memory:` doesn't persist to disk.

**Solution:**
```python
# WRONG:
memory = SqliteSaver.from_conn_string(":memory:")

# CORRECT:
from pathlib import Path
checkpoint_dir = Path("checkpoints")
checkpoint_dir.mkdir(exist_ok=True)
memory = SqliteSaver.from_conn_string(
    str(checkpoint_dir / "decomposition_state.db")
)
```

### Appendix B: LLM Model Assignments

| Node | Primary Model | Context Window | Cost (1M tokens) | Rationale |
|------|---------------|----------------|------------------|-----------|
| **Extract** | gemini-2.5-flash-lite | 1M tokens | $0.075 | Ultra-fast, handles 88K+ token PDFs |
| **Analyze** | claude-sonnet-3-5 | 200K tokens | $3.00 | Architectural reasoning excellence |
| **Decompose** | gpt-5-nano | 32K+ tokens | $0.15 | No TPM limits, cost-efficient |
| **Validate** | gemini-2.5-flash | 1M tokens | $0.15 | Best price-performance for QA |

**Fallback Chains:**
- Extract: gemini-2.5-flash-lite → gpt-4o-mini
- Analyze: claude-sonnet-3-5 → gemini-1.5-pro
- Decompose: gpt-5-nano → gpt-4o-mini
- Validate: gemini-2.5-flash → claude-3-5-haiku

### Appendix C: Quality Dimension Weights

**4-Dimension (Generic Domain):**
```python
QUALITY_WEIGHT_COMPLETENESS = 0.25
QUALITY_WEIGHT_CLARITY = 0.25
QUALITY_WEIGHT_TESTABILITY = 0.25
QUALITY_WEIGHT_TRACEABILITY = 0.25
```

**5-Dimension (Domain-Aware):**
```python
QUALITY_WEIGHT_COMPLETENESS = 0.20
QUALITY_WEIGHT_CLARITY = 0.20
QUALITY_WEIGHT_TESTABILITY = 0.20
QUALITY_WEIGHT_TRACEABILITY = 0.20
QUALITY_WEIGHT_DOMAIN_COMPLIANCE = 0.20
```

### Appendix D: Success Metrics

#### Technical Metrics
- ✅ **Quality Score:** ≥ 0.85 average for generated requirements
- ✅ **Traceability:** 100% parent-child coverage
- ✅ **Performance:** < 5 minutes end-to-end for typical specification
- ✅ **Cost:** < $2 per decomposition run
- ✅ **Reliability:** ≥ 95% success rate without errors
- ✅ **Uptime:** 99.9% availability (web application)
- ✅ **Real-time Latency:** < 500ms for SSE events
- ✅ **Page Load:** < 2 seconds

#### Business Metrics
- ✅ **Time Savings:** 70% reduction vs. manual decomposition
- ✅ **Consistency:** Reduced variance in requirement quality
- ✅ **Scalability:** Can process 100+ system requirements
- ✅ **Usability:** Non-experts can use with < 1 hour training
- ✅ **Concurrent Users:** Handles 100+ simultaneous workflows

### Appendix E: Docker Deployment Configuration

**File:** `docker-compose.yml`

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
      - NEXT_PUBLIC_API_URL=http://backend:8000
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
    ports:
      - '5432:5432'

  redis:
    image: redis:7-alpine
    ports:
      - '6379:6379'

volumes:
  postgres_data:
```

### Appendix F: Command Reference

#### Running the Backend Engine (CLI)
```bash
cd engine
source venv/bin/activate

# Basic execution
python main.py examples/sample_spec.md --subsystem "Train Management"

# With domain context
python main.py spec.pdf \
  --subsystem "Train Management" \
  --domain "csx_dispatch" \
  --subsystem-id "train_management"

# With custom configuration
python main.py spec.docx \
  --subsystem "Navigation System" \
  --max-iterations 5 \
  --quality-threshold 0.85

# Resume from checkpoint
python main.py --resume <checkpoint_id>
```

#### Running the Web Application (Development)
```bash
# Start all services
docker-compose up

# Or run separately:

# Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm run dev
```

#### Testing
```bash
# Backend tests
cd engine
pytest tests/ -v

# Frontend tests
cd frontend
npm test

# E2E tests
npm run test:e2e
```

### Appendix G: Future Enhancements (Post-MVP)

**Phase 13: Authentication & Multi-tenancy**
- User accounts (NextAuth.js)
- Team workspaces
- Project management
- Role-based access control

**Phase 14: Advanced Features**
- Requirement editing and refinement in UI
- Comparison between workflow runs
- Export to DOORS/Polarion/Jira
- PDF generation with custom branding
- Email notifications

**Phase 15: Collaboration**
- Real-time collaborative review
- Comments and annotations
- Approval workflows
- Version history and diffs

**Phase 16: Analytics Dashboard**
- Quality trends over time
- Cost analysis and optimization
- Model performance comparison
- Usage statistics and insights

**Phase 17: Integrations**
- Jira/Linear integration
- GitHub/GitLab sync
- Slack/Teams notifications
- REST API for external tools
- Webhook support

---

## Contact and Support

**Project Lead:** Michael Sweatt
**Email:** mdsweatt@gmail.com
**Website:** https://www.mikescorner.io/

For questions, issues, or contributions, please refer to the project repository.

---

**END OF COMPREHENSIVE IMPLEMENTATION PLAN v2.2**
