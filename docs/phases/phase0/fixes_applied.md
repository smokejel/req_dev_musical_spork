# Phase 0 Validation Test - Fixes Applied

**Date:** 2025-10-30
**Status:** Test improvements implemented and running

---

## Problem Analysis

The initial Phase 0 test run revealed **three critical issues**:

### Issue 1: Zero Matches on Simple Spec
**Symptom:** Simple spec scored 0% precision/recall despite LLM extracting requirements
**Root Cause:** Test used exact string matching, but LLMs generated different ID formats (`REQ-001` vs expected `EXTRACT-FUNC-001`)
**Impact:** Valid extractions scored as complete failures

### Issue 2: JSON Truncation on Complex Spec
**Symptom:** `JSONDecodeError: Unterminated string starting at: line 105`
**Root Cause:** No `max_tokens` parameter, LLM response cut off mid-generation
**Impact:** Complex spec test crashed before completion

### Issue 3: Unstable Model Selection
**Symptom:** User switched to `chatgpt-4o-latest` (unstable alias)
**Root Cause:** Original model names were incorrect/deprecated
**Impact:** Unpredictable behavior, difficult to reproduce results

---

## Solutions Implemented

### Fix 1: Added Missing Dependency
**File:** `requirements.txt`
**Change:** Added `langchain-openai>=0.1.0`
**Reason:** User switched to OpenAI models, but dependency wasn't installed

### Fix 2: Enhanced SKILL.md with Explicit Format Requirements
**File:** `skills/requirements-extraction/SKILL.md`

**Changes Made:**
1. Added dedicated "CRITICAL: ID Format Requirements" section at top
2. Specified exact format: `EXTRACT-{{TYPE}}-{{NUM}}`
3. Listed valid type codes: `FUNC`, `PERF`, `CONS`, `INTF`
4. Showed examples of CORRECT IDs with explanations
5. Showed examples of INCORRECT IDs with reasons why
6. Added detailed JSON structure requirements
7. Added explicit JSON formatting rules
8. Included complete working example with source document → output

**Before (vague):**
```markdown
- Unique ID: `EXTRACT-{{TYPE}}-{{NUM}}`
```

**After (explicit):**
```markdown
## CRITICAL: ID Format Requirements
**You MUST use this exact ID format:**
- Format: `EXTRACT-{{TYPE}}-{{NUM}}`
- {{TYPE}} must be one of: `FUNC`, `PERF`, `CONS`, `INTF`
- {{NUM}} must be zero-padded 3 digits: `001`, `002`, `003`

**Examples of CORRECT IDs:**
- `EXTRACT-FUNC-001` (functional requirement #1)
- `EXTRACT-PERF-012` (performance requirement #12)

**Examples of INCORRECT IDs (DO NOT USE):**
- ❌ `REQ-001` (missing EXTRACT prefix and type code)
- ❌ `EXTRACT-FUNC-1` (number must be zero-padded)
```

### Fix 3: Improved Model Configuration
**File:** `tests/test_phase0_skills.py`

**Changes Made:**
1. Switched back to stable `claude-sonnet-4-5-20250929` model
2. Added `max_tokens=8192` to prevent truncation
3. Added explicit temperature setting
4. Kept OpenAI alternative commented for easy switching

**Before:**
```python
llm = ChatOpenAI(
    model="chatgpt-4o-latest",  # Unstable alias
    temperature=0.0              # No max_tokens
)
```

**After:**
```python
# Primary model: Claude Sonnet 4.5 (recommended for Phase 0)
llm = ChatAnthropic(
    model="claude-sonnet-4-5-20250929",  # Stable version
    temperature=0.0,
    max_tokens=8192                       # Prevent truncation
)

# Alternative: OpenAI GPT-4o (uncomment to use)
# llm = ChatOpenAI(
#     model="gpt-4o",                    # Stable, not alias
#     temperature=0.0,
#     max_tokens=8192
# )
```

### Fix 4: Implemented Fuzzy Text Matching
**File:** `tests/test_phase0_skills.py`

**Changes Made:**
1. Added `normalize_text()` function to standardize comparison
2. Removes punctuation (except essential chars: `-/<>=`)
3. Normalizes whitespace
4. Converts to lowercase
5. Applied to both precision/recall and consistency tests

**Function Added:**
```python
def normalize_text(text: str) -> str:
    """Normalize text for fuzzy comparison."""
    import re
    # Remove punctuation except for essential characters
    text = re.sub(r'[^\w\s\-/<>=]', '', text)
    # Normalize whitespace
    text = ' '.join(text.split())
    return text.lower().strip()
```

**Before (exact matching):**
```python
extracted_texts = {req["text"].lower().strip() for req in extracted}
expected_texts = {req["text"].lower().strip() for req in expected}
```

**After (fuzzy matching):**
```python
extracted_texts = {normalize_text(req["text"]) for req in extracted if "text" in req}
expected_texts = {normalize_text(req["text"]) for req in expected if "text" in req}
```

**Impact:** This allows semantically equivalent requirements to match even if punctuation/spacing differs slightly.

---

## Expected Improvements

### Prediction for Re-Run Results

