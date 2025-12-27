# ReqDecompose API

FastAPI web service layer for the Requirements Decomposition System.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements-api.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update the configuration:

```bash
cp .env.example .env
```

Key settings:
- `API_KEY` - Change from default for production
- `CORS_ORIGINS` - Add your frontend URL
- `DATABASE_URL` - SQLite database path
- `UPLOAD_DIR` - Directory for uploaded files

### 3. Start the Server

**Development:**
```bash
python -m uvicorn api.main:app --reload --port 8000
```

**Production:**
```bash
gunicorn api.main:app \
  --workers 1 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 300
```

**IMPORTANT:** Use `--workers 1` for Phase 1. Multi-worker support requires Phase 2 (Redis-backed job queue).

### 4. Verify Installation

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "ReqDecompose API",
  "version": "1.0.0"
}
```

## API Documentation

Once the server is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Endpoints

### Public Endpoints
- `GET /` - API information
- `GET /health` - Health check

### Protected Endpoints (Require API Key)

All endpoints require `Authorization: Bearer {API_KEY}` header.

#### Workflow Management
- `POST /api/workflows/upload` - Upload spec document and create workflow
- `POST /api/workflows/{id}/start` - Start workflow execution (async, Phase 2)
- `GET /api/workflows/{id}/status` - Get workflow status
- `GET /api/workflows/{id}/stream` - Stream real-time progress via SSE (Phase 2)
- `POST /api/workflows/{id}/cancel` - Cancel running workflow (Phase 2)
- `GET /api/workflows/{id}/results` - Get full workflow results (Phase 3)
- `GET /api/workflows/{id}/export?format={md|docx|csv|json|zip}` - Export results (Phase 3)
- `GET /api/workflows/recent?limit=10` - List recent workflows

## Implementation Status

✅ **Phase 1 Complete:**
- File upload (PDF, DOCX, TXT)
- Workflow creation and storage
- Synchronous execution (blocks until completion)
- Status polling
- Recent workflows list
- API key authentication
- CORS support
- Database persistence

✅ **Phase 2 Complete:**
- Asynchronous execution (background jobs with asyncio)
- Server-Sent Events (SSE) for real-time progress
- Workflow cancellation
- Event buffering for reconnections

✅ **Phase 3 Complete:**
- Results endpoint with full workflow details
- Export functionality (MD, DOCX, CSV, JSON, ZIP)
- State transformation (snake_case → camelCase)
- Enhanced error handling and logging

## Example Usage

### 1. Create Workflow

```bash
curl -X POST "http://localhost:8000/api/workflows/upload" \
  -H "Authorization: Bearer dev-key-12345" \
  -F "file=@spec.pdf" \
  -F "subsystem=Navigation Subsystem" \
  -F "domain=aerospace" \
  -F "review_mode=before" \
  -F "analysis_mode=thorough" \
  -F "quality_threshold=0.85" \
  -F "max_iterations=3"
```

Response:
```json
{
  "workflowId": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Workflow created successfully"
}
```

### 2. Start Workflow (Async)

```bash
curl -X POST "http://localhost:8000/api/workflows/{workflowId}/start" \
  -H "Authorization: Bearer dev-key-12345"
```

**Phase 2:** Returns immediately with `{"workflowId": "...", "status": "processing"}`. Use `/stream` endpoint for real-time progress.

### 3. Check Status

```bash
curl -H "Authorization: Bearer dev-key-12345" \
  "http://localhost:8000/api/workflows/{workflowId}/status"
```

### 4. Stream Real-Time Progress (Phase 2)

```bash
curl -N --no-buffer -H "Authorization: Bearer dev-key-12345" \
  "http://localhost:8000/api/workflows/{workflowId}/stream"
```

**Events:** workflow_started, workflow_completed, workflow_failed

### 5. Cancel Workflow (Phase 2)

```bash
curl -X POST "http://localhost:8000/api/workflows/{workflowId}/cancel" \
  -H "Authorization: Bearer dev-key-12345"
```

### 6. Get Full Results (Phase 3)

```bash
curl -H "Authorization: Bearer dev-key-12345" \
  "http://localhost:8000/api/workflows/{workflowId}/results"
