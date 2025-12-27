"""
Unit tests for domain context loader.

Tests domain configuration registry and context loading functionality.
"""

import pytest
from pathlib import Path

from config.domain_config import registry, DomainConfig, SubsystemConfig
from src.utils.domain_loader import DomainLoader, DomainLoadError


class TestDomainRegistry:
    """Test domain registry functionality."""

    def test_list_domains(self):
        """Test listing all available domains."""
        domains = registry.list_domains()

        assert "csx_dispatch" in domains
        assert "generic" in domains
        assert len(domains) >= 2

    def test_get_domain_csx_dispatch(self):
        """Test retrieving CSX Dispatch domain configuration."""
        domain = registry.get_domain("csx_dispatch")

        assert domain is not None
        assert domain.name == "csx_dispatch"
        assert domain.description == "CSX Dispatch system requirements domain"
        assert len(domain.subsystems) >= 3

    def test_get_domain_generic(self):
        """Test retrieving generic domain configuration."""
        domain = registry.get_domain("generic")

        assert domain is not None
        assert domain.name == "generic"
        assert len(domain.subsystems) == 0

    def test_get_domain_invalid(self):
        """Test retrieving non-existent domain returns None."""
        domain = registry.get_domain("invalid_domain")
        assert domain is None

    def test_list_subsystems_csx_dispatch(self):
        """Test listing subsystems for CSX Dispatch domain."""
        subsystems = registry.list_subsystems("csx_dispatch")

        assert "train_management" in subsystems
        assert "traffic_control" in subsystems
        assert "bridge_control" in subsystems
        assert len(subsystems) >= 3

    def test_list_subsystems_generic(self):
        """Test listing subsystems for generic domain (should be empty)."""
        subsystems = registry.list_subsystems("generic")
        assert len(subsystems) == 0

    def test_list_subsystems_invalid_domain(self):
        """Test listing subsystems for invalid domain returns empty list."""
        subsystems = registry.list_subsystems("invalid_domain")
        assert len(subsystems) == 0


