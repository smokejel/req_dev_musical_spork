"""
Quality dimension weighting configuration.

This module provides configuration for quality metric dimension weighting,
allowing customization of how each dimension contributes to the overall score.

Phase 7.3: Domain-Aware Requirements Decomposition
"""

import os
from typing import Dict


class QualityConfig:
    """Configuration for quality dimension weighting."""

    # Default weights for 4-dimension (generic) scoring
    DEFAULT_GENERIC_WEIGHTS = {
        'completeness': 0.25,
        'clarity': 0.25,
        'testability': 0.25,
        'traceability': 0.25
    }

    # Default weights for 5-dimension (domain-aware) scoring
    DEFAULT_DOMAIN_WEIGHTS = {
        'completeness': 0.20,
        'clarity': 0.20,
        'testability': 0.20,
        'traceability': 0.20,
        'domain_compliance': 0.20
    }

    @staticmethod
    def get_weights(has_domain_context: bool = False) -> Dict[str, float]:
        """
        Get quality dimension weights from environment or use defaults.

        Args:
            has_domain_context: Whether domain context is present (5 dimensions vs 4)

        Returns:
            Dictionary mapping dimension names to weights (0.0-1.0)

        Raises:
            ValueError: If configured weights don't sum to 1.0 (±0.01 tolerance)
        """
        weights = {}

        # Load from environment variables or use defaults
        weights['completeness'] = float(os.getenv(
            'QUALITY_WEIGHT_COMPLETENESS',
            QualityConfig.DEFAULT_DOMAIN_WEIGHTS['completeness'] if has_domain_context
            else QualityConfig.DEFAULT_GENERIC_WEIGHTS['completeness']
        ))

        weights['clarity'] = float(os.getenv(
            'QUALITY_WEIGHT_CLARITY',
            QualityConfig.DEFAULT_DOMAIN_WEIGHTS['clarity'] if has_domain_context
            else QualityConfig.DEFAULT_GENERIC_WEIGHTS['clarity']
        ))

        weights['testability'] = float(os.getenv(
            'QUALITY_WEIGHT_TESTABILITY',
            QualityConfig.DEFAULT_DOMAIN_WEIGHTS['testability'] if has_domain_context
            else QualityConfig.DEFAULT_GENERIC_WEIGHTS['testability']
        ))

        weights['traceability'] = float(os.getenv(
            'QUALITY_WEIGHT_TRACEABILITY',
            QualityConfig.DEFAULT_DOMAIN_WEIGHTS['traceability'] if has_domain_context
            else QualityConfig.DEFAULT_GENERIC_WEIGHTS['traceability']
        ))

        # Add domain_compliance for domain-aware scoring
        if has_domain_context:
            weights['domain_compliance'] = float(os.getenv(
                'QUALITY_WEIGHT_DOMAIN_COMPLIANCE',
                QualityConfig.DEFAULT_DOMAIN_WEIGHTS['domain_compliance']
            ))

        # Validate weights sum to 1.0 (with small tolerance for floating point)
        total_weight = sum(weights.values())
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(
                f"Quality dimension weights must sum to 1.0, got {total_weight:.3f}. "
                f"Weights: {weights}"
            )

        return weights

    @staticmethod
    def compute_weighted_score(
        completeness: float,
        clarity: float,
        testability: float,
        traceability: float,
        domain_compliance: float = None
    ) -> float:
        """
        Compute weighted overall score from dimension scores.

        Args:
            completeness: Completeness score (0.0-1.0)
            clarity: Clarity score (0.0-1.0)
            testability: Testability score (0.0-1.0)
            traceability: Traceability score (0.0-1.0)
            domain_compliance: Domain compliance score (0.0-1.0, None for generic)

        Returns:
            Weighted overall score (0.0-1.0)
        """
        has_domain = domain_compliance is not None
        weights = QualityConfig.get_weights(has_domain_context=has_domain)

        # Calculate weighted sum
        weighted_sum = (
            completeness * weights['completeness'] +
            clarity * weights['clarity'] +
            testability * weights['testability'] +
            traceability * weights['traceability']
        )

        if has_domain:
            weighted_sum += domain_compliance * weights['domain_compliance']

        return weighted_sum
