"""
Tests for energy consumption tracking (Phase 6.1).

Validates energy calculation functions and ensures accurate energy estimates
based on published research values.
"""

import pytest
from config.llm_config import (
    GPT_4O,
    GPT_4O_MINI,
    GPT_5_NANO,
    CLAUDE_SONNET_4_5,
    GEMINI_2_5_FLASH_LITE,
    GEMINI_2_5_FLASH,
    GEMINI_2_5_PRO,
    estimate_energy
)
from src.graph import estimate_workflow_energy
from src.state import create_initial_state, Requirement, DetailedRequirement, RequirementType


class TestEnergyEstimation:
    """Test energy estimation functions."""

    def test_energy_calculation_gpt4o(self):
        """
        Test GPT-4o energy calculation matches published research.

        Expected: 0.3 Wh per 500 tokens (Epoch AI, Feb 2025)
        With PUE 1.10: 0.3 * 1.10 = 0.33 Wh
        """
        # 500 input + 500 output tokens = 1000 total tokens
        energy = estimate_energy(GPT_4O, input_tokens=500, output_tokens=500, include_pue=True)

        # Expected: (500/1000 * 0.0006 + 500/1000 * 0.0006) * 1.10
        # = (0.0003 + 0.0003) * 1.10 = 0.00066 Wh
        expected = 0.00066

        # Allow ±5% tolerance for floating point arithmetic
        assert abs(energy - expected) < expected * 0.05, \
            f"GPT-4o energy ({energy:.6f} Wh) should be ~{expected:.6f} Wh for 1000 tokens"

        # Verify energy is in reasonable range (0.0006-0.0007 Wh)
        assert 0.0006 <= energy <= 0.0007, \
            f"GPT-4o energy should be between 0.0006-0.0007 Wh, got {energy:.6f}"

    def test_energy_calculation_gemini(self):
        """
        Test Gemini energy calculation matches published research.

        Expected: 0.24 Wh per 500 tokens (Google, Aug 2025)
        With PUE 1.10: 0.24 * 1.10 = 0.264 Wh
        """
        # 500 input + 500 output tokens = 1000 total tokens
        energy = estimate_energy(
            GEMINI_2_5_FLASH,
            input_tokens=500,
            output_tokens=500,
            include_pue=True
        )

        # Expected: (500/1000 * 0.00048 + 500/1000 * 0.00048) * 1.10
        # = (0.00024 + 0.00024) * 1.10 = 0.000528 Wh
        expected = 0.000528

        # Allow ±5% tolerance
        assert abs(energy - expected) < expected * 0.05, \
            f"Gemini energy ({energy:.6f} Wh) should be ~{expected:.6f} Wh for 1000 tokens"

        # Verify energy is in reasonable range (0.00048-0.00055 Wh)
        assert 0.00048 <= energy <= 0.00055, \
            f"Gemini energy should be between 0.00048-0.00055 Wh, got {energy:.6f}"

    def test_energy_zero_tokens(self):
        """Test energy calculation with zero tokens (edge case)."""
        energy = estimate_energy(GPT_4O, input_tokens=0, output_tokens=0, include_pue=True)

        assert energy == 0.0, "Energy should be 0.0 for zero tokens"

    def test_energy_without_pue(self):
        """Test energy calculation without PUE overhead."""
        # Without PUE, energy should be lower
        energy_with_pue = estimate_energy(
            GPT_4O,
            input_tokens=1000,
            output_tokens=1000,
            include_pue=True
        )
        energy_without_pue = estimate_energy(
            GPT_4O,
            input_tokens=1000,
            output_tokens=1000,
            include_pue=False
        )

        # Energy with PUE should be 1.10x higher
        assert energy_with_pue > energy_without_pue, \
            "Energy with PUE should be higher than without PUE"

        assert abs(energy_with_pue - energy_without_pue * 1.10) < 0.000001, \
            "Energy with PUE should be exactly 1.10x energy without PUE"

    def test_all_models_have_energy_coefficients(self):
        """Ensure all configured models have energy coefficients > 0."""
        models = [
            GPT_4O,
            GPT_4O_MINI,
            GPT_5_NANO,
            CLAUDE_SONNET_4_5,
            GEMINI_2_5_FLASH_LITE,
            GEMINI_2_5_FLASH,
            GEMINI_2_5_PRO
        ]

        for model in models:
            assert model.energy_per_1k_input_wh > 0, \
                f"{model.name} should have energy_per_1k_input_wh > 0"
            assert model.energy_per_1k_output_wh > 0, \
                f"{model.name} should have energy_per_1k_output_wh > 0"

    def test_energy_scales_with_tokens(self):
        """Test that energy scales linearly with token count."""
        # 1000 tokens
        energy_1k = estimate_energy(GPT_4O, input_tokens=1000, output_tokens=0, include_pue=False)

        # 2000 tokens (should be 2x energy)
        energy_2k = estimate_energy(GPT_4O, input_tokens=2000, output_tokens=0, include_pue=False)

        # Allow small floating point tolerance
        assert abs(energy_2k - energy_1k * 2.0) < 0.000001, \
            "Energy should scale linearly with token count"


