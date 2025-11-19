# LangSmith Studio Usage Guide

This guide explains how to use LangSmith Studio for interactive debugging and testing of the requirements decomposition workflow.

## What is LangSmith Studio?

LangSmith Studio is an **agent IDE** (Integrated Development Environment) that provides:

- **Visual Graph Execution** - See your 6-node workflow execute in real-time with node-by-node visualization
- **State Inspection** - View the complete `DecompositionState` at each workflow step
- **Time Travel Debugging** - Rewind execution to any point and inspect historical states
- **Interactive Testing** - Run workflows without command-line interface
- **LangSmith Tracing** - See detailed traces of every LLM call with token counts and costs
- **Thread Management** - Create multiple parallel test runs with different configurations

**Use Case:** Studio is ideal for development, debugging, and testing. For production batch processing, use the CLI (`main.py`).

---

## Quick Start

### 1. Install LangGraph CLI

```bash
pip install -U "langgraph-cli[inmem]"
```

### 2. Ensure Configuration is Ready

The project already includes the required `langgraph.json` configuration file at the project root.

**Verify it exists:**
```bash
ls langgraph.json
# Should show: langgraph.json
```

### 3. Configure Environment Variables

Ensure your `.env` file has the required API keys:

```bash
# Required LLM API Keys
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...

# Optional: Enable LangSmith Tracing for cost/token tracking
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_...  # Get from https://smith.langchain.com/settings
LANGCHAIN_PROJECT=requirements-decomposition
```

### 4. Start the Local Agent Server

```bash
langgraph dev
```

**Expected output:**
```
Ready!
- API: http://localhost:2024
- Docs: http://localhost:2024/docs
- LangSmith Studio Web UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
```

### 5. Access Studio

Click the Studio URL from the terminal output, or navigate to:

```
https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
```

You should see the "decomposition" graph available in the Studio interface.

---

## Running Your First Decomposition in Studio

### Step 1: Create a New Run

1. In Studio, select the **"decomposition"** graph
2. Click **"New Run"** or **"Create Thread"**
3. Choose **Graph Mode** (Chat Mode is not available for this workflow)

### Step 2: Provide Input

Studio will prompt for the initial state. Provide a JSON object with:

```json
{
  "spec_document_path": "examples/phase0_simple_spec.txt",
  "target_subsystem": "Navigation Subsystem",
  "review_before_decompose": false,
  "max_iterations": 3,
  "quality_threshold": 0.80
}
```

**Required Fields:**
- `spec_document_path` - Path to specification document (.txt, .docx, .pdf)
- `target_subsystem` - Subsystem name for decomposition

**Optional Fields:**
- `review_before_decompose` - Enable human review before decomposition (default: false)
- `max_iterations` - Maximum refinement iterations (default: 3)
- `quality_threshold` - Quality gate threshold 0.0-1.0 (default: 0.80)

### Step 3: Execute the Workflow

Click **"Run"** or **"Invoke"** to start execution.

You'll see:
- **Graph Visualization** - Nodes light up as they execute
- **Real-Time Progress** - Current node highlighted
- **State Updates** - State changes at each step

### Step 4: Inspect Results

After execution completes:

1. **View Final State** - See the complete `DecompositionState` output
2. **Check Decomposed Requirements** - Inspect `decomposed_requirements` array
3. **Review Quality Metrics** - Check `quality_metrics` scores
4. **Examine Traceability** - View `traceability_matrix` parent-child links
5. **Check Output Path** - Find generated documentation in `final_document_path`

---

## Studio Features & Debugging

### Visual Graph Execution

**What you see:**
- **6 workflow nodes** displayed as a flowchart
- **Conditional edges** showing routing logic
- **Current node highlighted** during execution
- **Completed nodes marked** with checkmarks

**Nodes:**
1. `extract` - Parse specification and extract requirements
2. `analyze` - Create decomposition strategy
3. `decompose` - Generate detailed requirements
4. `validate` - Quality assessment and scoring
5. `human_review` - Interactive review (auto-approves in Studio)
6. `document` - Generate final output

### State Inspection

**At any node, you can view:**

```json
{
  "spec_document_path": "examples/phase0_simple_spec.txt",
  "target_subsystem": "Navigation Subsystem",
  "extracted_requirements": [...],  // After extract node
  "system_context": {...},           // After analyze node
  "decomposition_strategy": {...},   // After analyze node
  "decomposed_requirements": [...],  // After decompose node
  "quality_metrics": {...},          // After validate node
  "validation_passed": true,         // After validate node
  "final_document_path": "outputs/run_20251118_143022_navigation/requirements.md"
}
```

**How to inspect:**
1. Click on any node in the graph
2. View the "State" tab
3. Expand JSON to see full state object

### Time Travel Debugging

**Rewind execution to any point:**

1. Use the **timeline slider** at the bottom of Studio
2. Drag to any execution point
3. Inspect state at that moment
4. Compare states across different nodes

