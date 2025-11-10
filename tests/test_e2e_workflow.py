"""
End-to-end integration tests for complete requirements decomposition workflow.

These tests validate the entire system using REAL LLM API calls with authentic
PDF documents and synthetic edge case specifications.

**Important:** These tests make actual API calls and incur costs (~$2-5 total).
Only run when API keys are configured and you're ready for integration testing.

Test Strategy:
- Test 1: Simple PDF (happy path, quick validation)
- Test 2: Medium PDF (realistic workload, may have 1-2 refinement iterations)
- Test 3: Large PDF (performance test, stress test)
- Test 4: Zero allocation (edge case - no requirements for target subsystem)
- Test 5: Quality gate failure + refinement (ambiguous language detection)

Expected Total Cost: ~$2-5 for full suite
Expected Total Time: 10-30 minutes (depending on LLM response times)

Run with: pytest tests/test_e2e_workflow.py -v -s
(Use -s to see real-time progress output during long-running tests)
"""

import pytest
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from src.graph import create_decomposition_graph, generate_checkpoint_id
from src.state import DecompositionState

# Mark all tests in this file as integration tests
pytestmark = pytest.mark.integration


class TestE2EWorkflow:
    """
    End-to-end integration tests with real LLM API calls.

    These tests validate the complete workflow from document parsing
    through final output generation using authentic requirements documents.
    """

    @pytest.fixture(scope="class")
    def graph(self):
        """Create decomposition graph for all tests."""
        return create_decomposition_graph()

    @pytest.fixture(scope="class")
    def verify_api_keys(self):
        """Verify required API keys are configured before running tests."""
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        if not anthropic_key and not openai_key:
            pytest.skip(
                "Integration tests require ANTHROPIC_API_KEY or OPENAI_API_KEY. "
                "Set in .env file and re-run."
            )

        # Return True if at least one key is configured
        return True

    def get_latest_output_directory(self) -> Path:
        """Get the most recently created output directory."""
        output_dir = Path("outputs")
        if not output_dir.exists():
            return None

        # Get all run directories
        run_dirs = [d for d in output_dir.iterdir() if d.is_dir() and d.name.startswith("run_")]

        if not run_dirs:
            return None

        # Sort by creation time and return most recent
        latest = max(run_dirs, key=lambda d: d.stat().st_mtime)
        return latest

    def create_checkpoint_config(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Create checkpoint configuration for graph invocation."""
        checkpoint_id = generate_checkpoint_id(state)
        return {"configurable": {"thread_id": checkpoint_id}}

    def test_happy_path_simple_document(self, graph, verify_api_keys):
        """
        Test 1: Happy path with simple, well-formatted document.

        Document: Assignment1SampleSolution.pdf (191 KB, ~8 requirements)
        Expected: Clean extraction, successful decomposition, quality pass
        Expected Cost: ~$0.10-0.20
        Expected Time: 30-60 seconds
        """
        print("\n" + "="*80)
        print("TEST 1: HAPPY PATH - SIMPLE DOCUMENT")
        print("="*80)

        # Setup
        spec_path = "examples/Real_World/Assignment1SampleSolution.pdf"
        assert Path(spec_path).exists(), f"Test document not found: {spec_path}"

        initial_state = {
            "spec_document_path": spec_path,
            "target_subsystem": "System Controller",  # Generic subsystem
            "max_iterations": 3,
            "review_before_decompose": False
        }

        # Execute
        print(f"\n🚀 Starting decomposition for: {spec_path}")
        print(f"📋 Target subsystem: {initial_state['target_subsystem']}")

        # Create checkpoint configuration
        config = self.create_checkpoint_config(initial_state)

        start_time = datetime.now()
        final_state = graph.invoke(initial_state, config=config)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Assert basic workflow completion
        assert final_state is not None, "Graph invocation returned None"
        assert final_state.get("extracted_requirements"), "No requirements extracted"

        # Assert quality metrics
        quality_metrics = final_state.get("quality_metrics", {})
        assert quality_metrics.get("overall_score") is not None, "No quality score generated"

        # For simple document, should pass validation
        # (May be lower if zero allocation, that's OK)
        print(f"\n📊 Quality Score: {quality_metrics.get('overall_score', 0):.2f}")
        print(f"⏱️  Execution Time: {duration:.1f} seconds")

        # Check output directory was created
        output_dir = self.get_latest_output_directory()
        assert output_dir is not None, "No output directory created"
        assert output_dir.exists(), f"Output directory does not exist: {output_dir}"

        # Check for expected output files
        readme_path = output_dir / "README.txt"
        assert readme_path.exists(), "README.txt not created"

        # Either requirements.md OR allocation_report.md should exist
        requirements_path = output_dir / "requirements.md"
        allocation_path = output_dir / "allocation_report.md"
        assert requirements_path.exists() or allocation_path.exists(), \
            "Neither requirements.md nor allocation_report.md created"

        print(f"✅ Test completed successfully")
        print(f"📁 Output directory: {output_dir}")

    def test_happy_path_medium_document(self, graph, verify_api_keys):
        """
        Test 2: Happy path with medium-sized realistic document.

        Document: dot_61725_DS1.pdf (1.9 MB, ~844 requirements)
        Expected: May trigger 1-2 refinement iterations, eventual success
        Expected Cost: ~$0.30-0.50
        Expected Time: 1-3 minutes
        """
        print("\n" + "="*80)
        print("TEST 2: HAPPY PATH - MEDIUM DOCUMENT")
        print("="*80)

        # Setup
        spec_path = "examples/Real_World/dot_61725_DS1.pdf"
        assert Path(spec_path).exists(), f"Test document not found: {spec_path}"

        initial_state = {
            "spec_document_path": spec_path,
            "target_subsystem": "Data Management",  # Generic subsystem for this document
            "max_iterations": 3,
            "review_before_decompose": False
        }

        # Execute
        print(f"\n🚀 Starting decomposition for: {spec_path}")
        print(f"📋 Target subsystem: {initial_state['target_subsystem']}")

        # Create checkpoint configuration
        config = self.create_checkpoint_config(initial_state)

        start_time = datetime.now()
        final_state = graph.invoke(initial_state, config=config)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Assert workflow completion
        assert final_state is not None
        assert final_state.get("extracted_requirements")

        # May have multiple iterations
        iteration_count = final_state.get("iteration_count", 0)
        print(f"\n🔄 Iterations: {iteration_count}")

        # Should eventually pass or require human review
        validation_passed = final_state.get("validation_passed", False)
        requires_review = final_state.get("requires_human_review", False)
        assert validation_passed or requires_review, \
            "Workflow did not pass validation or request human review"

        # Performance check: should complete within reasonable time
        # Increased from 300s to 350s to account for LLM API variance
        assert duration < 350, f"Test took too long: {duration:.1f} seconds (max 350s / 5.8 min)"

        # Quality metrics
        quality_metrics = final_state.get("quality_metrics", {})
        print(f"📊 Quality Score: {quality_metrics.get('overall_score', 0):.2f}")
        print(f"⏱️  Execution Time: {duration:.1f} seconds")

        # Check outputs
        output_dir = self.get_latest_output_directory()
        assert output_dir is not None
        assert (output_dir / "README.txt").exists()

        print(f"✅ Test completed successfully")
        print(f"📁 Output directory: {output_dir}")

    @pytest.mark.slow
    @pytest.mark.skip(reason="Requires Gemini paid tier or >1hr wait between test runs due to 250K token/min free tier quota. Re-enable for paid tier.")
    def test_performance_large_document(self, graph, verify_api_keys):
        """
        Test 3: Performance test with large, complex document.

        Document: SRS_U.S. GEOLOGICAL SURVEY...pdf (9.9 MB, ~1,104 requirements)
        Expected: Long processing time, high token usage, may need human review
        Expected Cost: ~$1-2
        Expected Time: 5-10 minutes

        Note: Marked as @pytest.mark.slow - only run when explicitly requested
        Note: SKIPPED by default - Gemini free tier quota (250K tokens/min) insufficient
        """
        print("\n" + "="*80)
        print("TEST 3: PERFORMANCE TEST - LARGE DOCUMENT")
        print("="*80)
        print("⚠️  This test processes a very large document and may take 5-10 minutes")

        # Setup
        spec_path = "examples/Real_World/SRS_U.S. GEOLOGICAL SURVEY'S NATIONAL WATER INFORMATION SYSTEM II.pdf"
        assert Path(spec_path).exists(), f"Test document not found: {spec_path}"

        initial_state = {
            "spec_document_path": spec_path,
            "target_subsystem": "Water Data Management",
            "max_iterations": 3,
            "review_before_decompose": False
        }

        # Execute
        print(f"\n🚀 Starting decomposition for: {spec_path}")
        print(f"📋 Target subsystem: {initial_state['target_subsystem']}")

        # Create checkpoint configuration
        config = self.create_checkpoint_config(initial_state)

        start_time = datetime.now()
        final_state = graph.invoke(initial_state, config=config)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Assert workflow completion
        assert final_state is not None
        assert final_state.get("extracted_requirements")

        # Performance metrics
        print(f"\n⏱️  Execution Time: {duration:.1f} seconds ({duration/60:.1f} minutes)")

        # Should complete within 10 minutes
        assert duration < 600, f"Test exceeded 10 minute limit: {duration:.1f} seconds"

        # Check memory usage didn't cause issues
        extracted_count = len(final_state.get("extracted_requirements", []))
        print(f"📄 Requirements Extracted: {extracted_count}")

        # Quality metrics
        quality_metrics = final_state.get("quality_metrics", {})
        print(f"📊 Quality Score: {quality_metrics.get('overall_score', 0):.2f}")

        # Check outputs
        output_dir = self.get_latest_output_directory()
        assert output_dir is not None
        assert (output_dir / "README.txt").exists()

        print(f"✅ Performance test completed successfully")
        print(f"📁 Output directory: {output_dir}")

    def test_edge_case_zero_allocation(self, graph, verify_api_keys):
        """
        Test 4: Edge case - Zero requirements allocated to target subsystem.

        Specification: edge_case_zero_allocation.txt (Power Management requirements)
        Target: Navigation subsystem (different from source)
        Expected: Zero allocation is VALID, quality score 1.0, allocation report generated
        Expected Cost: ~$0.05-0.10
        Expected Time: 30-45 seconds
        """
        print("\n" + "="*80)
        print("TEST 4: EDGE CASE - ZERO REQUIREMENTS ALLOCATION")
        print("="*80)

        # Setup
        spec_path = "examples/test_specs/edge_case_zero_allocation.txt"
        assert Path(spec_path).exists(), f"Test specification not found: {spec_path}"

        initial_state = {
            "spec_document_path": spec_path,
            "target_subsystem": "Navigation",  # Different from source (Power Management)
            "max_iterations": 3,
            "review_before_decompose": False
        }

        # Execute
        print(f"\n🚀 Starting decomposition for: {spec_path}")
        print(f"📋 Target subsystem: {initial_state['target_subsystem']} (source: Power Management)")
        print(f"🎯 Expected: Zero allocation (valid outcome)")

        # Create checkpoint configuration
        config = self.create_checkpoint_config(initial_state)

        start_time = datetime.now()
        final_state = graph.invoke(initial_state, config=config)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Assert zero allocation was handled correctly
        decomposed_reqs = final_state.get("decomposed_requirements", [])
        print(f"\n📊 Decomposed Requirements: {len(decomposed_reqs)}")
        assert len(decomposed_reqs) == 0, "Expected zero requirements, but got some"

        # Quality score should be 1.0 for valid empty result
        quality_metrics = final_state.get("quality_metrics", {})
        quality_score = quality_metrics.get("overall_score", 0)
        print(f"📊 Quality Score: {quality_score:.2f}")

        # Validation should PASS (zero is valid)
        validation_passed = final_state.get("validation_passed", False)
        assert validation_passed, "Validation should pass for valid zero allocation"

        # Should NOT require human review
        requires_review = final_state.get("requires_human_review", False)
        assert not requires_review, "Zero allocation should not trigger human review"

        # Check output files
        output_dir = self.get_latest_output_directory()
        assert output_dir is not None

        # Should have allocation report, NOT requirements.md
        allocation_report = output_dir / "allocation_report.md"
        requirements_md = output_dir / "requirements.md"

        assert allocation_report.exists(), "allocation_report.md should exist for zero allocation"
        assert not requirements_md.exists(), "requirements.md should NOT exist for zero allocation"

        print(f"⏱️  Execution Time: {duration:.1f} seconds")
        print(f"✅ Zero allocation handled correctly")
        print(f"📁 Output directory: {output_dir}")

    def test_edge_case_quality_refinement_loop(self, graph, verify_api_keys):
        """
        Test 5: Edge case - Quality gate failure triggers refinement loop.

        Specification: edge_case_ambiguous_language.txt (vague requirements)
        Expected: First validation FAILS, refinement feedback generated, second iteration PASSES
        Expected Cost: ~$0.10-0.20
        Expected Time: 1-2 minutes
        """
        print("\n" + "="*80)
        print("TEST 5: EDGE CASE - QUALITY GATE FAILURE & REFINEMENT")
        print("="*80)

        # Setup
        spec_path = "examples/test_specs/edge_case_ambiguous_language.txt"
        assert Path(spec_path).exists(), f"Test specification not found: {spec_path}"

        initial_state = {
            "spec_document_path": spec_path,
            "target_subsystem": "User Interface",
            "max_iterations": 3,
            "review_before_decompose": False,
            "quality_threshold": 0.95  # Higher threshold to reliably trigger refinement
        }

        # Execute
        print(f"\n🚀 Starting decomposition for: {spec_path}")
        print(f"📋 Target subsystem: {initial_state['target_subsystem']}")
        print(f"🎯 Expected: Quality failure → Refinement → Success")

        # Create checkpoint configuration with interrupt before human review
        checkpoint_id = generate_checkpoint_id(initial_state)
        config = {
            "configurable": {
                "thread_id": checkpoint_id
            },
            "interrupt_before": ["human_review"]  # Stop before human review to avoid EOF error
        }

        start_time = datetime.now()
        final_state = graph.invoke(initial_state, config=config)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Should have at least 1 iteration (refinement triggered)
        iteration_count = final_state.get("iteration_count", 0)
        print(f"\n🔄 Iterations: {iteration_count}")
        assert iteration_count >= 1, \
            f"Expected at least 1 iteration (for refinement), got {iteration_count}"

        # Refinement feedback should have been generated
        refinement_feedback = final_state.get("refinement_feedback")
        assert refinement_feedback is not None, "Refinement feedback should be generated"
        print(f"💬 Refinement Feedback Generated: {len(refinement_feedback)} characters")

        # Validation issues should have been detected
        validation_issues = final_state.get("validation_issues", [])
        print(f"⚠️  Validation Issues Detected: {len(validation_issues)}")
        assert len(validation_issues) > 0, "Should have detected quality issues"

        # Eventually should pass (or require human review if still problematic)
        validation_passed = final_state.get("validation_passed", False)
        requires_review = final_state.get("requires_human_review", False)

        if validation_passed:
            print(f"✅ Validation PASSED after refinement")
            quality_metrics = final_state.get("quality_metrics", {})
            quality_score = quality_metrics.get("overall_score", 0)
            print(f"📊 Final Quality Score: {quality_score:.2f}")
            assert quality_score >= 0.90, f"Expected quality ≥0.90, got {quality_score:.2f}"
        else:
            print(f"⚠️  Validation did not pass, requires human review: {requires_review}")
            assert requires_review, "If validation didn't pass, should require human review"

        print(f"⏱️  Execution Time: {duration:.1f} seconds")
        print(f"✅ Refinement loop test completed successfully")

        # Check outputs
        output_dir = self.get_latest_output_directory()
        assert output_dir is not None
        assert (output_dir / "README.txt").exists()

        print(f"📁 Output directory: {output_dir}")


# Additional test class for helpers and utilities
class TestE2EHelpers:
    """Tests for E2E test helper functions and utilities."""

    def test_output_directory_detection(self):
        """Test that we can detect output directories correctly."""
        output_dir = Path("outputs")

        if output_dir.exists():
            run_dirs = [d for d in output_dir.iterdir() if d.is_dir() and d.name.startswith("run_")]

            if run_dirs:
                # Should be able to find latest
                latest = max(run_dirs, key=lambda d: d.stat().st_mtime)
                assert latest is not None
                assert latest.exists()
                assert latest.name.startswith("run_")

    def test_checkpoint_id_generation(self):
        """Test checkpoint ID generation for E2E tests."""
        test_state = {
            "target_subsystem": "Test Subsystem",
            "spec_document_path": "test.txt"
        }

        checkpoint_id = generate_checkpoint_id(test_state)

        # Should match format: YYYYMMDD_HHMMSS_subsystem_slug
        assert checkpoint_id is not None
        assert len(checkpoint_id) > 0
        assert "_" in checkpoint_id
        assert "test_subsystem" in checkpoint_id.lower()


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v", "-s"])
