"""
Integration tests for domain context workflow integration (Phase 7.2).

Tests that domain context is properly loaded in extract_node and passed
through state to decompose_node and validate_node.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from src.nodes.extract_node import extract_node
from src.nodes.decompose_node import decompose_node
from src.nodes.validate_node import validate_node
from src.state import create_initial_state


class TestExtractNodeDomainLoading:
    """Test domain context loading in extract_node."""

    @pytest.fixture
    def base_state(self):
        """Create base state for extract node testing."""
        return create_initial_state(
            spec_document_path="test_data/phase0/autonomous_train_spec.txt",
            target_subsystem="Train Management",
            domain_name="generic",
            subsystem_id=None
        )

    def test_extract_node_loads_generic_domain_by_default(self, base_state):
        """Test extract_node handles generic domain (no context loading)."""
        with patch('src.nodes.extract_node.parse_document') as mock_parse:
            mock_parse.return_value = ("Sample spec text", ".txt")

            with patch('src.agents.requirements_analyst.RequirementsAnalystAgent.extract_requirements') as mock_extract:
                from src.state import Requirement, RequirementType
                mock_extract.return_value = [
                    Requirement(
                        id="SYS-FUNC-001",
                        text="Sample requirement",
                        type=RequirementType.FUNCTIONAL,
                        source_section="1.0"
                    )
                ]

                result = extract_node(base_state)

                # Generic domain should not load domain_context
                assert result.get('domain_context') is None

    def test_extract_node_loads_csx_dispatch_domain_context(self):
        """Test extract_node loads domain context for csx_dispatch domain."""
        state = create_initial_state(
            spec_document_path="test_data/phase0/autonomous_train_spec.txt",
            target_subsystem="Train Management",
            domain_name="csx_dispatch",
            subsystem_id="train_management"
        )

        with patch('src.nodes.extract_node.parse_document') as mock_parse:
            mock_parse.return_value = ("Sample spec text", ".txt")

            with patch('src.agents.requirements_analyst.RequirementsAnalystAgent.extract_requirements') as mock_extract:
                from src.state import Requirement, RequirementType
                mock_extract.return_value = [
                    Requirement(
                        id="SYS-FUNC-001",
                        text="Sample requirement",
                        type=RequirementType.FUNCTIONAL,
                        source_section="1.0"
                    )
                ]

                result = extract_node(state)

                # Should have loaded domain context
                assert result.get('domain_context') is not None
                assert result['domain_context']['domain_name'] == 'csx_dispatch'
                assert result['domain_context']['subsystem_id'] == 'train_management'

                # Should have loaded conventions and glossary
                assert result['domain_context']['conventions'] is not None
                assert result['domain_context']['glossary'] is not None

    def test_extract_node_handles_domain_loading_failure_gracefully(self):
        """Test extract_node falls back to generic if domain loading fails."""
        state = create_initial_state(
            spec_document_path="test_data/phase0/autonomous_train_spec.txt",
            target_subsystem="Train Management",
            domain_name="nonexistent_domain",
            subsystem_id=None
        )

        with patch('src.nodes.extract_node.parse_document') as mock_parse:
            mock_parse.return_value = ("Sample spec text", ".txt")

            with patch('src.agents.requirements_analyst.RequirementsAnalystAgent.extract_requirements') as mock_extract:
                from src.state import Requirement, RequirementType
                mock_extract.return_value = [
                    Requirement(
                        id="SYS-FUNC-001",
                        text="Sample requirement",
                        type=RequirementType.FUNCTIONAL,
                        source_section="1.0"
                    )
                ]

                result = extract_node(state)

                # Should fall back to None (generic) on load error
                assert result.get('domain_context') is None

                # Should have logged error
                error_log = result.get('error_log', [])
                domain_errors = [e for e in error_log if 'Domain loading failed' in e.get('message', '')]
                assert len(domain_errors) > 0

    def test_extract_node_logs_successful_domain_load(self):
        """Test extract_node logs INFO message on successful domain load."""
        state = create_initial_state(
            spec_document_path="test_data/phase0/autonomous_train_spec.txt",
            target_subsystem="Train Management",
            domain_name="csx_dispatch",
            subsystem_id="train_management"
        )

        with patch('src.nodes.extract_node.parse_document') as mock_parse:
            mock_parse.return_value = ("Sample spec text", ".txt")

            with patch('src.agents.requirements_analyst.RequirementsAnalystAgent.extract_requirements') as mock_extract:
                from src.state import Requirement, RequirementType
                mock_extract.return_value = [
                    Requirement(
                        id="SYS-FUNC-001",
                        text="Sample requirement",
                        type=RequirementType.FUNCTIONAL,
                        source_section="1.0"
                    )
                ]

                result = extract_node(state)

                # Should have logged successful load
                error_log = result.get('error_log', [])
                domain_logs = [e for e in error_log if 'Loaded domain context' in e.get('message', '')]
                assert len(domain_logs) > 0
                assert domain_logs[0]['error_type'] == 'INFO'


class TestDecomposeNodeDomainPassing:
    """Test domain context passing in decompose_node."""

    @pytest.fixture
    def state_with_domain_context(self):
        """Create state with domain context already loaded."""
        from src.utils.domain_loader import DomainLoader

        state = {
            'extracted_requirements': [
                {
                    'id': 'SYS-FUNC-001',
                    'text': 'The system shall manage train movements',
                    'type': 'FUNC',
                    'source_section': '1.0'
                }
            ],
            'decomposition_strategy': {
                'target_subsystem': 'Train Management',
                'naming_convention': 'TM-{TYPE}-{NNN}',
                'allocation_rules': ['All train-related requirements'],
                'acceptance_criteria_required': True
            },
            'target_subsystem': 'Train Management',
            'domain_context': DomainLoader.load_context(
                domain_name="csx_dispatch",
                subsystem_id="train_management"
            ),
            'errors': [],
            'error_log': []
        }
        return state

    def test_decompose_node_passes_domain_context_to_agent(self, state_with_domain_context):
        """Test decompose_node passes domain_context to RequirementsEngineerAgent."""
        with patch('src.agents.requirements_engineer.RequirementsEngineerAgent.decompose_requirements') as mock_decompose:
            from src.state import DetailedRequirement, RequirementType
            mock_decompose.return_value = [
                DetailedRequirement(
                    id="TM-FUNC-001",
                    text="The Train Management subsystem shall track train positions",
                    type=RequirementType.FUNCTIONAL,
                    subsystem="Train Management",
                    parent_id="SYS-FUNC-001",
                    rationale="Decomposed from system requirement",
                    acceptance_criteria=["Verify train position accuracy"]
                )
            ]

            result = decompose_node(state_with_domain_context)

            # Verify agent was called with domain_context
            mock_decompose.assert_called_once()
            call_kwargs = mock_decompose.call_args[1]
            assert 'domain_context' in call_kwargs
            assert call_kwargs['domain_context'] is not None
            assert call_kwargs['domain_context']['domain_name'] == 'csx_dispatch'

    def test_decompose_node_works_without_domain_context(self):
        """Test decompose_node works correctly when domain_context is None (generic)."""
        state = {
            'extracted_requirements': [
                {
                    'id': 'SYS-FUNC-001',
                    'text': 'The system shall process data',
                    'type': 'FUNC',
                    'source_section': '1.0'
                }
            ],
            'decomposition_strategy': {
                'target_subsystem': 'Data Processing',
                'naming_convention': 'DP-{TYPE}-{NNN}',
                'allocation_rules': ['All data-related requirements'],
                'acceptance_criteria_required': False
            },
            'target_subsystem': 'Data Processing',
            'domain_context': None,  # Generic domain
            'errors': [],
            'error_log': []
        }

        with patch('src.agents.requirements_engineer.RequirementsEngineerAgent.decompose_requirements') as mock_decompose:
            from src.state import DetailedRequirement, RequirementType
            mock_decompose.return_value = [
                DetailedRequirement(
                    id="DP-FUNC-001",
                    text="The Data Processing subsystem shall validate inputs",
                    type=RequirementType.FUNCTIONAL,
                    subsystem="Data Processing",
                    parent_id="SYS-FUNC-001"
                )
            ]

            result = decompose_node(state)

            # Should still work, passing None as domain_context
            mock_decompose.assert_called_once()
            call_kwargs = mock_decompose.call_args[1]
            assert 'domain_context' in call_kwargs
            assert call_kwargs['domain_context'] is None


class TestValidateNodeDomainPassing:
    """Test domain context passing in validate_node."""

    @pytest.fixture
    def state_with_domain_context(self):
        """Create state with domain context for validation."""
        from src.utils.domain_loader import DomainLoader

        state = {
            'decomposed_requirements': [
                {
                    'id': 'TM-FUNC-001',
                    'text': 'The Train Management subsystem shall track train positions',
                    'type': 'FUNC',
                    'subsystem': 'Train Management',
                    'parent_id': 'SYS-FUNC-001',
                    'acceptance_criteria': ['Verify position accuracy']
                }
            ],
            'extracted_requirements': [
                {
                    'id': 'SYS-FUNC-001',
                    'text': 'The system shall manage train movements',
                    'type': 'FUNC',
                    'source_section': '1.0'
                }
            ],
            'decomposition_strategy': {
                'target_subsystem': 'Train Management',
                'naming_convention': 'TM-{TYPE}-{NNN}'
            },
            'traceability_matrix': {},
            'domain_context': DomainLoader.load_context(
                domain_name="csx_dispatch",
                subsystem_id="train_management"
            ),
            'quality_threshold': 0.80,
            'errors': [],
            'error_log': []
        }
        return state

    def test_validate_node_passes_domain_context_to_agent(self, state_with_domain_context):
        """Test validate_node passes domain_context to QualityAssuranceAgent."""
        with patch('src.utils.quality_checker.validate_all_requirements') as mock_validate:
            mock_validate.return_value = {'passed': True, 'issues': []}

            with patch('src.agents.quality_assurance.QualityAssuranceAgent.assess_quality') as mock_assess:
                from src.state import QualityMetrics
                mock_assess.return_value = QualityMetrics(
                    completeness=0.90,
                    clarity=0.90,
                    testability=0.90,
                    traceability=0.90,
                    domain_compliance=0.95,  # Phase 7.3: 5th dimension
                    overall_score=0.91,
                    issues=[]
                )

                result = validate_node(state_with_domain_context)

                # Verify agent was called with domain_context
                mock_assess.assert_called_once()
                call_kwargs = mock_assess.call_args[1]
                assert 'domain_context' in call_kwargs
                assert call_kwargs['domain_context'] is not None
                assert call_kwargs['domain_context']['domain_name'] == 'csx_dispatch'

    def test_validate_node_works_without_domain_context(self):
        """Test validate_node works correctly when domain_context is None (generic)."""
        state = {
            'decomposed_requirements': [
                {
                    'id': 'DP-FUNC-001',
                    'text': 'The subsystem shall process inputs',
                    'type': 'FUNC',
                    'subsystem': 'Data Processing',
                    'parent_id': 'SYS-FUNC-001'
                }
            ],
            'extracted_requirements': [
                {
                    'id': 'SYS-FUNC-001',
                    'text': 'The system shall process data',
                    'type': 'FUNC',
                    'source_section': '1.0'
                }
            ],
            'decomposition_strategy': {
                'target_subsystem': 'Data Processing',
                'naming_convention': 'DP-{TYPE}-{NNN}'
            },
            'traceability_matrix': {},
            'domain_context': None,  # Generic domain
            'quality_threshold': 0.80,
            'errors': [],
            'error_log': []
        }

        with patch('src.utils.quality_checker.validate_all_requirements') as mock_validate:
            mock_validate.return_value = {'passed': True, 'issues': []}

            with patch('src.agents.quality_assurance.QualityAssuranceAgent.assess_quality') as mock_assess:
                from src.state import QualityMetrics
                mock_assess.return_value = QualityMetrics(
                    completeness=0.85,
                    clarity=0.85,
                    testability=0.85,
                    traceability=0.85,
                    domain_compliance=None,  # None for generic domain
                    overall_score=0.85,
                    issues=[]
                )

                result = validate_node(state)

                # Should work with None domain_context
                mock_assess.assert_called_once()
                call_kwargs = mock_assess.call_args[1]
                assert 'domain_context' in call_kwargs
                assert call_kwargs['domain_context'] is None

                # Quality metrics should not include domain_compliance for generic
                quality_metrics = result['quality_metrics']
                assert quality_metrics['domain_compliance'] is None
