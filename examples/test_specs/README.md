# Synthetic Edge Case Test Specifications

This directory contains synthetic requirements specifications designed to test specific edge cases and quality validation features of the requirements decomposition system.

## Purpose

These test specifications validate:
- Zero requirements allocation handling
- Quality gate failure and refinement loops
- Ambiguous language detection
- Refinement feedback generation
- Iterative quality improvement

---

## Test Specifications

### 1. **edge_case_zero_allocation.txt** - Zero Requirements Allocation

**Test Purpose:** Validate system behavior when no requirements are allocated to target subsystem

**Specification Details:**
- **Source Subsystem:** Power Management
- **Requirements Count:** 10 requirements (all for Power Management)
- **Test Target:** "Navigation" subsystem (or any subsystem except "Power Management")

**Expected Behavior:**
1. Extract node: Successfully extracts all 10 Power Management requirements
2. Analyze node: Generates decomposition strategy
3. Decompose node: Applies allocation rules, determines ZERO requirements for target subsystem
4. Validate node: Quality score = 1.0 (PASSED) for valid empty allocation
5. Document node: Generates allocation report (NO requirements.md)

**Output Expectations:**
- ✅ `allocation_report.md` exists in output directory
- ✅ `allocation_report.md` explains why zero requirements allocated
- ✅ Lists source subsystem (Power Management) vs target subsystem
- ✅ NO `requirements.md` file generated (empty is valid)
- ✅ NO human review triggered (valid outcome)
- ✅ Quality score: 1.0 (perfect for valid empty result)

**Success Criteria:**
- System recognizes zero allocation as valid outcome
- No false quality gate failures
- Professional explanation of allocation result
- Workflow completes normally (not treated as error)

---

### 2. **edge_case_ambiguous_language.txt** - Quality Gate Failure & Refinement

**Test Purpose:** Validate quality validation, failure detection, and iterative refinement

**Specification Details:**
- **Subsystem:** User Interface
- **Requirements Count:** 8 requirements
- **Ambiguous Terms:** 8 specific vague terms (user-friendly, quickly enough, adequate, etc.)

**Ambiguous Language Examples:**
- "user-friendly interface" (vague - what metrics?)
- "quickly enough" (vague - no timing specified)
- "adequate screen space" (vague - no dimensions)
- "sufficiently fast" (vague - no performance target)
- "appropriate visual feedback" (vague - not defined)
- "varying levels" (vague - no scale defined)
- "clear and helpful" (vague - subjective)
- "intuitive manner" (vague - no criteria)

**Expected Behavior - Iteration 1 (FAIL):**
1. Extract node: Extracts all 8 requirements
2. Analyze node: Generates strategy
3. Decompose node: Generates subsystem requirements (with vague language)
4. Validate node: Quality score < 0.80 (FAIL)
   - Clarity score: LOW (due to ambiguous terms)
   - Testability score: LOW (no measurable criteria)
   - Issues flagged: "major" severity for each vague term
5. Routing: Validation fails → Generate refinement feedback → Back to decompose node

**Refinement Feedback Expected:**
- Specific identification of each vague term
- Suggested improvements (e.g., "Replace 'quickly enough' with specific time constraint")
- Clear guidance for improving quality

**Expected Behavior - Iteration 2 (PASS):**
1. Decompose node (retry): Uses refinement feedback to improve requirements
   - Replaces vague terms with specific metrics
   - Adds measurable acceptance criteria
2. Validate node: Quality score ≥ 0.80 (PASS)
   - Clarity score: IMPROVED
   - Testability score: IMPROVED
3. Document node: Generates final output

**Output Expectations:**
- ✅ `requirements.md` with improved, specific requirements
- ✅ `quality_report.md` showing iteration 1 (failed) and iteration 2 (passed)
- ✅ State field `iteration_count` = 2
- ✅ State field `refinement_feedback` populated with specific guidance
- ✅ State field `validation_issues` contains list of detected problems
- ✅ Final quality score ≥ 0.80