**Use cases:**
- Debug why validation failed
- Check what strategy was generated
- Inspect requirements before vs. after refinement
- Identify where errors occurred

### LangSmith Tracing (Optional)

If `LANGCHAIN_TRACING_V2=true` in `.env`:

**You'll see:**
- **Every LLM call** traced individually
- **Token counts** (input + output)
- **Model used** (Gemini, Claude, GPT)
- **Latency** per call
- **Cost estimates** based on pricing

**How to access traces:**
1. Click **"View Trace"** button in Studio
2. Navigate to LangSmith dashboard
3. Filter by project name
4. Drill down into specific LLM calls

---

## Workflow Routing in Studio

### After Extract Node → Analyze Node
Always proceeds to analyze (no conditions).

### After Analyze Node

**Conditional routing based on `review_before_decompose`:**

```
If review_before_decompose = true:
  → human_review (pre-decomposition review)
  → decompose

If review_before_decompose = false:
  → decompose (direct)
```

**In Studio:** Human review auto-approves with message "Auto-approving for Studio/automated execution".

### After Decompose Node → Validate Node
Always proceeds to validate (no conditions).

### After Validate Node

**Conditional routing based on quality and iterations:**

```
If validation_passed = true:
  → document (generate final output)
  → END

If validation_passed = false AND iteration_count < max_iterations:
  → decompose (retry with refinement feedback)

If validation_passed = false AND iteration_count >= max_iterations:
  → human_review (quality gate failure)
```

**What you'll see in Studio:**
- **Pass:** Green path to document node
- **Revise:** Yellow loop back to decompose
- **Human Review:** Red path to human_review

### After Human Review Node

**Conditional routing based on feedback:**

```
If human_feedback = "approved":
  → document
  → END

If human_feedback starts with "revise:":
  → decompose (with human feedback)
```

**In Studio:** Auto-approves, proceeding directly to document.

### After Document Node → END
Workflow complete.

---

## Known Limitations

### 1. Chat Mode Unavailable

**Issue:** Your workflow state (`DecompositionState`) doesn't extend `MessagesState`.

**Impact:** Chat Mode option in Studio is grayed out.

**Workaround:** Use **Graph Mode** only (provides full features).

### 2. Human Review Auto-Approves

**Issue:** Interactive `input()` prompts don't work in non-interactive environments.

**Impact:** Human review node automatically approves instead of waiting for user input.

**Workaround:** For manual review, use CLI mode (`python main.py`). Studio is for automated testing.

**How it works:**
```python
except (EOFError, OSError):
    # Non-interactive environment detected
    human_feedback = "approved"
    decision_approved = True
```

### 3. File Path Dependencies

**Issue:** Specification documents must be accessible to the Agent Server.

**Impact:** If `spec_document_path` points to a file that doesn't exist on the server, extract node will fail.

**Workaround:**
- Use relative paths from project root (e.g., `examples/phase0_simple_spec.txt`)
- Ensure files are in the project directory
- For Docker: Mount volumes with document files

### 4. Rich Console Output Doesn't Display

**Issue:** Custom CLI progress bars and formatted tables use Rich library.

**Impact:** You won't see the pretty "Performance, Cost & Energy Breakdown" table in Studio.

**Workaround:** Studio has its own visualization - this is expected behavior. For CLI output, use `python main.py`.

---

## Troubleshooting

### "Graph not found" Error

**Symptom:** Studio says "No graphs available" or "decomposition not found"

**Fix:**
1. Verify `langgraph.json` exists in project root
2. Check that `graphs` section points to `"./src/graph.py:get_graph"`
3. Restart Agent Server: `Ctrl+C`, then `langgraph dev`
4. Verify function exists: `python -c "from src.graph import get_graph; print(get_graph())"`

### Import Errors

**Symptom:** Server shows `ModuleNotFoundError: No module named 'X'`

**Fix:**
1. Ensure all dependencies installed: `pip install -r requirements.txt`
2. Check `langgraph.json` dependencies list matches `requirements.txt`
3. Activate correct virtual environment

### API Key Errors

**Symptom:** Node fails with "Authentication Error" or "Invalid API key"

**Fix:**
1. Check `.env` file has all required keys:
   - `ANTHROPIC_API_KEY`
   - `OPENAI_API_KEY`
   - `GOOGLE_API_KEY`
2. Verify `.env` is in project root (same directory as `langgraph.json`)
3. Restart Agent Server to reload environment variables

### Execution Hangs at Human Review

**Symptom:** Workflow stops at `human_review` node and never completes

**Fix:**
1. This shouldn't happen - human review auto-approves in Studio
2. Check logs for errors: Look at terminal running `langgraph dev`
3. Verify the try/except block exists in `src/nodes/human_review_node.py`
4. Try restarting the Agent Server

### File Not Found Errors

