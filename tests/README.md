# Testing Strategy & Guidelines

This document describes the comprehensive testing approach for the Requirements Development Agentic Workflow project.

## Overview

**Total Tests:** 290+ tests across all phases
**Test Framework:** pytest
**Current Pass Rate:** 100% (7/7 E2E tests passing)
**Test Markers:** `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.phaseN`

## Test Structure

### Test Organization

```
tests/
├── __init__.py
├── conftest.py                     # Shared fixtures and configuration
├── fixtures/                       # Test data and mock responses
│   └── requirements_quality_samples.json
├── test_nodes.py                   # Node functionality tests
├── test_agents.py                  # Agent tests
├── test_skills.py                  # Skill effectiveness tests
├── test_integration.py             # Integration tests
├── test_energy_tracking.py         # Energy tracking tests
├── test_cost_tracking.py           # Cost tracking tests
├── test_quality_tracking.py        # Quality tracking tests
└── test_end_to_end.py             # Full workflow tests
```

## Test Categories

### 1. Unit Tests

**Purpose:** Test individual components in isolation
**Speed:** Fast (5-6 seconds total)
**Cost:** Free (uses mocks, no API calls)
**Marker:** `@pytest.mark.unit`

#### Coverage Areas

**Node Tests (`test_nodes.py`):**
- Individual node functionality
- State transformations
- Error handling
- Input validation
- Output structure

**Agent Tests (`test_agents.py`):**
- Agent prompt generation
- LLM response parsing
- Skill integration
- Fallback logic
- Error taxonomy handling

**Skill Tests (`test_skills.py`):**
- Skill loading
- Skill validation
- Version compatibility
- Example verification

**Utility Tests:**
- Document parsing (txt, docx, pdf)
- Quality checking
- Traceability matrix generation
- Cost estimation
- Energy calculation

#### Running Unit Tests

```bash
# Run all unit tests
pytest -m unit

# Run with coverage
pytest -m unit --cov=src --cov-report=html

# Run specific test file
pytest tests/test_nodes.py -v
```

### 2. Integration Tests

**Purpose:** Test component interactions
**Speed:** Moderate (~30 seconds)
**Cost:** Low (uses mocked LLM responses where possible)
**Marker:** `@pytest.mark.integration`

#### Coverage Areas

- Node-to-node communication
- State persistence and restoration
- Quality gate loops
- Refinement feedback flow
- Human review interrupts
- Checkpoint system
- Multi-model fallback chains

#### Running Integration Tests

```bash
# Run all integration tests
pytest -m integration

# Run specific integration test
pytest tests/test_integration.py::test_quality_gate_loop -v
```

### 3. End-to-End Tests

**Purpose:** Validate full workflow with real LLM calls
**Speed:** Slow (2-5 minutes per test)
**Cost:** ~$0.08 per complete run (real API calls)
**Marker:** `@pytest.mark.e2e`

#### Coverage Areas

- Complete decomposition workflow
- Large document processing (88K+ tokens)
- Multi-iteration refinement
- Quality validation
- Traceability generation
- Output document creation
- Error recovery

#### Test Cases

1. **Happy Path:** Successful decomposition without intervention
2. **Quality Gate Failure:** Revision loop with quality improvement
3. **Human Review:** Interrupt and resume workflow
4. **Large Document:** 88K+ token PDF processing
5. **Zero Requirements:** Valid empty decomposition result
6. **Error Handling:** Graceful failure and recovery
7. **Multi-Iteration:** Multiple refinement cycles

#### Running E2E Tests

```bash
# Run all E2E tests (requires API keys)
pytest -m e2e

# Run single E2E test
pytest tests/test_end_to_end.py::test_happy_path -v -s

# Skip slow tests
pytest -m "not e2e"
```

## Test Execution

### Running All Tests

```bash
# Run entire test suite
pytest

# Run with verbose output
pytest -v

# Run with output capture disabled (see prints)
pytest -s

# Run specific phase tests
pytest -m phase1
pytest -m phase2
# ... etc
```

### Test Markers

```python
# Available markers
@pytest.mark.unit           # Fast, mocked unit tests
@pytest.mark.integration    # Component interaction tests
@pytest.mark.e2e           # End-to-end workflow tests
@pytest.mark.phase0        # Phase 0 specific tests
@pytest.mark.phase1        # Phase 1 specific tests
# ... through phase6
@pytest.mark.slow          # Tests that take >10 seconds
@pytest.mark.expensive     # Tests that cost money (API calls)
```

### Combining Markers

```bash
# Run all unit and integration tests (skip E2E)
pytest -m "unit or integration"

# Run only fast, cheap tests
pytest -m "unit and not expensive"

# Run phase-specific tests
pytest -m "phase4 or phase5"
```

## Mocking Strategy

### When to Mock

✅ **Mock in Unit Tests:**
- LLM API calls (use fixtures with expected responses)
- File I/O operations (use temporary files or mocks)
- External dependencies
- Time-consuming operations

❌ **Don't Mock in E2E Tests:**
- Real LLM API calls (validate actual behavior)
- Actual file operations (use temp directories)
- Real state persistence

### Mock Fixtures

Located in `conftest.py`:

```python
@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing"""
    return {
        "requirements": [...],
        "analysis": {...}
    }

@pytest.fixture
def mock_quality_score():
    """Mock quality metrics"""
    return {
        "completeness": 0.85,
        "clarity": 0.90,
        "testability": 0.80,
        "traceability": 0.95
    }
```

### Using Fixtures

