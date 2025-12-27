"""
Domain context loader for requirements decomposition.

This module loads domain-specific markdown files (conventions, glossary, examples)
and builds formatted sections for injection into LLM skill prompts.

Usage:
    from src.utils.domain_loader import DomainLoader

    # Load domain context
    context = DomainLoader.load_context("csx_dispatch", "train_management")

    # Build prompt section
    prompt_section = DomainLoader.build_skill_prompt_section(context, "Train Management (TM)")
"""

import logging
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

from config.domain_config import registry, DomainConfig, SubsystemConfig

logger = logging.getLogger(__name__)


class DomainLoadError(Exception):
    """Raised when domain context cannot be loaded."""
    pass


class DomainLoader:
    """Loads and caches domain context from markdown files."""

    @staticmethod
    @lru_cache(maxsize=32)
    def _load_markdown_file(file_path: Path) -> str:
        """
        Load and cache markdown file content.

        Args:
            file_path: Absolute path to markdown file

        Returns:
            File content as string

        Raises:
            DomainLoadError: If file cannot be loaded
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise DomainLoadError(f"Domain context file not found: {file_path}")
        except Exception as e:
            raise DomainLoadError(f"Failed to load domain context from {file_path}: {e}")

    @staticmethod
    def load_context(
        domain_name: str,
        subsystem_id: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Load domain context for a given domain and optional subsystem.

        Args:
            domain_name: Domain identifier (e.g., 'csx_railway', 'generic')
            subsystem_id: Optional subsystem identifier (e.g., 'train_management')

        Returns:
            Dictionary with loaded domain context sections:
            {
                'domain_name': str,
                'conventions': str or None,
                'glossary': str or None,
                'system_overview': str or None,
                'subsystem_overview': str or None,
                'examples': str or None
            }

        Raises:
            DomainLoadError: If domain not found or files cannot be loaded
        """
        domain = registry.get_domain(domain_name)
        if not domain:
            available = registry.list_domains()
            raise DomainLoadError(
                f"Unknown domain '{domain_name}'. Available: {available}"
            )

        context = {
            'domain_name': domain_name,
            'subsystem_id': subsystem_id,
            'conventions': None,
            'glossary': None,
            'system_overview': None,
            'subsystem_overview': None,
            'examples': None
        }

        # Load Layer 1: Common context (if directory exists)
        if domain.common_context_dir.exists():
            context.update(DomainLoader._load_common_context(domain))
        else:
            logger.warning(f"Common context directory not found: {domain.common_context_dir}")

        # Load Layer 2 & 3: Subsystem-specific context
        if subsystem_id:
            if subsystem_id not in domain.subsystems:
                available = list(domain.subsystems.keys())
                raise DomainLoadError(
                    f"Unknown subsystem '{subsystem_id}' for domain '{domain_name}'. "
                    f"Available: {available}"
                )

            subsystem = domain.subsystems[subsystem_id]
            if subsystem.context_dir.exists():
                context.update(DomainLoader._load_subsystem_context(subsystem))
            else:
                logger.warning(f"Subsystem context directory not found: {subsystem.context_dir}")

        return context

    @staticmethod
    def _load_common_context(domain: DomainConfig) -> Dict[str, Optional[str]]:
        """
        Load Layer 1 common context files.

        Args:
            domain: DomainConfig with common_context_dir path

        Returns:
            Dict with 'conventions', 'glossary', 'system_overview' keys
        """
        context = {}
        common_dir = domain.common_context_dir

        # Load conventions.md
        conventions_file = common_dir / "conventions.md"
        if conventions_file.exists():
            context["conventions"] = DomainLoader._load_markdown_file(conventions_file)
            logger.info(f"Loaded conventions from {conventions_file}")

        # Load glossary.md
        glossary_file = common_dir / "glossary.md"
        if glossary_file.exists():
            context["glossary"] = DomainLoader._load_markdown_file(glossary_file)
            logger.info(f"Loaded glossary from {glossary_file}")

        # Load system_overview.md
        overview_file = common_dir / "system_overview.md"
        if overview_file.exists():
            context["system_overview"] = DomainLoader._load_markdown_file(overview_file)
            logger.info(f"Loaded system overview from {overview_file}")

        return context

    @staticmethod
    def _load_subsystem_context(subsystem: SubsystemConfig) -> Dict[str, Optional[str]]:
        """
        Load Layer 2/3 subsystem-specific context files.

        Args:
            subsystem: SubsystemConfig with context_dir path

        Returns:
            Dict with 'subsystem_overview', 'examples' keys
        """
        context = {}
        subsystem_dir = subsystem.context_dir

        # Load subsystem_overview.md
        overview_file = subsystem_dir / "subsystem_overview.md"
        if overview_file.exists():
            context["subsystem_overview"] = DomainLoader._load_markdown_file(overview_file)
            logger.info(f"Loaded subsystem overview from {overview_file}")

        # Load examples.md
        examples_file = subsystem_dir / "examples.md"
        if examples_file.exists():
            context["examples"] = DomainLoader._load_markdown_file(examples_file)
            logger.info(f"Loaded examples from {examples_file}")

        return context

    @staticmethod
    def build_skill_prompt_section(
        context: Dict[str, str],
        subsystem_name: str = ""
    ) -> str:
        """
        Build domain context section for skill prompt injection.

        This section is inserted between the skill methodology and examples,
        providing domain-specific guidance without modifying core skill content.

        Args:
            context: Loaded domain context from load_context()
            subsystem_name: Human-readable subsystem name (e.g., "Train Management (TM)")

        Returns:
            Formatted markdown section for prompt injection, or empty string if no context
        """
        if not context or context.get('domain_name') == 'generic':
            return ""

        sections = []

        # Header
        header = "## Domain Context"
        if subsystem_name:
            header += f" ({subsystem_name})"
        sections.append(header)
        sections.append("")  # Blank line

        # Conventions (if present)
        if context.get("conventions"):
            sections.append("### Requirements Template Conventions")
            sections.append(context["conventions"])
            sections.append("")

        # Glossary (if present)
        if context.get("glossary"):
            sections.append("### Domain Glossary")
            sections.append(context["glossary"])
            sections.append("")

        # System Overview (if present)
        if context.get("system_overview"):
            sections.append("### System Overview")
            sections.append(context["system_overview"])
            sections.append("")

        # Subsystem Overview (if present)
        if context.get("subsystem_overview"):
            sections.append("### Subsystem Context")
            sections.append(context["subsystem_overview"])
            sections.append("")

        # Examples (if present)
        if context.get("examples"):
            sections.append("### Reference Examples")
            sections.append(context["examples"])
            sections.append("")

        return "\n".join(sections)

    @staticmethod
    def validate_context(context: Dict[str, str]) -> List[str]:
        """
        Validate loaded domain context for completeness and format.

        Args:
            context: Loaded domain context dictionary

        Returns:
            List of warning messages (empty if no issues)
        """
        warnings = []

        if not context.get("conventions"):
            warnings.append("Missing conventions.md (template format undefined)")

        if not context.get("glossary"):
            warnings.append("Missing glossary.md (term validation disabled)")

        # Validate glossary table format
        if context.get("glossary"):
            if "| Term |" not in context["glossary"]:
                warnings.append("Glossary missing markdown table header")

        return warnings
