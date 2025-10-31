# Model Reference Summary

**Date:** 2025-10-30
**Status:** Model definitions added to project memory

## What Was Created

### 1. Comprehensive Model Definitions Document
**File:** `config/MODEL_DEFINITIONS.md`

A complete reference guide containing:

- **Anthropic Claude Models:**
  - Latest: Claude 4.5 series (Sonnet, Haiku, Opus)
  - Legacy models still available
  - Deprecation timeline and replacement recommendations

- **OpenAI Models:**
  - GPT-5 series (frontier models)
  - GPT-4 series (still active)
  - Reasoning models (o-series)
  - Specialized models (Sora, DALL·E, Whisper, TTS)
  - Audio & Realtime models
  - Embeddings
  - Open-weight models

- **Google Gemini Models:**
  - Gemini 2.5 series (Pro, Flash, Flash-Lite)
  - Gemini 2.0 series (previous generation)
  - Specialized models (Image, Live, TTS)
  - Model version patterns (Stable, Preview, Latest, Experimental)

### 2. Project-Specific Recommendations
The document includes specific model recommendations for this project:

**Phase 0 (Skills Validation):**
- Primary: `claude-sonnet-4-5-20250929`
- Fallback: `gpt-4o`

**Phase 1-4 (MVP Implementation):**
| Node | Primary Model | Fallback | Rationale |
|------|---------------|----------|-----------|
| Extract | `gpt-4o-mini` | `gpt-4o` | Cost optimization |
| Analyze | `claude-sonnet-4-5-20250929` | `gpt-4o` | Architectural reasoning |
| Decompose | `gpt-4o` | `claude-sonnet-4-5-20250929` | Complex reasoning |
| Validate | `claude-sonnet-4-5-20250929` | `gpt-4o` | Quality assessment |

### 3. Error Handling & Fallback Strategy
Complete error taxonomy with handling recommendations:
- **Transient errors:** Retry with exponential backoff
- **Content errors:** Switch to fallback model
- **Fatal errors:** Stop and alert user

### 4. Cost Optimization Guidelines
- Model tier strategies
- Caching recommendations
- Batch operation tips
- Cost monitoring advice

## Bug Fixes Applied

### Issue 1: Template Variable Parsing Error
**Problem:** SKILL.md contained `{TYPE}` and `{NUM}` which LangChain interpreted as template variables.

**Fix:** Escaped all curly braces in SKILL.md by doubling them (`{{TYPE}}`, `{{NUM}}`).

**Files Modified:**
- `skills/requirements-extraction/SKILL.md`

### Issue 2: Missing Environment Variable Loading
**Problem:** Test script didn't load `.env` file, causing API authentication failure.

**Fix:** Added `python-dotenv` import and `load_dotenv()` call.

**Files Modified:**
- `tests/test_phase0_skills.py` (lines 10, 15)

### Issue 3: Invalid Model Name
**Problem:** Used non-existent model names (`claude-3-5-sonnet-20241022`, `claude-3-5-sonnet-20240620`).

**Fix:** Updated to correct Claude Sonnet 4.5 model name: `claude-sonnet-4-5-20250929`

**Files Modified:**
- `tests/test_phase0_skills.py` (lines 38, 63)

## Current Status

✅ **Model definitions document created** at `config/MODEL_DEFINITIONS.md`
✅ **All bugs fixed** in test script
✅ **Correct model names applied** based on official documentation
🔄 **Phase 0 validation test running** in background

## Next Steps

1. **Wait for test results** - The Phase 0 validation is currently running
2. **Review validation output** - Check if skills approach meets success criteria:
   - Quality improvement ≥20%
   - Consistency ≥85%
   - F1 score ≥0.70
3. **Make Go/No-Go decision** based on results
4. **Proceed to Phase 1** if validation passes

## How to Use Model Definitions

### In Code
```python
# Import model definitions
from config.llm_config import get_model_for_node

# Use recommended model for specific node
llm = get_model_for_node("extract")
```

### For Manual Reference
- Open `config/MODEL_DEFINITIONS.md`
- Search for specific model by name or provider
- Check deprecation timeline before using legacy models
- Review pricing to optimize costs

### For Testing
```python
# Always use specific version for reproducible tests
llm = ChatAnthropic(
    model="claude-sonnet-4-5-20250929",
    temperature=0.0
)
```

## Resources

All official documentation links included in `config/MODEL_DEFINITIONS.md`:
- Claude models: https://docs.anthropic.com/en/docs/about-claude/models
- OpenAI models: https://platform.openai.com/docs/models
- Gemini models: https://ai.google.dev/gemini-api/docs/models
- Deprecation notices for all providers

## Maintenance

**Recommended Update Schedule:**
- Check for new models: Quarterly
- Review deprecation notices: Monthly
- Update document: As new models are released

**How to Update:**
1. Visit official documentation links
2. Check for new models or deprecations
3. Update `config/MODEL_DEFINITIONS.md`
4. Test new models in development environment
5. Update project code if needed
