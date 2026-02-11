"""Contract tests for assessment public APIs."""

import dataclasses

from brownfield.models.assessment import (
    AssessmentReport,
    ComplexityViolation,
    ConfidenceLevel,
    LanguageDetection,
    Metrics,
    TechDebtCategory,
)


def test_assessment_report_is_importable():
    """AssessmentReport is importable and is a dataclass."""
    assert dataclasses.is_dataclass(AssessmentReport)


def test_assessment_report_has_to_markdown():
    """AssessmentReport exposes a to_markdown instance method."""
    assert hasattr(AssessmentReport, "to_markdown")
    assert callable(AssessmentReport.to_markdown)


def test_metrics_is_importable():
    """Metrics is importable and is a dataclass."""
    assert dataclasses.is_dataclass(Metrics)


def test_complexity_violation_is_importable():
    """ComplexityViolation is importable and is a dataclass."""
    assert dataclasses.is_dataclass(ComplexityViolation)


def test_confidence_level_is_enum():
    """ConfidenceLevel is an importable enum."""
    assert hasattr(ConfidenceLevel, "HIGH")
    assert hasattr(ConfidenceLevel, "MEDIUM")
    assert hasattr(ConfidenceLevel, "LOW")


def test_language_detection_is_importable():
    """LanguageDetection is importable and is a dataclass."""
    assert dataclasses.is_dataclass(LanguageDetection)


def test_tech_debt_category_is_importable():
    """TechDebtCategory is importable and is a dataclass."""
    assert dataclasses.is_dataclass(TechDebtCategory)
