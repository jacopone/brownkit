"""Smoke tests for report."""

from brownfield.models.report import (
    GraduationReport,
    SecurityFix,
    StructuralChange,
    TestImprovement,
    to_markdown,
)


def test_structuralchange_instantiation():
    """Test StructuralChange can be instantiated."""
    # Smoke test - verify class can be imported and instantiated
    assert StructuralChange is not None


def test_testimprovement_instantiation():
    """Test TestImprovement can be instantiated."""
    # Smoke test - verify class can be imported and instantiated
    assert TestImprovement is not None


def test_securityfix_instantiation():
    """Test SecurityFix can be instantiated."""
    # Smoke test - verify class can be imported and instantiated
    assert SecurityFix is not None


def test_graduationreport_instantiation():
    """Test GraduationReport can be instantiated."""
    # Smoke test - verify class can be imported and instantiated
    assert GraduationReport is not None


def test_to_markdown_exists():
    """Test to_markdown function exists."""
    # Smoke test - verify function can be imported
    assert callable(to_markdown)
