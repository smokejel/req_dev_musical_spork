# Gemini CLI Usage Guide

This guide explains how to use the Gemini CLI for large codebase analysis and requirements generation tasks.

## Overview

The Gemini CLI (`gemini`) provides access to Google Gemini's large context window (1M+ tokens) for analyzing large codebases, processing multiple files, and generating synthetic test data.

## Why Use Gemini CLI?

**Benefits:**
- **Massive context window:** 1M+ tokens (vs. typical 32K-200K)
- **File/directory inclusion:** Use `@` syntax to include entire directories
- **Codebase analysis:** Analyze large projects without context limits
- **Synthetic data generation:** Generate test requirements and specifications

**When to Use:**
- Analyzing large codebases (multiple files/directories)
- Processing files that might exceed standard context limits
- Generating synthetic test requirements
- Cross-file analysis and understanding

## Installation

```bash
# Install Gemini CLI (if not already installed)
npm install -g @google/generative-ai-cli

# Or using pip
pip install google-generativeai-cli

# Configure API key
gemini configure
```

## Basic Usage

### Command Structure

```bash
gemini -p "your prompt here"
```

### Common Options

```bash
gemini -p "prompt"           # Execute prompt
gemini -p "prompt" -v        # Verbose output
gemini -p "prompt" --model   # Specify model (default: gemini-pro)
```

## File and Directory Inclusion

### The `@` Syntax

Use `@` followed by a file or directory path to include content in your prompt. Paths are relative to WHERE you run the command.

### Single File Analysis

```bash
# Analyze a single Python file
gemini -p "@src/main.py Explain this file's purpose and structure"

# Analyze configuration file
gemini -p "@config/llm_config.py List all LLM models and their configurations"
```

### Multiple Files

```bash
# Analyze multiple specific files
gemini -p "@package.json @src/index.js Analyze the dependencies used in the code"

# Compare two files
gemini -p "@src/state.py @tests/test_state.py Verify test coverage for state.py"
```

### Entire Directory

```bash
# Analyze entire src directory
gemini -p "@src/ Summarize the architecture of this codebase"

# Analyze docs directory
gemini -p "@docs/ Summarize all documentation and identify gaps"
```

### Multiple Directories

```bash
# Analyze source and tests together
gemini -p "@src/ @tests/ Analyze test coverage for the source code"

# Compare implementation vs documentation
gemini -p "@src/ @docs/ Verify documentation matches implementation"
```

### Current Directory

```bash
# Analyze entire project
gemini -p "@./ Give me an overview of this entire project"

# Project structure analysis
gemini -p "@./ Describe the project structure and key components"
```

## Use Cases for This Project

### 1. Generating Synthetic Requirements

**Purpose:** Create test data for requirements decomposition

```bash
# Generate simple navigation requirements
gemini -p "Generate 10 simple navigation system requirements in the format:
REQ-001: Description
Include requirements for GPS, waypoints, and route planning."

# Generate complex requirements
gemini -p "Generate 30 complex avionics system requirements with:
- Functional requirements
- Performance constraints
- Safety requirements
- Integration requirements
Format as a system specification document."
```

**Note:** Gemini CLI cannot directly create files. Copy the output and save manually to `examples/` directory.

### 2. Codebase Analysis

```bash
# Analyze entire workflow
gemini -p "@src/ Explain the LangGraph workflow and how nodes interact"

# Find specific patterns
gemini -p "@src/ Find all places where quality metrics are calculated and explain the logic"

# Understand state management
gemini -p "@src/state.py @src/graph.py Explain how state flows through the workflow"
```

### 3. Documentation Review

```bash
# Check documentation completeness
gemini -p "@docs/ @src/ Identify undocumented functions and classes in src/"

# Verify examples match code
gemini -p "@docs/user_guide.md @main.py Verify CLI examples in user guide match actual implementation"
```

### 4. Test Coverage Analysis

```bash
# Analyze test coverage
gemini -p "@src/nodes/ @tests/ For each node in src/nodes/, list which tests cover it"

# Find untested code paths
gemini -p "@src/ @tests/ Identify functions in src/ with no corresponding tests"
```

### 5. Multi-File Refactoring Analysis

```bash
# Impact analysis
gemini -p "@src/ If we change the state schema in src/state.py, which files need updates?"

# Dependency mapping
gemini -p "@src/ @config/ Map dependencies between source files and configurations"
```

## Advanced Usage

### Analyzing Specific Patterns

```bash
# Find error handling patterns
gemini -p "@src/ List all error handling approaches used across the codebase"

# Track LLM model usage
gemini -p "@src/ @config/ Where is each LLM model used and why?"
```

### Cross-Reference Checking

```bash
# Verify CLAUDE.md accuracy
gemini -p "@CLAUDE.md @src/ Verify claims in CLAUDE.md match actual implementation"

# Check phase documentation
gemini -p "@docs/phases/ @src/ For each phase, verify documented features are implemented"
```

### Requirements Analysis

```bash
# Analyze test specifications
gemini -p "@examples/ Analyze all test specifications and categorize by complexity"

# Generate missing examples
gemini -p "@examples/ We have simple and complex specs. Generate a medium complexity spec with 15 requirements"
```

## Output Handling

### Saving Output

```bash
# Redirect to file
gemini -p "@src/ Summarize architecture" > architecture_summary.md

# Append to file
gemini -p "@tests/ List all test cases" >> test_inventory.txt
```