```

**Returns:** Full workflow details including:
- Extracted and decomposed requirements (camelCase format)
- Quality metrics with dimension scores
- Validation issues and suggestions
- Traceability matrix
- System context and decomposition strategy
- Cost, timing, and energy breakdowns

### 7. Export Results (Phase 3)

```bash
# Export as Markdown
curl -H "Authorization: Bearer dev-key-12345" \
  "http://localhost:8000/api/workflows/{workflowId}/export?format=md" \
  -o report.md

# Export as Word document
curl -H "Authorization: Bearer dev-key-12345" \
  "http://localhost:8000/api/workflows/{workflowId}/export?format=docx" \
  -o report.docx

# Export as CSV (requirements table)
curl -H "Authorization: Bearer dev-key-12345" \
  "http://localhost:8000/api/workflows/{workflowId}/export?format=csv" \
  -o requirements.csv

# Export as JSON (full state)
curl -H "Authorization: Bearer dev-key-12345" \
  "http://localhost:8000/api/workflows/{workflowId}/export?format=json" \
  -o data.json

# Export as ZIP (all formats bundled)
curl -H "Authorization: Bearer dev-key-12345" \
  "http://localhost:8000/api/workflows/{workflowId}/export?format=zip" \
  -o export.zip
```

**Supported formats:**
- `md` - Markdown report with requirements, quality metrics, issues
- `docx` - Word document (same content as Markdown)
- `csv` - Requirements table (id, text, category, priority, parent, rationale, acceptance criteria)
- `json` - Full workflow state and results
- `zip` - All four formats bundled together

### 8. List Recent Workflows

```bash
curl -H "Authorization: Bearer dev-key-12345" \
  "http://localhost:8000/api/workflows/recent?limit=10"
```

## Architecture

```
api/
├── main.py              # FastAPI app entrypoint
├── config.py            # Configuration
├── models/
│   ├── database.py      # SQLAlchemy ORM models
│   ├── requests.py      # Request DTOs
│   └── responses.py     # Response DTOs (camelCase)
├── routes/
│   ├── health.py        # Health check
│   └── workflows.py     # Workflow endpoints
├── services/            # Phase 2 & 3
│   ├── workflow_runner.py  # Async execution
│   ├── sse_manager.py      # SSE event broadcasting
│   └── export_service.py   # Multi-format export (Phase 3)
├── middleware/
│   ├── auth.py          # API key authentication
│   └── error_handler.py # Exception handling
└── utils/
    ├── file_handler.py      # File upload utilities
    └── state_transformer.py # snake_case ↔ camelCase (Phase 3)
```

## Database

SQLite database at `checkpoints/workflow_runs.db`.

**Schema:**
- `workflow_runs` - Workflow metadata and results

**Migrations:** Not yet implemented. Schema created on startup via `init_db()`.

## Security

**Phase 1:** Simple API key authentication
- Set `API_KEY` in `.env`
- Include in requests: `Authorization: Bearer {API_KEY}`

**Production Recommendations:**
- Use strong, random API keys
- Enable HTTPS (reverse proxy)
- Implement rate limiting
- Consider OAuth2 for external access (Phase 4)

## Troubleshooting

### Server won't start
- Check port 8000 is available
- Verify all dependencies installed: `pip install -r requirements-api.txt`
- Check `.env` file exists with required settings

### Authentication fails
- Verify `API_KEY` in `.env` matches request header
- Ensure header format: `Authorization: Bearer {key}`

### File upload fails
- Check file type is allowed (.txt, .docx, .pdf)
- Verify file size < 20MB (configurable via `MAX_UPLOAD_SIZE_MB`)
- Ensure `UPLOAD_DIR` is writable

### Workflow execution hangs
- Normal for Phase 1 (synchronous execution)
- Expect 30s-5min depending on document size
- Phase 2 will add async execution

## Development

### Running Tests

```bash
pytest tests/test_api*.py -v
```

### Linting

```bash
# Coming in Phase 3
```

## Next Steps

See `/Users/mdsweatt/.claude/plans/structured-sparking-reef.md` for the complete implementation plan.

**Phase 2 Goals:**
- Async workflow execution
- SSE real-time progress streaming
- Workflow cancellation
- Enhanced observability