```python
def test_node_execution(mock_llm_response, mock_quality_score):
    """Test node with mocked dependencies"""
    result = node.execute(state, llm_response=mock_llm_response)
    assert result["quality_metrics"] == mock_quality_score
```

## Test Data

### Fixtures Directory

Test data located in `tests/fixtures/`:

- `requirements_quality_samples.json` - Quality calibration dataset
- `sample_specs/` - Test specification documents
  - `simple_spec.txt` - 5 clear requirements
  - `medium_spec.txt` - 15 requirements with ambiguity
  - `complex_spec.txt` - 30+ requirements, poor formatting
  - `large_spec.pdf` - 88K+ token document
- `expected_outputs/` - Ground truth for validation
  - `simple_expected.json`
  - `medium_expected.json`
  - `complex_expected.json`

### Creating Test Data

```bash
# Generate synthetic requirements (using Gemini CLI)
gemini -p "Generate 10 simple navigation system requirements"

# Note: Save output manually to test fixtures
```

## Quality Metrics Testing

### Quality Threshold

**Default:** 0.80 (configurable per test)

Tests validate:
- Completeness scoring accuracy
- Clarity detection
- Testability verification
- Traceability validation

### Quality Test Cases

```python
# Test quality gate enforcement
def test_quality_gate_pass():
    """Requirements with score ≥0.80 should pass"""

def test_quality_gate_fail():
    """Requirements with score <0.80 should trigger refinement"""

def test_refinement_loop():
    """Refinement should improve quality scores"""

def test_max_iterations():
    """Loop should terminate after max_iterations"""
```

## Cost & Energy Testing

### Cost Tracking Tests

Located in `tests/test_cost_tracking.py`:

- Cost calculation accuracy (±30% tolerance)
- Budget warning thresholds
- Budget max enforcement
- Multi-provider token extraction
- Historical cost tracking

### Energy Tracking Tests

Located in `tests/test_energy_tracking.py`:

- Energy coefficient validation
- Token-based estimation accuracy
- PUE factor application
- Contextual comparison calculations
- Edge case handling (zero tokens)

## Continuous Integration

### GitHub Actions (Future)

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run unit tests
        run: pytest -m unit
      - name: Run integration tests
        run: pytest -m integration
      # E2E tests run on main branch only (cost control)
```

## Test Coverage

### Coverage Goals

- **Unit Tests:** ≥90% code coverage
- **Integration Tests:** All node interactions
- **E2E Tests:** All workflow paths

### Generating Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# View report
open htmlcov/index.html

# Generate terminal report
pytest --cov=src --cov-report=term-missing
```

## Debugging Tests

### Verbose Output

```bash
# Show all output
pytest -v -s

# Show only failed tests
pytest -v --tb=short

# Drop into debugger on failure
pytest --pdb
```

### Logging

```bash
# Enable logging output
pytest --log-cli-level=DEBUG

# Capture logs to file
pytest --log-file=test.log
```

## Common Test Patterns

### Testing State Transitions

```python
def test_state_transition():
    """Verify state changes correctly"""
    initial_state = create_initial_state(...)
    result_state = node.execute(initial_state)

    assert result_state["validation_passed"] is True
    assert "quality_metrics" in result_state
```

### Testing Error Handling

```python
def test_error_recovery():
    """Verify graceful error handling"""
    with pytest.raises(CustomError):
        node.execute(invalid_state)

    # Or test fallback
    result = node.execute_with_fallback(state)
    assert result["fallback_count"] == 1
```

### Testing Async Operations

```python
@pytest.mark.asyncio
async def test_async_node():
    """Test asynchronous node execution"""
    result = await async_node.execute(state)
    assert result["status"] == "completed"
```

## Test Maintenance

### Updating Tests

When modifying code:
1. Run affected tests first
2. Update test fixtures if state schema changes
3. Update mocks if API contracts change
4. Add new tests for new features
5. Remove obsolete tests

### Test Review Checklist

Before committing:
- [ ] All tests passing locally
- [ ] New features have tests
- [ ] Coverage hasn't decreased
- [ ] No skipped tests without justification
- [ ] Test names are descriptive
- [ ] Fixtures are reusable

## Known Test Limitations

### Gemini Free Tier

- 250K tokens/min quota
- Test 3 (large document) may require paid tier or delays
- Use `pytest -k "not large_document"` to skip

### Flaky Tests

Currently no known flaky tests. If encountered:
1. Document in issue tracker
2. Add `@pytest.mark.flaky(reruns=3)` marker
3. Investigate root cause

## Resources

### pytest Documentation

- **pytest Docs:** https://docs.pytest.org/
- **Fixtures:** https://docs.pytest.org/en/stable/fixture.html
- **Markers:** https://docs.pytest.org/en/stable/mark.html

### Project Testing Docs

- **Phase Test Results:** `docs/phases/phaseN/README.md`
- **API Documentation:** `docs/api_documentation.md`
- **User Guide:** `docs/user_guide.md`

## Getting Help

### Running Specific Tests

```bash
# List all available tests
pytest --collect-only

# List all markers
pytest --markers

# Get help
pytest --help
```

### Common Issues

**Issue:** Tests fail with API key errors
**Solution:** Ensure `.env` file exists with valid API keys

**Issue:** E2E tests timeout
**Solution:** Increase timeout or check network connectivity

**Issue:** Import errors
**Solution:** Run `pip install -e .` to install package in editable mode

---

**Last Updated:** November 15, 2025
**Test Suite Version:** 1.0
**Total Tests:** 290+
**Pass Rate:** 100% (E2E)
