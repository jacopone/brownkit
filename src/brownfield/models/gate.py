"""Readiness gate models."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ReadinessGate:
    """Quantitative validation gate."""

    name: str
    description: str
    threshold: float
    current_value: float
    passed: bool
    verification_command: str
    remediation_guidance: str
    exception_conditions: list[str] = field(default_factory=list)
    justification_required: bool = False
    justification: Optional[str] = None

    def evaluate(self) -> bool:
        """Check if gate passes based on threshold."""
        self.passed = self.current_value >= self.threshold
        return self.passed


# Predefined readiness gates
READINESS_GATES = [
    ReadinessGate(
        name="Test Coverage",
        description="Minimum test coverage on core business logic",
        threshold=0.6,
        current_value=0.0,
        passed=False,
        verification_command="pytest --cov=src --cov-report=json",
        remediation_guidance="Run /brownfield.testing to generate more tests",
        exception_conditions=["Project is pure library with no business logic"],
    ),
    ReadinessGate(
        name="Cyclomatic Complexity",
        description="Maximum cyclomatic complexity",
        threshold=10.0,
        current_value=0.0,
        passed=False,
        verification_command="lizard -C 10 src/",
        remediation_guidance="Refactor complex functions or document justification",
        exception_conditions=["Complexity justified in complexity-justification.md"],
    ),
    ReadinessGate(
        name="Directory Structure",
        description="Follows ecosystem conventions",
        threshold=1.0,
        current_value=0.0,
        passed=False,
        verification_command="manual",
        remediation_guidance="Run /brownfield.structure to reorganize directories",
    ),
    ReadinessGate(
        name="Build Status",
        description="Build passes cleanly",
        threshold=1.0,
        current_value=0.0,
        passed=False,
        verification_command="language-specific",
        remediation_guidance="Fix build errors and warnings",
    ),
    ReadinessGate(
        name="API Documentation",
        description="Public APIs documented",
        threshold=0.8,
        current_value=0.0,
        passed=False,
        verification_command="manual",
        remediation_guidance="Add docstrings/JSDoc to public functions/classes",
    ),
    ReadinessGate(
        name="Security",
        description="Zero critical vulnerabilities",
        threshold=0.0,
        current_value=0.0,
        passed=False,
        verification_command="bandit -r src/ -f json",
        remediation_guidance="Run /brownfield.quality to fix security issues",
    ),
    ReadinessGate(
        name="Git Hygiene",
        description="No secrets or large binaries",
        threshold=1.0,
        current_value=0.0,
        passed=False,
        verification_command="manual",
        remediation_guidance="Remove secrets and large files from git history",
    ),
]
