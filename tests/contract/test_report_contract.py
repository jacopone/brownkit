"""Contract tests for report public APIs."""

import dataclasses

from brownfield.models.report import (
    GraduationReport,
    SecurityFix,
    StructuralChange,
    TestImprovement,
)


def test_graduation_report_is_importable():
    """GraduationReport is importable and is a dataclass."""
    assert dataclasses.is_dataclass(GraduationReport)


def test_graduation_report_has_to_markdown():
    """GraduationReport exposes a to_markdown instance method."""
    assert hasattr(GraduationReport, "to_markdown")
    assert callable(GraduationReport.to_markdown)


def test_structural_change_is_importable():
    """StructuralChange is importable and is a dataclass."""
    assert dataclasses.is_dataclass(StructuralChange)


def test_test_improvement_is_importable():
    """TestImprovement is importable and is a dataclass."""
    assert dataclasses.is_dataclass(TestImprovement)


def test_security_fix_is_importable():
    """SecurityFix is importable and is a dataclass."""
    assert dataclasses.is_dataclass(SecurityFix)