class TestDomainLoader:
    """Test domain context loader functionality."""

    def test_load_context_generic(self):
        """Test loading generic domain context."""
        context = DomainLoader.load_context("generic")

        assert context["domain_name"] == "generic"
        # Generic domain has no context files
        assert context["conventions"] is None
        assert context["glossary"] is None
        assert context["system_overview"] is None
        assert context["subsystem_overview"] is None
        assert context["examples"] is None

    def test_load_context_csx_dispatch_common_only(self):
        """Test loading CSX Dispatch common context without subsystem."""
        context = DomainLoader.load_context("csx_dispatch")

        assert context["domain_name"] == "csx_dispatch"
        # Should have common context
        assert context["conventions"] is not None
        assert "TM-" in context["conventions"]  # Check for subsystem ID pattern
        assert context["glossary"] is not None
        assert "Train Management" in context["glossary"]
        assert context["system_overview"] is not None
        # Should not have subsystem-specific context
        assert context["subsystem_overview"] is None
        assert context["examples"] is None

    def test_load_context_csx_dispatch_with_train_management(self):
        """Test loading CSX Dispatch with Train Management subsystem."""
        context = DomainLoader.load_context("csx_dispatch", "train_management")

        assert context["domain_name"] == "csx_dispatch"
        # Should have all context
        assert context["conventions"] is not None
        assert context["glossary"] is not None
        assert context["system_overview"] is not None
        assert context["subsystem_overview"] is not None
        assert "Train Management Subsystem" in context["subsystem_overview"]
        assert context["examples"] is not None
        assert "UC-TM-040" in context["examples"]  # Check for benchmark example

    def test_load_context_invalid_domain(self):
        """Test loading context for invalid domain raises error."""
        with pytest.raises(DomainLoadError, match="Unknown domain"):
            DomainLoader.load_context("invalid_domain")

    def test_load_context_invalid_subsystem(self):
        """Test loading context for invalid subsystem raises error."""
        with pytest.raises(DomainLoadError, match="Unknown subsystem"):
            DomainLoader.load_context("csx_dispatch", "invalid_subsystem")

    def test_build_skill_prompt_section_no_context(self):
        """Test building prompt section with no domain context."""
        context = DomainLoader.load_context("generic")
        prompt_section = DomainLoader.build_skill_prompt_section(context)

        # Generic mode should return empty string
        assert prompt_section == ""

    def test_build_skill_prompt_section_csx_dispatch(self):
        """Test building prompt section with CSX Dispatch context."""
        context = DomainLoader.load_context("csx_dispatch", "train_management")
        prompt_section = DomainLoader.build_skill_prompt_section(
            context,
            subsystem_name="Train Management (TM)"
        )

        # Should include header with subsystem name
        assert "## Domain Context (Train Management (TM))" in prompt_section
        # Should include sections
        assert "### Requirements Template Conventions" in prompt_section
        assert "### Domain Glossary" in prompt_section
        assert "### System Overview" in prompt_section
        assert "### Subsystem Context" in prompt_section
        assert "### Reference Examples" in prompt_section

    def test_validate_context_complete(self):
        """Test validation with complete context."""
        context = DomainLoader.load_context("csx_dispatch", "train_management")
        warnings = DomainLoader.validate_context(context)

        # CSX Dispatch with TM should have no warnings
        assert len(warnings) == 0

    def test_validate_context_missing_conventions(self):
        """Test validation detects missing conventions."""
        context = {
            "domain_name": "test",
            "conventions": None,
            "glossary": "test glossary",
            "system_overview": None,
            "subsystem_overview": None,
            "examples": None
        }
        warnings = DomainLoader.validate_context(context)

        assert len(warnings) > 0
        assert any("conventions" in w.lower() for w in warnings)

    def test_validate_context_missing_glossary(self):
        """Test validation detects missing glossary."""
        context = {
            "domain_name": "test",
            "conventions": "test conventions",
            "glossary": None,
            "system_overview": None,
            "subsystem_overview": None,
            "examples": None
        }
        warnings = DomainLoader.validate_context(context)

        assert len(warnings) > 0
        assert any("glossary" in w.lower() for w in warnings)

    def test_caching(self):
        """Test that domain context loading is cached."""
        # Load same context twice
        context1 = DomainLoader.load_context("csx_dispatch")
        context2 = DomainLoader.load_context("csx_dispatch")

        # Should return cached result (same object reference for strings)
        # Note: This tests the @lru_cache decorator
        assert context1["conventions"] == context2["conventions"]
        assert context1["glossary"] == context2["glossary"]


class TestIntegration:
    """Integration tests for domain configuration and loading."""

    def test_domain_directory_structure_exists(self):
        """Test that domain context directory structure exists."""
        base_path = Path(__file__).parent.parent / "domain_contexts"

        # Check CSX Dispatch structure
        csx_path = base_path / "csx_dispatch"
        assert csx_path.exists(), "CSX Dispatch domain directory should exist"

        common_path = csx_path / "common"
        assert common_path.exists(), "CSX common context directory should exist"
        assert (common_path / "conventions.md").exists()
        assert (common_path / "glossary.md").exists()
        assert (common_path / "system_overview.md").exists()

        tm_path = csx_path / "subsystems" / "train_management"
        assert tm_path.exists(), "Train Management subsystem directory should exist"
        assert (tm_path / "subsystem_overview.md").exists()
        assert (tm_path / "examples.md").exists()

    def test_end_to_end_csx_dispatch_train_management(self):
        """End-to-end test: Load CSX Dispatch TM context and build prompt."""
        # Get domain
        domain = registry.get_domain("csx_dispatch")
        assert domain is not None

        # Get subsystem
        subsystem = domain.subsystems.get("train_management")
        assert subsystem is not None

        # Load context
        context = DomainLoader.load_context("csx_dispatch", "train_management")

        # Validate
        warnings = DomainLoader.validate_context(context)
        assert len(warnings) == 0, f"Context should be complete: {warnings}"

        # Build prompt section
        prompt_section = DomainLoader.build_skill_prompt_section(
            context,
            subsystem_name=subsystem.name
        )

        # Verify prompt contains expected content
        assert len(prompt_section) > 0
        assert subsystem.name in prompt_section
        assert "Train Management" in prompt_section
        assert "UC-TM-040" in prompt_section  # Benchmark example
