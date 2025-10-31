"""
Unit tests for utility modules (document_parser, skill_loader).
"""

import pytest
from pathlib import Path

from src.utils.document_parser import (
    parse_txt,
    parse_document,
    validate_document_content,
    DocumentParseError
)
from src.utils.skill_loader import (
    load_skill,
    list_available_skills,
    get_skill_info,
    validate_skill_content,
    clear_skill_cache,
    SkillLoadError
)


# ============================================================================
# Document Parser Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.phase1
class TestDocumentParser:
    """Test document parsing utilities."""

    def test_parse_txt_file(self):
        """Test parsing a plain text file."""
        # Use existing Phase 0 test file
        file_path = "examples/phase0_simple_spec.txt"

        content, file_type = parse_document(file_path)

        assert file_type == "txt"
        assert content is not None
        assert len(content) > 0
        assert "requirement" in content.lower() or "req" in content.lower()

    def test_parse_nonexistent_file(self):
        """Test that parsing nonexistent file raises error."""
        with pytest.raises(DocumentParseError) as exc_info:
            parse_document("/path/to/nonexistent/file.txt")

        assert "not found" in str(exc_info.value).lower()

    def test_parse_unsupported_file_type(self):
        """Test that unsupported file type raises error."""
        # Create a temporary file with unsupported extension
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".xyz", mode="w", delete=False) as f:
            f.write("test content")
            temp_path = f.name

        try:
            with pytest.raises(DocumentParseError) as exc_info:
                parse_document(temp_path)

            assert "unsupported" in str(exc_info.value).lower()
        finally:
            Path(temp_path).unlink()

    def test_validate_document_content_valid(self):
        """Test validating valid document content."""
        content = "This is a valid document with sufficient content."

        assert validate_document_content(content) is True

    def test_validate_document_content_empty(self):
        """Test validating empty content."""
        assert validate_document_content("") is False
        assert validate_document_content(None) is False

    def test_validate_document_content_too_short(self):
        """Test validating content that's too short."""
        assert validate_document_content("short", min_length=100) is False


# ============================================================================
# Skill Loader Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.phase1
class TestSkillLoader:
    """Test skill loading utilities."""

    def setup_method(self):
        """Clear skill cache before each test."""
        clear_skill_cache()

    def test_load_existing_skill(self):
        """Test loading an existing skill."""
        skill_content = load_skill("requirements-extraction")

        assert skill_content is not None
        assert len(skill_content) > 100
        assert "requirement" in skill_content.lower()

    def test_load_skill_caching(self):
        """Test that skills are cached."""
        # Load twice
        content1 = load_skill("requirements-extraction")
        content2 = load_skill("requirements-extraction")

        # Should be the same object (cached)
        assert content1 == content2

    def test_load_nonexistent_skill(self):
        """Test loading a nonexistent skill."""
        with pytest.raises(SkillLoadError) as exc_info:
            load_skill("nonexistent-skill")

        assert "not found" in str(exc_info.value).lower()

    def test_list_available_skills(self):
        """Test listing available skills."""
        skills = list_available_skills()

        assert isinstance(skills, list)
        assert "requirements-extraction" in skills
        assert len(skills) >= 1  # At least the extraction skill exists

    def test_get_skill_info(self):
        """Test getting skill metadata."""
        info = get_skill_info("requirements-extraction")

        assert info['name'] == "requirements-extraction"
        assert info['exists'] is True
        assert info['size'] > 0
        assert 'path' in info

    def test_get_skill_info_nonexistent(self):
        """Test getting info for nonexistent skill."""
        info = get_skill_info("nonexistent-skill")

        assert info['exists'] is False
        assert 'error' in info

    def test_validate_skill_content_valid(self):
        """Test validating valid skill content."""
        content = """
        # Purpose
        This skill helps with extraction.

        # Process
        Step 1: Do this
        Step 2: Do that

        # Output
        Return JSON format.
        """

        assert validate_skill_content(content) is True

    def test_validate_skill_content_invalid(self):
        """Test validating invalid skill content."""
        # Too short
        assert validate_skill_content("short") is False

        # No key sections
        assert validate_skill_content("x" * 200) is False

    def test_clear_cache(self):
        """Test clearing the skill cache."""
        # Load a skill
        load_skill("requirements-extraction")

        # Clear cache
        clear_skill_cache()

        # Load again - should reload from disk
        content = load_skill("requirements-extraction")
        assert content is not None
