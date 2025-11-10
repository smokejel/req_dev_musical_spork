# Real-World PDF Test Corpus

This directory contains 5 real-world requirements specification documents for integration testing the requirements decomposition system.

## Purpose

These documents test the system's ability to:
- Parse PDF documents with varying formats (PDF 1.3-1.7)
- Handle real-world complexity and formatting inconsistencies
- Extract meaningful requirements from authentic specifications
- Process documents of varying sizes (small to very large)
- Validate performance and cost metrics with realistic workloads

## Test Corpus Analysis

### 1. **Assignment1SampleSolution.pdf** ⭐ SIMPLE

**Classification:** Simple / Happy Path
**Size:** 191.2 KB (10 pages)
**PDF Version:** 1.3
**Complexity:** Low

**Statistics:**
- Characters: 25,163
- Words: 2,677
- Lines: 369
- Estimated Requirements: ~8

**Test Purpose:**
- Happy path testing with small, well-formatted document
- Quick validation of basic functionality
- Baseline for minimum complexity testing

**Expected Behavior:**
- Fast processing (<30 seconds)
- Clean extraction with minimal parsing issues
- High quality score (≥0.85)

**Recommended Usage:**
- Initial integration testing
- Smoke tests
- Quick validation during development

---

### 2. **dot_61725_DS1.pdf** ⭐⭐ MEDIUM

**Classification:** Medium / Moderate Complexity
**Size:** 1,951.1 KB
**PDF Version:** 1.6 (zip deflate encoded)
**Complexity:** Medium

**Statistics:**
- Characters: 351,699
- Words: 49,678
- Lines: 6,163
- Estimated Requirements: ~844

**Test Purpose:**
- Medium-scale document processing
- Compression handling (zip deflate)
- Realistic requirement volume testing
- Performance benchmarking for typical use case

**Expected Behavior:**
- Processing time: 1-3 minutes
- May trigger refinement loops (1-2 iterations)
- Quality score: 0.80-0.90

**Recommended Usage:**
- Standard integration testing
- Performance profiling
- Cost estimation baseline

---

### 3. **20080017417.pdf** (NASA UAS Document) ⭐⭐ MEDIUM

**Classification:** Medium / Technical Specification
**Size:** 2,223.3 KB
**PDF Version:** 1.6
**Complexity:** Medium

**Statistics:**
- Characters: 120,843
- Words: 16,263
- Lines: 431
- Estimated Requirements: ~169

**Test Purpose:**
- Technical domain testing (aerospace/UAS)
- Multi-page structured document
- Moderate requirement density

**Expected Behavior:**
- Processing time: 1-2 minutes
- Domain-specific terminology handling
- Quality score: 0.80-0.85

**Recommended Usage:**
- Domain-specific testing
- Traceability validation
- Multi-subsystem allocation testing

---

### 4. **Annex-A-Detailed-Software-Requirements-Specification-SRS.pdf** ⭐⭐⭐ COMPLEX

**Classification:** Complex / Large Document
**Size:** 6,436.0 KB
**PDF Version:** 1.7
**Complexity:** High

**Statistics:**
- Characters: 87,725
- Words: 9,779
- Lines: 1,798
- Estimated Requirements: ~368

**Test Purpose:**
- Large document stress testing
- PDF 1.7 format handling
- Complex formatting and structure
- Memory and performance limits

**Expected Behavior:**
- Processing time: 3-5 minutes
- Higher probability of quality gate failures (refinement loops)
- Quality score: 0.75-0.85 (may need human review)

**Recommended Usage:**
- Stress testing
- Performance limit discovery
- Complex document handling validation

---

### 5. **SRS_U.S. GEOLOGICAL SURVEY'S NATIONAL WATER INFORMATION SYSTEM II.pdf** ⭐⭐⭐⭐ VERY COMPLEX

**Classification:** Very Complex / Stress Test
**Size:** 9,897.4 KB (largest)
**PDF Version:** 1.5
**Complexity:** Very High

**Statistics:**
- Characters: 1,347,990
- Words: 202,018
- Lines: 26,861
- Estimated Requirements: ~1,104

**Test Purpose:**
- Maximum scale stress testing
- Performance upper bounds
- Cost analysis at scale
- Memory usage validation

**Expected Behavior:**
- Processing time: 5-10 minutes
- High token usage and cost
- Multiple refinement iterations likely
- Quality score: 0.70-0.85 (human review expected)

**Expected Cost:** ~$1-2 for full decomposition

**Recommended Usage:**
- Final validation before deployment
- Performance benchmarking
- Cost analysis at scale
- Scalability testing

---

## Test Strategy Recommendations

### For Integration Tests (Phase 4.1)

**Test 1: Happy Path - Simple**
- Document: `Assignment1SampleSolution.pdf`
- Target Subsystem: Extract from document or use generic subsystem
- Expected: Full workflow completion without intervention

**Test 2: Happy Path - Medium**
- Document: `dot_61725_DS1.pdf` or `20080017417.pdf`
- Target Subsystem: Relevant subsystem from document
- Expected: 1-2 refinement iterations, successful completion

**Test 3: Performance Test - Complex**
- Document: `SRS_U.S. GEOLOGICAL SURVEY...pdf` (largest)
- Target Subsystem: Water Data Management or similar
- Expected: Completes within 10 minutes, cost <$2

### Parsing Validation

All documents successfully parse with PyPDF2:
- ✅ PDF 1.3: Supported
- ✅ PDF 1.5: Supported
- ✅ PDF 1.6: Supported (including zip deflate)
- ✅ PDF 1.7: Supported

### Expected API Costs

**Per Integration Test Run:**
- Simple document: ~$0.10-0.20
- Medium document: ~$0.30-0.50
- Complex document: ~$1.00-2.00

**Full Test Suite (5 tests):** ~$2-5

---

## Document Categories

| Category | Files | Purpose |
|----------|-------|---------|
| **Simple** | Assignment1SampleSolution.pdf | Happy path, quick validation |
| **Medium** | dot_61725_DS1.pdf, 20080017417.pdf | Realistic workload, performance baseline |
| **Complex** | Annex-A-Detailed-Software-Requirements-Specification-SRS.pdf | Stress testing, edge cases |
| **Very Complex** | SRS_U.S. GEOLOGICAL SURVEY...pdf | Maximum scale, cost analysis |

---

## Parser Compatibility

All documents validated with:
- **Parser:** PyPDF2 ≥3.0.0
- **Python:** 3.11+
- **Encoding:** UTF-8
- **Platform:** macOS (darwin), tested on ARM64

---

## Test Execution Notes

1. **Run tests individually** to avoid token rate limits
2. **Monitor costs** using LangSmith or cost tracking (Phase 4.2)
3. **Save outputs** for manual quality review
4. **Document failures** for analysis and improvement
5. **Use caching** for repeated runs (Phase 4.2 feature)

---

## Last Updated

**Date:** November 4, 2025
**Phase:** 4.1 (Integration Testing)
**Status:** All documents validated and categorized

---

## Related Documentation

- [Phase 4.1-4.2 Plan](../../Phase_4.1_4.2_Plan.md)
- [User Guide](../../docs/user_guide.md)
- [Integration Test Implementation](../../tests/test_e2e_workflow.py)
