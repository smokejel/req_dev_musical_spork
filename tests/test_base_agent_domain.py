"""
Unit tests for BaseAgent domain context injection (Phase 7.2).

Tests the domain context injection mechanism in BaseAgent.get_skill_content().
Validates that domain context is properly injected between methodology and examples.
"""

import pytest
from pathlib import Path
from src.agents.requirements_engineer import RequirementsEngineerAgent
from src.agents.quality_assurance import QualityAssuranceAgent
from src.utils.domain_loader import DomainLoader


class TestBaseAgentDomainInjection:
    """Test domain context injection in BaseAgent."""

    def test_get_skill_content_without_domain_context(self):
        """Test get_skill_content returns original skill when no domain context provided."""
        agent = RequirementsEngineerAgent()

        # Get skill content without domain context
        skill_content = agent.get_skill_content(domain_context=None)

        # Should return original skill content
        assert skill_content is not None
        assert "Methodology" in skill_content or "methodology" in skill_content
        # Should NOT contain domain context markers
        assert "Domain Context" not in skill_content

    def test_get_skill_content_with_generic_domain(self):
        """Test get_skill_content returns original skill for generic domain."""
        agent = RequirementsEngineerAgent()

        # Create generic domain context
        domain_context = {
            'domain_name': 'generic',
            'conventions': None,
            'glossary': None
        }

        skill_content = agent.get_skill_content(domain_context=domain_context)

        # Should return original skill content (generic is same as no domain)
        assert skill_content is not None
        assert "Domain Context" not in skill_content

    def test_get_skill_content_with_domain_context_injection(self):
        """Test get_skill_content injects domain context between methodology and examples."""
        agent = RequirementsEngineerAgent()

        # Load real CSX Dispatch domain context
        domain_context = DomainLoader.load_context(
            domain_name="csx_dispatch",
            subsystem_id="train_management"
        )

        skill_content = agent.get_skill_content(domain_context=domain_context)

        # Should contain original skill content
        assert skill_content is not None
        assert "Methodology" in skill_content or "methodology" in skill_content

        # Should contain domain context section
        assert "## Domain Context" in skill_content

        # Should contain domain-specific content
        assert "TM-" in skill_content  # Train Management prefix from conventions
        assert "Active Train" in skill_content or "Train List" in skill_content  # From glossary

        # Validate injection happened before examples
        domain_idx = skill_content.find("## Domain Context")
        examples_idx = skill_content.find("## Examples") if "## Examples" in skill_content else skill_content.find("# Examples")

        if examples_idx > 0:
            assert domain_idx < examples_idx, "Domain context should be injected before examples"

    def test_get_skill_content_with_partial_domain_context(self):
        """Test get_skill_content handles partial domain context (missing some files)."""
        agent = QualityAssuranceAgent()

        # Create partial domain context (conventions only)
        domain_context = {
            'domain_name': 'csx_dispatch',
            'subsystem_id': 'train_management',
            'conventions': '**ID Template**: TM-{TYPE}-{NNN}',
            'glossary': None,
            'system_overview': None,
            'subsystem_overview': None,
            'examples': None
        }

        skill_content = agent.get_skill_content(domain_context=domain_context)

        # Should still inject domain context even with partial data
        assert "## Domain Context" in skill_content
        assert "TM-{TYPE}-{NNN}" in skill_content

        # Should NOT contain sections for missing data
        assert "### Domain Glossary" not in skill_content

    def test_get_skill_content_injection_multiple_agents(self):
        """Test domain context injection works across all agent types."""
        domain_context = DomainLoader.load_context(
            domain_name="csx_dispatch",
            subsystem_id="train_management"
        )

        # Test RequirementsEngineer agent
        decompose_agent = RequirementsEngineerAgent()
        decompose_content = decompose_agent.get_skill_content(domain_context)
        assert "## Domain Context" in decompose_content

        # Test QualityAssurance agent
        validate_agent = QualityAssuranceAgent()
        validate_content = validate_agent.get_skill_content(domain_context)
        assert "## Domain Context" in validate_content

    def test_get_skill_content_without_loaded_skill_raises_error(self):
        """Test get_skill_content raises error when skill not loaded."""
        # Create agent and unset skill content
        agent = RequirementsEngineerAgent()
        agent.skill_content = None  # Simulate unloaded skill

        # Should raise AgentError
        from src.agents.base_agent import AgentError
        with pytest.raises(AgentError, match="No skill loaded"):
            agent.get_skill_content()

    def test_domain_context_caching(self):
        """Test domain context is loaded once and reused across calls."""
        # This test validates LRU cache behavior in DomainLoader
        domain_context_1 = DomainLoader.load_context(
            domain_name="csx_dispatch",
            subsystem_id="train_management"
        )

        domain_context_2 = DomainLoader.load_context(
            domain_name="csx_dispatch",
            subsystem_id="train_management"
        )

        # Both should have same content (cache hit)
        assert domain_context_1 == domain_context_2

        # Check cache info to confirm caching is working
        cache_info = DomainLoader._load_markdown_file.cache_info()
        assert cache_info.hits > 0, "Expected cache hits from repeated loads"


class TestDomainContextInjectionEdgeCases:
    """Test edge cases for domain context injection."""

    def test_skill_without_examples_section(self):
        """Test injection when skill has no ## Examples section."""
        agent = RequirementsEngineerAgent()

        # Load domain context
        domain_context = DomainLoader.load_context(
            domain_name="csx_dispatch",
            subsystem_id="train_management"
        )

        # Even if no examples section, should append domain context at end
        skill_content = agent.get_skill_content(domain_context)
        assert "## Domain Context" in skill_content

    def test_domain_context_with_special_characters(self):
        """Test domain context with markdown special characters is handled correctly."""
        agent = RequirementsEngineerAgent()

        # Create domain context with special characters
        domain_context = {
            'domain_name': 'test_domain',
            'subsystem_id': None,
            'conventions': '**Bold**, *italic*, `code`, [link](url)',
            'glossary': '| Term | Definition |\n|------|------------|\n| Test | Test def |',
            'system_overview': None,
            'subsystem_overview': None,
            'examples': None
        }

        # Should handle special characters without breaking
        skill_content = agent.get_skill_content(domain_context)
        assert "**Bold**" in skill_content
        assert "`code`" in skill_content
        assert "| Term |" in skill_content
