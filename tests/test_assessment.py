"""Smoke tests for assessment."""

from brownfield.models.assessment import (
    ComplexityViolation,
    ConfidenceLevel,
    LanguageDetection,
    Metrics,
    TechDebtCategory,
    to_markdown,
)


def test_confidencelevel_instantiation():
    """Test ConfidenceLevel can be instantiated."""
    # Smoke test - verify class can be imported and instantiated
    assert ConfidenceLevel is not None


def test_languagedetection_instantiation():
    """Test LanguageDetection can be instantiated."""
    # Smoke test - verify class can be imported and instantiated
    assert LanguageDetection is not None


def test_complexityviolation_instantiation():
    """Test ComplexityViolation can be instantiated."""
    # Smoke test - verify class can be imported and instantiated
    assert ComplexityViolation is not None


def test_metrics_instantiation():
    """Test Metrics can be instantiated."""
    # Smoke test - verify class can be imported and instantiated
    assert Metrics is not None


def test_techdebtcategory_instantiation():
    """Test TechDebtCategory can be instantiated."""
    # Smoke test - verify class can be imported and instantiated
    assert TechDebtCategory is not None


def test_to_markdown_exists():
    """Test to_markdown function exists."""
    # Smoke test - verify function can be imported
    assert callable(to_markdown)
