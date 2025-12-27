# ReqDecompose Frontend

Next.js 14 frontend application for the Requirements Decomposition system. Provides a modern web interface for uploading specifications, monitoring workflow execution in real-time, and analyzing decomposition results.

## ✅ Implementation Status: COMPLETE

All 4 screens implemented and fully functional:
- **Landing Page** (Screen 1) - Hero, workflow cards, recent workflows
- **Upload & Configure** (Screen 4) - File upload, configuration panel
- **Progress Monitor** (Screen 3) - Real-time SSE, pipeline viz, log stream
- **Results Dashboard** (Screen 2) - Metrics, requirements table, export

## Quick Start

### Prerequisites

- Node.js 20+
- Backend API running at `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Environment Configuration

Edit `.env.local`:

```bash
# Backend API URL (default: http://localhost:8000)
NEXT_PUBLIC_API_URL=http://localhost:8000

# API Key (must match backend API_KEY)
NEXT_PUBLIC_API_KEY=dev-key-12345
```

## Tech Stack

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript 5
- **Styling:** Tailwind CSS + shadcn/ui
- **State:** TanStack Query (server) + Zustand (client)
- **Real-time:** EventSource (SSE)
- **Icons:** Lucide React
- **HTTP:** Axios

## Routes

- `/` - Landing page
- `/upload` - Upload & configure workflow
- `/progress/{workflowId}` - Real-time progress monitoring
- `/results/{workflowId}` - Results dashboard

## Features

### Landing Page
- Animated hero section
- 4 workflow stage cards
- Recent workflows table (auto-refresh)
- Empty states and loading skeletons

### Upload & Configure
- Drag-and-drop file upload (PDF, DOCX, TXT)
- Domain selection (Aerospace, Automotive, Medical, etc.)
- Analysis mode (Standard/Thorough)
- Review mode (Before/After)
- Form validation and error handling

### Progress Monitor
- **Real-time SSE connection** with auto-reconnect
- 4-stage pipeline visualization
- Live log stream with 3 tabs
- Generated requirements preview
- Cancel workflow functionality
- Auto-redirect on completion

### Results Dashboard
- 6 metric cards (extracted, generated, quality, time, cost, energy)
- Quality dimension breakdown
- Sortable requirements table with search
- Traceability focus panel
- Quality issues panel
- Export (MD, DOCX, CSV, JSON, ZIP)

## API Integration

### REST Endpoints

```typescript
POST   /api/workflows/upload        # Upload file and create workflow
POST   /api/workflows/{id}/start    # Start execution
GET    /api/workflows/{id}/status   # Get status
GET    /api/workflows/{id}/results  # Get results
GET    /api/workflows/recent        # List recent
POST   /api/workflows/{id}/cancel   # Cancel workflow
GET    /api/workflows/{id}/export   # Export results
```

### Server-Sent Events

```typescript
GET /api/workflows/{id}/stream

Events:
- workflow_started
- node_started, node_completed
- progress_update
- workflow_completed, workflow_failed
```

## Development

```bash
npm run dev      # Development server (http://localhost:3000)
npm run build    # Production build
npm run start    # Production server
npm run lint     # ESLint
```

## Production Build

```bash
npm run build
npm start
```

## Docker Deployment

See main project `docker-compose.yml` for multi-container setup.

```bash
# From project root
docker-compose up --build

# Frontend: http://localhost:3000
# API: http://localhost:8000
```

## Design System

### Dark Theme Colors

```css
--bg-primary: #0D1117        /* Main background */
--bg-secondary: #161B22      /* Cards */
--bg-tertiary: #21262D       /* Inputs */

--accent-blue: #388BFD       /* Primary actions */
--accent-green: #34D399      /* Success */
--accent-red: #F87171        /* Errors */
--accent-yellow: #FBBF24     /* Warnings */
```

### Typography

- **Sans:** Inter
- **Mono:** JetBrains Mono

## Troubleshooting

### Port already in use
```bash
lsof -ti:3000 | xargs kill -9
```

### API connection refused
1. Check backend is running: `curl http://localhost:8000/health`
2. Verify `NEXT_PUBLIC_API_URL` in `.env.local`
3. Check CORS settings in backend

### Build errors
```bash
rm -rf .next node_modules package-lock.json
npm install
npm run build
```

## Project Structure

```
src/
├── app/                  # Next.js pages (App Router)
├── components/           # React components
│   ├── ui/              # shadcn/ui (17 components)
│   ├── layout/          # Header, Breadcrumbs, PageShell
│   ├── landing/         # Landing page components
│   ├── upload/          # Upload page components
│   ├── progress/        # Progress page components
│   ├── results/         # Results page components
│   └── shared/          # Reusable components
├── lib/                 # Utilities
│   ├── api.ts          # Axios client
│   ├── queries.ts      # TanStack Query hooks
│   ├── sse.ts          # SSE connection manager
│   └── utils.ts        # Helper functions
└── types/              # TypeScript types
```

## Documentation

For detailed implementation plan, see:
- `/docs/implementation/reqdecompose-ui-ux-spec.md`
- `/Users/mdsweatt/.claude/plans/structured-sparking-reef.md`

## License

See main project LICENSE.
