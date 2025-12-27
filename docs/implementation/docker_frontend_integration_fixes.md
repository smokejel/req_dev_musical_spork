# Docker & Frontend Integration Fixes - Dec 23, 2025

This document summarizes the troubleshooting and resolution of Docker deployment and Frontend-Backend integration issues.

## 1. Docker Compose & Service Orchestration

### Added `req-decomp` Service
- **Issue:** The `docker-compose.override.yml` referenced a `req-decomp` service that was missing from the main `docker-compose.yml`.
- **Fix:** Added the `req-decomp` CLI service to `docker-compose.yml`, configured to build from the root `Dockerfile`.
- **Cleanup:** Removed obsolete `version: '3.8'` keys from both compose files to eliminate deprecation warnings.

### Database Connection Stability
- **Issue:** The API failed to start with `sqlite3.OperationalError: unable to open database file`.
- **Fix:** Updated `DATABASE_URL` in `docker-compose.yml` to use an absolute path with four slashes (`sqlite:////app/checkpoints/workflow_runs.db`). This ensures SQLAlchemy correctly locates the volume-mounted database inside the container.

## 2. Docker Image Build Fixes

### Multi-stage Build & Dependency Resolution
- **Issue:** Build failed because `requirements-api.txt` was not found during the `pip install` step in both `api/Dockerfile` and the root `Dockerfile`.
- **Fix:** 
  - Corrected `COPY` instructions to reference `requirements-api.txt` from the root context.
  - Ensured `requirements-api.txt` is copied *before* the `pip install -r requirements.txt` command, as the latter contains a relative reference (`-r requirements-api.txt`).

### Frontend Environment Variables
- **Issue:** Next.js was built without the `NEXT_PUBLIC_API_KEY`, causing `401 Unauthorized` errors when the client attempted to call the backend.
- **Fix:** 
  - Modified `reqdecompose-frontend/Dockerfile` to accept `ARG NEXT_PUBLIC_API_KEY`.
  - Updated `docker-compose.yml` to pass the `API_KEY` from the environment as a build argument.
  - This ensures the API key is baked into the static bundle during `npm run build`.

## 3. Frontend-Backend Data Alignment

### Resolved Client-Side Exceptions
- **Issue:** Browsing to `localhost:3000` resulted in an "Application error: a client-side exception has occurred".
- **Root Cause:** A mismatch between the backend Pydantic model and frontend TypeScript interfaces. The backend returned `id` and `createdAt` (via aliases), while the frontend expected `workflowId` and `dateCreated`. This caused `formatRelativeTime(undefined)` to throw a `RangeError`.
- **Fix:**
  - Updated `reqdecompose-frontend/src/types/api.ts` to use `id` and `createdAt`.
  - Updated `RecentWorkflowsTable.tsx` to utilize these correct field names for rendering and linking.

## Current Status
- [x] Docker images build successfully.
- [x] API server starts and initializes SQLite database correctly.
- [x] Frontend successfully authenticates with backend using correct API keys.
- [x] Recent Workflows list renders without crashing.
- [x] CLI `req-decomp` tool is accessible via `docker-compose run`.

## Next Steps for Production
- Change `API_KEY` from the default `change-this-in-production-12345`.
- Ensure `CORS_ORIGINS` are restricted to the production domain.
- Rotate all LLM API keys regularly.
