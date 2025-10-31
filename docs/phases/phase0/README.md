# Phase 0: Skills Architecture Validation

## Purpose
Validate that Claude Skills can reliably guide LLM behavior before committing to the full 4-week MVP implementation. This 2-3 day validation de-risks the entire project.

## What Was Created

### 1. Skills
- `skills/requirements-extraction/SKILL.md` - Minimal extraction methodology (~700 tokens)

### 2. Test Corpus
- `examples/phase0_simple_spec.txt` - 5 clear requirements (happy path)
- `examples/phase0_simple_expected.json` - Ground truth for simple spec
- `examples/phase0_medium_spec.txt` - 15 requirements with ambiguity and edge cases
- `examples/phase0_medium_expected.json` - Ground truth for medium spec
- `examples/phase0_complex_spec.txt` - 30+ requirements with poor formatting
- `examples/phase0_complex_expected.json` - Ground truth for complex spec

### 3. Test Harness
- `tests/test_phase0_skills.py` - Automated validation script

### 4. Environment
- `requirements.txt` - Minimal dependencies (langchain, langchain-anthropic, python-dotenv)
- `.env.example` - Template for API keys

## How to Run Phase 0 Validation

### Step 1: Setup Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure API Key

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your Anthropic API key
# Get key from: https://console.anthropic.com/
nano .env  # or use your preferred editor
```

Your `.env` should look like:
```
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

### Step 3: Run Validation

```bash
# Run the validation test
python tests/test_phase0_skills.py
```

### Step 4: Review Results

The test will output:
- Precision, Recall, F1 scores for each test spec (simple, medium, complex)
- Comparison: WITH skill vs. WITHOUT skill
- Improvement percentage
- Consistency across 3 runs
- **Overall GO/NO-GO decision**

## Success Criteria

Phase 0 PASSES if ALL three criteria are met:

1. ✅ **Quality Improvement ≥20%** - F1 score with skill vs. without skill
2. ✅ **Consistency ≥85%** - Agreement across 3 runs on same input
3. ✅ **Follows Instructions** - F1 score ≥0.70 with skill

## Expected Output

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

## Decision Matrix

| Scenario | Avg Improvement | Consistency | Action |
|----------|----------------|-------------|--------|
| **Best Case** | ≥30% | ≥90% | ✅ GO - Skills work great, proceed confidently |
| **Good Case** | ≥20% | ≥85% | ✅ GO - Skills work well, proceed as planned |
| **Marginal** | 10-20% | 75-85% | ⚠️ REFINE - Improve skill, re-test |
| **Failure** | <10% | <75% | ❌ PIVOT - Use structured prompts instead |

## If Phase 0 Fails

### Option A: Refine Skill (1 day)
- Add more examples to SKILL.md
- Clarify methodology steps
- Simplify instructions
- Re-run validation

### Option B: Hybrid Approach
- Use skills + few-shot examples in prompts
- Combine structured guidance with examples

### Option C: Pivot to Structured Prompts
- Define Pydantic schemas for outputs
- Use LLM JSON mode
- Hardcode methodology in system prompts
- Timeline impact: +1 week

## What Happens Next

### If GO (Expected):
1. ✅ Skills approach validated
2. Proceed to Phase 1: Foundation (Week 1)
3. 4-week MVP timeline remains on track
4. Build with confidence

### If NO-GO:
1. Execute pivot strategy (Options A, B, or C above)
2. Adjust timeline accordingly
3. Update architecture documentation
4. Re-run validation after changes

## Troubleshooting

### Issue: ModuleNotFoundError
**Solution:** Make sure you've activated the virtual environment and installed dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: API Key Error
**Solution:** Ensure your `.env` file contains a valid ANTHROPIC_API_KEY:
```bash
# Check if .env exists
cat .env
# Should show: ANTHROPIC_API_KEY=sk-ant-...
```

### Issue: JSON Parsing Error
**Solution:** The LLM occasionally returns malformed JSON. The test harness handles this, but if it persists:
- Check your API key is valid
- Ensure you have sufficient API credits
- Try running again (LLM outputs can vary)

### Issue: Low Scores
**Solution:** This is what Phase 0 is designed to catch! If scores are low:
1. Review the extracted requirements vs. expected
2. Check if the skill instructions are clear
3. Consider refining the skill or pivoting to structured prompts

## Cost Estimate

- Simple spec: ~3 LLM calls × 2 methods (with/without skill) = 6 calls
- Medium spec: ~3 LLM calls × 2 methods + 3 consistency runs = 9 calls
- Complex spec: ~3 LLM calls × 2 methods + 3 consistency runs = 9 calls
- **Total: ~24 LLM calls using Claude 3.5 Sonnet**
- **Estimated cost: $2-5** (depending on input/output tokens)

## Timeline

- Environment setup: 10-15 minutes
- Running validation: 5-10 minutes (depends on API speed)
- Analyzing results: 5-10 minutes
- **Total: 20-35 minutes**

## Next Steps After Validation

### If GO Decision:
1. Review `langgraph_requirements_mvp_plan.md` Phase 1
2. Begin Phase 1.1: Project Setup (Days 1-2)
3. Implement remaining skills based on validated approach
4. Build out the 4-node LangGraph workflow

### If NO-GO Decision:
1. Review validation output to understand failure modes
2. Choose pivot strategy (A, B, or C)
3. Update planning documents
4. Re-run validation with revised approach

## Questions?

See `CLAUDE.md` and `langgraph_requirements_mvp_plan.md` for:
- Full architecture details
- Implementation guidance
- Success metrics
- Resource references

---

**Status:** Phase 0 files created and ready for validation
**Last Updated:** 2025-10-30
**Next Action:** Run `python tests/test_phase0_skills.py`