**Success Criteria:**
- System detects ambiguous language (quality gate fails)
- Refinement feedback is specific and actionable
- Second iteration shows measurable improvement
- Requirements become testable and unambiguous
- Quality gate passes on second iteration

---

## Expected Test Results

| Test Case | Iteration Count | Final Quality Score | Human Review | Output Files |
|-----------|----------------|---------------------|--------------|--------------|
| Zero Allocation | 1 | 1.0 (PASSED) | No | allocation_report.md |
| Ambiguous Language | 2 | ≥0.80 (PASSED) | No | requirements.md, quality_report.md, traceability.csv |

---

## Integration Test Usage

### Test 4: Zero Allocation Test

```python
def test_edge_case_zero_allocation():
    """Test zero requirements allocation (valid empty result)."""

    initial_state = {
        "spec_document_path": "test_specs/edge_case_zero_allocation.txt",
        "target_subsystem": "Navigation",  # Different from source (Power Management)
        "max_iterations": 3
    }

    final_state = graph.invoke(initial_state)

    # Assertions
    assert final_state["validation_passed"] == True
    assert len(final_state.get("decomposed_requirements", [])) == 0
    assert final_state["quality_metrics"]["overall_score"] == 1.0
    assert not final_state.get("requires_human_review", False)

    # Check output files
    output_dir = get_latest_output_directory()
    assert (output_dir / "allocation_report.md").exists()
    assert not (output_dir / "requirements.md").exists()  # Should NOT exist
```

### Test 5: Ambiguous Language / Refinement Loop Test

```python
def test_edge_case_quality_refinement_loop():
    """Test quality gate failure and refinement loop."""

    initial_state = {
        "spec_document_path": "test_specs/edge_case_ambiguous_language.txt",
        "target_subsystem": "User Interface",
        "max_iterations": 3
    }

    final_state = graph.invoke(initial_state)

    # Assertions
    assert final_state["iteration_count"] == 2  # Should take 2 iterations
    assert final_state["validation_passed"] == True  # Eventually passes
    assert final_state["quality_metrics"]["overall_score"] >= 0.80
    assert final_state.get("refinement_feedback") is not None  # Feedback was generated
    assert len(final_state.get("validation_issues", [])) > 0  # Issues detected

    # Check quality improvement
    # (Note: Would need to track quality across iterations for full validation)
```

---

## Key Testing Insights

### Zero Allocation
- Tests that empty results are handled gracefully
- Validates allocation logic correctness
- Ensures no false failures for valid empty outputs
- Confirms professional reporting of allocation decisions

### Ambiguous Language
- Tests quality validation effectiveness
- Validates refinement feedback generation
- Confirms iterative quality improvement
- Ensures testability and clarity metrics work correctly

---

## Execution Notes

1. **Run independently:** Execute each test case separately to isolate behavior
2. **Monitor iterations:** Track iteration_count to verify refinement loop
3. **Inspect feedback:** Review refinement_feedback for actionable guidance
4. **Compare outputs:** Check quality scores between iterations
5. **Cost tracking:** Monitor LLM costs for multi-iteration workflows

---

## Expected API Costs

- **Zero Allocation Test:** ~$0.05-0.10 (single iteration, minimal processing)
- **Ambiguous Language Test:** ~$0.10-0.20 (two iterations with refinement)

**Total for both edge case tests:** ~$0.15-0.30

---

## Related Documentation

- [Phase 4.1-4.2 Plan](../Phase_4.1_4.2_Plan.md)
- [Integration Test Implementation](../tests/test_e2e_workflow.py)
- [User Guide - Zero Requirements Handling](../docs/user_guide.md#zero-requirements-handling)
- [Quality Validation](../docs/phases/phase3/README.md#quality-validation)

---

## Last Updated

**Date:** November 4, 2025
**Phase:** 4.1 (Integration Testing)
**Status:** Synthetic test specifications created and documented
