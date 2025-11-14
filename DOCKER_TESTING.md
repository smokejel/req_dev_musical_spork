# Docker Deployment Testing Guide

## Prerequisites

1. **Start Docker Desktop:**
   - Open Docker Desktop application
   - Wait for Docker to start (icon in menu bar should show "Docker Desktop is running")
   - Verify: `docker --version`

2. **API Keys Configured:**
   - Ensure `.env` file exists with all required keys
   - Copy from template: `cp .env.docker.example .env` (if needed)

## Testing Steps

### 1. Build the Docker Image

```bash
# Build with docker-compose (recommended)
docker-compose build

# OR build directly
docker build -t req-decomp:latest .
```

**Expected Output:**
- Multi-stage build process (builder + runtime)
- Image size: ~400MB
- No errors during dependency installation

**Verify Build:**
```bash
docker images | grep req-decomp
```

Should show:
```
req-decomp    latest    <image-id>    <time>    ~400MB
```

### 2. Test Basic Execution

```bash
# Test help command
docker-compose run req-decomp

# Expected: Help message displayed
```

**Expected Output:**
```
Requirements Decomposition System
AI-Powered Requirements Engineering

Usage: main.py [OPTIONS] SPEC_PATH
...
```

### 3. Test Simple Decomposition

```bash
# Run with simple example
docker-compose run req-decomp \
  python main.py examples/phase0_simple_spec.txt --subsystem "Authentication"
```

**Expected Output:**
- ✓ LangSmith tracing status
- Workflow execution progress (Extract, Analyze, Decompose, Validate)
- Quality score displayed (should be ≥0.80)
- Cost tracking ($0.001-$0.050 range)
- Output files created in `outputs/run_*` directory

**Verify Output:**
```bash
ls -lh outputs/run_*
```

Should show:
```
requirements.md
traceability.csv
quality_report.md
README.txt
```

### 4. Test Volume Mounts

**Verify all volumes are mounted correctly:**

```bash
docker-compose run req-decomp ls -la /app/

# Should show:
# - examples/ (mounted read-only)
# - outputs/ (mounted read-write)
# - checkpoints/ (mounted read-write)
# - data/ (mounted read-write)
# - scripts/ (mounted read-only)
```

**Test data persistence:**

```bash
# Run decomposition
docker-compose run req-decomp \
  python main.py examples/phase0_simple_spec.txt --subsystem "Auth"

# Check cost database was created
ls -lh data/

# Expected: cost_history.db and quality_history.db
```

### 5. Test Interactive Mode

```bash
# Drop into shell
docker-compose run req-decomp /bin/bash

# Inside container, run commands:
ls -la
python main.py --help
exit
```

### 6. Test Development Mode

**With docker-compose.override.yml:**

```bash
# Make a small change to src/ (local filesystem)
echo "# Test comment" >> src/state.py

# Run without rebuild - changes should be reflected
docker-compose run req-decomp python -c "import src.state; print('Development mode works!')"

# Clean up
git checkout src/state.py
```

### 7. Test Cost Tracking

```bash
# Run decomposition with LangSmith enabled
docker-compose run req-decomp \
  python main.py examples/phase0_simple_spec.txt --subsystem "Auth"

# Check cost database
ls -lh data/cost_history.db

# Generate cost report
docker-compose run req-decomp \
  python scripts/generate_reports.py --days 7
```

**Expected:**
- Cost report displays recent runs
- Token counts and costs tracked
- Source method: "langsmith" or "heuristic"

### 8. Test Error Handling

**Missing API keys:**

```bash
# Temporarily rename .env
mv .env .env.backup

# Run - should fail gracefully
docker-compose run req-decomp \
  python main.py examples/phase0_simple_spec.txt --subsystem "Auth"

# Expected: Clear error message about missing API keys

# Restore .env
mv .env.backup .env
```

### 9. Test with Different Input Formats

```bash
# TXT format
docker-compose run req-decomp \
  python main.py examples/phase0_simple_spec.txt --subsystem "Auth"

# DOCX format (if available)
# docker-compose run req-decomp \
#   python main.py examples/spec.docx --subsystem "Power"

# PDF format (if available)
# docker-compose run req-decomp \
#   python main.py examples/spec.pdf --subsystem "Navigation"
```

### 10. Test Direct Docker Commands

**Without docker-compose:**

```bash
docker run --rm \
  --env-file .env \
  -v $(pwd)/examples:/app/examples:ro \
  -v $(pwd)/outputs:/app/outputs \
  -v $(pwd)/checkpoints:/app/checkpoints \
  -v $(pwd)/data:/app/data \
  req-decomp:latest \
  python main.py examples/phase0_simple_spec.txt --subsystem "Authentication"
```

**Expected:** Same output as docker-compose run

## Troubleshooting

### Docker Daemon Not Running

**Error:**
```
Cannot connect to the Docker daemon at unix://...
```

**Solution:**
- Start Docker Desktop application
- Wait for Docker to fully start
- Verify: `docker ps` should not error

### Permission Denied on Volume Mounts

**Error:**
```
Permission denied: '/app/outputs/...'
```

**Solution:**
```bash
# Ensure directories exist and are writable
mkdir -p outputs checkpoints data
chmod -R 755 outputs checkpoints data
```

### Image Build Fails

**Error:**
```
ERROR: failed to solve...
```

**Solution:**
```bash
# Clean Docker cache
docker system prune -a

# Rebuild
docker-compose build --no-cache
```

### Module Import Errors in Container

**Error:**
```
ModuleNotFoundError: No module named 'src'
```

**Solution:**
- Check that `PYTHONPATH=/app` is set in Dockerfile (should be)
- Verify `src/` directory is copied to image
- Rebuild image: `docker-compose build`

### Volume Mounts Not Working

**Symptom:** Changes to local files don't appear in container

**Solution:**
```bash
# For development mode, ensure docker-compose.override.yml exists
ls docker-compose.override.yml

# For production, rebuild image after code changes
docker-compose build
```

## Performance Benchmarks

Track these metrics during testing:

| Metric | Expected Value | Notes |
|--------|---------------|-------|
| Build time | 2-5 minutes | First build (no cache) |
| Build time (cached) | 30-60 seconds | Subsequent builds |
| Image size | ~400MB | Multi-stage optimized |
| Simple decomposition | 1-2 minutes | 5 requirements |
| Medium decomposition | 3-5 minutes | 15 requirements |
| Large PDF (88K tokens) | 5-10 minutes | 396 requirements |
| Cost per simple run | $0.001-$0.010 | Depends on LangSmith |
| Cost per large run | $0.030-$0.050 | With LangSmith enabled |

## Cleanup

```bash
# Remove containers
docker-compose down

# Remove image
docker rmi req-decomp:latest

# Clean all Docker artifacts (careful!)
docker system prune -a --volumes
```

## Sign-Off Checklist

- [ ] Docker image builds successfully
- [ ] Help command works
- [ ] Simple decomposition completes
- [ ] Output files created correctly
- [ ] All volume mounts working
- [ ] Interactive mode accessible
- [ ] Cost tracking databases created
- [ ] Development mode works (override.yml)
- [ ] Error handling graceful
- [ ] Performance within expected ranges

## Notes

- Docker daemon must be running for all tests
- API keys required for actual decomposition tests
- Large document tests require Gemini paid tier or delays
- Cost estimates require LangSmith for precision

## Next Steps After Testing

1. Tag release version: `docker tag req-decomp:latest req-decomp:v1.0`
2. Push to registry (Docker Hub, GitHub Container Registry, etc.)
3. Update deployment documentation with registry URL
4. Create production docker-compose.yml (without override)
