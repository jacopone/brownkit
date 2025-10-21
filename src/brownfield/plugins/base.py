"""Base class for language-specific handlers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from brownfield.models.assessment import ConfidenceLevel


@dataclass
class DetectionResult:
    """Language/framework detection result."""

    language: str
    confidence: ConfidenceLevel
    version: Optional[str]
    framework: Optional[str]
    evidence: dict[str, str]


@dataclass
class StructureResult:
    """Structure remediation result."""

    directories_created: list[Path]
    files_moved: dict[Path, Path]
    imports_updated: int
    configs_created: list[Path]
    commits: list[str]


@dataclass
class TestSetupResult:
    """Test infrastructure setup result."""

    framework: str
    dependencies_added: list[str]
    test_files_created: list[Path]
    coverage: float
    tests_passing: int
    tests_failing: int


@dataclass
class QualitySetupResult:
    """Quality gates installation result."""

    linter: str
    formatter: str
    linter_issues_found: int
    linter_issues_fixed: int
    formatter_files_changed: int
    hooks_installed: list[str]
    complexity_violations: int


class LanguageHandler(ABC):
    """Abstract base class for language-specific handlers."""

    @abstractmethod
    def detect(self, project_root: Path) -> Optional[DetectionResult]:
        """
        Detect language and framework from project files.

        Args:
            project_root: Path to project directory

        Returns:
            DetectionResult if language detected, None otherwise
        """
        pass

    @abstractmethod
    def get_standard_structure(self) -> dict[str, list[str]]:
        """
        Return ecosystem-standard directory structure.

        Returns:
            Dictionary mapping directory names to expected files/patterns
        """
        pass

    @abstractmethod
    def bootstrap_tests(
        self, project_root: Path, core_modules: list[Path], coverage_target: float = 0.6
    ) -> TestSetupResult:
        """
        Add test framework and generate initial tests.

        Args:
            project_root: Path to project directory
            core_modules: Core business logic modules to test
            coverage_target: Desired coverage (0.0-1.0)

        Returns:
            TestSetupResult with setup details
        """
        pass

    @abstractmethod
    def install_quality_gates(
        self, project_root: Path, complexity_threshold: int = 10
    ) -> QualitySetupResult:
        """
        Install linters, formatters, and pre-commit hooks.

        Args:
            project_root: Path to project directory
            complexity_threshold: Maximum cyclomatic complexity

        Returns:
            QualitySetupResult with installation details
        """
        pass

    @abstractmethod
    def verify_build(self, project_root: Path) -> bool:
        """
        Verify project builds without errors.

        Args:
            project_root: Path to project directory

        Returns:
            True if build succeeds, False otherwise
        """
        pass

    @abstractmethod
    def measure_complexity(self, project_root: Path) -> dict[str, float]:
        """
        Measure cyclomatic complexity of codebase.

        Args:
            project_root: Path to project directory

        Returns:
            Dictionary with complexity metrics
        """
        pass

    @abstractmethod
    def scan_security(self, project_root: Path) -> dict[str, int]:
        """
        Scan for security vulnerabilities.

        Args:
            project_root: Path to project directory

        Returns:
            Dictionary with vulnerability counts by severity
        """
        pass