**Symptom:** Extract node fails with "FileNotFoundError" or similar

**Fix:**
1. Use paths relative to project root: `examples/phase0_simple_spec.txt`
2. Verify file exists: `ls examples/phase0_simple_spec.txt`
3. For absolute paths, ensure Agent Server has access to that location

---

## Best Practices

### Development Workflow

1. **Start simple:** Test with `examples/phase0_simple_spec.txt` first
2. **Check quality gates:** Try different `quality_threshold` values (0.70, 0.80, 0.90)
3. **Test refinement loop:** Use poor-quality specs to trigger validation failures
4. **Inspect states:** Always check state at each node to understand flow
5. **Use time travel:** Rewind to compare states before/after refinement

### Testing Scenarios

**Scenario 1: Happy Path (Quality Pass)**
```json
{
  "spec_document_path": "examples/phase0_simple_spec.txt",
  "target_subsystem": "Navigation",
  "quality_threshold": 0.70
}
```
**Expected:** Extract → Analyze → Decompose → Validate (pass) → Document → END

**Scenario 2: Refinement Loop (Quality Fail)**
```json
{
  "spec_document_path": "examples/phase0_complex_spec.txt",
  "target_subsystem": "Power",
  "quality_threshold": 0.95,
  "max_iterations": 2
}
```
**Expected:** Extract → Analyze → Decompose → Validate (fail) → Decompose (retry) → Validate → ...

**Scenario 3: Pre-Decomposition Review**
```json
{
  "spec_document_path": "examples/phase0_medium_spec.txt",
  "target_subsystem": "Control",
  "review_before_decompose": true
}
```
**Expected:** Extract → Analyze → Human Review (auto-approve) → Decompose → Validate → Document → END

### Performance Tuning

**For faster execution in Studio:**
1. Use smaller test documents
2. Lower `max_iterations` (1-2 instead of 3)
3. Set `quality_threshold` to 0.70 (easier to pass)
4. Disable LangSmith tracing if not needed

**For comprehensive testing:**
1. Use full specification documents
2. Set `max_iterations` to 3
3. Use default `quality_threshold` of 0.80
4. Enable LangSmith tracing for cost analysis

---

## Advanced Features

### Multiple Threads

Create parallel test runs:

1. **Thread 1:** Test with low quality threshold
2. **Thread 2:** Test with high quality threshold
3. **Thread 3:** Test with pre-decomposition review

Compare results side-by-side in Studio.

### Checkpointing & Resume

Studio automatically uses SQLite checkpointing:

1. **Pause execution** at any node
2. **Resume later** from the same state
3. **Inspect checkpoint** in `checkpoints/decomposition_state.db`

### Custom Input Variations

Test edge cases:

**Empty subsystem:**
```json
{
  "spec_document_path": "examples/phase0_simple_spec.txt",
  "target_subsystem": "",
  "quality_threshold": 0.80
}
```

**Very strict quality:**
```json
{
  "spec_document_path": "examples/phase0_simple_spec.txt",
  "target_subsystem": "Navigation",
  "quality_threshold": 0.99,
  "max_iterations": 5
}
```

---

## Comparison: CLI vs. Studio

| Feature | CLI (`main.py`) | LangSmith Studio |
|---------|-----------------|------------------|
| **Use Case** | Production, batch processing | Development, debugging |
| **Visualization** | Rich progress bars, tables | Interactive graph diagram |
| **State Inspection** | Final output only | Every node, time travel |
| **Human Review** | Interactive prompts | Auto-approve |
| **Performance Display** | Custom cost/energy tables | LangSmith traces |
| **Execution Speed** | Fast | Slightly slower (tracing overhead) |
| **Debugging** | Logs only | Visual + logs |
| **Batch Processing** | Yes (scripts) | No (one at a time) |
| **File Output** | Full control | Automatic |
| **Thread Management** | One at a time | Multiple parallel threads |

**Recommendation:** Use Studio for development and testing, CLI for production workflows.

---

## Next Steps

1. **Try the Quick Start** - Run your first decomposition in Studio
2. **Explore Time Travel** - Rewind execution and inspect states
3. **Enable LangSmith Tracing** - See detailed LLM call traces
4. **Test Edge Cases** - Try different quality thresholds and iteration limits
5. **Compare with CLI** - Run same inputs in both modes and compare outputs

---

## Resources

- **LangSmith Studio Docs:** https://docs.langchain.com/langsmith/studio
- **LangGraph CLI Reference:** https://docs.langchain.com/langsmith/langgraph-cli
- **Agent Server API:** https://docs.langchain.com/langsmith/agent-server
- **LangSmith Tracing:** https://docs.langchain.com/langsmith/tracing

---

**Questions or Issues?**
Check the troubleshooting section above or refer to the main README for CLI-based execution.

*Generated for requirements decomposition workflow - Updated: 2025-11-18*
