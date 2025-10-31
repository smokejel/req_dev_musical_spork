"""
Skill loading utilities for loading SKILL.md files.

Skills are modular expertise modules that guide LLM behavior through
detailed methodologies. Each skill is stored in a SKILL.md file.
"""

import os
from pathlib import Path
from typing import Optional, Dict
from functools import lru_cache


class SkillLoadError(Exception):
    """Raised when skill loading fails."""
    pass


# Cache loaded skills for performance
_skill_cache: Dict[str, str] = {}


def get_skills_directory() -> Path:
    """
    Get the path to the skills directory.

    Returns:
        Path object pointing to the skills directory

    Raises:
        SkillLoadError: If skills directory cannot be found
    """
    # Get the project root (3 levels up from this file)
    # skills/requirements-extraction/SKILL.md
    # src/utils/skill_loader.py
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent  # Go up 3 levels

    skills_dir = project_root / "skills"

    if not skills_dir.exists():
        raise SkillLoadError(
            f"Skills directory not found at: {skills_dir}. "
            f"Expected structure: project_root/skills/"
        )

    return skills_dir


def get_skill_path(skill_name: str) -> Path:
    """
    Get the path to a specific skill's SKILL.md file.

    Args:
        skill_name: Name of the skill (e.g., 'requirements-extraction')

    Returns:
        Path object pointing to the SKILL.md file

    Raises:
        SkillLoadError: If skill directory or SKILL.md file doesn't exist
    """
    skills_dir = get_skills_directory()
    skill_dir = skills_dir / skill_name
    skill_file = skill_dir / "SKILL.md"

    if not skill_dir.exists():
        available_skills = [
            d.name for d in skills_dir.iterdir()
            if d.is_dir() and not d.name.startswith('_')
        ]
        raise SkillLoadError(
            f"Skill directory not found: {skill_name}. "
            f"Available skills: {', '.join(available_skills)}"
        )

    if not skill_file.exists():
        raise SkillLoadError(
            f"SKILL.md file not found in: {skill_dir}. "
            f"Expected file: {skill_file}"
        )

    return skill_file


@lru_cache(maxsize=32)
def load_skill(skill_name: str, use_cache: bool = True) -> str:
    """
    Load the content of a SKILL.md file.

    This function is cached using lru_cache for performance. The same skill
    file will only be loaded once per Python session.

    Args:
        skill_name: Name of the skill (e.g., 'requirements-extraction')
        use_cache: Whether to use the internal cache (for testing)

    Returns:
        Content of the SKILL.md file as a string

    Raises:
        SkillLoadError: If skill cannot be loaded

    Example:
        >>> skill_content = load_skill('requirements-extraction')
        >>> print(len(skill_content))
        3137
    """
    # Check internal cache first (only if use_cache is True)
    if use_cache and skill_name in _skill_cache:
        return _skill_cache[skill_name]

    try:
        skill_file = get_skill_path(skill_name)

        # Read the skill file
        with open(skill_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Validate content is not empty
        if not content.strip():
            raise SkillLoadError(
                f"Skill file is empty: {skill_file}"
            )

        # Store in cache
        if use_cache:
            _skill_cache[skill_name] = content

        return content

    except SkillLoadError:
        raise  # Re-raise our own exceptions
    except Exception as e:
        raise SkillLoadError(
            f"Error loading skill '{skill_name}': {str(e)}"
        )


def list_available_skills() -> list[str]:
    """
    List all available skills in the skills directory.

    Returns:
        List of skill names (directory names containing SKILL.md files)

    Raises:
        SkillLoadError: If skills directory cannot be accessed
    """
    skills_dir = get_skills_directory()

    available_skills = []

    for item in skills_dir.iterdir():
        # Skip hidden directories and templates
        if item.name.startswith('_') or item.name.startswith('.'):
            continue

        # Only include directories that have a SKILL.md file
        if item.is_dir():
            skill_file = item / "SKILL.md"
            if skill_file.exists():
                available_skills.append(item.name)

    return sorted(available_skills)


def validate_skill_content(content: str, min_length: int = 100) -> bool:
    """
    Validate that skill content is meaningful.

    Args:
        content: Skill file content
        min_length: Minimum acceptable length in characters

    Returns:
        True if valid, False otherwise
    """
    if not content:
        return False

    stripped = content.strip()

    if len(stripped) < min_length:
        return False

    # Check for key skill components (basic heuristic)
    required_sections = ['purpose', 'process', 'output']
    content_lower = stripped.lower()

    # At least one required section should be present
    has_section = any(section in content_lower for section in required_sections)

    return has_section


def clear_skill_cache():
    """
    Clear the skill cache.

    Useful for testing or when skills are updated during runtime.
    """
    global _skill_cache
    _skill_cache.clear()
    # Also clear lru_cache
    load_skill.cache_clear()


def get_skill_info(skill_name: str) -> Dict[str, any]:
    """
    Get metadata about a skill without loading its full content.

    Args:
        skill_name: Name of the skill

    Returns:
        Dictionary with skill metadata (name, path, size, exists)

    Raises:
        SkillLoadError: If skill directory cannot be accessed
    """
    try:
        skill_file = get_skill_path(skill_name)

        return {
            'name': skill_name,
            'path': str(skill_file),
            'exists': skill_file.exists(),
            'size': skill_file.stat().st_size if skill_file.exists() else 0,
            'directory': str(skill_file.parent)
        }

    except SkillLoadError as e:
        return {
            'name': skill_name,
            'path': None,
            'exists': False,
            'size': 0,
            'error': str(e)
        }