### JSON Output (if supported)

```bash
# Request JSON format
gemini -p "@src/state.py Extract state schema as JSON schema"
```

## Limitations & Workarounds

### File Creation Limitation

**Issue:** Gemini CLI cannot directly write files
**Workaround:** Copy output manually or redirect to files using `>`

```bash
# Generate content
gemini -p "Generate requirements" > temp_requirements.txt

# Then manually move to proper location
mv temp_requirements.txt examples/generated_spec.txt
```

### Token Limits

While Gemini has a 1M+ context window, responses are still limited:

**Workaround:** Ask for summaries or chunked responses

```bash
# Instead of: "List every function in src/"
# Use: "Summarize the key functions in src/ grouped by module"
```

### Rate Limits

Free tier has rate limits:

**Workaround:** Add delays between requests or use paid tier

```bash
# Add delay between requests
gemini -p "prompt 1" && sleep 5 && gemini -p "prompt 2"
```

## Best Practices

### 1. Use Relative Paths

```bash
# Good (from project root)
gemini -p "@src/ @tests/ Analyze code"

# Bad (absolute paths may break on different machines)
gemini -p "@/Users/name/project/src/ Analyze code"
```

### 2. Be Specific in Prompts

```bash
# Good (specific request)
gemini -p "@src/nodes/ List each node's purpose, inputs, and outputs"

# Less good (vague)
gemini -p "@src/ Tell me about the nodes"
```

### 3. Request Structured Output

```bash
# Request markdown tables
gemini -p "@config/ Create a markdown table of all LLM models with name, context window, and use case"

# Request numbered lists
gemini -p "@docs/ List all documentation files in priority order for new users"
```

### 4. Combine with Project Context

```bash
# Include CLAUDE.md for context
gemini -p "@CLAUDE.md @src/ Based on the architecture in CLAUDE.md, explain how src/ implements it"
```

## Common Commands for This Project

### Generate Test Data

```bash
# Simple spec (5 requirements)
gemini -p "Generate 5 clear, unambiguous navigation system requirements. Format:
REQ-NAV-001: [Description]
Focus on GPS, waypoint management, and route calculation."

# Medium spec (15 requirements)
gemini -p "Generate 15 navigation system requirements with some ambiguity and complexity. Include functional and performance requirements."

# Complex spec (30+ requirements)
gemini -p "Generate 30+ avionics navigation requirements with poor formatting, nested requirements, and ambiguous language to test extraction robustness."
```

### Analyze Implementation

```bash
# Understand workflow
gemini -p "@src/graph.py @src/nodes/ Explain the complete workflow from document input to final output"

# Validate phase completion
gemini -p "@CLAUDE.md @src/ @tests/ Verify Phase 6 claims in CLAUDE.md match src/ implementation and tests/"
```

### Documentation Tasks

```bash
# Find documentation gaps
gemini -p "@README.md @docs/ @src/ What features in src/ are not documented in README or docs/?"

# Generate documentation outline
gemini -p "@src/utils/ Generate a documentation outline for all utility functions"
```

## Integration with Development Workflow

### Pre-Commit Analysis

```bash
# Before committing large changes
gemini -p "@src/ Identify potential breaking changes in recent modifications"
```

### Code Review

```bash
# Review specific changes
gemini -p "@src/nodes/validate_node.py Suggest improvements and identify potential bugs"
```

### Feature Planning

```bash
# Analyze feasibility
gemini -p "@CLAUDE.md @src/ Is Phase 7 (multi-subsystem support) feasible with current architecture?"
```

## Troubleshooting

### Command Not Found

```bash
# Check installation
which gemini

# Reinstall if needed
npm install -g @google/generative-ai-cli
```

### API Key Issues

```bash
# Reconfigure API key
gemini configure

# Or set environment variable
export GOOGLE_API_KEY=your_key_here
```

### Context Length Errors

If including too many files:

```bash
# Split into smaller chunks
gemini -p "@src/nodes/ Analyze nodes"
gemini -p "@src/agents/ Analyze agents"

# Or request summaries
gemini -p "@src/ Summarize each module in 2-3 sentences"
```

## Resources

### Official Documentation

- **Gemini API Docs:** https://ai.google.dev/docs
- **CLI Reference:** (Check package documentation)

### Project-Specific

- **Test Fixtures:** `examples/` directory for test specifications
- **Architecture:** `CLAUDE.md` for project context
- **User Guide:** `docs/user_guide.md`

## Examples from Project History

### Phase 0 Validation

```bash
# Generate validation test specs
gemini -p "Create 3 test specifications:
1. Simple (5 requirements)
2. Medium (15 requirements with some ambiguity)
3. Complex (30+ requirements with poor formatting)"
```

### Phase 4 Testing

```bash
# Verify large document support
gemini -p "@config/llm_config.py Confirm Gemini 2.5 Flash-Lite can handle 88K+ token inputs"
```

### Phase 6 Validation

```bash
# Check energy tracking implementation
gemini -p "@config/llm_config.py @src/graph.py @tests/test_energy_tracking.py Verify energy tracking is fully implemented"
```

---

**Last Updated:** November 15, 2025
**Gemini Model:** gemini-2.5-flash (or latest)
**Context Window:** 1M+ tokens
**Project Version:** Phase 6 Complete
