"""
Domain configuration registry for domain-aware requirements decomposition.

This module provides the registry for all available domains and their subsystems,
enabling zero-code-change extensibility for new domains.

Usage:
    from config.domain_config import registry

    # List all domains
    domains = registry.list_domains()

    # Get domain configuration
    domain = registry.get_domain("csx_railway")

    # List subsystems
    subsystems = registry.list_subsystems("csx_railway")
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class SubsystemConfig:
    """Configuration for a specific subsystem within a domain."""

    id: str
    """Unique identifier for the subsystem (e.g., 'train_management')"""

    name: str
    """Human-readable name (e.g., 'Train Management (TM)')"""

    description: str
    """Brief description of subsystem purpose"""

    context_dir: Path
    """Path to subsystem-specific context files"""


@dataclass
class DomainConfig:
    """Configuration for a requirements domain (e.g., CSX Railway)."""

    name: str
    """Domain identifier (e.g., 'csx_railway')"""

    description: str
    """Human-readable description of the domain"""

    common_context_dir: Path
    """Path to Layer 1 common context files (conventions, glossary, overview)"""

    subsystems: Dict[str, SubsystemConfig] = field(default_factory=dict)
    """Registry of subsystems within this domain"""


class DomainRegistry:
    """
    Registry of all available domains and their subsystems.

    This class provides centralized management of domain configurations,
    enabling the system to discover and load domain-specific context.
    """

    def __init__(self):
        """Initialize registry with built-in domains."""
        self._domains: Dict[str, DomainConfig] = {}
        self._register_builtin_domains()

    def _register_builtin_domains(self):
        """Register built-in domains (CSX Railway, Generic)."""
        base_path = Path(__file__).parent.parent / "domain_contexts"

        # CSX Dispatch Domain
        csx_path = base_path / "csx_dispatch"
        self._domains["csx_dispatch"] = DomainConfig(
            name="csx_dispatch",
            description="CSX Dispatch system requirements domain",
            common_context_dir=csx_path / "common",
            subsystems={
                "train_management": SubsystemConfig(
                    id="train_management",
                    name="Train Management (TM)",
                    description="Manages train data, profiles, sheets, and crew information",
                    context_dir=csx_path / "subsystems" / "train_management"
                ),
                "traffic_control": SubsystemConfig(
                    id="traffic_control",
                    name="Traffic Control (TC)",
                    description="Manages signal control, route management, and track authorities",
                    context_dir=csx_path / "subsystems" / "traffic_control"
                ),
                "bridge_control": SubsystemConfig(
                    id="bridge_control",
                    name="Bridge Control (BC)",
                    description="Manages bridge operations and safety protocols",
                    context_dir=csx_path / "subsystems" / "bridge_control"
                )
            }
        )

        # Generic Domain (no domain-specific context)
        self._domains["generic"] = DomainConfig(
            name="generic",
            description="Generic requirements (no domain-specific context)",
            common_context_dir=base_path / "generic",
            subsystems={}
        )

    def get_domain(self, name: str) -> Optional[DomainConfig]:
        """
        Retrieve domain configuration by name.

        Args:
            name: Domain identifier (e.g., 'csx_railway', 'generic')

        Returns:
            DomainConfig if found, None otherwise
        """
        return self._domains.get(name)

    def list_domains(self) -> List[str]:
        """
        List all available domain names.

        Returns:
            List of domain identifiers
        """
        return list(self._domains.keys())

    def list_subsystems(self, domain_name: str) -> List[str]:
        """
        List all subsystem IDs for a given domain.

        Args:
            domain_name: Domain identifier

        Returns:
            List of subsystem IDs, or empty list if domain not found
        """
        domain = self.get_domain(domain_name)
        return list(domain.subsystems.keys()) if domain else []

    def register_domain(self, domain: DomainConfig):
        """
        Register a new domain configuration.

        This method allows external modules to register custom domains
        without modifying this file.

        Args:
            domain: DomainConfig to register
        """
        self._domains[domain.name] = domain


# Singleton instance
registry = DomainRegistry()