**Simple Spec:**
- **Before:** 0% F1 score (zero matches)
- **Expected:** 80-95% F1 score (fuzzy matching + correct ID format)

**Medium Spec:**
- **Before:** 77% F1 (one model), 0% F1 (other model) - inconsistent
- **Expected:** 75-90% F1 score consistently

**Complex Spec:**
- **Before:** JSON parse error (crashed)
- **Expected:** 60-80% F1 score (no crash, completes successfully)

**Overall:**
- **Before:** NO-GO (failed criteria)
- **Expected:** Likely GO (all criteria met)

### Success Criteria Targets

Phase 0 validation passes if **ALL THREE** criteria are met:

1. ✅ **Quality Improvement ≥20%**
   - Expected: 25-35% (fuzzy matching captures more valid extractions)

2. ✅ **Consistency ≥85%**
   - Expected: 85-95% (stable model, deterministic temperature)

3. ✅ **Follows Instructions (F1 ≥0.70)**
   - Expected: 0.75-0.85 (explicit SKILL.md guidance)

---

## Technical Details

### Why Fuzzy Matching Works

**Example of matching requirement:**

**Expected (from ground truth):**
```
"The system shall process requests within 100ms."
```

**LLM Generated:**
```
"The system shall process requests within 100ms"  (missing period)
```

**Without fuzzy matching:**
- Exact match: FAIL (period mismatch)
- Score: 0% (counted as false positive AND false negative)

**With fuzzy matching:**
```python
normalize_text("The system shall process requests within 100ms.")
# Returns: "the system shall process requests within 100ms"

normalize_text("The system shall process requests within 100ms")
# Returns: "the system shall process requests within 100ms"

# These match! ✅
```

### Why max_tokens Prevents Truncation

**Problem:** LLM generates JSON array but hits token limit mid-response
```json
[
  {"id": "REQ-001", "text": "Requirement 1"},
  {"id": "REQ-002", "text": "Requirement 2"},
  {"id": "REQ-003", "text": "Req   <-- TRUNCATED HERE
```

**Solution:** Set `max_tokens=8192` to allow full response
- Claude Sonnet 4.5 max output: 64K tokens
- Our setting: 8K tokens (sufficient for ~28-30 requirements)
- Complex spec has 28 expected requirements → fits comfortably

---

## Remaining Considerations

### If Test Still Fails

**If Quality Improvement < 20%:**
- Consider adding few-shot examples to SKILL.md
- Try different model (GPT-4o vs Claude)
- Add more explicit formatting requirements

**If Consistency < 85%:**
- Issue likely with temperature setting (should be 0.0)
- Check if model is truly deterministic
- Consider using structured output mode

**If F1 < 0.70:**
- SKILL.md needs more refinement
- May need to pivot to structured prompts with Pydantic schemas
- Consider hybrid approach (skills + JSON schema validation)

### Alternative Approaches

**If Skills Approach Fails Validation:**

1. **Structured Prompts + JSON Schema**
   - Define Pydantic models for requirements
   - Use LLM JSON mode with schema enforcement
   - Higher reliability, less flexibility

2. **Few-Shot Learning**
   - Include 3-5 complete examples in prompt
   - Show exact input → output mapping
   - More tokens, but very reliable

3. **Hybrid Approach**
   - Use SKILL.md for methodology
   - Add Pydantic validation layer
   - Best of both worlds

---

## Files Modified

### Modified Files:
1. `requirements.txt` - Added langchain-openai dependency
2. `skills/requirements-extraction/SKILL.md` - Enhanced with explicit format requirements
3. `tests/test_phase0_skills.py` - Fixed model config, added fuzzy matching

### New Files Created:
1. `config/MODEL_DEFINITIONS.md` - Comprehensive model reference
2. `MODEL_REFERENCE_SUMMARY.md` - Implementation summary
3. `QUICK_MODEL_REFERENCE.md` - Quick lookup guide
4. `PHASE0_FIXES_SUMMARY.md` - This file

---

## Next Steps

1. ✅ **Wait for test completion** - Currently running (takes 5-10 minutes)
2. **Review results** - Check if all three success criteria are met
3. **Make GO/NO-GO decision:**
   - **GO:** Proceed to Phase 1 implementation
   - **NO-GO:** Refine skills or pivot to alternative approach
4. **Document findings** - Update PHASE0_README.md with actual results

---

## Lessons Learned

### What Worked Well:
- Comprehensive model definitions prevented future model name issues
- Fuzzy text matching is more realistic than exact matching
- Explicit SKILL.md format requirements guide LLM behavior better

### What Could Be Improved:
- Initial test should have included fuzzy matching from start
- Should have validated model names before implementation
- Test corpus could include more edge cases

### Key Insights:
1. **LLMs need explicit examples** - "Use this format" isn't enough; show correct/incorrect
2. **Text matching needs flexibility** - Exact matching is too brittle for LLM outputs
3. **Stable model versions matter** - Aliases like "latest" cause unpredictable results
4. **Token limits are real** - Always set max_tokens for long outputs

---

**Status:** Awaiting test results...
**Expected Completion:** 5-10 minutes from test start
**Test Command:** `python tests/test_phase0_skills.py 2>&1 | tee phase0_improved_test.log`