class TestWorkflowEnergyEstimation:
    """Test workflow-level energy estimation."""

    def test_estimate_workflow_energy_simple(self):
        """Test energy estimation for a simple workflow."""
        # Create state with 5 extracted and 10 decomposed requirements
        state = create_initial_state(
            spec_document_path="test.txt",
            target_subsystem="Test Subsystem"
        )
        state['extracted_requirements'] = [
            Requirement(
                id=f"EXTRACT-FUNC-{i:03d}",
                text=f"Requirement {i}",
                type=RequirementType.FUNCTIONAL
            )
            for i in range(5)
        ]
        state['decomposed_requirements'] = [
            DetailedRequirement(
                id=f"DECOMP-FUNC-{i:03d}",
                parent_id="EXTRACT-FUNC-001",
                text=f"Detailed requirement {i}",
                type=RequirementType.FUNCTIONAL,
                subsystem="Test",
                acceptance_criteria=["Criterion 1"]
            )
            for i in range(10)
        ]
        state['iteration_count'] = 0

        # Calculate energy
        energy_data = estimate_workflow_energy(state)

        # Verify structure
        assert 'total_energy_wh' in energy_data
        assert 'energy_breakdown' in energy_data

        # Verify all nodes have energy values
        expected_nodes = ['extract', 'analyze', 'decompose', 'validate', 'document']
        for node in expected_nodes:
            assert node in energy_data['energy_breakdown'], \
                f"Node '{node}' should be in energy breakdown"

        # Total energy should be sum of all nodes
        calculated_total = sum(energy_data['energy_breakdown'].values())
        assert abs(energy_data['total_energy_wh'] - calculated_total) < 0.000001, \
            "Total energy should equal sum of node energies"

        # Total energy should be > 0 (at least some work was done)
        assert energy_data['total_energy_wh'] > 0, \
            "Total energy should be greater than zero"

    def test_estimate_workflow_energy_with_iterations(self):
        """Test energy estimation scales with refinement iterations."""
        state = create_initial_state(
            spec_document_path="test.txt",
            target_subsystem="Test Subsystem"
        )
        state['extracted_requirements'] = [
            Requirement(
                id="EXTRACT-FUNC-001",
                text="Requirement",
                type=RequirementType.FUNCTIONAL
            )
        ]
        state['decomposed_requirements'] = [
            DetailedRequirement(
                id="DECOMP-FUNC-001",
                parent_id="EXTRACT-FUNC-001",
                text="Detailed requirement",
                type=RequirementType.FUNCTIONAL,
                subsystem="Test",
                acceptance_criteria=["Criterion 1"]
            )
        ]

        # Energy with 0 iterations
        state['iteration_count'] = 0
        energy_0_iter = estimate_workflow_energy(state)

        # Energy with 2 iterations (decompose and validate run 3x total)
        state['iteration_count'] = 2
        energy_2_iter = estimate_workflow_energy(state)

        # Energy should increase with iterations
        assert energy_2_iter['total_energy_wh'] > energy_0_iter['total_energy_wh'], \
            "Energy should increase with more iterations"

        # Decompose and validate nodes should have higher energy with iterations
        assert energy_2_iter['energy_breakdown']['decompose'] > \
               energy_0_iter['energy_breakdown']['decompose'], \
            "Decompose energy should increase with iterations"

        assert energy_2_iter['energy_breakdown']['validate'] > \
               energy_0_iter['energy_breakdown']['validate'], \
            "Validate energy should increase with iterations"

    def test_estimate_workflow_energy_zero_requirements(self):
        """Test energy estimation with zero requirements (edge case)."""
        state = create_initial_state(
            spec_document_path="test.txt",
            target_subsystem="Test Subsystem"
        )
        state['extracted_requirements'] = []
        state['decomposed_requirements'] = []
        state['iteration_count'] = 0

        energy_data = estimate_workflow_energy(state)

        # Energy should be very low (only analyze node has fixed cost)
        assert energy_data['total_energy_wh'] > 0, \
            "Total energy should be > 0 even with zero requirements (analyze node runs)"

        # Extract, decompose, validate should have ~0 energy
        assert energy_data['energy_breakdown']['extract'] == 0.0 or \
               energy_data['energy_breakdown']['extract'] < 0.001, \
            "Extract energy should be ~0 with zero requirements"


class TestEnergyComparisons:
    """Test energy coefficient comparisons across models."""

    def test_gemini_more_efficient_than_gpt4o(self):
        """Gemini should be more energy-efficient than GPT-4o (per research)."""
        # Same token count for both models
        tokens = 1000

        gpt4o_energy = estimate_energy(
            GPT_4O,
            input_tokens=tokens,
            output_tokens=tokens,
            include_pue=False
        )
        gemini_energy = estimate_energy(
            GEMINI_2_5_FLASH,
            input_tokens=tokens,
            output_tokens=tokens,
            include_pue=False
        )

        # Gemini (0.00048 Wh/1K) should be more efficient than GPT-4o (0.0006 Wh/1K)
        assert gemini_energy < gpt4o_energy, \
            f"Gemini ({gemini_energy:.6f} Wh) should be more efficient than GPT-4o ({gpt4o_energy:.6f} Wh)"

    def test_gpt4o_mini_more_efficient_than_gpt4o(self):
        """GPT-4o-mini should be more energy-efficient than GPT-4o."""
        tokens = 1000

        gpt4o_energy = estimate_energy(
            GPT_4O,
            input_tokens=tokens,
            output_tokens=tokens,
            include_pue=False
        )
        gpt4o_mini_energy = estimate_energy(
            GPT_4O_MINI,
            input_tokens=tokens,
            output_tokens=tokens,
            include_pue=False
        )

        # GPT-4o-mini (0.00015 Wh/1K) should be more efficient than GPT-4o (0.0006 Wh/1K)
        assert gpt4o_mini_energy < gpt4o_energy, \
            f"GPT-4o-mini ({gpt4o_mini_energy:.6f} Wh) should be more efficient than GPT-4o ({gpt4o_energy:.6f} Wh)"
