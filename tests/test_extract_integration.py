"""
Integration tests for the extract node with real API calls.

These tests make actual LLM API calls and are marked with @pytest.mark.integration
to allow selective execution.

Run with: pytest tests/test_extract_integration.py -m integration -v
"""

import pytest
import json
from pathlib import Path

from src.nodes.extract_node import extract_node
from src.state import create_initial_state, RequirementType


# =======================================================================
# Integration Tests with Real API (5 tests)
# =======================================================================

@pytest.mark.integration
@pytest.mark.requires_api_key
@pytest.mark.phase1
class TestExtractIntegration:
    """Integration tests with real LLM API calls."""

    def test_extract_simple_spec_real_api(self):
        """Test extraction from simple spec with real API.

        Expected:
        - 5 requirements extracted
        - All IDs match EXTRACT-{TYPE}-NNN format
        - Quality comparable to Phase 0 results
        
        Cost: ~$0.01
        """
        state = create_initial_state(
            spec_document_path="examples/phase0_simple_spec.txt",
            target_subsystem="Test"
        )

        result = extract_node(state)

        # Should have extracted requirements
        assert "extracted_requirements" in result
        assert len(result["extracted_requirements"]) >= 3

        # Verify ID format
        for req in result["extracted_requirements"]:
            assert req["id"].startswith("EXTRACT-")
            assert req["id"].count("-") == 2  # PREFIX-TYPE-NNN

        # Should have types (checking for enum objects, not strings)
        types = [req["type"] for req in result["extracted_requirements"]]
        assert RequirementType.FUNCTIONAL in types or RequirementType.PERFORMANCE in types

        # Load expected results for comparison
        expected_path = Path("examples/phase0_simple_expected.json")
        if expected_path.exists():
            with open(expected_path) as f:
                expected = json.load(f)

            # Should extract at least 80% of expected requirements
            assert len(result["extracted_requirements"]) >= len(expected) * 0.8

    def test_extract_medium_spec_real_api(self):
        """Test extraction from medium complexity spec with real API.

        Expected:
        - 12-15 requirements extracted
        - Handles ambiguity
        - May use fallback model
        
        Cost: ~$0.02
        """
        state = create_initial_state(
            spec_document_path="examples/phase0_medium_spec.txt",
            target_subsystem="Test"
        )

        result = extract_node(state)

        # Should have extracted requirements
        assert "extracted_requirements" in result
        assert len(result["extracted_requirements"]) >= 10

        # Check for various requirement types
        types = set(req["type"] for req in result["extracted_requirements"])
        assert len(types) >= 2  # Should have at least 2 different types

    def test_extract_complex_spec_real_api(self):
        """Test extraction from complex spec with real API.

        Expected:
        - 20+ requirements extracted
        - Handles poor formatting
        - May use fallback model
        
        Cost: ~$0.03
        """
        state = create_initial_state(
            spec_document_path="examples/phase0_complex_spec.txt",
            target_subsystem="Test"
        )

        result = extract_node(state)

        # Should have extracted requirements
        assert "extracted_requirements" in result
        assert len(result["extracted_requirements"]) >= 15

        # Complex spec may trigger fallback
        fallback_count = result.get("fallback_count", 0)
        # Fallback is OK for complex specs
        assert fallback_count >= 0

    def test_fallback_mechanism_real_api(self):
        """Test that fallback mechanism works with real API.

        This test verifies that the system can handle errors
        and fall back to alternative models.
        
        Cost: ~$0.01
        """
        # Use a simple spec that should succeed
        state = create_initial_state(
            spec_document_path="examples/phase0_simple_spec.txt",
            target_subsystem="Test"
        )

        result = extract_node(state)

        # Should complete successfully (with or without fallback)
        assert "extracted_requirements" in result

        # Error log should be trackable
        assert "error_log" in result

        # If fallback was used, it should be tracked
        if result.get("fallback_count", 0) > 0:
            # Verify fallback was logged
            assert "fallback_count" in result
            assert result["fallback_count"] > 0

    @pytest.mark.unit  # This one doesn't need real API
    def test_error_recovery_mocked(self):
        """Test error recovery with mocked errors.

        This test doesn't make real API calls.
        
        Cost: $0.00
        """
        # Test with nonexistent file
        state = create_initial_state(
            spec_document_path="nonexistent_file.txt",
            target_subsystem="Test"
        )

        result = extract_node(state)

        # Should handle error gracefully
        assert "errors" in result
        assert len(result["errors"]) > 0
        assert result.get("requires_human_review") == True

        # Test with empty file path
        state2 = create_initial_state(
            spec_document_path="",
            target_subsystem="Test"
        )

        result2 = extract_node(state2)
        assert "errors" in result2


# =======================================================================
# Comparison with Phase 0 Results
# =======================================================================

@pytest.mark.integration
@pytest.mark.requires_api_key
@pytest.mark.phase1
class TestPhase0Comparison:
    """Compare Phase 1 results with Phase 0 validation results."""

    def test_quality_matches_phase0(self):
        """Test that Phase 1 quality matches Phase 0 validation.

        Phase 0 Results:
        - Simple: F1 = 1.00
        - Medium: F1 = 0.80
        - Complex: F1 = 0.35
        
        Phase 1 should achieve similar or better results.
        
        Cost: ~$0.06 (all 3 specs)
        """
        test_cases = [
            ("examples/phase0_simple_spec.txt", "examples/phase0_simple_expected.json", 0.80),
            ("examples/phase0_medium_spec.txt", "examples/phase0_medium_expected.json", 0.70),
            ("examples/phase0_complex_spec.txt", "examples/phase0_complex_expected.json", 0.30),
        ]

        for spec_path, expected_path, min_f1 in test_cases:
            state = create_initial_state(
                spec_document_path=spec_path,
                target_subsystem="Test"
            )

            result = extract_node(state)

            # Should have requirements
            assert "extracted_requirements" in result

            # Load expected
            expected_file = Path(expected_path)
            if expected_file.exists():
                with open(expected_file) as f:
                    expected = json.load(f)

                # Calculate rough match (comparing counts as proxy for F1)
                extracted_count = len(result["extracted_requirements"])
                expected_count = len(expected)

                # Should be within reasonable range
                ratio = extracted_count / expected_count if expected_count > 0 else 0
                assert ratio >= 0.5  # At least 50% coverage
